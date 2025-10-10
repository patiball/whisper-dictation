# Task: Create System-Level Integration Diagram

## Objective
Create a comprehensive system integration diagram showing all components working together.

## Files to Create/Modify

### 1. Create New File
**Path**: `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/SYSTEM_INTEGRATION.md`

**Content Structure**:
```markdown
# System Integration Diagram

This diagram shows how all components of Whisper Dictation work together.

## Complete System Overview

```mermaid
graph TB
    subgraph "User Layer"
        U[User]
        KB[Keyboard - Hotkey]
    end
    
    subgraph "Application Core"
        M[Main Application<br/>whisper-dictation.py]
    end
    
    subgraph "Audio Layer"
        DM[DeviceManager<br/>device_manager.py]
        REC[Recorder<br/>recorder.py]
        PA[PyAudio<br/>Audio Stream]
    end
    
    subgraph "AI/ML Layer"
        TR[Transcriber<br/>transcriber.py]
        WM[Whisper Model<br/>openai-whisper]
        GPU[GPU/MPS/CPU<br/>Optimization]
    end
    
    subgraph "Output Layer"
        TI[Text Inserter<br/>pykeyboard]
        AW[Active Window]
    end
    
    subgraph "System Resources"
        MIC[Microphone Hardware]
        SYS[Operating System]
    end
    
    %% User interactions
    U -->|Press/Release hotkey| KB
    KB -->|Hotkey event| M
    
    %% Main app orchestration
    M -->|Initialize| DM
    M -->|Create| REC
    M -->|Create| TR
    M -->|Control recording| REC
    M -->|Request transcription| TR
    M -->|Insert text| TI
    
    %% Audio flow
    DM -->|Select device| MIC
    DM -->|Query devices| PA
    MIC -->|Audio stream| PA
    PA -->|16kHz 16-bit PCM| REC
    REC -->|Audio buffer| TR
    
    %% Transcription flow
    TR -->|Load model| WM
    TR -->|Optimize for| GPU
    WM -->|Use device| GPU
    WM -->|Return text| TR
    TR -->|Transcribed text| M
    
    %% Output flow
    M -->|Text to insert| TI
    TI -->|Simulate typing| SYS
    SYS -->|Insert text| AW
    AW -->|Display| U
    
    %% Styling
    classDef userClass fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef coreClass fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    classDef audioClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef aiClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef outputClass fill:#ffe0b2,stroke:#e64a19,stroke-width:2px
    classDef systemClass fill:#eceff1,stroke:#546e7a,stroke-width:2px
    
    class U,KB userClass
    class M coreClass
    class DM,REC,PA audioClass
    class TR,WM,GPU aiClass
    class TI,AW outputClass
    class MIC,SYS systemClass
```

## Data Flow Explanation

### 1. Initialization Phase
1. Main app starts
2. DeviceManager queries available audio devices
3. Recorder and Transcriber are initialized
4. Whisper model is loaded with optimal device (MPS/CUDA/CPU)

### 2. Recording Phase (Hotkey Pressed)
1. User presses hotkey
2. Main app signals Recorder to start
3. Recorder opens audio stream via PyAudio
4. Audio data flows: Microphone → PyAudio → Recorder buffer

### 3. Processing Phase (Hotkey Released)
1. User releases hotkey
2. Recorder stops and returns audio buffer
3. Main app passes audio to Transcriber
4. Transcriber processes with Whisper model
5. Model returns transcribed text

### 4. Output Phase
1. Main app receives text from Transcriber
2. Text Inserter simulates keyboard typing
3. Text appears in active application window
4. User sees result

## Component Dependencies

```mermaid
graph LR
    M[Main] --> DM[DeviceManager]
    M --> REC[Recorder]
    M --> TR[Transcriber]
    REC --> PA[PyAudio]
    TR --> WH[Whisper]
    TR --> DM
    
    style M fill:#fff9c4
    style DM fill:#f3e5f5
    style REC fill:#f3e5f5
    style TR fill:#e8f5e9
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Operation] --> B{Success?}
    B -->|Yes| C[Continue]
    B -->|No| D[DeviceManager handles error]
    D --> E{Fallback available?}
    E -->|Yes| F[Switch device]
    F --> A
    E -->|No| G[Log error & notify user]
```

## See Also
- [Architecture Details](ARCHITECTURE.md)
- [Data Flow Documentation](DATA_FLOW.md)
- [Module Documentation](modules/)
```

### 2. Update README.md
**Path**: `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/README.md`

**Action**: Add link to SYSTEM_INTEGRATION.md in appropriate section (e.g., in "Documentation" section or near the top).

Add this line:
```markdown
- **[System Integration Diagram](SYSTEM_INTEGRATION.md)** - Complete overview of all components working together
```

## Requirements

1. Create comprehensive Mermaid diagram showing:
   - All major components
   - Data flow between components
   - User interactions
   - External dependencies (PyAudio, Whisper, OS)
   - Clear visual grouping (subgraphs)
   - Color coding for different layers

2. Include explanatory text:
   - Phase-by-phase explanation
   - Component dependencies
   - Error handling overview

3. Keep it high-level but complete:
   - Show the big picture
   - Don't dive into implementation details
   - Make it understandable for newcomers

4. Add cross-references to detailed docs

## Verification

After creation:
```bash
# Verify file created
ls -lh /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/SYSTEM_INTEGRATION.md

# Check diagram syntax
grep -c 'mermaid' /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/SYSTEM_INTEGRATION.md

# Verify README link added
grep -n 'SYSTEM_INTEGRATION' /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/README.md
```

## Success Criteria
- [ ] SYSTEM_INTEGRATION.md file created
- [ ] Main integration diagram shows all components
- [ ] Dependencies diagram included
- [ ] Error handling flow shown
- [ ] Explanatory text provided
- [ ] README.md updated with link
- [ ] Diagrams use proper Mermaid syntax
- [ ] Visual grouping with subgraphs
- [ ] Color coding applied
