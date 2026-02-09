import argparse
import atexit
import json
import logging
import os
import platform
import signal
import subprocess
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import numpy as np
import psutil
import pyaudio
import torch
from pynput import keyboard
from whisper import load_model

try:
    import rumps
except Exception:
    rumps = None

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    pystray = None
    Image = None
    ImageDraw = None


def get_timestamp():
    """Returns formatted timestamp [HH:MM:SS.mmm]"""
    return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"


def setup_logging(log_level="INFO", log_file=None):
    """Configure centralized logging with rotation and console output."""
    if log_file is None:
        log_file = Path.home() / ".whisper-dictation.log"

    try:
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(formatter)

        # Configure root logger
        logger.setLevel(getattr(logging, log_level))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return True
    except Exception as e:
        # Fallback to console-only if file logging fails
        print(f"Warning: Could not set up file logging: {e}")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        return False


# Lock file mechanism to prevent multiple instances
_cleanup_done = False


def setup_lock_file():
    """Setup lock file to prevent multiple simultaneous instances."""
    global _cleanup_done
    lock_file = Path.home() / ".whisper-dictation.lock"

    try:
        if lock_file.exists():
            # Read existing PID
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()

                if pid_str:
                    try:
                        existing_pid = int(pid_str)
                        if psutil.pid_exists(existing_pid):
                            logging.error(
                                f"Another instance is already running (PID: {existing_pid})"
                            )
                            print(
                                f"Error: Another instance of whisper-dictation is already running (PID: {existing_pid})"
                            )
                            print(
                                "Please stop the other instance before starting a new one."
                            )
                            exit(1)
                        else:
                            logging.warning(
                                f"Found stale lock file with dead PID: {existing_pid}"
                            )
                            lock_file.unlink()
                    except ValueError:
                        logging.warning(f"Invalid PID in lock file: {pid_str}")
                        lock_file.unlink()
                else:
                    logging.warning("Empty lock file found")
                    lock_file.unlink()

            except (OSError, IOError) as e:
                logging.warning(f"Could not read lock file: {e}")
                # Try to continue anyway

        # Write current PID to lock file
        current_pid = os.getpid()
        with open(lock_file, "w") as f:
            f.write(str(current_pid))

        logging.info(f"Lock file created with PID: {current_pid}")

        # Register cleanup
        _cleanup_done = False
        atexit.register(cleanup_lock_file)

        return True

    except (OSError, IOError) as e:
        logging.error(f"Failed to create lock file: {e}")
        print(f"Warning: Could not create lock file: {e}")
        print("Multiple instance protection disabled.")
        return False


def cleanup_lock_file():
    """Remove lock file during shutdown."""
    global _cleanup_done
    if _cleanup_done:
        return

    lock_file = Path.home() / ".whisper-dictation.lock"

    try:
        if lock_file.exists():
            lock_file.unlink()
            logging.info("Lock file removed during shutdown")
    except (OSError, IOError) as e:
        logging.warning(f"Could not remove lock file during cleanup: {e}")
    finally:
        _cleanup_done = True


# Signal handlers for graceful shutdown
cleanup_in_progress = False
shutdown_requested = False
app = None
listener = None


def shutdown_application():
    """Best-effort shutdown for listeners, watchdog, and audio resources."""
    try:
        if (
            "app" in globals()
            and app is not None
            and hasattr(app, "started")
            and app.started
            and hasattr(app, "stop_app")
        ):
            app.stop_app(None)
            logging.info("Recording stopped during shutdown")
    except Exception as e:
        logging.warning(f"Failed to stop recording cleanly: {e}")

    try:
        if "listener" in globals() and listener is not None:
            listener.stop()
            logging.info("Keyboard listener stopped")
    except Exception as e:
        logging.warning(f"Failed to stop keyboard listener: {e}")

    try:
        stop_watchdog()
    except Exception as e:
        logging.warning(f"Failed to stop watchdog: {e}")

    try:
        if "app" in globals() and app is not None and hasattr(app, "recorder"):
            if hasattr(app.recorder, "close"):
                app.recorder.close()
                logging.info("Audio stream closed")
    except Exception as e:
        logging.warning(f"Failed to close audio stream: {e}")

    cleanup_lock_file()


