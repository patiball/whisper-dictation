
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


def run_whisper_cli(binary: str, model: str, audio_file: str, *args, timeout: int = None, output_dir: Path = None, capture_stdout_for_parsing: bool = False) -> subprocess.CompletedProcess:


    """


    Uruchamia whisper-cli z podanymi argumentami.


    Jeśli `capture_stdout_for_parsing` jest True, wyjście jest przechwytywane z stdout.


    W przeciwnym razie, jeśli `output_dir` jest podane, wyjście jest kierowane do pliku.


    """


    cmd = [binary, "-m", model, "-f", audio_file]


    


    if output_dir and not capture_stdout_for_parsing:


        # Ensure output is directed to the temporary directory via -of


        cmd.extend(["-of", str(output_dir / Path(audio_file).stem)])


        cmd.extend(args)


    else:


        # Rely on stdout capture for parsing, or no specific output file if output_dir is None


        cmd.extend(args)





    try:


        return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout)


    except subprocess.TimeoutExpired as e:


        return e

def test_timeout_handling(whisper_cli_binary, whisper_model_path, english_audio_file, tmp_path: Path):
    """
    Test: Sprawdza, czy obsługa timeoutu działa poprawnie.
    """
    # Test z krótkim timeoutem - powinien zakończyć się błędem TimeoutExpired
    short_timeout = 0.01 # sekunda
    result_timeout = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, output_dir=tmp_path, timeout=short_timeout)

    assert isinstance(result_timeout, subprocess.TimeoutExpired), \
        f"Expected TimeoutExpired, but got {type(result_timeout).__name__} with return code {result_timeout.returncode if hasattr(result_timeout, 'returncode') else 'N/A'}"

    # Test z wystarczającym timeoutem - powinien zakończyć się sukcesem
    long_timeout = 30 # sekundy (dla pliku ~10s, 30s powinno wystarczyć)
    result_success = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "-otxt", output_dir=tmp_path, timeout=long_timeout)

    assert not isinstance(result_success, subprocess.TimeoutExpired), \
        f"Did not expect TimeoutExpired, but got it. Stderr: {result_success.stderr if hasattr(result_success, 'stderr') else 'N/A'}"
    assert result_success.returncode == 0, f"whisper-cli failed with exit code {result_success.returncode}\nStderr: {result_success.stderr}"
    
    # Verify output file was created
    output_file = tmp_path / (Path(english_audio_file).stem + ".txt")
    assert output_file.exists(), f"Output file {output_file} was not created."
    assert output_file.read_text().strip() != "", "Output file should not be empty."

def test_stderr_error_logging(whisper_cli_binary, whisper_model_path, tmp_path: Path):
    """
    Test: Sprawdza, czy błędy na stderr są poprawnie przechwytywane.
    """
    invalid_model_path = "/non/existent/model.bin"

    # Uruchomienie whisper-cli z nieprawidłową ścieżką do modelu
    # Używamy dummy audio file i output_dir, aby zachować spójność wywołania run_whisper_cli
    result = run_whisper_cli(whisper_cli_binary, invalid_model_path, "/dev/null", output_dir=tmp_path)

    # Oczekujemy, że proces zakończy się błędem (non-zero return code)
    assert result.returncode != 0, f"Expected non-zero return code for invalid model path, but got {result.returncode}"

    # Oczekujemy, że stderr będzie zawierał komunikat o błędzie
    assert "failed to open file" in result.stderr.lower() or \
           "no such file or directory" in result.stderr.lower() or \
           "error" in result.stderr.lower(), \
           f"Expected error message in stderr, but got: {result.stderr}"


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

def test_transcription_not_translation_on_polish_audio(whisper_cli_binary, whisper_model_path, polish_audio_file, tmp_path: Path):
    """
    Test regresji: Sprawdza, czy polskie audio jest transkrybowane na polski.
    Ten test powinien zawieść, ponieważ obecna implementacja domyślnie tłumaczy.
    """
    # Uruchomienie whisper-cli bez flagi --task, aby odtworzyć błąd
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, polish_audio_file, "-l", "pl", "-otxt", output_dir=tmp_path)

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"
    
    # Read the output from the temporary file
    output_file = tmp_path / (Path(polish_audio_file).stem + ".txt")
    assert output_file.exists(), f"Output file {output_file} was not created."
    transcribed_text = output_file.read_text().strip()
    
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

def test_audio_cutting_regression(whisper_cli_binary, whisper_model_path, english_audio_file, tmp_path: Path):
    """
    Test regresji: Sprawdza, czy transkrypcja audio nie jest ucinana na początku/końcu.
    Ten test powinien zawieść, ponieważ obecna implementacja ma problem z ucinaniem audio.
    """
    expected_start_anchor = "This is a longer English"
    expected_end_anchor = "Numbers 1, 2, 3, 4, 5, 6, 7, 8, 9, 10."

    # Uruchomienie whisper-cli z angielskim audio
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "-l", "en", "-otxt", output_dir=tmp_path)

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    # Read the output from the temporary file
    output_file = tmp_path / (Path(english_audio_file).stem + ".txt")
    assert output_file.exists(), f"Output file {output_file} was not created."
    transcribed_text = output_file.read_text().strip()
    print(f"Transcribed text for audio cutting test: {transcribed_text}")

    # Sprawdzenie obecności kotwic na początku i końcu
    # Używamy prostego sprawdzenia 'in' dla fazy czerwonej, aby upewnić się, że tekst jest w ogóle obecny.
    # Bardziej zaawansowane sprawdzanie (np. fuzzy matching, pozycja) można dodać w fazie zielonej.
    assert expected_start_anchor in transcribed_text, f"Start anchor '{expected_start_anchor}' not found in transcription."
    assert expected_end_anchor in transcribed_text, f"End anchor '{expected_end_anchor}' not found in transcription."

