# Documentation Enhancement Plan

## Objective
To comprehensively review, refine, and enhance all existing project documentation within the `whisper-dictation` repository, addressing documentation-specific technical debt, improving clarity, conciseness, and accuracy, and ensuring the documentation is highly usable for both human developers and future AI agents. This plan prioritizes visual explanations using Mermaid diagrams over extensive code blocks where beneficial.

## Guiding Principles (from `temp/documentation_personality.md`)
- Clarity and Conciseness
- Structure and Scannability
- AI-Friendliness & Semantic Richness
- "Image over Code" Rule (prioritize diagrams)
- Accuracy and Maintainability
- Context and Purpose

## Phase 1: Critical Fixes (Truncated Files & Missing Core Docs)

### 1.1. Complete Truncated Files (CRITICAL)
*   **Goal**: Restore full content and apply "Image over Code" principle to these key documents.
*   **Affected Files**:
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/API_INTERFACES.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/MODULES.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/modules/device_manager.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/modules/recorder.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/modules/transcriber.md`
*   **Action**: For each, I will:
    1.  Read the existing (truncated) content.
    2.  Consult the relevant Python source files (`recorder.py`, `transcriber.py`, `device_manager.py`, `mps_optimizer.py`) to reconstruct the full API, methods, and logic.
    3.  Rewrite/complete the document, converting Python code blocks for method signatures and class structures into Mermaid class diagrams.
    4.  Add Mermaid flowcharts/sequence diagrams for key processes or interactions.
    5.  Ensure examples are minimal and focused.

### 1.2. Create Missing Core Directories and READMEs
*   **Goal**: Establish the full documentation structure as per `docs/DOCUMENTATION_PLAN.md`.
*   **Affected Files/Directories**:
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/modules/README.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/processes/` (directory)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/processes/README.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/context/` (directory)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/context/README.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/` (directory)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/ADR/` (directory)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/ADR/README.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/layers/` (directory)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/layers/README.md`
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/IMPLEMENTATION.md` (stub)
    *   `/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/architecture/RISKS.md` (stub)
*   **Action**: Create these directories and populate them with basic `README.md` files or stubs, linking them appropriately.

## Phase 2: "Image over Code" & Diagram Enhancements

### 2.1. `docs/API_INTERFACES.md`
*   **Goal**: Convert all Python method signatures and examples to Mermaid class diagrams and sequence diagrams.
*   **Action**: Replace code blocks with `classDiagram` for class structures and `sequenceDiagram` for interactions. Keep minimal code for usage examples.

### 2.2. `docs/ARCHITECTURE.md`
*   **Goal**: Condense the document, move detailed ADRs and implementation specifics to sub-documents, and enhance with diagrams.
*   **Action**:
    1.  Extract ADRs (ADR-001, ADR-002, ADR-003, ADR-004, ADR-005) into individual files in `docs/architecture/ADR/`.
    2.  Extract detailed implementation examples (e.g., for design patterns) into `docs/architecture/IMPLEMENTATION.md`.
    3.  Extract detailed risk analysis into `docs/architecture/RISKS.md`.
    4.  Condense the main `ARCHITECTURE.md` to be a high-level overview, linking to the new detailed files.
    5.  Ensure all remaining code blocks are converted to Mermaid diagrams or simplified.
    6.  Address TD-033 (TODO comments) by either resolving them or moving them to `TECHNICAL_DEBT.md` if they represent code debt.

### 2.3. `docs/DATA_FLOW.md`
*   **Goal**: Convert ASCII art diagrams and Python code blocks to Mermaid diagrams.
*   **Action**:
    1.  Replace ASCII art decision trees with Mermaid flowcharts.
    2.  Convert Python code blocks for error handling and audio pipeline to Mermaid flowcharts/sequence diagrams.
    3.  Add code examples for advanced scenarios (as per QA report).

### 2.4. `docs/MODULES.md`
*   **Goal**: Enhance with Mermaid diagrams for module structure, dependencies, and responsibilities.
*   **Action**: Add `graph TD` or `graph LR` diagrams to visualize module relationships.

### 2.5. Individual Module Docs (`docs/modules/*.md`)
*   **Goal**: Ensure each has 2-3 Mermaid diagrams (class structure, process flow, dependencies).
*   **Action**: Add `classDiagram`, `flowchart TD`, or `graph LR` diagrams to illustrate key aspects of each module.

### 2.6. `docs/diagrams/system-overview.mmd`
*   **Goal**: Replace the simplistic diagram with a comprehensive one.
*   **Action**: Create a detailed system overview diagram showing all major components and their interactions, as suggested in the QA report.

## Phase 3: Consistency and Clarity

### 3.1. Section Numbering
*   **Goal**: Fix inconsistent numbering in `docs/DATA_FLOW.md`.
*   **Action**: Renumber all sections to follow a logical hierarchy (1, 1.1, 1.1.1, etc.).

### 3.2. Table Formatting
*   **Goal**: Standardize table formatting across all documents.
*   **Action**: Ensure consistent spacing around `|` separators in all Markdown tables.

### 3.3. Metadata
*   **Goal**: Add consistent metadata footers to all major documents.
*   **Action**: Implement a standard footer with `Last updated`, `Version`, `Status` (e.g., ✅ Ukończone / 🚧 W trakcie / 📝 Planowane).

### 3.4. Emoji/Icons
*   **Goal**: Standardize emoji usage in headings.
*   **Action**: Review `docs/README.md` and other documents to ensure consistent application or removal of emojis in headings.

### 3.5. Conciseness
*   **Goal**: Review long documents for opportunities to condense or link to sub-documents.
*   **Action**: Ensure `ARCHITECTURE.md` and `DATA_FLOW.md` are high-level overviews, with details moved to linked sub-documents.

### 3.6. Cross-referencing
*   **Goal**: Ensure all links are correct and relative.
*   **Action**: Perform a link check across all documents.

### 3.7. Language Highlighting
*   **Goal**: Add language identifiers to all code blocks.
*   **Action**: Update all code blocks to use ````python`, ````bash`, ````mermaid`, etc.

## Phase 4: Documentation Debt & Final Polish

### 4.1. Address TD-013 (Documentation Debt)
*   **Goal**: Ensure `DeviceManager` public methods are well-documented.
*   **Action**: Verify `API_INTERFACES.md` and `docs/modules/device_manager.md` comprehensively cover `DeviceManager`'s public API.

### 4.2. Address TD-033 (Documentation Debt)
*   **Goal**: Resolve TODO comments in `ARCHITECTURE.md`.
*   **Action**: Either implement the suggested content or move the TODO to `TECHNICAL_DEBT.md` if it's a code-related task.

### 4.3. Review `PROJECT_OVERVIEW.md`
*   **Goal**: Ensure it's concise and high-level, linking to details.
*   **Action**: Verify its content aligns with the "overview" purpose.

### 4.4. Update `docs/README.md`
*   **Goal**: Reflect any new files or restructured sections.
*   **Action**: Add links to newly created ADRs, implementation details, and risk analysis documents.

### 4.5. Final QA
*   **Goal**: Perform a final review against the "Documentation Personality" principles.
*   **Action**: Read through all modified documents to ensure they meet the defined standards.

## Execution Strategy
I will execute this plan iteratively, committing changes after each logical step or set of related changes. I will prioritize Phase 1 and 2 to establish a solid foundation and visual clarity.
