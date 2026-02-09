import importlib.util
import sys

import pytest


def load_module():
    spec = importlib.util.spec_from_file_location("whisper_dictation_main", "whisper-dictation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["whisper_dictation_main"] = module
    spec.loader.exec_module(module)
    return module


def test_parse_args_default_backend_python():
    module = load_module()
    args = module.parse_args([])
    assert args.backend == "python"
    assert args.runtime_mode == "auto"


def test_parse_args_accepts_whispercpp_with_explicit_paths():
    module = load_module()
    args = module.parse_args(
        [
            "--backend",
            "whispercpp",
            "--whispercpp-cli",
            "C:/fake/whisper-cli.exe",
            "--whispercpp-model",
            "C:/fake/ggml-base.bin",
        ]
    )
    assert args.backend == "whispercpp"
    assert args.whispercpp_cli.endswith("whisper-cli.exe")
    assert args.whispercpp_model.endswith("ggml-base.bin")


def test_parse_args_whispercpp_requires_cli_and_model(monkeypatch):
    module = load_module()
    monkeypatch.delenv("WHISPER_CLI_BIN", raising=False)
    monkeypatch.delenv("WHISPER_CLI_MODEL", raising=False)
    monkeypatch.setattr(module.shutil, "which", lambda _name: None)

    with pytest.raises(ValueError):
        module.parse_args(["--backend", "whispercpp"])


def test_parse_args_fallback_controls():
    module = load_module()
    args = module.parse_args(
        [
            "--fallback-backend",
            "python",
            "--disable-backend-fallback",
        ]
    )
    assert args.fallback_backend == "python"
    assert args.backend_fallback_enabled is False


def test_parse_args_accepts_runtime_mode_headless():
    module = load_module()
    args = module.parse_args(["--runtime-mode", "headless"])
    assert args.runtime_mode == "headless"


def test_parse_args_tray_mode_rejected_on_unsupported_platform(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module.platform, "system", lambda: "Linux")
    with pytest.raises(ValueError):
        module.parse_args(["--runtime-mode", "tray"])


def test_console_print_falls_back_on_limited_stdout_encoding(monkeypatch):
    module = load_module()

    class Cp1250Stdout:
        encoding = "cp1250"

        def __init__(self):
            self._parts = []

        def write(self, text):
            text.encode(self.encoding)
            self._parts.append(text)
            return len(text)

        def flush(self):
            return None

        def value(self):
            return "".join(self._parts)

    fake_stdout = Cp1250Stdout()
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    module.console_print("✅ model loaded")

    rendered = fake_stdout.value()
    assert "model loaded" in rendered
    assert "?" in rendered
