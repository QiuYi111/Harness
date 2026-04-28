#!/usr/bin/env bash
# link-skills.sh — Install Harness skills into agent skill directories
# Adapted from mattpocock/skills installer pattern
#
# Usage:
#   ./scripts/link-skills.sh [agent] [target-dir]
#
# Agents: claude-code, codex, cursor, windsurf
# Default: claude-code (~/.claude/skills/)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$HARNESS_ROOT"

AGENT="${1:-claude-code}"
TARGET_DIR="${2:-}"

# Determine target directory based on agent
case "$AGENT" in
  claude-code)
    TARGET_DIR="${TARGET_DIR:-$HOME/.claude/skills/harness}"
    ;;
  codex)
    TARGET_DIR="${TARGET_DIR:-$HOME/.codex/skills/harness}"
    ;;
  cursor)
    TARGET_DIR="${TARGET_DIR:-$HOME/.cursor/skills/harness}"
    ;;
  windsurf)
    TARGET_DIR="${TARGET_DIR:-$HOME/.windsurf/skills/harness}"
    ;;
  *)
    echo "Unknown agent: $AGENT"
    echo "Supported: claude-code, codex, cursor, windsurf"
    exit 1
    ;;
esac

echo "Installing Harness skills for $AGENT..."
echo "  Source: $SOURCE_DIR"
echo "  Target: $TARGET_DIR"

if [ -e "$TARGET_DIR" ]; then
  if [ -L "$TARGET_DIR" ]; then
    rm "$TARGET_DIR"
    echo "  ↻ Replacing existing symlink"
  elif [ -d "$TARGET_DIR" ]; then
    echo "  ⚠ Target exists as directory. Remove manually: $TARGET_DIR"
    exit 1
  fi
fi

mkdir -p "$(dirname "$TARGET_DIR")"
ln -s "$SOURCE_DIR" "$TARGET_DIR"
echo "  ✓ Linked: harness (root skill + subskills)"

linked=1
skipped=0

echo ""
echo "Done. Linked $linked skill, skipped $skipped."
echo ""

if [ "$AGENT" = "claude-code" ]; then
  plugin_target="$HOME/.claude-plugin"
  mkdir -p "$plugin_target"
  if [ -f "$plugin_target/plugin.json" ]; then
    echo "⚠ ~/.claude-plugin/plugin.json already exists."
    echo "  Add this manually:"
    echo "  {\"name\":\"harness\", \"skills\":[\"$SOURCE_DIR\"]}"
  else
    cat > "$plugin_target/plugin.json" <<PLUGINEOF
{
  "name": "harness",
  "description": "Cache-friendly engineering governance for AI coding agents.",
  "skills": ["$SOURCE_DIR"]
}
PLUGINEOF
    echo "✓ Wrote ~/.claude-plugin/plugin.json with absolute path"
  fi
fi

echo ""
echo "Harness installed. Your agent now loads one skill: harness"
echo "The router inside detects phases and loads subskills on demand."
