#!/usr/bin/env python3
"""Evaluate benchmark report against rollout gate thresholds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate windows acceleration benchmark report against gate criteria."
    )
    parser.add_argument("--report", type=Path, required=True, help="Path to benchmark JSON report.")
    parser.add_argument(
        "--candidate-backend",
        type=str,
        default="whispercpp-openvino-gpu",
        help="Accelerated backend name to evaluate.",
    )
    parser.add_argument(
        "--max-median-ratio",
        type=float,
        default=0.35,
        help="Max allowed candidate/python median latency ratio.",
    )
    parser.add_argument(
        "--min-quality-p10",
        type=float,
        default=0.60,
        help="Minimum quality p10 required for candidate backend.",
    )
    parser.add_argument(
        "--max-below-threshold-count",
        type=int,
        default=1,
        help="Maximum allowed sample count below quality threshold.",
    )
    return parser.parse_args()


def evaluate_gate(
    report: dict,
    candidate_backend: str,
    max_median_ratio: float,
    min_quality_p10: float,
    max_below_threshold_count: int,
) -> tuple[bool, list[str]]:
    results = report.get("results", [])
    python_result = next((r for r in results if r.get("backend") == "python-whisper"), None)
    candidate_result = next((r for r in results if r.get("backend") == candidate_backend), None)

    reasons: list[str] = []
    passed = True

    if python_result is None:
        return False, ["Missing python-whisper baseline in report."]
    if candidate_result is None:
        return False, [f"Missing candidate backend '{candidate_backend}' in report."]

    py_median = python_result.get("latency_median_s")
    c_median = candidate_result.get("latency_median_s")
    if not py_median or not c_median:
        return False, ["Missing median latency in report results."]

    ratio = c_median / py_median
    if ratio > max_median_ratio:
        passed = False
        reasons.append(
            f"Latency ratio too high: candidate/python={ratio:.3f} > {max_median_ratio:.3f}"
        )
    else:
        reasons.append(
            f"Latency ratio OK: candidate/python={ratio:.3f} <= {max_median_ratio:.3f}"
        )

    quality = candidate_result.get("quality") or {}
    quality_p10 = quality.get("similarity_p10")
    below_count = quality.get("below_0_6_count")
    if quality_p10 is None:
        passed = False
        reasons.append("Missing candidate quality p10 metric.")
    elif quality_p10 < min_quality_p10:
        passed = False
        reasons.append(
            f"Quality p10 too low: {quality_p10:.3f} < {min_quality_p10:.3f}"
        )
    else:
        reasons.append(f"Quality p10 OK: {quality_p10:.3f} >= {min_quality_p10:.3f}")

    if below_count is None:
        passed = False
        reasons.append("Missing candidate below-threshold count metric.")
    elif below_count > max_below_threshold_count:
        passed = False
        reasons.append(
            f"Too many low-quality samples: {below_count} > {max_below_threshold_count}"
        )
    else:
        reasons.append(
            f"Low-quality sample count OK: {below_count} <= {max_below_threshold_count}"
        )

    if (candidate_result.get("failure_count") or 0) > 0:
        passed = False
        reasons.append(
            f"Candidate backend has failures: {candidate_result.get('failure_count')}"
        )
    else:
        reasons.append("Candidate backend failure count OK: 0")

    return passed, reasons


def main() -> int:
    args = parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))

    passed, reasons = evaluate_gate(
        report=report,
        candidate_backend=args.candidate_backend,
        max_median_ratio=args.max_median_ratio,
        min_quality_p10=args.min_quality_p10,
        max_below_threshold_count=args.max_below_threshold_count,
    )
    print("Benchmark gate:", "PASS" if passed else "FAIL")
    for line in reasons:
        print("-", line)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
