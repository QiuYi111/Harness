"""Unit tests for pm_runtime module."""

import textwrap
import unittest
from pathlib import Path

from scripts.harness_runtime.pm_runtime import (
    classify_loop_control,
    decide_next_action,
    get_branch_correction_plan,
    get_failure_breaker_status,
    get_loop_summary,
    get_pm_status,
    get_resume_context,
    inspect_git,
    parse_state_yaml,
    validate_branch_policy,
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
    def _complete_report(self) -> str:
        return textwrap.dedent("""\
            # Worker Report

            ## Task summary
            Updated validate_worker_report().

            ## What was done
            Added required section validation.

            ## Changed files
            - scripts/harness_runtime/pm_runtime.py
            - tests/test_pm_runtime.py

            ## Commands run
            uv run harness pm-status --project /tmp

            ## Test results
            26 tests passed.

            ## Acceptance criteria
            - [x] validate_worker_report returns invalid with missing details
            - [x] placeholder reports not treated as valid

            ## Problems encountered
            None.

            ## Deviations
            None.

            ## Evidence
            All verification commands passed.
        """)

    def test_missing_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "not_started")
            self.assertEqual(result["missing_sections"], [])

    def test_empty_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text("")
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "not_started")
            self.assertEqual(result["missing_sections"], [])

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
            self.assertEqual(result["missing_sections"], [])

    def test_valid_report_with_all_sections(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                self._complete_report()
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["missing_sections"], [])

    def test_invalid_report_missing_sections(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                "# Worker Report\n\n## Objective\nDid the thing.\n\n## Changes\n- foo.py\n"
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "invalid")
            self.assertIn("Changed files", result["missing_sections"])
            self.assertIn("Commands run", result["missing_sections"])
            self.assertIn("Test results", result["missing_sections"])
            self.assertIn("Acceptance criteria", result["missing_sections"])
            self.assertIn("Problems encountered", result["missing_sections"])
            self.assertIn("Deviations", result["missing_sections"])
            self.assertIn("Evidence", result["missing_sections"])
            self.assertIn("Objective", result["sections"])
            self.assertIn("Changes", result["sections"])

    def test_alternative_heading_names_accepted(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                textwrap.dedent("""\
                    # Worker Report

                    ## Objective
                    Did the thing.

                    ## Changes
                    - foo.py

                    ## Files Changed
                    - foo.py

                    ## Verification
                    Ran tests.

                    ## Tests
                    All pass.

                    ## Acceptance criteria checklist
                    - [x] Done

                    ## Problems encountered
                    None.

                    ## Deviations from task
                    None.

                    ## Evidence
                    See above.
                """)
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "valid", result.get("reason"))
            self.assertEqual(result["missing_sections"], [])

    def test_no_headings_is_not_started(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                "Some plain text without any headings.\n"
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "not_started")

    def test_invalid_report_missing_sections_field_populated(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            (root / ".pm" / "runtime" / "worker-report.md").write_text(
                "# Worker Report\n\n## Objective\nDid the thing.\n"
            )
            result = validate_worker_report(root)
            self.assertEqual(result["status"], "invalid")
            self.assertGreater(len(result["missing_sections"]), 0)
            self.assertIn("reason", result)
            self.assertIn("missing", result["reason"])


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


class TestDecideNextAction(unittest.TestCase):

    _BASE_STATE = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        consecutive_failures: 0
        max_consecutive_failures: 3
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    _COMPLETE_REPORT = textwrap.dedent("""\
        # Worker Report

        ## Task summary
        Did the thing.

        ## What was done
        Added feature.

        ## Changed files
        - foo.py

        ## Commands run
        Ran tests.

        ## Test results
        All pass.

        ## Acceptance criteria
        - [x] Done

        ## Problems encountered
        None.

        ## Deviations
        None.

        ## Evidence
        See above.
    """)

    def _make_project(self, tmp: str, *,
                      state_yaml: str | None = None,
                      loop_control: str = "CONTINUE",
                      worker_report: str | None = None,
                      omit_state: bool = False) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        if not omit_state:
            files[".pm/runtime/state.yaml"] = state_yaml if state_yaml is not None else self._BASE_STATE
        files[".pm/runtime/active-stage.md"] = "stage"
        files[".pm/runtime/handoff.md"] = "handoff"
        files[".pm/runtime/loop-control"] = loop_control
        files[".pm/runtime/next-task.md"] = "task"
        if worker_report is not None:
            files[".pm/runtime/worker-report.md"] = worker_report
        _write_tree(root, files)
        return root

    def test_invalid_pm_runtime_returns_stop(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, omit_state=True)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "stop")
            self.assertEqual(result["reason"], "invalid_pm_runtime")

    def test_loop_control_stop(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_control="STOP")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "stop")
            self.assertEqual(result["reason"], "loop_control_STOP")

    def test_loop_control_needs_user_decision(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_control="NEEDS_USER_DECISION")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "request_user_decision")
            self.assertEqual(result["reason"], "loop_control_needs_user_decision")

    def test_loop_control_blocked(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_control="BLOCKED")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "blocked")
            self.assertEqual(result["reason"], "loop_control_BLOCKED")

    def test_loop_control_stage_exit_reached(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_control="STAGE_EXIT_REACHED")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "stop")
            self.assertEqual(result["reason"], "loop_control_stage_exit_reached")

    def test_max_iterations_reached(self):
        import tempfile
        state = textwrap.dedent("""\
            project_id: "test"
            current_stage: "feasibility"
            current_phase: "ready_to_delegate"
            loop_iteration: 5
            max_iterations: 5
            consecutive_failures: 0
            max_consecutive_failures: 3
            readiness: {}
            worker: {engine: opencode, role: intern, mode: sync}
            git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
            next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
            failure_tracking: {}
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "stop")
            self.assertEqual(result["reason"], "max_iterations_reached")

    def test_max_iterations_null_allows_continue(self):
        import tempfile
        state = textwrap.dedent("""\
            project_id: "test"
            current_stage: "feasibility"
            current_phase: "ready_to_delegate"
            loop_iteration: 99
            max_iterations: null
            consecutive_failures: 0
            max_consecutive_failures: 3
            readiness: {}
            worker: {engine: opencode, role: intern, mode: sync}
            git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
            next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
            failure_tracking: {}
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "delegate")

    def test_consecutive_failures_exceeded(self):
        import tempfile
        state = textwrap.dedent("""\
            project_id: "test"
            current_stage: "feasibility"
            current_phase: "waiting_for_worker"
            loop_iteration: 3
            max_iterations: 5
            consecutive_failures: 3
            max_consecutive_failures: 3
            readiness: {}
            worker: {engine: opencode, role: intern, mode: sync}
            git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
            next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
            failure_tracking: {}
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "request_user_decision")
            self.assertEqual(result["reason"], "consecutive_failures_exceeded")

    def test_waiting_for_worker_no_report_returns_blocked(self):
        import tempfile
        state = self._BASE_STATE.replace('"ready_to_delegate"', '"waiting_for_worker"')
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state, worker_report=None)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "blocked")
            self.assertEqual(result["reason"], "waiting_for_worker_report")

    def test_waiting_for_worker_placeholder_report_returns_blocked(self):
        import tempfile
        state = self._BASE_STATE.replace('"ready_to_delegate"', '"waiting_for_worker"')
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state,
                                      worker_report="# Worker Report\n\nNo worker report yet.\n")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "blocked")
            self.assertEqual(result["reason"], "waiting_for_worker_report")

    def test_invalid_worker_report_returns_request_rework(self):
        import tempfile
        state = self._BASE_STATE.replace('"ready_to_delegate"', '"waiting_for_worker"')
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state,
                                      worker_report="# Worker Report\n\n## Objective\nIncomplete.\n")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "request_rework")
            self.assertEqual(result["reason"], "worker_report_invalid")

    def test_valid_report_waiting_for_worker_returns_review(self):
        import tempfile
        state = self._BASE_STATE.replace('"ready_to_delegate"', '"waiting_for_worker"')
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state,
                                      worker_report=self._COMPLETE_REPORT)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "review")
            self.assertEqual(result["reason"], "worker_report_valid_ready_for_review")

    def test_valid_report_review_pending_returns_review(self):
        import tempfile
        state = self._BASE_STATE.replace('"ready_to_delegate"', '"review_pending"')
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state,
                                      worker_report=self._COMPLETE_REPORT)
            result = decide_next_action(root)
            self.assertEqual(result["action"], "review")
            self.assertEqual(result["reason"], "worker_report_valid_ready_for_review")

    def test_ready_to_delegate_with_continue_returns_delegate(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=self._BASE_STATE, loop_control="CONTINUE")
            result = decide_next_action(root)
            self.assertEqual(result["action"], "delegate")
            self.assertEqual(result["reason"], "ready_to_delegate")

    def test_branch_mismatch_returns_request_user_decision(self):
        import tempfile
        from unittest.mock import patch

        state = self._BASE_STATE.replace(
            'current_goal_branch: "b"',
            'current_goal_branch: "codex/dogfood"',
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}):
                result = decide_next_action(root)
            self.assertEqual(result["action"], "request_user_decision")
            self.assertEqual(result["reason"], "branch_policy_mismatch")

    def test_branch_match_allows_normal_flow(self):
        import tempfile
        from unittest.mock import patch

        state = self._BASE_STATE.replace(
            'current_goal_branch: "b"',
            'current_goal_branch: "codex/dogfood"',
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                result = decide_next_action(root)
            self.assertEqual(result["action"], "delegate")
            self.assertEqual(result["reason"], "ready_to_delegate")

    def test_missing_goal_branch_does_not_block(self):
        import tempfile
        from unittest.mock import patch

        state = self._BASE_STATE.replace(
            'current_goal_branch: "b"',
            'current_goal_branch: null',
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}):
                result = decide_next_action(root)
            self.assertEqual(result["action"], "delegate")
            self.assertEqual(result["reason"], "ready_to_delegate")


class TestValidateBranchPolicy(unittest.TestCase):
    _STATE_WITH_GOAL = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, current_goal_branch: "codex/dogfood", auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    _STATE_NO_GOAL = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    def _make_state_project(self, tmp: str, state_yaml: str) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        files[".pm/runtime/state.yaml"] = state_yaml
        files[".pm/runtime/active-stage.md"] = "stage"
        files[".pm/runtime/handoff.md"] = "handoff"
        files[".pm/runtime/loop-control"] = "CONTINUE"
        files[".pm/runtime/next-task.md"] = "task"
        _write_tree(root, files)
        return root

    def test_matching_branch_returns_ok(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_state_project(tmp, self._STATE_WITH_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                result = validate_branch_policy(root)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["current_branch"], "codex/dogfood")
            self.assertEqual(result["expected_branch"], "codex/dogfood")

    def test_mismatched_branch_returns_mismatch(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_state_project(tmp, self._STATE_WITH_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}):
                result = validate_branch_policy(root)
            self.assertEqual(result["status"], "mismatch")
            self.assertEqual(result["current_branch"], "main")
            self.assertEqual(result["expected_branch"], "codex/dogfood")
            self.assertIn("main", result["reason"])
            self.assertIn("codex/dogfood", result["reason"])

    def test_no_goal_branch_returns_ok(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_state_project(tmp, self._STATE_NO_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}):
                result = validate_branch_policy(root)
            self.assertEqual(result["status"], "ok")
            self.assertIn("no goal branch", result["reason"])

    def test_git_error_returns_unknown(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_state_project(tmp, self._STATE_WITH_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": None, "dirty_files": [], "error": "not a git repo"}):
                result = validate_branch_policy(root)
            self.assertEqual(result["status"], "unknown")

    def test_branch_policy_in_get_pm_status(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_state_project(tmp, self._STATE_WITH_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                status = get_pm_status(root)
            self.assertIn("branch_policy", status)
            self.assertEqual(status["branch_policy"]["status"], "ok")


class TestGetResumeContext(unittest.TestCase):
    _BASE_STATE = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 3
        consecutive_failures: 0
        max_consecutive_failures: 3
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, current_goal_branch: "codex/dogfood", auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    _LOOP_LOG = textwrap.dedent("""\
        # Loop Log

        ## Iteration 0

        - Date: 2026-05-07
        - Phase: product_definition
        - Summary: First entry.

        ## Supervisor Delegation 1

        - Date: 2026-05-07
        - Phase: waiting_for_worker
        - Summary: Second entry.

        ## Supervisor Review 1

        - Date: 2026-05-07
        - Phase: ready_to_delegate
        - Summary: Third entry.

        ## Supervisor Delegation 2

        - Date: 2026-05-07
        - Phase: waiting_for_worker
        - Summary: Fourth entry.
    """)

    def _make_project(self, tmp: str, *,
                      state_yaml: str | None = None,
                      loop_log: str | None = None,
                      handoff: str | None = None,
                      worker_report: str | None = None,
                      loop_control: str = "CONTINUE",
                      omit_handoff: bool = False,
                      omit_loop_log: bool = False) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        files[".pm/runtime/state.yaml"] = state_yaml or self._BASE_STATE
        files[".pm/runtime/active-stage.md"] = "stage"
        if not omit_handoff:
            files[".pm/runtime/handoff.md"] = handoff or "# Handoff\n\nResume here."
        if not omit_loop_log:
            files[".pm/runtime/loop-log.md"] = loop_log or self._LOOP_LOG
        files[".pm/runtime/loop-control"] = loop_control
        files[".pm/runtime/next-task.md"] = "task"
        if worker_report is not None:
            files[".pm/runtime/worker-report.md"] = worker_report
        _write_tree(root, files)
        return root

    def test_includes_next_action_decision(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertIsNotNone(ctx["next_action"])
            self.assertEqual(ctx["next_action"]["action"], "delegate")
            self.assertEqual(ctx["next_action"]["reason"], "ready_to_delegate")

    def test_last_n_loop_log_entries(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root, log_entries=2)
            self.assertEqual(len(ctx["recent_log_entries"]), 2)
            self.assertIn("Supervisor Review 1", ctx["recent_log_entries"][0])
            self.assertIn("Supervisor Delegation 2", ctx["recent_log_entries"][1])

    def test_log_entries_default_three(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertEqual(len(ctx["recent_log_entries"]), 3)

    def test_missing_handoff_handled_gracefully(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, omit_handoff=True)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertIsNone(ctx["handoff"])

    def test_missing_loop_log_handled_gracefully(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, omit_loop_log=True)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertEqual(ctx["recent_log_entries"], [])

    def test_includes_branch_policy(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertEqual(ctx["branch_policy"]["status"], "ok")

    def test_includes_worker_report_status(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertEqual(ctx["worker_report"]["status"], "not_started")

    def test_includes_stage_phase_iteration(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                ctx = get_resume_context(root)
            self.assertEqual(ctx["stage"], "feasibility")
            self.assertEqual(ctx["phase"], "ready_to_delegate")
            self.assertEqual(ctx["loop_iteration"], 3)

    def test_read_only_does_not_mutate_files(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            snapshot = {}
            for rel in [".pm/runtime/state.yaml", ".pm/runtime/handoff.md",
                        ".pm/runtime/loop-log.md", ".pm/runtime/loop-control"]:
                p = root / rel
                snapshot[rel] = p.read_text() if p.exists() else None

            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                get_resume_context(root)

            for rel, original in snapshot.items():
                p = root / rel
                current = p.read_text() if p.exists() else None
                self.assertEqual(current, original, f"{rel} was mutated")

    def test_missing_state_handled_gracefully(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for name in [
                "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
            ]:
                files[f".pm/stable/{name}"] = "content"
            files[".pm/runtime/active-stage.md"] = "stage"
            files[".pm/runtime/handoff.md"] = "# Handoff"
            files[".pm/runtime/loop-control"] = "CONTINUE"
            files[".pm/runtime/next-task.md"] = "task"
            _write_tree(root, files)

            ctx = get_resume_context(root)
            self.assertIsNone(ctx["stage"])
            self.assertIsNone(ctx["phase"])


class TestGetBranchCorrectionPlan(unittest.TestCase):
    _STATE_WITH_GOAL = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, current_goal_branch: "codex/dogfood", auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    _STATE_NO_GOAL = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        readiness: {}
        worker: {engine: opencode, role: intern, mode: sync}
        git: {branch_policy: supervisor_managed, auto_merge: false, auto_push: false}
        next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
        failure_tracking: {}
    """)

    def _make_project(self, tmp: str, state_yaml: str | None = None) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        files[".pm/runtime/state.yaml"] = state_yaml or self._STATE_WITH_GOAL
        files[".pm/runtime/active-stage.md"] = "stage"
        files[".pm/runtime/handoff.md"] = "handoff"
        files[".pm/runtime/loop-control"] = "CONTINUE"
        files[".pm/runtime/next-task.md"] = "task"
        _write_tree(root, files)
        return root

    @staticmethod
    def _mock_subprocess(verify_rc=0, ancestor_rc=1, reverse_rc=1):
        from unittest.mock import MagicMock
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            result = MagicMock()
            cmd = args[0] if args else kwargs.get("args", [])
            if "rev-parse" in cmd and "--verify" in cmd:
                result.returncode = verify_rc
            elif "--is-ancestor" in cmd and "HEAD" in cmd and cmd[-1] == "HEAD":
                result.returncode = ancestor_rc
            elif "--is-ancestor" in cmd:
                result.returncode = reverse_rc
            else:
                result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        return side_effect

    def test_matching_branch_returns_ok(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "codex/dogfood", "dirty_files": [], "error": None}):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["commands"], [])

    def test_no_goal_branch_returns_ok(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=self._STATE_NO_GOAL)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["commands"], [])

    def test_expected_ancestor_of_current_returns_fast_forward(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            mock_run = self._mock_subprocess(verify_rc=0, ancestor_rc=0, reverse_rc=1)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}), \
                 patch("scripts.harness_runtime.pm_runtime.subprocess.run", side_effect=mock_run):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "safe_fast_forward_goal_branch")
            self.assertEqual(len(result["commands"]), 2)

    def test_current_ancestor_of_expected_returns_switch(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            mock_run = self._mock_subprocess(verify_rc=0, ancestor_rc=1, reverse_rc=0)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}), \
                 patch("scripts.harness_runtime.pm_runtime.subprocess.run", side_effect=mock_run):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "safe_switch_to_goal_branch")
            self.assertEqual(len(result["commands"]), 1)

    def test_diverged_returns_manual_review(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            mock_run = self._mock_subprocess(verify_rc=0, ancestor_rc=1, reverse_rc=1)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}), \
                 patch("scripts.harness_runtime.pm_runtime.subprocess.run", side_effect=mock_run):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "manual_review_required")
            self.assertEqual(result["commands"], [])

    def test_nonexistent_expected_branch_returns_manual_review(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            mock_run = self._mock_subprocess(verify_rc=128)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}), \
                 patch("scripts.harness_runtime.pm_runtime.subprocess.run", side_effect=mock_run):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "manual_review_required")
            self.assertEqual(result["commands"], [])

    def test_git_error_returns_unknown(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": None, "dirty_files": [], "error": "not a git repo"}):
                result = get_branch_correction_plan(root)
            self.assertEqual(result["status"], "unknown")

    def test_read_only_does_not_mutate(self):
        import tempfile
        from unittest.mock import patch, MagicMock

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            snapshot = {}
            for rel in [".pm/runtime/state.yaml", ".pm/runtime/handoff.md",
                        ".pm/runtime/loop-control"]:
                p = root / rel
                snapshot[rel] = p.read_text() if p.exists() else None

            mock_run = self._mock_subprocess(verify_rc=0, ancestor_rc=0, reverse_rc=1)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                       return_value={"branch": "main", "dirty_files": [], "error": None}), \
                 patch("scripts.harness_runtime.pm_runtime.subprocess.run", side_effect=mock_run):
                get_branch_correction_plan(root)

            for rel, original in snapshot.items():
                p = root / rel
                current = p.read_text() if p.exists() else None
                self.assertEqual(current, original, f"{rel} was mutated")


