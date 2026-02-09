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
