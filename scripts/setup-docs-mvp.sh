#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Ensure dirs
mkdir -p docs/diagrams docs/context

ABS_OVERVIEW="$REPO_ROOT/docs/PROJECT_OVERVIEW.md"
ABS_DIAGRAM="$REPO_ROOT/docs/diagrams/system-overview.mmd"

# Short prompt for high-level audit with absolute paths to avoid agent cwd issues
read -r -d '' PROMPT << PROMPT_EOF
Pracuj w kontekście projektu pod ścieżką: $REPO_ROOT
Utwórz DOKŁADNIE dwa artefakty pod poniższymi ŚCIEŻKAMI BEZWZGLĘDNYMI (nie używaj innej lokalizacji):
1) $ABS_OVERVIEW – plik Markdown o treści:
# Przegląd (MVP)
To jest test wygenerowany przez Warp CLI w trybie MVP. 
Dodaj sekcje: Cel aplikacji (2-3 zdania), Stos technologiczny (wypunktowanie, high-level), Struktura folderów (główne katalogi).
Na końcu dodaj sekcję "Powiązane dokumenty" z linkami względnymi do: ./README.md oraz ./diagrams/system-overview.mmd

2) $ABS_DIAGRAM – plik Mermaid z prostym diagramem high-level np.:
flowchart TD
  A[UI] --> B[Whisper Engine]
  B --> C[Transkrypcja]

WAŻNE:
- Zapisz pliki dokładnie pod powyższymi ścieżkami bezwzględnymi.
- Nie twórz innych plików ani katalogów.
- Opisy po polsku, tylko high-level (MVP), bez nadmiarowych sekcji.
PROMPT_EOF

# Run warp agent via wrapper (include explicit --cwd)
"$SCRIPT_DIR/warp-run.sh" --cwd "$REPO_ROOT" --prompt "$PROMPT" || {
  echo "warp agent run failed" >&2
  exit 1
}

# Post-process: ensure basic related-docs footer exists (idempotent)
ensure_footer() {
  local file="$1"
  local footer="\n---\nPowiązane dokumenty:\n- [README](./README.md)\n- [Diagram systemowy](./diagrams/system-overview.mmd)\n"
  if [ -f "$file" ]; then
    if ! grep -q "Powiązane dokumenty" "$file"; then
      printf "%b" "$footer" >> "$file"
    fi
  fi
}

ensure_footer "docs/PROJECT_OVERVIEW.md"

# Validation: check files exist and links from README
missing=()
for f in docs/PROJECT_OVERVIEW.md docs/diagrams/system-overview.mmd; do
  [ -f "$f" ] || missing+=("$f")
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "Brakujące pliki:" >&2
  printf ' - %s\n' "${missing[@]}" >&2
  exit 2
fi

python3 "$SCRIPT_DIR/check-links.py" || true

echo "MVP documentation generated successfully."