class TestGetLoopSummary(unittest.TestCase):
    def _make_project(self, tmp: str, *,
                      loop_log: str | None = None,
                      state_yaml: str | None = None) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        if state_yaml is not None:
            files[".pm/runtime/state.yaml"] = state_yaml
        files[".pm/runtime/active-stage.md"] = "stage"
        files[".pm/runtime/handoff.md"] = "handoff"
        files[".pm/runtime/loop-control"] = "CONTINUE"
        files[".pm/runtime/next-task.md"] = "task"
        if loop_log is not None:
            files[".pm/runtime/loop-log.md"] = loop_log
        _write_tree(root, files)
        return root

    def test_empty_log_returns_zeros(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp)
            result = get_loop_summary(root)
            self.assertEqual(result["total_iterations"], 0)
            self.assertEqual(result["total_reworks"], 0)
            self.assertEqual(result["delivered"], [])
            self.assertEqual(result["blockers"], 0)
            self.assertIsNone(result["valid_rate"])
            self.assertIsNone(result["last_commit"])

    def test_single_accepted_iteration(self):
        import tempfile

        loop_log = textwrap.dedent("""\
            # Loop Log

            ## Iteration 1

            - Date: 2026-05-07
            - Phase: waiting_for_worker
            - Verdict: accepted
            - Accepted result: Implemented feature X
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_log=loop_log)
            result = get_loop_summary(root)
            self.assertEqual(result["total_iterations"], 1)
            self.assertEqual(len(result["delivered"]), 1)
            self.assertIn("Implemented feature X", result["delivered"][0])

    def test_rework_counted(self):
        import tempfile

        loop_log = textwrap.dedent("""\
            # Loop Log

            ## Iteration 1

            - Date: 2026-05-07
            - Phase: needs_rework
            - Summary: Worker report was incomplete.
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_log=loop_log)
            result = get_loop_summary(root)
            self.assertEqual(result["total_reworks"], 1)

    def test_valid_rate_from_state(self):
        import tempfile

        state_yaml = textwrap.dedent("""\
            project_id: "test"
            current_stage: "feasibility"
            current_phase: "ready_to_delegate"
            loop_iteration: 1
            readiness: {}
            worker: {engine: opencode, role: intern, mode: sync}
            git: {branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}
            next_action: {type: delegate, summary: x, blocked: false, needs_user_decision: false}
            failure_tracking: {}
            raw:
              iteration_valid_count: 5
              iteration_total_count: 5
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state_yaml)
            result = get_loop_summary(root)
            self.assertEqual(result["valid_rate"], 1.0)
            self.assertEqual(result["iteration_valid_count"], 5)
            self.assertEqual(result["iteration_total_count"], 5)

    def test_dates_extracted(self):
        import tempfile

        loop_log = textwrap.dedent("""\
            # Loop Log

            ## Iteration 1

            - Date: 2026-05-06
            - Phase: waiting_for_worker

            ## Iteration 2

            - Date: 2026-05-07
            - Phase: ready_to_delegate
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_log=loop_log)
            result = get_loop_summary(root)
            self.assertIn("→", result["duration_note"])
            self.assertIn("2026-05-06", result["duration_note"])
            self.assertIn("2026-05-07", result["duration_note"])

    def test_last_commit_extracted(self):
        import tempfile

        loop_log = textwrap.dedent("""\
            # Loop Log

            ## Iteration 1

            - Date: 2026-05-07
            - Worker commit: abc1234
            - Phase: waiting_for_worker
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_log=loop_log)
            result = get_loop_summary(root)
            self.assertEqual(result["last_commit"], "abc1234")

    def test_blockers_counted(self):
        import tempfile

        loop_log = textwrap.dedent("""\
            # Loop Log

            ## Iteration 1

            - Date: 2026-05-07
            - Phase: blocked
            - Summary: Waiting for user input.
        """)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, loop_log=loop_log)
            result = get_loop_summary(root)
            self.assertEqual(result["blockers"], 1)


class TestGetFailureBreakerStatus(unittest.TestCase):
    def _make_project(self, tmp: str, *,
                      state_yaml: str | None = None) -> Path:
        root = Path(tmp)
        files = {}
        for name in [
            "product.md", "roadmap.md", "architecture-guardrails.md", "acceptance-rubric.md"
        ]:
            files[f".pm/stable/{name}"] = "content"
        if state_yaml is not None:
            files[".pm/runtime/state.yaml"] = state_yaml
        files[".pm/runtime/active-stage.md"] = "stage"
        files[".pm/runtime/handoff.md"] = "handoff"
        files[".pm/runtime/loop-control"] = "CONTINUE"
        files[".pm/runtime/next-task.md"] = "task"
        _write_tree(root, files)
        return root

    _STATE_TEMPLATE = textwrap.dedent("""\
        project_id: "test"
        current_stage: "feasibility"
        current_phase: "ready_to_delegate"
        loop_iteration: 1
        consecutive_failures: {cf}
        max_consecutive_failures: {mcf}
        readiness: {{}}
        worker: {{engine: opencode, role: intern, mode: sync}}
        git: {{branch_policy: supervisor_managed, current_goal_branch: "b", auto_merge: false, auto_push: false}}
        next_action: {{type: delegate, summary: x, blocked: false, needs_user_decision: false}}
        failure_tracking: {{}}
    """)

    def test_no_failures_not_triggered(self):
        import tempfile

        state = self._STATE_TEMPLATE.format(cf=0, mcf=3)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = get_failure_breaker_status(root)
            self.assertFalse(result["triggered"])
            self.assertEqual(result["consecutive_failures"], 0)
            self.assertEqual(result["max_consecutive_failures"], 3)

    def test_at_max_triggered(self):
        import tempfile

        state = self._STATE_TEMPLATE.format(cf=3, mcf=3)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = get_failure_breaker_status(root)
            self.assertTrue(result["triggered"])
            self.assertEqual(result["consecutive_failures"], 3)
            self.assertIn("3 consecutive times", result["reason"])

    def test_over_max_triggered(self):
        import tempfile

        state = self._STATE_TEMPLATE.format(cf=5, mcf=3)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            result = get_failure_breaker_status(root)
            self.assertTrue(result["triggered"])
            self.assertEqual(result["consecutive_failures"], 5)
            self.assertIn("5 consecutive times", result["reason"])

    def test_missing_state_not_triggered(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pm" / "runtime").mkdir(parents=True)
            result = get_failure_breaker_status(root)
            self.assertFalse(result["triggered"])
            self.assertIn("unavailable", result["reason"])

    def test_pm_status_includes_breaker(self):
        import tempfile
        from unittest.mock import patch

        state = self._STATE_TEMPLATE.format(cf=0, mcf=3)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_project(tmp, state_yaml=state)
            with patch("scripts.harness_runtime.pm_runtime.inspect_git",
                        return_value={"branch": "b", "dirty_files": [], "error": None}):
                status = get_pm_status(root)
            self.assertIn("failure_breaker", status)
            self.assertFalse(status["failure_breaker"]["triggered"])


if __name__ == "__main__":
    unittest.main()
