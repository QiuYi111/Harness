# Implementation Plan: [Feature Name]

## Inputs

| Source          | Reference                                          |
|-----------------|----------------------------------------------------|
| Spec            | `[path/to/spec.md]`                                |
| PRD             | `[path/to/prd.md]` (optional)                      |
| Related Contracts | `[path/to/contract.proto]` or "None"            |

## Technical Context

| Dimension             | Value                |
|-----------------------|----------------------|
| Language              | `[Language]`         |
| Framework             | `[Framework]`        |
| Storage               | `[Storage backend]`  |
| External Dependencies | `[Dep 1, Dep 2]`     |

## Architecture Impact

### DDD Layer Impact

| Layer            | Change                              |
|------------------|-------------------------------------|
| `domain/`        | None expected / [Description]       |
| `infrastructure/`| None expected / [Description]       |
| `api/`           | None expected / [Description]       |
| `cmd/`           | None expected / [Description]       |

### Contract Impact

- [List any API contracts, protobuf definitions, or service interfaces that change or get added. Write "None" if no contract changes.]

### Data Model Impact

- [List any schema migrations, new tables/collections, or model changes. Write "None" if no data model changes.]

## Blast Radius Classification

| Field     | Value                                                              |
|-----------|--------------------------------------------------------------------|
| Level     | `leaf` / `branch` / `core` / `infra`                               |
| Reason    | [Why this classification fits]                                     |
| Required Gates | [Gates that must pass before merge, e.g. "2 reviewer approval, integration tests"] |

### Classification Guide

- **leaf**: Touches one module, no shared types or contracts
- **branch**: Touches multiple modules or shared types, no cross-cutting concern
- **core**: Changes domain logic, shared contracts, or data model
- **infra**: Changes infrastructure, deployment, storage, or observability

## Constitution Check

| Check          | Pass | Notes |
|----------------|------|-------|
| Contract-first | Yes / No | [Rationale or reference] |
| DDD direction  | Yes / No | [Rationale or reference] |
| TDD/BDD        | Yes / No | [Rationale or reference] |
| Observability  | Yes / No | [Rationale or reference] |
| Security       | Yes / No | [Rationale or reference] |

## Implementation Strategy

[High-level approach: what gets built, in what order, and why this ordering makes sense. Keep it concise. Reference specific DDD layers and modules where applicable.]

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

- [Known edge cases to cover]
- [Boundary conditions]

## Rollback Plan

[Describe how to revert this change if deployment fails or issues arise. Include specific steps like reverting migrations, rolling back config, or reverting the branch.]

1. [Rollback step 1]
2. [Rollback step 2]
3. [Rollback step 3]

## Complexity Tracking

| Field      | Value        |
|------------|--------------|
| Estimated  | `[Low / Medium / High]` |
| Rationale  | [Why this complexity rating] |

## Rules

- core/infra plan must include rollback plan.
- branch/core/infra must include test strategy.
- core/infra requires human review marker: [REQUIRES HUMAN REVIEW].
