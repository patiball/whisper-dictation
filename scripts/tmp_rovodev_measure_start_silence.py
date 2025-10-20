#!/usr/bin/env python3
"""
PoC: measure start_silence_ms for multiple short recordings to assess clipping.

Usage:
  python3 scripts/tmp_rovodev_measure_start_silence.py \
      --runs 30 --duration 1.5 --frames-per-buffer 512 --warmup-buffers 2 --rate 16000 \
      --save-wavs false --out temp/start_silence_report.json

Notes:
- Computes start_silence_ms as time from first recorded sample (post warm-up) to first sample
  whose absolute amplitude exceeds 10% of the peak amplitude within the first second of audio.
- If no sample exceeds, returns null for that run.
- Designed for manual diagnostics; not part of automated tests.
"""
import argparse
import json
import os
import time
import wave
from pathlib import Path

import numpy as np
import pyaudio


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, default=30, help="Number of recordings to measure")
    p.add_argument("--duration", type=float, default=1.5, help="Recording duration per run in seconds")
    p.add_argument("--frames-per-buffer", dest="frames_per_buffer", type=int, default=512)
    p.add_argument("--warmup-buffers", dest="warmup_buffers", type=int, default=2)
    p.add_argument("--rate", type=int, default=16000)
    p.add_argument("--channels", type=int, default=1)
    p.add_argument("--save-wavs", dest="save_wavs", type=str, default="false",
                   help="Save individual WAVs under temp/ (true/false)")
    p.add_argument("--out", type=str, default="temp/start_silence_report.json")
    return p.parse_args()


def ensure_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def record_once(rate: int, channels: int, frames_per_buffer: int, warmup_buffers: int, duration: float) -> np.ndarray:
    pa = pyaudio.PyAudio()

    def open_stream(fpb):
        return pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            frames_per_buffer=fpb,
            input=True,
        )

    stream = open_stream(frames_per_buffer)

    # Warm-up: discard first N buffers
    for _ in range(int(warmup_buffers)):
        try:
            _ = stream.read(frames_per_buffer, exception_on_overflow=False)
        except Exception:
            pass

    frames = []
    total_reads = int(duration * rate / frames_per_buffer)

    for _ in range(total_reads):
        try:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)
            frames.append(data)
        except Exception:
            # pad with zeros if read fails to keep length consistent
            frames.append(b"\x00\x00" * frames_per_buffer)

    stream.stop_stream()
    stream.close()
    pa.terminate()

    audio = np.frombuffer(b"".join(frames), dtype=np.int16)
    return audio


def compute_start_silence_ms(audio: np.ndarray, rate: int) -> float | None:
    if audio.size == 0:
        return None
    first_second_len = min(len(audio), rate)
    if first_second_len == 0:
        return None
    window = audio[:first_second_len]
    peak = np.max(np.abs(window)) if first_second_len > 0 else 0
    if peak <= 0:
        return None
    threshold = 0.10 * peak
    # Find first index above threshold
    idxs = np.where(np.abs(window) >= threshold)[0]
    if idxs.size == 0:
        return None
    idx = int(idxs[0])
    ms = (idx / rate) * 1000.0
    return float(ms)


def save_wav(path: str, audio: np.ndarray, rate: int, channels: int):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio.astype(np.int16).tobytes())


def main():
    args = parse_args()
    ensure_dir(args.out)
    save_wavs = str(args.save_wavs).lower() in ("1", "true", "yes", "y")

    results = []
    for i in range(args.runs):
        print(f"[Run {i+1}/{args.runs}] Recording...")
        audio = record_once(
            rate=args.rate,
            channels=args.channels,
            frames_per_buffer=args.frames_per_buffer,
            warmup_buffers=args.warmup_buffers,
            duration=args.duration,
        )
        ss_ms = compute_start_silence_ms(audio, args.rate)
        result = {
            "run": i + 1,
            "frames_per_buffer": args.frames_per_buffer,
            "warmup_buffers": args.warmup_buffers,
            "rate": args.rate,
            "duration": args.duration,
            "start_silence_ms": ss_ms,
        }
        results.append(result)

        if save_wavs:
            wav_path = f"temp/start_silence_{i+1:02d}.wav"
            ensure_dir(wav_path)
            save_wav(wav_path, audio, args.rate, args.channels)
            result["wav_path"] = wav_path

    # Aggregate
    values = [r["start_silence_ms"] for r in results if r["start_silence_ms"] is not None]
    summary = {
        "runs": args.runs,
        "frames_per_buffer": args.frames_per_buffer,
        "warmup_buffers": args.warmup_buffers,
        "rate": args.rate,
        "duration": args.duration,
        "valid_count": len(values),
        "avg_start_silence_ms": float(np.mean(values)) if values else None,
        "p95_start_silence_ms": float(np.percentile(values, 95)) if values else None,
        "results": results,
    }

    ensure_dir(args.out)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved report: {args.out}")
    if values:
        print(f"avg={summary['avg_start_silence_ms']:.1f} ms, p95={summary['p95_start_silence_ms']:.1f} ms over {len(values)}/{args.runs} valid runs")


if __name__ == "__main__":
    main()
