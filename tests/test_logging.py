"""
Unit Tests for Enhanced Logging System
Tests: File creation, level configuration, rotation, event logging
"""

import logging
import os
import time
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

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

    def test_logging_file_creation(self, configured_logger):
        """Test log file is created in expected location."""
        logger, log_file = configured_logger
        
        # Log a test message
        logger.info("Test log message")
        
        # Log file should be created and contain content
        assert log_file.exists()
        assert log_file.stat().st_size > 0

    def test_logging_level_configuration(self, configured_logger):
        """Test different log levels work correctly."""
        logger, log_file = configured_logger
        
        # Set logger to DEBUG level (already set by fixture, but good for clarity)
        logger.setLevel(logging.DEBUG)
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content

    def test_logging_fallback_on_permission_error(self, tmp_path):
        """Test logging fallback when file cannot be created."""
        log_file = tmp_path / ".whisper-dictation.log"
        
        def setup_logging_with_fallback(log_file_path, level=logging.INFO):
            # Clear any existing handlers from the root logger before setting up
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.propagate = True # Ensure propagation for StreamHandler

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

        # Verify that a StreamHandler was added to the root logger
        root_logger = logging.getLogger()
        assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)

        def test_logging_directory_creation(self, tmp_path):

            """Test log directory is created when it doesn't exist."""

            nested_log_dir = tmp_path / "logs" / "whisper-dictation"

            log_file = nested_log_dir / "app.log"

            

            # Clear any existing handlers from the root logger before setting up

            root_logger = logging.getLogger()

            root_logger.handlers.clear()

            root_logger.propagate = True

    

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

    def test_log_rotation_at_size_limit(self, tmp_path):
        """Test log rotation occurs when file reaches size limit."""
        log_file = tmp_path / ".whisper-dictation.log"
        max_bytes = 1024  # 1KB for testing
        backup_count = 3
        
        # Clear any existing handlers from the root logger before setting up
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.propagate = False

        # Use rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger("test_rotation_logger")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Generate enough log content to trigger rotation
        long_message = "This is a long log message that will help us test log rotation when the file reaches the maximum size limit. " * 10
        
        for i in range(20):
            logger.info(f"Log entry {i}: {long_message}")
        
        # Check if backup files were created
        backup_files = list(tmp_path.glob(".whisper-dictation.log.*"))
        assert len(backup_files) > 0, "No backup files created after rotation"
        
        # Clean up handler
        handler.close()
        logger.removeHandler(handler)

        def test_backup_file_creation(self, tmp_path):
            """Test backup files are created with correct naming."""
            log_file = tmp_path / ".whisper-dictation.log"
            
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
            backup_files = list(tmp_path.glob(".whisper-dictation.log.*"))
            assert len(backup_files) == 3
            
            # Verify backup file naming
            for i, backup_file in enumerate(sorted(backup_files), 1):
                assert backup_file.name == f".whisper-dictation.log.{i}"
                assert f"Backup {i} content" in backup_file.read_text()
        def test_old_log_deletion(self, tmp_path):
            """Test old backup files are deleted when limit exceeded."""
            log_file = tmp_path / ".whisper-dictation.log"
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
            all_backups = list(tmp_path.glob(".whisper-dictation.log.*"))
            assert len(all_backups) == 5
            
            # Clean up old backups
            cleanup_old_backups(log_file, max_backups)
            
            # Verify only max_backups remain
            remaining_backups = list(tmp_path.glob(".whisper-dictation.log.*"))
            assert len(remaining_backups) == max_backups
    def test_log_rotation_timing(self, tmp_path):
        """Test log rotation doesn't block application startup."""
        start_time = time.time()
        
        def quick_logging_setup(log_file_path):
            """Quick logging setup for timing test."""
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clear any existing handlers from the root logger before setting up
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.propagate = False

            import logging.handlers
            handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=1024*1024,  # 1MB
                backupCount=3
            )
            
            logger = logging.getLogger("timing_logger")
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            return handler
        
        log_file = tmp_path / ".whisper-dictation.log"
        handler = quick_logging_setup(log_file)
        
        setup_time = time.time() - start_time
        assert setup_time < 0.1  # Should complete in less than 100ms

        # Clean up handler
        handler.close()
        logging.getLogger("timing_logger").removeHandler(handler)


