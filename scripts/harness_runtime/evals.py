import yaml
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


def check_gates(spec_dir: Path, gates_path: Path | None = None) -> list[tuple[str, str]]:
    if gates_path is None:
        gates_path = Path(__file__).resolve().parent.parent.parent / "references" / "policies" / "gates.yaml"

    results = []
    if not gates_path.exists():
        results.append(("warn", "gates.yaml not found — skipping gate checks"))
        return results

    gates_data = yaml.safe_load(gates_path.read_text())
    gates = gates_data.get("gates", {})

    for gate_name, gate_def in gates.items():
        check_str = gate_def.get("check", "")
        if not check_str or "{feature}" not in check_str:
            continue

        feature_id = spec_dir.name
        resolved = check_str.replace("{feature}", feature_id)

        if "exists" in resolved:
            file_path_str = resolved.split(" exists")[0].strip()
            file_path = spec_dir / Path(file_path_str).name
            if file_path.exists():
                results.append(("pass", f"gate:{gate_name}", f"exists: {file_path.name}"))
            else:
                results.append(("fail", f"gate:{gate_name}", f"missing: {file_path.name}"))
        elif "contains" in resolved:
            candidate = resolved.split(" contains")[0].strip()
            candidate_path = spec_dir / Path(candidate).name
            section = resolved.split(" contains ")[1].strip()
            if candidate_path.exists():
                content = candidate_path.read_text(errors="replace").lower()
                if section.lower() in content:
                    results.append(("pass", f"gate:{gate_name}", f"contains '{section}'"))
                else:
                    results.append(("warn", f"gate:{gate_name}", f"missing '{section}' section"))
            else:
                results.append(("warn", f"gate:{gate_name}", f"file not found: {candidate}"))

    return results


def run_eval(spec_dir: Path, project_root: Path, gates_path: Path | None = None) -> dict:
    if not spec_dir.exists():
        return {"error": f"spec directory not found: {spec_dir}", "ok": False}

    all_results = []
    all_results.extend(check_spec_completeness(spec_dir))
    all_results.extend(check_test_coverage(spec_dir, project_root))
    all_results.extend(check_artifact_consistency(spec_dir))
    all_results.extend(check_gates(spec_dir, gates_path))

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
