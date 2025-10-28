# Confluence Helper Scripts - Usage Guide

This project includes optimized helper scripts for working with Confluence pages efficiently.

## Available Scripts

### 1. Section-Aware Editor (Recommended) ⭐
**File**: `scripts/confluence_section_helper.py`

**Use case**: Update specific sections without touching others

**Commands**:
```bash
# List all sections
python3 scripts/confluence_section_helper.py list 131083

# Update by section number
python3 scripts/confluence_section_helper.py update 131083 "Page Title" 7 "<p>New content</p>"

# Update by section title
python3 scripts/confluence_section_helper.py update-title 131083 "Page Title" "Priorities" "<p>New content</p>"
```

**Python API**:
```python
from scripts.confluence_section_helper import ConfluenceSectionHelper

helper = ConfluenceSectionHelper()

# List sections
helper.list_sections("131083")

# Update by title (easiest)
helper.update_section_by_title(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_title="Next Priorities",
    new_content="<p>Updated content</p>"
)

# Append to section
helper.append_to_section(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_number=7,
    content_to_append="<p>Additional content</p>"
)
```

### 2. Mermaid Diagram Helper
**File**: `scripts/confluence_mermaid_helper.py`

**Use case**: Add Mermaid diagrams to pages

**Command**:
```bash
python3 scripts/confluence_mermaid_helper.py \
    131083 \
    "Metal Scribe — Start Page" \
    docs/diagrams/my-diagram.mmd \
    my-diagram \
    "<h2>Section Title</h2>"
```

**Python API**:
```python
from scripts.confluence_mermaid_helper import ConfluenceMermaidHelper

helper = ConfluenceMermaidHelper()

helper.add_mermaid_diagram(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    diagram_path="docs/diagrams/architecture.mmd",
    attachment_name="architecture-diagram",
    insert_after_pattern="<h2>Architecture</h2>"
)
```

## Setup

### Option 1: macOS Keychain (Recommended) ⭐

Store credentials securely in macOS keychain:

```bash
# Store credentials once
security add-generic-password -a "$USER" -s confluence_api_token -w 'YOUR_TOKEN'
security add-generic-password -a "$USER" -s confluence_username -w 'your-email@example.com'
```

The scripts will automatically retrieve from keychain when needed. No environment variables required!

### Option 2: Environment Variables

```bash
export CONFLUENCE_URL="https://metal-scribe.atlassian.net/wiki"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

### Option 3: Both (Best of Both Worlds)

Add to `~/.zshenv` for automatic loading:
```bash
# Load from keychain automatically
if [[ -z "$CONFLUENCE_API_TOKEN" ]]; then
    export CONFLUENCE_API_TOKEN=$(security find-generic-password -a "$USER" -s confluence_api_token -w 2>/dev/null)
fi

if [[ -z "$CONFLUENCE_USERNAME" ]]; then
    export CONFLUENCE_USERNAME=$(security find-generic-password -a "$USER" -s confluence_username -w 2>/dev/null)
fi

export CONFLUENCE_URL="https://metal-scribe.atlassian.net/wiki"
```

**Priority**: Environment variables → Keychain → Error

## Benefits

- **80%+ token savings** compared to manual approaches
- **Safe**: Section-aware editing only modifies specified sections
- **Fast**: Single fetch + single update (minimal API calls)
- **No dependencies**: Uses only Python stdlib + curl

## Examples

### Example 1: Update project status
```python
helper = ConfluenceSectionHelper()
helper.update_section_by_title(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_title="Current Status",
    new_content="""
    <p><strong>Status:</strong> ✅ All tests passing</p>
    <p><strong>Last update:</strong> 2025-10-28</p>
    """
)
```

### Example 2: Add architecture diagram
```python
helper = ConfluenceMermaidHelper()
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    diagram_path="docs/diagrams/system-overview.mmd",
    attachment_name="system-overview",
    insert_after_pattern="<h2>Architecture (high-level)</h2>"
)
```

### Example 3: Append to roadmap
```python
helper = ConfluenceSectionHelper()
helper.append_to_section(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_number=8,  # Roadmap section
    content_to_append="<p><em>Updated: Oct 2025</em></p>"
)
```

## Documentation

- **Quick summary**: `memory-bank/lessons_learned/confluence_optimization_summary.md`
- **Full guide**: `memory-bank/lessons_learned/confluence_workflow_optimization.md`
- **Mermaid specifics**: `memory-bank/lessons_learned/confluence_mermaid_diagrams.md`

## Notes

- Section helper follows best practices from lessons learned
- Mermaid diagrams uploaded without `.mmd` extension (critical!)
- All operations are atomic (one fetch, one update)
- Error handling included for common issues
