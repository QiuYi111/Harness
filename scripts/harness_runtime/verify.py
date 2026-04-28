import re
import yaml
from pathlib import Path

SKILL_BUCKETS = []
SKILLS_ROOT = "harness"
SPEC_ARTIFACTS = ["spec.md", "plan.md", "tasks.md", "eval.md", "report.md"]
FORBIDDEN_PATTERNS = ["Neural-Grid", "TODO"]
SUPPORTING_TEMPLATES = [
    "ARCHITECTURE.md", "CONSTITUTION_TEMPLATE.md", "CONTRACT_TEMPLATE.md",
    "CONTRIBUTING.md", "DATA_MODEL_TEMPLATE.md", "Makefile", "QUICKSTART_TEMPLATE.md",
]
MAX_DESCRIPTION_LEN = 1024


def _check(label: str, ok: bool, detail: str, fail_hard: bool = True) -> tuple[str, str, str]:
    if ok:
        return "pass", label, detail
    return "fail" if fail_hard else "warn", label, detail


def verify_skills(skills_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    if not skills_dir.is_dir():
        results.append(("warn", "subskills/", "directory not found"))
        return results

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            results.append(("fail", f"subskills/{skill_name}", "SKILL.md missing"))
            continue

        frontmatter = _parse_frontmatter(skill_md)
        label = f"subskills/{skill_name}"

        if "name" not in frontmatter:
            results.append(("fail", label, "frontmatter missing 'name'"))
        else:
            results.append(("pass", label, f"name={frontmatter['name']}"))

        if "description" not in frontmatter:
            results.append(("fail", label, "frontmatter missing 'description'"))
        elif len(frontmatter["description"]) > MAX_DESCRIPTION_LEN:
            results.append(("fail", label,
                f"description too long ({len(frontmatter['description'])} > {MAX_DESCRIPTION_LEN})"))
        else:
            results.append(("pass", label, f"description ok ({len(frontmatter['description'])} chars)"))

    return results


def verify_plugin_registry(plugin_path: Path, skills_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    if not plugin_path.exists():
        results.append(("fail", "plugin.json", "not found"))
        return results

    try:
        data = yaml.safe_load(plugin_path.read_text()) or {}
    except yaml.YAMLError:
        results.append(("fail", "plugin.json", "invalid YAML"))
        return results

    skills = data.get("skills", [])
    if not skills:
        results.append(("warn", "plugin.json", "no skills registered"))
        return results

    if isinstance(skills, dict):
        for skill_name, skill_conf in skills.items():
            path_str = skill_conf.get("path", "")
            skill_path = plugin_path.parent / path_str if path_str else None
            if not path_str:
                results.append(("fail", f"plugin/{skill_name}", "missing 'path' field"))
            elif skill_path and skill_path.exists():
                results.append(("pass", f"plugin/{skill_name}", str(path_str)))
            else:
                results.append(("fail", f"plugin/{skill_name}", f"path not found: {path_str}"))
    else:
        repo_root = plugin_path.parent.parent
        for i, path_str in enumerate(skills):
            skill_path = repo_root / path_str
            name = path_str.rsplit("/", 1)[-1] if "/" in path_str else "harness"
            if skill_path.exists():
                results.append(("pass", f"plugin/{name}", str(path_str)))
            else:
                results.append(("fail", f"plugin/{name}", f"path not found: {path_str}"))

    return results


def verify_policies(policies_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    for name in ["blast-radius.yaml", "gates.yaml", "project_index.yaml"]:
        path = policies_dir / name
        if not path.exists():
            results.append(("fail", f"policies/{name}", "missing"))
            continue
        try:
            yaml.safe_load(path.read_text())
            results.append(("pass", f"policies/{name}", "parses ok"))
        except yaml.YAMLError as e:
            results.append(("fail", f"policies/{name}", f"YAML error: {e}"))
    return results


def verify_templates(templates_dir: Path) -> list[tuple[str, str, str]]:
    results = []
    for name in SUPPORTING_TEMPLATES:
        path = templates_dir / name
        results.append(_check(f"templates/{name}", path.exists(), str(path) if path.exists() else "MISSING"))
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


def verify_no_stale_v2(templates_dir: Path, root_dir: Path) -> list[tuple[str, str, str]]:
    stale_names = [
        "BLAST_RADIUS_POLICY.md", "ROLE_POLICY.md",
        "PRD_TEMPLATE.md", "SPEC_TEMPLATE.md",
        "PLAN_TEMPLATE.md", "TASKS_TEMPLATE.md",
        "EVAL_TEMPLATE.md", "REPORT_TEMPLATE.md",
    ]
    results = []
    for name in stale_names:
        path = root_dir / name
        if path.exists():
            results.append(("warn", f"stale v2 template: {name}",
                "remove or migrate to resources/templates/"))
    return results


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


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def run_full_verify(skills_dir: Path, plugin_path: Path, policies_dir: Path,
                    templates_dir: Path, specs_dir: Path, project_root: Path) -> dict:
    all_results = []
    all_results.extend(verify_skills(skills_dir))
    all_results.extend(verify_plugin_registry(plugin_path, skills_dir))
    all_results.extend(verify_policies(policies_dir))
    all_results.extend(verify_templates(templates_dir))
    all_results.extend(verify_specs(specs_dir))
    all_results.extend(verify_no_stale_v2(templates_dir, project_root))

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
