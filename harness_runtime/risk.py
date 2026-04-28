import fnmatch
from pathlib import Path

import yaml

RISK_PRIORITY = {"infra": 4, "core": 3, "branch": 2, "leaf": 1}

PATTERNS = {
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
    ],
    "leaf": [
        "docs/*", "*.md", "*.txt",
        "tests/*",
        "scripts/*",
        "templates/*",
    ],
}


def load_policy(policy_path: Path | None = None) -> dict:
    if policy_path and policy_path.exists():
        with open(policy_path) as f:
            return yaml.safe_load(f)
    return {}


def classify_file(filepath: str) -> str:
    for risk_level in ("infra", "core", "leaf", "branch"):
        for pattern in PATTERNS[risk_level]:
            if fnmatch.fnmatch(filepath, pattern):
                return risk_level
    return "branch"


def classify_files(files: list[str]) -> tuple[str, list[tuple[str, str]]]:
    results = []
    max_risk = "leaf"
    for f in files:
        risk = classify_file(f)
        results.append((f, risk))
        if RISK_PRIORITY[risk] > RISK_PRIORITY[max_risk]:
            max_risk = risk
    return max_risk, results


def get_gates(risk_level: str, policy_path: Path | None = None) -> list[str]:
    default_gates = {
        "leaf": ["lint", "unit_test"],
        "branch": ["spec", "plan", "tests", "review_agent"],
        "core": ["human_spec_review", "architecture_review", "rollback_plan", "security_review"],
        "infra": ["dry_run", "explicit_human_approval", "rollback_plan", "security_review"],
    }
    policy = load_policy(policy_path)
    if policy and "risk_gate_map" in policy:
        return policy["risk_gate_map"].get(risk_level, default_gates.get(risk_level, []))
    return default_gates.get(risk_level, [])
