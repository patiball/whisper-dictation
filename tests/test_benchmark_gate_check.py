import importlib.util
import json
import sys


def load_module():
    spec = importlib.util.spec_from_file_location("benchmark_gate_check", "scripts/benchmark_gate_check.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["benchmark_gate_check"] = module
    spec.loader.exec_module(module)
    return module


def test_evaluate_gate_passes_with_good_metrics():
    module = load_module()
    report = {
        "results": [
            {"backend": "python-whisper", "latency_median_s": 10.0},
            {
                "backend": "whispercpp-openvino-gpu",
                "latency_median_s": 2.0,
                "failure_count": 0,
                "quality": {"similarity_p10": 0.75, "below_0_6_count": 1},
            },
        ]
    }
    ok, reasons = module.evaluate_gate(
        report=report,
        candidate_backend="whispercpp-openvino-gpu",
        max_median_ratio=0.35,
        min_quality_p10=0.60,
        max_below_threshold_count=1,
    )
    assert ok is True
    assert any("Latency ratio OK" in line for line in reasons)


def test_evaluate_gate_fails_on_quality_and_ratio():
    module = load_module()
    report = {
        "results": [
            {"backend": "python-whisper", "latency_median_s": 10.0},
            {
                "backend": "whispercpp-openvino-gpu",
                "latency_median_s": 5.0,
                "failure_count": 0,
                "quality": {"similarity_p10": 0.40, "below_0_6_count": 3},
            },
        ]
    }
    ok, reasons = module.evaluate_gate(
        report=report,
        candidate_backend="whispercpp-openvino-gpu",
        max_median_ratio=0.35,
        min_quality_p10=0.60,
        max_below_threshold_count=1,
    )
    assert ok is False
    assert any("Latency ratio too high" in line for line in reasons)
    assert any("Quality p10 too low" in line for line in reasons)
    assert any("Too many low-quality samples" in line for line in reasons)
