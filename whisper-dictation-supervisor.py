"""Supervisor entrypoint for worker lifecycle and fast profile switching."""

from __future__ import annotations

import argparse
import logging
import os
import platform
import sys
import time
from pathlib import Path

from supervisor_worker import (
    WorkerProcessSupervisor,
    WorkerProfile,
    SupervisorSettings,
    discover_cpp_model_profiles,
    resolve_cpp_model_path,
)

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    pystray = None
    Image = None
    ImageDraw = None


PYTHON_MODEL_PRESETS = ("tiny", "base", "small", "medium", "large")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Supervisor process for whisper-dictation worker. "
            "Provides tray-based start/stop/restart and backend/model switching."
        )
    )
    parser.add_argument(
        "--backend",
        choices=("python", "whispercpp"),
        default="whispercpp",
        help="Initial backend profile for worker startup.",
    )
    parser.add_argument(
        "--python-model",
        default="medium",
        choices=PYTHON_MODEL_PRESETS,
        help="Initial python backend model.",
    )
    parser.add_argument(
        "--cpp-model",
        default="large-v3",
        help="Initial whisper.cpp model alias (e.g. base, medium, large-v3) or full path.",
    )
    parser.add_argument(
        "--cpp-model-dir",
        default=str(Path(os.environ.get("LOCALAPPDATA", "")) / "whispercpp" / "models"),
        help="Directory used to resolve whisper.cpp model aliases.",
    )
    parser.add_argument(
        "--key-combination",
        default="ctrl_l+alt_l",
        help="Worker hotkey combination (passed to whisper-dictation.py).",
    )
    parser.add_argument(
        "--python-executable",
        default=sys.executable,
        help="Python executable used to launch worker.",
    )
    parser.add_argument(
        "--worker-script",
        default=str(Path(__file__).resolve().parent / "whisper-dictation.py"),
        help="Path to worker entry script.",
    )
    parser.add_argument(
        "--worker-runtime-mode",
        choices=("headless", "auto"),
        default="headless",
        help="Worker runtime mode. Use headless when supervised from tray.",
    )
    parser.add_argument(
        "--whispercpp-cli",
        default=os.environ.get("WHISPER_CLI_BIN"),
        help="Path to whisper-cli binary (or set WHISPER_CLI_BIN).",
    )
    parser.add_argument(
        "--whispercpp-args",
        default="-otxt -l auto -oved GPU",
        help="Extra args passed to whisper-cli by the worker.",
    )
    parser.add_argument(
        "--whispercpp-timeout-sec",
        type=int,
        default=int(os.environ.get("WHISPER_CLI_TIMEOUT_SEC", "120")),
        help="Per-call timeout for whisper.cpp worker backend.",
    )
    parser.add_argument(
        "--fallback-backend",
        choices=("python", "whispercpp", "none"),
        default="python",
        help="Worker fallback backend policy.",
    )
    parser.add_argument(
        "--disable-backend-fallback",
        action="store_true",
        help="Disable backend fallback in worker process.",
    )
    parser.add_argument(
        "--worker-arg",
        action="append",
        default=[],
        help="Additional arg forwarded to worker (repeatable).",
    )
    parser.add_argument(
        "--max-restart-attempts",
        type=int,
        default=3,
        help="Maximum automatic worker crash restarts.",
    )
    parser.add_argument(
        "--restart-backoff-sec",
        type=float,
        default=2.0,
        help="Delay between automatic crash restart attempts.",
    )
    parser.add_argument(
        "--no-auto-restart",
        action="store_true",
        help="Disable automatic restart after unexpected worker exit.",
    )
    parser.add_argument(
        "--log-file",
        default=str(Path.home() / ".whisper-dictation-supervisor.log"),
        help="Supervisor log file path.",
    )
    parser.add_argument(
        "--worker-log-file",
        default=str(Path.home() / ".whisper-dictation-worker.log"),
        help="Worker stdout/stderr log file path.",
    )
    parser.add_argument(
        "--no-tray",
        action="store_true",
        help="Run supervisor without tray icon (headless supervisor mode).",
    )
    return parser.parse_args(argv)


