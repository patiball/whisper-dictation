#!/usr/bin/env python3
import argparse
import time
import threading
import pyaudio
import numpy as np
import rumps
from pynput import keyboard
import platform
import subprocess
import os
import tempfile
import wave
from datetime import datetime

def get_timestamp():
    """Returns formatted timestamp [HH:MM:SS.mmm]"""
    return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"

class SpeechTranscriber:
    def __init__(self, model_path, allowed_languages=None, model_name='base', max_recording_time=120):
        self.model_path = model_path
        self.pykeyboard = keyboard.Controller()
        self.allowed_languages = allowed_languages
        self.model_name = model_name
        self.max_recording_time = max_recording_time
        print(f"Używam whisper.cpp z modelem: {model_path}")

    def transcribe(self, audio_data, language=None):
        
        # Zapisz audio do tymczasowego pliku WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
            
        # Konwertuj audio do WAV
        with wave.open(temp_wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            # Konwertuj float32 z powrotem do int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        try:
            # Jeśli mamy ograniczenia językowe i nie określono języka, użyj auto-detect w jednym przebiegu
            detected_language = language
            
            # Jedna faza: transkrypcja z automatycznym wykrywaniem języka (jeśli potrzebne)
            cmd = [
                '/opt/homebrew/bin/whisper-cli',  # whisper.cpp binary
                '-m', self.model_path,
                '-nt',  # Bez timestampów
                '-t', '8',  # Użyj 8 wątków dla M1
                '-np',  # Nie drukuj dodatkowych informacji
                # NOTE: Do NOT include -tr/--translate flag - it defaults to false (transcribe mode)
                temp_wav_path  # plik audio jako ostatni argument
            ]
            
            # Dodaj język lub użyj auto-detection
            if detected_language:
                cmd.insert(-1, '-l')
                cmd.insert(-1, detected_language)
                cmd.insert(-1, '-np')  # No prints for clean output
            else:
                # Auto-detect mode - use 'auto' for language detection (from whisper-dictation-optimized.py)
                cmd.insert(-1, '-l')
                cmd.insert(-1, 'auto')
                # Don't add -np to see verbose output with detected language
            
            # Domyślnie whisper-cli używa GPU na M1 jeśli dostępny
            
            # Calculate dynamic timeout based on model and recording time
            timeout = calculate_whisper_timeout(self.model_name, self.max_recording_time)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

            if result.returncode == 0:
                print(f'{get_timestamp()} Transcription complete')
                # Pobierz tekst ze stdout
                text = result.stdout.strip()
                if text:
                    print(f'{get_timestamp()} Typing text...')
                    # Wpisz tekst znak po znak
                    is_first = True
                    for element in text:
                        if is_first and element == " ":
                            is_first = False
                            continue
                        
                        try:
                            self.pykeyboard.type(element)
                            time.sleep(0.0025)
                        except:
                            pass
                else:
                    print("Pusty rezultat transkrypcji")
            else:
                print(f"Błąd whisper.cpp: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("Timeout podczas transkrypcji")
        except Exception as e:
            print(f"Błąd: {e}")
        finally:
            # Wyczyść tymczasowe pliki
            if os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)

class SoundPlayer:
    """Klasa do odtwarzania dźwięków systemowych macOS"""
    
    @staticmethod
    def play_start_sound():
        """Odtwarza dźwięk rozpoczęcia nagrywania (jak w systemowym rozpoznawaniu mowy)"""
        if platform.system() == 'Darwin':  # macOS
            try:
                # Używamy Tink - krótki, przyjemny dźwięk często używany w systemie
                subprocess.run(['afplay', '/System/Library/Sounds/Tink.aiff'], 
                             check=False, capture_output=True)
            except Exception:
                pass  # Cicho ignorujemy błędy odtwarzania dźwięku
    
    @staticmethod
    def play_stop_sound():
        """Odtwarza dźwięk zakończenia nagrywania"""
        if platform.system() == 'Darwin':  # macOS
            try:
                # Używamy Pop - krótki dźwięk sygnalizujący zakończenie
                subprocess.run(['afplay', '/System/Library/Sounds/Pop.aiff'], 
                             check=False, capture_output=True)
            except Exception:
                pass  # Cicho ignorujemy błędy odtwarzania dźwięku

class Recorder:
    def __init__(self, transcriber):
        self.recording = False
        self.transcriber = transcriber
        self.sound_player = SoundPlayer()

    def start(self, language=None):
        thread = threading.Thread(target=self._record_impl, args=(language,))
        thread.start()

    def stop(self):
        self.recording = False

    def _record_impl(self, language):
        self.recording = True

        frames_per_buffer = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        frames_per_buffer=frames_per_buffer,
                        input=True)
        frames = []

        # Delay start sound to avoid interfering with recording
        threading.Timer(0.1, self.sound_player.play_start_sound).start()

        while self.recording:
            data = stream.read(frames_per_buffer)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Process audio data before stop sound
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio_data_fp32 = audio_data.astype(np.float32) / 32768.0

        # Play stop sound immediately (no delay - per user request)
        self.sound_player.play_stop_sound()

        # Transcribe after sound
        self.transcriber.transcribe(audio_data_fp32, language)

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
        super().__init__("whisper-fast", "⚡")
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
        self.title = "⚡"
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

