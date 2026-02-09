"""Shared runtime and backend contracts for incremental cross-platform work."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RuntimeController(Protocol):
    """Contract for runtime controllers used by keyboard listeners and main loop."""

    started: bool

    def start_app(self, sender: Any) -> None:
        ...

    def stop_app(self, sender: Any) -> None:
        ...

    def toggle(self) -> None:
        ...

    def run(self) -> None:
        ...


@runtime_checkable
class TranscriptionBackend(Protocol):
    """Contract for audio transcription backends used by Recorder."""

    def transcribe(self, audio_data: Any, language: str | None = None) -> Any:
        ...


def validate_runtime_controller(controller: Any) -> RuntimeController:
    """Ensure runtime object satisfies controller contract."""
    required_methods = ("start_app", "stop_app", "toggle", "run")
    for method in required_methods:
        if not hasattr(controller, method):
            raise TypeError(
                f"Runtime controller must implement '{method}' (got {type(controller).__name__})"
            )

    if not hasattr(controller, "started"):
        raise TypeError(
            f"Runtime controller must expose 'started' state (got {type(controller).__name__})"
        )

    return controller


def validate_transcription_backend(backend: Any) -> TranscriptionBackend:
    """Ensure backend object satisfies transcription contract."""
    if not hasattr(backend, "transcribe"):
        raise TypeError(
            f"Transcription backend must implement 'transcribe' (got {type(backend).__name__})"
        )
    return backend


def create_runtime_app(
    system: str,
    recorder: Any,
    languages: Any,
    max_time: Any,
    status_bar_app_cls: Any,
    windows_tray_app_cls: Any,
    headless_runtime_app_cls: Any,
    runtime_mode: str = "auto",
) -> RuntimeController:
    """Create runtime controller based on platform and explicit runtime mode."""
    if runtime_mode not in ("auto", "headless", "tray"):
        raise ValueError(
            f"Unsupported runtime mode '{runtime_mode}'. Expected auto, headless, or tray."
        )

    if runtime_mode == "headless":
        return validate_runtime_controller(
            headless_runtime_app_cls(recorder, languages, max_time)
        )

    if runtime_mode == "tray":
        if system == "Darwin":
            return validate_runtime_controller(
                status_bar_app_cls(recorder, languages, max_time)
            )
        if system == "Windows":
            return validate_runtime_controller(
                windows_tray_app_cls(recorder, languages, max_time)
            )
        raise ValueError(
            f"Tray runtime mode is unsupported on platform '{system}'."
        )

    if system == "Darwin":
        return validate_runtime_controller(
            status_bar_app_cls(recorder, languages, max_time)
        )
    if system == "Windows":
        return validate_runtime_controller(
            windows_tray_app_cls(recorder, languages, max_time)
        )
    return validate_runtime_controller(headless_runtime_app_cls(recorder, languages, max_time))


def create_key_listener(
    use_double_cmd: bool,
    system: str,
    app: RuntimeController,
    key_combination: str,
    double_command_key_listener_cls: Any,
    global_key_listener_cls: Any,
) -> Any:
    """Create keyboard listener strategy while keeping macOS-only rule explicit."""
    if use_double_cmd and system == "Darwin":
        return double_command_key_listener_cls(app)
    return global_key_listener_cls(app, key_combination)
