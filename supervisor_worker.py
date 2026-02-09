"""Supervisor + Worker orchestration for dictation runtime."""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


DEFAULT_WHISPERCPP_ARGS = "-otxt -l auto -oved GPU"
WHISPERCPP_STATUS_PREFIX = "WHISPERCPP_STATUS"
KNOWN_CPP_MODEL_FILES = {
    "base": "ggml-base.bin",
    "small": "ggml-small.bin",
    "medium": "ggml-medium.bin",
    "large-v3": "ggml-large-v3.bin",
}


@dataclass(frozen=True)
class WorkerProfile:
    """Runtime profile used to launch the dictation worker."""

    name: str
    backend: str
    model: str

    def __post_init__(self) -> None:
        if self.backend not in ("python", "whispercpp"):
            raise ValueError(
                f"Unsupported backend '{self.backend}'. Expected python or whispercpp."
            )
        if not self.model:
            raise ValueError("Worker profile model must be non-empty.")


@dataclass(frozen=True)
class SupervisorSettings:
    """Configuration for worker command generation and process execution."""

    python_executable: str
    worker_script: str
    key_combination: str = "ctrl_l+alt_l"
    runtime_mode: str = "headless"
    whispercpp_cli: str | None = None
    whispercpp_args: str = DEFAULT_WHISPERCPP_ARGS
    whispercpp_timeout_sec: int = 120
    fallback_backend: str = "python"
    disable_backend_fallback: bool = False
    extra_worker_args: tuple[str, ...] = field(default_factory=tuple)
    working_directory: str | None = None
    worker_log_file: str | None = None


@dataclass(frozen=True)
class WorkerStatus:
    """Snapshot of current worker state."""

    running: bool
    pid: int | None
    profile_name: str
    backend: str
    model: str
    restart_attempts: int
    max_restart_attempts: int
    acceleration: str
    reported_model: str | None
    warning: str | None


