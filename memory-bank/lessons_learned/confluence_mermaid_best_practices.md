# Confluence Mermaid Diagrams - Best Practices

**Goal**: Add Mermaid diagrams to Confluence reliably on the first try.

---

## Core Principles

### 1. Use the Helper Script ⭐

**Recommended approach:**
```python
from scripts.confluence_mermaid_helper import ConfluenceMermaidHelper

helper = ConfluenceMermaidHelper()
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="My Page",
    diagram_path="docs/diagrams/architecture.mmd",
    attachment_name="architecture",  # No extension!
    insert_after_pattern="<h2>Architecture</h2>",
    clean_existing=True  # Prevents orphaned attachments
)
```

**Why this works:**
- Handles file naming correctly (no `.mmd` extension)
- Uses exact names (no random suffixes)
- Cleans up existing attachments automatically
- Sets correct revision parameter
- One function call = working diagram

---

## Essential Rules

### Rule 1: Generic Names Are Automatically Prefixed ⭐

**The helper automatically handles generic names!**

✅ **YOU CAN USE**: Generic names like "diagram", "chart", etc.
```python
attachment_name="diagram"  # Helper auto-prefixes to "diagram-24737279"
attachment_name="chart"    # Helper auto-prefixes to "chart-ef9f8c33"
```

**Auto-prefix behavior:**
- Generic names (`diagram`, `chart`, `image`, `graph`, `figure`, `visual`) get unique suffix
- Suffix based on `insert_after_pattern` (ensures same section = same name)
- Prevents conflicts across different sections automatically
- Non-generic names pass through unchanged

✅ **EVEN BETTER**: Use descriptive names (no prefix needed)
```python
attachment_name="architecture-overview"    # Used as-is
attachment_name="dataflow-sequence"        # Used as-is
attachment_name="section3-components"      # Used as-is
```

❌ **DON'T**: Include file extensions
```python
attachment_name="architecture.mmd"  # BAD - extension causes 404
```

**Examples:**
```python
# Section 3 - both use "diagram"
helper.add_mermaid_diagram(..., attachment_name="diagram", 
                          insert_after_pattern="<h2>Architecture</h2>")
# → Creates: "diagram-24737279"

# Section 7 - also uses "diagram" 
helper.add_mermaid_diagram(..., attachment_name="diagram",
                          insert_after_pattern="<h2>Data Flow</h2>")
# → Creates: "diagram-a1b2c3d4"
# ✅ No conflict! Different hash for different section
```

**Disable auto-prefix if needed:**
```python
helper.add_mermaid_diagram(..., attachment_name="my-unique-name", 
                          auto_prefix=False)
```

### Rule 2: One Diagram = One Clean Upload
✅ **DO**: Delete old attempts before uploading new
```python
helper.add_mermaid_diagram(..., clean_existing=True)
```

❌ **DON'T**: Upload multiple times without cleanup
```python
# First attempt fails
upload_diagram("my-diagram")  # Creates my-diagramXYZ123

# Second attempt
upload_diagram("my-diagram")  # Creates my-diagramABC456

# Result: Orphaned attachments, 404 errors
```

### Rule 3: Use HTML Storage Format
✅ **DO**: Work with HTML when adding macros
```python
section_helper.update_section(content="<ac:structured-macro...>")
```

❌ **DON'T**: Try to use Markdown
```python
# This strips the macro
update_confluence_page(find="...", replace="```mermaid\n...\n```")
```

### Rule 4: Match Revision to Attachment Version
✅ **DO**: Keep revision parameter in sync
```html
<!-- Attachment is at version 2 -->
<ac:parameter ac:name="revision">2</ac:parameter>
```

❌ **DON'T**: Forget to update revision
```html
<!-- Attachment updated to version 2, but macro still says: -->
<ac:parameter ac:name="revision">1</ac:parameter>
<!-- Result: Shows old diagram -->
```

---

## Recommended Workflow

### For New Diagrams

**Step 1**: Create `.mmd` file locally
```bash
# docs/diagrams/my-diagram.mmd
graph TB
    A[Component A]
    B[Component B]
    A --> B
```

**Step 2**: Use helper to add
```python
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="Page Title",
    diagram_path="docs/diagrams/my-diagram.mmd",
    attachment_name="my-diagram",
    insert_after_pattern="<h2>Architecture</h2>",
    clean_existing=True
)
```

**Done!** ✅

