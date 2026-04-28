import shutil
import subprocess
from pathlib import Path

import click

from . import __version__
from .risk import classify_files, get_gates, RISK_PRIORITY
from .verify import run_full_verify, check_role_boundaries
from .evals import run_eval
from .context import build_context, format_context
from .installer import install_skills

HARNESS_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = HARNESS_ROOT / "templates"
RESOURCES_DIR = HARNESS_ROOT / "resources"
POLICIES_DIR = RESOURCES_DIR / "policies"
SPECS_DIR = HARNESS_ROOT / "specs"

ICONS = {"pass": "✅", "fail": "❌", "warn": "⚠️ "}


def _git_diff_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, timeout=10,
            )
        return [f for f in result.stdout.strip().splitlines() if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _git_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.cwd()


@click.group()
@click.version_option(__version__, prog_name="harness")
def main():
    pass


@main.command()
def init():
    click.echo("Initializing Harness project...")
    click.echo(f"  Root: {HARNESS_ROOT}")

    dirs_to_create = ["specs", "docs", "scripts"]
    for d in dirs_to_create:
        path = HARNESS_ROOT / d
        path.mkdir(exist_ok=True)
        click.echo(f"  ✓ {d}/")

    templates_to_copy = [
        "AGENTS.md", "CLAUDE.md", "Makefile",
        "BLAST_RADIUS_POLICY.md", "ROLE_POLICY.md",
    ]
    for t in templates_to_copy:
        src = TEMPLATES_DIR / t
        dst = HARNESS_ROOT / t
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            click.echo(f"  ✓ copied {t}")
        elif dst.exists():
            click.echo(f"  ↻ {t} already exists")
        else:
            click.echo(f"  ⚠ template {t} not found")

    install_skills(HARNESS_ROOT)
    click.echo("\nDone. Run 'harness status' to verify.")


@main.command("install-skills")
@click.option("--agent", default="claude-code", help="Target agent (claude-code, codex, cursor)")
@click.option("--target", default=None, help="Override target directory")
def install_skills_cmd(agent, target):
    result = install_skills(HARNESS_ROOT, agent, target)
    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        raise SystemExit(1)

    for name in result["linked"]:
        click.echo(f"  ✓ {name}")
    for name in result["skipped"]:
        click.echo(f"  ⚠ skipped (exists): {name}")
    for err in result["errors"]:
        click.echo(f"  ✗ {err}")

    if result["plugin_copied"]:
        click.echo("  ✓ copied .claude-plugin/plugin.json")

    click.echo(f"\nInstalled {len(result['linked'])} skills to {result['target']}")


@main.command()
@click.argument("feature_id")
def specify(feature_id):
    feature_dir = SPECS_DIR / feature_id
    if feature_dir.exists():
        click.echo(f"specs/{feature_id}/ already exists.")
        raise SystemExit(1)

    feature_dir.mkdir(parents=True)

    template_map = {
        "SPEC_TEMPLATE.md": "spec.md",
        "PLAN_TEMPLATE.md": "plan.md",
        "TASKS_TEMPLATE.md": "tasks.md",
        "EVAL_TEMPLATE.md": "eval.md",
        "REPORT_TEMPLATE.md": "report.md",
    }

    for tmpl_name, artifact_name in template_map.items():
        src = TEMPLATES_DIR / tmpl_name
        dst = feature_dir / artifact_name
        if src.exists():
            shutil.copy2(src, dst)
            click.echo(f"  ✓ {artifact_name}")
        else:
            dst.touch()
            click.echo(f"  ⚠ {artifact_name} (empty, template not found)")

    click.echo(f"\nCreated specs/{feature_id}/ — fill in the templates.")


@main.command("classify-risk")
@click.option("--role", default="", help="Check role boundaries for TDD-RED/GREEN/REFACTOR/REVIEWER")
def classify_risk(role):
    files = _git_diff_files()
    if not files:
        click.echo("No changed files detected.")
        click.echo("Overall risk: leaf")
        return

    click.echo("Analyzing changed files for blast radius...\n")

    risk, results = classify_files(files)
    for filepath, file_risk in results:
        click.echo(f"  {filepath} → {file_risk}")

    click.echo(f"\nOverall risk: {risk}")

    gates = get_gates(risk, POLICIES_DIR / "gates.yaml")
    click.echo("\nRequired gates:")
    for g in gates:
        click.echo(f"  - {g}")

    if role:
        violations = check_role_boundaries(files, role)
        if violations:
            click.echo(f"\nRole boundary violations ({role}):")
            for status, label, detail in violations:
                click.echo(f"  {ICONS.get(status, '?')} {label}: {detail}")
        else:
            click.echo(f"\nNo role boundary violations for {role}.")


@main.command("verify-ai")
@click.option("--role", default="", help="Also check role boundaries")
def verify_ai(role):
    templates = TEMPLATES_DIR
    specs = SPECS_DIR

    if not _git_root().exists():
        pass

    git_root = _git_root()
    if git_root != HARNESS_ROOT:
        alt_templates = git_root / "templates"
        alt_specs = git_root / "specs"
        if alt_templates.exists():
            templates = alt_templates
        if alt_specs.exists():
            specs = alt_specs

    report = run_full_verify(templates, specs)

    click.echo("=== Harness AI Verification ===\n")

    for status, label, detail in report["results"]:
        icon = ICONS.get(status, "?")
        click.echo(f"  {icon} {label}: {detail}")

    click.echo(f"\n=== Summary ===")
    click.echo(f"  ✅ {report['passed']} passed")
    click.echo(f"  ❌ {report['failed']} failed")
    click.echo(f"  ⚠️  {report['warnings']} warnings")

    if role:
        files = _git_diff_files()
        violations = check_role_boundaries(files, role)
        if violations:
            click.echo(f"\nRole boundary violations ({role}):")
            for status, label, detail in violations:
                click.echo(f"  {ICONS.get(status, '?')} {label}: {detail}")

    if not report["ok"]:
        click.echo(f"\n🚨 {report['failed']} required check(s) failed. Fix before committing.")
        raise SystemExit(1)
    else:
        click.echo("\n🎉 All required checks passed.")


@main.command("eval")
@click.argument("feature_id")
def eval_cmd(feature_id):
    spec_dir = SPECS_DIR / feature_id
    git_root = _git_root()
    if git_root != HARNESS_ROOT:
        alt = git_root / "specs" / feature_id
        if alt.exists():
            spec_dir = alt

    result = run_eval(spec_dir, git_root)

    if "error" in result:
        click.echo(f"Error: {result['error']}", err=True)
        raise SystemExit(1)

    click.echo(f"=== Eval: {result['feature']} ===\n")

    for status, label in result["results"]:
        icon = ICONS.get(status, "?")
        click.echo(f"  {icon} {label}")

    click.echo(f"\n  {result['passed']} passed, {result['failed']} failed, {result['warnings']} warnings")

    if not result["ok"]:
        raise SystemExit(1)


@main.command()
@click.argument("feature_id")
def context(feature_id):
    spec_dir = SPECS_DIR / feature_id
    git_root = _git_root()
    if git_root != HARNESS_ROOT:
        alt = git_root / "specs" / feature_id
        if alt.exists():
            spec_dir = alt

    ctx = build_context(spec_dir)
    click.echo(format_context(ctx))


@main.command()
@click.argument("feature_id")
def report(feature_id):
    spec_dir = SPECS_DIR / feature_id
    git_root = _git_root()
    if git_root != HARNESS_ROOT:
        alt = git_root / "specs" / feature_id
        if alt.exists():
            spec_dir = alt

    if not spec_dir.exists():
        click.echo(f"Error: specs/{feature_id}/ not found.", err=True)
        raise SystemExit(1)

    click.echo(f"=== Report: {feature_id} ===\n")

    changed = _git_diff_files()
    if changed:
        risk, results = classify_files(changed)
        click.echo(f"Blast radius: {risk}")
        click.echo(f"Changed files ({len(changed)}):")
        for f, r in results:
            click.echo(f"  {f} ({r})")
    else:
        risk = "leaf"
        click.echo("No uncommitted changes.")
        click.echo("Blast radius: leaf")

    gates = get_gates(risk, POLICIES_DIR / "gates.yaml")
    click.echo(f"\nRequired gates: {', '.join(gates)}")

    eval_result = run_eval(spec_dir, git_root)
    click.echo(f"\nEval results:")
    for status, label in eval_result.get("results", []):
        icon = ICONS.get(status, "?")
        click.echo(f"  {icon} {label}")

    report_path = spec_dir / "report.md"
    click.echo(f"\nFill in {report_path} with implementation evidence.")


@main.command()
def status():
    click.echo("=== Harness Status ===\n")
    click.echo(f"Version: {__version__}")
    click.echo(f"Root: {HARNESS_ROOT}")

    git_root = _git_root()
    click.echo(f"Git root: {git_root}")

    templates_dir = TEMPLATES_DIR
    if (git_root / "templates").exists():
        templates_dir = git_root / "templates"
    specs_dir = SPECS_DIR
    if (git_root / "specs").exists():
        specs_dir = git_root / "specs"

    changed = _git_diff_files()
    if changed:
        risk, _ = classify_files(changed)
        gates = get_gates(risk, POLICIES_DIR / "gates.yaml")
        click.echo(f"\nActive changes: {len(changed)} files")
        click.echo(f"Blast radius: {risk}")
        click.echo(f"Gates: {', '.join(gates)}")
    else:
        click.echo("\nNo active changes.")

    if specs_dir.exists():
        features = sorted(d.name for d in specs_dir.iterdir() if d.is_dir())
        click.echo(f"\nFeatures ({len(features)}):")
        for f in features:
            spec_path = specs_dir / f / "spec.md"
            eval_path = specs_dir / f / "eval.md"
            status_str = "pending"
            if eval_path.exists() and eval_path.stat().st_size > 0:
                status_str = "complete"
            elif spec_path.exists() and spec_path.stat().st_size > 0:
                status_str = "in_progress"
            click.echo(f"  {f}: {status_str}")
    else:
        click.echo("\nNo specs/ directory.")


if __name__ == "__main__":
    main()
