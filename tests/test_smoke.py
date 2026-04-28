"""Smoke tests — verifies CLI is importable and all commands register."""
import subprocess
import sys
from pathlib import Path


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "harness_runtime.cli", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "harness" in result.stdout


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "harness_runtime.cli", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "3.0.0" in result.stdout


def test_cli_subcommands():
    result = subprocess.run(
        [sys.executable, "-m", "harness_runtime.cli", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    expected_commands = [
        "init", "install-skills", "specify",
        "classify-risk", "verify-ai", "eval",
        "context", "report", "status",
    ]
    for cmd in expected_commands:
        assert cmd in result.stdout, f"Missing subcommand: {cmd}"


def test_classify_risk_no_changes():
    result = subprocess.run(
        [sys.executable, "-m", "harness_runtime.cli", "classify-risk"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "leaf" in result.stdout.lower()


def test_verify_ai_runs():
    result = subprocess.run(
        [sys.executable, "-m", "harness_runtime.cli", "verify-ai"],
        capture_output=True, text=True,
    )
    assert "Harness AI Verification" in result.stdout or result.returncode == 0


def test_skills_exist():
    skills_dir = Path(__file__).resolve().parent.parent / "skills"
    buckets = ["engineering", "productivity", "misc"]
    for bucket in buckets:
        bd = skills_dir / bucket
        assert bd.is_dir(), f"Bucket missing: {bucket}"
        for skill_dir in bd.iterdir():
            if skill_dir.is_dir():
                assert (skill_dir / "SKILL.md").exists(), f"SKILL.md missing: {skill_dir.name}"


def test_policies_parse():
    import yaml
    policies_dir = Path(__file__).resolve().parent.parent / "resources" / "policies"
    for name in ["blast-radius.yaml", "gates.yaml", "project_index.yaml"]:
        path = policies_dir / name
        assert path.exists(), f"Policy missing: {name}"
        data = yaml.safe_load(path.read_text())
        assert data is not None, f"Policy failed to parse: {name}"


def test_plugin_json_valid():
    import yaml
    plugin_path = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"
    assert plugin_path.exists(), "plugin.json missing"
    data = yaml.safe_load(plugin_path.read_text())
    skills = data.get("skills", {})
    assert len(skills) == 12, f"Expected 12 skills, got {len(skills)}"


def test_risk_classify():
    from harness_runtime.risk import classify_file, load_blast_policy
    policy = load_blast_policy()

    assert classify_file("tests/test_utils.py", policy)[0] == "leaf"
    assert classify_file("docs/readme.md", policy)[0] == "leaf"

    assert classify_file("internal/domain/user.go", policy)[0] == "core"
    assert classify_file("pkg/auth/handler.go", policy)[0] == "core"

    assert classify_file(".github/workflows/ci.yml", policy)[0] == "infra"
    assert classify_file("Dockerfile", policy)[0] == "infra"

    assert classify_file("api/handler.go", policy)[0] == "branch"
    assert classify_file("cmd/main.go", policy)[0] == "branch"
