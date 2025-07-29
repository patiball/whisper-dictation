#!/bin/bash

# Ustawy ścieżki PATH dla launchd (nie ma dostępu do user PATH)
export PATH="/Users/mprzybyszewski/.local/bin:/Users/mprzybyszewski/.pyenv/shims:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Debug info
echo "START_WHISPER.SH: Starting whisper-dictation-fast.py at $(date)" 
echo "START_WHISPER.SH: Current directory: $(pwd)"
echo "START_WHISPER.SH: PATH: $PATH"
echo "START_WHISPER.SH: Python version: $(python3 --version)"
echo "START_WHISPER.SH: Poetry location: $(which poetry)"

# Przejdź do katalogu z aplikacją
cd /Users/mprzybyszewski/whisper-dictation
echo "START_WHISPER.SH: Changed to directory: $(pwd)"

# Sprawdź czy plik istnieje
if [ -f "whisper-dictation-fast.py" ]; then
    echo "START_WHISPER.SH: Found whisper-dictation-fast.py"
else
    echo "START_WHISPER.SH: ERROR - whisper-dictation-fast.py not found!"
    exit 1
fi

# Uruchom zoptymalizowaną wersję whisper-dictation (whisper.cpp) z modelem medium
# Inteligentne wykrywanie języka: cache + co 3. wywołanie pełna detekcja
# Poprawki dla utraty pierwszych sekund nagrania + Metal GPU na M1
echo "START_WHISPER.SH: Launching whisper-dictation-optimized.py..."
/Users/mprzybyszewski/.local/bin/poetry run python whisper-dictation-optimized.py \
    --k_double_cmd \
    --model_name medium \
    --allowed_languages "en,pl"
