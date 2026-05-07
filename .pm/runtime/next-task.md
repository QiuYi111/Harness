# Worker Task Packet

## Objective

Add a `get_failure_breaker_status()` read-only helper that checks whether the consecutive failure breaker has been triggered, so `pm-next` and `pm-status` can surface this without the supervisor manually inspecting state.yaml.

## Stage context

Stage 2: Unbounded `/goal` Dogfood. The safety-mechanisms reference says consecutive_failures >= max_consecutive_failures should trigger a stop, but `pm-next` does not explicitly surface this. The supervisor must currently read state.yaml fields manually. This helper makes the breaker status a first-class check.

## Read first

- `scripts/harness_runtime/pm_runtime.py`
- `scripts/harness_runtime/cli.py`
- `tests/test_pm_runtime.py`
- `Makefile`

## Task

1. Add `get_failure_breaker_status(project_root: Path) -> dict` in `pm_runtime.py`:
   - Reads `consecutive_failures` and `max_consecutive_failures` from state.yaml
   - Returns: `triggered` (bool), `consecutive_failures` (int), `max_consecutive_failures` (int), `reason` (str)
   - If triggered is True: reason = "Worker failed {n} consecutive times. Escalating to user."
   - If state.yaml missing or unreadable: triggered=False, reason="state.yaml unavailable"

2. Integrate into `decide_next_action()`: add a check AFTER the existing consecutive_failures block. The block already returns `request_user_decision` when the breaker triggers — this is correct. But also integrate into `get_pm_status()` to surface `failure_breaker` in the status dict.

3. Add to `get_pm_status()` return dict: add `failure_breaker` key with the breaker status dict.

4. Update `pm-status` CLI command to print the breaker status line.

5. Add focused tests in `TestGetFailureBreakerStatus`:
   - `test_no_failures_not_triggered` — consecutive=0, max=3 → not triggered
   - `test_at_max_triggered` — consecutive=3, max=3 → triggered
   - `test_over_max_triggered` — consecutive=5, max=3 → triggered
   - `test_missing_state_not_triggered` — no state.yaml → not triggered
   - `test_pm_status_includes_breaker` — get_pm_status() includes failure_breaker key

## Allowed scope

- `scripts/harness_runtime/pm_runtime.py`
- `scripts/harness_runtime/cli.py`
- `tests/test_pm_runtime.py`
- `.pm/runtime/worker-report.md` (final report only)

## Forbidden scope

- `scripts/harness_runtime/verify.py`
- `subskills/opencode-cli/SKILL.md`
- `subskills/opencode-cli/references/patterns.md`
- `.pm/stable/*`
- `Makefile` (no changes needed — existing targets sufficient)
- Any git mutation except the final task commit

## Acceptance criteria

- [ ] `get_failure_breaker_status()` is read-only and deterministic
- [ ] Returns triggered=True when consecutive >= max
- [ ] Returns triggered=False when consecutive < max or state unavailable
- [ ] `get_pm_status()` includes `failure_breaker` key
- [ ] `pm-status` CLI prints breaker status line
- [ ] All 5 test cases pass
- [ ] `make verify` passes
- [ ] One clear git commit

## Required verification commands

```bash
make test
make verify-ai
make pm-status
make verify
git status --short
git log --oneline -1
```

## Required report file

`.pm/runtime/worker-report.md`