def calculate_whisper_timeout(model_name, max_recording_time):
    """Calculate timeout for whisper-cli based on model size and recording time"""
    # Model processing time multipliers (smaller models are faster)
    model_multipliers = {
        'tiny': 0.5,   # Very fast
        'base': 1.0,   # Baseline
        'small': 1.5,  # Slower
        'medium': 2.0, # Much slower
        'large': 3.0   # Slowest
    }
    
    base_timeout = max_recording_time * 2  # Base: 2x recording time
    model_multiplier = model_multipliers.get(model_name, 1.0)
    
    # Final timeout with minimum of 30s
    timeout = max(30, int(base_timeout * model_multiplier))
    return timeout

def download_model(model_name):
    """Pobierz model dla whisper.cpp jeśli nie istnieje"""
    models_dir = os.path.expanduser("~/.whisper-models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_mapping = {
        'tiny': 'ggml-tiny.bin',
        'base': 'ggml-base.bin', 
        'small': 'ggml-small.bin',
        'medium': 'ggml-medium.bin',
        'large': 'ggml-large-v3.bin'
    }
    
    model_file = model_mapping.get(model_name, 'ggml-base.bin')
    model_path = os.path.join(models_dir, model_file)
    
    if not os.path.exists(model_path):
        print(f"Pobieranie modelu {model_name}...")
        url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_file}"
        subprocess.run(['curl', '-L', '-o', model_path, url], check=True)
        print(f"Model {model_name} pobrany do {model_path}")
    
    return model_path

def parse_args():
    parser = argparse.ArgumentParser(
        description='Szybka aplikacja dyktowania używająca whisper.cpp z obsługą M1 GPU')
    parser.add_argument('-m', '--model_name', type=str,
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        default='base',
                        help='Model whisper do użycia. Default: base.')
    parser.add_argument('--k_double_cmd', action='store_true',
                        help='Użyj podwójnego naciśnięcia klawisza Command do włączania/wyłączania')
    parser.add_argument('-l', '--language', type=str, default=None,
                        help='Kod języka (np. "en" dla angielskiego)')
    parser.add_argument('--allowed_languages', type=str, default=None,
                        help='Lista dozwolonych języków, np. "en,pl"')
    parser.add_argument('-t', '--max_time', type=float, default=120,
                        help='Maksymalny czas nagrywania w sekundach. Default: 120.')

    args = parser.parse_args()

    if args.language is not None:
        args.language = args.language.split(',')

    if args.allowed_languages:
        args.allowed_languages = [lang.strip() for lang in args.allowed_languages.split(',')]

    return args

if __name__ == "__main__":
    args = parse_args()
    
    # Pobierz model jeśli nie istnieje
    model_path = download_model(args.model_name)
    
    transcriber = SpeechTranscriber(model_path, args.allowed_languages, args.model_name, args.max_time)
    recorder = Recorder(transcriber)
    
    app = StatusBarApp(recorder, args.language, args.max_time)
    key_listener = DoubleCommandKeyListener(app)
    listener = keyboard.Listener(on_press=key_listener.on_key_press, on_release=key_listener.on_key_release)
    listener.start()

    print("Running whisper.cpp version (fast)...")
    app.run()
