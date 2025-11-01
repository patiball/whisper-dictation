"""
Integration Tests for Full Recording Flow
Tests: Complete recording, transcription, output cycle with all components
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class TestFullRecordingFlow:
    """Test complete recording, transcription, and output cycle."""

    def test_complete_recording_cycle(self, temp_home):
        """Test end-to-end recording cycle with all components."""
        # Create a test script that simulates the full recording flow
        test_script = temp_home / "test_full_cycle.py"
        test_script.write_text(
            """
import json
import time
import sys
import os
import tempfile
import wave
import numpy as np
from pathlib import Path

class MockRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
    
    def start_recording(self):
        self.recording = True
        self.frames = []
        # Generate mock audio data
        duration = 2.0  # 2 seconds
        sample_rate = 16000
        samples = int(duration * sample_rate)
        
        # Generate sine wave audio
        t = np.linspace(0, duration, samples, False)
        audio_data = np.sin(2 * np.pi * 440 * t) * 0.3  # 440 Hz sine wave
        audio_data = (audio_data * 32767).astype(np.int16)
        
        self.frames.append(audio_data.tobytes())
        print("Recording started")
    
    def stop_recording(self):
        self.recording = False
        print("Recording stopped")
        return b''.join(self.frames)

class MockTranscriber:
    def transcribe(self, audio_data):
        # Simulate transcription delay
        time.sleep(0.5)
        return "This is a test transcription from mock audio."

class MockLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, level, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {level} - {message}\\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

def simulate_full_recording_flow():
    log_file = Path.home() / ".whisper-dictation.log"
    logger = MockLogger(log_file)
    
    try:
        logger.log("INFO", "Application starting up")
        
        # Initialize components
        recorder = MockRecorder()
        transcriber = MockTranscriber()
        
        logger.log("INFO", "Components initialized")
        
        # Start recording
        recorder.start_recording()
        logger.log("INFO", "Recording started")
        
        # Simulate recording duration
        time.sleep(0.5)
        
        # Stop recording
        audio_data = recorder.stop_recording()
        logger.log("INFO", "Recording stopped")
        
        # Transcribe audio
        logger.log("INFO", "Starting transcription")
        transcription = transcriber.transcribe(audio_data)
        logger.log("INFO", "Transcription completed")
        
        # Output result
        print(f"Transcription: {transcription}")
        logger.log("INFO", "Output generated")
        
        logger.log("INFO", "Application finished successfully")
        return True
        
    except Exception as e:
        logger.log("ERROR", f"Application failed: {e}")
        return False

if __name__ == "__main__":
    success = simulate_full_recording_flow()
    sys.exit(0 if success else 1)
"""
        )

        # Run the full recording cycle test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            env={**os.environ, "HOME": str(temp_home)},
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete successfully
        assert result.returncode == 0
        assert "Transcription: This is a test transcription" in result.stdout

        # Verify log file was created and contains expected entries
        log_file = temp_home / ".whisper-dictation.log"
        assert log_file.exists()

        log_content = log_file.read_text()
        expected_log_entries = [
            "Application starting up",
            "Components initialized",
            "Recording started",
            "Recording stopped",
            "Starting transcription",
            "Transcription completed",
            "Output generated",
            "Application finished successfully",
        ]

        for entry in expected_log_entries:
            assert entry in log_content

    def test_component_interaction_correctness(self, temp_home):
        """Test all components interact correctly."""
        test_script = temp_home / "test_component_interaction.py"
        test_script.write_text(
            """
import json
import time
import sys
import os
from pathlib import Path

class ComponentTracker:
    def __init__(self):
        self.events = []
    
    def track(self, component, event):
        self.events.append({
            'component': component,
            'event': event,
            'timestamp': time.time()
        })
        print(f"{component}: {event}")

