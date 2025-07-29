#!/usr/bin/env python3
"""
Tool for recording controlled test audio samples for TDD testing.
This script helps create precise audio recordings with known texts.
"""

import time
import sys
import wave
import pyaudio
from pathlib import Path
import json
from datetime import datetime

class TestSampleRecorder:
    def __init__(self, output_dir="tests/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio recording parameters
        self.sample_rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk_size = 1024
        
        # Test texts to record
        self.test_texts = {
            'polish_5s': "To jest test polskiego języka. Liczby jeden, dwa, trzy, cztery, pięć.",
            'english_5s': "This is an English language test. Numbers one, two, three, four, five.",
            'mixed_5s': "Hello, jak się masz? I am testing mixed language recognition.",
            'polish_10s': "To jest dłuższy test polskiego języka. Będę mówić przez około dziesięć sekund. Liczby: jeden, dwa, trzy, cztery, pięć, sześć, siedem, osiem, dziewięć, dziesięć.",
            'english_10s': "This is a longer English language test. I will speak for approximately ten seconds. Numbers: one, two, three, four, five, six, seven, eight, nine, ten.",
            'immediate_start': "Start immediately with these exact words"
        }
        
        self.audio = pyaudio.PyAudio()

    def display_text_and_countdown(self, text, countdown_seconds=3):
        """Display text to read and countdown before recording."""
        print("\n" + "="*80)
        print("PRZYGOTUJ SIĘ DO NAGRANIA:")
        print(f"TEKST DO PRZECZYTANIA: '{text}'")
        print("="*80)
        print("\nZacznij mówić NATYCHMIAST po sygnale 'START!'")
        print("Przeczytaj tekst wyraźnie i w normalnym tempie.")
        
        for i in range(countdown_seconds, 0, -1):
            print(f"\nNagranie rozpocznie się za: {i}...")
            time.sleep(1)
        
        print("\n🔴 START! MÓWISZ TERAZ!")
        
    def record_audio(self, duration_seconds, filename):
        """Record audio for specified duration."""
        frames = []
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print(f"⏺️  Nagrywanie przez {duration_seconds} sekund...")
        
        start_time = time.time()
        for i in range(0, int(self.sample_rate / self.chunk_size * duration_seconds)):
            data = stream.read(self.chunk_size)
            frames.append(data)
            
            # Show progress
            elapsed = time.time() - start_time
            if int(elapsed) != int(elapsed - 0.1):  # Print every second
                remaining = max(0, duration_seconds - elapsed)
                print(f"⏰ Pozostało: {remaining:.1f}s", end='\r')
        
        print("\n✅ Nagranie zakończone!")
        
        stream.stop_stream()
        stream.close()
        
        # Save to file
        filepath = self.output_dir / filename
        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
        
        print(f"💾 Zapisano: {filepath}")
        return filepath

    def record_test_sample(self, test_key, duration=5):
        """Record a single test sample with controlled text."""
        text = self.test_texts[test_key]
        filename = f"test_{test_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        print(f"\n{'='*60}")
        print(f"NAGRANIE PRÓBKI: {test_key}")
        print(f"{'='*60}")
        
        self.display_text_and_countdown(text)
        filepath = self.record_audio(duration, filename)
        
        # Save metadata
        metadata = {
            'test_key': test_key,
            'expected_text': text,
            'filename': filename,
            'duration': duration,
            'sample_rate': self.sample_rate,
            'recorded_at': datetime.now().isoformat()
        }
        
        metadata_file = filepath.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Metadata: {metadata_file}")
        return filepath, metadata

    def record_all_samples(self):
        """Record all test samples interactively."""
        print("🎙️  NAGRYWANIE PRÓBEK TESTOWYCH DLA TDD")
        print("=" * 50)
        print("Zostaniesz poproszony o nagranie kilku próbek audio.")
        print("Każda próbka będzie miała dokładny tekst do przeczytania.")
        print("Ważne: Zacznij mówić NATYCHMIAST po sygnale 'START!'")
        
        results = {}
        
        # Record samples with different durations
        samples_to_record = [
            ('polish_5s', 5),
            ('english_5s', 5),
            ('mixed_5s', 5),
            ('immediate_start', 3),  # Shorter for start testing
            ('polish_10s', 10),
            ('english_10s', 10)
        ]
        
        for test_key, duration in samples_to_record:
            try:
                print(f"\n\nPROGRES: {len(results)+1}/{len(samples_to_record)}")
                
                filepath, metadata = self.record_test_sample(test_key, duration)
                results[test_key] = {
                    'filepath': str(filepath),
                    'metadata': metadata
                }
                
                # Pause between recordings
                if test_key != samples_to_record[-1][0]:  # Not last sample
                    print(f"\n⏸️  Przerwa 3 sekundy przed następnym nagraniem...")
                    for i in range(3, 0, -1):
                        print(f"Następne nagranie za: {i}s", end='\r')
                        time.sleep(1)
                    print(" " * 30, end='\r')  # Clear line
                    
            except KeyboardInterrupt:
                print(f"\n\n⚠️  Nagrywanie przerwane przez użytkownika.")
                break
            except Exception as e:
                print(f"\n❌ Błąd podczas nagrywania {test_key}: {e}")
                continue
        
        # Save summary
        summary_file = self.output_dir / f"recording_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n\n✅ NAGRYWANIE ZAKOŃCZONE!")
        print(f"📊 Podsumowanie: {summary_file}")
        print(f"🎵 Nagrane próbki: {len(results)}")
        
        return results

    def __del__(self):
        """Cleanup audio resources."""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def main():
    """Main function for interactive recording."""
    print("🎙️  NARZĘDZIE NAGRYWANIA PRÓBEK TESTOWYCH")
    print("="*50)
    
    recorder = TestSampleRecorder()
    
    try:
        # Check if audio is available
        recorder.audio.get_default_input_device_info()
        print("✅ Mikrofon wykryty i gotowy")
        
        print("\nNaciśnij Enter aby rozpocząć nagrywanie lub Ctrl+C aby anulować...")
        input()
        
        results = recorder.record_all_samples()
        
        print(f"\n🎉 Pomyślnie nagrano {len(results)} próbek!")
        print("Pliki są gotowe do testów TDD.")
        
    except KeyboardInterrupt:
        print("\n👋 Nagrywanie anulowane przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