def configure_logging(log_file: str) -> None:
    path = Path(log_file).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def model_alias_from_path(model_path: str) -> str:
    stem = Path(model_path).stem
    if stem.startswith("ggml-"):
        return stem[len("ggml-") :]
    return stem


def build_initial_profile(args: argparse.Namespace) -> WorkerProfile:
    if args.backend == "python":
        return WorkerProfile(
            name=f"python-{args.python_model}",
            backend="python",
            model=args.python_model,
        )

    model_path = resolve_cpp_model_path(args.cpp_model, args.cpp_model_dir)
    return WorkerProfile(
        name=f"cpp-{model_alias_from_path(model_path)}",
        backend="whispercpp",
        model=model_path,
    )


def build_python_profiles() -> list[WorkerProfile]:
    return [
        WorkerProfile(name=f"python-{model}", backend="python", model=model)
        for model in PYTHON_MODEL_PRESETS
    ]


def build_cpp_profiles(
    args: argparse.Namespace,
    initial_profile: WorkerProfile,
) -> list[WorkerProfile]:
    profiles = discover_cpp_model_profiles(args.cpp_model_dir)
    if (
        initial_profile.backend == "whispercpp"
        and all(p.model != initial_profile.model for p in profiles)
    ):
        profiles.append(initial_profile)
    return sorted(profiles, key=lambda profile: profile.name)


