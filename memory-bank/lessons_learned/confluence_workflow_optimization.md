# Confluence Workflow Optimization - Lessons Learned

## Context
When working with large Confluence pages via API/MCP tools, inefficient workflows can quickly consume tokens and context. This document outlines optimized approaches.

**Date**: 2025-10-28
**Project**: Metal Scribe (whisper-dictation)

---

## The Problem: Token-Inefficient Workflow

### What NOT to do:
```python
# ❌ Inefficient approach
1. Download full page content (large payload)
2. Parse entire HTML in Python
3. Reconstruct entire page HTML
4. Send entire page back via PUT request
5. Repeat for each modification
```

**Issues:**
- Large pages consume massive tokens
- Error-prone HTML reconstruction
- Multiple full page downloads/uploads
- Wasted API calls

---

## Optimized Approaches

### Approach 1: MCP Tools for Markdown Content ✅

**When to use**: Regular text content updates (not Mermaid macros)

```python
from mcp__atlassian__invoke_tool import update_confluence_page

# Direct find/replace without downloading full content
update_confluence_page(
    page_url="https://site.atlassian.net/wiki/spaces/ZP/pages/131083",
    find="## Old Heading",
    replace="## New Heading\n\nAdditional content here",
    version_message="Updated heading"
)
```

**Pros:**
- MCP handles version management
- No need to download/reconstruct page
- Works with Markdown format
- Token-efficient

**Cons:**
- Cannot handle HTML storage format macros (like Mermaid)
- Macros get stripped when using Markdown

---

### Approach 2: Targeted REST API Updates ✅

**When to use**: HTML macros (Mermaid), complex formatting

**Helper Script**: `scripts/confluence_mermaid_helper.py`

```python
helper = ConfluenceMermaidHelper()
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="My Page",
    diagram_path="diagram.mmd",
    attachment_name="my-diagram",  # No .mmd extension!
    insert_after_pattern="<h2>Section 3</h2>"
)
```

**Key Optimizations:**
1. **Minimal fetches**: Only get version + content when needed
2. **Single replacement**: Use Python `str.replace()` once
3. **Targeted pattern**: Find exact insertion point
4. **No re-parsing**: Work with raw HTML string

**Token Comparison:**
- ❌ Old approach: ~15-20K tokens per update (full page multiple times)
- ✅ New approach: ~3-5K tokens per update (one fetch, one replace, one push)

---

### Approach 3: Section-Aware Editing ✅ (RECOMMENDED)

**When to use**: Updating specific sections without touching others

**Helper Script**: `scripts/confluence_section_helper.py`

**Key Benefits:**
- **Surgical updates**: Only modify the section you specify
- **Safe**: Other sections remain completely untouched
- **Intuitive**: Use section numbers or titles (fuzzy match)
- **Efficient**: Still only one fetch + one push

**Usage Examples:**

```python
from scripts.confluence_section_helper import ConfluenceSectionHelper

helper = ConfluenceSectionHelper()

# 1. List all sections (find what you need)
helper.list_sections(page_id="131083")
# Output:
# 1. General information
# 2. 1) Purpose and Scope
# 3. 2) Key Features
# ...

# 2. Update by section number
helper.update_section(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_number=7,
    new_content="<p>New priority list...</p>"
)

# 3. Update by section title (easier!)
helper.update_section_by_title(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_title="Next Priorities",  # Fuzzy match
    new_content="<p>Updated priorities...</p>"
)

# 4. Append to existing section (don't replace)
helper.append_to_section(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_number=7,
    content_to_append="<p>Additional item.</p>"
)
```

**Command Line Usage:**
```bash
# List sections
python3 scripts/confluence_section_helper.py list 131083

# Update section by number
python3 scripts/confluence_section_helper.py update 131083 "Page Title" 7 "<p>New content</p>"

# Update by title
python3 scripts/confluence_section_helper.py update-title 131083 "Page Title" "Priorities" "<p>New content</p>"
```

**Why This is Better:**
- ✅ You say: "Update section 7"
- ✅ Only section 7 is modified
- ✅ Sections 1-6 and 8-13 are completely untouched
- ✅ No risk of accidentally modifying other content
- ✅ Clear intent in code/commands

