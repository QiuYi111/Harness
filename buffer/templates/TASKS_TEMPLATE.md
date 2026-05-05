# Tasks: [Feature Name]

> This template lives in the Harness v2 lifecycle: **PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT**.
> Tasks are the scheduling input for AI agents. They define what to do, in what order, with what dependencies.
> This document depends on SPEC_TEMPLATE.md and PLAN_TEMPLATE.md.

## Format

```
- [ ] T001 [P] [US1] Description with exact file path
```

| Marker | Meaning |
|--------|---------|
| `T001` | Unique task ID, sequential |
| `[P]` | Safe to run in parallel with other `[P]` tasks |
| `[US1]` | Maps to User Story 1 from the SPEC |

Rules for task descriptions:

- Every task names exact file paths. No vague references.
- A task touches one concern. Split if it reaches across unrelated boundaries.
- `[P]` tasks must not modify the same file as any other `[P]` task in the same wave.

## Phase 1: Setup

```
- [ ] T001 Create directory structure for [feature] in internal/domain/[feature]/
- [ ] T002 [P] Create contract placeholder in api/[feature].proto
```

Setup tasks create the skeleton. Nothing should compile or pass yet. The goal is to lay down the files and directories that everything else depends on.

## Phase 2: Tests First

```
- [ ] T003 [US1] Create failing unit test in internal/domain/[feature]/[feature]_test.go
- [ ] T004 [P] [US2] Create failing integration test in tests/integration/[feature]_test.go
```

TDD-RED phase. Write tests that describe the desired behavior. Every test should fail for the right reason: missing implementation, not a syntax error or import issue.

Checkpoint: **All tests are RED.** If any test passes at this stage, something is wrong with the test design.

## Phase 3: Implementation

```
- [ ] T005 [US1] Implement domain entity in internal/domain/[feature]/entity.go
- [ ] T006 [US1] Implement domain service in internal/domain/[feature]/service.go
- [ ] T007 [P] [US2] Implement repository interface in internal/domain/[feature]/repository.go
```

TDD-GREEN phase. Write the minimum code to make the red tests pass. Each task maps to a user story. Tasks touching different files can run in parallel.

Checkpoint: **All tests are GREEN.** Run the test suite. If anything is still red, stop and fix it before moving on.

## Phase 4: Integration

```
- [ ] T008 [US1] Wire infrastructure adapter in internal/infrastructure/[feature]/adapter.go
- [ ] T009 [US1] Register handler in cmd/server/main.go
```

Wire everything together. These tasks are sequential because they build on each other: the adapter needs the domain layer in place, and the handler registration needs the adapter.

Checkpoint: **`make verify` passes.** Linting, type checking, and basic tests all green.

## Phase 5: Verification

```
- [ ] T010 Run make verify
- [ ] T011 Run make verify-ai
- [ ] T012 Fill eval.md with results
- [ ] T013 Fill report.md with evidence
```

Final gate. Run the full verification suite, collect evidence, and document results. This phase is strictly sequential: each step depends on the previous one passing.

Checkpoint: **`make verify-ai` passes.** Eval and report are filled out.

## Dependencies

```
T003 → T005 → T006 → T008 → T009
T004 → T007 → T008
T009 → T010 → T011 → T012 → T013
T001, T002 are independent
```

Arrows mean "depends on". T005 depends on T003 because the implementation follows the test. T008 depends on both T006 and T007 because the adapter needs both the service and the repository interface wired up.

## Parallel Execution Plan

```
Wave 1: T001, T002 (independent setup)
Wave 2: T003, T004 (parallel tests)
Wave 3: T005, T006, T007 (parallel implementation, different files)
Wave 4: T008, T009 (sequential integration)
Wave 5: T010 → T011 → T012 → T013 (sequential verification)
```

Each wave starts only after all tasks in the previous wave complete. Within a wave, `[P]` tasks run concurrently on separate agents. Non-`[P]` tasks in the same wave still run sequentially.

## Checkpoints

| After Phase | What to verify |
|-------------|----------------|
| Phase 2 (Tests First) | All tests are RED (failing as expected) |
| Phase 3 (Implementation) | All tests are GREEN |
| Phase 4 (Integration) | `make verify` passes |
| Phase 5 (Verification) | `make verify-ai` passes, eval.md and report.md filled |

If a checkpoint fails, do not proceed to the next phase. Fix the current phase first.

## Rules

- `[P]` means safe to run in parallel with other `[P]` tasks in the same wave.
- `[P]` tasks must not modify the same file.
- Every implementation task should map to a user story or requirement.
- Every task must name exact file paths.
- TDD-RED creates tests only. TDD-GREEN creates implementation only.
- Do not skip phases. The checkpoints exist for a reason.
- If a checkpoint fails, stop and fix before moving forward.
