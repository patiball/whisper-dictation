# Epic: Ulepszenie rozpoznawania mowy wielojęzycznej
**Status**: Ready
**Priority**: High
**Complexity**: Complex

## Overview
Obecna implementacja transkrypcji ma problemy z poprawnym rozpoznawaniem mowy, gdy w jednym nagraniu używanych jest wiele języków (np. polski i angielski). Model Whisper, przy obecnej konfiguracji, wykrywa jeden dominujący język dla całego nagrania, co prowadzi do błędnej transkrypcji fragmentów w innych językach. Celem tego epiku jest zaimplementowanie solidnego mechanizmu, który pozwoli na dokładne rozpoznawanie mowy wielojęzycznej.

## Acceptance Criteria
- [ ] Aplikacja musi poprawnie transkrybować nagrania zawierające mieszankę języka polskiego i angielskiego.
- [ ] Transkrypcja musi być kompletna i nie może ucinać początku ani końca nagrania.
- [ ] Wydajność aplikacji nie może ulec znaczącemu pogorszeniu.
- [ ] Istniejące funkcjonalności, takie jak skróty klawiszowe i odtwarzanie dźwięków, muszą działać bez zmian.

## Detailed Implementation Plan
1.  **Setup and Dependencies:**
    - [ ] Add `webrtcvad-wheels` to the project's dependencies in `pyproject.toml`.

2.  **Implement VAD-based Audio Segmentation:**
    - [ ] In `transcriber.py`, create a new method to segment the input audio (`np.ndarray`) into smaller chunks based on voice activity using `webrtcvad`.
    - [ ] This method should yield audio frames that contain continuous speech.

3.  **Per-Segment Transcription:**
    - [ ] Create a new private method, e.g., `_transcribe_segment`, that takes a single audio segment.
    - [ ] Inside this method:
        - [ ] Use `whisper.load_audio` and `whisper.log_mel_spectrogram` to prepare the audio for language detection.
        - [ ] Call `self.model.detect_language()` to identify the language of the segment.
        - [ ] Call `self.model.transcribe()` on the segment, passing the explicitly detected language to ensure high accuracy.
        - [ ] Return the transcribed text and the detected language.

4.  **Refactor Main Transcribe Methods:**
    - [ ] Modify the existing `transcribe` and `transcribe_audio_data` methods.
    - [ ] These methods will first use the new VAD segmentation logic to split the audio.
    - [ ] They will then iterate through the segments, call `_transcribe_segment` for each one, and aggregate the results.
    - [ ] The final output will be a single string containing the combined transcriptions from all segments.
    - [ ] The overall detected language for the `TranscriptionResult` can be the most frequent language found across the segments.

5.  **Testing:**
    - [ ] Create new tests in the `tests/` directory specifically for multilingual audio to verify the accuracy of the new implementation.

## File Changes Required
- **`transcriber.py`**: Główne zmiany w logice transkrypcji, implementacja segmentacji i VAD.
- **`pyproject.toml`**: Dodanie zależności `webrtcvad-wheels`.
- **`tests/`**: Stworzenie nowych testów jednostkowych i integracyjnych dla mowy wielojęzycznej.

## Integration Points
Nowy mechanizm transkrypcji będzie kluczowym elementem aplikacji, dlatego jego integracja musi być dokładnie przetestowana. Zmiany wpłyną na sposób, w jaki dane audio są przekazywane do modelu Whisper i jak przetwarzane są wyniki.