### For Updating Existing Diagrams

**Step 1**: Edit the `.mmd` file locally

**Step 2**: Re-run helper with `clean_existing=True`
```python
# Same command as before
helper.add_mermaid_diagram(..., clean_existing=True)
```

The helper will:
1. Delete old attachment
2. Upload new version
3. Update macro revision parameter

---

## Safety Note: `clean_existing=True`

### What It Does
Deletes the attachment with the **exact same name** on the **same page** before uploading.

### With Auto-Prefix (Default)
✅ **SAFE** - Generic names are automatically made unique:
```python
# Section 3
helper.add_mermaid_diagram(..., attachment_name="diagram", clean_existing=True)
# → Creates "diagram-24737279"

# Section 7  
helper.add_mermaid_diagram(..., attachment_name="diagram", clean_existing=True)
# → Creates "diagram-a1b2c3d4"
# ✅ Different names = no conflict!
```

### Without Auto-Prefix
⚠️ **CAREFUL** when `auto_prefix=False`:
```python
# Section 3
helper.add_mermaid_diagram(..., attachment_name="diagram", 
                          clean_existing=True, auto_prefix=False)

# Section 7 - same name!
helper.add_mermaid_diagram(..., attachment_name="diagram",
                          clean_existing=True, auto_prefix=False)
# ⚠️ Deletes "diagram" from section 3!
```

### Recommendation
✅ **Use default settings** (`auto_prefix=True` + `clean_existing=True`)
- Handles generic names safely
- Cleans up old uploads automatically
- Works for teams without naming conventions

---

## When Things Go Wrong

### Symptom: "404 - Could not load diagram"

**Quick Fix (Clean Slate):**
```python
from scripts.confluence_section_helper import ConfluenceSectionHelper

# 1. Remove all macros from the section
helper = ConfluenceSectionHelper()
sections = helper.get_sections("131083")

# Find your section
section_content = sections[3][1]  # e.g., section 4

# Remove macros
import re
clean_content = re.sub(
    r'<ac:structured-macro ac:name="mermaid-cloud"[^>]*>.*?</ac:structured-macro>',
    '', section_content, flags=re.DOTALL
)

helper.update_section(page_id="131083", page_title="...", 
                     section_number=4, new_content=clean_content)

# 2. Re-add with helper
mermaid_helper = ConfluenceMermaidHelper()
mermaid_helper.add_mermaid_diagram(..., clean_existing=True)
```

**Why this works:**
- Removes all orphaned attachments
- Removes corrupted macros
- Fresh start = working diagram

---

## Anti-Patterns (What NOT to Do)

### ❌ Manual Upload with Random Names
```bash
# BAD: Creates random suffix
tmpfile=$(mktemp)
cat diagram.mmd > $tmpfile
curl -F "file=@$tmpfile" ...
# Result: attachment named "tmpXYZ123"
```

### ❌ Multiple Upload Attempts Without Cleanup
```python
# BAD: Trying again and again
upload_diagram("my-diagram")  # Fails
upload_diagram("my-diagram")  # Fails again
upload_diagram("my-diagram")  # Still fails
# Result: 3 orphaned attachments, still broken
```

### ❌ Copy-Paste Macro HTML
```python
# BAD: Hardcoded revision
macro = '<ac:parameter ac:name="revision">1</ac:parameter>'
# Later: attachment updates to v2, macro still says v1
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Add new diagram** | `helper.add_mermaid_diagram(..., clean_existing=True)` |
| **Update diagram** | Same as above (clean_existing handles it) |
| **Fix 404 errors** | Clean slate: remove macros → delete attachments → re-add |
| **List sections** | `helper.list_sections(page_id)` |
| **View attachments** | Check Confluence page → Tools → Attachments |

---

## Success Metrics

**Good workflow:**
- ✅ First upload works
- ✅ Diagram shows in view mode
- ✅ Edit mode shows correct source
- ✅ No orphaned attachments
- ✅ 2-3 iterations total

**Bad workflow:**
- ❌ Multiple failed uploads
- ❌ 404 errors
- ❌ Manual debugging
- ❌ 10+ iterations

---

## Key Takeaway

**Use the helper script with `clean_existing=True`**

This one parameter prevents 90% of issues by:
- Removing old attachments automatically
- Ensuring exact file names
- Setting correct revision
- Working on first try

**Don't fight Confluence quirks manually - let the helper handle it.**
