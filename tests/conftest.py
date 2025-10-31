# Test Configuration and Fixtures for Whisper Dictation TDD Tests

import pytest
import time
import os
import sys
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path to import whisper-dictation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def test_audio_dir():
    """Path to test audio files directory."""
    return Path(__file__).parent / "audio"

@pytest.fixture
def sample_texts():
    """Expected texts for controlled test recordings with realistic variations."""
    return {
        'polish_5s': "To jest test polskiego języka. Liczby jeden, dwa, trzy, cztery, pięć.",
        'polish_10s': "To jest dłuższy test polskiego języka. Będę mówić przez około dziesięć sekund. Liczby: jeden, dwa, trzy, cztery, pięć, sześć, siedem, osiem, dziewięć, dziesięć.",
        'english_5s': "This is an English language test. Numbers one, two, three, four, five.",
        'english_10s': "This is a longer English language test. I will speak for approximately ten seconds. Numbers: one, two, three, four, five, six, seven, eight, nine, ten.",
        'mixed': "Hello, jak się masz? I am testing mixed language recognition.",
        'immediate_start': "Start immediately with these exact words"
    }

@pytest.fixture
def performance_thresholds():
    """Performance criteria for tests."""
    return {
        'max_speed_ratio': 1.5,  # Max 1.5x audio duration for transcription
        'critical_speed_ratio': 2.0,  # Critical threshold
        'max_start_delay': 0.1,  # Max 100ms start delay
        'critical_start_delay': 0.2,  # Critical 200ms delay
        'language_accuracy': 0.95,  # 95% language detection accuracy
        'min_language_accuracy': 0.90  # Minimum acceptable accuracy
    }

def normalize_text(text):
    """Normalize text for realistic comparison with Whisper output."""
    import re
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation at word boundaries
    text = re.sub(r'[.,:;!?]', '', text)
    
    # Normalize number words to digits (Polish)
    number_map_pl = {
        'jeden': '1', 'dwa': '2', 'trzy': '3', 'cztery': '4', 'pięć': '5',
        'sześć': '6', 'siedem': '7', 'osiem': '8', 'dziewięć': '9', 'dziesięć': '10'
    }
    
    # Normalize number words to digits (English)
    number_map_en = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'
    }
    
    # Apply number normalization
    for word_num, digit in {**number_map_pl, **number_map_en}.items():
        text = re.sub(r'\b' + word_num + r'\b', digit, text)
    
    # Normalize common variations
    text = re.sub(r'\baproximately\b', 'approximately', text)  # Fix common typos
    text = re.sub(r'\bpermaximately\b', 'approximately', text)  # Whisper sometimes does this
    text = re.sub(r'\bhalo\b', 'hello', text)  # Polish-English mix
    
    return text

def similar_text(text1, text2, threshold=0.6):
    """Check if two texts are similar enough with normalization."""
    # Normalize both texts
    norm_text1 = normalize_text(text1)
    norm_text2 = normalize_text(text2)
    
    words1 = set(norm_text1.split())
    words2 = set(norm_text2.split())
    
    if not words1 or not words2:
        return False
        
    overlap = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    similarity = overlap / union if union > 0 else 0
    return similarity >= threshold

@pytest.fixture
def text_similarity_checker():
    """Fixture for text similarity checking."""
    return similar_text

# Lessons Learned Test Infrastructure Fixtures

@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    """Temporary home directory for lock files and user data."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    # Override HOME environment variable for this test using monkeypatch
    monkeypatch.setenv('HOME', str(home_dir))
    yield home_dir
    # monkeypatch automatically restores environment after test

@pytest.fixture
def temp_log_dir(tmp_path):
    """Temporary directory for test logs."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def clean_lock_file(temp_home):
    """Ensure lock file is cleaned before and after tests."""
    lock_file = temp_home / ".whisper-dictation.lock"
    if lock_file.exists():
        lock_file.unlink()
    yield lock_file
    if lock_file.exists():
        lock_file.unlink()

@pytest.fixture
def clean_log_file(temp_home):
    """Ensure log file is cleaned before and after tests."""
    log_file = temp_home / ".whisper-dictation.log"
    if log_file.exists():
        log_file.unlink()
    yield log_file
    if log_file.exists():
        log_file.unlink()

@pytest.fixture
def mock_pyaudio():
    """Mock PyAudio for hardware-independent testing."""
    with patch('pyaudio.PyAudio') as mock_py_audio:
        mock_instance = Mock()
        mock_py_audio.return_value = mock_instance
        
        # Mock device info
        mock_instance.get_device_info_by_index.return_value = {
            'maxInputChannels': 2,
            'name': 'Test Microphone'
        }
        mock_instance.get_device_count.return_value = 2
        
        yield mock_instance

@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice for microphone tests."""
    with patch('sounddevice.query_devices') as mock_query:
        mock_query.return_value = [
            {'name': 'Test Device 1', 'max_input_channels': 2},
            {'name': 'Test Device 2', 'max_input_channels': 0}
        ]
        yield mock_query

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for process management tests."""
    with patch('subprocess.Popen') as mock_popen, \
         patch('subprocess.run') as mock_run:
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        mock_run.return_value = Mock(returncode=0)
        yield mock_popen, mock_run

@pytest.fixture
def sample_lock_file_content():
    """Sample valid lock file content."""
    return {
        'pid': os.getpid(),
        'start_time': time.time(),
        'version': '1.0.0'
    }

@pytest.fixture
def heartbeat_tracker():
    """Mock heartbeat tracking for watchdog tests."""
    heartbeat_data = {'last_update': 0}
    
    def update_heartbeat():
        heartbeat_data['last_update'] = time.time()
    
    def get_last_update():
        return heartbeat_data['last_update']
    
    return {
        'update': update_heartbeat,
        'get_last': get_last_update,
        'data': heartbeat_data
    }

@pytest.fixture(autouse=True)
def reset_logging_state():
    """Reset logging configuration before each test to prevent handler pollution."""
    # Store original state
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level
    
    yield
    
    # Clean up all handlers and reset state
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    # Reset to original configuration
    root_logger.handlers = original_handlers
    root_logger.level = original_level
