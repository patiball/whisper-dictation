# Lessons Learned - Index

This directory contains lessons learned from working with various tools and workflows in the Metal Scribe project.

## Available Documents

### 1. [Confluence Mermaid Best Practices](confluence_mermaid_best_practices.md) ⭐
**Focus**: How to add Mermaid diagrams correctly the first time

**Key Principles**:
- Use the helper script with `clean_existing=True`
- Exact file names (no extensions, no random suffixes)
- One diagram = one clean upload
- HTML storage format only

**When to read**: Before adding Mermaid diagrams (prevents issues)

### 1a. [Confluence Mermaid Diagrams - Troubleshooting](confluence_mermaid_diagrams.md)
**Focus**: Detailed technical reference and troubleshooting

**Contents**:
- Step-by-step manual process
- 6 common pitfalls with fixes
- API reference and parameters

**When to read**: When debugging issues or working without helper

---

### 2. [Confluence Workflow Optimization](confluence_workflow_optimization.md)
**Focus**: Token-efficient workflows for large Confluence pages

**Key Learnings**:
- Use MCP tools for Markdown content (80% token savings)
- Use REST API with targeted string replacement for macros
- Minimize page fetches and reconstructions
- Helper script: `scripts/confluence_mermaid_helper.py`

**When to read**: Before making multiple updates to Confluence pages

**Token Savings**: 80-83% reduction for diagram operations

---

### 3. [macOS Dictate Recommendations](recommendations_from_macos_dictate.md)
**Focus**: Insights from macOS dictate implementation

**Key Learnings**:
- (Add summary when viewing this file)

---

### 4. [Code Review Summary (Pre-Merge)](code_review_summary.md)
**Focus**: Analysis of changes made after a long break from coding.

**Key Learnings**:
- Overly broad exception handling can hide bugs.
- Increased global state makes code harder to test.
- Inconsistent standards (e.g., comments in multiple languages) hurt maintainability.

**When to read**: Before a major merge, especially after time away from a project.

---

## Quick Reference

### Updating a Confluence Section (Recommended) ⭐

```bash
# Set environment variables
export CONFLUENCE_API_TOKEN="your-token"
export CONFLUENCE_USERNAME="your-email"
export CONFLUENCE_URL="https://your-site.atlassian.net/wiki"

# List sections to find what you need
python3 scripts/confluence_section_helper.py list 131083

# Update by section title (easiest)
python3 -c "
from scripts.confluence_section_helper import ConfluenceSectionHelper
helper = ConfluenceSectionHelper()
helper.update_section_by_title(
    '131083', 'Page Title', 'Next Priorities',
    '<p>New content here</p>'
)
"
```

### Adding a Mermaid Diagram

```bash
# Use helper script
python3 scripts/confluence_mermaid_helper.py \
    131083 \
    "Metal Scribe — Start Page" \
    docs/diagrams/my-diagram.mmd \
    my-diagram \
    "<h2>Section Title</h2>"
```

### Common Confluence Issues

| Problem | Document | Section |
|---------|----------|---------|
| Diagram shows 404 in editor | confluence_mermaid_diagrams.md | Pitfall 1 |
| All diagrams show same source | confluence_mermaid_diagrams.md | Pitfall 5 |
| Running out of tokens | confluence_workflow_optimization.md | Token Usage |
| Macro gets stripped | confluence_mermaid_diagrams.md | Pitfall 3 |

---

## Contributing

When adding new lessons learned:

1. **Create a new .md file** in this directory
2. **Use the template structure**:
   - Context (date, project, what triggered this)
   - The Problem
   - The Solution
   - Key Learnings
   - Common Pitfalls
   - Examples
3. **Update this README.md** with a summary
4. **Link from relevant project docs** if applicable

---

## Maintenance

These documents should be:
- ✅ Updated when new patterns emerge
- ✅ Referenced in ADRs when making related decisions
- ✅ Used as onboarding material for new contributors
- ✅ Consulted before similar work

Last updated: 2025-10-28
