# Tasks: Add Todo Item

> This template lives in the Harness v2 lifecycle: **PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT**.
> Tasks are the scheduling input for AI agents. They define what to do, in what order, with what dependencies.
> This document depends on `specs/001-add-todo/spec.md` and `specs/001-add-todo/plan.md`.

## Format

```
- [x] T001 [P] [US1] Description with exact file path
```

| Marker | Meaning |
|--------|---------|
| `T001` | Unique task ID, sequential |
| `[P]` | Safe to run in parallel with other `[P]` tasks |
| `[US1]` | Maps to User Story 1 from the spec |

Rules for task descriptions:

- Every task names exact file paths. No vague references.
- A task touches one concern. Split if it reaches across unrelated boundaries.
- `[P]` tasks must not modify the same file as any other `[P]` task in the same wave.

## Phase 1: Setup

```
- [x] T001 Create directory structure for todo feature in internal/domain/todo/ and internal/infrastructure/todo/
- [x] T002 [P] Create contract definition in api/todo_openapi.yaml
```

Setup tasks create the skeleton. Nothing should compile or pass yet. The goal is to lay down the files and directories that everything else depends on.

## Phase 2: Tests First

```
- [x] T003 [US1] Create failing unit test for Todo entity validation in internal/domain/todo/entity_test.go
- [x] T004 [P] [US2] Create failing integration test for POST /todos in tests/integration/todo_test.go
```

TDD-RED phase. Write tests that describe the desired behavior. Every test should fail for the right reason: missing implementation, not a syntax error or import issue.

Checkpoint: **All tests are RED.** If any test passes at this stage, something is wrong with the test design.

## Phase 3: Implementation

```
- [x] T005 [US1] Implement Todo entity with validation in internal/domain/todo/entity.go
- [x] T006 [US1] Implement TodoRepository interface in internal/domain/todo/repository.go
- [x] T007 [P] [US2] Implement PostgreSQL adapter in internal/infrastructure/todo/adapter.go
```

TDD-GREEN phase. Write the minimum code to make the red tests pass. Each task maps to a user story. Tasks touching different files can run in parallel.

Checkpoint: **All tests are GREEN.** Run the test suite. If anything is still red, stop and fix it before moving on.

## Phase 4: Integration

```
- [x] T008 Register handler in cmd/server/main.go
```

Wire everything together. The handler registration depends on the adapter being complete and the domain entity being defined.

Checkpoint: **`make verify` passes.** Linting, type checking, and basic tests all green.

## Phase 5: Verification

```
- [x] T009 Run make verify
- [x] T010 Run make verify-ai
- [x] T011 Fill eval.md with results
- [x] T012 Fill report.md with evidence
```

Final gate. Run the full verification suite, collect evidence, and document results. This phase is strictly sequential: each step depends on the previous one passing.

Checkpoint: **`make verify-ai` passes.** Eval and report are filled out.

## Dependencies

```
T001 → T003
T002 → T004
T003 → T005
T005 → T006
T006 → T007
T004 → T007
T007 → T008
T008 → T009 → T010 → T011 → T012
T001, T002 are independent
```

Arrows mean "depends on". T005 depends on T003 because the implementation follows the test. T007 depends on both T006 and T004 because the adapter needs the repository interface and the integration test expects the full stack.

## Parallel Execution Plan

```
Wave 1: T001, T002 (independent setup, different directories)
Wave 2: T003, T004 (parallel tests, different test files)
Wave 3: T005, T006, T007 (parallel implementation, different files)
Wave 4: T008 (sequential integration, single file)
Wave 5: T009 → T010 → T011 → T012 (sequential verification)
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
