# Task: Restructure ARCHITECTURE.md - Approach 1 "Short + Details in Attachments"

## Objective
Transform ARCHITECTURE.md from a monolithic document into a concise overview with detailed appendices in separate files.

## Current Issues
- Too much implementation detail in main document
- Repetitive recommendations and risk lists
- No quick "tl;dr" for readers wanting fast understanding
- Difficult to navigate ~1200 lines

## Target Structure

### Main ARCHITECTURE.md (Target: ~400-500 lines)
Should contain:
1. **TL;DR Section** (NEW)
   - 3-5 sentences summarizing key architectural decisions
   - Main flow diagram
   - Link to detailed sections

2. **System Overview** (CONDENSED)
   - High-level 5-layer architecture
   - Main components (4-6 bullet points per layer)
   - Dependencies overview
   - Links to detailed layer docs

3. **Key Diagrams** (KEEP)
   - Main architecture diagram
   - Component relationships
   - Data flow overview

4. **Architecture Decision Records** (CONDENSED)
   - Keep ADR titles and rationale (1-2 paragraphs each)
   - Move detailed consequences/alternatives to ADR/ folder

5. **Design Patterns** (CONDENSED)
   - Pattern names and purpose
   - Link to detailed pattern docs

6. **Links to Detailed Documentation**
   - ADRs → docs/architecture/ADR/
   - Implementation → docs/architecture/IMPLEMENTATION.md
   - Risks → docs/architecture/RISKS.md
   - Layer details → docs/architecture/layers/

### New Files to Create

#### 1. docs/architecture/ADR/README.md
- Index of all ADRs
- Quick reference table

#### 2. docs/architecture/ADR/ADR-001-audio-device-management.md
Extract from ARCHITECTURE.md ADR #1

#### 3. docs/architecture/ADR/ADR-002-whisper-integration.md
Extract from ARCHITECTURE.md ADR #2

#### 4. docs/architecture/ADR/ADR-003-text-insertion.md
Extract from ARCHITECTURE.md ADR #3

[Continue for all ADRs - should be ~7 files]

#### 5. docs/architecture/IMPLEMENTATION.md
Content to extract:
- Detailed API descriptions
- Method signatures
- Implementation examples
- Code snippets
- TODO lists
- Technical checklists

#### 6. docs/architecture/RISKS.md
Content to extract:
- Complete risk analysis (currently lines 935-1161)
- Mitigation strategies
- Risk prioritization
- Monitoring recommendations

#### 7. docs/architecture/layers/
Create separate files for each layer:
- LAYER_1_PRESENTATION.md (StatusBarApp, UI)
- LAYER_2_CONTROL.md (Event handling, KeyListener)
- LAYER_3_BUSINESS_LOGIC.md (Recorder, Transcriber, DeviceManager)
- LAYER_4_DATA.md (Buffers, Cache)
- LAYER_5_INTEGRATION.md (PyAudio, Whisper, OS integration)

## Step-by-Step Instructions

### Phase 1: Create Directory Structure
```bash
mkdir -p /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/ADR
mkdir -p /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/layers
```

### Phase 2: Read Current ARCHITECTURE.md
Analyze and identify sections to extract.

### Phase 3: Create New Files

For each ADR:
1. Extract ADR content from ARCHITECTURE.md
2. Create ADR-XXX-title.md following ADR template:
```markdown
# ADR-XXX: Title

**Status**: Accepted | Proposed | Deprecated  
**Date**: YYYY-MM-DD  
**Context**: [Problem statement]  
**Decision**: [What was decided]  
**Consequences**: [Positive and negative outcomes]  
**Alternatives Considered**: [Other options]  
```

For IMPLEMENTATION.md:
- Extract all detailed API descriptions
- Method signatures and parameters
- Code examples
- TODO lists
- Technical implementation notes

For RISKS.md:
- Extract complete "Obszary ryzyka" section
- Keep detailed mitigation strategies
- Add risk matrix/prioritization

For layers/:
- Extract detailed layer documentation
- Component details
- Internal interactions
- Technical specifications

### Phase 4: Restructure Main ARCHITECTURE.md

**New Structure**:
```markdown
# Architecture

## TL;DR
[3-5 sentences + main diagram + quick links]

## Table of Contents
[Clean ToC with links]

## 1. System Overview
[High-level description, 300-400 words]
[Main architecture diagram]
[Links to layer details]

## 2. Five-Layer Architecture
[Brief description of each layer, 4-6 points each]
[Diagram]
[Links to detailed layer docs]

## 3. Key Components
[Table with component, purpose, layer, link to details]

## 4. Architecture Decisions (Summary)
[ADR table with: ID, Title, Status, Link to details]

## 5. Design Patterns (Summary)
[Pattern name, purpose, link to implementation details]

## 6. Integration Points
[Brief overview]
[Diagram]
[Link to INTEGRATION.md details]

## 7. Quality Attributes
[Performance, Scalability, Maintainability - brief]
[Link to detailed analysis]

## 8. See Also
- [Detailed ADRs](./architecture/ADR/)
- [Implementation Details](./architecture/IMPLEMENTATION.md)
- [Risk Analysis](./architecture/RISKS.md)
- [Layer Documentation](./architecture/layers/)
- [System Integration](./SYSTEM_INTEGRATION.md)
- [Data Flow](./DATA_FLOW.md)

## Metadata
[Version, Last Updated, Contributors]
```

### Phase 5: Create Cross-References
- Ensure all links between documents work
- Add navigation breadcrumbs in subdocuments
- Create architecture/ README.md as index

### Phase 6: Update Related Documents
- Update README.md links if needed
- Update SYSTEM_INTEGRATION.md references
- Verify all cross-references work

## Verification

After restructuring:
```bash
# Check file structure
ls -R /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/

# Check main file length (should be ~400-500 lines)
wc -l /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/ARCHITECTURE.md

# Check for broken links
grep -r '\[.*\](.*\.md)' /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/ARCHITECTURE.md

# Verify ADR count
ls /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/ADR/*.md | wc -l
```

## Success Criteria
- [ ] ARCHITECTURE.md reduced to 400-500 lines
- [ ] TL;DR section added at top
- [ ] All ADRs extracted to separate files
- [ ] IMPLEMENTATION.md created with detailed API info
- [ ] RISKS.md created with complete risk analysis
- [ ] Layer documentation split into 5 files
- [ ] All cross-references working
- [ ] Directory structure created
- [ ] README files created for navigation
- [ ] No information lost (only reorganized)
- [ ] Diagrams remain in main doc or appropriately linked

## Benefits
✅ Faster navigation for readers seeking overview  
✅ Detailed info preserved for deep dives  
✅ Easier maintenance (update ADRs independently)  
✅ Better organization following industry standards  
✅ Clearer separation of concerns  
✅ Scalable structure for future additions  

## Estimated Time
- Phase 1: 2 minutes
- Phase 2: 5 minutes  
- Phase 3: 30-40 minutes (content extraction)
- Phase 4: 20-30 minutes (main doc restructuring)
- Phase 5: 10 minutes (cross-references)
- Phase 6: 5 minutes (updates)
**Total: ~75-90 minutes**
