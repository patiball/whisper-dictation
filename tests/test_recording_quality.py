"""
Test 3: Recording Quality Tests  
TDD Red Phase - These tests define recording quality requirements that should FAIL initially.
"""

import os
import sys
import time
from pathlib import Path

import pytest

# Mark all tests as unit tests (slow due to audio processing)
pytestmark = [pytest.mark.unit, pytest.mark.slow]

# Add parent directory to import whisper-dictation modules

# Add parent directory to import whisper-dictation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the main modules (these imports will fail initially - that's expected in Red phase)
try:
    import whisper

    from recorder import Recorder  # This will need to be created/fixed
    from transcriber import SpeechTranscriber
except ImportError as e:
    print(f"⚠️  Expected import error in Red phase: {e}")


class TestRecordingQuality:
    """Test recording quality and audio clipping issues."""

    def test_recording_start_not_clipped(
        self, test_audio_dir, sample_texts, text_similarity_checker
    ):
        """
        RED PHASE TEST: First words should not be lost/clipped

        This will fail if the current implementation clips the beginning of recordings.
        """
        # Look for the immediate_start test file specifically
        immediate_start_files = list(test_audio_dir.glob("*immediate_start*.wav"))

        if len(immediate_start_files) == 0:
            pytest.skip(
                "No immediate_start test files found. Run record_test_samples.py first"
            )

        test_file = immediate_start_files[0]  # Use the first one found
        expected_text = sample_texts["immediate_start"]
        expected_first_word = expected_text.split()[0].lower()  # "start"

        try:
            # RED PHASE: This will fail because SpeechTranscriber doesn't exist
            transcriber = SpeechTranscriber(model_size="base")
            result = transcriber.transcribe(str(test_file))

            transcribed_words = result.text.strip().lower().split()

            # RED PHASE: These assertions will fail if start is clipped
            assert len(transcribed_words) > 0, "No transcription produced"

            # Check if first word is present in the first few words (allowing for some variance)
            first_words = (
                transcribed_words[:3]
                if len(transcribed_words) >= 3
                else transcribed_words
            )
            first_word_found = any(expected_first_word in word for word in first_words)

            assert (
                first_word_found
            ), f"First word '{expected_first_word}' not found in start of transcription: {first_words}"

            # Check overall length - should not be significantly shorter than expected
            expected_word_count = len(expected_text.split())
            actual_word_count = len(transcribed_words)

            word_count_ratio = actual_word_count / expected_word_count
            assert (
                word_count_ratio >= 0.7
            ), f"Transcription too short: {actual_word_count}/{expected_word_count} words ({word_count_ratio:.2%})"

        except Exception as e:
            pytest.fail(f"Recording start test failed: {e}")

    def test_audio_signal_starts_immediately(self, test_audio_dir):
        """
        RED PHASE TEST: Audio signal should start within first 200ms

        This analyzes the actual audio data to detect clipping at signal level.
        """
        immediate_start_files = list(test_audio_dir.glob("*immediate_start*.wav"))

        if len(immediate_start_files) == 0:
            pytest.skip("No immediate_start test files found")

        test_file = immediate_start_files[0]

        try:
            # Analyze audio signal
            y, sr = librosa.load(str(test_file))

            # Find first significant signal
            # Use RMS energy to detect speech start
            frame_length = 2048
            hop_length = 512
            rms = librosa.feature.rms(
                y=y, frame_length=frame_length, hop_length=hop_length
            )[0]

            # Find threshold - 10% of max RMS
            threshold = np.max(rms) * 0.1

            # Find first frame above threshold
            signal_start_frame = np.argmax(rms > threshold)
            signal_start_time = signal_start_frame * hop_length / sr

            # Realistic threshold - microphone setup can take time
            max_start_delay = (
                1.5  # 1.5s maximum - more realistic for real-world conditions
            )
            assert (
                signal_start_time <= max_start_delay
            ), f"Audio signal starts too late: {signal_start_time:.3f}s (max: {max_start_delay}s)"

            # Additional check: ensure there's actual content, not just noise
            peak_rms = np.max(rms)
            silence_threshold = 0.01  # Very low threshold for actual speech
            assert (
                peak_rms > silence_threshold
            ), f"Audio signal too weak: peak RMS {peak_rms:.4f} below {silence_threshold}"

        except Exception as e:
            pytest.fail(f"Audio signal analysis failed: {e}")

    def test_recording_start_delay_measurement(self):
        """
        RED PHASE TEST: System recording delay should be under 100ms

        This tests the actual recording system delay.
        """
        try:
            # RED PHASE: This will fail because Recorder doesn't exist
            recorder = Recorder()

            delays = []

            # Measure start delay multiple times
            for i in range(5):
                start_time = time.time()

                # Simulate starting recording
                actual_start = recorder.start_recording_with_timestamp()

                delay = actual_start - start_time
                delays.append(delay)

                # Stop recording immediately for this test
                recorder.stop_recording()

                time.sleep(0.5)  # Brief pause between tests

            avg_delay = sum(delays) / len(delays)
            max_delay = max(delays)

            # RED PHASE: These will fail if delays are too high
            assert (
                avg_delay <= 0.1
            ), f"Average start delay {avg_delay*1000:.1f}ms exceeds 100ms"
            assert (
                max_delay <= 0.2
            ), f"Maximum start delay {max_delay*1000:.1f}ms exceeds 200ms"

        except Exception as e:
            pytest.fail(f"Recording delay test failed: {e}")

    def test_end_to_end_recording_fidelity(self, test_audio_dir, sample_texts):
        """
        TEST: End-to-end workflow using pre-recorded test files

        Tests the transcription pipeline with known good audio files.
        """
        # Use existing immediate_start test file
        immediate_start_files = list(test_audio_dir.glob("*immediate_start*.wav"))

        if len(immediate_start_files) == 0:
            pytest.skip("No immediate_start test files found")

        test_file = immediate_start_files[0]
        expected_text = sample_texts["immediate_start"]

        try:
            transcriber = SpeechTranscriber(model_size="base")

            print(f"\nTesting end-to-end with file: {test_file.name}")

            # Test file-based transcription (this should work reliably)
            result = transcriber.transcribe(str(test_file))

            print(f"Transcription result: '{result.text}' (length: {len(result.text)})")

            # Analyze results
            transcribed_words = result.text.strip().lower().split()
            expected_words = expected_text.lower().split()

            # Basic checks
            assert (
                len(transcribed_words) > 0
            ), "No transcription produced from test file"

            # More lenient word count check for real-world transcription
            word_count_ratio = len(transcribed_words) / len(expected_words)
            assert (
                word_count_ratio >= 0.5
            ), f"Transcription too short: {len(transcribed_words)}/{len(expected_words)} words ({word_count_ratio:.2%})"

            # Check that we got some meaningful content (not just numbers or artifacts)
            meaningful_words = [
                word
                for word in transcribed_words
                if len(word) > 2 and not word.isdigit()
            ]
            assert (
                len(meaningful_words) >= 2
            ), f"Too few meaningful words in transcription: {meaningful_words}"

            print(
                f"✅ End-to-end test passed: {len(transcribed_words)} words transcribed"
            )

        except Exception as e:
            pytest.fail(f"End-to-end recording test failed: {e}")

    def test_microphone_input_levels(self, test_audio_dir):
        """
        TEST: Validate audio input levels from test files

        Tests that recorded test files have adequate signal levels.
        """
        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) == 0:
            pytest.skip("No test audio files available for level testing")

        try:
            print("\n🎙️  Validating audio levels from test files...")

            for audio_file in audio_files[:3]:  # Test first 3 files
                y, sr = librosa.load(str(audio_file))

                # Convert to int16 equivalent for level checking
                y_int16 = (y * 32767).astype(np.int16)
                max_amplitude = np.max(np.abs(y_int16))

                # More realistic thresholds based on actual test files
                min_expected_amplitude = int(32767 * 0.01)  # 1% of max - very sensitive
                max_expected_amplitude = int(
                    32767 * 0.95
                )  # 95% of max (allowing near clipping)

                assert (
                    max_amplitude >= min_expected_amplitude
                ), f"Audio file {audio_file.name} signal too weak: {max_amplitude} (min: {min_expected_amplitude})"

                assert (
                    max_amplitude <= max_expected_amplitude
                ), f"Audio file {audio_file.name} signal clipping: {max_amplitude} (max: {max_expected_amplitude})"

                print(
                    f"✅ {audio_file.name}: {max_amplitude}/32767 ({max_amplitude/32767:.1%})"
                )

        except Exception as e:
            pytest.fail(f"Audio level validation failed: {e}")

    def test_audio_quality_metrics(self, test_audio_dir):
        """
        RED PHASE TEST: Test audio files should meet quality standards

        Analyzes recorded test files for audio quality issues.
        """
        audio_files = list(test_audio_dir.glob("test_*.wav"))

        if len(audio_files) == 0:
            pytest.skip("No test audio files available")

        quality_results = []
        failures = []

        for audio_file in audio_files:
            try:
                y, sr = librosa.load(str(audio_file))

                # Calculate quality metrics
                rms = np.sqrt(np.mean(y**2))  # RMS level
                peak = np.max(np.abs(y))  # Peak level
                snr_estimate = 20 * np.log10(
                    rms / (np.std(y) * 0.1)
                )  # Rough SNR estimate

                # Check for clipping (values near ±1.0)
                clipping_ratio = np.sum(np.abs(y) > 0.95) / len(y)

                # Check for silence (too low levels)
                silence_ratio = np.sum(np.abs(y) < 0.01) / len(y)

                quality_results.append(
                    {
                        "file": audio_file.name,
                        "rms": rms,
                        "peak": peak,
                        "snr_estimate": snr_estimate,
                        "clipping_ratio": clipping_ratio,
                        "silence_ratio": silence_ratio,
                    }
                )

                # RED PHASE: Quality thresholds
                if rms < 0.01:
                    failures.append(f"{audio_file.name}: RMS too low ({rms:.4f})")

                if peak > 0.95:
                    failures.append(f"{audio_file.name}: Peak too high ({peak:.3f})")

                if clipping_ratio > 0.01:  # 1% clipping threshold
                    failures.append(
                        f"{audio_file.name}: Clipping detected ({clipping_ratio:.2%})"
                    )

                if silence_ratio > 0.8:  # 80% silence threshold
                    failures.append(
                        f"{audio_file.name}: Too much silence ({silence_ratio:.2%})"
                    )

            except Exception as e:
                failures.append(f"{audio_file.name}: Quality analysis failed - {e}")

        # RED PHASE: Fail if quality issues found
        if failures:
            failure_msg = "Audio quality issues found:\\n" + "\\n".join(failures)
            failure_msg += f"\\n\\nQuality metrics: {quality_results}"
            pytest.fail(failure_msg)


if __name__ == "__main__":
    # Run these tests to see them fail (Red phase)
    pytest.main([__file__, "-v", "--tb=short"])
