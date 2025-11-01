#!/usr/bin/env python3
"""
Debug script to see actual transcription results from test files.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from transcriber import SpeechTranscriber


def main():
    # Initialize transcriber
    print("🔄 Loading transcriber...")
    transcriber = SpeechTranscriber(model_size="base", allowed_languages=["en", "pl"])

    # Find test files
    audio_dir = Path("tests/audio")
    audio_files = list(audio_dir.glob("test_*.wav"))

    print(f"\n📁 Found {len(audio_files)} test files:")

    expected_texts = {
        "polish": "To jest test polskiego języka. Liczby jeden, dwa, trzy, cztery, pięć.",
        "english": "This is an English language test. Numbers one, two, three, four, five.",
        "mixed": "Hello, jak się masz? I am testing mixed language recognition.",
    }

    for audio_file in sorted(audio_files):
        print(f"\n{'='*80}")
        print(f"📄 File: {audio_file.name}")
        print(f"{'='*80}")

        # Determine expected text
        expected_text = "Unknown"
        if "polish" in audio_file.name:
            expected_text = expected_texts["polish"]
        elif "english" in audio_file.name:
            expected_text = expected_texts["english"]
        elif "mixed" in audio_file.name:
            expected_text = expected_texts["mixed"]

        print(f"📝 Expected: {expected_text}")

        try:
            # Transcribe
            print("🔄 Transcribing...")
            result = transcriber.transcribe(str(audio_file))

            print(f"🌍 Detected Language: {result.language}")
            print(f"📤 Transcribed Text: '{result.text}'")
            print(f"⏱️  Detection Time: {result.detection_time:.2f}s")
            print(f"⏱️  Transcription Time: {result.transcription_time:.2f}s")

            # Compare words
            expected_words = expected_text.lower().split()
            transcribed_words = result.text.strip().lower().split()

            print(
                f"📊 Word Count: Expected {len(expected_words)}, Got {len(transcribed_words)}"
            )

            if expected_words and transcribed_words:
                first_match = (
                    expected_words[0] in transcribed_words[0:2]
                    if transcribed_words
                    else False
                )
                last_match = (
                    expected_words[-1].replace(".", "").replace(",", "")
                    in " ".join(transcribed_words[-2:])
                    if transcribed_words
                    else False
                )

                print(
                    f"🎯 First word match: {first_match} ('{expected_words[0]}' vs '{transcribed_words[0] if transcribed_words else 'NONE'}')"
                )
                print(
                    f"🎯 Last word match: {last_match} ('{expected_words[-1]}' vs '{transcribed_words[-1] if transcribed_words else 'NONE'}')"
                )

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
