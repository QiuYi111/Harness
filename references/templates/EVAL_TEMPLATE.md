# Eval: [Feature Name]

> Evaluation checklist for feature completion. Fill this out before requesting merge.

## Product Evaluation

### Acceptance Scenario Validation

| Scenario | Expected | Actual | Pass? | Evidence |
|----------|----------|--------|-------|----------|
| User creates account with valid email | Account created, confirmation email sent | Account created, email sent within 2s | yes | CI test `TestCreateAccount`, logs #4521 |
| User submits form with missing required field | Validation error returned, form not submitted | 400 returned with field-level error messages | yes | Postman screenshot, CI test `TestValidation` |
| User uploads file exceeding size limit | Rejected with clear error message | Rejected with "File must be under 10MB" | yes | Manual test, browser console log |

### Functional Requirement Validation

| FR | Expected | Actual | Pass? | Evidence |
|----|----------|--------|-------|----------|
| FR-001: User authentication via JWT | Login returns access + refresh tokens | Returns both tokens with correct expiry | yes | Integration test `TestAuthFlow` |
| FR-002: Role-based access control | Admin endpoints reject non-admin users | 403 returned for unauthorized roles | yes | RBAC test suite, CI run #112 |
| FR-003: Paginated list endpoint | Returns page of 20 items with metadata | Correct pagination headers and body | no | Off-by-one on last page, see issue #89 |

### Edge Cases

- Empty input submitted (zero-length strings, empty arrays)
- Concurrent requests for the same resource
- Unicode and special characters in text fields
- Maximum allowed payload size exactly at boundary
- Null/undefined values where optional fields exist
- Clock skew between client and server during token validation

### Error Handling

- [x] 400 for malformed request bodies
- [x] 401 for expired/invalid tokens
- [x] 403 for insufficient permissions
- [x] 404 for nonexistent resources
- [x] 409 for duplicate resource creation
- [x] 429 for rate limit exceeded
- [x] 500 responses include correlation ID for tracing
- [ ] Graceful degradation when downstream service unavailable

### Non-Functional Checks

**Performance**
- [ ] P99 latency under target threshold
- [ ] No N+1 query patterns in hot paths
- [ ] Response payload size within acceptable range

**Security**
- [x] Input validation on all external-facing endpoints
- [x] No secrets in logs or error messages
- [x] SQL injection protection verified
- [ ] Dependency vulnerability scan clean

**Observability**
- [x] Structured logging with correlation IDs
- [x] Metrics emitted for key operations
- [ ] Alerting rules defined and tested

---

## Harness Evaluation

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| Spec existed before implementation | yes | Written 2026-04-25, code started 2026-04-26 | yes |
| Plan existed before implementation | yes | `specs/001/plan.md` committed before first code commit | yes |
| Tasks generated | yes | 8 tasks generated, 8 completed | yes |
| Blast radius classified | yes | Classified as `domain` in `CLAUDE.md` | yes |
| Tests not modified during GREEN | yes | Git log shows no test file changes after GREEN phase started | yes |
| Review report produced | yes | `specs/001/reports/implementation-report.md` filed | yes |
| `make verify` passed | yes | Exit 0, all lints clean | yes |
| `make verify-ai` passed | yes | Exit 0, no anti-patterns detected | yes |

---

## Verdict

- [ ] Ready to merge
- [ ] Needs changes

**Notes**: [Describe any remaining concerns or conditions for approval]
