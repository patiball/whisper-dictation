import json
import importlib.util
import sys
import wave
from pathlib import Path
from types import SimpleNamespace


def load_benchmark_module():
    module_path = Path("scripts/windows_acceleration_benchmark.py")
    module_name = "windows_acceleration_benchmark"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def write_test_wav(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 1600)


def test_parse_candidates_adds_otxt_when_missing():
    module = load_benchmark_module()
    candidates = module.parse_candidates(["gpu=-l auto -oved GPU"])
    assert len(candidates) == 1
    assert candidates[0].name == "gpu"
    assert "-otxt" in candidates[0].extra_args


def test_parse_candidates_rejects_invalid_format():
    module = load_benchmark_module()
    try:
        module.parse_candidates(["invalid-format"])
        assert False, "Expected ValueError for invalid candidate format"
    except ValueError as exc:
        assert "Expected NAME=ARG_STRING" in str(exc)


def test_main_skip_python_runs_whispercpp_only(monkeypatch, tmp_path):
    module = load_benchmark_module()

    audio_dir = tmp_path / "audio"
    wav_path = audio_dir / "test_sample.wav"
    write_test_wav(wav_path)

    model_path = tmp_path / "ggml-base.bin"
    model_path.write_bytes(b"stub")

    output_dir = tmp_path / "reports"

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("benchmark_python should not be called with --skip-python")

    def fake_benchmark_whispercpp(*_args, **_kwargs):
        return {
            "backend": "whispercpp-openvino-gpu",
            "runs": 1,
            "sample_count": 1,
            "success_count": 1,
            "failure_count": 0,
            "latency_median_s": 1.0,
            "latency_p95_s": 1.0,
            "samples": [
                {
                    "file": str(wav_path),
                    "run": 1,
                    "latency_s": 1.0,
                    "returncode": 0,
                    "text": "ok",
                    "text_preview": "ok",
                }
            ],
            "failures": [],
        }

    monkeypatch.setattr(module, "benchmark_python", fail_if_called)
    monkeypatch.setattr(module, "benchmark_whispercpp_candidate", fake_benchmark_whispercpp)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    monkeypatch.setattr(
        module.sys,
        "argv",
        [
            "windows_acceleration_benchmark.py",
            "--skip-python",
            "--audio-dir",
            str(audio_dir),
            "--audio-pattern",
            "test_*.wav",
            "--runs",
            "1",
            "--output-dir",
            str(output_dir),
            "--whispercpp-cli",
            "whisper-cli",
            "--whispercpp-model",
            str(model_path),
            "--whispercpp-candidate",
            "whispercpp-openvino-gpu=-otxt -l auto -oved GPU",
        ],
    )

    rc = module.main()
    assert rc == 0

    json_reports = list(output_dir.glob("windows_acceleration_benchmark_*.json"))
    assert json_reports, "Expected benchmark JSON report"
    report = json.loads(json_reports[0].read_text(encoding="utf-8"))
    backends = [item["backend"] for item in report["results"]]
    assert "whispercpp-openvino-gpu" in backends
    assert "python-whisper" not in backends
