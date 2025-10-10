#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$REPO_ROOT/.warp-cli.config" ]; then
  echo "Missing .warp-cli.config in repo root" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "$REPO_ROOT/.warp-cli.config"

if [ -z "${PROFILE_ID:-}" ]; then
  echo "PROFILE_ID not set in .warp-cli.config" >&2
  exit 1
fi

# Build common args
ARGS=(agent run --profile "$PROFILE_ID")

# Pass through extra args to warp agent run
# Usage: warp-run.sh --cwd <dir> --prompt "..." [--mcp-server <id> ...]

# Optionally add MCP servers if enabled
if [[ "${ENABLE_MCP:-false}" == "true" && -n "${MCP_SERVER_IDS:-}" ]]; then
  IFS=',' read -ra IDS <<< "$MCP_SERVER_IDS"
  for id in "${IDS[@]}"; do
    id_tr=$(echo "$id" | xargs)
    [[ -n "$id_tr" ]] && ARGS+=(--mcp-server "$id_tr")
  done
fi

# Exec warp with the provided args
exec warp "${ARGS[@]}" "$@"
