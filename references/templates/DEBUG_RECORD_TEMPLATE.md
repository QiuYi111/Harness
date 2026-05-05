# Debug Record Template

Create at `maintenance/debug/<YYYY-MM-DD-<slug>/record.md` for each debug session.

---

```markdown
# Debug Record: <short-description>

## Status

- [ ] Intake
- [ ] Reproduced
- [ ] Evidence collected
- [ ] Root cause identified
- [ ] Minimal patch applied
- [ ] Regression verified
- [ ] Diff reviewed
- [ ] Closed

## Symptom

What is visibly wrong?

## Expected Behavior

What should happen?

## Actual Behavior

What actually happens?

## Reproduction

Exact command, input, environment, and observed output.

```
Command:
...
Expected:
...
Actual:
...
Determinism: deterministic / flaky / not reproduced
```

## Evidence

Logs, stack traces, debugger observations, failing tests, git diff, runtime state.
For large artifacts, save to `evidence/` subdirectory.

## Root Cause

The real cause, not just the symptom. Must be explicit.

## Hypotheses Tried

| # | Hypothesis | Evidence | Result |
|---|---|---|---|
| 1 | | | |

## Minimal Patch

### Patch Intent

What changed, and why this is the smallest sufficient change.

### Changed Files

| File | Change |
|---|---|
| | |

### Behavior Changed

...

### Behavior Preserved

...

### Why This Is Minimal

...

## Defense-in-Depth

Validation layers added after fix:
- [ ] Entry point validation
- [ ] Business logic validation
- [ ] Environment guard
- [ ] Debug instrumentation

## Regression Test

### Failing-Before Condition

Before the patch, this command/test failed:

```bash
...
```

### Passing-After Condition

After the patch, this command/test passes:

```bash
...
```

### Test Added

- File:
- Test name:
- What it protects:

### Remaining Blind Spots

...

## Diff Review

- [ ] No unrelated refactor
- [ ] No unrelated formatting
- [ ] No public API change, or API change is documented
- [ ] Existing tests still pass
- [ ] Regression test added or documented
- [ ] Rollback path is obvious

## Risk

leaf / branch / core / infra

Classification rationale:

## Rollback

How to revert this change if needed:

## Follow-up

Things intentionally not fixed in this patch.
```
