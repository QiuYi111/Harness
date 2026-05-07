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


def validate_branch_policy(project_root: Path) -> dict:
    """Compare the current git branch with the supervisor-managed goal branch.

    Read-only validation — never mutates git state.

    Returns dict with:
        status (str): one of 'ok', 'mismatch', 'unknown'
        current_branch (str|None): the branch HEAD is on
        expected_branch (str|None): the goal branch from state.yaml
        reason (str): human-readable explanation
    """
    git = inspect_git(project_root)
    current_branch = git.get("branch")

    expected_branch = None
    try:
        state = parse_state_yaml(project_root)
        expected_branch = state.get("git_policy", {}).get("goal_branch")
    except (FileNotFoundError, ValueError):
        pass

    if not expected_branch:
        return {
            "status": "ok",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": "no goal branch set, branch policy not enforced",
        }

    if git.get("error") or current_branch is None:
        return {
            "status": "unknown",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"git error: {git.get('error', 'branch unavailable')}",
        }

    if current_branch == expected_branch:
        return {
            "status": "ok",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"on expected branch '{expected_branch}'",
        }

    return {
        "status": "mismatch",
        "current_branch": current_branch,
        "expected_branch": expected_branch,
        "reason": f"on '{current_branch}' but expected '{expected_branch}'",
    }


