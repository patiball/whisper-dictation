"""Backend helpers for pluggable transcription integration."""

from __future__ import annotations

import logging
import re
import shlex
import subprocess
import tempfile
import threading
import time
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
from pynput import keyboard


def _timestamp() -> str:
    """Return formatted timestamp consistent with main runtime prints."""
    return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"


WHISPERCPP_STATUS_PREFIX = "WHISPERCPP_STATUS"


@dataclass(frozen=True)
class WhisperCppRuntimeDiagnostics:
    """Runtime diagnostics inferred from whisper-cli stdout/stderr."""

    expected_model: str
    loaded_model: str
    model_match: bool
    acceleration: str
    reason: str


def create_transcription_backend(
    backend_name: str,
    python_backend_factory: Callable[[], Any],
    whispercpp_backend_factory: Callable[[], Any],
) -> Any:
    """Create backend instance from selection while keeping wiring explicit."""
    if backend_name == "python":
        return python_backend_factory()
    if backend_name == "whispercpp":
        return whispercpp_backend_factory()
    raise ValueError(f"Unsupported backend '{backend_name}'")


class DeterministicFallbackTranscriber:
    """Wrap a primary backend with deterministic fallback behavior."""

    def __init__(
        self,
        primary_name: str,
        primary_factory: Callable[[], Any],
        fallback_name: str,
        fallback_factory: Callable[[], Any],
        fallback_enabled: bool = True,
    ) -> None:
        self.primary_name = primary_name
        self.primary_factory = primary_factory
        self.fallback_name = fallback_name
        self.fallback_factory = fallback_factory
        self.fallback_enabled = fallback_enabled

        self.active_name = primary_name
        self.active_backend: Any | None = None
        self._fallback_activated = False

        try:
            self.active_backend = self.primary_factory()
            logging.info(f"Backend selected: {self.primary_name}")
        except Exception as exc:
            if not self.fallback_enabled:
                logging.error(
                    f"Backend startup failed and fallback disabled: {self.primary_name}: {exc}"
                )
                raise

            logging.warning(
                f"Backend startup failed, activating fallback "
                f"{self.primary_name} -> {self.fallback_name}. Reason: {exc}"
            )
            self.active_backend = self.fallback_factory()
            self.active_name = self.fallback_name
            self._fallback_activated = True
            logging.info(
                f"Fallback activated at startup. Active backend: {self.active_name}"
            )

    def transcribe(self, audio_data: Any, language: str | None = None) -> Any:
        try:
            return self.active_backend.transcribe(audio_data, language)
        except Exception as exc:
            if not self.fallback_enabled:
                logging.error(
                    f"Backend runtime failure with fallback disabled "
                    f"({self.active_name}): {exc}"
                )
                raise

            if self._fallback_activated:
                logging.error(
                    f"Backend runtime failure on already-fallback backend "
                    f"({self.active_name}): {exc}"
                )
                raise

            logging.warning(
                f"Backend runtime failure, activating fallback "
                f"{self.active_name} -> {self.fallback_name}. Reason: {exc}"
            )
            self.active_backend = self.fallback_factory()
            self.active_name = self.fallback_name
            self._fallback_activated = True
            logging.info(
                f"Fallback activated at runtime. Active backend: {self.active_name}"
            )
            return self.active_backend.transcribe(audio_data, language)


def create_backend_with_fallback(
    selected_backend: str,
    python_backend_factory: Callable[[], Any],
    whispercpp_backend_factory: Callable[[], Any],
    fallback_backend: str = "python",
    fallback_enabled: bool = True,
) -> Any:
    """Create selected backend with optional deterministic fallback."""
    if (
        not fallback_enabled
        or fallback_backend == "none"
        or fallback_backend == selected_backend
    ):
        return create_transcription_backend(
            selected_backend,
            python_backend_factory=python_backend_factory,
            whispercpp_backend_factory=whispercpp_backend_factory,
        )

    factories = {
        "python": python_backend_factory,
        "whispercpp": whispercpp_backend_factory,
    }
    if selected_backend not in factories:
        raise ValueError(f"Unsupported backend '{selected_backend}'")
    if fallback_backend not in factories:
        raise ValueError(f"Unsupported fallback backend '{fallback_backend}'")

    return DeterministicFallbackTranscriber(
        primary_name=selected_backend,
        primary_factory=factories[selected_backend],
        fallback_name=fallback_backend,
        fallback_factory=factories[fallback_backend],
        fallback_enabled=fallback_enabled,
    )


