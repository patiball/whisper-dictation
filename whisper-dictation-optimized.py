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

class SpeechTranscriber:
    def __init__(self, model_path, allowed_languages=None):
        self.model_path = model_path
        self.pykeyboard = keyboard.Controller()
        self.allowed_languages = allowed_languages
        self.last_detected_language = None  # Cache ostatnio wykrytego języka
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
            # Strategia wyboru języka:
            # 1. Jeśli język jest określony - użyj go
            # 2. Jeśli mamy cache ostatnio wykrytego języka - użyj go (dla wydajności)
            # 3. Jeśli mamy allowed_languages - użyj pierwszy (bezpieczny fallback)
            # 4. Inaczej - auto-detect
            
            target_language = language
            use_detection = False
            
            if not target_language:
                if self.last_detected_language and self.last_detected_language in (self.allowed_languages or []):
                    target_language = self.last_detected_language
                    print(f"Używam cached języka: {target_language}")
                elif self.allowed_languages:
                    # Co 3. wywołanie rób detekcję języka dla sprawdzenia
                    if not hasattr(self, '_detection_counter'):
                        self._detection_counter = 0
                    self._detection_counter += 1
                    
                    if self._detection_counter % 3 == 1:  # Co 3. wywołanie
                        use_detection = True
                        print("Wykrywam język (co 3. wywołanie)")
                    else:
                        target_language = self.allowed_languages[0]
                        print(f"Używam domyślnego języka: {target_language}")
                else:
                    use_detection = True
            
            # Komenda whisper-cli
            cmd = [
                '/opt/homebrew/bin/whisper-cli',
                '-m', self.model_path,
                '-nt',  # Bez timestampów
                '-t', '8',  # Użyj 8 wątków dla M1
                temp_wav_path  # plik audio jako ostatni argument
            ]
            
            # Dodaj język lub pozwól na auto-detect
            if target_language and not use_detection:
                cmd.insert(-1, '-l')
                cmd.insert(-1, target_language)
                cmd.insert(-1, '-np')  # No prints dla czystego outputu
            else:
                # Auto-detect mode - użyj 'auto' dla language detection
                cmd.insert(-1, '-l')
                cmd.insert(-1, 'auto')
                # Nie dodawaj -np, żeby zobaczyć verbose output z wykrywanym językiem
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            process_time = time.time() - start_time
            
            print(f"Czas przetwarzania: {process_time:.2f}s")
            
            if result.returncode == 0:
                # Jeśli używaliśmy auto-detect, spróbuj wyłapać wykryty język
                if use_detection or not target_language:
                    for line in result.stderr.split('\n'):
                        if 'auto-detected language:' in line.lower():
                            if 'auto-detected language:' in line:
                                lang_start = line.find('auto-detected language:') + len('auto-detected language:')
                                detected_lang = line[lang_start:].strip().split()[0]
                                if not self.allowed_languages or detected_lang in self.allowed_languages:
                                    self.last_detected_language = detected_lang
                                    print(f"Wykryto i cached język: {detected_lang}")
                                break
                
                # Pobierz tekst ze stdout
                text = result.stdout.strip()
                if text:
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
        
        # Odtwórz dźwięk rozpoczęcia nagrywania
        self.sound_player.play_start_sound()
        
        # POPRAWKA: Dodaj krótkie opóźnienie po dźwięku startowym
        time.sleep(0.1)  # 100ms na dźwięk i przygotowanie
        
        frames_per_buffer = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        frames_per_buffer=frames_per_buffer,
                        input=True)
        frames = []
        
        # POPRAWKA: Dodaj krótką inicjalizację strumienia
        # Przeczytaj i odrzuć pierwsze kilka próbek (mogą być zniekształcone)
        for _ in range(5):
            stream.read(frames_per_buffer, exception_on_overflow=False)
        
        print("Nagrywanie rozpoczęte...")

        while self.recording:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Odtwórz dźwięk zakończenia nagrywania
        self.sound_player.play_stop_sound()

        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio_data_fp32 = audio_data.astype(np.float32) / 32768.0
        
        print(f"Nagrano {len(audio_data_fp32)/16000:.1f}s audio")
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
        super().__init__("whisper-optimized", "🚀")
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
        print('Listening...')
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

        print('Transcribing...')
        self.title = "🚀"
        self.started = False
        self.menu['Stop Recording'].set_callback(None)
        self.menu['Start Recording'].set_callback(self.start_app)
        self.recorder.stop()
        print('Done.\\n')

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
        description='Zoptymalizowana aplikacja dyktowania używająca whisper.cpp z inteligentnym wykrywaniem języka')
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
    parser.add_argument('-t', '--max_time', type=float, default=30,
                        help='Maksymalny czas nagrywania w sekundach. Default: 30.')

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
    
    transcriber = SpeechTranscriber(model_path, args.allowed_languages)
    recorder = Recorder(transcriber)
    
    app = StatusBarApp(recorder, args.language, args.max_time)
    key_listener = DoubleCommandKeyListener(app)
    listener = keyboard.Listener(on_press=key_listener.on_key_press, on_release=key_listener.on_key_release)
    listener.start()

    print("Running optimized whisper.cpp version...")
    app.run()
