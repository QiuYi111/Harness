# Product Requirement Document: [Project Name]

> **Note for Authors**: This PRD must be written with clear, structured markdown. It is designed to be directly consumed by AI Agents (via `CLAUDE.md` workflows) as the definitive source of truth. Every section must contain meaningful content, not just headings.

| Version | Date | Status | Author | Remarks |
| :--- | :--- | :--- | :--- | :--- |
| v0.1.0 | {Date} | **Draft** | {Author} | Initial Definition |

---

## 1. Vision & Scope

### 1.1 Core Definition

* **What**: A single sentence that describes what this product does and who it serves.
* **Input**: The primary data, events, or signals the system receives from users or external systems.
* **Output**: The primary artifacts, responses, or state changes the system produces.
* **Core Logic**: The key transformation or value the system performs between input and output. What makes this worth building instead of using something off the shelf?

### 1.2 MVP Goals

* {Goal 1}: A measurable, time-boxed target the MVP must hit.
* {Goal 2}: A second target that is critical for the first release.
* {Goal 3}: A stretch goal that's nice to have but won't block launch.

### 1.3 Out of Scope

The following are explicitly **NOT** included in this version. Any agent or engineer working on this project should treat these as hard boundaries, not open questions.

* {Excluded feature 1}: Brief reason why it's excluded (e.g., deferred to v2, handled by external system).
* {Excluded feature 2}: Brief reason.
* {Excluded integration 1}: Brief reason.
* {Excluded data source 1}: Brief reason.

---

## 2. User Stories

### US-001: {Story Title} (Priority: P1)

**Description**: As a {role}, I need to {action} so that {outcome}. Describe the concrete interaction and what the user expects to see or receive.

**Why this priority**: Explain why this story is P1. What breaks or what user segment is blocked if this isn't delivered?

**Independent Test**: Describe a test that can verify this story in isolation, without depending on any other user story being implemented. Include the setup, the action, and the assertion.

**Acceptance Scenarios**:
* Given {precondition about system state or user context}, When {the user performs this action}, Then {this is the observable result}.
* Given {an alternative precondition}, When {the same or different action}, Then {the expected result under these conditions}.
* Given {an edge case or error condition}, When {the action that triggers it}, Then {the graceful failure or error message}.

---

### US-002: {Story Title} (Priority: P2)

**Description**: As a {role}, I need to {action} so that {outcome}.

**Why this priority**: Explain why this is P2. It matters, but the product can ship without it.

**Independent Test**: Describe the isolated test scenario.

**Acceptance Scenarios**:
* Given {precondition}, When {action}, Then {result}.
* Given {edge case}, When {action}, Then {result}.

---

## 3. Functional Requirements

### FR-001: {Requirement Title}

The system must {specific behavior}. When {trigger condition}, the system shall {response}. {Any constraints on timing, ordering, or data format.}

### FR-002: {Requirement Title}

The system must {specific behavior}. This applies when {scope condition}.

### FR-003: {Requirement Title}

The system must {specific behavior}. [NEEDS CLARIFICATION: What exactly happens when {ambiguous scenario}? Is there a fallback, a retry, or an error state?]

---

## 4. Non-Functional Requirements

### Performance

* **Latency**: The {primary operation} must complete within {N} milliseconds under {load condition}.
* **Throughput**: The system must handle {N} {operations} per second at peak load.
* **Resource Budget**: {Memory/CPU/storage constraints under normal operation.}

### Security

* **Authentication**: {How users or services prove their identity.}
* **Authorization**: {How access control is enforced per role or resource.}
* **Data Protection**: {Encryption at rest and in transit expectations.}

### Privacy

* **Data Collection**: {What user data is collected and why.}
* **Data Retention**: {How long data is kept and how it's deleted.}
* **Compliance**: {Regulatory requirements, e.g., GDPR, CCPA.}

### Observability

* **Logging**: {What gets logged, at what level, and where.}
* **Metrics**: {Key operational metrics the system must expose.}
* **Tracing**: {Whether distributed tracing is required and what spans are expected.}

### Compatibility

* **Platforms**: {Operating systems, browsers, or runtime environments supported.}
* **Integrations**: {External systems or APIs this must work with.}
* **Backward Compatibility**: {Expectations around versioning and migration.}

---

## 5. Key Entities

| Entity | Description |
| :--- | :--- |
| **{EntityA}** | The core domain object that represents {concept}. Contains {key attributes}. |
| **{EntityB}** | The {relationship} to EntityA. Manages {responsibility}. |
| **{EntityC}** | A supporting entity that tracks {state or metadata}. |

---

## 6. System Architecture

### Core Pattern

{Describe the architectural pattern. For example: "Event-driven microservices with a command/query separation. Commands mutate state through a write model; queries are served by a read-optimized projection. All inter-service communication is asynchronous via message queues, except for user-facing read paths which use synchronous REST."}

Include a brief description of:
* How components communicate.
* Where state lives.
* How the system handles failures (retry, circuit breaker, graceful degradation).

### Tech Stack

* **Runtime**: {Language/Framework and version.}
* **Storage**: {Primary database, caching layer, and any specialized stores.}
* **Communication**: {Protocols used between services and with external clients.}
* **Infrastructure**: {Containerization, orchestration, CI/CD platform.}

---

## 7. Interfaces

### Contract (API)

Reference the API definition file here. For example:

* REST: `api/openapi/spec.yaml`
* gRPC: `api/proto/{service}.proto`

The contract is the source of truth. No implementation may deviate from the agreed schema.

### Data Schema

Reference or describe the core data models. For example:

* Relational schema: `docs/schemas/{database}.sql`
* Document schema: `docs/schemas/{collection}.json`

List the key tables or collections and their relationships. Note any constraints, indexes, or partitioning strategy.

---

## 8. Success Criteria

### SC-001: {Criterion Title}

**Metric**: {Quantitative measure, e.g., "API response time p99 < 200ms."}

**Measurement Method**: {How this will be measured in production or staging.}

**Threshold**: {The minimum acceptable value. Below this, the criteria is not met.}

### SC-002: {Criterion Title}

**Metric**: {Quantitative measure, e.g., "User completes {workflow} in under {N} seconds."}

**Measurement Method**: {How this will be measured.}

**Threshold**: {The minimum acceptable value.}

---

## 9. Assumptions & Ambiguities

### Assumptions

* {Assumption 1}: State the assumption and its impact if it turns out to be wrong.
* {Assumption 2}: State the assumption and its impact.
* {Assumption 3}: State the assumption and its impact.

### Ambiguities

* [NEEDS CLARIFICATION: {What is unclear? What decision needs to be made? Who needs to make it?}]
* [NEEDS CLARIFICATION: {Another open question with context about why it matters.}]

---

## 10. Hard Truths / Risks

| # | Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| 1 | {Describe the risk clearly. What could go wrong?} | {High/Medium/Low} | {What happens to the project if this materializes?} | {Concrete steps to reduce likelihood or soften the blow.} |
| 2 | {Risk description.} | {High/Medium/Low} | {Impact description.} | {Mitigation strategy.} |
| 3 | {Risk description.} | {High/Medium/Low} | {Impact description.} | {Mitigation strategy.} |

---

## Rules

* Every user story must be independently testable.
* Every ambiguity must be marked with [NEEDS CLARIFICATION].
* Agent must not guess values marked [NEEDS CLARIFICATION].
* Out of Scope is mandatory.
