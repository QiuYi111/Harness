# Acceptance Rubric

## Functional correctness

- [ ] Core use cases from product.md work as specified
- [ ] Happy path tested and passing
- [ ] Error paths tested and passing
- [ ] Edge cases covered

## UX correctness

- [ ] Matches ux-principles.md target feeling
- [ ] Primary user journey from user-journeys.md works end-to-end
- [ ] Empty states exist
- [ ] Loading states exist
- [ ] Error states provide recovery path
- [ ] No AI slop patterns

## Test evidence

- [ ] Unit tests cover core logic
- [ ] Integration tests cover critical paths
- [ ] `make verify` passes
- [ ] No skipped tests without explanation

## Harness compliance

- [ ] Risk classified (leaf/branch/core/infra)
- [ ] Appropriate gates passed for risk level
- [ ] No forbidden scope violations
- [ ] Process followed per stage-definitions.md

## Documentation

- [ ] Changed files documented in worker-report.md
- [ ] Public APIs documented if changed
- [ ] ADR written if architectural decision made

## Regression risk

- [ ] Existing tests still pass
- [ ] No uncontrolled side effects
- [ ] Rollback plan identified if core/infra

## Done definition

A task is done when ALL of:

1. All acceptance criteria in next-task.md checked
2. Test evidence exists and is fresh (run in this session)
3. worker-report.md written with all required sections
4. No deviations from task scope without explanation