def validate_whispercpp_paths(cli_path: str | None, model_path: str | None) -> tuple[str, str]:
    """Validate whisper.cpp runtime paths and return normalized string tuple."""
    if not cli_path:
        raise ValueError("whisper.cpp backend requires --whispercpp-cli or WHISPER_CLI_BIN")
    if not model_path:
        raise ValueError(
            "whisper.cpp backend requires --whispercpp-model or WHISPER_CLI_MODEL"
        )

    cli = Path(cli_path)
    model = Path(model_path)
    if not cli.exists():
        raise ValueError(f"whisper.cpp CLI binary not found: {cli}")
    if not model.exists():
        raise ValueError(f"whisper.cpp model file not found: {model}")

    return str(cli), str(model)


class WhisperCppTranscriber:
    """Transcription backend implementation using whisper-cli subprocess calls."""

    def __init__(
        self,
        cli_path: str,
        model_path: str,
        extra_args: str = "-otxt -l auto -oved GPU",
        timeout_sec: int = 120,
        typer: Any | None = None,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.cli_path, self.model_path = validate_whispercpp_paths(cli_path, model_path)
        self.timeout_sec = timeout_sec
        self.runner = runner
        self._transcribe_lock = threading.Lock()
        self.pykeyboard = typer if typer is not None else keyboard.Controller()

        parsed_args = shlex.split(extra_args.strip(), posix=False) if extra_args else []
        if "-otxt" not in parsed_args:
            parsed_args.append("-otxt")
        self.extra_args = parsed_args

    def _build_command(self, wav_path: Path, output_prefix: Path, language: str | None) -> list[str]:
        cmd = [
            self.cli_path,
            "-m",
            self.model_path,
            "-f",
            str(wav_path),
            "-of",
            str(output_prefix),
        ]

        extra_args = list(self.extra_args)
        if language:
            if "-l" in extra_args:
                idx = extra_args.index("-l")
                if idx + 1 < len(extra_args):
                    extra_args[idx + 1] = language
                else:
                    extra_args.extend(["-l", language])
            else:
                extra_args.extend(["-l", language])

        cmd.extend(extra_args)
        return cmd

    @staticmethod
    def _to_pcm16(audio_data: np.ndarray) -> np.ndarray:
        arr = np.asarray(audio_data, dtype=np.float32).flatten()
        if arr.size == 0:
            return np.zeros(1, dtype=np.int16)
        clipped = np.clip(arr, -1.0, 1.0)
        return (clipped * 32767.0).astype(np.int16)

    @staticmethod
    def _write_wav(path: Path, pcm16: np.ndarray, sample_rate: int = 16000) -> None:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm16.tobytes())

    @staticmethod
    def _detected_language(output: str) -> str | None:
        match = re.search(r"auto-detected language:\s*([a-z]{2})", output, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).lower()

    def _type_text(self, text: str) -> None:
        print(f"{_timestamp()} Typing text...")
        is_first = True
        for element in text:
            if is_first and element == " ":
                is_first = False
                continue
            try:
                self.pykeyboard.type(element)
                time.sleep(0.0025)
            except Exception as exc:
                logging.warning(f"Failed to type character '{element}': {exc}")

    @staticmethod
    def _loaded_model_from_output(output: str) -> str | None:
        match = re.search(r"loading model from '([^']+)'", output, re.IGNORECASE)
        if not match:
            return None
        return Path(match.group(1)).name

    def _runtime_diagnostics(self, output: str) -> WhisperCppRuntimeDiagnostics:
        expected_model = Path(self.model_path).name
        loaded_model = self._loaded_model_from_output(output) or expected_model
        model_match = loaded_model == expected_model

        openvino_loaded = "OpenVINO model loaded" in output
        openvino_failed = (
            "failed to init OpenVINO encoder" in output
            or "Could not open the file" in output and "encoder-openvino" in output
        )

        acceleration = "unknown"
        reason = "unknown"
        if openvino_loaded:
            acceleration = "gpu_openvino"
            reason = "openvino_encoder_loaded"
        elif openvino_failed:
            acceleration = "cpu_fallback"
            reason = "openvino_encoder_init_failed"

        return WhisperCppRuntimeDiagnostics(
            expected_model=expected_model,
            loaded_model=loaded_model,
            model_match=model_match,
            acceleration=acceleration,
            reason=reason,
        )

    @staticmethod
    def _print_runtime_status_line(diag: WhisperCppRuntimeDiagnostics) -> None:
        print(
            f"{WHISPERCPP_STATUS_PREFIX} "
            f"expected_model={diag.expected_model} "
            f"loaded_model={diag.loaded_model} "
            f"model_match={'true' if diag.model_match else 'false'} "
            f"acceleration={diag.acceleration} "
            f"reason={diag.reason}"
        )

    def transcribe(self, audio_data: Any, language: str | None = None) -> dict[str, Any]:
        started_at = time.time()
        with self._transcribe_lock:
            pcm16 = self._to_pcm16(np.asarray(audio_data))
            with tempfile.TemporaryDirectory(prefix="wd-whispercpp-") as temp_dir:
                temp_dir_path = Path(temp_dir)
                wav_path = temp_dir_path / "audio.wav"
                output_prefix = temp_dir_path / "transcript"
                self._write_wav(wav_path, pcm16)

                cmd = self._build_command(wav_path, output_prefix, language)
                try:
                    result = self.runner(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=self.timeout_sec,
                    )
                except subprocess.TimeoutExpired as exc:
                    raise RuntimeError(
                        f"whisper.cpp transcription timed out after {self.timeout_sec}s"
                    ) from exc

                if result.returncode != 0:
                    stderr = (result.stderr or "").strip()
                    raise RuntimeError(
                        f"whisper.cpp transcription failed (rc={result.returncode}): {stderr[:300]}"
                    )

                txt_path = Path(str(output_prefix) + ".txt")
                text = ""
                if txt_path.exists():
                    text = txt_path.read_text(encoding="utf-8", errors="ignore").strip()
                elif result.stdout:
                    text = result.stdout.strip()

                combined_output = "\n".join([(result.stdout or ""), (result.stderr or "")])
                detected_language = self._detected_language(combined_output)
                runtime_diag = self._runtime_diagnostics(combined_output)

        duration = time.time() - started_at
        print(f"{_timestamp()} Transcription complete ({duration:.2f}s)")
        print(
            f"{_timestamp()} whispercpp runtime: "
            f"model={runtime_diag.loaded_model} "
            f"accel={runtime_diag.acceleration}"
        )
        self._print_runtime_status_line(runtime_diag)

        if not runtime_diag.model_match:
            logging.warning(
                "whisper.cpp loaded model differs from configured model: "
                "expected=%s loaded=%s",
                runtime_diag.expected_model,
                runtime_diag.loaded_model,
            )
        if runtime_diag.acceleration == "cpu_fallback":
            logging.warning(
                "whisper.cpp is running in CPU fallback mode. reason=%s",
                runtime_diag.reason,
            )

        self._type_text(text)
        return {
            "text": text,
            "language": detected_language or language or "auto",
            "backend": "whispercpp",
            "model": runtime_diag.loaded_model,
            "expected_model": runtime_diag.expected_model,
            "acceleration": runtime_diag.acceleration,
            "acceleration_reason": runtime_diag.reason,
        }