def signal_handler(signum, frame):
    """Handle termination signals for graceful shutdown."""
    global cleanup_in_progress, shutdown_requested

    if cleanup_in_progress:
        logging.warning("Shutdown already in progress, ignoring signal")
        return

    cleanup_in_progress = True
    shutdown_requested = True

    signal_name = signal.Signals(signum).name
    logging.info(
        f"Received signal {signal_name} ({signum}), initiating graceful shutdown"
    )

    try:
        shutdown_application()
        logging.info("Graceful shutdown completed")

    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
    finally:
        # Force exit to ensure no hanging
        os._exit(0)


def register_signal_handlers():
    """Register signal handlers for graceful shutdown."""
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logging.info("Signal handlers registered for SIGINT and SIGTERM")
        return True
    except Exception as e:
        logging.error(f"Failed to register signal handlers: {e}")
        return False


# Microphone access verification
def test_microphone_access():
    """Test microphone access capability on startup."""
    try:
        import sounddevice as sd

        start_time = time.time()

        # Test microphone access
        sd.check_input_settings()

        elapsed_ms = (time.time() - start_time) * 1000
        logging.info(f"Microphone access test passed ({elapsed_ms:.1f}ms)")
        print("Microphone access test passed.")

    except PermissionError as e:
        logging.warning(f"Microphone access test failed: Permission denied - {e}")
        print("WARNING: Microphone access test failed: Permission denied")
        print("  Please check System Preferences → Privacy → Microphone")

    except RuntimeError as e:
        if "No input device" in str(e):
            logging.warning(
                f"Microphone access test failed: No audio input devices found - {e}"
            )
            print(
                "WARNING: Microphone access test failed: No audio input devices found"
            )
        else:
            logging.warning(f"Microphone access test failed: Audio system error - {e}")
            print(f"WARNING: Microphone access test failed: {e}")

    except Exception as e:
        logging.warning(f"Microphone access test failed: {e}")
        print(f"WARNING: Microphone access test failed: {e}")

    # Function never raises exceptions - graceful degradation


# Audio Stream Watchdog
last_heartbeat = datetime.now()
watchdog_active = False
recording = False
audio_timeout = 10  # seconds


def update_heartbeat():
    """Update the heartbeat timestamp after successful audio reads."""
    global last_heartbeat
    last_heartbeat = datetime.now()


def watchdog_monitor():
    """Background thread that monitors audio stream for stalls."""
    while watchdog_active:
        if recording:
            time_since = (datetime.now() - last_heartbeat).total_seconds()
            if time_since > audio_timeout:
                logging.warning(
                    f"Audio system stalled! No heartbeat for {time_since:.1f}s"
                )
                restart_audio_stream()
        time.sleep(1)


def restart_audio_stream():
    """Restart the audio stream after a stall is detected."""
    global last_heartbeat

    try:
        logging.info("Restarting audio stream...")

        # Stop and close current stream
        if (
            app is not None
            and hasattr(app, "recorder")
            and hasattr(app.recorder, "stream")
            and app.recorder.stream is not None
            and hasattr(app.recorder, "p")
            and app.recorder.p is not None
        ):
            app.recorder.stream.stop_stream()
            app.recorder.stream.close()

            # Reinitialize stream with same parameters
            app.recorder.stream = app.recorder.p.open(
                format=app.recorder.FORMAT,
                channels=app.recorder.CHANNELS,
                rate=app.recorder.RATE,
                input=True,
                frames_per_buffer=app.recorder.FRAMES_PER_BUFFER,
            )
            app.recorder.stream.start_stream()

            # Reset heartbeat
            last_heartbeat = datetime.now()
            logging.info("Audio stream restarted successfully")
        else:
            logging.error("Cannot restart stream: recorder or stream not available")

    except Exception as e:
        logging.error(f"Failed to restart audio stream: {e}")


def start_watchdog():
    """Start the audio watchdog thread."""
    global watchdog_active

    if not watchdog_active:
        watchdog_active = True
        watchdog_thread = threading.Thread(target=watchdog_monitor, daemon=True)
        watchdog_thread.start()
        logging.info("Watchdog thread started")


