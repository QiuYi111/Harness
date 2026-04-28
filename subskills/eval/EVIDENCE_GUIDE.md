# Evidence Guide

What counts as valid evidence for eval criteria. Every PASS/FAIL entry in `eval.md` must reference one of these.

## Valid Evidence Types

### Test Evidence
- Passing test suite output (`make verify` or equivalent)
- Specific test case names that validate the criterion
- Test coverage report showing the relevant code path is covered
- Manual test steps with observed results

### Code Evidence
- File path + line number(s) implementing the requirement
- Function/method name that handles the scenario
- Git diff showing the change (commit SHA)
- Architecture decision record (ADR) reference

### Process Evidence
- Existence of `specs/*/spec.md` with timestamp before implementation
- Existence of `specs/*/plan.md` with timestamp before implementation
- Existence of `specs/*/tasks.md` generated from plan
- Git log showing test-first commits (RED before GREEN)
- Review report file at expected path

### Verification Evidence
- `make verify` full output (not just "passed")
- `make verify-ai` full output
- `classify-risk` output showing blast radius level and reasoning
- Lint/typecheck output with zero errors
- CI pipeline green status

## Evidence Strength Hierarchy

1. **Deterministic** — automated test output, make target output, CI result
2. **Traceable** — file path + line number, git commit SHA, ADR reference
3. **Observable** — manual test steps with results, screenshot, log output
4. **Attestation** — human reviewer sign-off, approval record

Product Eval criteria should aim for strength 1-2. Harness Eval gates that are deterministic (make verify, make verify-ai) must use strength 1.

## Blast Radius Gate Evidence Requirements

| Blast Radius | Minimum Evidence Level |
|--------------|----------------------|
| leaf | Deterministic (make verify) |
| branch | Deterministic + Traceable (spec, plan, tasks paths) |
| core | All of branch + Attestation (human reviews) |
| infra | All of core + Attestation (human approval, dry run) |

## What Does NOT Count

- "Looks correct" without test or code reference
- "Tests exist" without naming them or showing output
- "Review happened" without file path or reviewer name
- Paraphrased spec text (must show actual implementation matches)
- Stale evidence from previous iterations (must be current)