**Token Comparison:**
- ❌ Manual HTML editing: ~15-20K tokens
- ✅ Section-aware update: ~3-5K tokens
- 💡 **Plus**: Much safer and easier to use!

---

### Approach 4: Batch Operations ✅

**When to use**: Multiple diagrams or updates

```python
# Get version once
version = helper.get_page_version(page_id)

# Upload all attachments (small operations)
attachments = []
for diagram_file in diagram_files:
    att = helper.upload_diagram(page_id, diagram_file, name)
    attachments.append(att)

# Single page update with all macros
# (Build replacement string with all macros, then one update)
```

---

## Best Practices

### 1. Use the Right Tool for the Job

| Content Type | Tool | Format |
|--------------|------|--------|
| Text, headings, lists | MCP `update_confluence_page` | Markdown |
| **Update specific section** | **`confluence_section_helper.py`** ⭐ | **HTML Storage** |
| Mermaid diagrams | `confluence_mermaid_helper.py` | HTML Storage |
| Tables (simple) | MCP | Markdown |
| Complex macros | REST API | HTML Storage |

**⭐ Recommended for most updates**: Section-aware editing is safer and more intuitive

### 2. Minimize Page Fetches

```python
# ❌ Bad: Multiple fetches
version = get_version(page_id)
content = get_content(page_id)
# ... make changes ...
update_page(page_id, new_content)
# ... oops, need to update again ...
version = get_version(page_id)  # Redundant fetch!

# ✅ Good: Single fetch when possible
data = get_page_with_version_and_content(page_id)
version = data['version']['number']
content = data['body']['storage']['value']
# ... make all changes ...
update_page(page_id, new_content, version + 1)
```

### 3. Use Targeted String Replacement

```python
# ❌ Bad: Parse and reconstruct
from bs4 import BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')
section = soup.find('h2', text='Section 3')
# ... complex DOM manipulation ...
new_content = str(soup)  # Risky reconstruction

# ✅ Good: Direct string replacement
pattern = '<h2>Section 3</h2>'
replacement = '<h2>Section 3</h2><mermaid-macro>...</mermaid-macro>'
new_content = content.replace(pattern, replacement, 1)
```

### 4. Verify Patterns Exist Before Update

```python
if insert_pattern not in content:
    raise ValueError(f"Pattern not found: {insert_pattern}")
```

---

## Helper Script Usage

### Basic Usage:
```bash
python3 scripts/confluence_mermaid_helper.py \
    131083 \
    "Metal Scribe — Start Page" \
    docs/diagrams/architecture.mmd \
    architecture-diagram \
    "<h2>Architecture</h2>"
```

### From Python Code:
```python
from scripts.confluence_mermaid_helper import ConfluenceMermaidHelper

helper = ConfluenceMermaidHelper()

# Add diagram
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    diagram_path="docs/diagrams/system-overview.mmd",
    attachment_name="system-overview",
    insert_after_pattern='<h2>Architecture (high-level)</h2>'
)
```

---

## Token Usage Estimates

### For a 500-line Confluence page:

| Operation | Old Approach | Optimized Approach | Savings |
|-----------|-------------|-------------------|---------|
| View page | ~8K tokens | ~8K tokens | 0% (same) |
| Add 1 diagram | ~20K tokens | ~4K tokens | **80%** |
| Add 3 diagrams | ~60K tokens | ~10K tokens | **83%** |
| Fix macro issue | ~25K tokens | ~5K tokens | **80%** |

**Key savings**: Avoiding multiple full-page reconstructions

---

## Common Patterns

### Pattern 1: Update a Specific Section (Recommended) ⭐
```python
# User says: "Please update section 7 with new priorities"
helper = ConfluenceSectionHelper()
helper.update_section_by_title(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_title="Next Priorities",
    new_content="<ol><li>New priority 1</li><li>New priority 2</li></ol>"
)
# Result: Only section 7 is updated, all other sections untouched
```

### Pattern 2: Add Content to End of Section
```python
# User says: "Add a note to the roadmap section"
helper.append_to_section(
    page_id="131083",
    page_title="Metal Scribe — Start Page",
    section_number=8,  # Short-term Roadmap
    content_to_append="<p><strong>Note:</strong> Timeline updated Oct 2025</p>"
)
```

