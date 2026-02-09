#!/usr/bin/env python3
"""Benchmark harness for Epic 19 / Issue 19-02 Windows acceleration spike."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Candidate:
    name: str
    extra_args: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run baseline Python Whisper and whisper.cpp candidate benchmarks on Windows."
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        default=Path("tests/audio"),
        help="Directory containing .wav files for benchmark corpus.",
    )
    parser.add_argument(
        "--audio-pattern",
        type=str,
        default="test_*.wav",
        help="Glob pattern for benchmark audio files.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of repeated runs per file/backend.",
    )
    parser.add_argument(
        "--python-model",
        type=str,
        default="base",
        help="OpenAI Whisper model for Python baseline (e.g. base, medium).",
    )
    parser.add_argument(
        "--python-language",
        type=str,
        default=None,
        help="Optional language code for Python baseline.",
    )
    parser.add_argument(
        "--whispercpp-cli",
        type=str,
        default=None,
        help="Path to whisper-cli binary (defaults to PATH/WHISPER_CLI_BIN auto-detection).",
    )
    parser.add_argument(
        "--whispercpp-model",
        type=str,
        default=None,
        help="Path to whisper.cpp model file (.bin), defaults to WHISPER_CLI_MODEL env.",
    )
    parser.add_argument(
        "--whispercpp-candidate",
        action="append",
        default=[],
        help=(
            "Candidate definition in form NAME=ARG_STRING; "
            "example: default=\"-l en -otxt\" or vulkan=\"-l en -otxt -ngl 99\""
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("memory-bank/docs/benchmarks"),
        help="Directory for benchmark JSON and Markdown reports.",
    )
    parser.add_argument(
        "--quality-files",
        action="append",
        default=[],
        help=(
            "Glob pattern (relative to --audio-dir) for trusted quality subset; "
            "repeat flag for multiple patterns (example: --quality-files \"test_english*.wav\")."
        ),
    )
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.6,
        help="Minimum median similarity required for recommending accelerated backend.",
    )
    return parser.parse_args()


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def audio_duration_seconds(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        return float(frames) / float(rate) if rate else 0.0


def detect_whisper_cli(cli_arg: str | None) -> str | None:
    if cli_arg:
        return cli_arg
    return shutil.which("whisper-cli") or os.environ.get("WHISPER_CLI_BIN")


def parse_candidates(raw_candidates: list[str]) -> list[Candidate]:
    if not raw_candidates:
        return [Candidate(name="whispercpp-default", extra_args=["-otxt"])]

    parsed: list[Candidate] = []
    for raw in raw_candidates:
        if "=" not in raw:
            raise ValueError(
                f"Invalid --whispercpp-candidate value '{raw}'. Expected NAME=ARG_STRING."
            )
        name, arg_string = raw.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError("Candidate NAME cannot be empty.")
        args = shlex.split(arg_string.strip(), posix=False)
        if "-otxt" not in args:
            args.append("-otxt")
        parsed.append(Candidate(name=name, extra_args=args))
    return parsed


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[.,:;!?]", "", text)
    number_map = {
        "jeden": "1",
        "dwa": "2",
        "trzy": "3",
        "cztery": "4",
        "pięć": "5",
        "sześć": "6",
        "siedem": "7",
        "osiem": "8",
        "dziewięć": "9",
        "dziesięć": "10",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }
    for word, digit in number_map.items():
        text = re.sub(r"\b" + re.escape(word) + r"\b", digit, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_similarity(actual: str, expected: str) -> float:
    a_words = set(normalize_text(actual).split())
    e_words = set(normalize_text(expected).split())
    if not a_words or not e_words:
        return 0.0
    overlap = len(a_words.intersection(e_words))
    union = len(a_words.union(e_words))
    return overlap / union if union else 0.0


def resolve_quality_subset(audio_dir: Path, patterns: list[str]) -> set[str]:
    subset: set[str] = set()
    for pattern in patterns:
        for file_path in audio_dir.glob(pattern):
            subset.add(str(file_path))
    return subset


def load_expected_texts(files: list[Path], subset: set[str]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for wav in files:
        key = str(wav)
        if subset and key not in subset:
            continue
        sidecar = wav.with_suffix(".json")
        if not sidecar.exists():
            continue
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("expected_text"):
                expected[key] = str(data["expected_text"])
        except Exception:
            continue
    return expected


def compute_quality_summary(
    backend_result: dict[str, Any], expected_texts: dict[str, str]
) -> dict[str, Any]:
    if not expected_texts:
        return {
            "evaluated_samples": 0,
            "similarity_median": None,
            "similarity_p10": None,
            "below_0_6_count": 0,
        }

    similarities: list[float] = []
    for sample in backend_result.get("samples", []):
        file_path = sample.get("file")
        transcript = sample.get("text", "")
        if sample.get("returncode") != 0:
            continue
        if file_path in expected_texts and transcript:
            similarities.append(text_similarity(transcript, expected_texts[file_path]))

    if not similarities:
        return {
            "evaluated_samples": 0,
            "similarity_median": None,
            "similarity_p10": None,
            "below_0_6_count": 0,
        }

    below = sum(1 for s in similarities if s < 0.6)
    return {
        "evaluated_samples": len(similarities),
        "similarity_median": round(statistics.median(similarities), 4),
        "similarity_p10": round(percentile(similarities, 0.10), 4),
        "below_0_6_count": below,
    }


def benchmark_python(
    files: list[Path], runs: int, model_name: str, language: str | None
) -> dict[str, Any]:
    import librosa
    import whisper

    print(f"[python] loading model '{model_name}'...")
    model = whisper.load_model(model_name)

    samples: list[dict[str, Any]] = []
    latencies: list[float] = []
    failures: list[dict[str, Any]] = []

    for audio_file in files:
        for run_idx in range(runs):
            try:
                audio_data, _ = librosa.load(str(audio_file), sr=16000, mono=True)
                start = time.perf_counter()
                result = model.transcribe(
                    audio_data,
                    language=language,
                    task="transcribe",
                )
                latency = time.perf_counter() - start
                latencies.append(latency)
                samples.append(
                    {
                        "file": str(audio_file),
                        "run": run_idx + 1,
                        "latency_s": round(latency, 4),
                        "text": result.get("text", "").strip(),
                        "text_preview": (result.get("text", "").strip()[:180]),
                        "language": result.get("language"),
                        "returncode": 0,
                    }
                )
            except Exception as exc:
                failures.append(
                    {
                        "file": str(audio_file),
                        "run": run_idx + 1,
                        "error": str(exc)[:300],
                    }
                )
                samples.append(
                    {
                        "file": str(audio_file),
                        "run": run_idx + 1,
                        "latency_s": None,
                        "text": "",
                        "text_preview": "",
                        "language": None,
                        "returncode": 1,
                    }
                )

    return {
        "backend": "python-whisper",
        "runs": runs,
        "sample_count": len(samples),
        "success_count": len(latencies),
        "failure_count": len(failures),
        "latency_median_s": round(statistics.median(latencies), 4) if latencies else 0.0,
        "latency_p95_s": round(percentile(latencies, 0.95), 4) if latencies else 0.0,
        "samples": samples,
        "failures": failures,
    }


def benchmark_whispercpp_candidate(
    files: list[Path], runs: int, cli_path: str, model_path: str, candidate: Candidate
) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    latencies: list[float] = []
    failures: list[dict[str, Any]] = []

    for audio_file in files:
        for run_idx in range(runs):
            with tempfile.TemporaryDirectory(prefix="wd-bench-") as tmp_dir:
                output_prefix = Path(tmp_dir) / f"{audio_file.stem}_{candidate.name}_{run_idx + 1}"
                cmd = [
                    cli_path,
                    "-m",
                    model_path,
                    "-f",
                    str(audio_file),
                    "-of",
                    str(output_prefix),
                    *candidate.extra_args,
                ]
                start = time.perf_counter()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                latency = time.perf_counter() - start

                txt_path = Path(str(output_prefix) + ".txt")
                text_preview = ""
                if txt_path.exists():
                    text_preview = txt_path.read_text(encoding="utf-8", errors="ignore").strip()[:180]
                elif result.stdout:
                    text_preview = result.stdout.strip()[:180]

                sample = {
                    "file": str(audio_file),
                    "run": run_idx + 1,
                    "latency_s": round(latency, 4),
                    "returncode": result.returncode,
                    "text": text_preview,
                    "text_preview": text_preview,
                }
                samples.append(sample)

                if result.returncode == 0:
                    latencies.append(latency)
                else:
                    failures.append(
                        {
                            "file": str(audio_file),
                            "run": run_idx + 1,
                            "returncode": result.returncode,
                            "stderr": result.stderr.strip()[:300],
                        }
                    )

    return {
        "backend": candidate.name,
        "runs": runs,
        "sample_count": len(samples),
        "success_count": len(latencies),
        "failure_count": len(failures),
        "latency_median_s": round(statistics.median(latencies), 4) if latencies else None,
        "latency_p95_s": round(percentile(latencies, 0.95), 4) if latencies else None,
        "samples": samples,
        "failures": failures,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = []
    lines.append("# Windows Acceleration Benchmark Report")
    lines.append("")
    lines.append(f"- Generated: {report['generated_at']}")
    lines.append(f"- Host platform: {report['platform']}")
    lines.append(f"- Corpus files: {len(report['corpus'])}")
    lines.append(f"- Runs per file: {report['runs']}")
    lines.append("")
    lines.append("## Corpus")
    for item in report["corpus"]:
        lines.append(f"- {item['file']} ({item['duration_s']}s)")
    lines.append("")
    lines.append("## Backend Summary")
    for backend in report["results"]:
        lines.append(
            "- "
            f"{backend['backend']}: median={backend.get('latency_median_s')}s, "
            f"p95={backend.get('latency_p95_s')}s, "
            f"samples={backend.get('sample_count')}, "
            f"failures={backend.get('failure_count', 0)}"
        )
        quality = backend.get("quality")
        if quality and quality.get("evaluated_samples", 0) > 0:
            lines.append(
                "  "
                f"quality: median={quality.get('similarity_median')}, "
                f"p10={quality.get('similarity_p10')}, "
                f"evaluated={quality.get('evaluated_samples')}, "
                f"below_0.6={quality.get('below_0_6_count')}"
            )
    lines.append("")
    lines.append("## Recommendation")
    lines.append(report["recommendation"])
    return "\n".join(lines) + "\n"


def pick_recommendation(
    results: list[dict[str, Any]], quality_threshold: float
) -> str:
    viable = [
        r
        for r in results
        if r.get("latency_median_s") is not None and r.get("failure_count", 0) == 0
    ]
    if not viable:
        return (
            "No fully viable accelerated candidate yet. Keep Python baseline and resolve "
            "whisper.cpp setup/compatibility issues first."
        )

    quality_viable = []
    for result in viable:
        q = result.get("quality")
        if q and q.get("evaluated_samples", 0) > 0:
            if (q.get("similarity_median") or 0.0) >= quality_threshold:
                quality_viable.append(result)
        else:
            quality_viable.append(result)

    if not quality_viable:
        return (
            f"No backend meets quality threshold (median similarity >= {quality_threshold}). "
            "Keep python-whisper as default and improve whisper.cpp language/task configuration."
        )

    best = min(quality_viable, key=lambda r: r["latency_median_s"])
    if best["backend"] == "python-whisper":
        return "Python baseline remains fastest/reliable on this profile; keep it as default for now."
    return (
        f"Use {best['backend']} as primary acceleration candidate for next integration step "
        "(Issue [19-03-00]), with fallback to python-whisper."
    )


def main() -> int:
    args = parse_args()

    files = sorted(args.audio_dir.glob(args.audio_pattern))
    if not files:
        print(f"No audio files found in {args.audio_dir} matching {args.audio_pattern}")
        return 1

    corpus = []
    for file_path in files:
        corpus.append(
            {"file": str(file_path), "duration_s": round(audio_duration_seconds(file_path), 3)}
        )
    quality_subset = resolve_quality_subset(args.audio_dir, args.quality_files)
    expected_texts = load_expected_texts(files, quality_subset)

    results: list[dict[str, Any]] = []
    python_result = (
        benchmark_python(files, args.runs, args.python_model, args.python_language)
    )
    python_result["quality"] = compute_quality_summary(python_result, expected_texts)
    results.append(python_result)

    whisper_cli = detect_whisper_cli(args.whispercpp_cli)
    whisper_model = args.whispercpp_model or os.environ.get("WHISPER_CLI_MODEL")
    candidates = parse_candidates(args.whispercpp_candidate)

    if whisper_cli and whisper_model and Path(whisper_model).exists():
        help_check = subprocess.run(
            [whisper_cli, "--help"], capture_output=True, text=True, check=False
        )
        print(f"[whisper.cpp] presence check return code: {help_check.returncode}")
        for candidate in candidates:
            print(f"[whisper.cpp] benchmarking candidate: {candidate.name}")
            candidate_result = (
                benchmark_whispercpp_candidate(
                    files, args.runs, whisper_cli, whisper_model, candidate
                )
            )
            candidate_result["quality"] = compute_quality_summary(
                candidate_result, expected_texts
            )
            results.append(candidate_result)
    else:
        print(
            "[whisper.cpp] skipped: missing CLI binary or model. "
            "Set --whispercpp-cli and --whispercpp-model (or WHISPER_CLI_MODEL)."
        )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "platform": sys.platform,
        "runs": args.runs,
        "python_model": args.python_model,
        "corpus": corpus,
        "results": results,
        "quality_subset": sorted(list(quality_subset)),
        "quality_threshold": args.quality_threshold,
    }
    report["recommendation"] = pick_recommendation(results, args.quality_threshold)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = args.output_dir / f"windows_acceleration_benchmark_{ts}.json"
    md_path = args.output_dir / f"windows_acceleration_benchmark_{ts}.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(report), encoding="utf-8")

    print(f"Benchmark JSON: {json_path}")
    print(f"Benchmark MD:   {md_path}")
    print(f"Recommendation: {report['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
