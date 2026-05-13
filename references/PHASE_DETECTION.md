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

Signals:
- User says codebase is messy, large refactor, unclear module boundaries, DDD violation suspected
- Keywords: "codebase feels complex", "untestable", "hard to navigate", "architecture review", "shallow modules"

Action: use `harness-architecture-review`

## Domain Language Phase

Signals:
- User mentions terminology inconsistency, agents using different words for the same thing
- No `CONTEXT.md` or `UBIQUITOUS_LANGUAGE.md` exists in the project
- User says "ubiquitous language", "define domain terms", "resolve naming ambiguity", "onboard agents to terminology"
- New project after `harness-init`, or agents produce inconsistent naming across sessions

Action: use `harness-domain-language`

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

## Code Semantic Atlas Phase

Signals:
- User says "atlas", "semantic map", "audit this code", "代码语义地图", "语义审计"
- User wants to understand code behavior without reading source
- User asks "这段代码在做什么", "帮我搞懂这个模块", "code audit"
- PR review needs structured understanding, not just diff reading
- User inherits unfamiliar codebase

Action: use `harness-atlas`

## Detection Algorithm

For a given repository:

0. **Check user intent for product discovery signals** (".pm/", "product idea", "worth building", "goal", "supervisor", "MVP", "UI direction", "I have an idea") — if detected, route to `harness-grill-product` or `harness-supervisor` regardless of whether `.harness/` exists. Product discovery does NOT require Harness to be installed.
1. **Check for atlas/audit signals** ("atlas", "semantic map", "audit this code", "代码语义地图", "语义审计", "帮我搞懂") — if detected, route to `harness-atlas` regardless of whether Harness is installed.
2. Check for `.harness/` and `AGENTS.md` -> if missing, No Harness
3. **Check for PM/product signals** (".pm/", "product idea", "worth building", "goal", "supervisor") -> if `.pm/` exists, check state.yaml for phase; if `.pm/` missing and product keywords present, Product Discovery Phase
4. **Check for debug signals** (bug keywords, error logs, stack traces, "fix", "broken", "not working") -> if present, Maintenance Debug Phase
5. **Check for refactor signals** ("refactor", "clean up", "remove dead code", "optimize") -> if present, run `harness-specify` first (lightweight refactor scope), then route to plan → tasks → tdd
6. **Check for domain-language signals** ("terminology inconsistent", "ubiquitous language", "define domain terms", "naming ambiguity") -> if present, Domain Language Phase
7. **Check for architecture-review signals** ("codebase messy", "complex", "untestable", "hard to navigate", "architecture review") -> if present, Architecture Review Phase
8. Check `specs/` for feature directories -> if none with spec.md, Intake Phase
9. For each feature, check artifact presence in order: spec -> plan -> tasks -> eval -> report
10. The earliest missing artifact determines the phase
11. If all artifacts present and code changes are requested, Implementation Phase
12. If all artifacts present and user asks about completion, Verification Phase
