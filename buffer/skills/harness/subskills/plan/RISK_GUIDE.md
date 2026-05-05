# Risk Classification Guide

Blast radius classification determines agent autonomy and required quality gates. Use this guide when creating an implementation plan.

## Decision Tree

Answer these questions in order. Stop at the first match.

1. **Does the change touch deployment, CI/CD, secrets, or database migrations?** → **infra**
2. **Does the change touch domain models, auth logic, permissions, storage schema, plugin protocol, or the scheduler?** → **core**
3. **Does the change alter behavior across multiple files, touch the service layer, add an endpoint, or implement a feature module?** → **branch**
4. **Is the change limited to docs, tests, a one-off script, an isolated component, or an adapter working against an existing contract?** → **leaf**
5. **Still uncertain?** → Choose the **higher** risk level. Over-classify, never under-classify.

## Risk Levels

### leaf — High Autonomy

Isolated, low-dependency changes. Agent may proceed independently after standard checks.

- **Required gates**: lint, unit_test
- **Examples**: documentation, isolated UI component, one-off script, test file, adapter with existing contract

### branch — Medium Autonomy

Feature-level, multi-file behavior changes. Agent must plan before executing.

- **Required gates**: spec, plan, tests, review_agent
- **Examples**: feature module, service layer, new endpoint, multi-file behavior change

### core — Low Autonomy

Domain, auth, storage, permissions, protocol changes. Wide-reaching impact.

- **Required gates**: human_spec_review, architecture_review, rollback_plan, security_review
- **Examples**: domain model, auth logic, permission system, storage schema, plugin protocol, scheduler
- **Marker**: `[REQUIRES HUMAN REVIEW]` must appear in the plan

### infra — Very Low Autonomy

Deployment, CI/CD, secrets, migrations. Affects the entire system.

- **Required gates**: dry_run, explicit_human_approval, rollback_plan, security_review
- **Examples**: CI/CD pipeline, deployment config, database migration, secrets management
- **Marker**: `[REQUIRES HUMAN REVIEW]` must appear in the plan

## Multi-File Rule

When a change touches multiple files, classify at the **highest** risk level among any file in the change set. A PR that modifies a README (leaf) and an auth middleware (core) is classified as **core**.

## Classification Examples

| Change | Level | Reason |
|--------|-------|--------|
| Fix README typo | leaf | Docs only, zero runtime impact |
| Add isolated CLI helper | leaf | Low dependency, self-contained |
| Add contract test | leaf | Test-only, no production code |
| Add new REST endpoint | branch | Externally visible behavior change |
| Add service method across 3 files | branch | Feature-level behavior change |
| Change domain entity field | core | Affects data model and all consumers |
| Change auth middleware | core | Permission and security impact |
| Add database migration | core/infra | Schema change plus deployment risk |
| Modify GitHub Actions deploy job | infra | Deployment pipeline risk |
| Add .env handling | infra | Secrets and config risk |

## Gate Definitions

| Gate | What It Means |
|------|---------------|
| lint | Code passes linter (make lint) |
| unit_test | Unit tests pass (make test) |
| spec | Feature spec exists and is complete |
| plan | Implementation plan exists and is reviewed |
| tests | Test strategy defined, tests written and passing |
| review_agent | Automated review agent validates the result |
| human_spec_review | Human has reviewed and approved the spec |
| architecture_review | Architecture decisions reviewed by human or architect |
| rollback_plan | Explicit rollback steps documented |
| security_review | Security implications reviewed |
| dry_run | Change executed in dry-run mode, output verified |
| explicit_human_approval | Human has explicitly approved this change |
