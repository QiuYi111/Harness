# Implementation Plan: Add Todo Item

## Inputs

| Source          | Reference                                          |
|-----------------|----------------------------------------------------|
| Spec            | `specs/001-add-todo/spec.md`                        |
| PRD             | None (first feature, spec serves as source of truth) |
| Related Contracts | `api/todo.proto` (to be created)                 |

## Technical Context

| Dimension             | Value                |
|-----------------------|----------------------|
| Language              | Go                   |
| Framework             | Standard library + chi router |
| Storage               | PostgreSQL           |
| External Dependencies | github.com/go-chi/chi, github.com/lib/pq |

## Architecture Impact

### DDD Layer Impact

| Layer            | Change                              |
|------------------|-------------------------------------|
| `domain/`        | New `todo` package with Todo entity and repository interface |
| `infrastructure/`| New PostgreSQL adapter implementing the todo repository |
| `api/`           | New protobuf/OpenAPI contract for the POST /todos endpoint |
| `cmd/`           | Register new handler on the chi router |

### Contract Impact

- New OpenAPI definition at `api/todo_openapi.yaml` specifying the POST /todos endpoint with request body schema (title: string required, description: string optional) and response schema (id, title, description, completed, created_at).

### Data Model Impact

- New `todos` table in PostgreSQL with columns: id (serial primary key), title (varchar 200 not null), description (varchar 1000), completed (boolean default false), created_at (timestamptz default now()).

## Blast Radius Classification

| Field     | Value                                                              |
|-----------|--------------------------------------------------------------------|
| Level     | `branch`                                                           |
| Reason    | Touches multiple modules (domain, infrastructure, cmd) and adds a new shared route. Does not modify existing domain logic or shared types. |
| Required Gates | spec, plan, tests, automated review                               |

### Classification Guide

- **leaf**: Touches one module, no shared types or contracts
- **branch**: Touches multiple modules or shared types, no cross-cutting concern
- **core**: Changes domain logic, shared contracts, or data model
- **infra**: Changes infrastructure, deployment, storage, or observability

## Constitution Check

| Check          | Pass | Notes |
|----------------|------|-------|
| Contract-first | Yes  | OpenAPI spec created before handler implementation |
| DDD direction  | Yes  | domain depends on nothing, infrastructure depends on domain, cmd wires both |
| TDD/BDD        | Yes  | Unit tests for entity validation, integration test for endpoint |
| Observability  | No   | Logging and metrics deferred to a follow-up feature |
| Security       | Yes  | Input validation on title length and content type enforcement |

## Implementation Strategy

The implementation follows a bottom-up approach through the DDD layers. Start with the API contract to define the boundary, then build the domain entity and repository interface, then implement the infrastructure adapter, and finally wire the handler in cmd.

1. Define the OpenAPI contract at `api/todo_openapi.yaml` so the endpoint shape is locked before any code is written.
2. Implement the Todo domain entity with validation logic and the TodoRepository interface in `internal/domain/todo/`.
3. Implement the PostgreSQL adapter in `internal/infrastructure/todo/adapter.go` that satisfies the repository interface.
4. Wire the handler in `cmd/server/main.go` to register the POST /todos route on the chi router.

## Test Strategy

### Unit Tests

- Todo entity validation: test title too short, too long, valid title, valid title with description.
- Coverage target: 90% for `internal/domain/todo/` package.

### Integration Tests

- POST /todos with valid title-only body returns 201.
- POST /todos with valid title+description body returns 201.
- POST /todos with missing title returns 400.
- POST /todos with empty title returns 400.
- POST /todos with title exceeding 200 chars returns 400.
- Test environment: local PostgreSQL instance via docker-compose.

### Edge Cases

- Title exactly 1 character long (minimum valid).
- Title exactly 200 characters long (maximum valid).
- Title exactly 201 characters long (just over limit).
- Description exactly 1000 characters long.
- Description exactly 1001 characters long.
- Title with leading/trailing whitespace (should be trimmed or rejected).
- Title with only whitespace characters.

## Rollback Plan

1. Remove the route registration in `cmd/server/main.go` (delete the `r.Post("/todos", todoHandler.Create)` line).
2. Drop the `todos` table if the migration was applied: `DROP TABLE IF EXISTS todos;`.
3. Revert the branch: `git revert <merge-commit>` or delete the feature branch.
4. No data loss concern since this is a new table with no existing data dependencies.

## Complexity Tracking

| Field      | Value        |
|------------|--------------|
| Estimated  | Low          |
| Rationale  | Single endpoint, no cross-cutting concerns, straightforward CRUD operation. New module with no modifications to existing domain logic. |

## Rules

- core/infra plan must include rollback plan.
- branch/core/infra must include test strategy.
- core/infra requires human review marker: [REQUIRES HUMAN REVIEW].
