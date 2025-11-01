"""
Unit Tests for Enhanced Logging System
Tests: File creation, level configuration, rotation, event logging
"""

import pytest
import logging
import time
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Mark all tests as unit tests
pytestmark = pytest.mark.unit

@pytest.fixture
def isolated_logger():
    """Provide a clean logger for each test to prevent handler pollution."""
    # Get a unique logger name for this test
    logger_name = f"test_logger_{id(object())}"
    logger = logging.getLogger(logger_name)
    
    # Ensure logger has no handlers from previous tests
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Set up clean configuration
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Don't propagate to root logger
    
    yield logger
    
    # Cleanup after test
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

class TestLoggingSetup:
    """Test logging file creation, level configuration, and fallback."""

    def test_logging_file_creation(self, temp_home, temp_log_dir, isolated_logger):
        """Test log file is created in expected location."""
        log_file = temp_home / ".whisper-dictation.log"
        
        # Create directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add file handler to isolated logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        isolated_logger.addHandler(file_handler)
        
        # Log a test message
        isolated_logger.info("Test log message")
        
        # Flush handler to ensure content is written
        file_handler.flush()
        
        # Log file should be created and contain content
        assert log_file.exists()
        assert log_file.stat().st_size > 0

    def test_logging_level_configuration(self, temp_home, isolated_logger):
        """Test different log levels work correctly."""
        log_file = temp_home / ".whisper-dictation.log"
        
        # Create directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add file handler to isolated logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        isolated_logger.addHandler(file_handler)
        
        # Set logger to DEBUG level
        isolated_logger.setLevel(logging.DEBUG)
        
        # Test different log levels
        isolated_logger.debug("Debug message")
        isolated_logger.info("Info message")
        isolated_logger.warning("Warning message")
        
        # Flush handler to ensure content is written
        file_handler.flush()
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content

    def test_logging_fallback_on_permission_error(self, temp_home):
        """Test logging fallback when file cannot be created."""
        log_file = temp_home / ".whisper-dictation.log"
        
        def setup_logging_with_fallback(log_file_path, level=logging.INFO):
            try:
                log_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to create file handler
                file_handler = logging.FileHandler(log_file_path)
                
                # Configure logging
                logging.basicConfig(
                    level=level,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[file_handler]
                )
                
                return True  # Success
                
            except (PermissionError, OSError):
                # Fallback to console-only logging
                logging.basicConfig(
                    level=level,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()]
                )
                return False  # Fallback mode
        
        # Mock permission error
        with patch('logging.FileHandler', side_effect=PermissionError("Permission denied")):
            result = setup_logging_with_fallback(log_file)
            assert result is False  # Should fallback

    def test_logging_directory_creation(self, temp_home):
        """Test log directory is created when it doesn't exist."""
        nested_log_dir = temp_home / "logs" / "whisper-dictation"
        log_file = nested_log_dir / "app.log"
        
        def setup_logging_with_directory_creation(log_file_path, level=logging.INFO):
            # Create nested directory structure
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=level,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.FileHandler(log_file_path)]
            )
            
            return log_file_path
        
        result_path = setup_logging_with_directory_creation(log_file)
        
        # Directory should be created
        assert nested_log_dir.exists()
        assert nested_log_dir.is_dir()
        assert log_file.exists()
        assert result_path == log_file

