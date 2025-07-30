#!/usr/bin/env python3
"""
Unit tests for whisper dictation performance and language detection
Uses pytest framework
"""

import pytest
import time
import os
import tempfile
import wave
import numpy as np
import sys
import importlib.util

# Import from file with hyphens
spec = importlib.util.spec_from_file_location("whisper_optimized", "whisper-dictation-optimized.py")
whisper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(whisper_module)

SpeechTranscriber = whisper_module.SpeechTranscriber
download_model = whisper_module.download_model


class TestWhisperPerformance:
    """Test class for whisper performance and language detection"""
    
    @classmethod
    def setup_class(cls):
        """Setup test class with model and test files"""
        cls.model_path = download_model('medium')
        cls.test_files = {}
        
        # Find test audio files
        for file in os.listdir('.'):
            if file.startswith('test_') and file.endswith('.wav'):
                if 'polish' in file.lower():
                    cls.test_files['polish'] = file
                elif 'english' in file.lower():
                    cls.test_files['english'] = file
        
        if not cls.test_files:
            pytest.skip("No test audio files found")
        
        print(f"Found test files: {cls.test_files}")
    
    def get_audio_duration(self, audio_file):
        """Get duration of audio file in seconds"""
        with wave.open(audio_file, 'rb') as wav:
            frames = wav.getnframes()
            sample_rate = wav.getframerate()
            return frames / sample_rate
    
    def load_audio_data(self, audio_file):
        """Load audio data from WAV file"""
        with wave.open(audio_file, 'rb') as wav:
            frames = wav.readframes(-1)
            audio_data = np.frombuffer(frames, dtype=np.int16)
            # Convert to float32 as expected by SpeechTranscriber
            return audio_data.astype(np.float32) / 32768.0
    
    def test_english_language_detection(self):
        """Test that English audio is detected as English"""
        if 'english' not in self.test_files:
            pytest.skip("No English test file found")
        
        transcriber = SpeechTranscriber(self.model_path, allowed_languages=['en', 'pl'])
        audio_file = self.test_files['english']
        audio_data = self.load_audio_data(audio_file)
        
        # Mock the transcribe method to capture language detection
        original_transcribe = transcriber.transcribe
        detected_language = None
        
        def mock_transcribe(audio_data, language=None):
            nonlocal detected_language
            result = original_transcribe(audio_data, language)
            detected_language = transcriber.last_detected_language
            return result
        
        transcriber.transcribe = mock_transcribe
        
        # Test auto-detection
        start_time = time.time()
        transcriber.transcribe(audio_data)
        transcription_time = time.time() - start_time
        
        # Assertions
        assert detected_language == 'en', f"Expected English detection, got: {detected_language}"
        
        audio_duration = self.get_audio_duration(audio_file)
        speed_ratio = transcription_time / audio_duration
        assert speed_ratio < 1.0, f"Transcription too slow: {speed_ratio:.2f}x"
        
        print(f"English detection: ✓, Speed: {speed_ratio:.2f}x")
    
    def test_polish_language_detection(self):
        """Test that Polish audio is detected as Polish"""
        if 'polish' not in self.test_files:
            pytest.skip("No Polish test file found")
        
        transcriber = SpeechTranscriber(self.model_path, allowed_languages=['en', 'pl'])
        audio_file = self.test_files['polish']
        audio_data = self.load_audio_data(audio_file)
        
        # Mock the transcribe method to capture language detection
        original_transcribe = transcriber.transcribe
        detected_language = None
        
        def mock_transcribe(audio_data, language=None):
            nonlocal detected_language
            result = original_transcribe(audio_data, language)
            detected_language = transcriber.last_detected_language
            return result
        
        transcriber.transcribe = mock_transcribe
        
        # Test auto-detection
        start_time = time.time()
        transcriber.transcribe(audio_data)
        transcription_time = time.time() - start_time
        
        # Assertions
        assert detected_language == 'pl', f"Expected Polish detection, got: {detected_language}"
        
        audio_duration = self.get_audio_duration(audio_file)
        speed_ratio = transcription_time / audio_duration
        assert speed_ratio < 1.0, f"Transcription too slow: {speed_ratio:.2f}x"
        
        print(f"Polish detection: ✓, Speed: {speed_ratio:.2f}x")
    
    def test_performance_target(self):
        """Test that transcription meets performance targets"""
        transcriber = SpeechTranscriber(self.model_path, allowed_languages=['en', 'pl'])
        
        total_time = 0
        total_audio = 0
        
        for lang, audio_file in self.test_files.items():
            audio_data = self.load_audio_data(audio_file)
            audio_duration = self.get_audio_duration(audio_file)
            
            # Test with explicit language for best performance
            lang_code = 'en' if lang == 'english' else 'pl'
            
            start_time = time.time()
            transcriber.transcribe(audio_data, language=lang_code)
            transcription_time = time.time() - start_time
            
            total_time += transcription_time
            total_audio += audio_duration
            
            speed_ratio = transcription_time / audio_duration
            
            # Performance targets:
            # - Should be faster than real-time (< 1.0x)
            # - Ideally should be < 0.6x for good user experience
            assert speed_ratio < 1.0, f"Too slow for {lang}: {speed_ratio:.2f}x"
            
            if speed_ratio > 0.6:
                print(f"WARNING: {lang} transcription is slow: {speed_ratio:.2f}x")
            else:
                print(f"{lang} performance: {speed_ratio:.2f}x ✓")
        
        # Overall performance
        avg_speed = total_time / total_audio
        assert avg_speed < 1.0, f"Average performance too slow: {avg_speed:.2f}x"
        print(f"Average performance: {avg_speed:.2f}x")
    
    def test_language_cache_effectiveness(self):
        """Test that language caching improves performance"""
        transcriber = SpeechTranscriber(self.model_path, allowed_languages=['en', 'pl'])
        
        if 'english' not in self.test_files:
            pytest.skip("No English test file for cache test")
        
        audio_file = self.test_files['english']
        audio_data = self.load_audio_data(audio_file)
        
        # First transcription (should detect and cache language)
        start_time = time.time()
        transcriber.transcribe(audio_data)
        first_time = time.time() - start_time
        
        # Second transcription (should use cached language)
        start_time = time.time()
        transcriber.transcribe(audio_data)
        second_time = time.time() - start_time
        
        # The second should be equal or faster (but whisper.cpp might not show much difference)
        # This is more about ensuring the cache works without errors
        assert transcriber.last_detected_language is not None, "Language should be cached"
        assert second_time < first_time * 1.2, "Second transcription shouldn't be much slower"
        
        print(f"Cache test: First: {first_time:.2f}s, Second: {second_time:.2f}s")
    
    def test_model_loading_performance(self):
        """Test that model loading time is reasonable"""
        start_time = time.time()
        transcriber = SpeechTranscriber(self.model_path, allowed_languages=['en', 'pl'])
        loading_time = time.time() - start_time
        
        # Model loading should be fast (whisper.cpp should be efficient)
        assert loading_time < 5.0, f"Model loading too slow: {loading_time:.2f}s"
        
        # First transcription includes model initialization in whisper.cpp
        if 'english' in self.test_files:
            audio_data = self.load_audio_data(self.test_files['english'])
            start_time = time.time()
            transcriber.transcribe(audio_data, language='en')
            first_transcription_time = time.time() - start_time
            
            # First transcription might be slower due to model warming up
            assert first_transcription_time < 10.0, f"First transcription too slow: {first_transcription_time:.2f}s"
            print(f"Model loading: {loading_time:.2f}s, First transcription: {first_transcription_time:.2f}s")


