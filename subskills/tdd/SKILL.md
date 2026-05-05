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

### Step 0: Classify Risk

```bash
harness classify-risk
```

If risk returns **core** or **infra**: STOP. Require human approval before writing any code.

If risk returns **leaf** or **branch**: proceed to Step 1.

This gate ensures the TDD skill (the primary code-writing skill) never bypasses risk classification, even when invoked directly without going through plan/tasks first.

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

## Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

No exceptions:
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Red Flags — STOP and Follow Process

If you catch yourself doing any of these, STOP:

- Code before test
- Test after implementation
- Test passes immediately (proves nothing)
- Can't explain why test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"
- "TDD is dogmatic, I'm being pragmatic"
- "This is different because..."

**ALL of these mean: Delete code. Start over with TDD.**

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing about correctness. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

## Per-Cycle Checklist

- [ ] Test describes behavior, not implementation
- [ ] Test uses the public interface (would survive a refactor)
- [ ] GREEN code is minimal — no speculative features
- [ ] No test file modified during GREEN or REFACTOR
- [ ] REVIEWER confirms spec alignment
- [ ] `make verify` and `make verify-ai` both pass
