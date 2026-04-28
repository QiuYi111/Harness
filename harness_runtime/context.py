from pathlib import Path

SPEC_ARTIFACTS = ["spec.md", "plan.md", "tasks.md", "eval.md", "report.md"]


def build_context(spec_dir: Path, skills_dir: Path | None = None,
                  policies_dir: Path | None = None, project_root: Path | None = None) -> dict:
    if not spec_dir.exists():
        return {"error": f"spec directory not found: {spec_dir}", "ok": False}

    ctx = {
        "feature": spec_dir.name,
        "artifacts": {},
        "must_read": [],
        "forbidden_context": [
            "archived/", "3rdParty/", ".sisyphus/", "__pycache__/",
            "harness.egg-info/", "dist/", "build/", ".git/",
        ],
    }

    for artifact in SPEC_ARTIFACTS:
        path = spec_dir / artifact
        if path.exists():
            content = path.read_text(errors="replace")
            ctx["artifacts"][artifact] = {
                "exists": True,
                "size": len(content),
                "lines": len(content.splitlines()),
                "preview": content[:500] if content else "",
            }
            ctx["must_read"].append(str(path.relative_to(project_root) if project_root else path))
        else:
            ctx["artifacts"][artifact] = {"exists": False}

    root = project_root or spec_dir.parent.parent
    for agent_file in ["AGENTS.md", "CLAUDE.md"]:
        af = root / agent_file
        if af.exists():
            ctx["must_read"].insert(0, agent_file)

    for policy_name in ["blast-radius.yaml", "gates.yaml"]:
        if policies_dir:
            pp = policies_dir / policy_name
            if pp.exists():
                ctx["must_read"].append(str(pp))

    ctx["ok"] = True
    return ctx


def format_context(ctx: dict) -> str:
    if ctx.get("error"):
        return ctx["error"]

    lines = [
        f"# Context Bundle: {ctx['feature']}",
        "",
        "## Must Read",
        "",
    ]

    for item in ctx.get("must_read", []):
        lines.append(f"- `{item}`")

    lines.extend([
        "",
        "## Forbidden Context",
        "",
    ])
    for item in ctx.get("forbidden_context", []):
        lines.append(f"- `{item}`")

    lines.extend([
        "",
        "## Artifact Summary",
        "",
        "| Artifact | Status | Lines | Size |",
        "|----------|--------|-------|------|",
    ])

    for name, info in ctx.get("artifacts", {}).items():
        if info["exists"]:
            lines.append(f"| {name} | ✅ present | {info['lines']} | {info['size']}B |")
        else:
            lines.append(f"| {name} | ❌ missing | - | - |")

    lines.extend([
        "",
        "## Artifact Previews",
        "",
    ])
    for name, info in ctx.get("artifacts", {}).items():
        if info.get("exists") and info.get("preview"):
            lines.append(f"### {name}")
            lines.append("```")
            lines.append(info["preview"])
            if info["size"] > 500:
                lines.append(f"... ({info['size'] - 500} more bytes)")
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def write_context(ctx: dict, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_context(ctx))
    return output_path
