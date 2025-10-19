#!/usr/bin/env python3
import sys
import os
sys.path.append('/Users/mprzybyszewski/whisper-dictation')

# Test import
try:
    from whisper_dictation_fast import SpeechTranscriber
    print("✅ Import działa")
except ImportError as e:
    print(f"❌ Import nie działa: {e}")
    sys.exit(1)

# Test inicjalizacji
try:
    model_path = "/Users/mprzybyszewski/.whisper-models/ggml-medium.bin"
    allowed_languages = ["en", "pl"]
    
    transcriber = SpeechTranscriber(model_path, allowed_languages)
    print("✅ SpeechTranscriber zainicjalizowany")
    print(f"✅ Model: {transcriber.model_path}")
    print(f"✅ Dozwolone języki: {transcriber.allowed_languages}")
    
except Exception as e:
    print(f"❌ Błąd inicjalizacji: {e}")
    sys.exit(1)

print("🎯 Test zakończony pomyślnie")