def stop_watchdog():
    """Stop the audio watchdog thread."""
    global watchdog_active

    if watchdog_active:
        watchdog_active = False
        # Give thread time to exit
        time.sleep(2)
        logging.info("Watchdog thread stopped")


class SpeechTranscriber:
    def __init__(self, model, allowed_languages=None, device_manager=None):
        self.model = model
        self.pykeyboard = keyboard.Controller()
        self.allowed_languages = allowed_languages
        self.device_manager = device_manager
        self._transcribe_lock = threading.Lock()

        # Get device from model if device_manager not provided
        if hasattr(model, "device"):
            self.device = str(model.device)
        else:
            self.device = "cpu"

        print(f"SpeechTranscriber: Using device {self.device}")
        logging.debug(f"SpeechTranscriber initialized with device: {self.device}")

    def transcribe(self, audio_data, language=None):
        start_time = time.time()
        logging.debug(f"Starting transcription, language: {language or 'auto'}")

        with self._transcribe_lock:
            # Get optimized options from device manager if available
            if self.device_manager:
                options = self.device_manager.get_optimized_settings(
                    self.device, "base"
                )  # Default to base model
                if language:
                    options["language"] = language
                logging.debug("Using device manager optimized settings")
            else:
                # Fallback to original options
                options = {
                    "fp16": self.device == "mps",  # Use half precision on GPU
                    "language": language,
                    "task": "transcribe",
                    "no_speech_threshold": 0.6,  # Higher threshold for better performance
                    "logprob_threshold": -1.0,
                    "compression_ratio_threshold": 2.4,
                }
                logging.debug("Using fallback transcription options")

            # If we have allowed languages and no specific language is set, detect and constrain
            if self.allowed_languages and language is None:
                logging.debug("Detecting language with allowed constraints")
                # First, detect the language without constraining
                result = self.model.transcribe(
                    audio_data, **{k: v for k, v in options.items() if k != "language"}
                )
                detected_lang = result.get("language", "en")
                logging.debug(f"Detected language: {detected_lang}")

                # If detected language is not in allowed list, use the first allowed language
                if detected_lang not in self.allowed_languages:
                    options["language"] = self.allowed_languages[0]
                    logging.info(
                        f"Constraining to allowed language: {self.allowed_languages[0]} (detected: {detected_lang})"
                    )
                else:
                    options["language"] = detected_lang
                    logging.debug(f"Using detected language: {detected_lang}")

                # Re-transcribe with the constrained language
                result = self.model.transcribe(audio_data, **options)
            else:
                result = self.model.transcribe(audio_data, **options)

        duration = time.time() - start_time
        text = result.get("text", "").strip()
        logging.info(
            f"Transcription complete in {duration:.2f}s, text length: {len(text)}"
        )

        print(f"{get_timestamp()} Transcription complete")
        print(f"{get_timestamp()} Typing text...")
        is_first = True
        for element in result["text"]:
            if is_first and element == " ":
                is_first = False
                continue

            try:
                self.pykeyboard.type(element)
                time.sleep(0.0025)
            except Exception as e:
                logging.warning(f"Failed to type character '{element}': {e}")
                pass

        return result


