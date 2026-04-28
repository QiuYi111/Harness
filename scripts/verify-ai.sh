#!/usr/bin/env bash
# verify-ai.sh — Harness v2 Template Integrity Verification
# Checks that all required templates exist and are properly configured.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$REPO_ROOT/templates"

passed=0
failed=0
warnings=0

check_file() {
    local label="$1"
    local path="$2"
    local required="${3:-true}"

    if [ -f "$path" ]; then
        echo "✅ $label exists"
        passed=$((passed + 1))
    elif [ "$required" = "true" ]; then
        echo "❌ $label MISSING: $path"
        failed=$((failed + 1))
    else
        echo "⚠️  $label not found (optional): $path"
        warnings=$((warnings + 1))
    fi
}

check_no_pattern() {
    local label="$1"
    local pattern="$2"
    local dir="$3"
    local required="${4:-true}"

    local matches
    matches=$(grep -rl "$pattern" "$dir" --include="*.md" 2>/dev/null || true)

    if [ -z "$matches" ]; then
        echo "✅ $label: clean"
        passed=$((passed + 1))
    elif [ "$required" = "true" ]; then
        echo "❌ $label found in:"
        echo "$matches" | sed 's/^/   /'
        failed=$((failed + 1))
    else
        echo "⚠️  $label found in some files"
        warnings=$((warnings + 1))
    fi
}

echo "=== Harness v2 AI Verification ==="
echo "Checking template integrity..."
echo ""

# --- Required template files ---
echo "--- Required Templates ---"
check_file "AGENTS.md" "$TEMPLATES_DIR/AGENTS.md"
check_file "CLAUDE.md" "$TEMPLATES_DIR/CLAUDE.md"
check_file "PRD_TEMPLATE.md" "$TEMPLATES_DIR/PRD_TEMPLATE.md"
check_file "SPEC_TEMPLATE.md" "$TEMPLATES_DIR/SPEC_TEMPLATE.md"
check_file "PLAN_TEMPLATE.md" "$TEMPLATES_DIR/PLAN_TEMPLATE.md"
check_file "TASKS_TEMPLATE.md" "$TEMPLATES_DIR/TASKS_TEMPLATE.md"
check_file "BLAST_RADIUS_POLICY.md" "$TEMPLATES_DIR/BLAST_RADIUS_POLICY.md"
check_file "ROLE_POLICY.md" "$TEMPLATES_DIR/ROLE_POLICY.md"
check_file "EVAL_TEMPLATE.md" "$TEMPLATES_DIR/EVAL_TEMPLATE.md"
check_file "REPORT_TEMPLATE.md" "$TEMPLATES_DIR/REPORT_TEMPLATE.md"
echo ""

# --- Content checks ---
echo "--- Content Checks ---"

# CLAUDE.md line count
claude_lines=$(wc -l < "$TEMPLATES_DIR/CLAUDE.md" 2>/dev/null || echo "999")
if [ "$claude_lines" -le 200 ]; then
    echo "✅ CLAUDE.md is $claude_lines lines (≤ 200)"
    passed=$((passed + 1))
else
    echo "❌ CLAUDE.md is $claude_lines lines (exceeds 200 limit)"
    failed=$((failed + 1))
fi

check_no_pattern "Neural-Grid references" "Neural-Grid" "$TEMPLATES_DIR"
check_no_pattern "TODO in templates" "TODO" "$TEMPLATES_DIR"
echo ""

# --- Optional checks ---
echo "--- Optional Templates ---"
check_file "QUICKSTART_TEMPLATE.md" "$TEMPLATES_DIR/QUICKSTART_TEMPLATE.md" false
check_file "CONTRACT_TEMPLATE.md" "$TEMPLATES_DIR/CONTRACT_TEMPLATE.md" false
check_file "DATA_MODEL_TEMPLATE.md" "$TEMPLATES_DIR/DATA_MODEL_TEMPLATE.md" false
check_file "CONSTITUTION_TEMPLATE.md" "$TEMPLATES_DIR/CONSTITUTION_TEMPLATE.md" false
check_file "Makefile" "$TEMPLATES_DIR/Makefile" false
check_file ".pre-commit-config.yaml" "$TEMPLATES_DIR/.pre-commit-config.yaml" false
echo ""

# --- Spec directory check (optional) ---
echo "--- Spec Directory ---"
if [ -d "$REPO_ROOT/specs" ]; then
    for feature_dir in "$REPO_ROOT/specs"/*/; do
        if [ -d "$feature_dir" ]; then
            fname=$(basename "$feature_dir")
            missing=""
            for artifact in spec.md plan.md tasks.md eval.md report.md; do
                if [ ! -f "$feature_dir$artifact" ]; then
                    missing="$missing $artifact"
                fi
            done
            if [ -z "$missing" ]; then
                echo "✅ specs/$fname has all required artifacts"
                passed=$((passed + 1))
            else
                echo "⚠️  specs/$fname missing:$missing"
                warnings=$((warnings + 1))
            fi
        fi
    done
else
    echo "⚠️  No specs/ directory found (optional at template-level)"
    warnings=$((warnings + 1))
fi
echo ""

# --- Summary ---
echo "=== Summary ==="
echo "✅ $passed passed"
echo "❌ $failed failed"
echo "⚠️  $warnings warnings"
echo ""

if [ "$failed" -eq 0 ]; then
    echo "🎉 All required checks passed."
    exit 0
else
    echo "🚨 $failed required check(s) failed. Fix before committing."
    exit 1
fi
