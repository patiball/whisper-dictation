# Issues & Backlog - Whisper Dictation C++ Version

**Last Updated**: 2025-11-04  
**Status**: Active Issues Identified

---

## 🔴 CRITICAL ISSUES

### Issue 1: Audio Clipping at Start (Intermittent)
**Status**: In Progress — Quick Fix (Python) deployed; measurement ongoing  
**Priority**: High  
**Description**: First 50-200ms of audio is sometimes lost, causing beginning of speech to be cut off  
**Evidence**: Occurs intermittently - not 100% reproducible  
**Root Cause**: Diagnostic spec created - see `memory-bank/specs/task-audio-clipping-diagnosis.md`  
**Related Files**:
- `whisper-dictation-fast.py` (lines 134-162, `Recorder._record_impl()`) — C++ path (pending)
- `whisper-dictation.py` (Recorder `_record_impl`) — Python path (quick fix deployed)
- `specs/[08-00-00]_audio_clipping_warmup_fix.md` — spec for warm-up + buffer sizing
- `scripts/tmp_rovodev_measure_start_silence.py` — diagnostic script to measure start_silence_ms  
**Diagnosis Status**:
- [x] Phase 1: Initial instrumentation strategy defined (spec) — minimal debug timestamps in Python path
- [x] Phase 2: Audio content analysis via start_silence_ms script (PoC added)
- [ ] Phase 3: Component isolation tests (Python vs C++ paths) — pending
- [ ] Phase 4: Root cause confirmation — pending (collect metrics over 30 runs)

---

### Issue 2: First Two Words Joined (Text Processing)
**Status**: NEW - Needs Investigation  
**Priority**: High  
**Description**: First two words are concatenated without space  
- **Example**: "Długi tekst" appears as "Długitekst"
- **Affects**: Every recording - consistent behavior
- **Symptom**: Missing space between word 1 and word 2 only
- **Scope**: Only impacts first two words, rest of text is fine

**Possible Root Causes**:
1. Transcription model issue (whisper.cpp returning text without space?)
2. Text processing in `SpeechTranscriber.transcribe()` (lines 22-94)
3. Keyboard input simulation issue in `pykeyboard.type()` (lines 70-81)
4. WAV file encoding issue (first frames contain partial data)

**Investigation Needed**:
- [ ] Capture raw transcription output from whisper-cli before keyboard input
- [ ] Check if space character is being skipped (lines 71-75 show special handling)
- [ ] Compare against Python version behavior
- [ ] Test with different languages (PL, EN, etc.)

**Files to Check**:
- `whisper-dictation-fast.py:22-94` - Transcription logic
- `whisper-dictation-fast.py:70-81` - Keyboard typing logic (special space handling?)

---

### Issue 3: Silent Stop - No User Feedback on Max Recording Time
**Status**: NEW - UX/Safety Issue  
**Priority**: High  
**Description**: When recording reaches max time limit, recording silently stops WITHOUT notifying user
- **Behavior**: User continues speaking, but audio is no longer being captured
- **User Experience**: User has no way to know recording stopped
- **Current Max Time**: 30 seconds (hardcoded default in line 297)

**Impact**:
- User dictates what they think is being recorded, but it's not
- Wasted time and frustration
- No error recovery

**Possible Solutions**:
1. Add visual/audio feedback when max time is reached
   - Play system sound (like Pop.aiff)
   - Update status bar icon to indicate max time reached
2. Increase default max time or make it configurable per session
3. Show countdown timer as recording approaches limit

**Related Code**:
- `whisper-dictation-fast.py:224-226` - Timer creation and max_time handling
- `whisper-dictation-fast.py:247-252` - Timer display (shows elapsed time in title)
- `whisper-dictation-fast.py:297-298` - Max time default is 30 seconds

**Files to Modify**:
- `whisper-dictation-fast.py` - Add max-time-reached feedback
- `StatusBarApp.stop_app()` - Add notification logic

---

## 🟡 SECONDARY ISSUES

