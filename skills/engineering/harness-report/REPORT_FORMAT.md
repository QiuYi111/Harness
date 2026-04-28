# Report Format

Template for `specs/<feature>/report.md`. Fill every section. Omit sections only if explicitly marked optional.

## Summary

One paragraph: what was built, why, blast radius level, and verdict.

## Files Changed

| File | Change Type | Risk Level | Reason |
|------|------------|------------|--------|
| _path/to/file_ | added / modified / deleted | leaf / branch / core / infra | _why this file changed_ |

## Architecture Decisions

Numbered list of decisions made during implementation. Reference ADRs if any.

1. _Decision — rationale (ADR-XXXX if applicable)_
2. _Decision — rationale_

## Tests

| Suite | Result | Evidence |
|-------|--------|----------|
| Unit tests | PASS / FAIL / N/A | _test runner output or path_ |
| Integration tests | PASS / FAIL / N/A | _test runner output or path_ |
| E2E tests | PASS / FAIL / N/A | _test runner output or path_ |

## Verification

| Gate | Command | Result | Output |
|------|---------|--------|--------|
| `make verify` | `make verify` | PASS / FAIL | _key output lines_ |
| `make verify-ai` | `make verify-ai` | PASS / FAIL / N/A | _key output lines_ |
| Risk classification | `classify-risk` or manual | leaf / branch / core / infra | _reasoning_ |

## Review Summary

If a review was conducted:

- **Reviewer**: _agent name or human_
- **Findings**: _count of critical / high / medium / low_
- **Status**: _all addressed / deferred items listed below_

If no review was conducted, state: "No review conducted for this blast radius level." (acceptable for leaf only)

## Known Issues

| Issue | Severity | Status | Tracking |
|-------|----------|--------|----------|
| _description_ | critical / high / medium / low | open / deferred / accepted | _link or reference_ |

Leave empty table with "None identified" if no known issues.

## Rollback Plan

**Required for**: core, infra. Optional for leaf and branch but recommended.

1. **Trigger**: _what condition triggers rollback_
2. **Steps**:
   - _step 1 (e.g., git revert <sha>)_
   - _step 2 (e.g., redeploy previous version)_
3. **Validation**: _how to confirm rollback succeeded_
4. **Data considerations**: _any data migration rollback needed_

If leaf/branch and no rollback plan: "Low-risk change. Standard git revert sufficient."

## Final Verdict

**Blast radius**: leaf / branch / core / infra
**Eval status**: _pass/fail or "not run"_
**Recommendation**: Ready to merge / Needs changes / Blocked
**Conditions** (if not Ready to merge): _what must happen first_
