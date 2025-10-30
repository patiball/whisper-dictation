import argparse
import time
import threading
import pyaudio
import numpy as np
import rumps
from pynput import keyboard
from whisper import load_model
import platform
import subprocess
import os
import torch
from datetime import datetime
import signal
import atexit
import json
import psutil
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

def get_timestamp():
    """Returns formatted timestamp [HH:MM:SS.mmm]"""
    return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"

def setup_logging(log_level='INFO', log_file=None):
    """Configure centralized logging with rotation and console output."""
    if log_file is None:
        log_file = Path.home() / ".whisper-dictation.log"
    
    try:
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
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
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        return False

class SpeechTranscriber:
    def __init__(self, model, allowed_languages=None, device_manager=None):
        self.model = model
        self.pykeyboard = keyboard.Controller()
        self.allowed_languages = allowed_languages
        self.device_manager = device_manager
        
        # Get device from model if device_manager not provided
        if hasattr(model, 'device'):
            self.device = str(model.device)
        else:
            self.device = "cpu"
        
        print(f"SpeechTranscriber: Używam urządzenia {self.device}")
        logging.debug(f"SpeechTranscriber initialized with device: {self.device}")

    def transcribe(self, audio_data, language=None):
        start_time = time.time()
        logging.debug(f"Starting transcription, language: {language or 'auto'}")
        
        # Get optimized options from device manager if available
        if self.device_manager:
            options = self.device_manager.get_optimized_settings(self.device, "base")  # Default to base model
            if language:
                options["language"] = language
            logging.debug("Using device manager optimized settings")
        else:
            # Fallback to original options
            options = {
                "fp16": self.device == "mps",  # Użyj half precision na GPU
                "language": language,
                "task": "transcribe",
                "no_speech_threshold": 0.6,  # Zwiększ próg dla lepszej wydajności
                "logprob_threshold": -1.0,
                "compression_ratio_threshold": 2.4
            }
            logging.debug("Using fallback transcription options")
        
        # If we have allowed languages and no specific language is set, detect and constrain
        if self.allowed_languages and language is None:
            logging.debug("Detecting language with allowed constraints")
            # First, detect the language without constraining
            result = self.model.transcribe(audio_data, **{k: v for k, v in options.items() if k != "language"})
            detected_lang = result.get('language', 'en')
            logging.debug(f"Detected language: {detected_lang}")
            
            # If detected language is not in allowed list, use the first allowed language
            if detected_lang not in self.allowed_languages:
                options["language"] = self.allowed_languages[0]
                logging.info(f"Constraining to allowed language: {self.allowed_languages[0]} (detected: {detected_lang})")
            else:
                options["language"] = detected_lang
                logging.debug(f"Using detected language: {detected_lang}")
            
            # Re-transcribe with the constrained language
            result = self.model.transcribe(audio_data, **options)
        else:
            result = self.model.transcribe(audio_data, **options)

        duration = time.time() - start_time
        text = result.get('text', '').strip()
        logging.info(f"Transcription complete in {duration:.2f}s, text length: {len(text)}")
        
        print(f'{get_timestamp()} Transcription complete')
        print(f'{get_timestamp()} Typing text...')
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
    """Klasa do odtwarzania dźwięków systemowych macOS"""

    @staticmethod
    def _play_sound(sound_path):
        try:
            subprocess.run(['afplay', sound_path], check=False, capture_output=True)
        except Exception:
            pass  # Cicho ignorujemy błędy odtwarzania dźwięku

    @staticmethod
    def play_start_sound():
        """Odtwarza dźwięk rozpoczęcia nagrywania (jak w systemowym rozpoznawaniu mowy)"""
        if platform.system() == 'Darwin':  # macOS
            sound_path = '/System/Library/Sounds/Tink.aiff'
            threading.Thread(target=SoundPlayer._play_sound, args=(sound_path,)).start()

    @staticmethod
    def play_stop_sound():
        """Odtwarza dźwięk zakończenia nagrywania"""
        if platform.system() == 'Darwin':  # macOS
            sound_path = '/System/Library/Sounds/Pop.aiff'
            threading.Thread(target=SoundPlayer._play_sound, args=(sound_path,)).start()

