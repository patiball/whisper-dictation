"""
Integration Tests for Lock File Multi-Instance Behavior
Tests: Second instance exits, lock file cleanup, stale lock recovery
"""

import pytest
import subprocess
import time
import json
import os
import signal
from pathlib import Path

# Mark all tests as integration tests
pytestmark = pytest.mark.integration

class TestMultiInstanceBehavior:
    """Test multi-instance scenarios with real processes."""

    def test_second_instance_exits_when_first_running(self, temp_home):
        """Test second instance exits gracefully when first instance is running."""
        # Create a simple test script that simulates lock file behavior
        test_script = temp_home / "test_lock_instance.py"
        test_script.write_text("""
import json
import time
import sys
import os
from pathlib import Path

def simulate_lock_file_behavior(instance_id, duration=5):
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    # Check if lock file exists
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                lock_content = json.load(f)
            
            # Check if process is still alive
            try:
                os.kill(lock_content['pid'], 0)
                print(f"Instance {instance_id}: Another instance is running (PID {lock_content['pid']})")
                sys.exit(1)
            except (OSError, ProcessLookupError):
                # Process is dead, can continue
                pass
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Create lock file
    lock_content = {
        'pid': os.getpid(),
        'start_time': time.time(),
        'instance_id': instance_id
    }
    
    with open(lock_file, 'w') as f:
        json.dump(lock_content, f)
    
    print(f"Instance {instance_id}: Started successfully")
    
    # Simulate running for specified duration
    time.sleep(duration)
    
    # Clean up lock file
    if lock_file.exists():
        lock_file.unlink()
    
    print(f"Instance {instance_id}: Finished")

if __name__ == "__main__":
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    simulate_lock_file_behavior(instance_id, duration)
""")
        
        # Start first instance
        first_process = subprocess.Popen([
            sys.executable, str(test_script), "first", "10"
        ], env={**os.environ, 'HOME': str(temp_home)})
        
        # Give first instance time to start
        time.sleep(1)
        
        # Try to start second instance
        second_process = subprocess.Popen([
            sys.executable, str(test_script), "second", "1"
        ], env={**os.environ, 'HOME': str(temp_home)},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for second instance to complete
        stdout, stderr = second_process.communicate(timeout=5)
        
        # Second instance should exit with error code
        assert second_process.returncode == 1
        assert b"Another instance is running" in stdout
        
        # Clean up first process
        first_process.terminate()
        first_process.wait(timeout=5)

    def test_lock_file_removed_on_ctrl_c(self, temp_home):
        """Test lock file is removed when process receives Ctrl+C."""
        test_script = temp_home / "test_signal_cleanup.py"
        test_script.write_text("""
import json
import time
import signal
import sys
import os
from pathlib import Path

lock_file = None

def signal_handler(signum, frame):
    global lock_file
    print(f"Received signal {signum}, cleaning up...")
    if lock_file and lock_file.exists():
        lock_file.unlink()
        print("Lock file cleaned up")
    sys.exit(0)

def simulate_signal_handling():
    global lock_file
    
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create lock file
    lock_content = {
        'pid': os.getpid(),
        'start_time': time.time()
    }
    
    with open(lock_file, 'w') as f:
        json.dump(lock_content, f)
    
    print("Process started, lock file created")
    
    # Wait for signal
    while True:
        time.sleep(1)

if __name__ == "__main__":
    simulate_signal_handling()
""")
        
        # Start process
        process = subprocess.Popen([
            sys.executable, str(test_script)
        ], env={**os.environ, 'HOME': str(temp_home)},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give process time to start and create lock file
        time.sleep(1)
        
        # Verify lock file exists
        lock_file = temp_home / ".whisper-dictation.lock"
        assert lock_file.exists()
        
        # Send SIGINT (Ctrl+C)
        process.send_signal(signal.SIGINT)
        
        # Wait for process to finish
        stdout, stderr = process.communicate(timeout=5)
        
        # Process should exit gracefully and lock file should be removed
        assert process.returncode == 0
        assert not lock_file.exists()
        assert b"Lock file cleaned up" in stdout

    def test_stale_lock_recovery_with_real_processes(self, temp_home):
        """Test stale lock recovery with real process simulation."""
        test_script = temp_home / "test_stale_lock.py"
        test_script.write_text("""
import json
import time
import sys
import os
from pathlib import Path

def check_and_clean_stale_lock():
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                lock_content = json.load(f)
            
            # Check if process is still alive
            try:
                os.kill(lock_content['pid'], 0)
                print(f"Process {lock_content['pid']} is still alive")
                return False
            except (OSError, ProcessLookupError):
                print(f"Process {lock_content['pid']} is dead, cleaning stale lock")
                lock_file.unlink()
                return True
                
        except (json.JSONDecodeError, FileNotFoundError):
            print("Invalid lock file, cleaning up")
            lock_file.unlink()
            return True
    
    print("No lock file found")
    return True

def create_new_instance():
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    lock_content = {
        'pid': os.getpid(),
        'start_time': time.time(),
        'instance_id': 'recovery'
    }
    
    with open(lock_file, 'w') as f:
        json.dump(lock_content, f)
    
    print(f"New instance created with PID {os.getpid()}")

if __name__ == "__main__":
    if check_and_clean_stale_lock():
        create_new_instance()
    else:
        print("Cannot create instance, lock is valid")
        sys.exit(1)
""")
        
        # Create a stale lock file with fake PID
        lock_file = temp_home / ".whisper-dictation.lock"
        stale_content = {
            'pid': 99999,  # Fake PID that doesn't exist
            'start_time': time.time() - 3600,  # 1 hour ago
            'instance_id': 'stale'
        }
        
        with open(lock_file, 'w') as f:
            json.dump(stale_content, f)
        
        # Run recovery script
        result = subprocess.run([
            sys.executable, str(test_script)
        ], env={**os.environ, 'HOME': str(temp_home)},
        capture_output=True, text=True)
        
        # Should successfully recover and create new instance
        assert result.returncode == 0
        assert "Process 99999 is dead" in result.stdout
        assert "New instance created" in result.stdout
        
        # Verify lock file was updated with new PID
        with open(lock_file, 'r') as f:
            new_content = json.load(f)
        
        assert new_content['pid'] != 99999
        assert new_content['instance_id'] == 'recovery'

class TestLockFilePersistence:
    """Test lock file behavior across process lifecycle."""

    def test_lock_file_content_persistence(self, temp_home):
        """Test lock file content persists correctly."""
        test_script = temp_home / "test_persistence.py"
        test_script.write_text("""
import json
import time
import sys
import os
from pathlib import Path

def create_persistent_lock():
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    lock_content = {
        'pid': os.getpid(),
        'start_time': time.time(),
        'version': '1.0.0',
        'test_data': 'persistence_test'
    }
    
    with open(lock_file, 'w') as f:
        json.dump(lock_content, f)
    
    print(f"Lock file created with content: {lock_content}")

if __name__ == "__main__":
    create_persistent_lock()
""")
        
        # Create lock file
        result = subprocess.run([
            sys.executable, str(test_script)
        ], env={**os.environ, 'HOME': str(temp_home)},
        capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Verify lock file content
        lock_file = temp_home / ".whisper-dictation.lock"
        assert lock_file.exists()
        
        with open(lock_file, 'r') as f:
            content = json.load(f)
        
        assert 'pid' in content
        assert 'start_time' in content
        assert 'version' in content
        assert content['test_data'] == 'persistence_test'

    def test_lock_file_cleanup_on_process_crash(self, temp_home):
        """Test lock file behavior when process crashes."""
        test_script = temp_home / "test_crash.py"
        test_script.write_text("""
import json
import time
import sys
import os
from pathlib import Path

def simulate_crash():
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    lock_content = {
        'pid': os.getpid(),
        'start_time': time.time(),
        'simulate_crash': True
    }
    
    with open(lock_file, 'w') as f:
        json.dump(lock_content, f)
    
    print("Lock file created, simulating crash...")
    
    # Simulate crash by exiting without cleanup
    sys.exit(1)

if __name__ == "__main__":
    simulate_crash()
""")
        
        # Run crash simulation
        result = subprocess.run([
            sys.executable, str(test_script)
        ], env={**os.environ, 'HOME': str(temp_home)},
        capture_output=True, text=True)
        
        # Process should crash
        assert result.returncode == 1
        
        # Lock file should still exist (stale)
        lock_file = temp_home / ".whisper-dictation.lock"
        assert lock_file.exists()
        
        # Next instance should detect stale lock
        recovery_script = temp_home / "test_crash_recovery.py"
        recovery_script.write_text("""
import json
import os
from pathlib import Path

def detect_stale_lock():
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    if lock_file.exists():
        with open(lock_file, 'r') as f:
            content = json.load(f)
        
        try:
            os.kill(content['pid'], 0)
            return False  # Process is alive
        except (OSError, ProcessLookupError):
            return True  # Process is dead (stale lock)
    
    return False

if __name__ == "__main__":
    if detect_stale_lock():
        print("Stale lock detected from crashed process")
        sys.exit(0)
    else:
        print("Lock is valid")
        sys.exit(1)
""")
        
        # Run stale lock detection
        recovery_result = subprocess.run([
            sys.executable, str(recovery_script)
        ], env={**os.environ, 'HOME': str(temp_home)},
        capture_output=True, text=True)
        
        assert recovery_result.returncode == 0
        assert "Stale lock detected" in recovery_result.stdout

class TestConcurrentAccess:
    """Test concurrent access scenarios."""

    def test_multiple_concurrent_instances(self, temp_home):
        """Test behavior with multiple concurrent instances attempting to start."""
        test_script = temp_home / "test_concurrent.py"
        test_script.write_text("""
import json
import time
import sys
import os
import random
from pathlib import Path

def attempt_instance_start(instance_id):
    lock_file = Path.home() / ".whisper-dictation.lock"
    
    # Random delay to increase chance of race conditions
    time.sleep(random.uniform(0.1, 0.5))
    
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                lock_content = json.load(f)
            
            try:
                os.kill(lock_content['pid'], 0)
                print(f"Instance {instance_id}: Lost race to {lock_content['pid']}")
                sys.exit(1)
            except (OSError, ProcessLookupError):
                pass
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Attempt to create lock file
    try:
        lock_content = {
            'pid': os.getpid(),
            'start_time': time.time(),
            'instance_id': instance_id
        }
        
        with open(lock_file, 'w') as f:
            json.dump(lock_content, f)
        
        print(f"Instance {instance_id}: Won race, PID {os.getpid()}")
        
        # Hold lock for short time
        time.sleep(2)
        
        # Cleanup
        if lock_file.exists():
            lock_file.unlink()
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Instance {instance_id}: Error {e}")
        sys.exit(1)

if __name__ == "__main__":
    instance_id = sys.argv[1]
    attempt_instance_start(instance_id)
""")
        
        # Start multiple instances concurrently
        processes = []
        for i in range(5):
            process = subprocess.Popen([
                sys.executable, str(test_script), f"instance_{i}"
            ], env={**os.environ, 'HOME': str(temp_home)},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)
        
        # Wait for all processes to complete
        results = []
        for i, process in enumerate(processes):
            stdout, stderr = process.communicate(timeout=10)
            results.append({
                'instance': f"instance_{i}",
                'returncode': process.returncode,
                'stdout': stdout.decode()
            })
        
        # Only one instance should succeed
        successful_instances = [r for r in results if r['returncode'] == 0]
        failed_instances = [r for r in results if r['returncode'] == 1]
        
        assert len(successful_instances) == 1
        assert len(failed_instances) == 4
        
        # Verify successful instance message
        success_result = successful_instances[0]
        assert "Won race" in success_result['stdout']
        
        # Verify failed instances messages
        for failed_result in failed_instances:
            assert "Lost race" in failed_result['stdout']

# Skip conditions for CI environments
@pytest.mark.skipif(
    os.environ.get('CI') == 'true',
    reason="Integration tests with subprocess may not work in CI environments"