def get_branch_correction_plan(project_root: Path) -> dict:
    """Read-only branch correction plan for supervisor recovery.

    Inspects current branch, expected goal branch, and ancestry
    relationships to suggest safe correction commands — never mutates
    git state.

    Returns dict with:
        status (str): one of 'ok', 'safe_fast_forward_goal_branch',
                      'safe_switch_to_goal_branch', 'manual_review_required',
                      'unknown'
        current_branch (str|None): the branch HEAD is on
        expected_branch (str|None): the goal branch from state.yaml
        reason (str): human-readable explanation
        commands (list[str]): suggested non-destructive commands
    """
    git = inspect_git(project_root)
    current_branch = git.get("branch")

    expected_branch = None
    try:
        state = parse_state_yaml(project_root)
        expected_branch = state.get("git_policy", {}).get("goal_branch")
    except (FileNotFoundError, ValueError):
        pass

    if not expected_branch:
        return {
            "status": "ok",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": "no goal branch configured",
            "commands": [],
        }

    if git.get("error") or current_branch is None:
        return {
            "status": "unknown",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"git error: {git.get('error', 'branch unavailable')}",
            "commands": [],
        }

    if current_branch == expected_branch:
        return {
            "status": "ok",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"already on expected branch '{expected_branch}'",
            "commands": [],
        }

    try:
        verify = subprocess.run(
            ["git", "rev-parse", "--verify", expected_branch],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if verify.returncode != 0:
            return {
                "status": "manual_review_required",
                "current_branch": current_branch,
                "expected_branch": expected_branch,
                "reason": f"expected branch '{expected_branch}' does not exist",
                "commands": [],
            }

        ancestor_check = subprocess.run(
            ["git", "merge-base", "--is-ancestor", expected_branch, "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if ancestor_check.returncode == 0:
            return {
                "status": "safe_fast_forward_goal_branch",
                "current_branch": current_branch,
                "expected_branch": expected_branch,
                "reason": f"expected branch '{expected_branch}' is behind current '{current_branch}', safe to fast-forward",
                "commands": [
                    f"git branch -f {expected_branch} HEAD",
                    f"git switch {expected_branch}",
                ],
            }

        reverse_check = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", expected_branch],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if reverse_check.returncode == 0:
            return {
                "status": "safe_switch_to_goal_branch",
                "current_branch": current_branch,
                "expected_branch": expected_branch,
                "reason": f"current branch '{current_branch}' is behind expected '{expected_branch}', safe to switch",
                "commands": [f"git switch {expected_branch}"],
            }

        return {
            "status": "manual_review_required",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"branches '{current_branch}' and '{expected_branch}' have diverged",
            "commands": [],
        }

    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {
            "status": "unknown",
            "current_branch": current_branch,
            "expected_branch": expected_branch,
            "reason": f"git error: {exc}",
            "commands": [],
        }


def decide_next_action(project_root: Path) -> dict:
    """Deterministic read-only next-action decision helper for the supervisor.

    Inspects PM runtime state, loop-control, worker-report status, iteration
    limits, and failure counters to compute what the supervisor should do next.

    Returns dict with:
        action (str): one of delegate, review, request_rework,
                      request_user_decision, stop, blocked
        reason (str): short machine-readable reason
        details (list[str]): optional specific details
    """
    details: list[str] = []

    # ── Invalid PM runtime state → stop ──────────────────────────────────
    status = get_pm_status(project_root)
    if not status["ok"]:
        return {
            "action": "stop",
            "reason": "invalid_pm_runtime",
            "details": [f"pm_status.ok=False, state_error={status.get('state_error')}"],
        }

    state = status["state"]
    raw = state.get("raw", {})

    # ── Branch policy mismatch ───────────────────────────────────────────
    branch_policy = status.get("branch_policy", {})
    if branch_policy.get("status") == "mismatch":
        details.append(
            f"current_branch={branch_policy['current_branch']}, "
            f"expected_branch={branch_policy['expected_branch']}"
        )
        return {
            "action": "request_user_decision",
            "reason": "branch_policy_mismatch",
            "details": details,
        }

    # ── Loop-control directives ──────────────────────────────────────────
    loop = status["loop_control"]
    directive = loop["directive"]

    if directive == "STOP":
        return {"action": "stop", "reason": "loop_control_STOP", "details": []}
    if directive == "NEEDS_USER_DECISION":
        return {"action": "request_user_decision", "reason": "loop_control_needs_user_decision", "details": []}
    if directive == "BLOCKED":
        return {"action": "blocked", "reason": "loop_control_BLOCKED", "details": []}
    if directive == "STAGE_EXIT_REACHED":
        return {"action": "stop", "reason": "loop_control_stage_exit_reached", "details": []}

    # ── Iteration limits ─────────────────────────────────────────────────
    max_iterations = raw.get("max_iterations")
    loop_iteration = raw.get("loop_iteration", 0) or 0

    if max_iterations is not None and loop_iteration >= max_iterations:
        details.append(f"loop_iteration={loop_iteration} >= max_iterations={max_iterations}")
        return {"action": "stop", "reason": "max_iterations_reached", "details": details}

    # ── Consecutive failures ─────────────────────────────────────────────
    consecutive_failures = raw.get("consecutive_failures", 0) or 0
    max_consecutive_failures = raw.get("max_consecutive_failures", 3) or 3

    if consecutive_failures >= max_consecutive_failures:
        details.append(f"consecutive_failures={consecutive_failures} >= max={max_consecutive_failures}")
        return {"action": "request_user_decision", "reason": "consecutive_failures_exceeded", "details": details}

    # ── Worker report status ─────────────────────────────────────────────
    report = status["worker_report"]
    report_status = report["status"]
    phase = state.get("phase")

    # waiting_for_worker + no usable report → blocked or ask user
    if phase == "waiting_for_worker" and report_status in ("not_started", "placeholder"):
        details.append(f"phase={phase}, report={report_status}")
        return {"action": "blocked", "reason": "waiting_for_worker_report", "details": details}

    # Invalid worker report → rework
    if report_status == "invalid":
        if report.get("missing_sections"):
            details.append(f"missing sections: {', '.join(report['missing_sections'])}")
        return {"action": "request_rework", "reason": "worker_report_invalid", "details": details}

    # Valid report + waiting or review phase → review
    if report_status == "valid" and phase in ("waiting_for_worker", "review_pending"):
        details.append(f"phase={phase}, report={report_status}")
        return {"action": "review", "reason": "worker_report_valid_ready_for_review", "details": details}

    # ── Default: delegate if ready ───────────────────────────────────────
    if directive == "CONTINUE":
        details.append(f"phase={phase}, loop_control=CONTINUE")
        return {"action": "delegate", "reason": "ready_to_delegate", "details": details}

    # Fallback
    return {"action": "stop", "reason": "unknown_state", "details": [f"directive={directive}, phase={phase}"]}


def _parse_loop_log_entries(loop_log_path: Path) -> list[str]:
    """Parse loop-log.md into a list of entry strings (one per ## heading section).

    Returns empty list if the file is missing or empty.
    """
    if not loop_log_path.exists():
        return []

    content = loop_log_path.read_text().strip()
    if not content:
        return []

    lines = content.splitlines()
    entries: list[str] = []
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_lines:
                entries.append("\n".join(current_lines).strip())
            current_lines = [line]
        elif line.startswith("# "):
            continue
        elif current_lines:
            current_lines.append(line)

    if current_lines:
        entries.append("\n".join(current_lines).strip())

    return entries


def get_resume_context(project_root: Path, log_entries: int = 3) -> dict:
    """Deterministic read-only resume-context helper.

    Collects everything an interrupted supervisor loop needs to recover:
    current stage/phase, loop iteration, loop-control directive, next-action
    decision, handoff text, recent loop-log entries, branch-policy status,
    and worker-report status.

    Missing files are handled gracefully — None or empty values are returned
    rather than raising.

    Returns dict with:
        stage, phase, loop_iteration, loop_control, next_action,
        handoff, recent_log_entries, branch_policy, worker_report
    """
    # ── State ────────────────────────────────────────────────────────────
    stage = None
    phase = None
    loop_iteration = None
    try:
        state = parse_state_yaml(project_root)
        stage = state.get("stage")
        phase = state.get("phase")
        loop_iteration = state.get("loop_iteration")
    except (FileNotFoundError, ValueError):
        pass

    # ── Loop control ─────────────────────────────────────────────────────
    loop_control = classify_loop_control(project_root)

    # ── Next-action decision ─────────────────────────────────────────────
    next_action: dict = {"action": None, "reason": None, "details": []}
    try:
        next_action = decide_next_action(project_root)
    except Exception:
        pass

    # ── Handoff ──────────────────────────────────────────────────────────
    handoff_path = project_root / ".pm" / "runtime" / "handoff.md"
    handoff: str | None = None
    if handoff_path.exists():
        text = handoff_path.read_text().strip()
        if text:
            handoff = text

    # ── Loop log entries ─────────────────────────────────────────────────
    loop_log_path = project_root / ".pm" / "runtime" / "loop-log.md"
    all_entries = _parse_loop_log_entries(loop_log_path)
    recent = all_entries[-log_entries:] if log_entries > 0 else []

    # ── Branch policy ────────────────────────────────────────────────────
    branch_policy = validate_branch_policy(project_root)

    # ── Worker report ────────────────────────────────────────────────────
    worker_report = validate_worker_report(project_root)

    return {
        "stage": stage,
        "phase": phase,
        "loop_iteration": loop_iteration,
        "loop_control": loop_control,
        "next_action": next_action,
        "handoff": handoff,
        "recent_log_entries": recent,
        "branch_policy": branch_policy,
        "worker_report": worker_report,
    }


def get_loop_summary(project_root: Path) -> dict:
    """Read-only loop run summary for supervisor audit."""
    loop_log_path = project_root / ".pm" / "runtime" / "loop-log.md"
    entries = _parse_loop_log_entries(loop_log_path)

    total_iterations = 0
    total_reworks = 0
    last_commit = None
    delivered = []
    blockers = 0
    dates = []

    for entry in entries:
        lines = entry.splitlines()
        entry_text = "\n".join(lines)

        if "- Verdict: accepted" in entry_text:
            total_iterations += 1
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("- Accepted result:"):
                    summary = stripped[len("- Accepted result:"):].strip()[:120]
                    delivered.append(summary)
                    break

        if "- Phase: needs_rework" in entry_text:
            total_reworks += 1

        if "Phase: blocked" in entry_text or "action: blocked" in entry_text:
            blockers += 1

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- Worker commit:") or stripped.startswith("- Worker commits:"):
                commit_part = stripped.split(":", 1)[1].strip()
                commits = [c.strip().rstrip(",") for c in commit_part.split(",") if c.strip()]
                if commits:
                    last_commit = commits[-1]
            if stripped.startswith("- Date:"):
                date_val = stripped[len("- Date:"):].strip()
                if date_val:
                    dates.append(date_val)

    valid_rate = None
    consecutive_failures = 0
    stage = None
    iteration_valid_count = 0
    iteration_total_count = 0

    try:
        state = parse_state_yaml(project_root)
        raw = state.get("raw", {})
        iteration_valid_count = raw.get("raw", {}).get("iteration_valid_count") or 0
        iteration_total_count = raw.get("raw", {}).get("iteration_total_count") or 0
        if iteration_total_count > 0:
            valid_rate = round(iteration_valid_count / iteration_total_count, 2)
        consecutive_failures = raw.get("consecutive_failures") or 0
        stage = state.get("stage")
    except (FileNotFoundError, ValueError):
        pass

    duration_note = ""
    if dates:
        unique = list(dict.fromkeys(dates))
        if len(unique) == 1:
            duration_note = unique[0]
        else:
            duration_note = f"{unique[0]} → {unique[-1]}"

    return {
        "total_iterations": total_iterations,
        "total_reworks": total_reworks,
        "valid_rate": valid_rate,
        "iteration_valid_count": iteration_valid_count,
        "iteration_total_count": iteration_total_count,
        "consecutive_failures": consecutive_failures,
        "stage": stage,
        "last_commit": last_commit,
        "duration_note": duration_note,
        "delivered": delivered,
        "blockers": blockers,
    }


def get_failure_breaker_status(project_root: Path) -> dict:
    """Read-only check of whether the consecutive failure breaker has been triggered.

    Returns dict with: triggered (bool), consecutive_failures (int),
    max_consecutive_failures (int), reason (str).
    """
    state_path = project_root / ".pm" / "runtime" / "state.yaml"
    if not state_path.exists():
        return {
            "triggered": False,
            "consecutive_failures": 0,
            "max_consecutive_failures": 0,
            "reason": "state.yaml unavailable",
        }

    try:
        text = state_path.read_text()
        if not text.strip():
            return {
                "triggered": False,
                "consecutive_failures": 0,
                "max_consecutive_failures": 0,
                "reason": "state.yaml unavailable",
            }
        raw = yaml.safe_load(text) or {}
    except (yaml.YAMLError, OSError):
        return {
            "triggered": False,
            "consecutive_failures": 0,
            "max_consecutive_failures": 0,
            "reason": "state.yaml unavailable",
        }

    consecutive = raw.get("consecutive_failures", 0) or 0
    max_consecutive = raw.get("max_consecutive_failures", 3) or 3
    triggered = consecutive >= max_consecutive

    if triggered:
        reason = f"Worker failed {consecutive} consecutive times. Escalating to user."
    else:
        reason = "Breaker not triggered."

    return {
        "triggered": triggered,
        "consecutive_failures": consecutive,
        "max_consecutive_failures": max_consecutive,
        "reason": reason,
    }


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
    branch_policy = validate_branch_policy(project_root)

    failure_breaker = get_failure_breaker_status(project_root)

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
        "branch_policy": branch_policy,
        "failure_breaker": failure_breaker,
    }
