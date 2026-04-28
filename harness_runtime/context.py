from pathlib import Path

SPEC_ARTIFACTS = ["spec.md", "plan.md", "tasks.md", "eval.md", "report.md"]


def build_context(spec_dir: Path) -> dict:
    if not spec_dir.exists():
        return {"error": f"spec directory not found: {spec_dir}"}

    ctx = {"feature": spec_dir.name, "artifacts": {}}

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
        else:
            ctx["artifacts"][artifact] = {"exists": False}

    return ctx


def format_context(ctx: dict) -> str:
    if "error" in ctx:
        return ctx["error"]

    lines = [f"=== Context Bundle: {ctx['feature']} ===", ""]

    for name, info in ctx["artifacts"].items():
        if info["exists"]:
            lines.append(f"--- {name} ({info['lines']} lines, {info['size']} bytes) ---")
            lines.append(info["preview"])
            if info["size"] > 500:
                lines.append(f"... ({info['size'] - 500} more bytes)")
            lines.append("")
        else:
            lines.append(f"--- {name}: MISSING ---")
            lines.append("")

    return "\n".join(lines)