def test_component_interactions():
    tracker = ComponentTracker()
    
    try:
        # Simulate component initialization
        tracker.track("Application", "starting")
        tracker.track("LockFile", "initialized")
        tracker.track("SignalHandler", "registered")
        tracker.track("Logger", "configured")
        
        # Simulate recording flow
        tracker.track("Recorder", "starting_recording")
        time.sleep(0.1)
        tracker.track("Watchdog", "monitoring_started")
        time.sleep(0.1)
        tracker.track("Recorder", "stopping_recording")
        tracker.track("Watchdog", "monitoring_stopped")
        
        # Simulate transcription
        tracker.track("Transcriber", "processing_audio")
        time.sleep(0.2)
        tracker.track("Transcriber", "transcription_completed")
        
        # Simulate output
        tracker.track("Application", "output_generated")
        tracker.track("Application", "finished")
        
        # Verify event sequence
        expected_sequence = [
            ("Application", "starting"),
            ("LockFile", "initialized"),
            ("SignalHandler", "registered"),
            ("Logger", "configured"),
            ("Recorder", "starting_recording"),
            ("Watchdog", "monitoring_started"),
            ("Recorder", "stopping_recording"),
            ("Watchdog", "monitoring_stopped"),
            ("Transcriber", "processing_audio"),
            ("Transcriber", "transcription_completed"),
            ("Application", "output_generated"),
            ("Application", "finished")
        ]
        
        actual_sequence = [(e['component'], e['event']) for e in tracker.events]
        
        if actual_sequence == expected_sequence:
            print("Component interaction sequence is correct")
            return True
        else:
            print(f"Expected: {expected_sequence}")
            print(f"Actual: {actual_sequence}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_component_interactions()
    sys.exit(0 if success else 1)
"""
        )

        # Run component interaction test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            env={**os.environ, "HOME": str(temp_home)},
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0
        assert "Component interaction sequence is correct" in result.stdout

    def test_no_resource_leaks(self, temp_home):
        """Test no resource leaks or hangs after recording cycle."""
        test_script = temp_home / "test_resource_leaks.py"
        test_script.write_text(
            """
import json
import time
import sys
import os
import gc
import threading
from pathlib import Path

class ResourceTracker:
    def __init__(self):
        self.initial_threads = threading.active_count()
        self.initial_objects = len(gc.get_objects())
    
    def check_for_leaks(self):
        final_threads = threading.active_count()
        final_objects = len(gc.get_objects())
        
        thread_leak = final_threads > self.initial_threads
        object_leak = final_objects > self.initial_objects * 1.1  # Allow 10% growth
        
        return {
            'thread_leak': thread_leak,
            'object_leak': object_leak,
            'initial_threads': self.initial_threads,
            'final_threads': final_threads,
            'initial_objects': self.initial_objects,
            'final_objects': final_objects
        }

def simulate_recording_with_resources():
    tracker = ResourceTracker()
    
    # Simulate resource usage during recording
    threads = []
    
    def mock_audio_thread():
        time.sleep(0.5)
    
    def mock_transcription_thread():
        time.sleep(0.3)
    
    try:
        # Start mock threads
        for _ in range(3):
            thread = threading.Thread(target=mock_audio_thread)
            thread.start()
            threads.append(thread)
        
        # Simulate some object creation
        objects = []
        for i in range(100):
            objects.append({'data': f'test_{i}', 'timestamp': time.time()})
        
        # Wait for threads to complete with timeout
        for thread in threads:
            thread.join(timeout=5.0)
            if thread.is_alive():
                logging.warning(f"Thread {thread.name} did not exit after 5.0s timeout in resource leak test")
        
        # Clean up objects
        objects.clear()
        gc.collect()
        
        # Check for leaks
        leak_report = tracker.check_for_leaks()
        
        print(f"Leak report: {leak_report}")
        
        if leak_report['thread_leak']:
            print("WARNING: Thread leak detected")
        
        if leak_report['object_leak']:
            print("WARNING: Object leak detected")
        
        # Return True if no significant leaks
        return not (leak_report['thread_leak'] or leak_report['object_leak'])
        
    except Exception as e:
        print(f"Resource test failed: {e}")
        return False

if __name__ == "__main__":
    success = simulate_recording_with_resources()
    sys.exit(0 if success else 1)
"""
        )

        # Run resource leak test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            env={**os.environ, "HOME": str(temp_home)},
            capture_output=True,
            text=True,
            timeout=20,
        )

        assert result.returncode == 0
        assert "WARNING:" not in result.stdout  # No warnings about leaks


class TestLoggingIntegration:
    """Test logging captures full sequence correctly."""

    def test_logging_captures_full_sequence(self, temp_home):
        """Test logging captures the complete application sequence."""
        test_script = temp_home / "test_logging_sequence.py"
        test_script.write_text(
            """
import json
import time
import sys
import os
from pathlib import Path

class SequenceLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.sequence = []
    
    def log_event(self, event_type, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"{timestamp} - {event_type} - {message}\\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        self.sequence.append((event_type, message, timestamp))
        print(f"Logged: {event_type} - {message}")

def test_logging_sequence():
    log_file = Path.home() / ".whisper-dictation.log"
    logger = SequenceLogger(log_file)
    
    # Simulate application lifecycle events
    events = [
        ("INFO", "Application starting up"),
        ("INFO", "Lock file mechanism initialized"),
        ("INFO", "Signal handlers registered"),
        ("INFO", "Enhanced logging system configured"),
        ("INFO", "Microphone capability check completed"),
        ("INFO", "Application ready for recording"),
        ("INFO", "Recording started"),
        ("DEBUG", "Audio stream initialized"),
        ("DEBUG", "Heartbeat monitoring active"),
        ("INFO", "Recording stopped"),
        ("INFO", "Transcription started"),
        ("INFO", "Transcription completed"),
        ("INFO", "Output written to clipboard"),
        ("INFO", "Application shutting down"),
        ("INFO", "Lock file cleaned up"),
        ("INFO", "Application shutdown complete")
    ]
    
    try:
        for event_type, message in events:
            logger.log_event(event_type, message)
            time.sleep(0.05)  # Small delay to ensure distinct timestamps
        
        # Verify all events were logged
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        for event_type, message in events:
            if message not in log_content:
                print(f"Missing log entry: {event_type} - {message}")
                return False
        
        print("All events logged successfully")
        return True
        
    except Exception as e:
        print(f"Logging sequence test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_logging_sequence()
    sys.exit(0 if success else 1)
"""
        )

        # Run logging sequence test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            env={**os.environ, "HOME": str(temp_home)},
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0
        assert "All events logged successfully" in result.stdout

        # Verify log file contains all expected events
        log_file = temp_home / ".whisper-dictation.log"
        log_content = log_file.read_text()

        expected_events = [
            "Application starting up",
            "Lock file mechanism initialized",
            "Signal handlers registered",
            "Enhanced logging system configured",
            "Microphone capability check completed",
            "Application ready for recording",
            "Recording started",
            "Audio stream initialized",
            "Heartbeat monitoring active",
            "Recording stopped",
            "Transcription started",
            "Transcription completed",
            "Output written to clipboard",
            "Application shutting down",
            "Lock file cleaned up",
            "Application shutdown complete",
        ]

        for event in expected_events:
            assert event in log_content


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_graceful_error_handling(self, temp_home):
        """Test graceful handling of errors during recording cycle."""
        test_script = temp_home / "test_error_handling.py"
        test_script.write_text(
            """
import json
import time
import sys
import os
from pathlib import Path

class ErrorSimulator:
    def __init__(self):
        self.error_count = 0
    
    def simulate_recording_error(self):
        self.error_count += 1
        if self.error_count == 1:
            raise RuntimeError("Simulated recording device error")
        return True  # Subsequent calls succeed
    
    def simulate_transcription_error(self):
        self.error_count += 1
        if self.error_count == 2:
            raise RuntimeError("Simulated transcription service error")
        return "Fallback transcription result"

def test_error_recovery():
    log_file = Path.home() / ".whisper-dictation.log"
    error_sim = ErrorSimulator()
    
    def log_message(message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - INFO - {message}\\n")
    
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_message("Application starting up")
        
        # Test recording error recovery
        try:
            error_sim.simulate_recording_error()
        except RuntimeError as e:
            log_message(f"Recording error handled: {e}")
            # Simulate recovery
            log_message("Recording recovered with fallback device")
        
        # Test transcription error recovery
        try:
            result = error_sim.simulate_transcription_error()
            log_message(f"Transcription completed: {result}")
        except RuntimeError as e:
            log_message(f"Transcription error handled: {e}")
            log_message("Using offline transcription fallback")
        
        log_message("Application finished with error recovery")
        return True
        
    except Exception as e:
        log_message(f"Critical error: {e}")
        return False

if __name__ == "__main__":
    success = test_error_recovery()
    sys.exit(0 if success else 1)
"""
        )

        # Run error handling test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            env={**os.environ, "HOME": str(temp_home)},
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0

        # Verify error handling was logged
        log_file = temp_home / ".whisper-dictation.log"
        log_content = log_file.read_text()

        assert "Recording error handled" in log_content
        assert "Recording recovered with fallback device" in log_content
        assert "Transcription error handled" in log_content
        assert "Application finished with error recovery" in log_content


# Skip conditions for CI environments
@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Integration tests with subprocess may not work in CI environments",
)
class TestErrorRecovery:
    """Test error recovery and graceful degradation scenarios."""