### Issue 4: Delay Between Transcription Completion and Text Insertion
**Status**: NEW - UX/Performance Issue
**Priority**: Medium
**Description**: Noticeable delay between when transcription completes (CLI output shows "Done") and when text actually appears in the editor
- **User Experience**: User sees transcription finished in terminal, but has to wait additional time before text is pasted
- **Impact**: Creates confusion about whether transcription actually succeeded
- **Possible causes**:
  1. Keyboard simulation delay (pykeyboard typing speed)
  2. Processing overhead between whisper-cli completion and keyboard input start
  3. OS-level clipboard or input method latency
  4. Delay in status bar app state transitions

**Investigation Needed**:
- [ ] Measure time between whisper-cli process exit and first keyboard event
- [ ] Check if delay is proportional to text length
- [ ] Profile keyboard typing speed in `pykeyboard.type()` (lines 70-81)
- [ ] Add timestamps to track state transitions

**Related Code**:
- `whisper-dictation-fast.py:70-81` - Keyboard typing logic
- `whisper-dictation-fast.py:22-94` - Transcription completion handling

**Possible Solutions**:
1. Increase keyboard typing speed
2. Use clipboard paste instead of character-by-character typing
3. Add visual feedback during text insertion phase
4. Optimize state transition logic

---

### Issue 5: Max Recording Time - Configurability & Feedback
**Status**: NEW - Enhancement/UX  
**Priority**: Medium  
**Description**: Max recording time (30s) should be either increased or user-configurable
- **Current limit**: 30 seconds (arbitrary, not documented)
- **Problem**: Too short for longer dictations, silent stop with no feedback
- **Solutions**:
  1. Increase default limit to 120+ seconds
  2. Make configurable via command-line argument (already supported, but undiscoverable)
  3. Add runtime UI control to change limit during session
  4. Add feedback when max time is approaching (countdown)

**Implementation Options**:
- **Quick fix**: Just increase default from 30 to 120 seconds
- **Better fix**: Add visual countdown when approaching limit
- **Best fix**: Add CLI arg to set custom limit + UI feedback

**Related Files**:
- `whisper-dictation-fast.py:295-298` - Already supports `-t` arg but needs discovery
- `whisper-dictation-fast.py:224-226` - Timer logic

**Acceptance Criteria**:
- [ ] User can specify max time via CLI: `--max-time 300` (5 minutes)
- [ ] Default increased to more reasonable value (120s recommended)
- [ ] User gets visual/audio feedback when time is running low

---

### Issue 6: Long Transcription Time
**Status**: Known/Expected
**Priority**: Low (Acknowledged as secondary)
**Description**: Model transcription takes significant time for longer audio (medium model)
- **Scope**: Using medium model (1.4GB) with Metal GPU
- **Expected**: Longer than base model, but still reasonable for medium quality
- **Acceptable**: User acknowledged this as secondary concern

**Current Performance** (needs measurement):
- [ ] Measure actual transcription time for 10s, 20s, 30s audio
- [ ] Compare: Python version vs C++ version
- [ ] Verify Metal GPU is actually being used during transcription

---

## 💡 FEATURE REQUESTS & ENHANCEMENTS

