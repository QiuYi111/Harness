# Implementation Report: Add Todo Item

> Filled out after implementation is complete, before requesting merge.

## Summary

Implemented the POST /todos endpoint for creating todo items. The feature introduces a new `todo` domain module with an entity, repository interface, and PostgreSQL adapter. A chi router handler is registered in cmd/server to expose the endpoint. All validation rules from the spec (title required, 1-200 chars, optional description up to 1000 chars) are enforced at the domain layer. One minor follow-up item remains open (see Known Issues).

## Files Changed

| File | Change | Risk Level | Reason |
|------|--------|------------|--------|
| `internal/domain/todo/entity.go` | Added Todo struct with Title, Description, Completed, CreatedAt fields and NewTodo constructor with validation | branch | New domain entity, validates all business rules |
| `internal/domain/todo/repository.go` | Added TodoRepository interface with Create method | branch | New repository interface, no existing code affected |
| `internal/infrastructure/todo/adapter.go` | Implemented PostgresTodoAdapter satisfying TodoRepository using parameterized SQL INSERT | branch | New infrastructure adapter, touches PostgreSQL |
| `internal/domain/todo/entity_test.go` | Unit tests for Todo entity validation (8 test cases) | branch | New test file, no production code changes |
| `tests/integration/todo_test.go` | Integration tests for POST /todos endpoint (5 test cases) | branch | New test file, hits the full HTTP stack |
| `cmd/server/main.go` | Registered POST /todos route on chi router | branch | Existing entry point, small additive change |
| `api/todo_openapi.yaml` | OpenAPI 3.0 spec for POST /todos | branch | New contract file |
| `specs/001-add-todo/spec.md` | Feature specification | docs | Specification artifact |
| `specs/001-add-todo/plan.md` | Implementation plan | docs | Planning artifact |
| `specs/001-add-todo/tasks.md` | Task DAG | docs | Execution artifact |

## Architecture Decisions

1. **Validation in the domain entity, not the handler**: The `NewTodo` constructor enforces all business rules (title length, non-empty). The HTTP handler delegates to the domain layer and never validates directly. This keeps validation logic testable without HTTP machinery.

2. **Repository interface in domain, adapter in infrastructure**: The `TodoRepository` interface lives in `internal/domain/todo/`. The PostgreSQL implementation lives in `internal/infrastructure/todo/`. This preserves DDD dependency direction: infrastructure depends on domain, never the reverse.

3. **chi router over standard library mux**: Chose chi for cleaner route grouping and middleware support. The standard library `http.ServeMux` would work but chi provides a more ergonomic API for future route expansion (listing, updating, deleting todos).

## Tests

| Suite | Result | Evidence |
|-------|--------|----------|
| Unit Tests | PASS (8/8) | `internal/domain/todo/entity_test.go`, `go test ./internal/domain/todo/` |
| Integration Tests | PASS (5/5) | `tests/integration/todo_test.go`, `go test ./tests/integration/` |
| Contract Tests | PASS (1/1) | OpenAPI spec validated against test requests |
| Lint / Static Analysis | PASS (0 warnings) | `make verify`, CI run #301 |

## Verification

- `make verify`: PASS (exit 0, all lints clean, no unused imports, all types checked)
- `make verify-ai`: PASS (exit 0, no anti-patterns, no hardcoded secrets, no debug logging)
- `classify-risk`: `branch` (new endpoint touching multiple modules, no changes to existing domain logic)

## Review Summary

- Reviewer confirmed DDD layering is correct. Domain depends on nothing. Infrastructure depends on domain. No reverse dependencies.
- Suggested adding structured logging to the handler. Deferred to follow-up feature since observability was explicitly marked out of scope in this spec.
- OpenAPI spec correctly documents request and response schemas.
- Parameterized SQL queries verified, no injection risk.

## Known Issues

1. No structured logging or correlation IDs on the POST /todos handler. Errors return plain text messages rather than structured JSON error objects. Tracked as a follow-up for the observability feature.

## Rollback Plan

1. Delete the route registration in `cmd/server/main.go` (remove the `r.Post("/todos", todoHandler.Create)` line).
2. Run `DROP TABLE IF EXISTS todos;` against the PostgreSQL instance to remove the created table.
3. Revert the feature branch: `git revert <merge-commit>` or delete `feat/feat-001-add-todo`.
4. No data loss: the `todos` table is new with no foreign key dependencies. Existing tables and data are untouched.

## Final Verdict

- [x] Approved
- [ ] Needs revision

---

## Rules

- core/infra changes must include rollback plan.
- report must include risk classification.
- report must include verification evidence.