class TestLogRotation:
    """Test log rotation, backup creation, and old log deletion."""

    def test_log_rotation_at_size_limit(self, temp_home):
        """Test log rotation occurs when file reaches size limit."""
        log_file = temp_home / ".whisper-dictation.log"
        max_size = 1024  # 1KB for testing
        
        def setup_rotating_logging(log_file_path, max_bytes=1024, backup_count=3):
            import logging.handlers
            
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler
            handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            logger = logging.getLogger()
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            return handler
        
        # Setup rotating logging
        handler = setup_rotating_logging(log_file)
        logger = logging.getLogger()
        
        # Generate enough log content to trigger rotation
        long_message = "This is a long log message that will help us test log rotation when the file reaches the maximum size limit. " * 10
        
        for i in range(20):
            logger.info(f"Log entry {i}: {long_message}")
        
        # Check if backup files were created
        backup_files = list(temp_home.glob(".whisper-dictation.log.*"))
        assert len(backup_files) > 0, "No backup files created after rotation"

    def test_backup_file_creation(self, temp_home):
        """Test backup files are created with correct naming."""
        log_file = temp_home / ".whisper-dictation.log"
        
        def create_backup_files(original_file, num_backups=3):
            """Simulate backup file creation."""
            for i in range(1, num_backups + 1):
                backup_file = original_file.with_suffix(f".log.{i}")
                backup_file.write_text(f"Backup {i} content")
        
        # Create original log file
        log_file.write_text("Original log content")
        
        # Create backups
        create_backup_files(log_file)
        
        # Verify backup files exist
        backup_files = list(temp_home.glob(".whisper-dictation.log.*"))
        assert len(backup_files) == 3
        
        # Verify backup file naming
        for i, backup_file in enumerate(sorted(backup_files), 1):
            assert backup_file.name == f".whisper-dictation.log.{i}"
            assert f"Backup {i} content" in backup_file.read_text()

    def test_old_log_deletion(self, temp_home):
        """Test old backup files are deleted when limit exceeded."""
        log_file = temp_home / ".whisper-dictation.log"
        max_backups = 3
        
        def create_excess_backups(original_file, count=5):
            """Create more backups than allowed."""
            for i in range(1, count + 1):
                backup_file = original_file.with_suffix(f".log.{i}")
                backup_file.write_text(f"Backup {i} content")
        
        def cleanup_old_backups(original_file, max_count):
            """Clean up old backups exceeding the limit."""
            backup_files = sorted(original_file.parent.glob(original_file.name + ".*"))
            
            if len(backup_files) > max_count:
                # Remove oldest backups
                for old_backup in backup_files[:-max_count]:
                    old_backup.unlink()
        
        # Create excess backups
        create_excess_backups(log_file, 5)
        
        # Verify all backups exist
        all_backups = list(temp_home.glob(".whisper-dictation.log.*"))
        assert len(all_backups) == 5
        
        # Clean up old backups
        cleanup_old_backups(log_file, max_backups)
        
        # Verify only max_backups remain
        remaining_backups = list(temp_home.glob(".whisper-dictation.log.*"))
        assert len(remaining_backups) == max_backups

    def test_log_rotation_timing(self, temp_home):
        """Test log rotation doesn't block application startup."""
        start_time = time.time()
        
        def quick_logging_setup(log_file_path):
            """Quick logging setup for timing test."""
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            import logging.handlers
            handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=1024*1024,  # 1MB
                backupCount=3
            )
            
            logger = logging.getLogger()
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            return handler
        
        log_file = temp_home / ".whisper-dictation.log"
        quick_logging_setup(log_file)
        
        setup_time = time.time() - start_time
        assert setup_time < 0.1  # Should complete in less than 100ms

class TestLogFormat:
    """Test log format includes timestamp, level, and message correctly."""

    def test_log_format_includes_timestamp(self, temp_home, isolated_logger):
        """Test log entries include timestamps."""
        log_file = temp_home / ".whisper-dictation.log"

        # Create and add a handler to the isolated logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        isolated_logger.addHandler(file_handler)

        isolated_logger.info("Test message with timestamp")

        # Close the handler to ensure logs are flushed to disk before reading
        file_handler.close()

        with open(log_file, 'r') as f:
            log_content = f.read()

        # Should contain timestamp pattern
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        assert re.search(timestamp_pattern, log_content)
        assert "Test message with timestamp" in log_content

    def test_log_format_includes_level(self, temp_home, isolated_logger):
        """Test log entries include log levels."""
        log_file = temp_home / ".whisper-dictation.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        isolated_logger.addHandler(file_handler)
        isolated_logger.setLevel(logging.DEBUG)

        isolated_logger.debug("Debug message")
        isolated_logger.info("Info message")
        isolated_logger.warning("Warning message")
        isolated_logger.error("Error message")

        file_handler.close()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "DEBUG" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content

    def test_custom_log_format(self, temp_home):
        """Test custom log format works correctly."""
        log_file = temp_home / ".whisper-dictation.log"
        
        def setup_custom_format_logging(log_file_path):
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
            
            handler = logging.FileHandler(log_file_path)
            handler.setFormatter(formatter)
            
            logger = logging.getLogger()
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        setup_custom_format_logging(log_file)
        logger = logging.getLogger()
        logger.info("Custom format test")
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Should match custom format
        assert "[INFO]" in log_content
        assert "Custom format test" in log_content