def test_language_auto_detection(whisper_cli_binary, whisper_model_path, english_audio_file, tmp_path: Path):
    """
    Test regresji: Sprawdza, czy automatyczna detekcja języka działa poprawnie.
    Ten test powinien zawieść, jeśli whisper-cli wymusza język zamiast auto-detekcji.
    """
    expected_language = "en"

    # Uruchomienie whisper-cli z flagą --detect-language
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "--detect-language", output_dir=tmp_path, capture_stdout_for_parsing=True)

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    detected_language = result.stdout.strip()
    print(f"Detected language: {detected_language}")

    assert detected_language == expected_language, f"Expected language '{expected_language}', but detected '{detected_language}'"

def test_language_detection_with_confidence(whisper_cli_binary, whisper_model_path, english_audio_file, tmp_path: Path):
    """
    Test: Sprawdza, czy detekcja języka z confidence działa poprawnie.
    """
    expected_language = "en"
    min_confidence = 0.90 # Zgodnie ze specyfikacją

    # Uruchomienie whisper-cli z flagami --detect-language i --print-confidence
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, english_audio_file, "--detect-language", "--print-confidence", output_dir=tmp_path, capture_stdout_for_parsing=True)

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

def test_language_detection_polish_with_confidence(whisper_cli_binary, whisper_model_path, polish_audio_file, tmp_path: Path):
    """
    Test: Sprawdza, czy detekcja języka polskiego z confidence działa poprawnie.
    """
    expected_language = "pl"
    min_confidence = 0.90 # Zgodnie ze specyfikacją

    # Uruchomienie whisper-cli z flagami --detect-language i --print-confidence
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, polish_audio_file, "--detect-language", "--print-confidence", output_dir=tmp_path, capture_stdout_for_parsing=True)

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    output_lines = result.stdout.strip().split('\n')
    
    if len(output_lines) < 2:
        pytest.fail(f"Unexpected output format for language detection with confidence: {result.stdout}")

    detected_language = output_lines[-1].strip()
    try:
        detected_confidence = float(output_lines[-2].strip())
    except ValueError:
        pytest.fail(f"Could not parse confidence from output: {output_lines[-2]}")

            print(f"Detected Polish language: {detected_language}, Confidence: {detected_confidence}")
        
            assert detected_language == expected_language, f"Expected language '{expected_language}', but detected '{detected_language}'"
            assert detected_confidence >= min_confidence, f"Expected confidence >= {min_confidence}, but got {detected_confidence}"        
        def test_whisper_cli_internal_timeout(whisper_cli_binary, whisper_model_path, english_audio_file, tmp_path: Path):    """
    Test: Sprawdza, czy wewnętrzny mechanizm timeoutu whisper-cli działa poprawnie
    kontrolowany przez WHISPER_CLI_TIMEOUT_SEC.
    """
    # Ustawienie bardzo krótkiego timeoutu wewnętrznego dla whisper-cli
    env = os.environ.copy()
    env["WHISPER_CLI_TIMEOUT_SEC"] = "1" # 1 sekunda

    # Uruchomienie whisper-cli z długim plikiem audio, oczekując timeoutu
    # Używamy subprocess.run bezpośrednio, aby przekazać zmienne środowiskowe
    cmd = [whisper_cli_binary, "-m", whisper_model_path, "-f", english_audio_file, "-l", "en", "-otxt", "-of", str(tmp_path / Path(english_audio_file).stem)]
    
    # Oczekujemy, że whisper-cli zakończy się błędem z powodu timeoutu
    # Nie używamy timeoutu subprocess.run, aby przetestować wewnętrzny timeout whisper-cli
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)

    assert result.returncode != 0, f"Expected non-zero return code for timeout, but got {result.returncode}"
    assert "timeout" in result.stderr.lower() or \
           "aborted" in result.stderr.lower() or \
           "error" in result.stderr.lower(), \
           f"Expected timeout/error message in stderr, but got: {result.stderr}"

    # Sprawdzenie, czy plik wyjściowy nie został utworzony lub jest pusty
    output_file = tmp_path / (Path(english_audio_file).stem + ".txt")
    assert not output_file.exists() or output_file.read_text().strip() == "", \
        f"Output file {output_file} should not exist or be empty after timeout."


def test_language_auto_detection_polish(whisper_cli_binary, whisper_model_path, polish_audio_file, tmp_path: Path):
    """
    Test regresji: Sprawdza, czy automatyczna detekcja języka polskiego działa poprawnie.
    Ten test powinien zawieść, jeśli whisper-cli wymusza język zamiast auto-detekcji.
    """
    expected_language = "pl"

    # Uruchomienie whisper-cli z flagą --detect-language
    result = run_whisper_cli(whisper_cli_binary, whisper_model_path, polish_audio_file, "--detect-language", output_dir=tmp_path, capture_stdout_for_parsing=True)

    assert result.returncode == 0, f"whisper-cli failed with exit code {result.returncode}\nStderr: {result.stderr}"

    detected_language = result.stdout.strip()
    print(f"Detected Polish language: {detected_language}")

    assert detected_language == expected_language, f"Expected language '{expected_language}', but detected '{detected_language}'"

