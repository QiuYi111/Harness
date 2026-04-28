# Changelog

All notable changes to Harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-04-28

### Changed

- **Architecture pivot**: From template repo to composable skill pack. 18 templates → 12 composable skills.
- **Skill-based system**: Each skill has a SKILL.md with YAML frontmatter, imperative instructions, and linked reference files (progressive disclosure pattern from mattpocock/skills).
- **Plugin registry**: `.claude-plugin/plugin.json` registers all 12 skills for Claude Code.
- **Thin CLI**: `harness_runtime/` Python package with `harness` command for deterministic operations (classify-risk, verify-ai, eval, context, status).
- **Installer**: `scripts/link-skills.sh` symlinks skills into agent-specific directories.

### Added

- **12 skills**: harness-specify, harness-plan, harness-tasks, harness-tdd, harness-risk, harness-eval, harness-report, harness-context, harness-domain-language, harness-grill, harness-architecture-review, harness-init.
- **DOMAIN-AWARENESS.md**: Universal consumer contract for all engineering skills.
- **Resources structure**: `resources/templates/`, `resources/policies/`, `resources/examples/`.
- **Bucket READMEs**: skills/engineering/README.md, skills/productivity/README.md, skills/misc/README.md.

### Removed

- Direct template copying workflow (replaced by skill-based invocation).
- Bash-only gate scripts (ported to Python CLI).

## [2.0.0] - 2025-01-28

### Added

- **Feature Artifact Lifecycle**: Standard spec directory structure (`specs/001-feature-name/`) with `spec.md`, `plan.md`, `tasks.md`, `eval.md`, `report.md`.
- **Blast Radius Policy** (`templates/BLAST_RADIUS_POLICY.md`): Four risk levels (leaf/branch/core/infra) with YAML frontmatter, decision tree, and classification examples.
- **Role Policy** (`templates/ROLE_POLICY.md`): TDD role isolation defining RED/GREEN/REFACTOR/REVIEWER/HUMAN with file boundaries and obligations.
- **AGENTS.md** (`templates/AGENTS.md`): Cross-agent standard document with commands table, architecture rules, and spec-driven workflow. No Claude-specific syntax.
- **SPEC_TEMPLATE.md**: Feature-level specification template with user scenarios, requirements, success criteria, and clarification markers.
- **PLAN_TEMPLATE.md**: Technical implementation plan template with DDD layer impact, blast radius classification, and test strategy.
- **TASKS_TEMPLATE.md**: Task DAG template with parallel markers `[P]`, user story references `[US]`, and exact file paths.
- **EVAL_TEMPLATE.md**: Evaluation template with product eval and harness eval sections.
- **REPORT_TEMPLATE.md**: Implementation report template with files changed, risk classification, and rollback plan.
- **QUICKSTART_TEMPLATE.md**: Quickstart template with manual and automated validation paths.
- **CONTRACT_TEMPLATE.md**: Contract placeholder template for OpenAPI/protobuf/event schemas.
- **DATA_MODEL_TEMPLATE.md**: Data model template for entity/schema/migration documentation.
- **CONSTITUTION_TEMPLATE.md**: Project principles and governance template.
- **scripts/classify-risk.sh**: Path-based risk classifier outputting leaf/branch/core/infra.
- **scripts/verify-ai.sh**: Template integrity verification checking file existence, line counts, and branding.
- **examples/minimal-project/**: Example project demonstrating Harness v2 usage with filled artifacts.
- `make spec-init FEATURE=001-name` target: Creates feature spec directories from templates.
- `make verify-ai` target: Runs harness/process verification.
- `make classify-risk` target: Classifies current diff risk level.
- `make security-scan` target: Runs gitleaks when available.
- VERSION file set to `2.0.0`.

### Changed

- **PRD_TEMPLATE.md**: Rewritten with user stories, functional/non-functional requirements, success criteria, ambiguity markers, and out-of-scope section.
- **CLAUDE.md**: Refactored to under 200 lines as a routing layer referencing policies and spec artifacts.
- **Makefile**: Upgraded with v2 targets (`spec-init`, `verify-ai`, `classify-risk`, `security-scan`, `typecheck`, `contract-test`).
- **README.md**: Rewritten for v2 with quick start, workflow diagram, template inventory, and risk levels.
- **MANIFESTO.md**: Added Risk-Classified Autonomy principle.
- **CONTRIBUTING.md**: Updated Golden Path to 14-step spec-first workflow.
- **ARCHITECTURE.md**: Removed TODO, added DDD-to-blast-radius mapping table.
- **IMPLEMENTATION_GUIDE.md**: Added spec-init and spec lifecycle adoption path.
- **.pre-commit-config.yaml**: Upgraded with secret scanning and commit conventions.

### Removed

- All "Neural-Grid" branding references.
- Inconsistent "Framework" naming replaced with "Harness".
