#!/usr/bin/env python3
import os
import subprocess
import time
import wave
from datetime import datetime

import numpy as np
import pyaudio


def record_test_audio(duration=10, filename_prefix="test"):
    """Nagraj audio testowe i zapisz je na stałe"""
    print(f"🎤 Nagrywanie przez {duration} sekund...")
    print("📣 NAGRAJ TERAZ PO POLSKU:")
    print(
        "   'Jeden, dwa, trzy, cztery, pięć. To jest test aplikacji whisper z językiem polskim.'"
    )

    # Odliczanie
    for i in range(3, 0, -1):
        print(f"🔴 {i}...")
        time.sleep(1)
    print("🎯 NAGRYWAM!")

    # Parametry nagrywania (identyczne z aplikacją)
    frames_per_buffer = 1024
    sample_rate = 16000

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        frames_per_buffer=frames_per_buffer,
        input=True,
    )

    frames = []
    start_time = time.time()

    # Nagrywaj przez określony czas
    while time.time() - start_time < duration:
        data = stream.read(frames_per_buffer)
        frames.append(data)

        # Pokazuj postęp
        elapsed = time.time() - start_time
        remaining = duration - elapsed
        print(f"\r⏰ Pozostało: {remaining:.1f}s", end="", flush=True)

    print("\n✅ Nagrywanie zakończone!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Zapisz plik z timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file = f"{filename_prefix}_{timestamp}.wav"

    with wave.open(audio_file, "wb") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(frames))

    # Sprawdź rozmiar i długość
    file_size = os.path.getsize(audio_file)
    duration_actual = len(b"".join(frames)) / (sample_rate * 2)  # 2 bytes per sample

    print(f"📁 Zapisano: {audio_file}")
    print(f"📊 Rozmiar: {file_size/1024:.1f} KB")
    print(f"⏱️  Długość: {duration_actual:.1f}s")

    return audio_file


def test_whisper_performance(audio_file, model_path):
    """Przetestuj wydajność whisper.cpp z różnymi opcjami"""
    print(f"\n🧪 TESTOWANIE WYDAJNOŚCI: {audio_file}")
    print(f"🤖 Model: {model_path}")

    # Test 1: Wykrywanie języka
    print("\n1️⃣ TEST WYKRYWANIA JĘZYKA...")
    detect_cmd = [
        "/opt/homebrew/bin/whisper-cli",
        "-m",
        model_path,
        "-dl",  # Detect language only
        audio_file,
    ]

    start_time = time.time()
    result = subprocess.run(detect_cmd, capture_output=True, text=True)
    detect_time = time.time() - start_time

    print(f"⏱️  Czas wykrywania: {detect_time:.2f}s")

    # Parse wykryty język
    detected_lang = "unknown"
    for line in result.stderr.split("\n"):
        if "auto-detected language:" in line.lower():
            if "auto-detected language:" in line:
                lang_start = line.find("auto-detected language:") + len(
                    "auto-detected language:"
                )
                detected_lang = line[lang_start:].strip().split()[0]
                print(f"🌍 Wykryty język: {detected_lang}")
                break

    # Test 2: Transkrypcja z wykrytym językiem
    print(f"\n2️⃣ TEST TRANSKRYPCJI Z JĘZYKIEM: {detected_lang}")
    transcribe_cmd = [
        "/opt/homebrew/bin/whisper-cli",
        "-m",
        model_path,
        "-l",
        detected_lang,
        "-nt",  # No timestamps
        "-np",  # No prints for clean output
        audio_file,
    ]

    start_time = time.time()
    result = subprocess.run(transcribe_cmd, capture_output=True, text=True)
    transcribe_time = time.time() - start_time

    print(f"⏱️  Czas transkrypcji: {transcribe_time:.2f}s")
    print(f"📝 Transkrypcja: '{result.stdout.strip()}'")

    # Test 3: Sprawdź czy używa GPU
    print(f"\n3️⃣ TEST WYKORZYSTANIA GPU...")
    gpu_cmd = [
        "/opt/homebrew/bin/whisper-cli",
        "-m",
        model_path,
        "-l",
        detected_lang,
        "-nt",
        audio_file,
    ]

    start_time = time.time()
    result = subprocess.run(gpu_cmd, capture_output=True, text=True)
    gpu_time = time.time() - start_time

    # Sprawdź stderr dla informacji o GPU
    gpu_info = []
    for line in result.stderr.split("\n"):
        if any(
            keyword in line.lower() for keyword in ["gpu", "metal", "apple m1", "cuda"]
        ):
            gpu_info.append(line.strip())

    print(f"⏱️  Czas z GPU info: {gpu_time:.2f}s")
    print("🖥️  Informacje GPU:")
    for info in gpu_info[:5]:  # Pokazuj max 5 linii
        print(f"   {info}")

    # Podsumowanie
    total_time = detect_time + transcribe_time
    print(f"\n📊 PODSUMOWANIE:")
    print(f"   🔍 Wykrywanie: {detect_time:.2f}s")
    print(f"   📝 Transkrypcja: {transcribe_time:.2f}s")
    print(f"   🔺 Łącznie: {total_time:.2f}s")
    print(f"   🌍 Język: {detected_lang}")


def main():
    model_path = "/Users/mprzybyszewski/.whisper-models/ggml-medium.bin"

    print("🎯 ZAAWANSOWANY TEST NAGRYWANIA I TRANSKRYPCJI")
    print("=" * 60)

    # Nagraj audio testowe
    audio_file = record_test_audio(10, "test_polish")

    # Przetestuj wydajność
    test_whisper_performance(audio_file, model_path)

    print(f"\n💾 Plik zachowany: {audio_file}")
    print("📖 Informacje dodane do README.md")


if __name__ == "__main__":
    main()
