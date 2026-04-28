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

# Also copy .claude-plugin if installing for Claude Code
if [ "$AGENT" = "claude-code" ]; then
  plugin_src="$HARNESS_ROOT/.claude-plugin/plugin.json"
  if [ -f "$plugin_src" ]; then
    plugin_target="$HOME/.claude-plugin"
    mkdir -p "$plugin_target"
    if [ -f "$plugin_target/plugin.json" ]; then
      echo "⚠ ~/.claude-plugin/plugin.json already exists — not overwriting."
      echo "  Merge harness skills into your existing plugin.json manually."
    else
      cp "$plugin_src" "$plugin_target/plugin.json"
      echo "✓ Copied .claude-plugin/plugin.json"
    fi
  fi
fi

echo ""
echo "Skills installed. Agents can now invoke Harness skills by name."
echo "Available skills:"
echo "  harness-specify, harness-plan, harness-tasks, harness-tdd"
echo "  harness-risk, harness-eval, harness-report, harness-context"
echo "  harness-domain-language, harness-grill, harness-architecture-review"
echo "  harness-init"
