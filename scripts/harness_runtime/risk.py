import fnmatch
from pathlib import Path

import yaml

RISK_PRIORITY = {"infra": 4, "core": 3, "branch": 2, "leaf": 1}

_DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent.parent / "references" / "policies" / "blast-radius.yaml"


def load_blast_policy(path: Path | None = None) -> dict:
    """Load blast-radius.yaml. Returns risk_levels dict or falls back to built-in."""
    p = path or _DEFAULT_POLICY_PATH
    if p.exists():
        with open(p) as f:
            return yaml.safe_load(f)
    return {}


def _get_patterns(policy: dict) -> dict[str, list[str]]:
    """Extract flat pattern lists per risk level from policy file."""
    levels = policy.get("risk_levels", {})
    result = {}
    for level, spec in levels.items():
        patterns = []
        for group in spec.get("pattern_groups", []):
            patterns.extend(group.get("patterns", []))
        result[level] = patterns
    return result


def classify_file(filepath: str, policy: dict | None = None) -> tuple[str, str | None]:
    """Classify one file path. Returns (risk_level, matched_pattern_or_None)."""
    if policy is None:
        policy = load_blast_policy()
    patterns = _get_patterns(policy) if policy else _BUILTIN_PATTERNS

    for level in ("infra", "core", "branch", "leaf"):
        for pat in patterns.get(level, []):
            if fnmatch.fnmatch(filepath, pat):
                return level, pat

    return "branch", None


def classify_files(files: list[str], policy: dict | None = None) -> tuple[str, list[tuple[str, str, str | None]]]:
    """Classify multiple files. Returns (max_risk, [(filepath, risk, matched_pattern)])."""
    if policy is None:
        policy = load_blast_policy()

    results = []
    max_risk = "leaf"
    for f in files:
        risk, pat = classify_file(f, policy)
        results.append((f, risk, pat))
        if RISK_PRIORITY.get(risk, 0) > RISK_PRIORITY.get(max_risk, 0):
            max_risk = risk
    return max_risk, results


def get_gates(risk_level: str, policy: dict | None = None) -> list[str]:
    """Get required gates for a risk level from blast-radius.yaml."""
    if policy is None:
        policy = load_blast_policy()

    levels = policy.get("risk_levels", {})
    if risk_level in levels:
        return levels[risk_level].get("required_gates", [])

    _fallback = {
        "leaf": ["lint", "unit_test"],
        "branch": ["spec", "plan", "tests", "review_agent"],
        "core": ["human_spec_review", "architecture_review", "rollback_plan", "security_review"],
        "infra": ["dry_run", "explicit_human_approval", "rollback_plan", "security_review"],
    }
    return _fallback.get(risk_level, [])


_BUILTIN_PATTERNS = {
    "infra": [
        ".github/*", ".gitlab-ci.yml", "Jenkinsfile",
        "Dockerfile*", "docker-compose*",
        "*.env*",
        "terraform/*",
        "migrations/*", "db/*",
    ],
    "core": [
        "*auth*", "*permission*", "*rbac*",
        "*migration*", "*schema*",
        "internal/domain/*",
    ],
    "branch": [
        "internal/infrastructure/*",
        "cmd/*",
        "api/*",
        "src/*",
        "app/*",
        "lib/*",
        "packages/*",
    ],
    "leaf": [
        "docs/*", "*.md", "*.txt",
        "tests/*",
        "scripts/*",
        "templates/*",
    ],
}