class SupervisorTrayApp:
    """Windows tray app for controlling worker profiles."""

    def __init__(
        self,
        supervisor: WorkerProcessSupervisor,
        python_profiles: list[WorkerProfile],
        cpp_profiles: list[WorkerProfile],
    ) -> None:
        if pystray is None or Image is None or ImageDraw is None:
            raise RuntimeError("Tray mode requires pystray and Pillow.")

        self.supervisor = supervisor
        self.python_profiles = python_profiles
        self.cpp_profiles = cpp_profiles
        self.icon: pystray.Icon | None = None

    def run(self) -> None:
        self.supervisor.start_worker(reason="supervisor-startup")
        self.icon = pystray.Icon(
            "whisper-dictation-supervisor",
            self._create_icon_image(),
            "Whisper Dictation Supervisor",
            self._build_menu(),
        )
        self.icon.run()

    def _create_icon_image(self):
        image = Image.new("RGB", (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 18, 54, 26), fill=(230, 230, 230))
        draw.rectangle((10, 30, 54, 38), fill=(230, 230, 230))
        draw.ellipse((22, 42, 42, 62), fill=(220, 40, 40))
        return image

    def _status_text(self) -> str:
        status = self.supervisor.status_snapshot()
        state = "running" if status.running else "stopped"
        model = status.reported_model or Path(status.model).name
        warning_flag = " | WARN" if status.warning else ""
        return (
            f"Worker: {state} | profile={status.profile_name} "
            f"| model={model} | accel={status.acceleration} "
            f"| retries {status.restart_attempts}/{status.max_restart_attempts}"
            f"{warning_flag}"
        )

    def _warning_text(self) -> str:
        status = self.supervisor.status_snapshot()
        if status.warning:
            return f"Warning: {status.warning}"
        return "Warning: none"

    def _refresh_menu(self) -> None:
        if self.icon is not None:
            self.icon.update_menu()

    def _build_profile_menu(self, profiles: list[WorkerProfile]):
        if not profiles:
            return pystray.Menu(pystray.MenuItem("No profiles found", None, enabled=False))

        items = []
        for profile in profiles:
            items.append(
                pystray.MenuItem(
                    profile.name,
                    self._make_switch_callback(profile),
                    checked=lambda _item, p=profile: self.supervisor.status_snapshot().profile_name
                    == p.name,
                )
            )
        return pystray.Menu(*items)

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(lambda _item: self._status_text(), None, enabled=False),
            pystray.MenuItem(lambda _item: self._warning_text(), None, enabled=False),
            pystray.MenuItem(
                "Start Worker",
                self._on_start_worker,
                enabled=lambda _item: not self.supervisor.status_snapshot().running,
            ),
            pystray.MenuItem(
                "Stop Worker",
                self._on_stop_worker,
                enabled=lambda _item: self.supervisor.status_snapshot().running,
            ),
            pystray.MenuItem("Restart Worker", self._on_restart_worker),
            pystray.MenuItem(
                "Switch to whisper.cpp",
                self._build_profile_menu(self.cpp_profiles),
                enabled=lambda _item: len(self.cpp_profiles) > 0,
            ),
            pystray.MenuItem(
                "Switch to python",
                self._build_profile_menu(self.python_profiles),
                enabled=lambda _item: len(self.python_profiles) > 0,
            ),
            pystray.MenuItem("Exit Supervisor", self._on_exit),
        )

    def _make_switch_callback(self, profile: WorkerProfile):
        def callback(icon, _item):
            try:
                logging.info("Switching worker profile to %s", profile.name)
                self.supervisor.switch_profile(profile)
            except Exception:
                logging.exception("Failed to switch profile to %s", profile.name)
            finally:
                if icon is not None:
                    icon.update_menu()

        return callback

    def _on_start_worker(self, icon, _item):
        self.supervisor.start_worker(reason="tray-start")
        if icon is not None:
            icon.update_menu()

    def _on_stop_worker(self, icon, _item):
        self.supervisor.stop_worker(reason="tray-stop")
        if icon is not None:
            icon.update_menu()

    def _on_restart_worker(self, icon, _item):
        self.supervisor.restart_worker(reason="tray-restart")
        if icon is not None:
            icon.update_menu()

    def _on_exit(self, icon, _item):
        logging.info("Supervisor exit requested from tray")
        self.supervisor.shutdown()
        icon.stop()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_file)

    worker_script = Path(args.worker_script).expanduser().resolve()
    if not worker_script.exists():
        raise FileNotFoundError(f"Worker script not found: {worker_script}")

    if args.backend == "whispercpp" and not args.whispercpp_cli:
        raise ValueError(
            "whispercpp backend requires --whispercpp-cli or WHISPER_CLI_BIN."
        )

    initial_profile = build_initial_profile(args)
    python_profiles = build_python_profiles()
    cpp_profiles = build_cpp_profiles(args, initial_profile)

    settings = SupervisorSettings(
        python_executable=args.python_executable,
        worker_script=str(worker_script),
        key_combination=args.key_combination,
        runtime_mode=args.worker_runtime_mode,
        whispercpp_cli=args.whispercpp_cli,
        whispercpp_args=args.whispercpp_args,
        whispercpp_timeout_sec=args.whispercpp_timeout_sec,
        fallback_backend=args.fallback_backend,
        disable_backend_fallback=args.disable_backend_fallback,
        extra_worker_args=tuple(args.worker_arg),
        working_directory=str(worker_script.parent),
        worker_log_file=args.worker_log_file,
    )
    supervisor = WorkerProcessSupervisor(
        settings=settings,
        initial_profile=initial_profile,
        auto_restart=not args.no_auto_restart,
        max_restart_attempts=args.max_restart_attempts,
        restart_backoff_sec=args.restart_backoff_sec,
    )

    try:
        if args.no_tray:
            logging.info("Starting supervisor in headless mode")
            supervisor.start_worker(reason="headless-supervisor-start")
            while True:
                time.sleep(1)
        else:
            if platform.system() != "Windows":
                raise RuntimeError("Tray supervisor mode is currently supported on Windows.")
            tray = SupervisorTrayApp(
                supervisor=supervisor,
                python_profiles=python_profiles,
                cpp_profiles=cpp_profiles,
            )
            tray.run()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down supervisor")
    finally:
        supervisor.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
