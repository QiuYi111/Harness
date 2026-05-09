"""Harness atlas — semantic code audit module.

Provides language detection, template loading, and prompt assembly
for the `harness atlas` CLI command.
"""

from pathlib import Path


EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".c": "c",
    ".h": "cpp",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".rs": "rust",
    ".go": "go",
}

ATLAS_SUBSKILL_DIR = Path(__file__).resolve().parent.parent.parent / "subskills" / "atlas"


def detect_language(filepath: str | Path) -> str:
    """Detect programming language from file extension.

    Args:
        filepath: Path to source file.

    Returns:
        Language name string (e.g. 'python', 'typescript', 'cpp').

    Raises:
        ValueError: If extension is not in the MVP support list.
    """
    ext = Path(filepath).suffix.lower()
    if ext in EXTENSION_LANGUAGE_MAP:
        return EXTENSION_LANGUAGE_MAP[ext]
    supported = ", ".join(sorted(EXTENSION_LANGUAGE_MAP.keys()))
    raise ValueError(
        f"Unsupported file extension '{ext}'. "
        f"MVP supports: {supported}"
    )


def resolve_output_path(input_path: str | Path, output_dir: str | None = None) -> Path:
    """Resolve the output path for a semantic atlas file.

    Default: docs/semantic_atlas/<relative_path>.semantic_atlas.md
    Custom: <output_dir>/<basename>.semantic_atlas.md

    Args:
        input_path: Path to the source file being analyzed.
        output_dir: Optional custom output directory.

    Returns:
        Resolved output file path.
    """
    src = Path(input_path)
    stem = src.stem
    suffix = ".semantic_atlas.md"

    if output_dir:
        base = Path(output_dir)
    else:
        base = Path("docs") / "semantic_atlas"

    return base / f"{stem}{suffix}"


def load_template() -> str:
    """Load the semantic atlas output template.

    Returns:
        Template string with all 14 section placeholders.

    Raises:
        FileNotFoundError: If template file is missing.
    """
    template_path = ATLAS_SUBSKILL_DIR / "templates" / "semantic_atlas.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Atlas template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def load_skill_prompt() -> str:
    """Load the SKILL.md prompt for atlas generation.

    Returns:
        SKILL.md content string.

    Raises:
        FileNotFoundError: If SKILL.md is missing.
    """
    skill_path = ATLAS_SUBSKILL_DIR / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Atlas SKILL.md not found: {skill_path}")
    return skill_path.read_text(encoding="utf-8")


def load_reference(filename: str) -> str:
    """Load a reference document from the atlas references directory.

    Args:
        filename: Name of the reference file (e.g. 'FAITHFULNESS_RULES.md').

    Returns:
        Reference document content.

    Raises:
        FileNotFoundError: If reference file is missing.
    """
    ref_path = ATLAS_SUBSKILL_DIR / "references" / filename
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference not found: {ref_path}")
    return ref_path.read_text(encoding="utf-8")


def assemble_prompt(
    source_code: str,
    language: str,
    template: str,
    strict: bool = False,
    diagram_heavy: bool = False,
    verify_mermaid: bool = False,
) -> str:
    """Assemble the full LLM prompt for semantic atlas generation.

    Args:
        source_code: Raw source code text to analyze.
        language: Detected programming language.
        template: Output template with section placeholders.
        strict: Enable strict mode (all uncertainty labeled).
        diagram_heavy: Diagrams + tables >= 80% of content.
        verify_mermaid: Validate Mermaid syntax in output.

    Returns:
        Assembled prompt string ready for LLM consumption.
    """
    parts: list[str] = []

    skill_prompt = load_skill_prompt()
    parts.append(skill_prompt)

    flags: list[str] = []
    if strict:
        flags.append("STRICT MODE: All uncertainty must be explicitly labeled. No unmarked assumptions allowed.")
    if diagram_heavy:
        flags.append("DIAGRAM-HEAVY MODE: Diagrams + tables must comprise >= 80% of output. Minimize paragraph text.")
    if verify_mermaid:
        flags.append("MERMAID VERIFICATION: Validate all Mermaid diagram syntax. Degrade to table on persistent failure.")

    if flags:
        parts.append("\n## Active Flags\n\n" + "\n".join(f"- {f}" for f in flags))

    parts.append("\n## Output Template\n\nFill the following template completely. Every section is required:\n")
    parts.append(template)

    parts.append(f"\n## Source Code to Analyze\n\nLanguage: {language}\n\n```{language}\n{source_code}\n```")

    return "\n".join(parts)
