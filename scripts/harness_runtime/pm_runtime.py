"""PM runtime health-check module.

Validates .pm structure, parses state, classifies loop control,
inspects worker reports, and reads git status — all read-only.
"""

import subprocess
from pathlib import Path

import yaml

PM_STABLE_REQUIRED = [
    "product.md",
    "roadmap.md",
    "architecture-guardrails.md",
    "acceptance-rubric.md",
]

PM_RUNTIME_REQUIRED = [
    "state.yaml",
    "active-stage.md",
    "handoff.md",
    "loop-control",
    "next-task.md",
]

LOOP_CONTROL_VALID = {
    "CONTINUE",
    "STOP",
    "NEEDS_USER_DECISION",
    "BLOCKED",
    "STAGE_EXIT_REACHED",
}

PLACEHOLDER_REPORT_LINES = {"# Worker Report", "No worker report yet."}

# Each required section maps a canonical name to a list of acceptable
# heading texts (case-insensitive match).  At least one alternative per
# group must appear as a markdown heading in the report.
REQUIRED_REPORT_SECTIONS: list[tuple[str, list[str]]] = [
    ("Task summary", ["task summary", "objective"]),
    ("What was done", ["what was done", "changes"]),
    ("Changed files", ["changed files", "files changed"]),
    ("Commands run", ["commands run", "verification evidence", "verification"]),
    ("Test results", ["test results", "tests"]),
    ("Acceptance criteria", ["acceptance criteria", "acceptance criteria checklist"]),
    ("Problems encountered", ["problems encountered", "problems"]),
    ("Deviations", ["deviations", "deviations from task"]),
    ("Evidence", ["evidence"]),
]


def _section_present(heading: str, alternatives: list[str]) -> bool:
    low = heading.lower()
    return any(alt in low for alt in alternatives)


def validate_pm_structure(project_root: Path) -> dict:
    """Check that all required .pm/stable and .pm/runtime files exist and are non-empty.

    Returns dict with keys: ok (bool), missing (list[str]), empty (list[str]).
    """
    missing: list[str] = []
    empty: list[str] = []

    for rel in PM_STABLE_REQUIRED:
        p = project_root / ".pm" / "stable" / rel
        if not p.exists():
            missing.append(f".pm/stable/{rel}")
        elif p.stat().st_size == 0:
            empty.append(f".pm/stable/{rel}")

    for rel in PM_RUNTIME_REQUIRED:
        p = project_root / ".pm" / "runtime" / rel
        if not p.exists():
            missing.append(f".pm/runtime/{rel}")
        elif p.stat().st_size == 0:
            empty.append(f".pm/runtime/{rel}")

    return {"ok": len(missing) == 0 and len(empty) == 0, "missing": missing, "empty": empty}


def parse_state_yaml(project_root: Path) -> dict:
    """Parse .pm/runtime/state.yaml and return a structured summary.

    Returns dict with: stage, phase, loop_iteration, readiness, worker, git_policy, next_action, raw.
    Raises FileNotFoundError or ValueError if state.yaml is missing or invalid.
    """
    state_path = project_root / ".pm" / "runtime" / "state.yaml"
    if not state_path.exists():
        raise FileNotFoundError(f"Missing {state_path}")

    text = state_path.read_text()
    if not text.strip():
        raise ValueError("state.yaml is empty")

    try:
        raw = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"state.yaml is invalid YAML: {exc}") from exc

    return {
        "stage": raw.get("current_stage"),
        "phase": raw.get("current_phase"),
        "loop_iteration": raw.get("loop_iteration"),
        "readiness": raw.get("readiness", {}),
        "worker": {
            "engine": raw.get("worker", {}).get("engine"),
            "role": raw.get("worker", {}).get("role"),
            "mode": raw.get("worker", {}).get("mode"),
        },
        "git_policy": {
            "branch_policy": raw.get("git", {}).get("branch_policy"),
            "goal_branch": raw.get("git", {}).get("current_goal_branch"),
            "auto_merge": raw.get("git", {}).get("auto_merge"),
            "auto_push": raw.get("git", {}).get("auto_push"),
        },
        "next_action": {
            "type": raw.get("next_action", {}).get("type"),
            "summary": raw.get("next_action", {}).get("summary"),
            "blocked": raw.get("next_action", {}).get("blocked"),
            "needs_user_decision": raw.get("next_action", {}).get("needs_user_decision"),
        },
        "failure_tracking": raw.get("failure_tracking", {}),
        "raw": raw,
    }