class TestLogFormat:
    """Test log format includes timestamp, level, and message correctly."""

    def test_log_format_includes_timestamp(self, configured_logger):
        """Test log entries include timestamps."""
        logger, log_file = configured_logger

        logger.info("Test message with timestamp")

        with open(log_file, 'r') as f:
            log_content = f.read()

        # Should contain timestamp pattern
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        assert re.search(timestamp_pattern, log_content)
        assert "Test message with timestamp" in log_content

    def test_log_format_includes_level(self, configured_logger):
        """Test log entries include log levels."""
        logger, log_file = configured_logger

        logger.setLevel(logging.DEBUG)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "DEBUG" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content

    def test_custom_log_format(self, tmp_path):
        """Test custom log format works correctly."""
        log_file = tmp_path / ".whisper-dictation.log"
        
        # Clear any existing handlers from the root logger before setting up
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.propagate = False

        def setup_custom_format_logging(log_file_path):
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
            
            handler = logging.FileHandler(log_file_path)
            handler.setFormatter(formatter)
            
            logger = logging.getLogger("custom_format_logger")
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        setup_custom_format_logging(log_file)
        logger = logging.getLogger("custom_format_logger")
        logger.info("Custom format test")
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Should match custom format
        assert "[INFO]" in log_content
        assert "Custom format test" in log_content

        # Clean up handler
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


class TestEventLogging:
    """Test key events are logged at appropriate levels."""

    def test_startup_event_logging(self, configured_logger):
        """Test application startup events are logged."""
        logger, log_file = configured_logger

        def log_startup_events():
            logger.info("Application starting up")
            logger.info("Lock file mechanism initialized")
            logger.info("Signal handlers registered")
            logger.info("Microphone check completed")
            logger.info("Application ready")

        log_startup_events()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "Application starting up" in log_content
        assert "Lock file mechanism initialized" in log_content
        assert "Signal handlers registered" in log_content
        assert "Microphone check completed" in log_content
        assert "Application ready" in log_content

    def test_error_event_logging(self, configured_logger):
        """Test error events are logged at appropriate levels."""
        logger, log_file = configured_logger

        logger.setLevel(logging.ERROR)

        def log_error_events():
            logger.error("Failed to initialize audio device")
            logger.error("Microphone permission denied")
            logger.warning("Using fallback audio configuration")

        log_error_events()

        with open(log_file, 'r') as f:
            log_content = f.read()

        assert "Failed to initialize audio device" in log_content
        assert "Microphone permission denied" in log_content
        # Warning should not appear at ERROR level
        assert "Using fallback audio configuration" not in log_content

    def test_recording_events_logging(self, configured_logger):
        """Test recording-related events are logged."""
        logger, log_file = configured_logger

        def log_recording_events():
            logger.info("Recording started")
            logger.debug("Audio stream initialized")
            logger.debug("Heartbeat updated")
            logger.info("Recording stopped")
            logger.info("Transcription completed")

        log_recording_events()

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

    def test_logging_with_invalid_path(self, tmp_path):
        """Test logging handles invalid file paths gracefully."""
        def setup_logging_with_invalid_path(log_file_path):
            # Clear any existing handlers from the root logger before setting up
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.propagate = True

            try:
                # Try to setup logging with invalid path
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file_path)]
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
        
        # Create a path that is guaranteed to be invalid for file writing
        invalid_path = tmp_path / "nonexistent_dir" / "log.log"
        result = setup_logging_with_invalid_path(invalid_path)
        assert result is True

        # Verify that a StreamHandler was added to the root logger
        root_logger = logging.getLogger()
        assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)

    def test_logging_concurrent_access(self, configured_logger):
        """Test logging handles concurrent access safely."""
        logger, log_file = configured_logger
        
        def concurrent_logger(thread_id):
            for i in range(10):
                logger.info(f"Thread {thread_id} - Message {i}")
                time.sleep(0.001)
        
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
