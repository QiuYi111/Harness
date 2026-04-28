# Plan Format Reference

Template for `specs/<feature-id>/plan.md`. Fill after reading the spec and analyzing architecture impact.

---

```markdown
# Implementation Plan: [Feature Name]

## Inputs

| Source            | Reference                        |
|-------------------|----------------------------------|
| Spec              | `specs/<feature-id>/spec.md`     |
| PRD               | `docs/prd/<feature-id>.md` (opt) |
| Related Contracts | `[path]` or "None"               |

## Technical Context

| Dimension             | Value                |
|-----------------------|----------------------|
| Language              | `[Language]`         |
| Framework             | `[Framework]`        |
| Storage               | `[Storage backend]`  |
| External Dependencies | `[Dep 1, Dep 2]`     |

## Architecture Impact

### DDD Layer Impact

| Layer             | Change                         |
|-------------------|--------------------------------|
| `domain/`         | None / [Description of change] |
| `infrastructure/` | None / [Description of change] |
| `api/`            | None / [Description of change] |
| `cmd/`            | None / [Description of change] |

### Contract Impact

- [List API contracts, protobuf definitions, or interfaces that change. "None" if no changes.]

### Data Model Impact

- [List schema migrations, new tables/collections, or model changes. "None" if no changes.]

## Blast Radius Classification

| Field          | Value                                                                  |
|----------------|------------------------------------------------------------------------|
| Level          | `leaf` / `branch` / `core` / `infra`                                   |
| Reason         | [Why this classification fits]                                         |
| Required Gates | [Gates that must pass before merge]                                    |

## Constitution Check

| Check          | Pass      | Notes                        |
|----------------|-----------|------------------------------|
| Contract-first | Yes / No  | [Rationale or reference]     |
| DDD direction  | Yes / No  | [Rationale or reference]     |
| TDD/BDD        | Yes / No  | [Rationale or reference]     |
| Observability  | Yes / No  | [Rationale or reference]     |
| Security       | Yes / No  | [Rationale or reference]     |

## Implementation Strategy

[High-level approach: what gets built, in what order, and why.]

1. [Step 1: foundation or contract work]
2. [Step 2: core logic or domain implementation]
3. [Step 3: integration and wiring]
4. [Step 4: verification and cleanup]

## Test Strategy

### Unit Tests
- [What unit tests to write, at which layers]
- [Coverage targets]

### Integration Tests
- [What integration tests to write, what they verify]
- [Test environment requirements]

### Edge Cases
- [Known edge cases from spec acceptance scenarios]
- [Boundary conditions]

## Rollback Plan

[How to revert if deployment fails. Mandatory for core/infra.]

1. [Rollback step 1]
2. [Rollback step 2]
3. [Rollback step 3]

## Complexity Tracking

| Field     | Value                    |
|-----------|--------------------------|
| Estimated | `[Low / Medium / High]`  |
| Rationale | [Why this complexity]    |
```

---

## Section Guidelines

- **Inputs**: Always reference the spec. PRD is optional.
- **Technical Context**: Pull from project config or `DOMAIN-AWARENESS.md`.
- **DDD Layer Impact**: Map every requirement to affected layers. "None" is a valid answer.
- **Blast Radius**: Use the decision tree in `RISK_GUIDE.md`. Never self-promote to higher autonomy.
- **Constitution Check**: Each check must have a clear pass/fail and rationale.
- **Implementation Strategy**: Foundation-first ordering. Reference specific files and modules.
- **Test Strategy**: Derived from spec acceptance scenarios. Cover edge cases explicitly.
- **Rollback Plan**: Concrete revert steps. Not "git revert" — describe what actually gets undone.
- **Complexity**: Subjective but justified. Consider number of layers touched, external dependencies, and unknowns.
