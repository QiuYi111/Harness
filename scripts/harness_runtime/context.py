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


def build_context_cache_aware(spec_dir: Path, project_root: Path,
                               cache_config_path: Path | None = None) -> dict:
    from .fingerprint import load_cache_config, fingerprint_layers, estimate_tokens

    if cache_config_path is None:
        cache_config_path = Path(__file__).resolve().parent.parent.parent / "references" / "policies" / "cache-context.yaml"

    layers = load_cache_config(cache_config_path)
    fingerprints = fingerprint_layers(layers, project_root) if layers else {}

    ctx = {
        "feature": spec_dir.name,
        "layers": {},
        "fingerprints": fingerprints,
        "ok": True,
    }

    for layer_name, paths in layers.items():
        layer_files = []
        total_tokens = 0
        for p in paths:
            fpath = project_root / p
            if fpath.exists() and fpath.is_file():
                content = fpath.read_text(errors="replace")
                tokens = estimate_tokens(content)
                total_tokens += tokens
                layer_files.append({
                    "path": p,
                    "lines": len(content.splitlines()),
                    "tokens": tokens,
                    "preview": content[:300] if content else "",
                })
        ctx["layers"][layer_name] = {
            "files": layer_files,
            "total_tokens": total_tokens,
        }

    ctx["total_tokens"] = sum(l["total_tokens"] for l in ctx["layers"].values())
    return ctx


def format_context_cache_aware(ctx: dict) -> str:
    if ctx.get("error"):
        return ctx["error"]

    lines = [
        f"# Context Bundle: {ctx['feature']}",
        "",
        f"**Total estimated tokens**: {ctx.get('total_tokens', 0)}",
        "",
    ]

    fingerprints = ctx.get("fingerprints", {})
    if fingerprints:
        lines.append("## Fingerprints")
        lines.append("")
        for name, h in fingerprints.items():
            lines.append(f"- `{name}`: `{h}`")
        lines.append("")

    layer_order = ["stable_prefix", "semi_stable_context", "active_feature_context", "dynamic_suffix"]
    for layer_name in layer_order:
        layer = ctx.get("layers", {}).get(layer_name)
        if not layer:
            continue
        lines.append(f"## {layer_name.replace('_', ' ').title()} ({layer['total_tokens']} tokens)")
        lines.append("")
        for f in layer["files"]:
            lines.append(f"- `{f['path']}` ({f['lines']} lines, ~{f['tokens']} tokens)")
        lines.append("")

    lines.append("## Forbidden Context")
    lines.append("")
    lines.append("- `.git/` `node_modules/` `dist/` `build/` `coverage/` `3rdParty/`")
    lines.append("- Unrelated specs/ features")
    lines.append("- Generated build artifacts")

    return "\n".join(lines)
