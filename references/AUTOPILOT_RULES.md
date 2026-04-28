# Autopilot Rules

Harness should proceed automatically unless a stop condition is reached.

## Default Autopilot

If a task is leaf or branch risk and requirements are clear:

1. Create or update spec artifacts if missing.
2. Create plan and tasks if missing.
3. Classify risk.
4. Generate context bundle.
5. Execute implementation using appropriate TDD role.
6. Run verify-ai.
7. Produce eval/report.

## Fast Path for Leaf Work

For leaf changes (docs, typo fixes, tests, isolated scripts, templates):

- Do NOT force full SPEC -> PLAN -> TASKS lifecycle.
- Classify risk.
- Make change.
- Run relevant verification.
- Write short report only if user asks or PR requires it.

## Branch Path

For feature-level work (services, endpoints, new features):

- SPEC required
- PLAN required
- TASKS required
- EVAL/REPORT required before merge

## Core Path

For domain/auth/schema/permission changes:

- SPEC required
- PLAN required
- Rollback plan required
- Human approval required BEFORE implementation
- EVAL/REPORT required
- Architecture review recommended

## Infra Path

For CI/CD/deployment/secrets/migration:

- Dry run required
- Rollback plan required
- Explicit human approval required
- Security review required
- No auto-merge

## Never Ask If You Can Infer

Do NOT ask the user for:
- Feature ID if one can be generated from context
- File paths if repo structure reveals them
- Test command if Makefile exposes it
- Risk level if classify-risk can determine it
- Context files if context bundle can be generated

## Always Ask For

Stop and ask human input when:
- Core or infra risk requires approval
- Product scope is ambiguous
- Acceptance criteria conflict
- The requested change violates role boundaries
- Implementation would require changing tests during GREEN phase
- Security/permission/data-migration implications exist