def default_cpp_models_dir() -> Path:
    """Return default whisper.cpp model directory on the current OS."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "whispercpp" / "models"
    return Path.home() / ".whispercpp" / "models"


def resolve_cpp_model_path(model_value: str, models_dir: str | Path | None = None) -> str:
    """Resolve model alias or path into existing whisper.cpp model file path."""
    if not model_value:
        raise ValueError("cpp model value must be non-empty")

    provided = Path(model_value).expanduser()
    if provided.exists():
        return str(provided.resolve())

    base_dir = Path(models_dir) if models_dir is not None else default_cpp_models_dir()
    alias = model_value.lower().strip()
    model_file = KNOWN_CPP_MODEL_FILES.get(alias)
    if model_file is None:
        normalized = alias
        if normalized.endswith(".bin"):
            model_file = normalized
        elif normalized.startswith("ggml-"):
            model_file = f"{normalized}.bin"
        else:
            model_file = f"ggml-{normalized}.bin"

    candidate = (base_dir / model_file).resolve()
    if not candidate.exists():
        raise FileNotFoundError(
            f"Could not resolve whisper.cpp model '{model_value}' under '{base_dir}'."
        )
    return str(candidate)


def discover_cpp_model_profiles(models_dir: str | Path | None = None) -> list[WorkerProfile]:
    """Discover known whisper.cpp model profiles from local model directory."""
    base_dir = Path(models_dir) if models_dir is not None else default_cpp_models_dir()
    profiles: list[WorkerProfile] = []
    for alias, model_file in KNOWN_CPP_MODEL_FILES.items():
        candidate = (base_dir / model_file).resolve()
        if candidate.exists():
            profiles.append(
                WorkerProfile(
                    name=f"cpp-{alias}",
                    backend="whispercpp",
                    model=str(candidate),
                )
            )
    return profiles


def build_worker_command(profile: WorkerProfile, settings: SupervisorSettings) -> list[str]:
    """Build worker launch command for a selected profile."""
    if settings.runtime_mode not in ("auto", "headless", "tray"):
        raise ValueError(
            f"Unsupported runtime_mode '{settings.runtime_mode}'."
        )

    command = [
        settings.python_executable,
        settings.worker_script,
        "--backend",
        profile.backend,
        "--runtime-mode",
        settings.runtime_mode,
        "-k",
        settings.key_combination,
    ]

    if profile.backend == "python":
        command.extend(["-m", profile.model])
    elif profile.backend == "whispercpp":
        if not settings.whispercpp_cli:
            raise ValueError(
                "whispercpp profile requires whispercpp_cli in supervisor settings."
            )
        command.extend(
            [
                "--whispercpp-cli",
                settings.whispercpp_cli,
                "--whispercpp-model",
                profile.model,
                "--whispercpp-args",
                settings.whispercpp_args,
                "--whispercpp-timeout-sec",
                str(settings.whispercpp_timeout_sec),
                "--fallback-backend",
                settings.fallback_backend,
            ]
        )
        if settings.disable_backend_fallback:
            command.append("--disable-backend-fallback")

    if settings.extra_worker_args:
        command.extend(settings.extra_worker_args)

    return command


class WorkerProcessSupervisor:
    """Controls worker process lifecycle and bounded crash restarts."""

    def __init__(
        self,
        settings: SupervisorSettings,
        initial_profile: WorkerProfile,
        *,
        auto_restart: bool = True,
        max_restart_attempts: int = 3,
        restart_backoff_sec: float = 2.0,
        popen_factory: Callable[..., subprocess.Popen] = subprocess.Popen,
        sleep_fn: Callable[[float], None] = time.sleep,
        logger: logging.Logger | None = None,
    ) -> None:
        self.settings = settings
        self._profile = initial_profile
        self.auto_restart = auto_restart
        self.max_restart_attempts = max_restart_attempts
        self.restart_backoff_sec = restart_backoff_sec
        self._popen_factory = popen_factory
        self._sleep_fn = sleep_fn
        self._logger = logger or logging.getLogger(__name__)

        self._lock = threading.Lock()
        self._monitor_stop_event = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        self._process: subprocess.Popen | None = None
        self._intentional_stop = False
        self._restart_attempts = 0
        self._worker_log_handle = None
        self._worker_log_path: Path | None = None
        self._worker_log_read_pos = 0
        self._acceleration_state = "unknown"
        self._reported_model: str | None = None
        self._warning_message: str | None = None

    @property
    def profile(self) -> WorkerProfile:
        with self._lock:
            return self._profile

    def set_profile(self, profile: WorkerProfile) -> None:
        with self._lock:
            self._profile = profile

    def status_snapshot(self) -> WorkerStatus:
        with self._lock:
            running = self._is_running_locked()
            pid = self._process.pid if running and self._process is not None else None
            return WorkerStatus(
                running=running,
                pid=pid,
                profile_name=self._profile.name,
                backend=self._profile.backend,
                model=self._profile.model,
                restart_attempts=self._restart_attempts,
                max_restart_attempts=self.max_restart_attempts,
                acceleration=self._acceleration_state,
                reported_model=self._reported_model,
                warning=self._warning_message,
            )

    def start_worker(self, reason: str = "manual-start") -> bool:
        with self._lock:
            if self._is_running_locked():
                return False
            self._spawn_locked(reason=reason, reset_restart_attempts=True)
            self._ensure_monitor_thread_locked()
            return True

    def stop_worker(self, reason: str = "manual-stop", timeout_sec: float = 12.0) -> bool:
        with self._lock:
            process = self._process
            self._intentional_stop = True
            if process is None or process.poll() is not None:
                self._process = None
                return False

        self._logger.info("Stopping worker (%s), pid=%s", reason, process.pid)
        process.terminate()
        try:
            process.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            self._logger.warning(
                "Worker did not stop in %.1fs, forcing kill (pid=%s).",
                timeout_sec,
                process.pid,
            )
            process.kill()
            process.wait(timeout=5)

        with self._lock:
            if self._process is process:
                self._process = None
            self._intentional_stop = False
        return True

    def restart_worker(
        self,
        new_profile: WorkerProfile | None = None,
        reason: str = "manual-restart",
    ) -> None:
        if new_profile is not None:
            self.set_profile(new_profile)
        self.stop_worker(reason=f"{reason}:stop")
        self.start_worker(reason=f"{reason}:start")

    def switch_profile(self, new_profile: WorkerProfile) -> None:
        self.restart_worker(new_profile=new_profile, reason=f"profile-switch:{new_profile.name}")

    def check_worker_health(self) -> bool:
        """Observe worker state and apply bounded crash restart policy."""
        should_restart = False
        attempt_no = 0
        with self._lock:
            process = self._process
            if process is None:
                return False

            exit_code = process.poll()
            if exit_code is None:
                return False

            self._process = None

            if self._intentional_stop:
                self._intentional_stop = False
                self._logger.info("Worker exited after intentional stop, code=%s.", exit_code)
                return False

            if not self.auto_restart:
                self._logger.error(
                    "Worker exited unexpectedly with code=%s, auto-restart disabled.",
                    exit_code,
                )
                return False

            if self._restart_attempts >= self.max_restart_attempts:
                self._logger.error(
                    "Worker exited unexpectedly with code=%s; retry limit reached (%s).",
                    exit_code,
                    self.max_restart_attempts,
                )
                return False

            self._restart_attempts += 1
            attempt_no = self._restart_attempts
            should_restart = True

        if should_restart:
            self._logger.warning(
                "Worker crashed; scheduling auto-restart attempt %s/%s in %.1fs.",
                attempt_no,
                self.max_restart_attempts,
                self.restart_backoff_sec,
            )
            self._sleep_fn(self.restart_backoff_sec)
            with self._lock:
                if self._process is None and not self._intentional_stop:
                    self._spawn_locked(
                        reason=f"auto-restart-{attempt_no}",
                        reset_restart_attempts=False,
                    )
                    return True
        return False

    def shutdown(self) -> None:
        """Shutdown monitor thread and worker process."""
        self._monitor_stop_event.set()
        self.stop_worker(reason="supervisor-shutdown")
        thread = self._monitor_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        with self._lock:
            if self._worker_log_handle is not None:
                self._worker_log_handle.close()
                self._worker_log_handle = None

    def _ensure_monitor_thread_locked(self) -> None:
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="worker-supervisor-monitor",
            daemon=True,
        )
        self._monitor_thread.start()

    def _monitor_loop(self) -> None:
        while not self._monitor_stop_event.is_set():
            try:
                self._consume_worker_status_events()
                self.check_worker_health()
            except Exception:  # pragma: no cover - safety net
                self._logger.exception("Supervisor monitor loop failed.")
            self._sleep_fn(1.0)

    def _spawn_locked(self, *, reason: str, reset_restart_attempts: bool) -> None:
        command = build_worker_command(self._profile, self.settings)
        if reset_restart_attempts:
            self._restart_attempts = 0
        self._intentional_stop = False
        self._reported_model = (
            Path(self._profile.model).name
            if self._profile.backend == "whispercpp"
            else self._profile.model
        )
        self._acceleration_state = "pending" if self._profile.backend == "whispercpp" else "n/a"
        self._warning_message = self._preflight_warning_for_profile(self._profile)
        if self._warning_message:
            self._logger.warning("%s", self._warning_message)
        self._ensure_worker_log_handle_locked()

        assert self._worker_log_handle is not None
        self._worker_log_handle.write(f"[{time.strftime('%H:%M:%S')}] START {reason}\n")
        self._worker_log_handle.write(" ".join(command) + "\n")
        self._worker_log_handle.flush()
        self._worker_log_read_pos = self._worker_log_handle.tell()

        popen_kwargs = {
            "cwd": self.settings.working_directory
            or str(Path(self.settings.worker_script).resolve().parent),
            "stdout": self._worker_log_handle,
            "stderr": subprocess.STDOUT,
        }
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        self._process = self._popen_factory(command, **popen_kwargs)
        self._logger.info(
            "Worker started (%s), pid=%s, profile=%s.",
            reason,
            self._process.pid,
            self._profile.name,
        )

    def _ensure_worker_log_handle_locked(self) -> None:
        if self._worker_log_handle is not None and not self._worker_log_handle.closed:
            return

        log_path = self.settings.worker_log_file
        if not log_path:
            log_path = str(Path.home() / ".whisper-dictation-worker.log")

        path = Path(log_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._worker_log_path = path
        self._worker_log_handle = path.open("a", encoding="utf-8")
        self._worker_log_read_pos = self._worker_log_handle.tell()

    def _is_running_locked(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def _preflight_warning_for_profile(self, profile: WorkerProfile) -> str | None:
        if profile.backend != "whispercpp":
            return None
        if "-oved" not in self.settings.whispercpp_args.lower():
            return None

        model_path = Path(profile.model).expanduser()
        base_stem = model_path.stem
        xml_path = model_path.with_name(f"{base_stem}-encoder-openvino.xml")
        bin_path = model_path.with_name(f"{base_stem}-encoder-openvino.bin")
        missing = [str(path) for path in (xml_path, bin_path) if not path.exists()]
        if not missing:
            return None

        return (
            "OpenVINO encoder artifacts missing; whisper.cpp may run in CPU fallback. "
            f"Missing: {', '.join(missing)}"
        )

    def _consume_worker_status_events(self) -> None:
        path = self._worker_log_path
        if path is None or not path.exists():
            return

        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            handle.seek(self._worker_log_read_pos)
            new_lines = handle.readlines()
            self._worker_log_read_pos = handle.tell()

        for raw_line in new_lines:
            line = raw_line.strip()
            if not line.startswith(f"{WHISPERCPP_STATUS_PREFIX} "):
                continue
            fields = self._parse_status_fields(line)
            loaded_model = fields.get("loaded_model")
            acceleration = fields.get("acceleration")
            model_match = fields.get("model_match")
            reason = fields.get("reason", "unknown")

            with self._lock:
                if loaded_model:
                    self._reported_model = loaded_model
                if acceleration:
                    self._acceleration_state = acceleration

                if model_match == "false":
                    self._warning_message = (
                        "Worker loaded model differs from selected profile: "
                        f"selected={Path(self._profile.model).name}, "
                        f"loaded={self._reported_model or 'unknown'}"
                    )
                elif acceleration == "cpu_fallback":
                    self._warning_message = (
                        "whisper.cpp running in CPU fallback mode "
                        f"(reason={reason}, model={self._reported_model or 'unknown'})"
                    )
                elif acceleration == "gpu_openvino":
                    self._warning_message = None

    @staticmethod
    def _parse_status_fields(line: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for token in line.split()[1:]:
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            fields[key] = value
        return fields
