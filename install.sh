#!/usr/bin/env bash
# Install Dymola Agentic AI skills into Claude Code (macOS/Linux)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${HOME}/.claude/skills"
COPY=0
[[ "${1:-}" == "--copy" ]] && COPY=1

mkdir -p "$DEST"
items=(
  scripts
  validate-dymola
  simulate-dymola
  expose-encrypted-params
  inspect-dymosim
  tune-parameters
  diagnose-dymola
  edit-modelica-dymola
  dymola-model-architecture
)

for name in "${items[@]}"; do
  src="$ROOT/$name"
  dst="$DEST/$name"
  [[ -e "$src" ]] || { echo "Missing $src — skip"; continue; }
  rm -rf "$dst"
  if [[ "$COPY" -eq 1 ]]; then
    cp -R "$src" "$dst"
    echo "Copied $name"
  else
    ln -s "$src" "$dst"
    echo "Linked $name"
  fi
done

echo
echo "Done. Start a new Claude Code session and ask it to list Dymola skills."