class Recorder:
    def __init__(self, transcriber, frames_per_buffer=512, warmup_buffers=2, debug=False):
        self.recording = False
        self.transcriber = transcriber
        self.sound_player = SoundPlayer()
        self.frames_per_buffer = frames_per_buffer
        self.warmup_buffers = warmup_buffers
        self.debug = debug

    def start(self, language=None):
        thread = threading.Thread(target=self._record_impl, args=(language,))
        thread.start()

    def stop(self):
        self.recording = False


    def _record_impl(self, language):
        import os
        self.recording = True
        
        # Odtwórz dźwięk rozpoczęcia nagrywania
        self.sound_player.play_start_sound()
        
        # Resolve frames_per_buffer from ENV override if provided
        env_fpb = os.getenv('WHISPER_FRAMES_PER_BUFFER')
        try:
            frames_per_buffer = int(env_fpb) if env_fpb else int(self.frames_per_buffer)
        except Exception:
            frames_per_buffer = int(self.frames_per_buffer)
        
        p = pyaudio.PyAudio()

        def open_stream(fpb):
            return p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          frames_per_buffer=fpb,
                          input=True)
        
        stream = open_stream(frames_per_buffer)
        frames = []
        
        # Warm-up: discard first N buffers to stabilize stream
        for _ in range(int(self.warmup_buffers)):
            try:
                _ = stream.read(frames_per_buffer, exception_on_overflow=False)
            except Exception:
                pass
        
        # Main read loop with simple auto-fallback on early errors
        errors = 0
        reads = 0
        escalated = False
        
        while self.recording:
            try:
                data = stream.read(frames_per_buffer, exception_on_overflow=False)
                frames.append(data)
            except Exception:
                errors += 1
                if self.debug:
                    print(f"[Recorder] read error (errors={errors})")
            finally:
                reads += 1
            
            # Auto-fallback logic only in the first 10 reads, single escalation
            if not escalated and reads <= 10 and errors >= 3 and frames_per_buffer < 1024:
                try:
                    if self.debug:
                        print(f"[Recorder] escalating frames_per_buffer {frames_per_buffer} -> 1024 and reopening stream")
                    stream.stop_stream()
                    stream.close()
                    frames_per_buffer = 1024
                    stream = open_stream(frames_per_buffer)
                    # Warm-up again after reopen
                    for _ in range(int(self.warmup_buffers)):
                        try:
                            _ = stream.read(frames_per_buffer, exception_on_overflow=False)
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
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Odtwórz dźwięk zakończenia nagrywania
        self.sound_player.play_stop_sound()
        
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio_data_fp32 = audio_data.astype(np.float32) / 32768.0
        self.transcriber.transcribe(audio_data_fp32, language)


class GlobalKeyListener:
    def __init__(self, app, key_combination):
        self.app = app
        self.key1, self.key2 = self.parse_key_combination(key_combination)
        self.key1_pressed = False
        self.key2_pressed = False

    def parse_key_combination(self, key_combination):
        key1_name, key2_name = key_combination.split('+')
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
            if not is_listening and current_time - self.last_press_time < 0.5:  # Double click to start listening
                self.app.toggle()
            elif is_listening:  # Single click to stop listening
                self.app.toggle()
            self.last_press_time = current_time

    def on_key_release(self, key):
        pass