class SoundPlayer:
    """Class for playing platform-appropriate recording cues."""

    @staticmethod
    def _generate_tone_wav(path, freqs, durations, volume=0.12, sample_rate=22050):
        import math
        import struct
        import wave

        samples = []
        # short lead-in silence to avoid output-device transient click
        samples.extend([0] * int(sample_rate * 0.012))
        for freq, duration in zip(freqs, durations):
            tone_samples = int(sample_rate * duration)
            attack = max(1, int(sample_rate * 0.008))
            release = max(1, int(sample_rate * 0.012))
            for i in range(tone_samples):
                envelope = 1.0
                if i < attack:
                    envelope = i / attack
                elif i > tone_samples - release:
                    envelope = max(0.0, (tone_samples - i) / release)

                value = (
                    volume
                    * envelope
                    * math.sin(2 * math.pi * freq * (i / sample_rate))
                )
                samples.append(int(max(-1.0, min(1.0, value)) * 32767))

            # brief silence between tones
            silence_samples = int(sample_rate * 0.03)
            samples.extend([0] * silence_samples)

        # tail silence to avoid hard stop click
        samples.extend([0] * int(sample_rate * 0.02))

        with wave.open(str(path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = b"".join(struct.pack("<h", sample) for sample in samples)
            wav_file.writeframes(frames)

    @staticmethod
    def _ensure_windows_cue_file(pattern):
        cues_dir = Path.home() / ".whisper-dictation-cues"
        cues_dir.mkdir(parents=True, exist_ok=True)
        cue_path = cues_dir / f"{pattern}.wav"
        if pattern == "start":
            # Soft ascending cue.
            SoundPlayer._generate_tone_wav(
                cue_path, freqs=[660, 880], durations=[0.06, 0.10], volume=0.10
            )
        else:
            # Soft descending cue.
            SoundPlayer._generate_tone_wav(
                cue_path, freqs=[620, 440], durations=[0.06, 0.12], volume=0.10
            )

        return cue_path

    @staticmethod
    def _play_sound(sound_path):
        try:
            subprocess.run(["afplay", sound_path], check=False, capture_output=True)
        except Exception as e:
            logging.warning(f"Failed to play sound: {e}")

    @staticmethod
    def _play_windows_sound(pattern):
        try:
            import winsound

            cue_path = SoundPlayer._ensure_windows_cue_file(pattern)
            winsound.PlaySound(
                str(cue_path),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        except Exception:
            try:
                import winsound

                tone = (
                    winsound.MB_ICONASTERISK
                    if pattern == "start"
                    else winsound.MB_ICONEXCLAMATION
                )
                winsound.MessageBeep(tone)
            except Exception as e:
                logging.warning(f"Failed to play Windows {pattern} sound: {e}")

    @staticmethod
    def play_start_sound():
        """Play recording start sound (similar to system speech recognition)"""
        system = platform.system()
        if system == "Darwin":
            sound_path = "/System/Library/Sounds/Tink.aiff"
            threading.Thread(
                target=SoundPlayer._play_sound, args=(sound_path,), daemon=True
            ).start()
        elif system == "Windows":
            threading.Thread(
                target=SoundPlayer._play_windows_sound, args=("start",), daemon=True
            ).start()

    @staticmethod
    def play_stop_sound():
        """Play recording stop sound"""
        system = platform.system()
        if system == "Darwin":
            sound_path = "/System/Library/Sounds/Pop.aiff"
            threading.Thread(
                target=SoundPlayer._play_sound, args=(sound_path,), daemon=True
            ).start()
        elif system == "Windows":
            threading.Thread(
                target=SoundPlayer._play_windows_sound, args=("stop",), daemon=True
            ).start()


class Recorder:
    def __init__(
        self, transcriber, frames_per_buffer=512, warmup_buffers=2, debug=False
    ):
        self.recording = False
        self.transcriber = transcriber
        self.sound_player = SoundPlayer()
        self.frames_per_buffer = frames_per_buffer
        self.warmup_buffers = warmup_buffers
        self.debug = debug

        # Store audio parameters for watchdog restart
        self.p = None
        self.stream = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.FRAMES_PER_BUFFER = frames_per_buffer

    def start(self, language=None):
        thread = threading.Thread(target=self._record_impl, args=(language,))
        thread.start()

    def stop(self):
        global recording
        self.recording = False
        recording = False  # Reset global flag immediately

    def close(self):
        """Close audio resources for shutdown."""
        if hasattr(self, "stream") and self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        if hasattr(self, "p") and self.p:
            try:
                self.p.terminate()
            except Exception:
                pass

    def _record_impl(self, language):
        import os

        global recording

        self.recording = True
        recording = True  # Set global flag for watchdog
        update_heartbeat()

        # Play recording start sound
        self.sound_player.play_start_sound()

        # Resolve frames_per_buffer from ENV override if provided
        env_fpb = os.getenv("WHISPER_FRAMES_PER_BUFFER")
        try:
            frames_per_buffer = int(env_fpb) if env_fpb else int(self.frames_per_buffer)
        except Exception:
            frames_per_buffer = int(self.frames_per_buffer)

        self.p = pyaudio.PyAudio()
        self.FRAMES_PER_BUFFER = frames_per_buffer

        def open_stream(fpb):
            return self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                frames_per_buffer=fpb,
                input=True,
            )

        self.stream = open_stream(frames_per_buffer)
        frames = []

        # Warm-up: discard first N buffers to stabilize stream
        for _ in range(int(self.warmup_buffers)):
            try:
                _ = self.stream.read(frames_per_buffer, exception_on_overflow=False)
            except Exception:
                pass

        # Main read loop with simple auto-fallback on early errors
        errors = 0
        reads = 0
        escalated = False

        while self.recording:
            try:
                data = self.stream.read(frames_per_buffer, exception_on_overflow=False)
                frames.append(data)
                # Update heartbeat after successful read
                update_heartbeat()
            except Exception:
                errors += 1
                if self.debug:
                    print(f"[Recorder] read error (errors={errors})")
            finally:
                reads += 1

            # Auto-fallback logic only in the first 10 reads, single escalation
            if (
                not escalated
                and reads <= 10
                and errors >= 3
                and frames_per_buffer < 1024
            ):
                try:
                    if self.debug:
                        print(
                            f"[Recorder] escalating frames_per_buffer {frames_per_buffer} -> 1024 and reopening stream"
                        )
                    self.stream.stop_stream()
                    self.stream.close()
                    frames_per_buffer = 1024
                    self.stream = open_stream(frames_per_buffer)
                    # Warm-up again after reopen
                    for _ in range(int(self.warmup_buffers)):
                        try:
                            _ = self.stream.read(
                                frames_per_buffer, exception_on_overflow=False
                            )
                        except Exception:
                            pass
                    errors = 0
                    reads = 0
                    escalated = True
                except Exception as e:
                    if self.debug:
                        print(f"[Recorder] escalation failed: {e}")
                    # If escalation fails, continue with current settings
                    escalated = True

        # Cleanup
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # Reset global recording flag
        recording = False

        # Play recording stop sound
        self.sound_player.play_stop_sound()

        audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)
        audio_data_fp32 = audio_data.astype(np.float32) / 32768.0
        try:
            self.transcriber.transcribe(audio_data_fp32, language)
        except Exception as e:
            logging.error(f"Transcription failed: {e}", exc_info=True)


class GlobalKeyListener:
    def __init__(self, app, key_combination):
        self.app = app
        self.key1, self.key2 = self.parse_key_combination(key_combination)
        self.key1_pressed = False
        self.key2_pressed = False

    def parse_key_combination(self, key_combination):
        key1_name, key2_name = key_combination.split("+")
        key1 = getattr(keyboard.Key, key1_name, keyboard.KeyCode(char=key1_name))
        key2 = getattr(keyboard.Key, key2_name, keyboard.KeyCode(char=key2_name))
        return key1, key2

    def on_key_press(self, key):
        if key == self.key1:
            self.key1_pressed = True
        elif key == self.key2:
            self.key2_pressed = True

        if self.key1_pressed and self.key2_pressed:
            self.app.toggle()

    def on_key_release(self, key):
        if key == self.key1:
            self.key1_pressed = False
        elif key == self.key2:
            self.key2_pressed = False


class DoubleCommandKeyListener:
    def __init__(self, app):
        self.app = app
        self.key = keyboard.Key.cmd_l
        self.pressed = 0
        self.last_press_time = 0

    def on_key_press(self, key):
        is_listening = self.app.started
        if key == self.key:
            current_time = time.time()
            if (
                not is_listening and current_time - self.last_press_time < 0.5
            ):  # Double click to start listening
                self.app.toggle()
            elif is_listening:  # Single click to stop listening
                self.app.toggle()
            self.last_press_time = current_time

    def on_key_release(self, key):
        pass


class BaseRuntimeApp:
    def __init__(self, recorder, languages=None, max_time=None):
        self.languages = languages
        self.current_language = languages[0] if languages is not None else None
        self.started = False
        self.recorder = recorder
        self.max_time = max_time
        self.timer = None

    def start_app(self, _):
        if self.started:
            return

        print(f"{get_timestamp()} Listening...")
        self.started = True
        self.recorder.start(self.current_language)
        self.on_started()

        if self.max_time is not None:
            self.timer = threading.Timer(self.max_time, lambda: self.stop_app(None))
            self.timer.start()

    def stop_app(self, _):
        if not self.started:
            return

        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

        print(f"{get_timestamp()} Transcribing...")
        self.started = False
        self.recorder.stop()
        self.on_stopped()

    def toggle(self):
        if self.started:
            self.stop_app(None)
        else:
            self.start_app(None)

    def on_started(self):
        """Hook for runtime-specific UI state updates."""

    def on_stopped(self):
        """Hook for runtime-specific UI state updates."""

    def run(self):
        raise NotImplementedError


if rumps is not None:

    class StatusBarApp(rumps.App, BaseRuntimeApp):
        def __init__(self, recorder, languages=None, max_time=None):
            rumps.App.__init__(self, "whisper", "⏯")
            BaseRuntimeApp.__init__(self, recorder, languages, max_time)
            self.elapsed_time = 0

            menu = [
                "Start Recording",
                "Stop Recording",
                None,
            ]

            if languages is not None:
                for lang in languages:
                    callback = (
                        self.change_language if lang != self.current_language else None
                    )
                    menu.append(rumps.MenuItem(lang, callback=callback))
                menu.append(None)

            self.menu = menu
            self.menu["Stop Recording"].set_callback(None)

        def change_language(self, sender):
            self.current_language = sender.title
            for lang in self.languages:
                self.menu[lang].set_callback(
                    self.change_language if lang != self.current_language else None
                )

        @rumps.clicked("Start Recording")
        def start_app(self, _):
            BaseRuntimeApp.start_app(self, _)
            self.menu["Start Recording"].set_callback(None)
            self.menu["Stop Recording"].set_callback(self.stop_app)
            self.start_time = time.time()
            self.update_title()

        @rumps.clicked("Stop Recording")
        def stop_app(self, _):
            if not self.started:
                return
            self.title = "⏯"
            BaseRuntimeApp.stop_app(self, _)
            self.menu["Stop Recording"].set_callback(None)
            self.menu["Start Recording"].set_callback(self.start_app)

        def update_title(self):
            if self.started:
                self.elapsed_time = int(time.time() - self.start_time)
                minutes, seconds = divmod(self.elapsed_time, 60)
                self.title = f"({minutes:02d}:{seconds:02d}) 🔴"
                threading.Timer(1, self.update_title).start()

else:

    class StatusBarApp(BaseRuntimeApp):
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "macOS status bar runtime is unavailable because rumps could not be imported."
            )


