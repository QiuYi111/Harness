from pathlib import Path

SPEC_ARTIFACTS = ["spec.md", "plan.md", "tasks.md", "eval.md", "report.md"]


def check_spec_completeness(spec_dir: Path) -> list[tuple[str, str]]:
    results = []
    for artifact in SPEC_ARTIFACTS:
        path = spec_dir / artifact
        if not path.exists():
            results.append(("fail", f"{artifact} missing"))
        elif path.stat().st_size == 0:
            results.append(("fail", f"{artifact} is empty"))
        else:
            results.append(("pass", f"{artifact} present"))
    return results


def check_test_coverage(spec_dir: Path, project_root: Path) -> list[tuple[str, str]]:
    results = []
    tasks_path = spec_dir / "tasks.md"
    if not tasks_path.exists():
        results.append(("warn", "tasks.md not found — cannot check coverage"))
        return results

    content = tasks_path.read_text(errors="replace").lower()
    has_test_task = "test" in content or "tdd" in content or "spec" in content
    if has_test_task:
        results.append(("pass", "test tasks referenced in tasks.md"))
    else:
        results.append(("warn", "no test tasks found in tasks.md"))
    return results


def check_artifact_consistency(spec_dir: Path) -> list[tuple[str, str]]:
    results = []
    spec_path = spec_dir / "spec.md"
    plan_path = spec_dir / "plan.md"

    if spec_path.exists() and plan_path.exists():
        spec_text = spec_path.read_text(errors="replace").lower()
        plan_text = plan_path.read_text(errors="replace").lower()

        if "acceptance" in spec_text or "criteria" in spec_text:
            results.append(("pass", "spec has acceptance criteria"))
        else:
            results.append(("warn", "spec missing acceptance criteria"))

        if "rollback" in plan_text or "rollback" in spec_text:
            results.append(("pass", "plan has rollback section"))
        else:
            results.append(("warn", "plan missing rollback section"))
    return results


def run_eval(spec_dir: Path, project_root: Path) -> dict:
    if not spec_dir.exists():
        return {"error": f"spec directory not found: {spec_dir}", "ok": False}

    all_results = []
    all_results.extend(check_spec_completeness(spec_dir))
    all_results.extend(check_test_coverage(spec_dir, project_root))
    all_results.extend(check_artifact_consistency(spec_dir))

    passed = sum(1 for r in all_results if r[0] == "pass")
    failed = sum(1 for r in all_results if r[0] == "fail")
    warnings = sum(1 for r in all_results if r[0] == "warn")

    return {
        "feature": spec_dir.name,
        "results": all_results,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "ok": failed == 0,
    }