class StatusBarApp(rumps.App):
    def __init__(self, recorder, languages=None, max_time=None):
        super().__init__("whisper", "⏯")
        self.languages = languages
        self.current_language = languages[0] if languages is not None else None

        menu = [
            'Start Recording',
            'Stop Recording',
            None,
        ]

        if languages is not None:
            for lang in languages:
                callback = self.change_language if lang != self.current_language else None
                menu.append(rumps.MenuItem(lang, callback=callback))
            menu.append(None)
            
        self.menu = menu
        self.menu['Stop Recording'].set_callback(None)

        self.started = False
        self.recorder = recorder
        self.max_time = max_time
        self.timer = None
        self.elapsed_time = 0

    def change_language(self, sender):
        self.current_language = sender.title
        for lang in self.languages:
            self.menu[lang].set_callback(self.change_language if lang != self.current_language else None)

    @rumps.clicked('Start Recording')
    def start_app(self, _):
        print(f'{get_timestamp()} Listening...')
        self.started = True
        self.menu['Start Recording'].set_callback(None)
        self.menu['Stop Recording'].set_callback(self.stop_app)
        self.recorder.start(self.current_language)

        if self.max_time is not None:
            self.timer = threading.Timer(self.max_time, lambda: self.stop_app(None))
            self.timer.start()

        self.start_time = time.time()
        self.update_title()

    @rumps.clicked('Stop Recording')
    def stop_app(self, _):
        if not self.started:
            return
        
        if self.timer is not None:
            self.timer.cancel()

        print(f'{get_timestamp()} Transcribing...')
        self.title = "⏯"
        self.started = False
        self.menu['Stop Recording'].set_callback(None)
        self.menu['Start Recording'].set_callback(self.start_app)
        self.recorder.stop()

    def update_title(self):
        if self.started:
            self.elapsed_time = int(time.time() - self.start_time)
            minutes, seconds = divmod(self.elapsed_time, 60)
            self.title = f"({minutes:02d}:{seconds:02d}) 🔴"
            threading.Timer(1, self.update_title).start()

    def toggle(self):
        if self.started:
            self.stop_app(None)
        else:
            self.start_app(None)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Dictation app using the OpenAI whisper ASR model. By default the keyboard shortcut cmd+option '
        'starts and stops dictation')
    parser.add_argument('-m', '--model_name', type=str,
                        choices=['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en', 'large'],
                        default='base',
                        help='Specify the whisper ASR model to use. Options: tiny, base, small, medium, or large. '
                        'To see the  most up to date list of models along with model size, memory footprint, and estimated '
                        'transcription speed check out this [link](https://github.com/openai/whisper#available-models-and-languages). '
                        'Note that the models ending in .en are trained only on English speech and will perform better on English '
                        'language. Note that the small, medium, and large models may be slow to transcribe and are only recommended '
                        'if you find the base model to be insufficient. Default: base.')
    parser.add_argument('-k', '--key_combination', type=str, default='cmd_l+alt' if platform.system() == 'Darwin' else 'ctrl+alt',
                        help='Specify the key combination to toggle the app. Example: cmd_l+alt for macOS '
                        'ctrl+alt for other platforms. Default: cmd_r+alt (macOS) or ctrl+alt (others).')
    parser.add_argument('--k_double_cmd', action='store_true',
                            help='If set, use double Right Command key press on macOS to toggle the app (double click to begin recording, single click to stop recording). '
                                 'Ignores the --key_combination argument.')
    parser.add_argument('-l', '--language', type=str, default=None,
                        help='Specify the two-letter language code (e.g., "en" for English) to improve recognition accuracy. '
                        'This can be especially helpful for smaller model sizes.  To see the full list of supported languages, '
                        'check out the official list [here](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py).')
    parser.add_argument('--allowed_languages', type=str, default=None,
                        help='Comma-separated list of allowed languages (e.g., "en,pl"). '
                        'If specified, language detection will be constrained to these languages only.')
    parser.add_argument('-t', '--max_time', type=float, default=120,
                        help='Specify the maximum recording time in seconds. The app will automatically stop recording after this duration. '
                        'Default: 120 seconds.')
    parser.add_argument('--frames-per-buffer', dest='frames_per_buffer', type=int, choices=[256,512,1024], default=512,
                        help='Frames per buffer for audio input. Default: 512. Can be overridden by env WHISPER_FRAMES_PER_BUFFER.')
    parser.add_argument('--warmup-buffers', dest='warmup_buffers', type=int, default=2,
                        help='Number of warm-up buffers to discard right after opening the stream. Default: 2.')
    parser.add_argument('--debug-recorder', dest='debug_recorder', action='store_true',
                        help='Enable verbose debug logs for Recorder (startup timing, escalation).')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Set logging level. Default: INFO.')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Override default log file location. Default: ~/.whisper-dictation.log')

    args = parser.parse_args()

    if args.language is not None:
        args.language = args.language.split(',')

    if args.model_name.endswith('.en') and args.language is not None and any(lang != 'en' for lang in args.language):
        raise ValueError('If using a model ending in .en, you cannot specify a language other than English.')

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

    # Import DeviceManager for intelligent device handling
    from device_manager import DeviceManager, OperationType
    from mps_optimizer import EnhancedDeviceManager
    
    # Initialize Enhanced DeviceManager
    device_manager = EnhancedDeviceManager()
    logging.info("Device manager initialized")
    
    # Get optimal device for model loading
    device = device_manager.get_device_for_operation(OperationType.MODEL_LOADING, args.model_name)
    logging.info(f"DeviceManager: Selected {device} for model {args.model_name}")

    print("Loading model...")
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
        device_manager.base_manager.register_operation_success(device, OperationType.MODEL_LOADING)
        
    except Exception as e:
        logging.error(f"Model loading failed on {device}: {e}")
        if device_manager.base_manager.should_retry_with_fallback(e):
            fallback_device, user_message = device_manager.handle_device_error_enhanced(
                e, OperationType.MODEL_LOADING, device
            )
            print(f"🔄 {user_message}")
            print(f"Szczegóły: Przełączam z {device} na {fallback_device}")
            logging.warning(f"Retrying with fallback device: {fallback_device}")
            
            device = fallback_device
            model = load_model(model_name, device=device)
            device_manager.optimize_model(model, device)
            print(f"✅ {model_name} model loaded successfully on fallback device: {device}")
            logging.info(f"Model loaded on fallback device: {model_name} on {device}")
            
            # Register successful fallback
            device_manager.base_manager.register_operation_success(device, OperationType.MODEL_LOADING)
        else:
            logging.error(f"Model loading failed completely: {e}")
            raise e
    
    # Parse allowed languages if specified
    allowed_languages = None
    if args.allowed_languages:
        allowed_languages = [lang.strip() for lang in args.allowed_languages.split(',')]
        print(f"Language detection constrained to: {allowed_languages}")
        logging.info(f"Language detection constrained to: {allowed_languages}")
    
    transcriber = SpeechTranscriber(model, allowed_languages, device_manager)
    logging.info("Speech transcriber initialized")
    
    recorder = Recorder(
        transcriber,
        frames_per_buffer=args.frames_per_buffer,
        warmup_buffers=args.warmup_buffers,
        debug=bool(args.debug_recorder or os.getenv('WHISPER_DEBUG_RECORDER')),
    )
    logging.info(f"Recorder initialized with frames_per_buffer={args.frames_per_buffer}, warmup_buffers={args.warmup_buffers}")
    
    app = StatusBarApp(recorder, args.language, args.max_time)
    logging.info("Status bar app initialized")
    
    if args.k_double_cmd:
        key_listener = DoubleCommandKeyListener(app)
        logging.info("Using double command key listener")
    else:
        key_listener = GlobalKeyListener(app, args.key_combination)
        logging.info(f"Using global key listener with combination: {args.key_combination}")
        
    listener = keyboard.Listener(on_press=key_listener.on_key_press, on_release=key_listener.on_key_release)
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
        logging.info("Application shutdown complete")

