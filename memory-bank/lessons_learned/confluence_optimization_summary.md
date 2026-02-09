# Confluence Optimization - Quick Summary

**Date**: 2025-10-28  
**Achievement**: 80%+ token reduction for Confluence updates

---

## What We Built

### 1. Section-Aware Editor ⭐ (RECOMMENDED)
**Script**: `scripts/confluence_section_helper.py`

**Use when**: "Update section X with new content"

**Example**:
```python
helper.update_section_by_title(
    page_id="131083",
    page_title="My Page",
    section_title="Next Priorities",
    new_content="<p>Updated priorities</p>"
)
```

**Why it's great**:
- Only specified section is modified
- Other sections completely untouched
- Intuitive (use section titles or numbers)
- Safe and reliable

### 2. Mermaid Diagram Helper
**Script**: `scripts/confluence_mermaid_helper.py`

**Use when**: Adding Mermaid diagrams

**Example**:
```python
helper.add_mermaid_diagram(
    page_id="131083",
    page_title="My Page",
    diagram_path="diagram.mmd",
    attachment_name="diagram",
    insert_after_pattern="<h2>Section</h2>"
)
```

---

## Token Savings

| Operation | Before | After | Savings |
|-----------|--------|-------|---------|
| Update section | 15-20K | 3-5K | **80%** |
| Add diagram | 15-20K | 3-5K | **80%** |
| Add 3 diagrams | 60K | 10K | **83%** |

---

## Quick Decision Guide

**"Update section X"** → Use `confluence_section_helper.py` ⭐  
**"Add Mermaid diagram"** → Use `confluence_mermaid_helper.py`  
**"Simple text update"** → Use MCP `update_confluence_page`

---

## Full Documentation

See: `memory-bank/lessons_learned/confluence_workflow_optimization.md`
