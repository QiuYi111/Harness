# Maintenance Index Template

Create at `maintenance/index.md` in the target project.

---

```markdown
# Maintenance Index

One row per debug session. Status tracks the current phase.

## Active

| Date | ID | Status | Risk | Summary |
|---|---|---|---|---|
| 2026-05-05 | cache-aware-write | patching | leaf | Fixed cache-aware context write formatting |
| 2026-05-06 | login-flaky | diagnosing | branch | Flaky login test under concurrent load |

## Closed

| Date | ID | Risk | Summary | Root Cause |
|---|---|---|---|---|
| 2026-05-04 | missing-validation | leaf | Added input validation for edge case | Empty string bypassed entry check |

## Cannot Reproduce

| Date | ID | Summary | Investigation Summary |
|---|---|---|---|
| | | | |

## Escalated

| Date | ID | Risk | Reason |
|---|---|---|---|
| | | | 3+ failed hypotheses |
| | | | Architecture concern |
```
