# Handoff

## Current State

Product contract is frozen. Harness is in feasibility stage for dogfood-grade `/goal` long-running supervisor loop.

## Read First On Resume

1. `.pm/runtime/state.yaml`
2. `.pm/runtime/active-stage.md`
3. `.pm/stable/roadmap.md`
4. `.pm/stable/product.md`
5. `.pm/runtime/loop-log.md`
6. `.pm/runtime/loop-control`

## Next Expected Action

Create the next bounded feasibility task, then delegate to OpenCode intern.

## Important Constraints

- Do not overwrite user changes.
- Supervisor manages branch policy.
- Intern must create a clear commit for each accepted task.
- Existing modified file `scripts/harness_runtime/verify.py` predates this worker task and is forbidden scope.
- Worker commit `6125f40` plus rework commit `07d4af8` are accepted as iteration 1.
- The new `harness pm-status` command is available and should be used in future supervisor checks.
- No auto-merge, push, publish, or deploy.
- Stop for core, infra, security, auth, payment, deployment, or product-boundary changes.

## Current User Decision

The user approved dogfood MVP, no visual UI, `/goal` long-run requirement, sync worker mode for first validation, and branch/commit separation.
