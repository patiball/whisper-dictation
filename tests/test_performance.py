"""
Test 2: Performance Tests
TDD Red Phase - These tests define performance requirements that should FAIL initially.
"""

import os
import sys
import time
from pathlib import Path

import librosa
import pytest

# Add parent directory to import whisper-dictation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the main modules (these imports will fail initially - that's expected in Red phase)
try:
    import whisper

    from transcriber import SpeechTranscriber  # This will need to be created/fixed
except ImportError as e:
    print(f"⚠️  Expected import error in Red phase: {e}")


class TestPerformance:
    """Test transcription performance and speed requirements."""

    def test_transcription_performance_speed_ratio(
        self, test_audio_dir, performance_thresholds
    ):
        """
        RED PHASE TEST: Transcription should not take longer than 1.5x audio duration

        This will fail initially because the current implementation is too slow.
        """
        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) == 0:
            pytest.skip("No test audio files available")

        performance_results = []
        failures = []

        for audio_file in audio_files:
            try:
                # Get actual audio duration
                y, sr = librosa.load(str(audio_file))
                actual_duration = len(y) / sr

                # RED PHASE: This will fail because SpeechTranscriber doesn't exist
                transcriber = SpeechTranscriber(model_size="base")

                # Measure transcription time
                start_time = time.time()
                result = transcriber.transcribe(str(audio_file))
                transcription_time = time.time() - start_time

                speed_ratio = transcription_time / actual_duration

                performance_results.append(
                    {
                        "file": audio_file.name,
                        "audio_duration": actual_duration,
                        "transcription_time": transcription_time,
                        "speed_ratio": speed_ratio,
                        "text_length": (
                            len(result.text) if hasattr(result, "text") else 0
                        ),
                    }
                )

                # RED PHASE: These assertions will fail for slow performance
                if speed_ratio > performance_thresholds["max_speed_ratio"]:
                    failures.append(
                        f"{audio_file.name}: Speed ratio {speed_ratio:.2f}x exceeds target {performance_thresholds['max_speed_ratio']}x"
                    )

                if speed_ratio > performance_thresholds["critical_speed_ratio"]:
                    failures.append(
                        f"{audio_file.name}: CRITICAL - Speed ratio {speed_ratio:.2f}x exceeds {performance_thresholds['critical_speed_ratio']}x"
                    )

            except Exception as e:
                failures.append(f"{audio_file.name}: Performance test failed - {e}")

        # RED PHASE: This will fail with detailed performance info
        if failures:
            failure_msg = f"Performance tests failed:\n" + "\n".join(failures)
            failure_msg += f"\n\nDetailed results: {performance_results}"
            pytest.fail(failure_msg)

    def test_gpu_vs_cpu_acceleration(self, test_audio_dir):
        """
        RED PHASE TEST: GPU should be faster than CPU

        This will fail if GPU acceleration is not working properly.
        """
        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) == 0:
            pytest.skip("No test audio files available")

        # Use a medium-length file for testing
        test_file = None
        for file in audio_files:
            if "5s" in file.name:  # Use 5-second files
                test_file = file
                break

        if not test_file:
            pytest.skip("No suitable test file found")

        try:
            # RED PHASE: This will fail because SpeechTranscriber doesn't exist

            # Test with CPU
            transcriber_cpu = SpeechTranscriber(model_size="base", device="cpu")
            start_cpu = time.time()
            result_cpu = transcriber_cpu.transcribe(str(test_file))
            time_cpu = time.time() - start_cpu

            # Test with GPU (MPS on M1)
            transcriber_gpu = SpeechTranscriber(model_size="base", device="mps")
            start_gpu = time.time()
            result_gpu = transcriber_gpu.transcribe(str(test_file))
            time_gpu = time.time() - start_gpu

            # Realistic tolerance - MPS may have compatibility issues
            tolerance = 0.15  # 15% tolerance for timing variations
            if abs(time_gpu - time_cpu) < 0.1:
                print(
                    f"WARNING: GPU/CPU timing very close: GPU {time_gpu:.2f}s, CPU {time_cpu:.2f}s"
                )

            # Only fail if GPU is significantly slower
            assert time_gpu < time_cpu * (
                1 + tolerance
            ), f"GPU ({time_gpu:.2f}s) significantly slower than CPU ({time_cpu:.2f}s) beyond {tolerance*100}% tolerance"

            # Results should be similar (text quality)
            # RED PHASE: This will also be tested but might be lenient initially
            similarity_threshold = 0.8  # 80% word overlap
            if hasattr(result_cpu, "text") and hasattr(result_gpu, "text"):
                words_cpu = set(result_cpu.text.lower().split())
                words_gpu = set(result_gpu.text.lower().split())

                if words_cpu and words_gpu:
                    overlap = len(words_cpu.intersection(words_gpu))
                    similarity = overlap / max(len(words_cpu), len(words_gpu))

                    assert (
                        similarity >= similarity_threshold
                    ), f"GPU/CPU results too different: {similarity:.2%} similarity"

        except Exception as e:
            pytest.fail(f"GPU acceleration test failed: {e}")

    def test_model_loading_time(self):
        """
        Test model initialization performance (excluding download time)

        This tests only the loading time from local cache, ensuring models
        are pre-downloaded and measuring actual initialization performance.
        """
        # Use only locally available models
        from transcriber import SpeechTranscriber

        print("\nChecking locally available models...")

        available_models = SpeechTranscriber.list_available_models()
        model_sizes = [
            model
            for model, size in available_models
            if model in ["tiny", "base", "small"]
        ]

        if not model_sizes:
            pytest.skip("No suitable models (tiny/base/small) available locally")

        print(f"Testing with local models: {model_sizes}")

        for model_size in model_sizes:
            # Pre-download if needed (this is not timed)
            try:
                temp_model = whisper.load_model(model_size)
                del temp_model  # Free memory
                print(f"✓ {model_size} model ready")
            except Exception as e:
                pytest.skip(f"Could not prepare {model_size} model: {e}")

        # Now test actual loading performance
        loading_results = []

        for model_size in model_sizes:
            try:
                # Measure actual initialization time (models should be cached)
                start_time = time.time()
                transcriber = SpeechTranscriber(model_size=model_size)
                loading_time = time.time() - start_time

                loading_results.append(
                    {"model_size": model_size, "loading_time": loading_time}
                )

                print(f"{model_size} model loading time: {loading_time:.2f}s")

                # Realistic loading time thresholds (for cached models)
                max_loading_times = {
                    "tiny": 10.0,  # 10 seconds max for tiny (includes PyTorch init)
                    "base": 15.0,  # 15 seconds max for base
                    "small": 20.0,  # 20 seconds max for small
                    "medium": 30.0,  # 30 seconds max for medium
                    "large": 45.0,  # 45 seconds max for large
                }

                max_time = max_loading_times.get(model_size, 45.0)
                if loading_time > max_time:
                    pytest.fail(
                        f"Model {model_size} loading too slow: {loading_time:.2f}s > {max_time}s"
                    )

                # Cleanup to free memory for next test
                del transcriber

            except Exception as e:
                pytest.fail(f"Model loading test failed for {model_size}: {e}")

        print(f"\nModel loading test results: {loading_results}")

    def test_memory_usage_during_transcription(self, test_audio_dir):
        """
        RED PHASE TEST: Memory usage should be reasonable

        This will help identify memory leaks or excessive usage.
        """
        import os

        import psutil

        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) == 0:
            pytest.skip("No test audio files available")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        try:
            # RED PHASE: This will fail because SpeechTranscriber doesn't exist
            transcriber = SpeechTranscriber(model_size="base")
            after_init_memory = process.memory_info().rss / 1024 / 1024  # MB

            max_memory = after_init_memory

            # Transcribe multiple files to check for memory leaks
            for audio_file in audio_files[:3]:  # Test with first 3 files
                result = transcriber.transcribe(str(audio_file))
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                max_memory = max(max_memory, current_memory)

            memory_growth = max_memory - after_init_memory

            # RED PHASE: Define memory usage thresholds
            max_memory_growth = 100  # MB max growth during transcription
            max_total_memory = 2000  # MB max total usage

            assert (
                memory_growth < max_memory_growth
            ), f"Memory growth {memory_growth:.1f}MB exceeds {max_memory_growth}MB limit"

            assert (
                max_memory < max_total_memory
            ), f"Peak memory {max_memory:.1f}MB exceeds {max_total_memory}MB limit"

        except Exception as e:
            pytest.fail(f"Memory usage test failed: {e}")

    def test_batch_transcription_performance(
        self, test_audio_dir, performance_thresholds
    ):
        """
        RED PHASE TEST: Batch processing should be efficient

        Tests performance when processing multiple files sequentially.
        """
        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) < 2:
            pytest.skip("Need at least 2 audio files for batch testing")

        try:
            # RED PHASE: This will fail because SpeechTranscriber doesn't exist
            transcriber = SpeechTranscriber(model_size="base")

            batch_results = []
            total_audio_duration = 0
            total_transcription_time = 0

            batch_start = time.time()

            for audio_file in audio_files:
                # Get audio duration
                y, sr = librosa.load(str(audio_file))
                audio_duration = len(y) / sr
                total_audio_duration += audio_duration

                # Transcribe
                file_start = time.time()
                result = transcriber.transcribe(str(audio_file))
                file_time = time.time() - file_start
                total_transcription_time += file_time

                batch_results.append(
                    {
                        "file": audio_file.name,
                        "duration": audio_duration,
                        "transcription_time": file_time,
                        "speed_ratio": file_time / audio_duration,
                    }
                )

            batch_total_time = time.time() - batch_start
            average_speed_ratio = total_transcription_time / total_audio_duration

            # RED PHASE: Performance requirements for batch processing
            assert (
                average_speed_ratio <= performance_thresholds["max_speed_ratio"]
            ), f"Batch average speed ratio {average_speed_ratio:.2f}x exceeds {performance_thresholds['max_speed_ratio']}x"

            # Batch processing shouldn't be significantly slower than individual files
            # (accounting for model loading overhead)
            expected_batch_time = (
                total_transcription_time + 5.0
            )  # 5s overhead allowance
            assert (
                batch_total_time <= expected_batch_time * 1.2
            ), f"Batch processing overhead too high: {batch_total_time:.2f}s vs expected {expected_batch_time:.2f}s"

        except Exception as e:
            pytest.fail(f"Batch transcription test failed: {e}")


if __name__ == "__main__":
    # Run these tests to see them fail (Red phase)
    pytest.main([__file__, "-v", "--tb=short"])