def classify_loop_control(project_root: Path) -> dict:
    """Read .pm/runtime/loop-control and classify the supervisor directive.

    Returns dict with: directive (str), valid (bool), reason (str|None).
    """
    lc_path = project_root / ".pm" / "runtime" / "loop-control"
    if not lc_path.exists():
        return {"directive": None, "valid": False, "reason": "loop-control file missing"}

    content = lc_path.read_text().strip()
    if not content:
        return {"directive": None, "valid": False, "reason": "loop-control is empty"}

    directive = content.splitlines()[0].strip()
    if directive not in LOOP_CONTROL_VALID:
        return {"directive": directive, "valid": False, "reason": f"unknown directive: {directive}"}

    descriptions = {
        "CONTINUE": "supervisor should continue delegating",
        "STOP": "supervisor should stop the loop",
        "NEEDS_USER_DECISION": "supervisor should pause for user decision",
        "BLOCKED": "supervisor is blocked by an unresolved issue",
        "STAGE_EXIT_REACHED": "stage exit criteria have been met",
    }
    return {"directive": directive, "valid": True, "reason": descriptions[directive]}


def validate_worker_report(project_root: Path) -> dict:
    """Validate .pm/runtime/worker-report.md structure and required sections.

    Returns dict with:
        status (not_started|placeholder|invalid|valid),
        sections (list[str]),
        reason (str),
        missing_sections (list[str], empty unless status is 'invalid').
    """
    report_path = project_root / ".pm" / "runtime" / "worker-report.md"
    if not report_path.exists():
        return {"status": "not_started", "sections": [], "reason": "worker-report.md does not exist", "missing_sections": []}

    content = report_path.read_text()
    if not content.strip():
        return {"status": "not_started", "sections": [], "reason": "worker-report.md is empty", "missing_sections": []}

    lines = content.strip().splitlines()
    non_empty = [l.strip() for l in lines if l.strip()]

    if set(non_empty) == PLACEHOLDER_REPORT_LINES:
        return {"status": "placeholder", "sections": [], "reason": "placeholder report, not started", "missing_sections": []}

    sections = [l.lstrip("# ").strip() for l in lines if l.startswith("#")]

    if not sections:
        return {"status": "not_started", "sections": [], "reason": "no headings found in report", "missing_sections": []}

    missing: list[str] = []
    for canonical_name, alternatives in REQUIRED_REPORT_SECTIONS:
        if not any(_section_present(s, alternatives) for s in sections):
            missing.append(canonical_name)

    if missing:
        return {
            "status": "invalid",
            "sections": sections,
            "reason": f"missing required sections: {', '.join(missing)}",
            "missing_sections": missing,
        }

    return {"status": "valid", "sections": sections, "reason": f"{len(sections)} section(s) found", "missing_sections": []}


def inspect_git(project_root: Path) -> dict:
    """Inspect git branch and dirty files without mutating state.

    Returns dict with: branch (str|None), dirty_files (list[str]), error (str|None).
    """
    result: dict = {"branch": None, "dirty_files": [], "error": None}

    try:
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if branch_proc.returncode == 0:
            result["branch"] = branch_proc.stdout.strip()
        else:
            result["error"] = branch_proc.stderr.strip() or "git rev-parse failed"
            return result
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        result["error"] = str(exc)
        return result

    try:
        dirty_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if dirty_proc.returncode == 0:
            result["dirty_files"] = [
                line.strip() for line in dirty_proc.stdout.splitlines() if line.strip()
            ]
        else:
            result["error"] = dirty_proc.stderr.strip() or "git status failed"
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        result["error"] = str(exc)

    return result


def get_pm_status(project_root: Path) -> dict:
    """Collect full PM runtime status for a project.

    Returns dict suitable for CLI output. The top-level 'ok' key is False only
    when required runtime state is invalid or missing.
    """
    structure = validate_pm_structure(project_root)

    state: dict = {}
    state_error: str | None = None
    try:
        state = parse_state_yaml(project_root)
    except (FileNotFoundError, ValueError) as exc:
        state_error = str(exc)

    loop = classify_loop_control(project_root)
    report = validate_worker_report(project_root)
    git = inspect_git(project_root)

    # ok = False only when required files are missing/invalid
    ok = structure["ok"] and state_error is None and loop["valid"]

    return {
        "ok": ok,
        "structure": structure,
        "state": state,
        "state_error": state_error,
        "loop_control": loop,
        "worker_report": report,
        "git": git,
    }
