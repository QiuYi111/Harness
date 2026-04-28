# Engineering

Core workflow skills for spec-governed, risk-classified AI engineering.

- **[harness-specify](./harness-specify/SKILL.md)** — Create a feature specification with user stories, acceptance scenarios, and success criteria. Use when defining a feature, converting an idea into a spec, writing a PRD, or starting a new implementation workflow.
- **[harness-plan](./harness-plan/SKILL.md)** — Create an implementation plan from a spec, with architecture impact analysis, blast-radius classification, and test strategy. Use when turning a spec into a build plan.
- **[harness-tasks](./harness-tasks/SKILL.md)** — Break a spec and plan into vertical-slice tasks with dependencies and parallel markers. Use when turning a plan into executable work items for AI agents.
- **[harness-tdd](./harness-tdd/SKILL.md)** — Run a role-isolated TDD workflow: RED, GREEN, REFACTOR, REVIEWER with file-level boundary enforcement. Use when implementing features with test-first discipline.
- **[harness-risk](./harness-risk/SKILL.md)** — Classify a proposed change by blast radius (leaf/branch/core/infra) and determine required gates. Use when planning changes that touch multiple files or core logic.
- **[harness-eval](./harness-eval/SKILL.md)** — Evaluate whether an implementation satisfies the spec and whether the agent followed Harness process gates. Use before merge or after implementation.
- **[harness-report](./harness-report/SKILL.md)** — Produce an implementation report with changed files, risk classification, test evidence, and rollback plan. Use after implementation or before PR review.
- **[harness-context](./harness-context/SKILL.md)** — Create a minimal context bundle for a feature to reduce agent context pollution. Use before implementation or review.
- **[harness-domain-language](./harness-domain-language/SKILL.md)** — Extract or maintain a DDD-style ubiquitous language. Identifies ambiguous terms, resolves synonyms, writes CONTEXT.md and ADR records. Use when starting a project or when terminology drifts.
