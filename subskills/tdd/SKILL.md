---
name: harness-tdd
description: "Run a role-isolated TDD workflow: RED (tests only, no implementation), GREEN (implementation only, no test changes), REFACTOR (implementation only), REVIEWER (reports only). Use when implementing features with test-first discipline, or when the user says 'TDD', 'red green refactor', 'test first', or 'role-isolated testing'."
---

# Harness TDD

Role-isolated Test-Driven Development with enforced file boundaries. Each TDD cycle is split across roles that cannot edit each other's files.

## Prerequisites

- `../../references/DOMAIN-AWARENESS.md`
- Active `spec.md` for acceptance criteria
- [ROLE_POLICY.md](ROLE_POLICY.md) — file-level boundaries
- [TESTING_GUIDE.md](TESTING_GUIDE.md) — test philosophy and patterns
- [EXAMPLES.md](EXAMPLES.md) — worked examples

## How This Differs from Standard TDD

| Aspect | Standard TDD | Harness TDD |
|--------|-------------|-------------|
| Isolation | Process discipline | File-level enforcement via `harness verify-ai` |
| Roles | Implicit (same developer) | Explicit: RED, GREEN, REFACTOR, REVIEWER |
| Review | Optional | REVIEWER role is mandatory |
| Enforcement | Trust-based | `harness verify-ai` blocks boundary violations |

## Workflow

### Step 1: Plan the Tracer Bullet

Select one vertical slice from `tasks.md`. Identify the public interface, implementation files, and test files.

### Step 2: RED Cycle — **Role: TDD-RED**

1. Write tests describing expected behavior through the public interface
2. Run tests — they MUST fail (compilation or assertion)
3. Commit: `RED: [description]`
4. `harness verify-ai` confirms: test files only, no implementation touched

### Step 3: GREEN Cycle — **Role: TDD-GREEN**

1. Write minimal implementation to make all RED tests pass
2. Do NOT modify any test file
3. Run tests — they MUST pass
4. Commit: `GREEN: [what was implemented]`
5. `harness verify-ai` confirms: implementation files only, no tests touched

### Step 4: REFACTOR Cycle (optional) — **Role: TDD-REFACTOR**

1. Restructure implementation for clarity, performance, or DRY
2. Do NOT modify any test file — tests are the safety net
3. Commit: `REFACTOR: [what changed]`

### Step 5: REVIEWER Cycle (mandatory) — **Role: REVIEWER**

1. Generate compliance report in `specs/**/report.md`
2. Verify: all tests pass, no speculative features, spec alignment
3. Run `make verify-ai` and report results

### Step 6: Repeat for Next Slice

Return to Step 1 with the next vertical slice from `tasks.md`.

## Enforcement

`harness verify-ai` enforces role boundaries at the file level. Run after each commit:

```bash
harness verify-ai --role TDD-RED --base HEAD~1      # after RED
harness verify-ai --role TDD-GREEN --base HEAD~1     # after GREEN
harness verify-ai --role TDD-REFACTOR --base HEAD~1  # after REFACTOR
harness verify-ai --role REVIEWER                     # after REVIEWER
```

Boundary violations invalidate the commit. Redo within the correct role.

## Per-Cycle Checklist

- [ ] Test describes behavior, not implementation
- [ ] Test uses the public interface (would survive a refactor)
- [ ] GREEN code is minimal — no speculative features
- [ ] No test file modified during GREEN or REFACTOR
- [ ] REVIEWER confirms spec alignment
- [ ] `make verify` and `make verify-ai` both pass
