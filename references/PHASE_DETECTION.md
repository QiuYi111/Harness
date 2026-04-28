# Phase Detection

Determine the current Harness phase by checking repository artifacts.

## No Harness

Signals: no `.harness/`, no `AGENTS.md`, no `specs/`
Action: use `harness-init`

## Intake Phase

Signals: user describes idea, no feature ID, no `specs/<feature>/spec.md`
Action: use `harness-grill` (if fuzzy), then `harness-specify`

## Spec Phase

Signals: `spec.md` exists, `plan.md` missing or empty
Action: use `harness-plan`

## Planning Phase

Signals: `plan.md` exists, `tasks.md` missing or empty
Action: use `harness-tasks`

## Implementation Phase

Signals: `tasks.md` exists, code changes requested, no eval/report yet
Action: `harness-risk` -> `harness-context` -> `harness-tdd` (if tests involved)

## Verification Phase

Signals: implementation exists, tests pass or user asks if complete, `eval.md` missing/incomplete
Action: use `harness-eval`

## Reporting Phase

Signals: eval complete, PR/review/merge requested, report missing/incomplete
Action: use `harness-report`

## Architecture Review Phase

Signals: user says codebase is messy, large refactor, unclear module boundaries, DDD violation suspected
Action: use `harness-architecture-review`

## Cache/Context Phase

Signals: context too large, agent repeatedly reading same files, user asks about cache/cost/token reduction
Action: use `harness-cache`, then `harness-context`

## Detection Algorithm

For a given repository:

1. Check for `.harness/` and `AGENTS.md` -> if missing, No Harness
2. Check `specs/` for feature directories -> if none with spec.md, Intake Phase
3. For each feature, check artifact presence in order: spec -> plan -> tasks -> eval -> report
4. The earliest missing artifact determines the phase
5. If all artifacts present and code changes are requested, Implementation Phase
6. If all artifacts present and user asks about completion, Verification Phase