### Pattern 3: List Sections Before Updating
```python
# User says: "Update the architecture section"
# First, find which section number it is:
helper.list_sections("131083")
# Output shows: "4. 3) Architecture (high-level)"
# Then update it:
helper.update_section(page_id="131083", page_title="...", section_number=4, new_content="...")
```

### Pattern 4: Add Diagram After Heading
```python
insert_after_pattern = '<h2>My Section</h2>'
```

### Pattern 5: Add Diagram After Paragraph
```python
insert_after_pattern = '<p>This is where the diagram goes.</p>'
```

### Pattern 6: Replace Existing Content
```python
find_pattern = '<p>Old diagram placeholder</p>'
replacement = '<mermaid-macro>...</mermaid-macro>'
```

### Pattern 7: Fix Existing Macro
```python
# Remove .mmd extension from existing macro
find_pattern = '<ac:parameter ac:name="filename">diagram.mmd</ac:parameter>'
replacement = '<ac:parameter ac:name="filename">diagram</ac:parameter>'
```

---

## Error Handling

### Check Pattern Exists
```python
try:
    helper.update_page_targeted(page_id, pattern, replacement, title)
except ValueError as e:
    print(f"Pattern not found. Checking page content...")
    # Log available patterns or sections
```

### Handle Version Conflicts
```python
try:
    helper.update_page_targeted(...)
except requests.HTTPError as e:
    if e.response.status_code == 409:
        print("Version conflict. Page was modified. Retrying...")
        # Fetch new version and retry
```

---

## Credential Management

### macOS Keychain Integration (Recommended) ⭐

Both helper scripts support automatic credential retrieval from macOS keychain:

**Setup once:**
```bash
security add-generic-password -a "$USER" -s confluence_api_token -w 'YOUR_TOKEN'
security add-generic-password -a "$USER" -s confluence_username -w 'your-email@example.com'
```

**Scripts auto-load from keychain** - no manual export needed!

**Fallback order:**
1. Environment variables (if set)
2. macOS keychain (automatic)
3. Error if neither found

**Benefits:**
- ✅ Secure (macOS encrypted storage)
- ✅ No tokens in files/git
- ✅ Industry standard pattern
- ✅ Works in any shell (bash/zsh)

**Optional: Auto-load in ~/.zshenv**
```bash
if [[ -z "$CONFLUENCE_API_TOKEN" ]]; then
    export CONFLUENCE_API_TOKEN=$(security find-generic-password -a "$USER" -s confluence_api_token -w 2>/dev/null)
fi

if [[ -z "$CONFLUENCE_USERNAME" ]]; then
    export CONFLUENCE_USERNAME=$(security find-generic-password -a "$USER" -s confluence_username -w 2>/dev/null)
fi

export CONFLUENCE_URL="https://your-domain.atlassian.net/wiki"
```

---

## Summary

✅ **Do:**
- **Use section-aware editing for most updates** ⭐ (safest, most intuitive)
- Use MCP tools for simple Markdown content
- Use helper scripts for Mermaid diagrams and section updates
- Make targeted string replacements
- Minimize page fetches
- Batch operations when possible

❌ **Don't:**
- Parse and reconstruct full HTML unnecessarily
- Fetch page content multiple times
- Use Markdown for macros (they get stripped)
- Work with large payloads when small ones suffice
- Modify entire page when you only need to update one section

**Key Insights**: 
1. **Section-aware editing** is the safest approach - only the specified section is modified
2. Treat Confluence page content as a string for targeted modifications, not as a DOM to be parsed and reconstructed
3. This is faster, more reliable, and far more token-efficient (80%+ savings)

## Quick Decision Guide

**"I need to update section X with new content"**
→ Use `confluence_section_helper.py` ⭐

**"I need to add a Mermaid diagram"**
→ Use `confluence_mermaid_helper.py`

**"I need to update simple text/markdown"**
→ Use MCP `update_confluence_page`

**"I need complex HTML manipulation"**
→ Use REST API with targeted string replacement
