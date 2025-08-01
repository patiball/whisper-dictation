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

class SpeechTranscriber:
    def __init__(self, model, allowed_languages=None):
        self.model = model
        self.pykeyboard = keyboard.Controller()
        self.allowed_languages = allowed_languages
        
        # Sprawdź dostępność GPU na M1
        self.device = "cpu"
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            self.device = "mps"
            print(f"Używam Metal Performance Shaders (GPU) na M1: {self.device}")
        else:
            print(f"Używam CPU: {self.device}")

    def transcribe(self, audio_data, language=None):
        # Dodatkowe opcje dla wydajności
        options = {
            "fp16": self.device == "mps",  # Użyj half precision na GPU
            "language": language,
            "task": "transcribe",
            "no_speech_threshold": 0.6,  # Zwiększ próg dla lepszej wydajności
            "logprob_threshold": -1.0,
            "compression_ratio_threshold": 2.4
        }
        
        # If we have allowed languages and no specific language is set, detect and constrain
        if self.allowed_languages and language is None:
            # First, detect the language without constraining
            result = self.model.transcribe(audio_data, **{k: v for k, v in options.items() if k != "language"})
            detected_lang = result.get('language', 'en')
            
            # If detected language is not in allowed list, use the first allowed language
            if detected_lang not in self.allowed_languages:
                options["language"] = self.allowed_languages[0]
            else:
                options["language"] = detected_lang
            
            # Re-transcribe with the constrained language
            result = self.model.transcribe(audio_data, **options)
        else:
            result = self.model.transcribe(audio_data, **options)
            
        is_first = True
        for element in result["text"]:
            if is_first and element == " ":
                is_first = False
                continue

            try:
                self.pykeyboard.type(element)
                time.sleep(0.0025)
            except:
                pass

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
        
        frames_per_buffer = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        frames_per_buffer=frames_per_buffer,
                        input=True)
        frames = []

        while self.recording:
            data = stream.read(frames_per_buffer)
            frames.append(data)

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
        self.title = "⏯"
        self.started = False
        self.menu['Stop Recording'].set_callback(None)
        self.menu['Start Recording'].set_callback(self.start_app)
        self.recorder.stop()
        print('Done.\n')

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
    parser.add_argument('-t', '--max_time', type=float, default=30,
                        help='Specify the maximum recording time in seconds. The app will automatically stop recording after this duration. '
                        'Default: 30 seconds.')

    args = parser.parse_args()

    if args.language is not None:
        args.language = args.language.split(',')

    if args.model_name.endswith('.en') and args.language is not None and any(lang != 'en' for lang in args.language):
        raise ValueError('If using a model ending in .en, you cannot specify a language other than English.')

    return args


if __name__ == "__main__":
    args = parse_args()

    # Określ urządzenie dla modelu
    device = "cpu"
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        device = "mps"
        print(f"Próbuję użyć Metal Performance Shaders (GPU) na M1: {device}")
    else:
        print(f"Używam CPU: {device}")

    print("Loading model...")
    model_name = args.model_name
    
    try:
        model = load_model(model_name, device=device)
        print(f"{model_name} model loaded on {device}")
    except Exception as e:
        if device == "mps":
            print(f"Błąd z MPS: {str(e)[:100]}...")
            print("Przełączam na CPU jako fallback")
            device = "cpu"
            model = load_model(model_name, device=device)
            print(f"{model_name} model loaded on {device}")
        else:
            raise e
    
    # Parse allowed languages if specified
    allowed_languages = None
    if args.allowed_languages:
        allowed_languages = [lang.strip() for lang in args.allowed_languages.split(',')]
        print(f"Language detection constrained to: {allowed_languages}")
    
    transcriber = SpeechTranscriber(model, allowed_languages)
    recorder = Recorder(transcriber)
    
    app = StatusBarApp(recorder, args.language, args.max_time)
    if args.k_double_cmd:
        key_listener = DoubleCommandKeyListener(app)
    else:
        key_listener = GlobalKeyListener(app, args.key_combination)
    listener = keyboard.Listener(on_press=key_listener.on_key_press, on_release=key_listener.on_key_release)
    listener.start()

    print("Running... ")
    app.run()

