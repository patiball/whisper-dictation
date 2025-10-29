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

### Rule 1: File Names Must Be Exact
✅ **DO**: Use exact names without extensions
```python
attachment_name="system-overview"  # Correct
```

❌ **DON'T**: Include extensions or allow random suffixes
```python
attachment_name="system-overview.mmd"  # Wrong - causes 404
# or
temp_file = tempfile.NamedTemporaryFile(prefix="system-overview")  # Wrong - adds random suffix
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
