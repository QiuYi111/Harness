---
name: harness-tasks
description: Break a spec and plan into vertical-slice implementation tasks with dependencies, parallel-safe markers, checkpoints, and exact file paths. Use when turning a plan into executable work items, creating tasks.md, decomposing work for AI agents, or when the user says "create tasks", "break this down", "task DAG", or "implementation order".
---

# Harness Tasks

Convert a `spec.md` + `plan.md` into an executable task DAG (`tasks.md`) using vertical slices.

## Prerequisites

Read before starting:
- `../../references/DOMAIN-AWARENESS.md`
- The active `spec.md` and `plan.md` for the feature
- `specs/` directory for any existing eval criteria

## Process

### 1. Gather Context

- Read `spec.md` and `plan.md` fully
- Read `DOMAIN-AWARENESS.md` for glossary and ADRs
- Explore the codebase to map existing file paths
- Identify what already exists vs. what must be created

### 2. Draft Vertical Slices

Each slice must be a **tracer bullet**: thin but complete path through every layer. A completed slice is demoable end-to-end.

Rules:
- Each task group = one vertical slice, NEVER horizontal
- Every task names exact file paths (no vague references)
- Mark parallel-safe tasks with `[P]`
- Classify each task as HITL (human-in-the-loop) or AFK (autonomous)
- Prefer AFK over HITL unless risk level requires human gates

### 3. Build the DAG

- Number tasks: `T001`, `T002`, etc.
- Draw dependency arrows: `T003 → T001, T002`
- Identify parallel execution groups
- Add checkpoints between groups

### 4. Output `tasks.md`

Generate using the format in [TASKS_FORMAT.md](TASKS_FORMAT.md).

## Slicing Rules

See [VERTICAL_SLICE_GUIDE.md](VERTICAL_SLICE_GUIDE.md) for detailed examples.

**Anti-patterns:**
- "Write all tests first" (horizontal) — forbidden
- "Set up all models, then all services" (horizontal) — forbidden
- "Create the full UI, then wire it up" (horizontal) — forbidden

**Correct pattern:**
- One user story → one slice → test + implementation + integration in one task group

## Task Classification

- **AFK**: Agent can complete autonomously. Default for leaf/branch risk.
- **HITL**: Requires human approval checkpoint. Required for core/infra risk, spec changes, or architecture decisions.

Use `harness classify-risk` to determine which classification applies.

## Dependency Rules

1. A task that creates a file is a dependency of every task that modifies it
2. Test tasks depend on their implementation target existing
3. Integration tasks depend on all slice implementations completing
4. Verification tasks depend on everything

## Checkpoint Format

```
### Checkpoint 1: [Name]
- After: T003
- Verify: `make verify-ai`
- Gate: All tests pass, no lint errors
- Continue: T004–T006
```

## Checklist Before Output

- [ ] Every task has exact file paths
- [ ] No horizontal slices exist
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Parallel groups are correctly marked `[P]`
- [ ] HITL/AFK classification matches risk level
- [ ] Checkpoints placed between dependency groups
- [ ] Risk terminology uses leaf/branch/core/infra (see DOMAIN-AWARENESS.md)
