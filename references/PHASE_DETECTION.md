# Phase Detection

Determine the current Harness phase by checking repository artifacts.

## No Harness

Signals: no `.harness/`, no `AGENTS.md`, no `specs/`
Action: use `harness-init`

## Product Discovery Phase

Signals:
- User describes a product idea, not a specific feature
- `.pm/` directory missing or `.pm/stable/product.md` missing/empty
- Keywords: "worth building", "product idea", "I want to build", "MVP", "startup idea"
- No `.pm/runtime/state.yaml` or `product_definition_ready: false`

Action: use `harness-grill-product`

## Product Delivery Phase (Supervisor Loop)

Signals:
- `.pm/runtime/state.yaml` exists with `product_definition_ready: true`
- User says "goal", "supervisor", "advance", "keep going", "PM loop"
- `.pm/runtime/next-task.md` needs to be created or executed
- Codex `/goal` session active

Action: use `harness-supervisor`

## Worker Execution Phase

Signals:
- `.pm/runtime/next-task.md` exists with a defined task
- OpenCode session instructed to execute a task
- `.pm/runtime/worker-report.md` needs to be written

Action: use `harness-intern`

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

## Maintenance Debug Phase

Signals:
- User mentions bug, failing test, regression, unexpected behavior
- Existing codebase (not green-field)
- Fix request without new feature intent
- Stack trace / error log present
- `maintenance/debug/` directory exists with open records

Action: use `harness-maintain-debug`

## Cache/Context Phase

Signals: context too large, agent repeatedly reading same files, user asks about cache/cost/token reduction
Action: use `harness-cache`, then `harness-context`

## Detection Algorithm

For a given repository:

1. Check for `.harness/` and `AGENTS.md` -> if missing, No Harness
2. **Check for PM/product signals** (".pm/", "product idea", "worth building", "goal", "supervisor") -> if `.pm/` exists, check state.yaml for phase; if `.pm/` missing and product keywords present, Product Discovery Phase
3. **Check for debug signals** (bug keywords, error logs, stack traces, "fix", "broken", "not working") -> if present, Maintenance Debug Phase
4. **Check for refactor signals** ("refactor", "clean up", "remove dead code", "optimize") -> if present, run `harness-specify` first (lightweight refactor scope), then route to plan → tasks → tdd
5. Check `specs/` for feature directories -> if none with spec.md, Intake Phase
6. For each feature, check artifact presence in order: spec -> plan -> tasks -> eval -> report
7. The earliest missing artifact determines the phase
8. If all artifacts present and code changes are requested, Implementation Phase
9. If all artifacts present and user asks about completion, Verification Phase
