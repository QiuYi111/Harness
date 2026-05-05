# Feature Spec: [Feature Name]

## Metadata

| Field     | Value                          |
|-----------|--------------------------------|
| Feature ID | `[FEAT-XXX]`                   |
| Branch    | `feat/feat-xxx-[feature-name]` |
| Status    | Draft / In Review / Approved   |
| Owner     | `[Owner]`                      |
| Date      | `[YYYY-MM-DD]`                 |

## Summary

[One paragraph describing the feature: what it does, who it serves, and why it matters. Write this after the spec is complete.]

## User Scenarios

### US-001: [Scenario Title]

**Priority**: P1

**Independent Test**: [How to verify this scenario in isolation. For P1 scenarios, include exact steps, inputs, and expected outputs.]

**Acceptance Scenarios**:
- Given [precondition], When [user action], Then [observable result]
- Given [precondition], When [user action with edge case], Then [observable result]

### US-002: [Scenario Title]

**Priority**: P2

**Independent Test**: [How to verify this scenario in isolation.]

**Acceptance Scenarios**:
- Given [precondition], When [user action], Then [observable result]

## Requirements

### Functional Requirements

- **FR-001**: [Clear, testable requirement statement]
- **FR-002**: [Clear, testable requirement statement]

### Non-Functional Requirements

- **NFR-001**: Performance - [Specific measurable target]
- **NFR-002**: Reliability - [Specific measurable target]
- **NFR-003**: Security - [Specific measurable target]

## Success Criteria

| #  | Criterion                                         | Measured By              |
|----|---------------------------------------------------|--------------------------|
| SC-1 | [Measurable outcome tied to a user scenario]      | [Metric or test]         |
| SC-2 | [Measurable outcome tied to a requirement]        | [Metric or test]         |
| SC-3 | [Measurable outcome tied to quality gate]         | [Metric or test]         |

## Assumptions

- [Assumption 1: what the team is taking as given]
- [Assumption 2: dependency or precondition assumed true]
- [Assumption 3: environmental or infrastructural assumption]

## Clarifications

- [Question or decision point] - [NEEDS CLARIFICATION: what specifically is unresolved]

## Out of Scope

- [Explicit exclusion 1: what this feature will NOT do]
- [Explicit exclusion 2: what this feature will NOT do]
- [Explicit exclusion 3: related feature deferred to a future spec]

## Risk Notes

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk description] | Low / Medium / High | Low / Medium / High | [What the team will do about it] |

## Rules

- Every spec must have at least one user scenario.
- Every P1 scenario must have independent test instructions.
- Every feature must define success criteria.
- Agent must not guess values marked [NEEDS CLARIFICATION].
