#!/usr/bin/env bash
set -euo pipefail

ERRORS=0

validate_plugin() {
  local plugin_dir="$1"
  local plugin_name
  plugin_name=$(basename "$plugin_dir")

  echo "Validating $plugin_name..."

  local json_file="$plugin_dir/.claude-plugin/plugin.json"
  if [[ ! -f "$json_file" ]]; then
    echo "  ERROR: Missing .claude-plugin/plugin.json"
    ERRORS=$((ERRORS + 1))
    return
  fi

  for field in name description author; do
    if ! jq -e ".$field" "$json_file" > /dev/null 2>&1; then
      echo "  ERROR: plugin.json missing required field: $field"
      ERRORS=$((ERRORS + 1))
    fi
  done

  if [[ ! -f "$plugin_dir/README.md" ]]; then
    echo "  ERROR: Missing README.md"
    ERRORS=$((ERRORS + 1))
  fi

  local skill_found=0
  if [[ -d "$plugin_dir/skills" ]]; then
    for skill_dir in "$plugin_dir/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      local skill_md="$skill_dir/SKILL.md"
      if [[ -f "$skill_md" ]]; then
        skill_found=1
        for field in name description; do
          if ! grep -q "^$field:" "$skill_md"; then
            echo "  ERROR: $(basename "$skill_dir")/SKILL.md missing frontmatter field: $field"
            ERRORS=$((ERRORS + 1))
          fi
        done
      fi
    done
  fi

  if [[ $skill_found -eq 0 ]]; then
    echo "  ERROR: No SKILL.md found in any skills/ subdirectory"
    ERRORS=$((ERRORS + 1))
  fi
}

plugin_count=0
for base_dir in plugins external_plugins; do
  [[ -d "$base_dir" ]] || continue
  for plugin_dir in "$base_dir"/*/; do
    [[ -d "$plugin_dir" ]] || continue
    validate_plugin "$plugin_dir"
    plugin_count=$((plugin_count + 1))
  done
done

echo ""
if [[ $ERRORS -gt 0 ]]; then
  echo "Validation failed with $ERRORS error(s) across $plugin_count plugin(s)."
  exit 1
else
  echo "All $plugin_count plugin(s) valid."
fi
