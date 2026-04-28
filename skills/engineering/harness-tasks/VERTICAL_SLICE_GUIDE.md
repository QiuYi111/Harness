# Vertical Slice Guide

How to decompose features into vertical slices for `harness-tasks`.

## What is a Vertical Slice?

A vertical slice (tracer bullet) cuts through every layer of the architecture to deliver one complete, demoable piece of user-facing behavior. It is the opposite of horizontal slicing.

**Vertical ✅:** One user story → domain + infrastructure + API + test, all in one task group.

**Horizontal ❌:** "Write all domain models" → "Write all services" → "Write all endpoints."

## Why Vertical?

1. **Demoable immediately.** Each completed slice shows working software.
2. **Risk reduction.** Integration problems surface early, not at the end.
3. **Accurate estimates.** Velocity is measurable per slice.
4. **Spec alignment.** Each slice maps to one acceptance criterion.

## Anatomy of a Slice

A single slice covers:

```
Test → Domain → Infrastructure → Interface → Integration Test
```

Example for "Create Order":

| Layer | File | Action |
|-------|------|--------|
| Test | `src/ordering/domain/order_test.go` | Write behavior test |
| Domain | `src/ordering/domain/order.go` | Implement entity |
| Infra | `src/ordering/infra/order_repo.go` | Implement repository |
| Interface | `src/ordering/cmd/create_order.go` | HTTP handler |
| Integration | `tests/integration/create_order_test.go` | End-to-end test |

This is ONE task group: T001–T005, all belonging to the same slice.

## Slicing Rules

### Rule 1: One User Story Per Slice

Each slice implements exactly one user story from the spec. If a story is too large, split the story, not the layers.

### Rule 2: Every Slice is Demoable

After completing a slice, the behavior should be exercisable. If you can't demo it, the slice is too thin or missing a layer.

### Rule 3: Prefer AFK Over HITL

Mark slices AFK by default. Only add HITL gates when:
- Risk level is core or infra
- The slice modifies auth, schema, or deployment config
- The spec explicitly requires human review

### Rule 4: Exact File Paths

Every task in the slice names the exact file it creates or modifies. No "and related files" or "etc."

### Rule 5: Slices are Independent When Possible

Two slices that don't share files should both be marked `[P]` (parallel-safe). Only add dependencies when one slice genuinely depends on another's output.

## Common Patterns

### Pattern: CRUD Feature

```
Slice A: Create [US1]
  T001 [P] [AFK] Test + Domain + Repo + Handler + Integration

Slice B: Read [US2]
  T002 [P] [AFK] Test + Domain + Repo + Handler + Integration

Slice C: Update [US3]
  T003 → T001 (depends on Create's domain entity)

Slice D: Delete [US4]
  T004 → T001 (depends on Create's domain entity)
```

Slices A and B are parallel. C and D depend on A.

### Pattern: Event-Driven Feature

```
Slice A: Publish Event [US1]
  T001 [P] [AFK] Domain event + publisher + test

Slice B: Consume Event [US2]
  T002 → T001 (needs event definition from A)
  T003 [AFK] Handler + side effect + integration test
```

### Pattern: Multi-Step Workflow

```
Slice A: Step 1 → Step 2 [US1]
  T001 [P] [AFK] Complete thin path: validate → execute → confirm

Slice B: Error Handling [US2]
  T002 → T001 (adds error branches to existing path)

Slice C: Retry Logic [US3]
  T003 → T002 (adds retry around error paths)
```

## Anti-Patterns

### Anti-Pattern: "Set Up All Models First"

```markdown
# ❌ Wrong
T001 Create all domain entities
T002 Create all repositories
T003 Create all handlers
```

This is horizontal. Nobody can demo anything until T003 is done.

### Anti-Pattern: "Test Phase" Then "Implementation Phase"

```markdown
# ❌ Wrong
## Phase 1: Tests
T001 Write all tests
## Phase 2: Implementation
T002 Write all implementation
```

Tests and implementation are interleaved within a slice, not separated across phases. Use `harness-tdd` for role-isolated TDD within each slice.

### Anti-Pattern: Vague File References

```markdown
# ❌ Wrong
T001 Update related files in the ordering module

# ✅ Correct
T001 [AFK] Add Submit method to Order entity
  - `src/ordering/domain/order.go` (modify)
  - `src/ordering/domain/order_test.go` (modify)
```
