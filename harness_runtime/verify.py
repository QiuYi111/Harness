import re
from pathlib import Path

REQUIRED_TEMPLATES = [
    "AGENTS.md", "CLAUDE.md",
    "PRD_TEMPLATE.md", "SPEC_TEMPLATE.md", "PLAN_TEMPLATE.md",
    "TASKS_TEMPLATE.md", "BLAST_RADIUS_POLICY.md", "ROLE_POLICY.md",
    "EVAL_TEMPLATE.md", "REPORT_TEMPLATE.md",
]

OPTIONAL_TEMPLATES = [
    "QUICKSTART_TEMPLATE.md", "CONTRACT_TEMPLATE.md",
    "DATA_MODEL_TEMPLATE.md", "CONSTITUTION_TEMPLATE.md",
    "Makefile", ".pre-commit-config.yaml",
]

SPEC_ARTIFACTS = ["spec.md", "plan.md", "tasks.md", "eval.md", "report.md"]

FORBIDDEN_PATTERNS = ["Neural-Grid", "TODO"]


def check_file(label: str, path: Path, required: bool = True) -> tuple[str, str, str]:
    if path.exists():
        return "pass", label, str(path)
    if required:
        return "fail", label, f"MISSING: {path}"
    return "warn", label, f"not found (optional): {path}"


def check_no_pattern(label: str, pattern: str, directory: Path) -> tuple[str, str, str]:
    if not directory.exists():
        return "warn", label, f"directory not found: {directory}"
    matches = []
    for f in directory.rglob("*.md"):
        if pattern in f.read_text(errors="replace"):
            matches.append(str(f.relative_to(directory)))
    if not matches:
        return "pass", label, "clean"
    joined = ", ".join(matches[:5])
    return "fail", label, f"pattern '{pattern}' found in: {joined}"


def check_role_boundaries(changed_files: list[str], role: str = "") -> list[tuple[str, str, str]]:
    boundaries = {
        "TDD-RED": {"allowed": ["tests/", "specs/"], "forbidden": ["internal/", "cmd/", "pkg/"]},
        "TDD-GREEN": {"allowed": ["internal/", "cmd/"], "forbidden": ["tests/"]},
        "TDD-REFACTOR": {"allowed": ["internal/", "cmd/", "pkg/"], "forbidden": ["tests/"]},
        "REVIEWER": {"allowed": ["docs/reports/", "specs/"], "forbidden": ["internal/", "tests/"]},
    }
    results = []
    if not role or role not in boundaries:
        return results
    b = boundaries[role]
    for f in changed_files:
        in_allowed = any(f.startswith(p) for p in b["allowed"])
        in_forbidden = any(f.startswith(p) for p in b["forbidden"])
        if in_forbidden and not in_allowed:
            results.append(("fail", f"role boundary violation ({role})", f))
    return results


def verify_templates(templates_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    for t in REQUIRED_TEMPLATES:
        results.append(check_file(t, templates_dir / t, required=True))
    for t in OPTIONAL_TEMPLATES:
        results.append(check_file(t, templates_dir / t, required=False))
    return results


def verify_content(templates_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    for pattern in FORBIDDEN_PATTERNS:
        results.append(check_no_pattern(f"Forbidden '{pattern}'", pattern, templates_dir))

    claude_path = templates_dir / "CLAUDE.md"
    if claude_path.exists():
        lines = len(claude_path.read_text(errors="replace").splitlines())
        if lines <= 200:
            results.append(("pass", "CLAUDE.md length", f"{lines} lines (<= 200)"))
        else:
            results.append(("fail", "CLAUDE.md length", f"{lines} lines (exceeds 200)"))
    return results


def verify_specs(specs_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    if not specs_dir.exists():
        results.append(("warn", "specs/", "No specs/ directory found"))
        return results
    for feature_dir in sorted(specs_dir.iterdir()):
        if not feature_dir.is_dir():
            continue
        missing = [a for a in SPEC_ARTIFACTS if not (feature_dir / a).exists()]
        name = feature_dir.name
        if missing:
            results.append(("warn", f"specs/{name}", f"missing: {', '.join(missing)}"))
        else:
            results.append(("pass", f"specs/{name}", "all artifacts present"))
    return results


def run_full_verify(templates_dir: Path, specs_dir: Path) -> dict:
    all_results = []
    all_results.extend(verify_templates(templates_dir))
    all_results.extend(verify_content(templates_dir))
    all_results.extend(verify_specs(specs_dir))

    passed = sum(1 for r in all_results if r[0] == "pass")
    failed = sum(1 for r in all_results if r[0] == "fail")
    warnings = sum(1 for r in all_results if r[0] == "warn")

    return {
        "results": all_results,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "ok": failed == 0,
    }
