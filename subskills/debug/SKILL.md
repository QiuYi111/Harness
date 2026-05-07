---
name: harness-maintain-debug
description: >
  Systematic debugging as a maintenance transaction. Use when encountering bugs, test failures,
  regressions, unexpected behavior, or any fix request in existing code. Enforces:
  symptom → reproduce → evidence → root cause → minimal patch → regression → review → close.
  Triggers on: "debug this", "fix this bug", "test failed", "not working", "regression",
  "unexpected behavior", "why is this broken", "修一下", "为什么失败".
---

# Harness Maintain: Debug

Systematic debugging as a tracked maintenance transaction. Every debug session produces a traceable repair record with enforced gates.

## Iron Laws

```
1. NO PATCH WITHOUT REPRODUCTION AND EVIDENCE.
2. NO COMPLETION WITHOUT REGRESSION TEST.
3. NO CONTINUED PATCHING AFTER 3 FAILED HYPOTHESES — ESCALATE.
```

Violating the letter of these laws is violating the spirit of debugging.

## When to Use

Use for ANY technical issue in existing code: test failures, bugs in production, unexpected behavior, performance problems, build failures, integration issues, regressions.

See `./references/anti-patterns.md` for "use ESPECIALLY when" and "don't skip when" guidance.

## Prerequisites

- Read `../../references/DOMAIN-AWARENESS.md` for project terminology
- This is existing code (not green-field). If no codebase exists, use `harness-specify` instead.

## The Seven Phases — Overview

You MUST complete each phase before proceeding to the next. Read `./references/phases-detail.md` for full steps.

| Phase | Name | One-line |
|-------|------|----------|
| 0 | Intake | Create the maintenance record, determine debug ID |
| 1 | Reproduce | Reproduce the issue consistently, record exact steps |
| 2 | Evidence | Gather logs, traces, diffs, multi-component boundary data |
| 3 | Diagnose | Find working examples, form single hypothesis, test minimally |
| 4 | Patch | Classify risk, create failing test, implement minimal fix |
| 5 | Regression | Add anti-recurrence test, verify red-green cycle |
| 6 | Review | Review diff, answer checklist, re-classify risk |
| 7 | Close | Verify all conditions met, route by risk level |

## State Machine

```
intake
  ↓
reproducing
  ├─ not-reproduced → evidence-needed
  │     └─ cannot-reproduce → close-with-note
  └─ reproduced
        ↓
  diagnosing
        ↓
  root-caused
        ↓
  patching ──── [risk gate: core/infra → human approval]
        ↓
  regression
        ↓
  review
        ↓
  closed
  └─ (if risk ≥ branch → eval → report)
```

**Failure escalation:**
```
hypothesis failed once     → return to evidence
hypothesis failed twice    → re-read code, compare working examples
three failed patches       → ESCALATE to architecture-review
```

**Escalation rule:** Three failed patches means the architecture may be wrong, not the fix. Stop and discuss with the human before attempting more fixes.

## Risk Integration

Debug flow does NOT bypass Harness risk gates. It calls `harness-risk` at two points:

1. **Before patching** (Phase 4): Classify blast radius. core/infra → human approval required.
2. **Before closing** (Phase 6): Re-check diff. Risk may have escalated.

Rule: **Debug is not a low-risk exemption. A bug fix can still be a core/infra change.**

## Project File Structure

```
project/
├── maintenance/
│   ├── index.md                          # maintenance log index
│   └── debug/
│       └── YYYY-MM-DD-<slug>/
│           ├── record.md                  # debug record (required)
│           ├── evidence/                  # logs, traces, patches (if needed)
│           └── ...
```

For small bugs, `record.md` contains everything. For complex bugs, split into separate files as needed. All sections currently live in `record.md`. When a record exceeds ~200 lines, split into separate files (`repro.md`, `regression.md`, `review.md`). The index should always be one row per debug session, not one row per phase.

## References

- `../../references/DOMAIN-AWARENESS.md` — project terminology and DDD rules
- `../../references/ROUTING_TABLE.md` — routing table (includes debug routes)
- `./references/root-cause-tracing.md` — backward tracing through call stacks
- `./references/defense-in-depth.md` — multi-layer validation after fixes
- `./references/phases-detail.md` — full instructions for all seven phases
- `./references/anti-patterns.md` — red flags, rationalizations, when to use process
- `../../references/templates/DEBUG_RECORD_TEMPLATE.md` — record template
- `../../references/templates/DEBUG_INDEX_TEMPLATE.md` — index template

## Related Skills

- **harness-risk** — blast radius classification before and after patching
- **harness-tdd** — for writing the failing test in Phase 4
- **harness-eval** — for final compliance check
- **harness-report** — for implementation report if needed

## Real-World Impact

From systematic debugging sessions (source: Superpowers project):
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common
