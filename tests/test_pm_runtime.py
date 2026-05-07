"""Unit tests for pm_runtime module."""

import textwrap
import unittest
from pathlib import Path

from scripts.harness_runtime.pm_runtime import (
    classify_loop_control,
    get_pm_status,
    inspect_git,
    parse_state_yaml,
    validate_pm_structure,
    validate_worker_report,
)

_FIXTURES = Path(__file__).resolve().parent / "_fixtures"


def _write_tree(base: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


class TestValidatePmStructure(unittest.TestCase):
    def test_valid_structure(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for name in [
                "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
            ]:
                files[f".pm/stable/{name}"] = "content"
            for name in [
                "state.yaml", "active-stage.md", "handoff.md", "loop-control", "next-task.md"
            ]:
                files[f".pm/runtime/{name}"] = "content"
            _write_tree(root, files)

            result = validate_pm_structure(root)
            self.assertTrue(result["ok"])
            self.assertEqual(result["missing"], [])
            self.assertEqual(result["empty"], [])

    def test_missing_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "stable").mkdir(parents=True)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "stable" / "product.md").write_text("x")

            result = validate_pm_structure(root)
            self.assertFalse(result["ok"])
            self.assertIn(".pm/stable/roadmap.md", result["missing"])

    def test_empty_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for name in [
                "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
            ]:
                files[f".pm/stable/{name}"] = "content"
            for name in [
                "state.yaml", "active-stage.md", "handoff.md", "loop-control", "next-task.md"
            ]:
                files[f".pm/runtime/{name}"] = "content"
            files[".pm/stable/acceptance-rubric.md"] = ""
            _write_tree(root, files)

            result = validate_pm_structure(root)
            self.assertFalse(result["ok"])
            self.assertIn(".pm/stable/acceptance-rubric.md", result["empty"])


class TestParseStateYaml(unittest.TestCase):
    def _valid_state_yaml(self) -> str:
        return textwrap.dedent("""\
            project_id: "test"
            current_stage: "feasibility"
            current_phase: "waiting_for_worker"
            loop_iteration: 1
            readiness:
              product_definition_ready: true
            worker:
              engine: opencode
              role: intern
              mode: sync
            git:
              branch_policy: supervisor_managed
              current_goal_branch: "codex/test"
              auto_merge: false
              auto_push: false
            next_action:
              type: delegate
              summary: do stuff
              blocked: false
              needs_user_decision: false
            failure_tracking: {}
        """)

    def test_parses_valid_state(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "state.yaml").write_text(self._valid_state_yaml())

            result = parse_state_yaml(root)
            self.assertEqual(result["stage"], "feasibility")
            self.assertEqual(result["phase"], "waiting_for_worker")
            self.assertEqual(result["loop_iteration"], 1)
            self.assertEqual(result["worker"]["engine"], "opencode")
            self.assertEqual(result["git_policy"]["branch_policy"], "supervisor_managed")
            self.assertFalse(result["next_action"]["blocked"])

    def test_missing_state_raises(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                parse_state_yaml(root)

    def test_empty_state_raises(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "state.yaml").write_text("")
            with self.assertRaises(ValueError):
                parse_state_yaml(root)

    def test_invalid_yaml_raises(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "state.yaml").write_text("{{invalid yaml")
            with self.assertRaises(ValueError):
                parse_state_yaml(root)


class TestClassifyLoopControl(unittest.TestCase):
    def test_continue(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("CONTINUE")
            result = classify_loop_control(root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["directive"], "CONTINUE")

    def test_stop(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("STOP")
            result = classify_loop_control(root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["directive"], "STOP")

    def test_needs_user_decision(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("NEEDS_USER_DECISION")
            result = classify_loop_control(root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["directive"], "NEEDS_USER_DECISION")

    def test_blocked(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("BLOCKED")
            result = classify_loop_control(root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["directive"], "BLOCKED")

    def test_stage_exit_reached(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("STAGE_EXIT_REACHED")
            result = classify_loop_control(root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["directive"], "STAGE_EXIT_REACHED")

    def test_unknown_directive(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("RUN_FOREVER")
            result = classify_loop_control(root)
            self.assertFalse(result["valid"])

    def test_legacy_user_decision_rejected(self):
        """USER_DECISION is not in the supervisor protocol; must be rejected."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "loop-control").write_text("USER_DECISION")
            result = classify_loop_control(root)
            self.assertFalse(result["valid"])
            self.assertEqual(result["directive"], "USER_DECISION")

    def test_missing_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = classify_loop_control(root)
            self.assertFalse(result["valid"])


class TestValidateWorkerReport(unittest.TestCase):
    def test_missing_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "not_started")

    def test_empty_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text("")
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "not_started")

    def test_placeholder_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                "# Worker Report\n\nNo worker report yet.\n"
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "placeholder")

    def test_valid_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                "# Worker Report\n\n## Objective\nDid the thing.\n\n## Changes\n- foo.py\n"
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "valid")
            self.assertIn("Objective", result["sections"])
            self.assertIn("Changes", result["sections"])


class TestGetPmStatus(unittest.TestCase):
    def test_ok_with_valid_state(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for name in [
                "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
            ]:
                files[f".pm/stable/{name}"] = "content"
            state_yaml = textwrap.dedent("""\
                project_id: "test"
                current_stage: "feasibility"
                current_phase: "waiting_for_worker"
                loop_iteration: 0
                readiness: {}
                worker: {engine: opencode, role: intern, mode: sync}
                git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
                next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
                failure_tracking: {}
            """)
            files[".pm/runtime/state.yaml"] = state_yaml
            files[".pm/runtime/active-stage.md"] = "stage"
            files[".pm/runtime/handoff.md"] = "handoff"
            files[".pm/runtime/loop-control"] = "CONTINUE"
            files[".pm/runtime/next-task.md"] = "task"
            _write_tree(root, files)

            result = get_pm_status(root)
            self.assertTrue(result["ok"])
            self.assertEqual(result["state"]["stage"], "feasibility")

    def test_not_ok_with_missing_files(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = get_pm_status(root)
            self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