class WindowsTrayApp(BaseRuntimeApp):
    def __init__(self, recorder, languages=None, max_time=None):
        super().__init__(recorder, languages, max_time)
        if pystray is None or Image is None or ImageDraw is None:
            raise RuntimeError(
                "Windows tray runtime requires pystray and Pillow. Install requirements and retry."
            )
        self.icon = None

    def _create_icon_image(self):
        image = Image.new("RGB", (64, 64), color=(22, 22, 22))
        draw = ImageDraw.Draw(image)
        draw.ellipse((12, 12, 52, 52), fill=(230, 230, 230))
        draw.ellipse((24, 24, 40, 40), fill=(220, 30, 30))
        return image

    def _on_menu_start(self, icon, item):
        self.start_app(None)
        self._refresh_menu()

    def _on_menu_stop(self, icon, item):
        self.stop_app(None)
        self._refresh_menu()

    def _on_menu_exit(self, icon, item):
        shutdown_application()
        icon.stop()

    def _refresh_menu(self):
        if self.icon is not None:
            self.icon.update_menu()

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem(
                "Start Recording",
                self._on_menu_start,
                enabled=lambda _: not self.started,
            ),
            pystray.MenuItem(
                "Stop Recording",
                self._on_menu_stop,
                enabled=lambda _: self.started,
            ),
            pystray.MenuItem("Exit", self._on_menu_exit),
        )
        self.icon = pystray.Icon(
            "whisper-dictation",
            self._create_icon_image(),
            "Whisper Dictation",
            menu,
        )
        self.icon.run()

    def on_started(self):
        self._refresh_menu()

    def on_stopped(self):
        self._refresh_menu()


