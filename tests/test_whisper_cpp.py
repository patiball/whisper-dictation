
# UWAGA: Te testy są przeznaczone do weryfikacji działania `whisper-cli` w izolacji.
# Przechodzące testy nie oznaczają, że błędy end-to-end (np. ucinanie audio, tryb tłumaczenia) nie występują w całym systemie.
# Mogą one wynikać z interakcji z innymi komponentami lub specyficznych warunków środowiskowych.

import pytest
import subprocess
import os
import shutil
from pathlib import Path

# Sprawdzenie, czy `whisper-cli` jest dostępne w systemie
WHISPER_CLI_PATH = shutil.which("whisper-cli") or os.environ.get("WHISPER_CLI_BIN")

# Warunek do pomijania testów, jeśli `whisper-cli` nie jest znalezione lub jeśli jest ustawiona zmienna środowiskowa
skip_if_no_whisper_cpp = pytest.mark.skipif(
    not WHISPER_CLI_PATH,
    reason="whisper-cli not found in PATH or WHISPER_CLI_BIN env var"
)

skip_if_env_var_set = pytest.mark.skipif(
    os.environ.get("WHISPER_CPP_SKIP", "false").lower() == "true",
    reason="WHISPER_CPP_SKIP environment variable is set to true"
)

# Zastosowanie markerów na poziomie modułu
pytestmark = [skip_if_no_whisper_cpp, skip_if_env_var_set, pytest.mark.whisper_cpp]


@pytest.fixture(scope="module")
def whisper_cli_binary() -> str:
    """Zwraca ścieżkę do binarki whisper-cli."""
    return WHISPER_CLI_PATH


@pytest.fixture(scope="module")
def whisper_model_path() -> str:
    """Zwraca ścieżkę do modelu Whisper, pomijając test, jeśli nie jest dostępna."""
    model_path = os.environ.get("WHISPER_CLI_MODEL")
    print(f"[DEBUG] WHISPER_CLI_MODEL: {model_path}")
    if model_path:
        print(f"[DEBUG] Path({model_path}).exists(): {Path(model_path).exists()}")
    if not model_path or not Path(model_path).exists():
        pytest.skip(f"Model not found at path specified by WHISPER_CLI_MODEL: {model_path}")
    return model_path


def run_whisper_cli(binary: str, model: str, audio_file: str, *args) -> subprocess.CompletedProcess:
    """Uruchamia whisper-cli z podanymi argumentami."""
    cmd = [binary, "-m", model, "-f", audio_file, *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


@pytest.fixture
def polish_audio_file() -> str:
    """Zwraca ścieżkę do polskiego pliku audio, pomijając test, jeśli go nie ma."""
    # Wybieramy dynamicznie najnowszy polski plik testowy
    audio_dir = Path(__file__).parent / "audio"
    polish_files = list(audio_dir.glob("test_polish*.wav"))
    if not polish_files:
        pytest.skip("No Polish audio files found in tests/audio/")
    
    # Zwraca najnowszy plik na podstawie daty modyfikacji
    latest_file = max(polish_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def is_polish(text: str) -> bool:
    """Prosta heurystyka do sprawdzania, czy tekst jest w języku polskim."""
    polish_chars = "ąćęłńóśźż"
    return any(char in text.lower() for char in polish_chars)

def test_transcription_not_translation_on_polish_audio(whisper_cli_binary, whisper_model_path, polish_audio_file):
    """
    Test regresji: Sprawdza, czy polskie audio jest transkrybowane na polski.
    Ten test powinien zawieść, ponieważ obecna implementacja domyślnie tłumaczy.
    """
    # Uruchomienie whisper-cli bez flagi --task, aby odtworzyć błąd
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, polish_audio_file, "-l", "pl", "-otxt")

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"
    
    transcribed_text = result.stdout.strip()
    
    print(f"Transcribed text: {transcribed_text}")
    
    # Asercja, która powinna zawieść
    assert is_polish(transcribed_text), f"Text seems to be translated to English, not transcribed in Polish.\nOutput: '{transcribed_text}'"

@pytest.fixture
def english_audio_file() -> str:
    """Zwraca ścieżkę do angielskiego pliku audio, pomijając test, jeśli go nie ma."""
    audio_dir = Path(__file__).parent / "audio"
    english_files = list(audio_dir.glob("test_english*.wav"))
    if not english_files:
        pytest.skip("No English audio files found in tests/audio/")
    latest_file = max(english_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def test_audio_cutting_regression(whisper_cli_binary, whisper_model_path, english_audio_file):
    """
    Test regresji: Sprawdza, czy transkrypcja audio nie jest ucinana na początku/końcu.
    Ten test powinien zawieść, ponieważ obecna implementacja ma problem z ucinaniem audio.
    """
    expected_start_anchor = "This is a longer English"
    expected_end_anchor = "Numbers 1, 2, 3, 4, 5, 6, 7, 8, 9, 10."

    # Uruchomienie whisper-cli z angielskim audio
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "-l", "en", "-otxt")

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    transcribed_text = result.stdout.strip()
    print(f"Transcribed text for audio cutting test: {transcribed_text}")

    # Sprawdzenie obecności kotwic na początku i końcu
    # Używamy prostego sprawdzenia 'in' dla fazy czerwonej, aby upewnić się, że tekst jest w ogóle obecny.
    # Bardziej zaawansowane sprawdzanie (np. fuzzy matching, pozycja) można dodać w fazie zielonej.
    assert expected_start_anchor in transcribed_text, f"Start anchor '{expected_start_anchor}' not found in transcription."
    assert expected_end_anchor in transcribed_text, f"End anchor '{expected_end_anchor}' not found in transcription."

def test_language_auto_detection(whisper_cli_binary, whisper_model_path, english_audio_file):
    """
    Test regresji: Sprawdza, czy automatyczna detekcja języka działa poprawnie.
    Ten test powinien zawieść, jeśli whisper-cli wymusza język zamiast auto-detekcji.
    """
    expected_language = "en"

    # Uruchomienie whisper-cli z flagą --detect-language
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "--detect-language")

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    detected_language = result.stdout.strip()
    print(f"Detected language: {detected_language}")

    assert detected_language == expected_language, f"Expected language '{expected_language}', but detected '{detected_language}'"

def test_language_detection_with_confidence(whisper_cli_binary, whisper_model_path, english_audio_file):
    """
    Test: Sprawdza, czy detekcja języka z confidence działa poprawnie.
    """
    expected_language = "en"
    min_confidence = 0.90 # Zgodnie ze specyfikacją

    # Uruchomienie whisper-cli z flagami --detect-language i --print-confidence
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "--detect-language", "--print-confidence")

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    output_lines = result.stdout.strip().split('\n')
    
    # Oczekujemy, że ostatnia linia to język, a przedostatnia to confidence
    # To jest heurystyka, może wymagać dostosowania w zależności od dokładnego formatu wyjścia
    if len(output_lines) < 2:
        pytest.fail(f"Unexpected output format for language detection with confidence: {result.stdout}")

    detected_language = output_lines[-1].strip()
    try:
        detected_confidence = float(output_lines[-2].strip())
    except ValueError:
        pytest.fail(f"Could not parse confidence from output: {output_lines[-2]}")

    print(f"Detected language: {detected_language}, Confidence: {detected_confidence}")

    assert detected_language == expected_language, f"Expected language '{expected_language}', but detected '{detected_language}'"
    assert detected_confidence >= min_confidence, f"Expected confidence >= {min_confidence}, but got {detected_confidence}"

