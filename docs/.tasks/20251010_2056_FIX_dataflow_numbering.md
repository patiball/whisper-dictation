# Task: Fix Section Numbering in DATA_FLOW.md

## File
`/Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/DATA_FLOW.md`

## Issue
Section numbering is inconsistent - jumps from 2.2 to 3 instead of 2.3.

Current flow: 1 → 2 → 2.1 → 2.2 → **3** (incorrect jump)

## Action Required
Renumber all sections to follow proper hierarchy:
- Top-level sections: 1, 2, 3, 4...
- Sub-sections: 1.1, 1.2, 2.1, 2.2...
- Sub-sub-sections: 1.1.1, 1.1.2...

## Instructions
1. Read the file and identify current section structure
2. Create correct numbering scheme
3. Update ALL section headers with correct numbers
4. Update any internal cross-references if they exist
5. Ensure ToC (if present) is updated

## Verification
```bash
# Extract all section headers
grep "^##" /Users/mprzybyszewski/dev/ai-projects/whisper-dictation/docs/DATA_FLOW.md | head -20
```
Should show logical progression without jumps.

## Success Criteria
- [ ] All sections numbered logically
- [ ] No skipped numbers in sequence
- [ ] Sub-section numbering is consistent
- [ ] Cross-references updated if any exist
- [ ] Document flows logically
