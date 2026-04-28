import os
from pathlib import Path

AGENT_TARGETS = {
    "claude-code": "~/.claude/skills/harness",
    "codex": "~/.codex/skills/harness",
    "cursor": "~/.cursor/skills/harness",
    "windsurf": "~/.windsurf/skills/harness",
}


def install_skills(
    harness_root: Path,
    agent: str = "claude-code",
    target_dir: str | None = None,
) -> dict:
    if agent not in AGENT_TARGETS:
        return {"error": f"unknown agent: {agent}. Supported: {', '.join(AGENT_TARGETS)}"}

    target = Path(target_dir) if target_dir else Path(os.path.expanduser(AGENT_TARGETS[agent]))
    skills_dir = harness_root

    if not skills_dir.exists():
        return {"error": f"skills directory not found: {skills_dir}"}

    linked = []
    errors = []

    try:
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            return {"error": f"target exists and is not a symlink: {target}", "target": str(target)}

        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(skills_dir.resolve())
        linked.append("harness (root skill + subskills)")
    except OSError as e:
        errors.append(f"harness: {e}")

    plugin_copied = False
    if agent == "claude-code":
        import json
        plugin_target = Path(os.path.expanduser("~/.claude-plugin"))
        plugin_target.mkdir(parents=True, exist_ok=True)
        dest = plugin_target / "plugin.json"
        plugin_data = {
            "name": "harness",
            "description": "Cache-friendly engineering governance for AI coding agents.",
            "skills": [str(skills_dir.resolve())],
        }
        existing = {}
        if dest.exists():
            try:
                existing = json.loads(dest.read_text())
            except (json.JSONDecodeError, ValueError):
                pass
        existing_skills = existing.get("skills", [])
        if existing_skills != [str(skills_dir.resolve())]:
            existing.update(plugin_data)
            dest.write_text(json.dumps(existing, indent=2))
            plugin_copied = True

    return {
        "linked": linked,
        "skipped": [],
        "errors": errors,
        "plugin_copied": plugin_copied,
        "target": str(target),
    }