def test_baseline_performance():
    """Standalone test for baseline performance measurement"""
    print("\n" + "="*60)
    print("BASELINE PERFORMANCE TEST")
    print("="*60)
    
    model_path = download_model('medium')
    transcriber = SpeechTranscriber(model_path, allowed_languages=['en', 'pl'])
    
    # Find test files
    test_files = {}
    for file in os.listdir('.'):
        if file.startswith('test_') and file.endswith('.wav'):
            if 'polish' in file.lower():
                test_files['polish'] = file
            elif 'english' in file.lower():
                test_files['english'] = file
    
    if not test_files:
        pytest.skip("No test files for baseline test")
    
    for lang, audio_file in test_files.items():
        print(f"\nTesting {lang}: {audio_file}")
        
        # Load audio
        with wave.open(audio_file, 'rb') as wav:
            frames = wav.readframes(-1)
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            duration = wav.getnframes() / wav.getframerate()
        
        # Test auto-detection
        print("Auto-detection:")
        start_time = time.time()
        transcriber.transcribe(audio_data)
        auto_time = time.time() - start_time
        auto_speed = auto_time / duration
        print(f"  Time: {auto_time:.2f}s, Speed: {auto_speed:.2f}x")
        print(f"  Detected language: {transcriber.last_detected_language}")
        
        # Test explicit language
        lang_code = 'en' if lang == 'english' else 'pl'
        print(f"Explicit {lang_code}:")
        start_time = time.time()
        transcriber.transcribe(audio_data, language=lang_code)
        explicit_time = time.time() - start_time
        explicit_speed = explicit_time / duration
        print(f"  Time: {explicit_time:.2f}s, Speed: {explicit_speed:.2f}x")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Run the baseline test
    test_baseline_performance()
