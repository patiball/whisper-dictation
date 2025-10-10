#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Ensure dirs
mkdir -p docs/diagrams docs/context

# Short prompt for high-level audit
read -r -d '' PROMPT << 'PROMPT_EOF'
Przeanalizuj aktualny kod tego repozytorium (wysoki poziom) i wygeneruj tylko dwa artefakty:
1) docs/PROJECT_OVERVIEW.md – zawiera:
   - Cel aplikacji i główne funkcjonalności
   - Stos technologiczny (języki, frameworki, zależności) wykryte z kodu
   - Uproszczoną strukturę folderów (tylko główne katalogi i entry points)
   - Sekcję "[TO INVESTIGATE]" dla elementów niejednoznacznych
   - Sekcję "Powiązane dokumenty" z linkami do: docs/README.md i docs/diagrams/system-overview.mmd
   - Krótką sekcję "Następne kroki" (co rozszerzyć w pełnej dokumentacji)

2) docs/diagrams/system-overview.mmd – Mermaid diagram high-level głównych komponentów i relacji.

WAŻNE:
- Nie twórz innych plików poza wymienionymi.
- Opisy w języku polskim, bazuj na faktycznym kodzie repo (nie wymyślaj).
- Zapewnij spójność linków (coherent docs) – używaj ścieżek względnych.
PROMPT_EOF

# Run warp agent via wrapper
"$SCRIPT_DIR/warp-run.sh" --cwd "$REPO_ROOT" --prompt "$PROMPT" || {
  echo "warp agent run failed" >&2
  exit 1
}

# Post-process: ensure basic related-docs footer exists
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

echo "MVP documentation generated successfully."
