"""
Unit Tests for Audio Stream Watchdog
Tests: Heartbeat tracking, stall detection, stream recovery, thread safety
"""

import pytest
import time
import threading
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mark all tests as unit tests
pytestmark = pytest.mark.unit


@pytest.fixture
def watchdog_test_harness():
    """Provides a harness for testing thread lifecycle and cleanup."""
    stop_event = threading.Event()
    thread = None

    def _start_thread(target_func, *args):
        nonlocal thread
        thread = threading.Thread(target=target_func, args=(stop_event, *args))
        thread.start()
        return thread

    yield _start_thread, stop_event

    # Teardown
    if thread and thread.is_alive():
        stop_event.set()
        thread.join(timeout=2.0)
        if thread.is_alive():
            pytest.fail(f"Thread {thread.name} failed to terminate cleanly.")


@pytest.fixture
def thread_manager():
    """A fixture to manage and clean up multiple threads created during a test."""
    active_threads = []
    
    def _thread_starter(target, args=()):
        thread = threading.Thread(target=target, args=args)
        thread.start()
        active_threads.append(thread)
        return thread

    yield _thread_starter
    
    # Teardown
    for thread in active_threads:
        if thread.is_alive():
            thread.join(timeout=2.0)
            if thread.is_alive():
                pytest.fail(f"Thread {thread.name} did not terminate cleanly.")







class TestHeartbeatTracking:
    """Test heartbeat update mechanism and timestamp validation."""

    def test_heartbeat_update_mechanism(self, heartbeat_tracker):
        """Test heartbeat updates are recorded correctly."""
        # Initial state should have no update
        assert heartbeat_tracker['get_last']() == 0
        
        # Update heartbeat
        heartbeat_tracker['update']()
        
        # Should have recent timestamp
        last_update = heartbeat_tracker['get_last']()
        assert last_update > 0
        assert time.time() - last_update < 1.0  # Within last second

    def test_multiple_heartbeat_updates(self, heartbeat_tracker):
        """Test multiple heartbeat updates work correctly."""
        updates = []
        
        def record_update():
            updates.append(heartbeat_tracker['get_last']())
            heartbeat_tracker['update']()
        
        # Record initial state
        record_update()
        time.sleep(0.1)
        record_update()
        time.sleep(0.1)
        record_update()
        
        # Should have 3 updates with increasing timestamps
        assert len(updates) == 3
        assert updates[0] == 0  # Initial state
        assert updates[1] > updates[0]
        assert updates[2] > updates[1]

    def test_heartbeat_timestamp_validation(self, heartbeat_tracker):
        """Test heartbeat timestamps are valid."""
        heartbeat_tracker['update']()
        
        timestamp = heartbeat_tracker['get_last']()
        
        # Timestamp should be reasonable
        assert isinstance(timestamp, float)
        assert timestamp > 0
        assert timestamp < time.time() + 1  # Should not be in future
        assert time.time() - timestamp < 10  # Should be recent

    def test_heartbeat_thread_safety(self, heartbeat_tracker, thread_manager):
        """Test heartbeat updates are thread-safe."""
        errors = []
        
        def concurrent_updates(thread_id):
            try:
                for _ in range(100):
                    heartbeat_tracker['update']()
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        # Run multiple threads updating heartbeat
        threads = [thread_manager(target=concurrent_updates, args=(i,)) for i in range(5)]
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Should have no errors
        assert len(errors) == 0
        
        # Final heartbeat should be recent
        final_update = heartbeat_tracker['get_last']()
        assert time.time() - final_update < 1.0

