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

Use for ANY technical issue in existing code:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues
- Regressions

**Use ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- The fix "looks obvious" (symptoms ≠ root cause)

## Prerequisites

- Read `../../references/DOMAIN-AWARENESS.md` for project terminology
- This is existing code (not green-field). If no codebase exists, use `harness-specify` instead.

## The Seven Phases

You MUST complete each phase before proceeding to the next.

### Phase 0: Intake

**Create the maintenance record.**

1. Determine debug ID: `YYYY-MM-DD-<short-slug>`
2. Create `maintenance/debug/<id>/record.md` from template
3. Record symptom, expected behavior, actual behavior

**Trigger conditions:**
- bug, test failure, regression, not working, unexpected behavior
- fix request without new feature intent
- stack trace / error log present

### Phase 1: Reproduce

**Iron Law: Cannot reproduce → cannot fix.**

1. **Reproduce consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If flaky → gather more data, don't guess

2. **Record reproduction**
   - Exact command, input, environment
   - Expected output vs actual output
   - Determinism: deterministic / flaky / not reproduced

3. **Update record.md** with reproduction section

**If not reproducible:** Enter evidence gathering (Phase 2). Do NOT propose fixes.

### Phase 2: Evidence

**Iron Law: Evidence before hypotheses.**

Gather:
- Error logs, stack traces (read completely, note line numbers and error codes)
- Failing test output
- `git diff` / recent commits (`git log --oneline -20`)
- Runtime state, environment variables
- Nearby working examples for comparison
- For multi-component systems: add diagnostic instrumentation at EACH component boundary

**Multi-component evidence gathering:**
```
For EACH component boundary:
  - Log what data enters component
  - Log what data exits component
  - Verify environment/config propagation
  - Check state at each layer

Run once to gather evidence showing WHERE it breaks
THEN analyze evidence to identify failing component
```

**For errors deep in call stack:** Use backward tracing technique.
See `./references/root-cause-tracing.md` for the complete method.

Quick version:
- Where does bad value originate?
- What called this with bad value?
- Keep tracing up until you find the source
- Fix at source, not at symptom

**Update record.md** with evidence section. Save artifacts to `maintenance/debug/<id>/evidence/` if large.

### Phase 3: Diagnose

**This phase must output a clear root cause.**

1. **Find working examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare against references**
   - Read reference implementation COMPLETELY
   - List every difference, however small
   - Don't assume "that can't matter"

3. **Form single hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down in record.md
   - Be specific, not vague

4. **Test minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

5. **Verify before continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

**Rules:**
```
One hypothesis → one minimal verification
Failed hypothesis → return to Phase 2
Cannot stack patches
```

**Update record.md** with:
- Root cause (mandatory, must be explicit)
- Hypotheses tried table

### Phase 4: Patch

**Iron Law: Only fix the root cause. No drive-by refactoring.**

1. **Classify risk first**
   ```bash
   harness classify-risk
   ```
   If risk returns **core** or **infra**: STOP. Require human approval before patching.
   Bug fixes are NOT exempt from risk gates.

 2. **Create failing test**
    - For **leaf** risk: write test inline in this skill
    - For **branch/core/infra** risk: formally invoke `harness-tdd` RED role to write the test, then GREEN role for the fix. This ensures role isolation and `verify-ai` enforcement.
    - Simplest possible reproduction
    - Automated test preferred
    - MUST have test before fixing
    - The test MUST fail first — watch it fail

3. **Implement minimal fix**
   - Address the root cause identified in Phase 3
   - ONE change at a time
   - No "while I'm here" improvements

4. **Verify fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

**FORBIDDEN:**
```
Drive-by refactoring
Drive-by formatting
Drive-by dependency upgrades
Drive-by API changes
Drive-by renaming
Deleting tests to make green
```

**Patch output must include:**
```
Patch intent:
Changed files:
Behavior changed:
Behavior preserved:
Why this is minimal:
```

**After fix, add defense-in-depth validation:**
- Entry point: validate input at API boundary
- Business logic: ensure data makes sense
- Environment guards: prevent dangerous operations in specific contexts
- Debug instrumentation: capture context for forensics

See `./references/defense-in-depth.md` for the complete pattern.

**Update record.md** with minimal patch section.

### Phase 5: Regression

**Iron Law: Every bug fix must leave anti-recurrence evidence.**

Priority:
1. **Automated test**: best
2. **Deterministic reproduction script**: acceptable
3. **Manual check**: temporary only, never long-term

**Regression test must:**
- Fail before the patch
- Pass after the patch
- Be verified with red-green cycle

**Update record.md** with regression section.

### Phase 6: Review

**Iron Law: Must review diff before closing.**

Run:
```bash
git diff
harness classify-risk
```

Answer:
1. Any unrelated files?
2. Any unrelated formatting?
3. Any public API changes?
4. Any removed behavior?
5. Any new regressions introduced?
6. How to rollback?

**Update record.md** with review section.

### Phase 7: Close

**Close conditions — base (all must be met):**
- [ ] Bug reproduced or reproduction failure documented
- [ ] Root cause written clearly
- [ ] Patch is minimal (only fixes root cause)
- [ ] Regression test added and passing
- [ ] Diff reviewed
- [ ] Risk level classified
- [ ] `make verify` passes (if available)

**Additional close conditions by risk level:**
- **leaf**: Base conditions sufficient
- **branch**: + `eval.md` produced (load `harness-eval`)
- **core/infra**: + `eval.md` and `report.md` produced + human sign-off on record.md

**Cannot-reproduce outcome:** If evidence is insufficient after thorough investigation (Phase 2 exhausted):
1. Document everything investigated in record.md
2. Implement appropriate monitoring/logging for future investigation
3. Close with status `cannot-reproduce` (not `closed`)
4. Record in index.md with summary of what was checked

**Post-close routing:**
- If risk ≥ branch: load `harness-eval`, then `harness-report`
- If risk = leaf: close is sufficient

**Update `maintenance/index.md`** with closed entry.

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

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "One more fix attempt" (when already tried 2+)
- Each fix reveals new problem in different place
- Proposing solutions before tracing data flow
- **"This is a simple bug, I don't need the process"**

**ALL of these mean: STOP. Return to Phase 1.**

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the design, don't fix again. |
| "I'll refactor while I'm here" | Debug is repair, not renovation. One change. |
| "The bug is obvious" | Obvious symptoms often hide non-obvious causes. |

## Risk Integration

Debug flow does NOT bypass Harness risk gates. It calls `harness-risk` at two points:

1. **Before patching** (Phase 4): Classify blast radius. core/infra → human approval required.
2. **Before closing** (Phase 6): Re-check diff. Risk may have escalated.

Rule: **Debug is not a low-risk exemption. A bug fix can still be a core/infra change.**

## Project File Structure

When this skill runs in a target project:

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

For small bugs, `record.md` contains everything. For complex bugs, split into separate files as needed.

**MVP note:** All sections currently live in `record.md`. When a record exceeds ~200 lines, split into separate files (`repro.md`, `regression.md`, `review.md`) following the structure in the design doc. The index should always be one row per debug session, not one row per phase.

## References

- `../../references/DOMAIN-AWARENESS.md` — project terminology and DDD rules
- `../../references/ROUTING_TABLE.md` — routing table (includes debug routes)
- `./references/root-cause-tracing.md` — backward tracing through call stacks
- `./references/defense-in-depth.md` — multi-layer validation after fixes
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
