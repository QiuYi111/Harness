---
name: harness-plan
description: Create an implementation plan from an existing spec, including architecture impact analysis, DDD layer impact, blast-radius classification (leaf/branch/core/infra), test strategy, and rollback plan. Use after spec exists and before implementation. Use when turning a spec into a build plan.
---

# harness-plan

Read an existing spec and produce a structured implementation plan. Outputs `specs/<feature-id>/plan.md` with architecture decisions, file change list, DDD dependency analysis, blast radius classification, test strategy, and rollback plan.

## When to Use

- User says "plan this spec", "create a plan", "build plan for this feature"
- A spec exists and is approved or in review
- Before starting implementation

## Prerequisites

- An existing spec at `specs/<feature-id>/spec.md` (or a path the user provides)
- The spec should be at least Draft status

## Before Starting

1. Read `../../references/DOMAIN-AWARENESS.md` for project architecture, DDD layers, and terminology.
2. Read the target spec file completely.
3. Scan the codebase to understand current DDD layer structure: `domain/`, `infrastructure/`, `api/`, `cmd/`.

## Steps

1. **Read the spec**: Extract user scenarios, requirements, success criteria, and out-of-scope items.

2. **Analyze architecture impact**: Map each requirement to affected DDD layers. Identify contract changes, data model changes, and cross-layer dependencies.

3. **Classify blast radius**: Use `RISK_GUIDE.md` decision tree. Default to the higher risk level when uncertain. The classification determines required gates.

4. **Draft implementation strategy**: Order the work from foundation → core logic → integration → verification. Reference specific files and modules.

5. **Define test strategy**: Unit tests per layer, integration tests for cross-cutting concerns, edge cases from the spec's acceptance scenarios.

6. **Write rollback plan**: Mandatory for core/infra. Describe specific revert steps for each phase.

7. **Constitution check**: Verify contract-first, DDD direction, TDD/BDD, observability, and security constraints.

8. **Write plan**: Use `PLAN_FORMAT.md` as the template. Save to `specs/<feature-id>/plan.md`.

## Rules

- Never plan without reading the spec first.
- core/infra plans must include a rollback plan.
- core/infra plans must include `[REQUIRES HUMAN REVIEW]` marker.
- When touching multiple files, classify at the highest risk level among them.
- Ask the user about any `[NEEDS CLARIFICATION]` items from the spec before planning.

## Reference Files

- `PLAN_FORMAT.md` — Full plan template with section descriptions
- `RISK_GUIDE.md` — Blast radius classification decision tree and gate requirements