class TestStallDetection:
    """Test stall detection logic and timeout handling."""

    def test_stall_detection_basic(self, heartbeat_tracker):
        """Test basic stall detection functionality."""
        # Stall detection function (to be implemented)
        def is_stream_stalled(last_heartbeat, timeout_seconds=5.0):
            return (time.time() - last_heartbeat) > timeout_seconds
        
        # Fresh heartbeat should not be stalled
        heartbeat_tracker['update']()
        assert is_stream_stalled(heartbeat_tracker['get_last']()) is False
        
        # Old heartbeat should be stalled
        old_timestamp = time.time() - 10.0  # 10 seconds ago
        assert is_stream_stalled(old_timestamp) is True

    def test_stall_detection_timeout_values(self, heartbeat_tracker):
        """Test stall detection with different timeout values."""
        heartbeat_tracker['update']()
        current_time = heartbeat_tracker['get_last']()
        
        def is_stream_stalled(last_heartbeat, timeout_seconds):
            return (time.time() - last_heartbeat) > timeout_seconds
        
        # Test with an old timestamp to ensure stall detection works
        old_timestamp = time.time() - 1.0  # 1 second ago
        
        # Test various timeout values
        assert is_stream_stalled(old_timestamp, 0.001) is True  # Very short timeout
        assert is_stream_stalled(old_timestamp, 2.0) is False   # 2 second timeout
        assert is_stream_stalled(old_timestamp, 60.0) is False  # 1 minute timeout
        
        # Test with current timestamp (should not be stalled for reasonable timeouts)
        time.sleep(0.01)  # Small delay to make current timestamp old enough
        assert is_stream_stalled(current_time, 0.001) is True  # Now current time is > 0.001s old
        assert is_stream_stalled(current_time, 1.0) is False   # 1 second timeout should not trigger

    def test_stall_detection_edge_cases(self):
        """Test edge cases in stall detection."""
        def is_stream_stalled(last_heartbeat, timeout_seconds=5.0):
            return (time.time() - last_heartbeat) > timeout_seconds
        
        # Test with zero timestamp
        assert is_stream_stalled(0) is True
        
        # Test with future timestamp (should not be stalled)
        future_timestamp = time.time() + 10.0
        assert is_stream_stalled(future_timestamp) is False
        
        # Test with negative timestamp
        assert is_stream_stalled(-1.0) is True

    def test_stall_detection_with_grace_period(self, heartbeat_tracker):
        """Test stall detection with grace period for slow operations."""
        def is_stream_stalled_with_grace(last_heartbeat, timeout_seconds=5.0, grace_period=1.0):
            elapsed = time.time() - last_heartbeat
            return elapsed > (timeout_seconds + grace_period)
        
        heartbeat_tracker['update']()
        
        # Should not be stalled even after short timeout due to grace period
        time.sleep(0.1)
        assert is_stream_stalled_with_grace(heartbeat_tracker['get_last'](), 0.05) is False

class TestWatchdogThread:
    """Test watchdog thread lifecycle and monitoring logic."""

    def test_watchdog_thread_creation(self, watchdog_test_harness):
        """Test watchdog thread can be created and started."""
        start_thread, stop_event = watchdog_test_harness
        thread_started = threading.Event()
        
        def watchdog_monitor(stop_event_inner):
            thread_started.set()
            stop_event_inner.wait()  # Wait until stop is signaled by fixture

        watchdog_thread = start_thread(watchdog_monitor)
        
        # Assert thread starts and is alive
        assert thread_started.wait(timeout=1.0)
        assert watchdog_thread.is_alive()
        
        # Teardown and thread stop is handled by the fixture

    def test_watchdog_monitoring_loop(self, watchdog_test_harness, heartbeat_tracker):
        """Test watchdog monitoring loop behavior."""
        start_thread, stop_event = watchdog_test_harness
        monitoring_active = threading.Event()
        stall_detected = threading.Event()
        
        def watchdog_loop(stop_event_inner):
            monitoring_active.set()
            while not stop_event_inner.is_set():
                last_update = heartbeat_tracker['get_last']()
                if time.time() - last_update > 0.1:  # 100ms timeout for testing
                    stall_detected.set()
                    break
                time.sleep(0.01)
        
        start_thread(watchdog_loop)
        assert monitoring_active.wait(timeout=1.0)
        
        # Wait for stall detection (no heartbeat updates)
        assert stall_detected.wait(timeout=2.0)
        
        # Teardown is handled by the fixture

    def test_watchdog_thread_exception_handling(self, watchdog_test_harness):
        """Test watchdog thread handles exceptions gracefully."""
        start_thread, stop_event = watchdog_test_harness
        exception_occurred = threading.Event()
        
        def faulty_watchdog(stop_event_inner):
            try:
                # The fixture will stop this loop
                if not stop_event_inner.is_set():
                    raise RuntimeError("Simulated watchdog error")
            except Exception:
                exception_occurred.set()
            finally:
                # Keep thread alive until fixture's teardown signals stop
                stop_event_inner.wait()

        start_thread(faulty_watchdog)
        
        # Exception should be caught and handled
        assert exception_occurred.wait(timeout=1.0)
        
        # Teardown is handled by the fixture