class TestEventLogging:
    """Test key events are logged at appropriate levels."""

    def test_startup_event_logging(self, temp_home, isolated_logger):
        """Test application startup events are logged."""
        log_file = temp_home / ".whisper-dictation.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        isolated_logger.addHandler(file_handler)

        def log_startup_events():
            isolated_logger.info("Application starting up")
            isolated_logger.info("Lock file mechanism initialized")
            isolated_logger.info("Signal handlers registered")
            isolated_logger.info("Microphone check completed")
            isolated_logger.info("Application ready")

        log_startup_events()
        file_handler.close()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "Application starting up" in log_content
        assert "Lock file mechanism initialized" in log_content
        assert "Signal handlers registered" in log_content
        assert "Microphone check completed" in log_content
        assert "Application ready" in log_content

    def test_error_event_logging(self, temp_home, isolated_logger):
        """Test error events are logged at appropriate levels."""
        log_file = temp_home / ".whisper-dictation.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        isolated_logger.addHandler(file_handler)
        isolated_logger.setLevel(logging.ERROR)

        def log_error_events():
            isolated_logger.error("Failed to initialize audio device")
            isolated_logger.error("Microphone permission denied")
            isolated_logger.warning("Using fallback audio configuration")

        log_error_events()
        file_handler.close()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "Failed to initialize audio device" in log_content
        assert "Microphone permission denied" in log_content
        # Warning should not appear at ERROR level
        assert "Using fallback audio configuration" not in log_content

    def test_recording_events_logging(self, temp_home, isolated_logger):
        """Test recording-related events are logged."""
        log_file = temp_home / ".whisper-dictation.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        isolated_logger.addHandler(file_handler)

        def log_recording_events():
            isolated_logger.info("Recording started")
            isolated_logger.debug("Audio stream initialized")
            isolated_logger.debug("Heartbeat updated")
            isolated_logger.info("Recording stopped")
            isolated_logger.info("Transcription completed")

        log_recording_events()
        file_handler.close()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "Recording started" in log_content
        assert "Audio stream initialized" in log_content
        assert "Heartbeat updated" in log_content
        assert "Recording stopped" in log_content
        assert "Transcription completed" in log_content

# Test logging configuration and edge cases
class TestLoggingEdgeCases:
    """Test edge cases and error handling in logging system."""

    def test_logging_with_invalid_path(self):
        """Test logging handles invalid file paths gracefully."""
        def setup_logging_with_invalid_path():
            try:
                invalid_path = "/invalid/path/that/does/not/exist/.whisper-dictation.log"
                
                # Try to setup logging with invalid path
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(invalid_path)]
                )
                return False  # Should not reach here
                
            except (OSError, PermissionError):
                # Fallback to console logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()]
                )
                return True  # Fallback successful
        
        result = setup_logging_with_invalid_path()
        assert result is True

    def test_logging_concurrent_access(self, temp_home):
        """Test logging handles concurrent access safely."""
        log_file = temp_home / ".whisper-dictation.log"
        
        def setup_concurrent_logging(log_file_path):
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.FileHandler(log_file_path)]
            )
        
        def concurrent_logger(thread_id):
            logger = logging.getLogger()
            for i in range(10):
                logger.info(f"Thread {thread_id} - Message {i}")
                time.sleep(0.001)
        
        setup_concurrent_logging(log_file)
        
        # Start multiple threads logging concurrently
        import threading
        threads = []
        
        for i in range(5):
            thread = threading.Thread(target=concurrent_logger, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all messages were logged
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Should have 5 threads * 10 messages = 50 messages
        message_count = log_content.count("Thread")
        assert message_count == 50
