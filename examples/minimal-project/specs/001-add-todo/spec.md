# Feature Spec: Add Todo Item

## Metadata

| Field     | Value                          |
|-----------|--------------------------------|
| Feature ID | `FEAT-001`                    |
| Branch    | `feat/feat-001-add-todo`       |
| Status    | Approved                       |
| Owner     | example-author                 |
| Date      | 2026-04-28                     |

## Summary

This feature adds the ability to create a new todo item via a REST API endpoint. A user sends a POST request with a title and optional description, and the system persists the item and returns it with a generated ID, completion status, and timestamp. This is the first feature in the Todo API project and establishes the foundational domain model and endpoint pattern.

## User Scenarios

### US-001: Create todo with title only

**Priority**: P1

**Independent Test**: Send a POST request to `/todos` with JSON body `{"title": "Buy milk"}`. Expect HTTP 201 with a response body containing `id` (integer), `title` (string, "Buy milk"), `description` (null or empty string), `completed` (boolean, false), and `created_at` (ISO 8601 timestamp).

**Acceptance Scenarios**:
- Given no todos exist, When user POSTs `{"title": "Buy milk"}`, Then todo is created with id=1, completed=false, created_at set to current server time
- Given no todos exist, When user POSTs `{"title": ""}`, Then server returns 400 with error message "title is required"

### US-002: Create todo with title and description

**Priority**: P2

**Independent Test**: Send a POST request to `/todos` with JSON body `{"title": "Buy milk", "description": "From the grocery store"}`. Expect HTTP 201 with both fields preserved in the response.

**Acceptance Scenarios**:
- Given no todos exist, When user POSTs `{"title": "Buy milk", "description": "From the grocery store"}`, Then todo is created with title="Buy milk" and description="From the grocery store"

## Requirements

### Functional Requirements

- **FR-001**: POST /todos endpoint accepts JSON body with required `title` field (string, 1-200 characters). Returns 400 for missing title, empty title, or title exceeding 200 characters.
- **FR-002**: Returns HTTP 201 with created todo object including auto-generated `id` (integer), `completed` (boolean, defaults to false), and `created_at` (ISO 8601 timestamp).
- **FR-003**: Optional `description` field (string, max 1000 characters) is accepted and persisted when provided.

### Non-Functional Requirements

- **NFR-001**: Performance - Response time under 100ms at P99 for the POST /todos endpoint under normal load.
- **NFR-002**: Documentation - OpenAPI spec published documenting the POST /todos endpoint, request body schema, and response schema.

## Success Criteria

| #  | Criterion                                         | Measured By              |
|----|---------------------------------------------------|--------------------------|
| SC-1 | POST /todos returns 201 with valid todo object for title-only input | Integration test `TestCreateTodoWithTitleOnly` |
| SC-2 | POST /todos returns 201 with valid todo object for title+description input | Integration test `TestCreateTodoWithDescription` |
| SC-3 | POST /todos returns 400 for missing, empty, or oversized title | Integration test `TestCreateTodoValidationErrors` |

## Assumptions

- PostgreSQL is available as the persistence layer and already provisioned.
- The API runs behind a router that handles content-type negotiation and basic error formatting.
- No authentication is required for this endpoint (auth will be added in a future feature).

## Clarifications

- None. All requirements are fully specified.

## Out of Scope

- Listing, updating, or deleting todos (separate features).
- User authentication and authorization.
- Pagination or filtering of results.
- Assigning todos to users or categories.

## Risk Notes

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Title validation edge cases missed | Low | Medium | Comprehensive unit tests covering boundary values (0 chars, 1 char, 200 chars, 201 chars) |
| Database connection failure on create | Low | High | Integration test verifies graceful 500 response when DB is unreachable |

## Rules

- Every spec must have at least one user scenario.
- Every P1 scenario must have independent test instructions.
- Every feature must define success criteria.
- Agent must not guess values marked as unresolved. Ask the spec author instead.
