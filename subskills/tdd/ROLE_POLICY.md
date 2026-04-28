# Role Policy

File-level boundaries for each TDD role. Enforced by `harness verify-ai`.

## Roles

### TDD-RED

**Purpose:** Write failing tests that describe expected behavior.

| Category | Allowed | Forbidden |
|----------|---------|-----------|
| Tests | `tests/**`, `**/*_test.go`, `**/*_test.py`, `**/*_test.ts` | — |
| Specs | `specs/**/spec.md`, `specs/**/eval.md` | — |
| Implementation | — | `internal/**`, `cmd/**`, `src/**/domain/**`, `src/**/infra/**` |
| Config | — | `Makefile`, `*.yaml`, `*.toml`, `docker-compose*` |

**Enforcement rule:** `git diff --name-only HEAD~1` must contain only test files and spec files.

### TDD-GREEN

**Purpose:** Write minimal implementation to make RED tests pass.

| Category | Allowed | Forbidden |
|----------|---------|-----------|
| Implementation | `internal/**`, `cmd/**`, `src/**/domain/**`, `src/**/infra/**` | — |
| Tests | — | `tests/**`, `**/*_test.*` |
| Specs | — | `specs/**` |
| Config | `go.mod`, `package.json`, `requirements.txt` (dependency additions only) | `Makefile`, CI config |

**Enforcement rule:** `git diff --name-only HEAD~1` must not contain any test files.

### TDD-REFACTOR

**Purpose:** Restructure implementation without changing behavior.

| Category | Allowed | Forbidden |
|----------|---------|-----------|
| Implementation | Same as TDD-GREEN | — |
| Tests | — | `tests/**`, `**/*_test.*` |
| Specs | — | `specs/**` |
| Config | — | All config files |

**Additional rule:** `git diff --stat HEAD~1` must not add new public symbols. Refactoring reorganizes, it does not extend.

### REVIEWER

**Purpose:** Validate compliance and generate evidence reports.

| Category | Allowed | Forbidden |
|----------|---------|-----------|
| Reports | `docs/reports/**`, `specs/**/report.md` | — |
| All source | — | `internal/**`, `cmd/**`, `src/**`, `tests/**` |

**Enforcement rule:** REVIEWER never modifies source or test files. It reads and reports only.

### HUMAN

**Purpose:** Approval gate for HITL checkpoints.

| Category | Allowed | Forbidden |
|----------|---------|-----------|
| Approval | Sign off on reports, merge PRs | — |
| Source | Emergency fixes only (requires justification) | All other source changes |

## Boundary Violation Protocol

When `harness verify-ai` detects a violation:

1. **Block.** The commit is rejected.
2. **Report.** The specific files and role mismatch are logged.
3. **Redo.** The agent must redo the work within the correct role boundaries.

Example violation:
```
harness verify-ai --role TDD-GREEN --base HEAD~1
ERROR: Role boundary violation
  Role: TDD-GREEN
  Forbidden files modified:
    - tests/unit/order_test.go (test files not allowed for TDD-GREEN)
  Allowed to modify: internal/**, cmd/**, src/**/domain/**, src/**/infra/**
```

## Cross-Role Dependencies

```
RED → GREEN → REFACTOR → REVIEWER → (next slice RED)
                    ↑                |
                    └── if REPORTER flags issues, back to GREEN
```

- RED depends on the spec and the chosen vertical slice
- GREEN depends on RED tests existing
- REFACTOR depends on GREEN tests passing
- REVIEWER depends on REFACTOR (or GREEN if no refactor) completing
- Next-slice RED depends on REVIEWER report being clean
