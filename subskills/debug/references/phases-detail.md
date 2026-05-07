# Debug Phases — Full Detail

Complete instructions for all seven phases. Read this before executing any phase.

---

## Phase 0: Intake

**Create the maintenance record.**

1. Determine debug ID: `YYYY-MM-DD-<short-slug>`
2. Create `maintenance/debug/<id>/record.md` from template
3. Record symptom, expected behavior, actual behavior

**Trigger conditions:**
- bug, test failure, regression, not working, unexpected behavior
- fix request without new feature intent
- stack trace / error log present

---

## Phase 1: Reproduce

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

---

## Phase 2: Evidence

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
See `./root-cause-tracing.md` for the complete method.

Quick version:
- Where does bad value originate?
- What called this with bad value?
- Keep tracing up until you find the source
- Fix at source, not at symptom

**Update record.md** with evidence section. Save artifacts to `maintenance/debug/<id>/evidence/` if large.

---

## Phase 3: Diagnose

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

---

## Phase 4: Patch

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

See `./defense-in-depth.md` for the complete pattern.

**Update record.md** with minimal patch section.

---

## Phase 5: Regression

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

---

## Phase 6: Review

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

---

## Phase 7: Close

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