### Enhancement 1: Sparkle Framework Integration for Automatic Updates
**Status**: NEW - Backlog  
**Priority**: Low  
**Description**: Integrate Sparkle framework (https://sparkle-project.org/) for automatic macOS app updates

**Benefits**:
- **Seamless Updates**: True self-updating without user intervention
- **Security**: Support for EdDSA signatures and Apple Code Signing  
- **User Choice**: Users can choose automatic silent updates or manual control
- **Delta Updates**: Smaller, faster incremental updates between versions
- **Professional UX**: Custom branding, no "Sparkle" mentions visible to user

**Technical Requirements**:
- **Framework**: Sparkle 2 (supports macOS 10.13+, compatible with our 10.15+ target)
- **Packaging**: Requires .app bundle distribution (not script-based)
- **Signing**: Code signing certificate for update verification
- **Infrastructure**: Web server to host appcast.xml and update files
- **Build Process**: Automated release pipeline integration

**Implementation Considerations**:
- [ ] **App Bundle Migration**: Convert from script-based to .app bundle distribution
- [ ] **Release Pipeline**: Integrate with GitHub Actions for automated releases
- [ ] **Signing Infrastructure**: Set up Apple Developer certificate for code signing
- [ ] **Update Server**: Configure hosting for appcast and release files
- [ ] **User Migration**: Transition existing script users to app bundle

**Integration Points**:
- Works with existing Rumps-based status bar app architecture
- Compatible with both Python and C++ implementations
- No code changes required in core whisper-dictation logic

**Future Benefit**: Professional deployment model suitable for wider distribution

---

### Enhancement 1b: VoiceInk Discovery & Lessons Learned Integration
**Status**: NEW - Backlog  
**Priority**: Medium  
**Description**: Comprehensive discovery and comparison with VoiceInk (https://github.com/Beingpax/VoiceInk), a mature macOS voice-to-text app, to identify learnings and library integrations

**Scope of Discovery**:
1. **Architectural Comparison**
   - [ ] Compare code structure and patterns
   - [ ] Review app lifecycle and state management
   - [ ] Analyze how VoiceInk handles edge cases vs our implementation
   - [ ] Identify architectural improvements applicable to whisper-dictation

2. **Lessons Learned ("Lessons on Slern")** 
   - [ ] Document best practices from VoiceInk mature codebase
   - [ ] Identify reliability patterns (error handling, recovery)
   - [ ] Review performance optimization techniques
   - [ ] Extract user experience insights
   - [ ] Create Lessons Learned document: `memory-bank/lessons_learned/voiceink_architecture_review.md`

3. **Library & Dependency Analysis**
   - [ ] **KeyboardShortcuts** (MIT, sindresorhus) - Global hotkey management
     - Current: Using pynput; VoiceInk uses native Swift wrapper
     - Evaluation: Potential improvement for macOS-native hotkey handling
   - [ ] **LaunchAtLogin** (MIT, sindresorhus) - Startup behavior
     - Current: Manual scripts/shell integration
     - Evaluation: Could simplify startup management
   - [ ] **Zip** (MIT) - File compression utilities
     - Current: Not used; VoiceInk uses for package bundling
     - Evaluation: Needed if migrating to .app distribution
   - [ ] **FluidAudio** (Apache 2.0) - Audio processing utilities
     - Current: Using PyAudio; VoiceInk uses native Swift audio
     - Evaluation: Could improve audio quality/compatibility
   - [ ] **MediaRemoteAdapter** (BSD-3-Clause) - Media control integration
     - Current: Not implemented; VoiceInk supports media playback control
     - Evaluation: Enhancement for recording playback management
   - [ ] **SelectedTextKit** (macOS library) - Selected text handling
     - Current: Using clipboard directly
     - Evaluation: Could improve reliability of text insertion

4. **License Compatibility Review**
   - [ ] Verify whisper-dictation current license (likely MIT or similar)
   - [ ] Analyze each VoiceInk dependency license compatibility
   - [ ] Ensure commercial/future use remains viable
   - [ ] Document any license restrictions or requirements
   - [ ] Check if forked dependencies have different terms
   - Create License Compliance Matrix document

5. **Implementation Priority Matrix**
   - [ ] Rate each library for: usefulness, licensing risk, integration effort
   - [ ] Identify quick wins (easy integrations with high value)
   - [ ] Create roadmap for selective integrations
   - [ ] Determine if Python or Swift migration would be prerequisite

**Acceptance Criteria**:
- [ ] VoiceInk codebase reviewed and documented
- [ ] Lessons Learned document created and stored in memory-bank
- [ ] Library analysis completed with pros/cons for each
- [ ] License compatibility matrix established
- [ ] Implementation recommendations prioritized
- [ ] Future integration roadmap proposed

**Deliverables**:
1. `memory-bank/lessons_learned/voiceink_architecture_review.md`
2. `memory-bank/specs/discovery-voiceink-library-analysis.md` (if detailed spec needed)
3. Updated backlog with library integration priorities

**Related Files**:
- VoiceInk repo: https://github.com/Beingpax/VoiceInk
- Our current dependencies: `pyproject.toml`, `requirements.txt`

---

### Enhancement 2: Expandable Application Menu
**Status**: NEW - Backlog
**Priority**: Medium
**Description**: Add runtime configuration options to the application menu for better UX control

**Requested Features**:
1. **Recording Time Limit Control**
   - Current: Hardcoded 30s default, only changeable via CLI args
   - Desired: Menu option to increase limit (60s, 120s, custom)
   - Benefit: User doesn't need terminal knowledge

2. **Model Selection Menu**
   - Current: Fixed model selection via CLI (`--model base`, `--model medium`)
   - Desired: Menu option to switch between models (base, small, medium)
   - Benefit: Runtime model switching without restart

3. **Other Settings (To Research)**
   - Language selection (auto, EN, PL, etc.)
   - Mic sensitivity/input device selection
   - Output format/text processing options
   - Hotkey customization
   - Log verbosity level

**Implementation Approach**:
- [ ] Research: What settings are user-configurable and valuable?
- [ ] Design: Menu structure for Rumps status bar app
- [ ] Implement: Add configuration UI to StatusBarApp
- [ ] Persist: Save user preferences to config file (~/.whisper-dictation-config.json?)
- [ ] Test: Ensure menu changes take effect without restart where possible

**Related Code**:
- `whisper-dictation.py:StatusBarApp` - GUI menu logic
- `whisper-dictation-fast.py:StatusBarApp` - GUI menu logic (C++ version)
- Config handling: May need to add new config module

**Acceptance Criteria**:
- [ ] User can change recording time limit from menu (instant effect on next recording)
- [ ] User can select model from menu (instant effect on next recording)
- [ ] Settings persist across app restarts
- [ ] Both Python and C++ versions support all new menu options

---

## 📋 INVESTIGATION CHECKLIST

### For Issue 2 (First Two Words Joined):
```
[ ] Run test dictation and capture raw whisper-cli output
[ ] Check if space between words 1-2 exists in raw output
[ ] If exists: problem is in keyboard typing
[ ] If missing: problem is in transcription
[ ] Test with: en, pl, mixed languages
[ ] Compare: Python version behavior
```

### For Issue 3 (Silent Stop):
```
[ ] Measure actual max time enforcement
[ ] Test with 30s, 60s recordings
[ ] Confirm no user feedback when stopping
[ ] Check StatusBarApp state transitions
```

---

## 📁 Related Documentation

- **Diagnostic Spec**: `memory-bank/specs/task-audio-clipping-diagnosis.md`
- **Data Flow**: `docs/DATA_FLOW.md`
- **Current Context**: `current_context.md`
- **README**: Known issues section

---

## 🔧 Next Steps

1. **Immediate**: Implement diagnostics for Issue 1 (audio clipping)
2. **Parallel**: Investigate Issue 2 (joined words) - simpler to debug
3. **Quick Fix**: Increase max-time default + add feedback for Issue 3 & 4
4. **Later**: Optimize transcription time if needed

---

## Test Cases to Create

```python
def test_first_two_words_spacing():
    """Verify that first two words are properly spaced"""
    # Record: "Pierwsza druga trzecia słowa"
    # Expected: "Pierwsza druga trzecia słowa"
    # Actual: "Pierwszadruga trzecia słowa" ?

def test_max_time_feedback():
    """Verify user gets feedback when max time is reached"""
    # Record for 30+ seconds
    # Expected: Audio stops at 30s with notification
    # Actual: Audio stops silently?

def test_audio_clipping_consistency():
    """Measure how often clipping occurs"""
    # Record 10 samples
    # Measure silence duration at start
    # Calculate: clipping rate, average loss duration
```

---

## Metadata

**Created**: 2025-10-20  
**Session**: Audio Issues Review  
**Reporter**: User (Marcin Przybyszewski)  
**Status**: Active - Ready for Investigation
