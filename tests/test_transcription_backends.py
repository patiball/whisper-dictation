import subprocess
from pathlib import Path

import numpy as np
import pytest

from transcription_backends import (
    DeterministicFallbackTranscriber,
    WhisperCppTranscriber,
    create_backend_with_fallback,
    create_transcription_backend,
    validate_whispercpp_paths,
)


class DummyTyper:
    def __init__(self):
        self.typed = []

    def type(self, ch):
        self.typed.append(ch)


def test_create_transcription_backend_selects_python():
    backend = create_transcription_backend(
        "python",
        python_backend_factory=lambda: "python-backend",
        whispercpp_backend_factory=lambda: "cpp-backend",
    )
    assert backend == "python-backend"


def test_create_transcription_backend_selects_whispercpp():
    backend = create_transcription_backend(
        "whispercpp",
        python_backend_factory=lambda: "python-backend",
        whispercpp_backend_factory=lambda: "cpp-backend",
    )
    assert backend == "cpp-backend"


def test_create_transcription_backend_rejects_unknown():
    with pytest.raises(ValueError):
        create_transcription_backend(
            "invalid",
            python_backend_factory=lambda: object(),
            whispercpp_backend_factory=lambda: object(),
        )


def test_validate_whispercpp_paths_requires_existing(tmp_path):
    cli = tmp_path / "whisper-cli.exe"
    model = tmp_path / "ggml-base.bin"
    cli.write_text("stub", encoding="utf-8")
    model.write_text("stub", encoding="utf-8")

    resolved_cli, resolved_model = validate_whispercpp_paths(str(cli), str(model))
    assert resolved_cli == str(cli)
    assert resolved_model == str(model)


def test_whispercpp_transcriber_transcribe_contract(tmp_path):
    cli = tmp_path / "whisper-cli.exe"
    model = tmp_path / "ggml-base.bin"
    cli.write_text("stub", encoding="utf-8")
    model.write_text("stub", encoding="utf-8")
    typer = DummyTyper()

    def fake_runner(cmd, capture_output, text, check, timeout):
        output_prefix = Path(cmd[cmd.index("-of") + 1])
        (Path(str(output_prefix) + ".txt")).write_text("hello world", encoding="utf-8")
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout="",
            stderr="whisper_full_with_state: auto-detected language: en (p = 0.99)",
        )

    transcriber = WhisperCppTranscriber(
        cli_path=str(cli),
        model_path=str(model),
        extra_args="-otxt -l auto -oved GPU",
        timeout_sec=10,
        typer=typer,
        runner=fake_runner,
    )

    audio = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(audio_data=audio, language=None)
    assert result["text"] == "hello world"
    assert result["language"] == "en"
    assert result["backend"] == "whispercpp"
    assert "".join(typer.typed).replace(" ", "") == "helloworld"


def test_deterministic_fallback_startup_failure_activates_fallback():
    backend = DeterministicFallbackTranscriber(
        primary_name="whispercpp",
        primary_factory=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
        fallback_name="python",
        fallback_factory=lambda: "python-backend",
        fallback_enabled=True,
    )
    assert backend.active_name == "python"
    assert backend.active_backend == "python-backend"


def test_deterministic_fallback_runtime_failure_switches_once():
    class FailingPrimary:
        def __init__(self):
            self.called = 0

        def transcribe(self, _audio, _language=None):
            self.called += 1
            raise RuntimeError("runtime boom")

    class FallbackBackend:
        def transcribe(self, _audio, _language=None):
            return {"text": "ok", "language": "pl"}

    backend = DeterministicFallbackTranscriber(
        primary_name="whispercpp",
        primary_factory=FailingPrimary,
        fallback_name="python",
        fallback_factory=FallbackBackend,
        fallback_enabled=True,
    )
    result = backend.transcribe(np.zeros(16, dtype=np.float32))
    assert backend.active_name == "python"
    assert result["text"] == "ok"


def test_create_backend_with_fallback_can_disable_fallback():
    with pytest.raises(RuntimeError):
        create_backend_with_fallback(
            selected_backend="whispercpp",
            python_backend_factory=lambda: "python-backend",
            whispercpp_backend_factory=lambda: (_ for _ in ()).throw(RuntimeError("fail")),
            fallback_backend="python",
            fallback_enabled=False,
        )
