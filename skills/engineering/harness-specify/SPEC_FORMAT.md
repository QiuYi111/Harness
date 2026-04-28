# Spec Format Reference

Template for `specs/<feature-id>/spec.md`. Replace all `[placeholders]` with actual content.

---

```markdown
# Feature Spec: [Feature Name]

## Metadata

| Field      | Value                          |
|------------|--------------------------------|
| Feature ID | `[FEAT-XXX]`                   |
| Branch     | `feat/feat-xxx-[feature-name]` |
| Status     | Draft / In Review / Approved   |
| Owner      | `[Owner]`                      |
| Date       | `[YYYY-MM-DD]`                 |

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

| #    | Criterion                                    | Measured By          |
|------|----------------------------------------------|----------------------|
| SC-1 | [Measurable outcome tied to a user scenario] | [Metric or test]     |
| SC-2 | [Measurable outcome tied to a requirement]   | [Metric or test]     |
| SC-3 | [Measurable outcome tied to quality gate]    | [Metric or test]     |

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
| [Risk description] | Low / Medium / High | Low / Medium / High | [Mitigation strategy] |
```

---

## Section Guidelines

- **Metadata**: Use existing project conventions for Feature ID and branch naming.
- **Summary**: Write last. Must be self-contained — someone reading only this paragraph should understand the feature.
- **User Scenarios**: Number sequentially (US-001, US-002...). Each needs priority, independent test, and at least one Given/When/Then.
- **Requirements**: Number sequentially (FR-001, NFR-001). Each must be independently testable. Mark unknowns as `[NEEDS CLARIFICATION]`.
- **Success Criteria**: Tie each criterion to a specific user scenario or requirement. Include how it will be measured.
- **Assumptions**: State what the team is taking as given. Note impact if the assumption is wrong.
- **Clarifications**: Unresolved items marked `[NEEDS CLARIFICATION]`. The agent must never guess these.
- **Out of Scope**: Mandatory. Explicit exclusions prevent scope creep.
- **Risk Notes**: Optional but recommended for P1 features.