class HeadlessRuntimeApp(BaseRuntimeApp):
    def run(self):
        print("Running without tray/status bar UI. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dictation app using the OpenAI whisper ASR model. By default the keyboard shortcut cmd+option "
        "starts and stops dictation"
    )
    parser.add_argument(
        "-m",
        "--model_name",
        type=str,
        choices=[
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
        ],
        default="base",
        help="Specify the whisper ASR model to use. Options: tiny, base, small, medium, or large. "
        "To see the  most up to date list of models along with model size, memory footprint, and estimated "
        "transcription speed check out this [link](https://github.com/openai/whisper#available-models-and-languages). "
        "Note that the models ending in .en are trained only on English speech and will perform better on English "
        "language. Note that the small, medium, and large models may be slow to transcribe and are only recommended "
        "if you find the base model to be insufficient. Default: base.",
    )
    parser.add_argument(
        "-k",
        "--key_combination",
        type=str,
        default="cmd_l+alt" if platform.system() == "Darwin" else "ctrl+alt",
        help="Specify the key combination to toggle the app. Example: cmd_l+alt for macOS "
        "ctrl+alt for other platforms. Default: cmd_r+alt (macOS) or ctrl+alt (others).",
    )
    parser.add_argument(
        "--k_double_cmd",
        action="store_true",
        help="If set, use double Right Command key press on macOS to toggle the app (double click to begin recording, single click to stop recording). "
        "Ignores the --key_combination argument.",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default=None,
        help='Specify the two-letter language code (e.g., "en" for English) to improve recognition accuracy. '
        "This can be especially helpful for smaller model sizes.  To see the full list of supported languages, "
        "check out the official list [here](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py).",
    )
    parser.add_argument(
        "--allowed_languages",
        type=str,
        default=None,
        help='Comma-separated list of allowed languages (e.g., "en,pl"). '
        "If specified, language detection will be constrained to these languages only.",
    )
    parser.add_argument(
        "-t",
        "--max_time",
        type=float,
        default=120,
        help="Specify the maximum recording time in seconds. The app will automatically stop recording after this duration. "
        "Default: 120 seconds.",
    )
    parser.add_argument(
        "--frames-per-buffer",
        dest="frames_per_buffer",
        type=int,
        choices=[256, 512, 1024],
        default=512,
        help="Frames per buffer for audio input. Default: 512. Can be overridden by env WHISPER_FRAMES_PER_BUFFER.",
    )
    parser.add_argument(
        "--warmup-buffers",
        dest="warmup_buffers",
        type=int,
        default=2,
        help="Number of warm-up buffers to discard right after opening the stream. Default: 2.",
    )
    parser.add_argument(
        "--debug-recorder",
        dest="debug_recorder",
        action="store_true",
        help="Enable verbose debug logs for Recorder (startup timing, escalation).",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level. Default: INFO.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Override default log file location. Default: ~/.whisper-dictation.log",
    )

    args = parser.parse_args()

    if args.language is not None:
        args.language = args.language.split(",")

    if (
        args.model_name.endswith(".en")
        and args.language is not None
        and any(lang != "en" for lang in args.language)
    ):
        raise ValueError(
            "If using a model ending in .en, you cannot specify a language other than English."
        )

    return args


