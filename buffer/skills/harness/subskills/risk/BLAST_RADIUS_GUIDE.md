# Blast Radius Guide

Detailed classification guide for the four Harness risk levels.

## Level 1: Leaf

**Autonomy:** High
**Scope:** Isolated, single-component changes with no downstream dependents.

### Characteristics
- Touches a single file or tightly coupled file pair
- No other modules import or depend on the changed code
- Change is reversible without side effects
- No behavioral impact on other features

### Examples
- Updating a README or doc comment
- Adding a unit test for existing behavior
- Refactoring a private function (no signature change)
- Fixing a typo in a constant string
- Adding a log statement to a leaf module

### Required Gates
1. **lint** — code passes linter
2. **unit_test** — existing and new tests pass

### HITL Required: No

---

## Level 2: Branch

**Autonomy:** Medium
**Scope:** Feature-level, multi-file changes with bounded behavioral impact.

### Characteristics
- Spans multiple files within one feature module
- Changes public API or interface signatures
- Affects a user-facing behavior
- Other modules may depend on the changed interface
- Change requires integration testing

### Examples
- Adding a new endpoint to an existing service
- Modifying a repository to return additional data
- Changing validation rules for a feature
- Adding a new domain event type
- Modifying an existing handler's behavior

### Required Gates
1. **spec** — change is covered by an approved spec
2. **plan** — implementation plan exists and was reviewed
3. **tests** — new behavior is tested (TDD preferred)
4. **review** — code review by at least one agent or human

### HITL Required: No (unless spec explicitly requires it)

---

## Level 3: Core

**Autonomy:** Low
**Scope:** Domain model, authentication, authorization, storage, permissions, cross-cutting protocols.

### Characteristics
- Changes the domain model (entities, value objects, aggregates)
- Modifies auth or permission logic
- Changes data persistence (schema, repository contracts)
- Affects protocols used across multiple bounded contexts
- Could break existing integrations if done incorrectly

### Examples
- Adding a new role to the permission system
- Changing an aggregate root's invariants
- Modifying the event sourcing logic
- Changing the authentication token format
- Altering a shared domain event schema

### Required Gates
1. **human_spec_review** — a human has reviewed and approved the spec
2. **architecture_review** — an architect (or architecture-aware agent) has validated the approach
3. **rollback** — a rollback plan exists and is tested
4. **security** — security implications are documented and accepted

### HITL Required: Yes

---

## Level 4: Infra

**Autonomy:** Very Low
**Scope:** Deployment, CI/CD, secrets, database migrations, infrastructure configuration.

### Characteristics
- Changes how the system is deployed or built
- Modifies CI/CD pipeline configuration
- Touches secrets, certificates, or credentials
- Alters database schema (migrations)
- Changes infrastructure-as-code (Terraform, Docker, K8s)
- Could cause downtime if done incorrectly

### Examples
- Adding a new database migration
- Changing the Dockerfile or docker-compose config
- Modifying GitHub Actions / CI pipeline
- Rotating secrets or changing secret management
- Scaling configuration changes
- Network or firewall rule changes

### Required Gates
1. **dry_run** — the change has been validated in a dry-run environment
2. **human_approval** — a human has explicitly approved the change
3. **rollback** — a rollback plan exists and is tested
4. **security** — security scan passes, no secrets exposed

### HITL Required: Yes

---

## Classification Decision Tree

```
START
  │
  ├─ Q1: Touches deployment, CI/CD, secrets, or migrations?
  │    YES → infra
  │    NO ↓
  │
  ├─ Q2: Touches auth, permissions, domain model, or protocols?
  │    YES → core
  │    NO ↓
  │
  ├─ Q3: Spans multiple files or affects user-facing behavior?
  │    YES → branch
  │    NO ↓
  │
  └─ Q4: Single file, no downstream dependents?
       YES → leaf
       NO → branch (safe default escalation)
```

## Escalation Rules

1. **When in doubt, escalate.** Misclassifying up is cautious. Misclassifying down is negligent.
2. **Multi-level changes inherit the highest risk.** If a change is leaf in one file but core in another, classify the whole change as core.
3. **Spec overrides classification.** If the spec marks a feature as requiring human review, honor it regardless of the file-level classification.

## De-escalation

A change can be de-escalated one level only if:
- The change is split into smaller, independent parts
- Each part is classified independently
- No individual part exceeds the lower risk level

Example: A branch-level change to add a new endpoint with auth can be split into:
- leaf: Add route stub (no logic)
- branch: Add handler logic (no auth)
- core: Add auth middleware

Each part runs its own gate requirements.
