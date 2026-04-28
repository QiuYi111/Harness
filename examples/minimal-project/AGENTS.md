# AGENTS.md

## Project Overview

Todo API is a REST API for managing todo items with basic CRUD operations.
This project follows the Harness spec-governed engineering methodology.

## Setup

1. Copy this file to your project root.
2. Copy `templates/CLAUDE.md` (or equivalent agent instructions file) to your project root.
3. Copy `templates/Makefile` to your project root.
4. Run `make init` to set up the development environment.

## Development Commands

| Command | Purpose |
|---|---|
| `make init` | Initialize project environment |
| `make spec-init FEATURE=001-name` | Create feature spec directory with templates |
| `make lint` | Run code linters |
| `make test` | Run tests |
| `make typecheck` | Run type checks |
| `make contract-test` | Run contract tests |
| `make security-scan` | Scan for security issues (gitleaks) |
| `make verify` | Full product verification (lint + test + typecheck + contract-test + security-scan) |
| `make verify-ai` | Harness/process verification (template integrity + policy compliance) |
| `make classify-risk` | Classify current changes by risk level |

## Architecture Rules

### DDD Layers

- `internal/domain/` - Pure business logic. Depends on NOTHING.
- `internal/infrastructure/` - DB, HTTP, external service adapters. Depends on domain.
- `api/` - Contract definitions (Protobuf/OpenAPI).
- `cmd/` - Application entry points. Wires everything.

### Dependency Direction

```
domain → nothing
infrastructure → domain
cmd → domain + infrastructure
api → generated boundary
```

### Never Reverse Dependencies

- infrastructure MUST NOT import from cmd.
- domain MUST NOT import from infrastructure or api.

## Spec-Driven Workflow

### Feature Lifecycle

```
PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT → REVIEW
```

### Steps

1. Define or reference PRD (project-level requirements).
2. Create feature spec directory: `make spec-init FEATURE=001-feature-name`
3. Fill `specs/001-feature-name/spec.md` with user scenarios and acceptance criteria.
4. Fill `specs/001-feature-name/plan.md` with technical approach and DDD impact.
5. Classify blast radius level (leaf/branch/core/infra).
6. Fill `specs/001-feature-name/tasks.md` with task DAG for agent execution.
7. Write tests first (TDD-RED phase).
8. Implement according to role (TDD-GREEN phase).
9. Refactor if needed (TDD-REFACTOR phase).
10. Run `make verify` and `make verify-ai`.
11. Fill `specs/001-feature-name/eval.md` with acceptance results.
12. Fill `specs/001-feature-name/report.md` with implementation evidence.
13. Review and merge.

## Blast Radius Policy

| Level | Autonomy | Required Gates |
|---|---|---|
| leaf | High | lint, unit_test |
| branch | Medium | spec, plan, tests, review |
| core | Low | human_review, architecture_review, rollback_plan, security_review |
| infra | Very Low | dry_run, human_approval, rollback_plan, security_review |

When uncertain, escalate to the higher risk level.
When touching multiple files, use the highest risk level.
See `templates/BLAST_RADIUS_POLICY.md` for full policy.

## Role Boundaries

| Role | Allowed | Forbidden |
|---|---|---|
| TDD-RED | tests/**, specs/**/eval.md | implementation files |
| TDD-GREEN | internal/**, cmd/** | tests/** |
| TDD-REFACTOR | implementation files | tests/** |
| REVIEWER | docs/reports/**, specs/**/report.md | implementation, tests |
| HUMAN | (approval only) | n/a |

See `templates/ROLE_POLICY.md` for full role definitions.

## Before Commit

1. Run `make verify` - all checks pass.
2. Run `make verify-ai` - harness compliance passes.
3. Run `make classify-risk` - know your risk level.
4. For core/infra changes: get human approval first.
5. Ensure eval.md and report.md are filled for active features.

## Agent Rules

1. Do not implement before reading the active spec.
2. Do not modify tests during GREEN/REFACTOR phase.
3. Classify blast radius before implementation.
4. Core/infra changes require human approval.
5. Every feature must end with eval.md and report.md evidence.
6. Run `make verify` and `make verify-ai` before commit.

## Key References

- `templates/BLAST_RADIUS_POLICY.md` - Full risk classification policy
- `templates/ROLE_POLICY.md` - Full TDD role boundaries
- `templates/PRD_TEMPLATE.md` - Product requirements template
- `templates/SPEC_TEMPLATE.md` - Feature specification template
- `templates/PLAN_TEMPLATE.md` - Implementation plan template
- `templates/TASKS_TEMPLATE.md` - Task DAG template
- `templates/EVAL_TEMPLATE.md` - Evaluation template
- `templates/REPORT_TEMPLATE.md` - Report template
