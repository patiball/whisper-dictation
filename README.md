# Multilingual Dictation App based on OpenAI Whisper
Multilingual dictation app based on the powerful OpenAI Whisper ASR model(s) to provide accurate and efficient speech-to-text conversion in any application. The app runs in the background and is triggered through a keyboard shortcut. It is also entirely offline, so no data will be shared. It allows users to set up their own keyboard combinations and choose from different Whisper models, and languages.

## Prerequisites
The PortAudio and llvm library is required for this app to work. You can install it on macOS using the following command:

```bash
brew install portaudio llvm
```

## Permissions
The app requires accessibility permissions to register global hotkeys and permission to access your microphone for speech recognition.

## Installation
Clone the repository:

```bash
git clone https://github.com/foges/whisper-dictation.git
cd whisper-dictation
```

If you use poetry:

```shell
poetry install
poetry shell
```

Or, if you don't use poetry, first create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### 🔄 **Two Whisper Implementations Available**

This project includes **two different Whisper implementations** with different trade-offs:

#### 1. **Python Version (Production-Ready, CPU Only)**
```bash
# High accuracy, stable, CPU only (M1 GPU not supported due to PyTorch MPS incompatibility)
poetry run python whisper-dictation.py --k_double_cmd

# With specific model
poetry run python whisper-dictation.py -m large --k_double_cmd -l en
```

#### 2. **C++ Version (Production-Ready, M1/M2 GPU Accelerated)** ✅
```bash
# M1/M2 GPU acceleration via Metal, all quality issues resolved (Oct 2025)
poetry run python whisper-dictation-fast.py --k_double_cmd

# With model selection (tiny/base/small/medium/large)
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd  # Recommended
poetry run python whisper-dictation-fast.py -m small --k_double_cmd   # Balanced
poetry run python whisper-dictation-fast.py -m base --k_double_cmd    # Default
poetry run python whisper-dictation-fast.py -m tiny --k_double_cmd    # Fastest

# With language specification
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd -l pl
poetry run python whisper-dictation-fast.py -m medium --k_double_cmd --allowed_languages en,pl
```

**📊 Model Comparison (C++ Version):**
| Model | Size | Quality | Speed |
|-------|------|---------|-------|
| tiny | 74MB | Basic | Fastest |
| base | 141MB | Good | Fast |
| small | 470MB | Very Good | Medium |
| medium | 1.4GB | Excellent | Slower |
| large | 3GB | Best | Slowest |

**✅ Recent Fixes (Oct 2025):**
- Audio pipeline optimized (start sound delayed 0.1s)
- Language detection fixed (proper Polish → Polish transcription)
- Translation mode verified (defaults to transcription, not translation)

### **Prerequisites for C++ Version**
```bash
# Install whisper.cpp (if not already installed)
brew install whisper-cpp
```

**Note:** Models are automatically downloaded to `~/.whisper-models/` on first use.

### **Standard Usage (Python Version)**
```bash
poetry run python whisper-dictation.py -m large -k cmd_r+shift -l en
```

The models are multilingual, and you can specify a two-letter language code (e.g., "no" for Norwegian) with the `-l` or `--language` option. Specifying the language can improve recognition accuracy, especially for smaller model sizes.

#### Replace macOS default dictation trigger key
You can use this app to replace macOS built-in dictation. Trigger to begin recording with a double click of Right Command key and stop recording with a single click of Right Command key.
```bash
python whisper-dictation.py -m large --k_double_cmd -l en
```
To use this trigger, go to System Settings -> Keyboard, disable Dictation. If you double click Right Command key on any text field, macOS will ask whether you want to enable Dictation, so select Don't Ask Again.

## Setting the App as a Startup Item
To have the app run automatically when your computer starts, follow these steps:

 1. Open System Preferences.
 2. Go to Users & Groups.
 3. Click on your username, then select the Login Items tab.
 4. Click the + button and add the `run.sh` script from the whisper-dictation folder.

## Test Files

The repository contains test audio files for debugging and performance testing:

- `test_polish_*.wav` - Polish language test recordings
- `test_english_*.wav` - English language test recordings (if available)

### Test Results

**Latest Performance Test (Polish):**
- File: `test_polish_20250630_083944.wav`
- Content: "1, 2, 3, 4, 5. To jest test aplikacji Whisper z językiem polskim."
- Language Detection: 2.13s (Polish detected correctly)
- Transcription: 2.95s
- Total Processing: 5.08s
- **Note**: This test was with Python version (CPU only)

**M1 GPU Support Status:**
- **Python Version**: ❌ MPS backend incompatible with OpenAI Whisper (SparseMPS errors)
- **C++ Version**: ✅ Native M1 GPU support via whisper.cpp, but with quality issues
- **Current Recommendation**: Use Python version for accuracy, C++ version experimental

**Implementation Comparison:**
| Feature | Python Version | C++ Version |
|---------|---------------|-------------|
| M1 GPU Support | ❌ CPU only | ✅ Native GPU |
| Transcription Quality | ✅ High | ⚠️ Issues detected |
| Audio Processing | ✅ Complete | ❌ Cutting issues |
| Language Support | ✅ Multilingual | ❌ Forces English |
| Stability | ✅ Production ready | ⚠️ Experimental |

### Running Tests

```bash
# Advanced recording and performance test
poetry run python test_recording_advanced.py

# Basic language detection test
poetry run python test_language_detection.py
```
