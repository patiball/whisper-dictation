#!/usr/bin/env python3
import pyaudio
import wave
import numpy as np
import subprocess
import tempfile
import os
import time

def record_audio(duration=5, sample_rate=16000):
    """Nagraj audio przez określony czas"""
    print(f"Nagrywanie przez {duration} sekund...")
    print("Powiedz coś po polsku (np. 'To jest test polskiego języka')")
    
    # Odliczanie
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("Nagrywam!")
    
    frames_per_buffer = 1024
    p = pyaudio.PyAudio()
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    frames_per_buffer=frames_per_buffer,
                    input=True)
    
    frames = []
    
    for i in range(0, int(sample_rate / frames_per_buffer * duration)):
        data = stream.read(frames_per_buffer)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("Nagrywanie zakończone!")
    
    # Zapisz do pliku WAV
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_wav_path = temp_wav.name
    
    with wave.open(temp_wav_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return temp_wav_path

def test_language_detection(audio_file, model_path):
    """Przetestuj wykrywanie języka"""
    print(f"\n=== TEST WYKRYWANIA JĘZYKA ===")
    print(f"Plik audio: {audio_file}")
    print(f"Model: {model_path}")
    
    # Test 1: Wykrywanie języka
    print("\n1. Wykrywanie języka...")
    detect_cmd = [
        '/opt/homebrew/bin/whisper-cli',
        '-m', model_path,
        '-dl',  # Detect language only
        audio_file
    ]
    
    try:
        result = subprocess.run(detect_cmd, capture_output=True, text=True, timeout=30)
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
    except Exception as e:
        print(f"Błąd wykrywania języka: {e}")
    
    # Test 2: Transkrypcja bez określenia języka
    print("\n2. Transkrypcja bez określenia języka...")
    transcribe_auto_cmd = [
        '/opt/homebrew/bin/whisper-cli',
        '-m', model_path,
        '-nt',  # No timestamps
        '-np',  # No prints
        audio_file
    ]
    
    try:
        result = subprocess.run(transcribe_auto_cmd, capture_output=True, text=True, timeout=30)
        print(f"Return code: {result.returncode}")
        print(f"TRANSKRYPCJA (auto): {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"Błąd transkrypcji auto: {e}")
    
    # Test 3: Transkrypcja z polskim językiem
    print("\n3. Transkrypcja z językiem polskim...")
    transcribe_pl_cmd = [
        '/opt/homebrew/bin/whisper-cli',
        '-m', model_path,
        '-l', 'pl',  # Polish
        '-nt',  # No timestamps
        '-np',  # No prints
        audio_file
    ]
    
    try:
        result = subprocess.run(transcribe_pl_cmd, capture_output=True, text=True, timeout=30)
        print(f"Return code: {result.returncode}")
        print(f"TRANSKRYPCJA (pl): {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"Błąd transkrypcji PL: {e}")
    
    # Test 4: Transkrypcja z angielskim językiem
    print("\n4. Transkrypcja z językiem angielskim...")
    transcribe_en_cmd = [
        '/opt/homebrew/bin/whisper-cli',
        '-m', model_path,
        '-l', 'en',  # English
        '-nt',  # No timestamps
        '-np',  # No prints
        audio_file
    ]
    
    try:
        result = subprocess.run(transcribe_en_cmd, capture_output=True, text=True, timeout=30)
        print(f"Return code: {result.returncode}")
        print(f"TRANSKRYPCJA (en): {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"Błąd transkrypcji EN: {e}")

def main():
    model_path = "/Users/mprzybyszewski/.whisper-models/ggml-medium.bin"
    
    print("=== TEST WYKRYWANIA JĘZYKA WHISPER.CPP ===")
    print("Ten skrypt nagra 5 sekund audio i przetestuje wykrywanie języka")
    
    # Nagraj audio
    audio_file = record_audio(5)
    
    try:
        # Przetestuj wykrywanie języka
        test_language_detection(audio_file, model_path)
    finally:
        # Wyczyść plik tymczasowy
        if os.path.exists(audio_file):
            os.unlink(audio_file)
            print(f"\nPlik tymczasowy {audio_file} usunięty")

if __name__ == "__main__":
    main()
