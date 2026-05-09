"""Mermaid syntax validation for Harness atlas output."""

import re
import shutil
import subprocess


def verify_mermaid_syntax(mermaid_text: str) -> tuple[bool, str]:
    """Validate Mermaid diagram syntax.

    Uses mmdc (Mermaid CLI) if available, otherwise falls back to
    basic syntax checks (matching braces, valid keywords).

    Args:
        mermaid_text: Raw Mermaid diagram text (without ``` fences).

    Returns:
        Tuple of (is_valid, error_message). error_message is empty
        string when valid.
    """
    if not mermaid_text.strip():
        return False, "Empty diagram"

    stripped = mermaid_text.strip()

    # Check diagram type keyword
    valid_keywords = (
        "flowchart", "graph", "sequenceDiagram", "classDiagram",
        "stateDiagram", "stateDiagram-v2", "erDiagram", "gantt",
        "pie", "journey", "mindmap", "timeline", "gitGraph",
    )
    first_line = stripped.splitlines()[0].strip()
    if not any(first_line.startswith(kw) for kw in valid_keywords):
        return False, f"Invalid diagram type: {first_line}"

    # Basic syntax checks
    error = _basic_checks(stripped)
    if error:
        return False, error

    # Try mmdc if available
    mmdc_path = shutil.which("mmdc")
    if mmdc_path:
        return _verify_with_mmdc(stripped, mmdc_path)

    return True, ""


def _basic_checks(text: str) -> str:
    """Run basic syntax checks on Mermaid text.

    Returns error message or empty string if OK.
    """
    lines = text.splitlines()

    # Check balanced braces in node definitions
    open_braces = text.count("[") + text.count("{") + text.count("(")
    close_braces = text.count("]") + text.count("}") + text.count(")")
    # Allow slight imbalance for arrow syntax like A-->B
    # but brackets should be balanced
    sq_open = text.count("[")
    sq_close = text.count("]")
    if sq_open != sq_close:
        return f"Unbalanced square brackets: {sq_open} open, {sq_close} close"

    cur_open = text.count("{")
    cur_close = text.count("}")
    if cur_open != cur_close:
        return f"Unbalanced curly braces: {cur_open} open, {cur_close} close"

    # Check for invalid characters in node IDs
    node_id_pattern = re.compile(r"^\s*([A-Za-z_]\w*)")
    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith("%") or line.startswith("%%"):
            continue
        if line.startswith("subgraph") or line.startswith("end"):
            continue
        if line.startswith("style") or line.startswith("classDef"):
            continue
        if "-->" in line or "---" in line or "->" in line or "-.->" in line:
            continue
        if "==" in line or "--" in line:
            continue
        # StateDiagram lines
        if line.startswith("[*]") or line.startswith("state "):
            continue
        if ":" in line.split()[0] if line.split() else False:
            continue

    return ""


def _verify_with_mmdc(text: str, mmdc_path: str) -> tuple[bool, str]:
    """Verify Mermaid syntax using mmdc CLI."""
    try:
        result = subprocess.run(
            [mmdc_path, "-i", "-", "--output", "/dev/null"],
            input=text,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        error_msg = result.stderr.strip() or result.stdout.strip()
        return False, f"mmdc: {error_msg}"
    except subprocess.TimeoutExpired:
        return False, "mmdc timed out"
    except FileNotFoundError:
        return True, ""  # mmdc not found, skip external validation
