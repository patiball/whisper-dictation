#!/usr/bin/env python3
"""
Test performance script for whisper dictation
Measures transcription time and language detection accuracy
"""

import argparse
import os
import subprocess
import tempfile
import time
import wave

import numpy as np


def test_transcription_performance(
    audio_file, model_path, language=None, expected_language=None
):
    """
    Test transcription performance for a given audio file

    Returns:
        dict: {
            'audio_duration': float,
            'transcription_time': float,
            'text': str,
            'detected_language': str,
            'speed_ratio': float  # transcription_time / audio_duration
        }
    """

    # Get audio duration
    with wave.open(audio_file, "rb") as wav:
        frames = wav.getnframes()
        sample_rate = wav.getframerate()
        audio_duration = frames / sample_rate

    # Prepare whisper-cli command
    cmd = [
        "/opt/homebrew/bin/whisper-cli",
        "-m",
        model_path,
        "-nt",  # No timestamps
        "-t",
        "8",  # Use 8 threads for M1
        audio_file,
    ]

    # Add language if specified
    if language:
        cmd.insert(-1, "-l")
        cmd.insert(-1, language)
        cmd.insert(-1, "-np")  # No prints for clean output

    print(f"Testing: {os.path.basename(audio_file)}")
    print(f"Audio duration: {audio_duration:.2f}s")
    print(f"Language: {language or 'auto-detect'}")

    # Run transcription
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    transcription_time = time.time() - start_time

    detected_language = None
    text = ""

    if result.returncode == 0:
        text = result.stdout.strip()

        # Try to extract detected language from stderr
        if not language:  # Only if we're auto-detecting
            for line in result.stderr.split("\n"):
                if "auto-detected language:" in line.lower():
                    if "auto-detected language:" in line:
                        lang_start = line.find("auto-detected language:") + len(
                            "auto-detected language:"
                        )
                        detected_language = line[lang_start:].strip().split()[0]
                        break
    else:
        print(f"Error: {result.stderr}")
        return None

    speed_ratio = transcription_time / audio_duration

    results = {
        "audio_duration": audio_duration,
        "transcription_time": transcription_time,
        "text": text,
        "detected_language": detected_language or language,
        "speed_ratio": speed_ratio,
        "real_time_factor": speed_ratio,  # compatibility
    }

    print(f"Transcription time: {transcription_time:.2f}s")
    print(f"Speed ratio: {speed_ratio:.2f}x (lower is better)")
    print(f"Text: '{text}'")
    print(f"Detected language: {detected_language or language}")

    # Language accuracy check
    if expected_language and detected_language:
        language_correct = detected_language == expected_language
        print(
            f"Language detection: {'✓' if language_correct else '✗'} (expected: {expected_language})"
        )
        results["language_correct"] = language_correct

    print("-" * 50)
    return results


def download_model_if_needed(model_name):
    """Download model for whisper.cpp if it doesn't exist"""
    models_dir = os.path.expanduser("~/.whisper-models")
    os.makedirs(models_dir, exist_ok=True)

    model_mapping = {
        "tiny": "ggml-tiny.bin",
        "base": "ggml-base.bin",
        "small": "ggml-small.bin",
        "medium": "ggml-medium.bin",
        "large": "ggml-large-v3.bin",
    }

    model_file = model_mapping.get(model_name, "ggml-base.bin")
    model_path = os.path.join(models_dir, model_file)

    if not os.path.exists(model_path):
        print(f"Downloading model {model_name}...")
        url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_file}"
        subprocess.run(["curl", "-L", "-o", model_path, url], check=True)
        print(f"Model {model_name} downloaded to {model_path}")

    return model_path


def main():
    parser = argparse.ArgumentParser(
        description="Test whisper transcription performance"
    )
    parser.add_argument(
        "-m",
        "--model",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use",
    )
    parser.add_argument(
        "--audio-files",
        nargs="+",
        help="Audio files to test (if not provided, uses test files in current dir)",
    )

    args = parser.parse_args()

    # Get model path
    model_path = download_model_if_needed(args.model)

    # Find test audio files
    if args.audio_files:
        audio_files = args.audio_files
    else:
        # Look for test files in current directory
        audio_files = []
        for file in os.listdir("."):
            if file.startswith("test_") and file.endswith(".wav"):
                audio_files.append(file)

        if not audio_files:
            print(
                "No test audio files found. Please provide --audio-files or create test_*.wav files"
            )
            return

    print(f"Testing with model: {args.model}")
    print(f"Model path: {model_path}")
    print("=" * 60)

    all_results = []

    for audio_file in audio_files:
        if not os.path.exists(audio_file):
            print(f"File not found: {audio_file}")
            continue

        # Determine expected language from filename
        expected_language = None
        if "polish" in audio_file.lower():
            expected_language = "pl"
        elif "english" in audio_file.lower():
            expected_language = "en"

        # Test auto-detection
        print(f"\n--- AUTO-DETECTION TEST ---")
        result_auto = test_transcription_performance(
            audio_file, model_path, language=None, expected_language=expected_language
        )
        if result_auto:
            result_auto["test_type"] = "auto-detection"
            result_auto["audio_file"] = audio_file
            all_results.append(result_auto)

        # Test with explicit language (if we know expected language)
        if expected_language:
            print(f"\n--- EXPLICIT LANGUAGE TEST ({expected_language}) ---")
            result_explicit = test_transcription_performance(
                audio_file,
                model_path,
                language=expected_language,
                expected_language=expected_language,
            )
            if result_explicit:
                result_explicit["test_type"] = f"explicit-{expected_language}"
                result_explicit["audio_file"] = audio_file
                all_results.append(result_explicit)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for result in all_results:
        print(
            f"{result['audio_file']} ({result['test_type']}): "
            f"{result['transcription_time']:.2f}s "
            f"({result['speed_ratio']:.2f}x) - "
            f"'{result['text'][:50]}{'...' if len(result['text']) > 50 else ''}'"
        )

    # Average performance
    if all_results:
        avg_speed = sum(r["speed_ratio"] for r in all_results) / len(all_results)
        print(f"\nAverage speed ratio: {avg_speed:.2f}x")

        # Language detection accuracy
        correct_detections = sum(
            1 for r in all_results if r.get("language_correct", True)
        )
        total_detections = len([r for r in all_results if "language_correct" in r])
        if total_detections > 0:
            accuracy = correct_detections / total_detections * 100
            print(
                f"Language detection accuracy: {accuracy:.1f}% ({correct_detections}/{total_detections})"
            )


if __name__ == "__main__":
    main()
