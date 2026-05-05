# PRD Format Reference

Template for `docs/prd/<feature-id>.md`. Use for product-level requirements when the feature warrants a broader document. Replace all `[placeholders]` with actual content.

---

```markdown
# Product Requirement Document: [Feature Name]

| Version | Date       | Status | Author      | Remarks           |
|---------|------------|--------|-------------|-------------------|
| v0.1.0  | [Date]     | Draft  | [Author]    | Initial Definition |

---

## 1. Vision & Scope

### 1.1 Core Definition

- **What**: [Single sentence: what this product does and who it serves]
- **Input**: [Primary data, events, or signals the system receives]
- **Output**: [Primary artifacts, responses, or state changes produced]
- **Core Logic**: [Key transformation between input and output]

### 1.2 MVP Goals

- [Goal 1: measurable, time-boxed target]
- [Goal 2: critical for first release]
- [Goal 3: stretch goal]

### 1.3 Out of Scope

- [Excluded feature 1: reason]
- [Excluded feature 2: reason]
- [Excluded integration 1: reason]

---

## 2. User Stories

### US-001: [Story Title] (Priority: P1)

**Description**: As a [role], I need to [action] so that [outcome].

**Why this priority**: [What breaks if this isn't delivered]

**Independent Test**: [Isolated test: setup, action, assertion]

**Acceptance Scenarios**:
- Given [precondition], When [action], Then [result]
- Given [alternative precondition], When [action], Then [result]
- Given [edge case or error condition], When [action], Then [result]

---

## 3. Functional Requirements

### FR-001: [Requirement Title]

The system must [specific behavior]. When [trigger condition], the system shall [response].

### FR-002: [Requirement Title]

The system must [specific behavior]. [NEEDS CLARIFICATION: ambiguous scenario]

---

## 4. Non-Functional Requirements

### Performance
- **Latency**: [Primary operation] within [N]ms under [load condition]
- **Throughput**: [N] [operations] per second at peak
- **Resource Budget**: [Memory/CPU/storage constraints]

### Security
- **Authentication**: [How identity is proven]
- **Authorization**: [How access control is enforced]
- **Data Protection**: [Encryption expectations]

### Observability
- **Logging**: [What, level, where]
- **Metrics**: [Key operational metrics]

---

## 5. Key Entities

| Entity | Description |
|--------|-------------|
| [EntityA] | [Core domain object, key attributes] |
| [EntityB] | [Relationship to EntityA, responsibility] |

---

## 6. System Architecture

### Core Pattern

[Architectural pattern description: communication, state, failure handling]

### Tech Stack

- **Runtime**: [Language/Framework and version]
- **Storage**: [Primary database, caching layer]
- **Communication**: [Protocols between services and clients]

---

## 7. Interfaces

### Contract (API)

[Reference to API definition file, e.g., `api/openapi/spec.yaml`]

### Data Schema

[Reference to schema files, e.g., `docs/schemas/database.sql`]

---

## 8. Success Criteria

### SC-001: [Criterion Title]

**Metric**: [Quantitative measure]
**Measurement Method**: [How measured]
**Threshold**: [Minimum acceptable value]

---

## 9. Assumptions & Ambiguities

### Assumptions
- [Assumption 1: state and impact if wrong]

### Ambiguities
- [NEEDS CLARIFICATION: what is unclear, who decides]

---

## 10. Hard Truths / Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | [Risk description] | [H/M/L] | [Impact] | [Strategy] |
```

---

## PRD vs Spec Guidance

- **Write a PRD when**: Feature spans multiple teams, has significant business context, or needs executive visibility.
- **A spec alone is enough when**: Feature is self-contained, single-team, and the PRD already exists at the project level.
- **Both**: The spec references the PRD. The PRD contains the "why"; the spec contains the "what and how".
