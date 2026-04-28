import os
from pathlib import Path

AGENT_TARGETS = {
    "claude-code": "~/.claude/skills/harness",
    "codex": "~/.codex/skills/harness",
    "cursor": "~/.cursor/skills/harness",
    "windsurf": "~/.windsurf/skills/harness",
}

SKILL_BUCKETS = ["engineering", "productivity", "misc"]


def install_skills(
    harness_root: Path,
    agent: str = "claude-code",
    target_dir: str | None = None,
) -> dict:
    if agent not in AGENT_TARGETS:
        return {"error": f"unknown agent: {agent}. Supported: {', '.join(AGENT_TARGETS)}"}

    target = Path(target_dir) if target_dir else Path(os.path.expanduser(AGENT_TARGETS[agent]))
    skills_dir = harness_root / "skills"

    if not skills_dir.exists():
        return {"error": f"skills directory not found: {skills_dir}"}

    target.mkdir(parents=True, exist_ok=True)

    linked, skipped, errors = [], [], []

    for bucket in SKILL_BUCKETS:
        bucket_dir = skills_dir / bucket
        if not bucket_dir.is_dir():
            continue
        for skill_dir in sorted(bucket_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_name = skill_dir.name
            link_path = target / skill_name

            try:
                if link_path.is_symlink():
                    link_path.unlink()
                    link_path.symlink_to(skill_dir)
                    linked.append(skill_name)
                elif link_path.exists():
                    skipped.append(skill_name)
                else:
                    link_path.symlink_to(skill_dir)
                    linked.append(skill_name)
            except OSError as e:
                errors.append(f"{skill_name}: {e}")

    plugin_src = harness_root / ".claude-plugin" / "plugin.json"
    plugin_copied = False
    if agent == "claude-code" and plugin_src.exists():
        plugin_target = Path(os.path.expanduser("~/.claude-plugin"))
        plugin_target.mkdir(parents=True, exist_ok=True)
        dest = plugin_target / "plugin.json"
        if not dest.exists():
            import shutil
            shutil.copy2(plugin_src, dest)
            plugin_copied = True

    return {
        "linked": linked,
        "skipped": skipped,
        "errors": errors,
        "plugin_copied": plugin_copied,
        "target": str(target),
    }
