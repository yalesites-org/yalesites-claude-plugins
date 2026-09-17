#!/usr/bin/env bash
#
# Sync the canonical writing standards in standards/ into each consuming plugin.
#
# Claude Code plugins cannot read each other's files, so every plugin has to carry
# its own copy. The copies are generated, never hand-edited: edit standards/ and
# re-run this script. validate-plugins.sh fails the build if a copy drifts.
#
#   bash scripts/sync-standards.sh           # write the copies
#   bash scripts/sync-standards.sh --check   # verify only, non-zero on drift
#
set -euo pipefail

cd "$(dirname "$0")/.."

CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

# Each target is the skill directory that hosts the shared files for its plugin.
TARGETS=(
  "plugins/yalesites-dev/skills/yalesites-pr"
  "plugins/yalesites-product/skills/ticket"
  "plugins/yalesites-security/skills/supply-chain-audit"
)

DOCS=(
  "github-communication-format.md"
  "github-writing.md"
)

SCRIPTS=(
  "check-github-text.py"
)

DRIFT=0

sync_one() {
  local src="$1" dest="$2"
  if [[ $CHECK -eq 1 ]]; then
    if [[ ! -f "$dest" ]]; then
      echo "  MISSING: $dest"
      DRIFT=$((DRIFT + 1))
    elif ! cmp -s "$src" "$dest"; then
      echo "  DRIFT:   $dest"
      DRIFT=$((DRIFT + 1))
    fi
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "  wrote $dest"
  fi
}

for target in "${TARGETS[@]}"; do
  if [[ $CHECK -eq 0 ]]; then
    echo "$target"
  fi
  for doc in "${DOCS[@]}"; do
    sync_one "standards/$doc" "$target/references/$doc"
  done
  for script in "${SCRIPTS[@]}"; do
    sync_one "standards/$script" "$target/scripts/$script"
    [[ $CHECK -eq 0 ]] && chmod +x "$target/scripts/$script"
  done
done

if [[ $CHECK -eq 1 ]]; then
  if [[ $DRIFT -gt 0 ]]; then
    echo ""
    echo "$DRIFT synced file(s) out of date with standards/."
    echo "Run: bash scripts/sync-standards.sh"
    exit 1
  fi
  echo "Standards in sync."
else
  echo ""
  echo "Synced $(( ${#TARGETS[@]} * (${#DOCS[@]} + ${#SCRIPTS[@]}) )) file(s) from standards/."
fi
