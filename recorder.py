"""
TDD-compatible Recorder module
Wrapper around recording functionality for testing.
"""

import time
import threading
import pyaudio
import numpy as np
from pathlib import Path
import wave

class Recorder:
    """
    TDD-compatible Recorder with timestamp and duration methods.
    
    This class provides the interface required by TDD tests for recording audio.
    """
    
    def __init__(self, transcriber=None):
        """
        Initialize the recorder.
        
        Args:
            transcriber: Optional SpeechTranscriber instance
        """
        self.transcriber = transcriber
        self.recording = False
        self.audio_data = []
        self.start_timestamp = None
        
        # Audio parameters
        self.sample_rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk_size = 1024
        
        self.audio_interface = None
        self.stream = None
    
    def start_recording_with_timestamp(self):
        """
        Start recording and return the actual start timestamp.
        
        Returns:
            float: Timestamp when recording actually started
        """
        # Initialize audio if not already done
        if self.audio_interface is None:
            self.audio_interface = pyaudio.PyAudio()
        
        # Record the timestamp as close to stream start as possible
        pre_start_time = time.time()
        
        try:
            self.stream = self.audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Record actual start time after stream is opened
            self.start_timestamp = time.time()
            self.recording = True
            self.audio_data = []
            
            return self.start_timestamp
            
        except Exception as e:
            raise RuntimeError(f"Failed to start recording: {e}")
    
    def stop_recording(self):
        """Stop recording and return recorded audio data."""
        if not self.recording:
            return None
        
        self.recording = False
        
        # Stop and close stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Convert recorded data to numpy array
        if self.audio_data:
            audio_bytes = b''.join(self.audio_data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            return audio_float
        
        return None
    
    def record_duration(self, duration_seconds):
        """
        Record for a specific duration.
        
        Args:
            duration_seconds (float): Duration to record in seconds
            
        Returns:
            np.ndarray: Recorded audio data
        """
        self.start_recording_with_timestamp()
        
        # Record for specified duration
        frames_to_record = int(self.sample_rate / self.chunk_size * duration_seconds)
        
        for i in range(frames_to_record):
            if not self.recording:
                break
            
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
        
        return self.stop_recording()
    
    def start(self, language=None):
        """
        Start recording in background thread (compatible with original interface).
        
        Args:
            language (str): Optional language for transcription
        """
        self.current_language = language
        thread = threading.Thread(target=self._record_background)
        thread.start()
    
    def stop(self):
        """Stop background recording."""
        self.recording = False
    
    def _record_background(self):
        """Background recording implementation."""
        try:
            self.start_recording_with_timestamp()
            
            while self.recording:
                if self.stream:
                    try:
                        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                        self.audio_data.append(data)
                    except Exception as e:
                        print(f"Recording error: {e}")
                        break
                else:
                    break
            
            # Get recorded audio
            audio_data = self.stop_recording()
            
            # Transcribe if transcriber is available
            if self.transcriber and audio_data is not None:
                result = self.transcriber.transcribe_audio_data(audio_data)
                # Could implement typing here like in the original
                print(f"Transcribed: {result.text}")
                
        except Exception as e:
            print(f"Background recording failed: {e}")
        finally:
            self.recording = False
    
    def save_recording(self, audio_data, filename):
        """
        Save recorded audio data to file.
        
        Args:
            audio_data (np.ndarray): Audio data to save
            filename (str): Output filename
        """
        if audio_data is None:
            return
        
        # Convert float32 back to int16 for saving
        if audio_data.dtype == np.float32:
            audio_int16 = (audio_data * 32767).astype(np.int16)
        else:
            audio_int16 = audio_data
        
        # Save as WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())
    
    def get_recording_delay(self):
        """
        Measure the delay between calling start and actual recording start.
        
        Returns:
            float: Delay in seconds
        """
        test_delays = []
        
        for i in range(3):
            call_time = time.time()
            actual_start = self.start_recording_with_timestamp()
            delay = actual_start - call_time
            test_delays.append(delay)
            
            # Quick stop for testing
            self.stop_recording()
            time.sleep(0.1)  # Brief pause between tests
        
        return sum(test_delays) / len(test_delays)
    
    def __del__(self):
        """Cleanup audio resources."""
        if self.recording:
            self.stop_recording()
        
        if self.audio_interface:
            self.audio_interface.terminate()
