import shutil
import subprocess
from pathlib import Path

import click

from . import __version__
from .risk import classify_files, get_gates, load_blast_policy
from .verify import run_full_verify, check_role_boundaries
from .evals import run_eval
from .context import build_context, format_context, write_context, build_context_cache_aware, format_context_cache_aware
from .installer import install_skills

DIST_ROOT = Path(__file__).resolve().parent.parent.parent
RESOURCES_DIR = DIST_ROOT / "references"
POLICIES_DIR = RESOURCES_DIR / "policies"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
SKILLS_DIR = DIST_ROOT / "subskills"
PLUGIN_PATH = DIST_ROOT / ".claude-plugin" / "plugin.json"

ICONS = {"pass": "✅", "fail": "❌", "warn": "⚠️ "}


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


def _git_diff_files(base: str | None = None) -> list[str]:
    try:
        if base:
            cmd = ["git", "diff", "--name-only", base]
        else:
            cmd = ["git", "diff", "--name-only", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 and not base:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, timeout=10,
            )
        return [f for f in result.stdout.strip().splitlines() if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _project_specs_dir(project_root: Path | None = None) -> Path:
    return (project_root or _git_root()) / "specs"


@click.group()
@click.version_option(__version__, prog_name="harness")
def main():
    pass


@main.command()
@click.argument("target", required=False, default=".")
def init(target):
    project_root = Path(target).resolve()
    if str(project_root) == str(DIST_ROOT.resolve()):
        click.echo("Error: target is Harness itself. Run from a project directory.", err=True)
        raise SystemExit(1)

    click.echo("Initializing Harness project...")
    click.echo(f"  Project root: {project_root}")

    dirs_to_create = ["specs", ".harness", ".harness/policies"]
    for d in dirs_to_create:
        path = project_root / d
        path.mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✓ {d}/")

    templates_to_copy = [
        "AGENTS.md", "CLAUDE.md", "Makefile", "CACHE.md",
    ]
    for t in templates_to_copy:
        src = TEMPLATES_DIR / t
        dst = project_root / t
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            click.echo(f"  ✓ copied {t}")
        elif dst.exists():
            click.echo(f"  ↻ {t} already exists")
        else:
            click.echo(f"  ⚠ template {t} not found at {src}")

    policy_files = [
        "blast-radius.yaml", "gates.yaml", "cache-context.yaml",
    ]
    for p in policy_files:
        src = POLICIES_DIR / p
        dst = project_root / ".harness" / "policies" / p
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            click.echo(f"  ✓ copied .harness/policies/{p}")
        elif dst.exists():
            click.echo(f"  ↻ .harness/policies/{p} already exists")
        else:
            click.echo(f"  ⚠ policy {p} not found at {src}")

    install_skills(DIST_ROOT)
    click.echo("\nDone. Run 'harness status' to verify.")


@main.command("install-skills")
@click.option("--agent", default="claude-code",
              help="Target agent (claude-code, codex, cursor, windsurf)")
@click.option("--target", default=None, help="Override target directory")
def install_skills_cmd(agent, target):
    result = install_skills(DIST_ROOT, agent, target)
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
@click.option("--target", default=None, help="Project root (default: git root or cwd)")
def specify(feature_id, target):
    project_root = Path(target).resolve() if target else _git_root()
    specs_dir = project_root / "specs"
    feature_dir = specs_dir / feature_id

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
            click.echo(f"  ⚠ {artifact_name} (empty, template not found at {src})")

    click.echo(f"\nCreated specs/{feature_id}/ — fill in the templates.")


@main.command("classify-risk")
@click.option("--base", default=None, help="Git base ref (e.g. 'main', 'HEAD~1')")
@click.option("--role", default="", help="Check role boundaries for TDD-RED/GREEN/REFACTOR/REVIEWER")
def classify_risk(base, role):
    policy = load_blast_policy()
    files = _git_diff_files(base)
    if not files:
        click.echo("No changed files detected.")
        click.echo("Overall risk: leaf")
        return

    click.echo("Analyzing changed files for blast radius...\n")

    risk, results = classify_files(files, policy)
    for filepath, file_risk, pattern in results:
        pattern_str = f" (matched '{pattern}')" if pattern else ""
        click.echo(f"  {filepath} → {file_risk}{pattern_str}")

    click.echo(f"\nOverall risk: {risk}")

    gates = get_gates(risk, policy)
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
@click.option("--base", default=None, help="Git base ref for role boundary check")
@click.option("--role", default="", help="Also check role boundaries")
@click.option("--project", default=None, help="Project root for specs/ check")
def verify_ai(base, role, project):
    project_root = Path(project).resolve() if project else _git_root()
    specs_dir = project_root / "specs"

    click.echo("=== Harness AI Verification ===\n")
    click.echo("Skill-pack integrity checks:\n")

    report = run_full_verify(
        skills_dir=SKILLS_DIR,
        plugin_path=PLUGIN_PATH,
        policies_dir=POLICIES_DIR,
        templates_dir=TEMPLATES_DIR,
        specs_dir=specs_dir,
        project_root=project_root,
    )

    for status, label, detail in report["results"]:
        icon = ICONS.get(status, "?")
        click.echo(f"  {icon} {label}: {detail}")

    click.echo(f"\n=== Summary ===")
    click.echo(f"  ✅ {report['passed']} passed")
    click.echo(f"  ❌ {report['failed']} failed")
    click.echo(f"  ⚠️  {report['warnings']} warnings")

    if role:
        files = _git_diff_files(base)
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
@click.option("--project", default=None, help="Project root")
def eval_cmd(feature_id, project):
    project_root = Path(project).resolve() if project else _git_root()
    spec_dir = project_root / "specs" / feature_id

    result = run_eval(spec_dir, project_root, POLICIES_DIR / "gates.yaml")

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
@click.option("--write", is_flag=True, default=False, help="Write context.md to specs/ dir")
@click.option("--project", default=None, help="Project root")
@click.option("--cache-aware", is_flag=True, default=False, help="Use cache-friendly ordering")
def context(feature_id, write, project, cache_aware):
    project_root = Path(project).resolve() if project else _git_root()
    spec_dir = project_root / "specs" / feature_id

    if cache_aware:
        ctx = build_context_cache_aware(spec_dir, project_root)
        if write:
            output = spec_dir / "context.md"
            write_context(ctx, output)
            click.echo(f"Wrote cache-aware {output}")
        else:
            click.echo(format_context_cache_aware(ctx))
        return

    ctx = build_context(
        spec_dir,
        skills_dir=SKILLS_DIR,
        policies_dir=POLICIES_DIR,
        project_root=project_root,
    )

    if write:
        output = spec_dir / "context.md"
        write_context(ctx, output)
        click.echo(f"Wrote {output}")
    else:
        click.echo(format_context(ctx))


@main.command()
@click.argument("feature_id")
@click.option("--project", default=None, help="Project root")
@click.option("--base", default=None, help="Git base ref for risk classification")
def report(feature_id, project, base):
    project_root = Path(project).resolve() if project else _git_root()
    spec_dir = project_root / "specs" / feature_id

    if not spec_dir.exists():
        click.echo(f"Error: specs/{feature_id}/ not found.", err=True)
        raise SystemExit(1)

    policy = load_blast_policy()
    click.echo(f"=== Report: {feature_id} ===\n")

    changed = _git_diff_files(base)
    if changed:
        risk, results = classify_files(changed, policy)
        click.echo(f"Blast radius: {risk}")
        click.echo(f"Changed files ({len(changed)}):")
        for f, r, _ in results:
            click.echo(f"  {f} ({r})")
    else:
        risk = "leaf"
        click.echo("No uncommitted changes.")
        click.echo("Blast radius: leaf")

    gates = get_gates(risk, policy)
    click.echo(f"\nRequired gates: {', '.join(gates)}")

    eval_result = run_eval(spec_dir, project_root, POLICIES_DIR / "gates.yaml")
    click.echo(f"\nEval results:")
    for status, label in eval_result.get("results", []):
        icon = ICONS.get(status, "?")
        click.echo(f"  {icon} {label}")

    report_path = spec_dir / "report.md"
    click.echo(f"\nFill in {report_path} with implementation evidence.")


@main.command()
@click.option("--project", default=None, help="Project root")
def status(project):
    project_root = Path(project).resolve() if project else _git_root()

    click.echo("=== Harness Status ===\n")
    click.echo(f"Version: {__version__}")
    click.echo(f"Harness dist: {DIST_ROOT}")
    click.echo(f"Project root: {project_root}")

    specs_dir = project_root / "specs"

    changed = _git_diff_files()
    if changed:
        policy = load_blast_policy()
        risk, _ = classify_files(changed, policy)
        gates = get_gates(risk, policy)
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


@main.command("cache-report")
@click.option("--project", default=None, help="Project root")
def cache_report(project):
    """Show estimated token breakdown by cache layer."""
    from .fingerprint import estimate_tokens

    project_root = Path(project).resolve() if project else _git_root()

    click.echo("=== Cache Report ===\n")

    click.echo("## Harness Stable Prefix (same across all projects)")
    click.echo("")
    harness_total = 0
    harness_files = [
        SKILLS_DIR.parent / "SKILL.md",
    ]
    for sd in sorted(SKILLS_DIR.iterdir()):
        if sd.is_dir():
            sk = sd / "SKILL.md"
            if sk.exists():
                harness_files.append(sk)
    for f in harness_files:
        try:
            content = f.read_text(errors="replace")
            tokens = estimate_tokens(content)
            harness_total += tokens
            display = f.relative_to(DIST_ROOT) if f.is_relative_to(DIST_ROOT) else f.name
            click.echo(f"  {str(display):45s} ~{tokens:>5} tokens")
        except OSError:
            pass
    click.echo(f"  {'─' * 50}")
    click.echo(f"  Harness stable prefix total:        ~{harness_total} tokens")
    click.echo("")

    click.echo("## Project Protocol")
    click.echo("")
    project_total = 0
    config_path = project_root / ".harness" / "policies" / "cache-context.yaml"
    if not config_path.exists():
        config_path = POLICIES_DIR / "cache-context.yaml"

    from .fingerprint import load_cache_config
    layers = load_cache_config(config_path)
    project_files = []
    for paths in layers.values():
        for p in paths:
            fpath = project_root / p
            if fpath.exists():
                project_files.append(fpath)

    for f in sorted(set(project_files)):
        try:
            content = f.read_text(errors="replace")
            tokens = estimate_tokens(content)
            project_total += tokens
            click.echo(f"  {f.name:35s} ~{tokens:>5} tokens")
        except OSError:
            pass
    click.echo(f"  {'─' * 50}")
    click.echo(f"  Project protocol total:              ~{project_total} tokens")
    click.echo("")

    click.echo(f"## Summary")
    click.echo(f"  Harness prefix:   ~{harness_total} tokens  (stable across all projects)")
    click.echo(f"  Project protocol: ~{project_total} tokens  (stable within project)")
    click.echo(f"  Combined stable:  ~{harness_total + project_total} tokens")
    click.echo(f"\nNote: token estimates are approximate (4 chars/token).")


if __name__ == "__main__":
    main()