if __name__ == "__main__":
    args = parse_args()

    # Initialize logging early
    log_file = Path(args.log_file) if args.log_file else None
    setup_logging(args.log_level, log_file)

    # Log application startup
    logging.info(f"Application starting up, PID={os.getpid()}")
    logging.info(f"Log level: {args.log_level}")
    if log_file:
        logging.info(f"Log file: {log_file}")

    # Setup lock file to prevent multiple instances
    setup_lock_file()
    logging.info("Lock file mechanism initialized")

    # Register signal handlers for graceful shutdown
    register_signal_handlers()
    logging.info("Signal handlers registered")

    # Test microphone access on startup
    test_microphone_access()
    logging.info("Microphone check completed")

    # Start audio watchdog thread
    start_watchdog()
    logging.info("Audio watchdog started")

    # Import DeviceManager for intelligent device handling
    from device_manager import OperationType
    from mps_optimizer import EnhancedDeviceManager

    # Initialize Enhanced DeviceManager
    device_manager = EnhancedDeviceManager()
    logging.info("Device manager initialized")

    # Get optimal device for model loading
    device = device_manager.get_device_for_operation(
        OperationType.MODEL_LOADING, args.model_name
    )
    logging.info(f"DeviceManager: Selected {device} for model {args.model_name}")

    print(f"Loading model '{args.model_name}'...")
    print(
        "If this is the first run for this model, it will be downloaded and cached automatically."
    )
    model_name = args.model_name
    logging.info(f"Loading model: {model_name} on device: {device}")

    try:
        model = load_model(model_name, device=device)
        print(f"✅ {model_name} model loaded successfully on {device}")
        logging.info(f"Model loaded successfully: {model_name} on {device}")

        # Apply device optimizations
        device_manager.optimize_model(model, device)
        logging.debug("Model optimizations applied")

        # Register successful loading
        device_manager.base_manager.register_operation_success(
            device, OperationType.MODEL_LOADING
        )

    except Exception as e:
        logging.error(f"Model loading failed on {device}: {e}")
        if device_manager.base_manager.should_retry_with_fallback(e):
            fallback_device, user_message = device_manager.handle_device_error_enhanced(
                e, OperationType.MODEL_LOADING, device
            )
            print(f"🔄 {user_message}")
            print(f"Details: Switching from {device} to {fallback_device}")
            logging.warning(f"Retrying with fallback device: {fallback_device}")

            device = fallback_device
            model = load_model(model_name, device=device)
            device_manager.optimize_model(model, device)
            print(
                f"✅ {model_name} model loaded successfully on fallback device: {device}"
            )
            logging.info(f"Model loaded on fallback device: {model_name} on {device}")

            # Register successful fallback
            device_manager.base_manager.register_operation_success(
                device, OperationType.MODEL_LOADING
            )
        else:
            logging.error(f"Model loading failed completely: {e}")
            raise e

    # Parse allowed languages if specified
    allowed_languages = None
    if args.allowed_languages:
        allowed_languages = [lang.strip() for lang in args.allowed_languages.split(",")]
        print(f"Language detection constrained to: {allowed_languages}")
        logging.info(f"Language detection constrained to: {allowed_languages}")

    transcriber = SpeechTranscriber(model, allowed_languages, device_manager)
    logging.info("Speech transcriber initialized")

    recorder = Recorder(
        transcriber,
        frames_per_buffer=args.frames_per_buffer,
        warmup_buffers=args.warmup_buffers,
        debug=bool(args.debug_recorder or os.getenv("WHISPER_DEBUG_RECORDER")),
    )
    logging.info(
        f"Recorder initialized with frames_per_buffer={args.frames_per_buffer}, warmup_buffers={args.warmup_buffers}"
    )

    system = platform.system()
    if system == "Darwin":
        app = StatusBarApp(recorder, args.language, args.max_time)
        logging.info("macOS status bar app initialized")
    elif system == "Windows":
        app = WindowsTrayApp(recorder, args.language, args.max_time)
        logging.info("Windows tray app initialized")
    else:
        app = HeadlessRuntimeApp(recorder, args.language, args.max_time)
        logging.info("Headless runtime app initialized")

    if args.k_double_cmd and system != "Darwin":
        logging.warning(
            "--k_double_cmd is only supported on macOS. Falling back to --key_combination."
        )
        args.k_double_cmd = False

    if args.k_double_cmd:
        key_listener = DoubleCommandKeyListener(app)
        logging.info("Using double command key listener")
    else:
        key_listener = GlobalKeyListener(app, args.key_combination)
        logging.info(
            f"Using global key listener with combination: {args.key_combination}"
        )

    listener = keyboard.Listener(
        on_press=key_listener.on_key_press, on_release=key_listener.on_key_release
    )
    listener.start()
    logging.info("Keyboard listener started")

    print("Running... ")
    logging.info("Application ready - entering main loop")
    try:
        app.run()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received")
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise
    finally:
        shutdown_application()
        logging.info("Application shutdown complete")
