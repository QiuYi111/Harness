# Eval Format

Template for `specs/<feature>/eval.md`. Fill every section. Mark each criterion PASS or FAIL with evidence.

## Product Evaluation

### Acceptance Scenario Validation

| Scenario | Expected | Actual | Result |
|----------|----------|--------|--------|
| _(from spec acceptance criteria)_ | _(spec says)_ | _(code does)_ | PASS / FAIL |

### Functional Requirement Validation

| Requirement | Implementation | Evidence | Result |
|-------------|---------------|----------|--------|
| _(from spec functional requirements)_ | _(which file/function)_ | _(test or manual check)_ | PASS / FAIL |

### Edge Cases

| Edge Case | Spec Definition | Implementation | Result |
|-----------|----------------|----------------|--------|
| _(e.g., empty input, null, max size)_ | _(what spec says)_ | _(how code handles it)_ | PASS / FAIL / N/A |

### Error Handling

| Error Condition | Expected Behavior | Actual Behavior | Result |
|-----------------|-------------------|-----------------|--------|
| _(e.g., network timeout, invalid auth)_ | _(spec says)_ | _(code does)_ | PASS / FAIL / N/A |

### Non-Functional Checks

| Category | Criterion | Evidence | Result |
|----------|-----------|----------|--------|
| Performance | _(e.g., p99 < 200ms)_ | _(benchmark or test)_ | PASS / FAIL / N/A |
| Security | _(e.g., input validated)_ | _(where in code)_ | PASS / FAIL / N/A |
| Observability | _(e.g., metrics emitted)_ | _(where in code)_ | PASS / FAIL / N/A |

## Harness Evaluation

| Gate | Required For | Evidence | Result |
|------|-------------|----------|--------|
| Spec existed | branch, core, infra | _(path to spec.md)_ | PASS / FAIL |
| Plan existed | branch, core, infra | _(path to plan.md)_ | PASS / FAIL |
| Tasks generated | branch, core, infra | _(path to tasks.md)_ | PASS / FAIL |
| Blast radius classified | all levels | _(leaf/branch/core/infra + reason)_ | PASS / FAIL |
| Tests not modified in GREEN | branch, core, infra | _(git diff evidence)_ | PASS / FAIL / N/A |
| Review report produced | branch, core, infra | _(path to review)_ | PASS / FAIL / N/A |
| `make verify` passed | all levels | _(command output)_ | PASS / FAIL |
| `make verify-ai` passed | branch, core, infra | _(command output)_ | PASS / FAIL |
| Human spec review | core, infra | _(reviewer sign-off)_ | PASS / N/A |
| Architecture review | core, infra | _(review notes)_ | PASS / N/A |
| Rollback plan | core, infra | _(path to plan)_ | PASS / N/A |
| Security review | core, infra | _(review notes)_ | PASS / N/A |
| Dry run | infra | _(dry run output)_ | PASS / N/A |
| Human approval | infra | _(approval record)_ | PASS / N/A |

## Verdict

**Status**: Ready to merge / Needs changes

**Blocking issues** (if Needs changes):
1. _(issue)_
2. _(issue)_

**Deferred** (non-blocking, tracked separately):
1. _(item)_
