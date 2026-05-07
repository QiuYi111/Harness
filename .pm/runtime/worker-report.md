# Worker Report

## Task summary

Add a read-only branch correction plan helper (`get_branch_correction_plan`) so the supervisor can recover from branch drift without guessing or mutating git state.

## What was done

- **Added**: `get_branch_correction_plan()` in `scripts/harness_runtime/pm_runtime.py`
  - Purely read-only function that inspects current branch, expected goal branch, and ancestry relationships
  - Returns one of 5 statuses: `ok`, `safe_fast_forward_goal_branch`, `safe_switch_to_goal_branch`, `manual_review_required`, `unknown`
  - Suggests non-destructive correction commands when safe to do so

- **Added**: `pm-branch-plan` CLI command in `scripts/harness_runtime/cli.py`
  - Click command printing formatted branch correction plan
  - Follows same pattern as existing `pm-status`, `pm-next`, `pm-resume` commands

- **Updated**: `Makefile`
  - Added `pm-branch-plan` to `.PHONY`
  - Added `pm-branch-plan` target with help text

- **Added**: 8 focused tests in `tests/test_pm_runtime.py`
  - `TestGetBranchCorrectionPlan` class with all spec-required test cases
  - All git subprocess calls mocked (no real git repos created)

## Changed files

- `scripts/harness_runtime/pm_runtime.py` — added `get_branch_correction_plan()` function
- `scripts/harness_runtime/cli.py` — added import and `pm-branch-plan` command
- `Makefile` — added `.PHONY` entry and target
- `tests/test_pm_runtime.py` — added `TestGetBranchCorrectionPlan` with 8 tests

## Commands run

```
$ make test
65 passed in 0.68s
EXIT: 0

$ make verify-ai
47 passed, 0 failed, 1 warnings
🎉 All required checks passed.
EXIT: 0

$ make pm-status
✅ PM runtime state is valid.
Branch policy: ✅ ok
EXIT: 0

$ make pm-next
Action: delegate
Reason: ready_to_delegate
EXIT: 0

$ make pm-resume
Stage: delivery, Phase: worker_running, Loop iteration: 6
EXIT: 0

$ make pm-branch-plan
=== PM Branch Correction Plan ===
Status: ok
Current branch: codex/dogfood
Expected branch: codex/dogfood
Reason: already on expected branch 'codex/dogfood'
No correction commands suggested.
EXIT: 0

$ make verify
(test + verify-ai + pm-status all pass)
EXIT: 0

$ git status --short
 M Makefile
 M scripts/harness_runtime/cli.py
 M scripts/harness_runtime/pm_runtime.py
 M tests/test_pm_runtime.py
(verify.py and opencode-cli/* are pre-existing dirty, not touched by this task)
```

## Test results

65 tests pass (8 new tests in `TestGetBranchCorrectionPlan`). All pre-existing tests continue to pass.

New tests:
- `test_matching_branch_returns_ok` — current == expected → ok
- `test_no_goal_branch_returns_ok` — no goal branch configured → ok
- `test_expected_ancestor_of_current_returns_fast_forward` — safe fast-forward with 2 commands
- `test_current_ancestor_of_expected_returns_switch` — safe switch with 1 command
- `test_diverged_returns_manual_review` — neither is ancestor → manual review
- `test_nonexistent_expected_branch_returns_manual_review` — branch doesn't exist → manual review
- `test_git_error_returns_unknown` — git inspection failure → unknown
- `test_read_only_does_not_mutate` — verifies no file mutations

## Acceptance criteria

- [x] `get_branch_correction_plan()` is purely read-only (never mutates git state)
- [x] Function returns correct status for all 5 cases: ok, safe_fast_forward_goal_branch, safe_switch_to_goal_branch, manual_review_required, unknown
- [x] CLI command `harness pm-branch-plan` runs without error and prints formatted output
- [x] Makefile target `pm-branch-plan` added and works
- [x] All 8 required tests pass with mocked git subprocess calls
- [x] Import added to both `pm_runtime.py` exports and `cli.py`
- [x] `.PHONY` line in Makefile updated
- [x] All verification commands pass (make test, make verify-ai, make pm-status, make pm-next, make pm-resume, make pm-branch-plan, make verify)
- [x] Forbidden files not touched (verify.py, opencode-cli/SKILL.md, opencode-cli/references/patterns.md, .pm/stable/*)

## Problems encountered

None.

## Deviations

None. All changes stayed within allowed scope.

## Evidence

- Branch: `codex/dogfood` (branch-policy ok)
- 65/65 tests pass (8 new + 57 existing)
- All 7 Makefile targets exit 0 (test, verify-ai, pm-status, pm-next, pm-resume, pm-branch-plan, verify)
- `harness verify-ai` passes (47/0/1)
- Forbidden files show pre-existing diffs only, none staged by this task
