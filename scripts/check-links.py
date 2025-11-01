import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1]
readme = root / "docs" / "README.md"
missing = []
if not readme.exists():
    print("docs/README.md missing", file=sys.stderr)
    sys.exit(1)
content = readme.read_text(encoding="utf-8")
for rel in ["./PROJECT_OVERVIEW.md", "./diagrams/system-overview.mmd"]:
    p = (readme.parent / rel).resolve()
    if not p.exists():
        missing.append(rel)
if missing:
    print("Broken links in docs/README.md:")
    for m in missing:
        print(" -", m)
    sys.exit(2)
print("Links OK")