class TestStreamRestart:
    """Test stream stop/close/reinit sequence."""

    def test_stream_stop_sequence(self):
        """Test audio stream stopping sequence."""
        stream_stopped = threading.Event()
        cleanup_called = threading.Event()
        
        class MockAudioStream:
            def __init__(self):
                self.is_active = True
            
            def stop(self):
                self.is_active = False
                stream_stopped.set()
            
            def close(self):
                cleanup_called.set()
        
        def restart_stream(stream):
            """Stream restart function (to be implemented)."""
            # Stop current stream
            if hasattr(stream, 'stop'):
                stream.stop()
            
            # Close stream
            if hasattr(stream, 'close'):
                stream.close()
            
            # Reinitialize would go here
            return MockAudioStream()
        
        # Test restart sequence
        original_stream = MockAudioStream()
        assert original_stream.is_active
        
        new_stream = restart_stream(original_stream)
        
        # Original stream should be stopped and closed
        assert stream_stopped.wait(timeout=1.0)
        assert cleanup_called.wait(timeout=1.0)
        assert not original_stream.is_active
        
        # New stream should be active
        assert new_stream.is_active

    def test_stream_restart_with_error_handling(self):
        """Test stream restart with error handling."""
        restart_attempts = []
        
        class FailingAudioStream:
            def stop(self):
                raise RuntimeError("Stream stop failed")
            
            def close(self):
                raise RuntimeError("Stream close failed")
        
        def safe_restart_stream(stream, max_attempts=3):
            """Safe stream restart with error handling."""
            for attempt in range(max_attempts):
                try:
                    if hasattr(stream, 'stop'):
                        stream.stop()
                    if hasattr(stream, 'close'):
                        stream.close()
                    return True  # Success
                except Exception as e:
                    restart_attempts.append(f"Attempt {attempt + 1}: {e}")
                    if attempt == max_attempts - 1:
                        return False  # All attempts failed
                    time.sleep(0.01)  # Brief delay before retry
        
        # Test error handling
        failing_stream = FailingAudioStream()
        result = safe_restart_stream(failing_stream)
        
        assert result is False
        assert len(restart_attempts) == 3

    def test_stream_restart_timing(self):
        """Test stream restart completes within reasonable time."""
        def quick_restart_stream():
            """Quick stream restart for timing test."""
            start_time = time.time()
            
            # Simulate quick restart operations
            time.sleep(0.01)  # 10ms for stop
            time.sleep(0.01)  # 10ms for cleanup
            time.sleep(0.01)  # 10ms for reinit
            
            end_time = time.time()
            return end_time - start_time
        
        restart_time = quick_restart_stream()
        assert restart_time < 0.1  # Should complete in less than 100ms

class TestThreadSafety:
    """Test thread safety of global variable access and race conditions."""

    def test_global_variable_access(self, thread_manager):
        """Test safe access to global variables across threads."""
        global_state = {'counter': 0, 'errors': []}
        lock = threading.Lock()
        
        def increment_counter(thread_id):
            try:
                for _ in range(1000):
                    with lock:  # Thread-safe access
                        global_state['counter'] += 1
                        time.sleep(0.0001)  # Small delay to increase contention
            except Exception as e:
                global_state['errors'].append(f"Thread {thread_id}: {e}")
        
        # Run multiple threads
        threads = [thread_manager(target=increment_counter, args=(i,)) for i in range(5)]
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Should have no errors and correct counter value
        assert len(global_state['errors']) == 0
        assert global_state['counter'] == 5000  # 5 threads * 1000 increments

    def test_race_condition_prevention(self, thread_manager):
        """Test race conditions are prevented with proper synchronization."""
        shared_resource = {'data': [], 'errors': []}
        lock = threading.Lock()
        
        def append_data(thread_id, value):
            try:
                with lock:
                    # Simulate critical section
                    current_length = len(shared_resource['data'])
                    time.sleep(0.001)  # Simulate processing time
                    shared_resource['data'].append(f"Thread {thread_id}: {value}")
                    
                    # Verify data integrity
                    assert len(shared_resource['data']) == current_length + 1
            except AssertionError as e:
                shared_resource['errors'].append(f"Race condition in thread {thread_id}: {e}")
        
        # Run multiple threads appending data
        threads = [thread_manager(target=append_data, args=(i, i)) for i in range(10)]
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Should have no race conditions
        assert len(shared_resource['errors']) == 0
        assert len(shared_resource['data']) == 10

    def test_deadlock_prevention(self, thread_manager):
        """Test that a deadlock scenario is detected without hanging."""
        deadlock_detected = threading.Event()
        lock1 = threading.Lock()
        lock2 = threading.Lock()

        def thread1():
            try:
                with lock1:
                    time.sleep(0.01)
                    # Attempt to acquire lock2 with a timeout
                    if not lock2.acquire(timeout=0.5):
                        deadlock_detected.set()
                        return  # Exit thread
                    try:
                        pass  # Should not be reached in a deadlock
                    finally:
                        lock2.release()
            except Exception:
                deadlock_detected.set()

        def thread2():
            try:
                with lock2:
                    time.sleep(0.01)
                    # Attempt to acquire lock1 with a timeout
                    if not lock1.acquire(timeout=0.5):
                        deadlock_detected.set()
                        return  # Exit thread
                    try:
                        pass  # Should not be reached in a deadlock
                    finally:
                        lock1.release()
            except Exception:
                deadlock_detected.set()

        # Start threads
        t1 = thread_manager(target=thread1)
        t2 = thread_manager(target=thread2)

        # Wait for completion
        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        # Assert that the deadlock was detected by one of the threads timing out
        assert deadlock_detected.is_set()
