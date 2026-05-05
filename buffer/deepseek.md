# Harness v2 Implementation Plan

> **Status**: Draft | **Created**: 2026-04-28 | **Target**: v2.0.0

## 0. Executive Summary

### Problem Statement

Harness v1 succeeds as a **personal discipline system** — it provides AI agent prompts (CLAUDE.md), a Makefile interface, and a PRD template. But it lacks the **runtime governance** needed for production agent engineering: no blast-radius classification, no machine-enforced guards, no eval suite, no feature-level artifact lifecycle, no cross-agent standard (AGENTS.md), no security gates.

### Architecture Decision: Harness wraps spec-kit

**Decision**: Harness v2 will wrap spec-kit (already vendored at `3rdParty/spec-kit/`) as its execution engine. Harness adds the governance, safety, context-engineering, and eval layers that spec-kit does not provide.

| Concern | spec-kit provides | Harness v2 adds |
|---|---|---|
| Feature lifecycle | `speckit.specify/plan/tasks/implement` | Pre-flight checks, post-implementation gates, human-in-the-loop for core changes |
| Spec templates | `spec.md`, `plan.md`, `tasks.md` | Extended PRD with `[NEEDS CLARIFICATION]`, `eval.md`, `report.md` |
| Agent integration | 30+ agents via registry | `AGENTS.md` as cross-agent source of truth |
| Task structure | `[P]` markers, phase deps | Guard hooks that validate `[P]` claims at runtime |
| Project principles | `constitution.md` | `constitution.md` → `blast-radius.yaml` risk-to-policy mappings |
| CI/CD | GitHub Actions (test/lint/release) | Security scan, spec-drift check, role-enforcement hooks |
| CLI | `specify` CLI | `harness` CLI for guard/classify-risk/sync-agent-docs |

### Target Architecture

```text
Project/
├── .harness/                    # [NEW] Harness governance layer
│   ├── constitution.md          # Source of truth for all policies
│   ├── commands.yaml            # Command registry (what agents can do)
│   ├── state.json               # Project state tracking
│   └── policies/
│       ├── blast-radius.yaml    # Risk classification for all file types
│       ├── permissions.yaml     # What each role can touch
│       └── roles.yaml           # Role definitions (RED/GREEN/REFACTOR/REVIEW)
│
├── .github/workflows/           # [NEW] CI/CD
│   ├── ci.yml                   # Lint + test + typecheck
│   ├── security-scan.yml        # Secret scan + dependency audit
│   └── harness-guards.yml       # Harness-specific policy checks
│
├── specs/                       # [NEW] Feature-level artifacts (spec-kit convention)
│   └── 001-feature-name/
│       ├── spec.md              # spec-kit generated
│       ├── plan.md              # spec-kit generated
│       ├── research.md          # spec-kit generated
│       ├── contracts/           # spec-kit generated
│       ├── data-model.md        # spec-kit generated
│       ├── quickstart.md        # spec-kit generated
│       ├── tasks.md             # spec-kit generated (with [P] markers)
│       ├── eval.md              # [NEW] Harness eval criteria
│       └── report.md            # [NEW] Harness implementation report
│
├── evals/                       # [NEW] Harness eval suite
│   ├── harness/                 # Validates harness itself
│   │   ├── no-test-edit-during-green.yaml
│   │   ├── core-change-requires-review.yaml
│   │   └── report-required.yaml
│   └── product/                 # Validates generated software
│       ├── api-contract-cases.yaml
│       └── e2e-playwright-cases.yaml
│
├── project_index/               # [NEW] Context engineering layer
│   ├── repo.md                  # Global map
│   ├── modules/                 # Per-module context
│   ├── decisions/               # Architecture Decision Records
│   └── api-map.md               # API surface map
│
├── scripts/                     # [EXPANDED]
│   ├── guard-role-permission.sh # [NEW]
│   ├── guard-no-secret.sh       # [NEW]
│   ├── guard-touched-files.sh   # [NEW]
│   └── context-bundle.sh        # [NEW]
│
├── templates/                   # [UPGRADED]
│   ├── CLAUDE.md                # [UPGRADED] v2 with blast-radius awareness
│   ├── PRD_TEMPLATE.md          # [UPGRADED] Extended anti-hallucination fields
│   ├── Makefile                 # [UPGRADED] v2 targets
│   ├── ARCHITECTURE.md          # [UPGRADED] Fixed TODO, DDD policy
│   ├── CONTRIBUTING.md          # [UPGRADED] v2 workflow
│   ├── .pre-commit-config.yaml  # [UPGRADED] More hooks
│   ├── eval-template.md         # [NEW]
│   └── report-template.md       # [NEW]
│
├── AGENTS.md                    # [NEW] Cross-agent standard
├── .gitignore                   # [NEW]
├── README.md                    # [UPGRADED]
├── CHANGELOG.md                 # [NEW]
└── VERSION                      # [NEW]
```

---

## Phase 0: Foundation (Week 1)

> **Goal**: Establish the `.harness/` governance layer, AGENTS.md, CI/CD, and basic safety rails.

### File 1: `.harness/constitution.md`

**Purpose**: Single source of truth for all Harness policies. All other configs (AGENTS.md, blast-radius.yaml, Makefile, CLAUDE.md) are DERIVED from this file.

**Specification**:

```markdown
# Harness Constitution

## Article 1: Environment as Code
- If it requires more than `make init` to start developing, it is broken.
- Docker Compose & Dev Containers are mandatory.
- Enforcement: CI gate `make init` MUST exit 0.

## Article 2: Contract First
- No backend code is written before the API definition is reviewed and merged.
- Frontend and Backend work in parallel against the contract.
- Enforcement: `harness guard no-code-before-contract`

## Article 3: Strict DDD
- `internal/domain` depends on NOTHING (no SQL, no HTTP).
- `internal/infrastructure` depends on `domain`. Never reverse.
- Enforcement: CI linter + `harness guard no-domain-imports-infra`

## Article 4: TDD & BDD
- Pure logic → TDD (Red → Green → Refactor).
- Feature flows → BDD (Integration tests before wiring).
- Enforcement: `harness guard role-permission` blocks role violations.

## Article 5: Observable Logging
- Banned: `print`, `console.log`.
- Required: Structured logging (JSON) with searchable keys.
- Enforcement: Pre-commit hook.

## Article 6: AI-First Collaboration
- Agents are governed by this constitution, not ad-hoc prompts.
- Human defines architecture; Agent executes within defined blast radius.
- Enforcement: `harness guard blast-radius` classifies every change.

## Article 7: CI is the Gatekeeper
- Pre-commit blocks low-level garbage.
- CI blocks logical failures.
- Rule: If CI is red, the branch does not exist.

## Article 8: Spec Over Code
- Specs are primary artifacts; code is expression of spec.
- Every feature MUST have a complete spec/ bundle before implementation.
- Enforcement: `harness guard spec-required-before-implement`

## Article 9: Security by Default
- No secrets in code. No hardcoded credentials.
- Dependencies must be audited.
- Enforcement: `harness guard no-secret` + CI security scan.
```

**Dependencies**: None.
**Estimated effort**: 30 min (adapt from existing MANIFESTO.md).

---

### File 2: `.harness/policies/blast-radius.yaml`

**Purpose**: Classifies every file/pattern by risk level, determining agent autonomy and required gates.

**Specification**:

```yaml
# Blast Radius Policy
# Determines: (a) what autonomy level an agent has, (b) what gates must pass before merge.

risk_levels:

  leaf:
    description: "Isolated, stateless, low-impact changes"
    examples:
      - "isolated UI component"
      - "one-off script"
      - "documentation (*.md)"
      - "adapter with existing contract"
      - "test file (tests/**)"
      - "Makefile targets"
    file_patterns:
      - "docs/**"
      - "*.md"
      - "tests/**"
      - "scripts/**"
      - "templates/**"
    autonomy: high
    max_parallel_agents: 5
    required_gates:
      - lint
      - unit_test
    review_requirements:
      autonomous_review: true
      human_review: false

  branch:
    description: "Feature module, service layer, multi-file behavior"
    examples:
      - "feature module"
      - "service layer"
      - "multi-file behavior change"
      - "new API endpoint"
    file_patterns:
      - "internal/infrastructure/**"
      - "cmd/**"
      - "api/**"
    autonomy: medium
    max_parallel_agents: 3
    required_gates:
      - spec_exists          # specs/xxx/spec.md must exist
      - plan_exists          # specs/xxx/plan.md must exist
      - unit_test
      - integration_test
      - review_agent
    review_requirements:
      autonomous_review: true
      human_review: false

  core:
    description: "Domain model, auth, permissions, storage schema, plugin protocol"
    examples:
      - "domain entity changes"
      - "auth logic"
      - "permission system"
      - "storage schema migration"
      - "plugin protocol"
      - "scheduler logic"
    file_patterns:
      - "internal/domain/**"
      - "**/auth/**"
      - "**/migrations/**"
      - "**/schema/**"
    autonomy: low
    max_parallel_agents: 1
    required_gates:
      - spec_exists
      - plan_exists
      - human_spec_review
      - architecture_review
      - migration_plan
      - rollback_plan
      - unit_test
      - integration_test
      - security_review
      - review_agent
    review_requirements:
      autonomous_review: true
      human_review: true
      human_review_triggers:
        - "any change to internal/domain/**"
        - "any auth/permission change"
        - "any schema migration"

  infra:
    description: "CI/CD, deployment, database migration, secrets management"
    examples:
      - "CI/CD pipeline changes"
      - "deployment configuration"
      - "database migration (execution)"
      - "secrets/credential management"
    file_patterns:
      - ".github/workflows/**"
      - "docker-compose*.yml"
      - "Dockerfile*"
      - ".env*"
    autonomy: very_low
    max_parallel_agents: 1
    required_gates:
      - dry_run
      - rollback_plan
      - explicit_approval
      - security_review
    review_requirements:
      autonomous_review: false
      human_review: true
      human_review_triggers:
        - "all changes require human sign-off"

# Classification rules for multi-file changes:
# When a commit touches files across multiple levels, the HIGHEST risk level applies.
# Example: commit touches docs/* + internal/domain/* → classified as "core".
```

**Dependencies**: `.harness/constitution.md`
**Estimated effort**: 1 hour.

---

### File 3: `.harness/policies/roles.yaml`

**Purpose**: Formalizes the TDD role definitions from CLAUDE.md into machine-readable format.

**Specification**:

```yaml
roles:
  tdd-red:
    display_name: "TDD-RED (Test Writer)"
    description: "Writes failing tests only. Never writes implementation."
    permissions:
      write:
        - "tests/**"
        - "specs/**/spec.md"
        - "specs/**/eval.md"
      read:
        - "**/*"
      forbidden:
        - "internal/domain/*.go"        # No implementation in domain
        - "internal/infrastructure/**"  # No infra implementation
    post_action:
      - "Mark test files as read-only for subsequent phases"
      - "Confirm tests are FAILING before handoff"

  tdd-green:
    display_name: "TDD-GREEN (Implementer)"
    description: "Writes minimal code to make tests pass. NEVER modifies tests."
    permissions:
      write:
        - "internal/domain/**"
        - "internal/infrastructure/**"
        - "cmd/**"
      forbidden:
        - "tests/**"                    # NEVER modify tests
    constraints:
      - "If tests are impossible to satisfy, STOP and write bug report to docs/reports/bugs/"
      - "Never lower test requirements"
    post_action:
      - "Confirm all existing tests pass"
      - "Do NOT mark tests as complete - refactorer does that"

  tdd-refactor:
    display_name: "TDD-REFACTOR (Refactorer)"
    description: "Optimizes code under test protection. Must keep all tests green."
    permissions:
      write:
        - "internal/domain/**"
        - "internal/infrastructure/**"
        - "cmd/**"
      forbidden:
        - "tests/**"                    # NEVER modify tests
    constraints:
      - "All tests must remain GREEN after refactoring"
    post_action:
      - "Run full test suite"
      - "Run linter"

  reviewer:
    display_name: "Review Agent"
    description: "Independent code review. No implementation bias."
    permissions:
      write:
        - "docs/reports/reviews/**"
      read:
        - "**/*"
      forbidden:
        - "internal/**"                 # Read-only for code
        - "tests/**"                    # Read-only for tests
        - "cmd/**"                      # Read-only for entrypoints
    post_action:
      - "Generate review report"
      - "Flag issues for implementer to fix"

  human:
    display_name: "Human Architect"
    permissions:
      write:
        - "**/*"
      read:
        - "**/*"
    description: "Full access. Defines architecture and approves core changes."
```

**Dependencies**: `.harness/constitution.md`
**Estimated effort**: 45 min.

---

### File 4: `.harness/policies/permissions.yaml`

**Purpose**: Maps roles to file patterns with read/write/forbidden permissions.

**Specification**:

```yaml
# Permission Matrix
# Maps roles to file access patterns

permissions:
  test_files:
    pattern: "tests/**"
    roles:
      tdd-red: write
      tdd-green: forbidden
      tdd-refactor: forbidden
      reviewer: read
      human: write

  domain_logic:
    pattern: "internal/domain/**"
    roles:
      tdd-red: forbidden
      tdd-green: write
      tdd-refactor: write
      reviewer: read
      human: write

  infrastructure:
    pattern: "internal/infrastructure/**"
    roles:
      tdd-red: forbidden
      tdd-green: write
      tdd-refactor: write
      reviewer: read
      human: write

  contracts:
    pattern: "api/**"
    roles:
      tdd-red: read
      tdd-green: read
      tdd-refactor: read
      reviewer: read
      human: write

  specs:
    pattern: "specs/**"
    roles:
      tdd-red: read
      tdd-green: read
      tdd-refactor: read
      reviewer: read
      human: write

  docs:
    pattern: "docs/**"
    roles:
      tdd-red: write    # Bug reports
      tdd-green: write  # Bug reports
      tdd-refactor: write
      reviewer: write   # Review reports
      human: write

  config:
    pattern: ".harness/**"
    roles:
      tdd-red: read
      tdd-green: read
      tdd-refactor: read
      reviewer: read
      human: write

  ci_cd:
    pattern: ".github/**"
    roles:
      tdd-red: forbidden
      tdd-green: forbidden
      tdd-refactor: forbidden
      reviewer: forbidden
      human: write
```

**Dependencies**: `.harness/policies/roles.yaml`
**Estimated effort**: 30 min.

---

### File 5: `.harness/commands.yaml`

**Purpose**: Registry of all harness commands available to agents and humans.

**Specification**:

```yaml
commands:
  init:
    description: "Initialize a new Harness project"
    entry: "scripts/init.sh"
    args: ["project-name"]

  guard:
    description: "Run safety guard checks"
    subcommands:
      role-permission:
        description: "Check if current role can touch modified files"
        entry: "scripts/guard-role-permission.sh"
        args: ["--role"]
      no-secret:
        description: "Scan for secrets in changed files"
        entry: "scripts/guard-no-secret.sh"
      no-unapproved-migration:
        description: "Block unapproved database migrations"
        entry: "scripts/guard-no-unapproved-migration.sh"
      blast-radius:
        description: "Classify risk level of current changes"
        entry: "scripts/guard-touched-files.sh"

  classify-risk:
    description: "Classify risk level of a file or change set"
    entry: "scripts/classify-risk.sh"
    args: ["target"]

  context-bundle:
    description: "Generate minimal context bundle for a feature"
    entry: "scripts/context-bundle.sh"
    args: ["feature-id"]

  sync-agent-docs:
    description: "Sync AGENTS.md and CLAUDE.md from .harness/constitution.md"
    entry: "scripts/sync-agent-docs.sh"

  verify:
    description: "Run full verification (product + harness)"
    subcommands:
      product:
        description: "Product-level verification (lint, test, build)"
        entry: "make verify"
      ai:
        description: "Harness-level verification (spec coverage, role compliance, security)"
        entry: "make verify-ai"

  review:
    description: "Run autonomous review agent"
    entry: "scripts/launch-review-agent.sh"
```

**Dependencies**: None.
**Estimated effort**: 30 min.

---

### File 6: `.harness/state.json`

**Purpose**: Tracks project-level state (current spec, active role, checkpoint).

**Specification**:

```json
{
  "version": "2.0.0",
  "project_name": "",
  "current_feature": null,
  "active_role": null,
  "last_verify": null,
  "checkpoints": {}
}
```

**Dependencies**: None.
**Estimated effort**: 15 min.

---

### File 7: `AGENTS.md`

**Purpose**: Cross-agent governance standard. Generated from `.harness/constitution.md` via `harness sync-agent-docs`. Must work with Claude Code, Codex, Cursor, Windsurf, Copilot, Gemini CLI, and other agents.

**Specification**:

```markdown
# AGENTS.md

> **This file is auto-generated from `.harness/constitution.md`.**
> Run `harness sync-agent-docs` to regenerate. Do not edit manually.

## Project Overview

[Project name and one-line description]

## Setup

```bash
make init     # Install tools, hooks, dependencies
make up       # Start infrastructure (Docker)
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `make init` | Initialize development environment |
| `make up` | Start all infrastructure in Docker |
| `make down` | Tear down infrastructure |
| `make proto` | Generate code from API contracts |
| `make test` | Run all tests |
| `make lint` | Run linters |
| `make verify` | Full verification before push |
| `make verify-ai` | Harness-specific AI quality checks |

## Architecture

- `internal/domain/` — Pure business logic. NO external dependencies.
- `internal/infrastructure/` — DB, HTTP, RPC implementations. Depends on domain.
- `api/` — Contract definitions (Protobuf/OpenAPI).
- `cmd/` — Application entry points.
- `specs/` — Feature specifications and artifacts.
- `docs/` — Documentation, PRDs, reports.

## Coding Standards

- TDD mandatory for domain logic.
- BDD mandatory for feature flows.
- Structured logging only (no `print`/`console.log`).
- Contract-first: no code before API definition is merged.

## Security

- No secrets in code.
- No hardcoded credentials.
- Dependencies audited via CI.
- All changes classified by blast radius.

## Agent Guidelines

### Blast Radius Policy
- **Leaf** (docs, tests, scripts): High autonomy. Lint + test required.
- **Branch** (infrastructure, endpoints): Medium autonomy. Spec + plan + tests + review required.
- **Core** (domain, auth, schema): Low autonomy. Human review required.
- **Infra** (CI/CD, deploy, secrets): Very low autonomy. Explicit approval required.

### Role-Based Access
- **TDD-RED**: Write tests only. Never implement.
- **TDD-GREEN**: Write minimal implementation. NEVER modify tests.
- **TDD-REFACTOR**: Optimize under test protection. NEVER modify tests.
- **REVIEWER**: Read-only code review. Produce review report.
- **HUMAN**: Full access. Approve core changes.

### Before Every Commit
1. Run `make verify`
2. Run `harness guard blast-radius`
3. Confirm CI is green

## Spec-Driven Development

Every feature follows the spec-kit lifecycle:
1. `/speckit.specify` — Define requirements
2. `/speckit.clarify` — Resolve ambiguities
3. `/speckit.plan` — Create technical plan
4. `/speckit.tasks` — Generate task list
5. `/speckit.implement` — Execute implementation
6. `harness verify` — Full verification
7. `harness review` — Autonomous review
```

**Dependencies**: `.harness/constitution.md`, `.harness/commands.yaml`
**Estimated effort**: 1 hour (template) + `sync-agent-docs.sh` script.

---

### File 8: `.github/workflows/ci.yml`

**Purpose**: Standard CI pipeline for lint, test, typecheck.

**Specification**:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linters
        run: make lint

  test:
    runs-on: ubuntu-latest
    services:
      # Add project-specific services (postgres, redis, etc.)
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make test

  verify:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Full verification
        run: make verify
```

**Dependencies**: None.
**Estimated effort**: 30 min.

---

### File 9: `.github/workflows/security-scan.yml`

**Purpose**: Automated security scanning (secrets, dependencies, static analysis).

**Specification**:

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * 1'  # Weekly on Monday

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Secret scanning
        uses: github/codeql-action/init@v3
      - name: Run analysis
        uses: github/codeql-action/analyze@v3

  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Audit dependencies
        run: |
          # Language-specific dependency audit
          # npm audit / pip-audit / go mod verify / cargo audit
          echo "Run dependency audit"

  harness-guards:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Harness guard checks
        run: |
          harness guard no-secret
          harness guard blast-radius
```

**Dependencies**: `.harness/policies/blast-radius.yaml`
**Estimated effort**: 30 min.

---

### File 10: Root `.gitignore`

```gitignore
# Dependencies
node_modules/
vendor/
__pycache__/
*.pyc
.venv/
venv/

# Build
dist/
build/
*.exe
*.dll
*.so
*.dylib

# Environment
.env
.env.local
.env.*.local
*.log

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Harness
.harness/state.json

# Docker
docker-compose.override.yml
```

**Estimated effort**: 10 min.

---

## Phase 1: Feature Lifecycle & Templates (Week 2)

### File 11: `templates/PRD_TEMPLATE.md` (UPGRADE)

**Current state**: 42 lines with Vision, Input, Output, Core Logic, Architecture, Interfaces, Hard Truths.
**Target state**: Add User Stories, Acceptance Scenarios, Functional Requirements, Success Criteria, Out of Scope, Assumptions, `[NEEDS CLARIFICATION]` markers.

**Specification** — Full template with these sections:

```markdown
# Product Requirement Document (PRD): {Project Name}

> **Note for AI Agents**: This PRD is the definitive source of truth.
> Sections marked `[NEEDS CLARIFICATION]` MUST be resolved before implementation.
> All user stories MUST be independently testable.

| Version | Date | Status | Author | Remarks |
|---------|------|--------|--------|---------|
| v0.1.0  | DATE | Draft  | TEAM   | Initial |

## 1. Vision & Scope

### 1.1 Core Definition
- **What**: One sentence description.
- **Input**: What data enters the system.
- **Output**: What data leaves the system.
- **Core Logic**: The main value proposition.

### 1.2 MVP Goals
- Goal 1
- Goal 2

### 1.3 Out of Scope *(mandatory)*
- Explicitly excluded feature 1
- Explicitly excluded feature 2

## 2. User Stories *(mandatory)*

<!--
  Each story MUST be:
  - Independently testable (delivers value alone)
  - Prioritized (P1 = MVP, P2 = important, P3 = nice-to-have)
  - Include Given/When/Then acceptance scenarios
-->

### US-001: [Brief Title] (Priority: P1)

**Description**: [Plain language description of the user journey]

**Why this priority**: [Justification]

**Independent Test**: [How to verify this story standalone]

**Acceptance Scenarios**:
- **Given** [initial state], **When** [user action], **Then** [expected outcome]
- **Given** [initial state], **When** [user action], **Then** [expected outcome]

### US-002: [Brief Title] (Priority: P2)

[Same structure...]

## 3. Functional Requirements *(mandatory)*

- **FR-001**: System MUST [capability]
- **FR-002**: System MUST [capability]
- **FR-003**: [NEEDS CLARIFICATION: what authentication method?]

## 4. Non-Functional Requirements *(mandatory)*

### 4.1 Performance
- Target latency / throughput

### 4.2 Security
- Auth requirements, data protection

### 4.3 Observability
- Logging format, metrics, alerting

### 4.4 Compatibility
- Platform, browser, API version support

## 5. System Architecture

### 5.1 Core Pattern
Event-Driven / REST / Actor Model / etc.

### 5.2 Tech Stack
- **Runtime**: Language/Framework
- **Storage**: Databases
- **Communication**: Protocols

## 6. Interfaces

### 6.1 Contract (API)
Reference to `.proto` or OpenAPI spec.

### 6.2 Data Schema
Key entities and relationships.

## 7. Success Criteria *(mandatory)*

- **SC-001**: [Measurable outcome]
- **SC-002**: [Measurable outcome]
- **SC-003**: [Measurable outcome]

## 8. Assumptions

- Assumption 1 about users/environment
- Assumption 2 about dependencies
- Assumption 3 about scope boundaries

## 9. Ambiguities *(mandatory)*

<!--
  Mark anything unclear with [NEEDS CLARIFICATION].
  AI agents MUST NOT guess — they must flag these.
-->

- [NEEDS CLARIFICATION: specific question here]
- [NEEDS CLARIFICATION: another question]

## 10. Risks (Hard Truths)

1. **Risk 1**: Description → Mitigation strategy
2. **Risk 2**: Description → Mitigation strategy
```

**Dependencies**: None (standalone template upgrade).
**Estimated effort**: 1 hour.

---

### File 12: `templates/eval-template.md` (NEW)

**Purpose**: Template for feature-level eval criteria. Used by both harness eval and product eval.

**Specification**:

```markdown
# Eval Criteria: {Feature Name}

**Feature**: {feature-id} | **Spec**: specs/{feature-id}/spec.md | **Date**: {date}

## Product Evals

### Acceptance Scenario Validation

| Scenario ID | Description | Given | When | Then | Status | Evidence |
|-------------|-------------|-------|------|------|--------|----------|
| AS-001 | {description} | {state} | {action} | {expected} | ⬜ Pass / ❌ Fail | |
| AS-002 | {description} | {state} | {action} | {expected} | ⬜ Pass / ❌ Fail | |

### Functional Requirement Validation

| FR ID | Requirement | Status | Evidence |
|-------|-------------|--------|----------|
| FR-001 | {requirement} | ⬜ / ❌ | |
| FR-002 | {requirement} | ⬜ / ❌ | |

### Edge Case Validation

| Edge Case | Expected Behavior | Actual Behavior | Status |
|-----------|-------------------|-----------------|--------|
| {case 1} | {expected} | {actual} | ⬜ |
| {case 2} | {expected} | {actual} | ⬜ |

### Non-Functional Validation

| NFR Type | Target | Actual | Status |
|----------|--------|--------|--------|
| Performance | {target} | {actual} | ⬜ |
| Security | {target} | {actual} | ⬜ |

## Harness Evals

### Process Compliance

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Spec exists before code | specs/{id}/spec.md present | | ⬜ |
| Plan exists before code | specs/{id}/plan.md present | | ⬜ |
| Tasks generated | specs/{id}/tasks.md present | | ⬜ |
| TDD role isolation | Tests not modified during GREEN | | ⬜ |
| Review completed | Review report exists | | ⬜ |
| Report generated | specs/{id}/report.md present | | ⬜ |

### Blast Radius Compliance

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Risk classification correct | Matches blast-radius.yaml | | ⬜ |
| Gates passed for risk level | All required gates green | | ⬜ |
| Core changes human-reviewed | Review record exists | | ⬜ |

## Overall Verdict

- [ ] All product evals pass
- [ ] All harness evals pass
- [ ] Ready for merge

**Evaluator**: {agent/name} | **Date**: {date}
```

**Dependencies**: None.
**Estimated effort**: 1 hour.

---

### File 13: `templates/report-template.md` (NEW)

**Purpose**: Standardized implementation report for each feature.

**Specification**:

```markdown
# Implementation Report: {Feature Name}

**Feature**: {feature-id} | **Branch**: {branch-name} | **Date**: {date}
**Spec**: specs/{feature-id}/spec.md | **Plan**: specs/{feature-id}/plan.md

## Summary

[2-3 sentence summary of what was built]

## Changes

### Files Created
| File | Purpose | Risk Level |
|------|---------|------------|
| path/to/file.go | description | leaf/branch/core/infra |

### Files Modified
| File | Purpose | Risk Level |
|------|---------|------------|
| path/to/file.go | description | leaf/branch/core/infra |

## Architecture Decisions

### ADR: {Title}
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Consequences**: [What this enables and constrains]

## Test Results

| Test Suite | Total | Passed | Failed | Coverage |
|------------|-------|--------|--------|----------|
| Unit | | | | |
| Integration | | | | |
| Contract | | | | |
| E2E | | | | |

## Review Summary

- **Review Agent**: {agent name}
- **Issues Found**: {count} (Resolved: {count}, Open: {count})
- **Review Verdict**: [Approve / Changes Requested]

## Remaining Issues

| Issue | Severity | Owner | Status |
|-------|----------|-------|--------|
| {description} | high/medium/low | {assignee} | open/in-progress |

## Rollback Plan

[If this change goes wrong, how do we revert?]

1. {step 1}
2. {step 2}

**Report Author**: {name} | **Date**: {date}
```

**Dependencies**: None.
**Estimated effort**: 45 min.

---

## Phase 2: Guard Scripts & Eval Suite (Week 3)

### Files 14-17: Guard Scripts

All guard scripts follow the same pattern: take `--role` and target file list, check against policies, exit 0 (pass) or 1 (fail) with error message.

#### File 14: `scripts/guard-role-permission.sh`

```bash
#!/usr/bin/env bash
# guard-role-permission.sh — Check if current role can touch the modified files
set -euo pipefail

ROLE="${1:---role required}"
shift
FILES=("$@")

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLICY_DIR="$SCRIPT_DIR/../.harness/policies"

source "$POLICY_DIR/../lib/common.sh"

for file in "${FILES[@]}"; do
  if ! check_permission "$ROLE" "$file"; then
    echo "❌ Permission denied: Role '$ROLE' cannot modify '$file'"
    exit 1
  fi
done

echo "✅ Role permission check passed for role '$ROLE'"
```

#### File 15: `scripts/guard-no-secret.sh`

```bash
#!/usr/bin/env bash
# guard-no-secret.sh — Scan changed files for secrets/credentials
set -euo pipefail

FILES=("$@")

# Patterns to detect
SECRET_PATTERNS=(
  'password\s*=\s*["'"'"'][^"'"'"']+["'"'"']'
  'secret\s*=\s*["'"'"'][^"'"'"']+["'"'"']'
  'api[_]?key\s*=\s*["'"'"'][^"'"'"']+["'"'"']'
  '-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----'
)

for file in "${FILES[@]}"; do
  for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -qE "$pattern" "$file" 2>/dev/null; then
      echo "❌ Potential secret found in $file"
      exit 1
    fi
  done
done

echo "✅ No secrets detected"
```

#### File 16: `scripts/guard-touched-files.sh`

```bash
#!/usr/bin/env bash
# guard-touched-files.sh — Classify risk level of changed files
set -euo pipefail

FILES=("$@")
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLICY="$SCRIPT_DIR/../.harness/policies/blast-radius.yaml"

# Parse YAML and classify each file
# Output: RISK_LEVEL for each file, overall HIGHEST risk
# Exit 0 with classification; exit 1 if classification fails

# Normalize: the highest risk level among all files applies
MAX_RISK=0  # 0=leaf, 1=branch, 2=core, 3=infra

for file in "${FILES[@]}"; do
  risk=$(classify_file "$file" "$POLICY")
  echo "  $file → $risk"
  # Update MAX_RISK
done

echo "Overall risk level: $MAX_RISK_LEVEL"
echo "$MAX_RISK_LEVEL" > /tmp/harness-risk-level
```

#### File 17: `scripts/context-bundle.sh`

```bash
#!/usr/bin/env bash
# context-bundle.sh — Generate minimal context bundle for a feature
set -euo pipefail

FEATURE_ID="${1:-}"
if [ -z "$FEATURE_ID" ]; then
  echo "Usage: context-bundle.sh <feature-id>"
  exit 1
fi

SPEC_DIR="specs/$FEATURE_ID"
CONTEXT_FILE="$SPEC_DIR/context.md"

# Generate context bundle
{
  echo "# Context Bundle: $FEATURE_ID"
  echo ""
  echo "## Required Context"
  echo ""
  echo "@project_index/repo.md"
  echo "@$SPEC_DIR/spec.md"
  echo "@$SPEC_DIR/plan.md"

  # Auto-detect related modules from plan.md
  if [ -f "$SPEC_DIR/plan.md" ]; then
    echo ""
    echo "## Related Modules"
    grep -oP 'project_index/modules/\K[^)]+' "$SPEC_DIR/plan.md" 2>/dev/null || true
  fi

  echo ""
  echo "## Forbidden Context"
  echo "Do not scan unrelated modules."
  echo "Do not load archived experiments."
} > "$CONTEXT_FILE"

echo "✅ Context bundle generated: $CONTEXT_FILE"
```

**Dependencies**: `.harness/policies/` (blast-radius.yaml, permissions.yaml, roles.yaml)
**Estimated effort**: 2 hours total for all 4 scripts.

---

### Files 18-19: Eval Configurations

#### File 18: `evals/harness/no-test-edit-during-green.yaml`

```yaml
name: "No Test Edit During GREEN Phase"
description: "Verifies that TDD-GREEN agents never modify test files"
check:
  type: "git-diff"
  pattern: "tests/**"
  forbidden_roles: ["tdd-green", "tdd-refactor"]
severity: "critical"
failure_action: "block_merge"
```

#### File 19: `evals/harness/core-change-requires-review.yaml`

```yaml
name: "Core Change Requires Review"
description: "Verifies that core-level changes have human review approval"
check:
  type: "process-gate"
  trigger: "files matching internal/domain/** or **/auth/**"
  required_evidence: "human_review_approval.md in specs/*/"
severity: "critical"
failure_action: "block_merge"
```

#### File 20: `evals/harness/report-required.yaml`

```yaml
name: "Report Required Per Feature"
description: "Verifies every completed feature has an implementation report"
check:
  type: "file-exists"
  pattern: "specs/*/report.md"
  condition: "exists for every spec.md in specs/*/"
severity: "medium"
failure_action: "warn"
```

**Estimated effort**: 1.5 hours for all eval YAML files.

---

### Files 21-22: Context Engineering

#### File 21: `project_index/repo.md`

A global map of the repository. Template to be filled per project:

```markdown
# Project Index: {project-name}

## Quick Reference
- **Language**: {language}
- **Framework**: {framework}
- **Database**: {database}
- **Entry Point**: `cmd/server/main.go`

## Architecture Overview

[Brief description of system architecture, key components, and their relationships]

## Module Map

| Module | Path | Purpose | Dependencies |
|--------|------|---------|--------------|
| Domain | internal/domain/ | Pure business logic | None |
| Infrastructure | internal/infrastructure/ | DB, HTTP, RPC | domain |
| API Contracts | api/ | Protobuf/OpenAPI | None |
| Entry Points | cmd/ | Application wiring | domain, infrastructure |

## Key Decisions

See `project_index/decisions/ADR-*.md`

## API Surface

See `project_index/api-map.md`
```

#### File 22: `project_index/decisions/ADR-template.md`

```markdown
# ADR-{NNN}: {Title}

**Status**: [Proposed / Accepted / Deprecated / Superseded]
**Date**: {YYYY-MM-DD}
**Deciders**: {names}

## Context

[What is the issue that we're seeing that is motivating this decision or change?]

## Decision

[What is the change that we're proposing and/or doing?]

## Consequences

[What becomes easier or more difficult to do because of this change?]
```

**Estimated effort**: 1 hour.

---

## Phase 3: CLI & Polish (Week 4)

### File 23: `templates/Makefile` (UPGRADE)

Add new targets to existing 8-target Makefile:

```makefile
# New targets for v2:

# --- 5. Harness Governance ---

verify-ai: ## Run AI-specific harness checks
	@echo "🤖 Running Harness AI Verification..."
	@bash scripts/guard-role-permission.sh
	@bash scripts/guard-no-secret.sh
	@bash scripts/guard-touched-files.sh
	@echo "✅ Harness AI verification passed."

classify-risk: ## Classify risk level of current changes
	@echo "🎯 Classifying risk level..."
	@bash scripts/guard-touched-files.sh $$(git diff --name-only HEAD)

sync-agent-docs: ## Sync AGENTS.md and CLAUDE.md from constitution
	@echo "📝 Syncing agent documentation..."
	@bash scripts/sync-agent-docs.sh
	@echo "✅ Agent docs synced."

security-scan: ## Run security scanning
	@echo "🛡️  Running security scan..."
	@bash scripts/guard-no-secret.sh
	@# Add dependency audit
	@echo "✅ Security scan passed."

# Updated verify target:
verify: up proto lint test security-scan ## Run full verification (Pre-Push Gate)
	@echo "🛡️  Full System Verification Passed."
```

**Dependencies**: Guard scripts must exist.
**Estimated effort**: 30 min.

---

### File 24: `harness` CLI (scaffold)

Minimal CLI in bash for Mac/Linux:

```bash
#!/usr/bin/env bash
# harness — Harness CLI entry point
set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)/.harness"

usage() {
  cat <<EOF
Harness v2 — Spec-Governed Agentic Engineering Harness

Usage: harness <command> [args]

Commands:
  init <name>         Initialize a new Harness project
  guard <type>        Run safety guard checks
  classify-risk       Classify risk level of changes
  context-bundle      Generate context bundle for feature
  sync-agent-docs     Sync AGENTS.md and CLAUDE.md from constitution
  verify              Run product + harness verification
  review              Launch autonomous review agent

EOF
  exit 0
}

case "${1:-}" in
  init)       shift; bash scripts/init.sh "$@" ;;
  guard)      shift; bash scripts/guard-${1}.sh "${@:2}" ;;
  classify-risk) bash scripts/guard-touched-files.sh $(git diff --name-only HEAD) ;;
  context-bundle) shift; bash scripts/context-bundle.sh "$@" ;;
  sync-agent-docs) bash scripts/sync-agent-docs.sh ;;
  verify)     make verify && make verify-ai ;;
  review)     bash scripts/launch-review-agent.sh ;;
  *)          usage ;;
esac
```

**Dependencies**: All scripts must exist.
**Estimated effort**: 1 hour.

---

### Files 25-28: Documentation Updates

#### File 25: `templates/CONTRIBUTING.md` (UPGRADE)

Add:
- Blast radius policy reference
- `harness` CLI commands
- `make verify-ai` requirement
- Eval submission requirement
- Updated Golden Path (6 phases → 7 phases with eval)

#### File 26: `templates/ARCHITECTURE.md` (UPGRADE)

- Fix `TODO: sync with guide`
- Add DDD enforcement policy
- Add blast radius implications for domain changes

#### File 27: `README.md` (UPGRADE)

- Rename from "Framework" / "Neural-Grid Framework" to "Harness"
- Add v2 features
- Add spec-kit integration reference
- Updated architecture diagram

#### File 28: `templates/CLAUDE.md` (UPGRADE)

- Add blast-radius awareness
- Add `harness guard` invocation before committing
- Add reference to AGENTS.md
- Add spec-kit workflow integration

**Estimated effort**: 2 hours total for all doc updates.

---

## Dependency Graph

```text
Phase 0 (Foundation)
├── File 1: .harness/constitution.md  ← No deps
├── File 6: .harness/state.json       ← No deps
├── File 5: .harness/commands.yaml    ← No deps
├── File 10: .gitignore               ← No deps
├── File 2: .harness/policies/blast-radius.yaml  ← Depends on constitution.md
├── File 3: .harness/policies/roles.yaml         ← Depends on constitution.md
├── File 4: .harness/policies/permissions.yaml   ← Depends on roles.yaml
├── File 7: AGENTS.md                  ← Depends on constitution.md, commands.yaml
├── File 8: .github/workflows/ci.yml   ← No deps
└── File 9: .github/workflows/security-scan.yml ← Depends on blast-radius.yaml

Phase 1 (Feature Lifecycle)
├── File 11: templates/PRD_TEMPLATE.md (upgrade) ← No deps
├── File 12: templates/eval-template.md           ← No deps
└── File 13: templates/report-template.md         ← No deps

Phase 2 (Agent Runtime)
├── Files 14-16: scripts/guard-*.sh    ← Depends on .harness/policies/
├── File 17: scripts/context-bundle.sh ← No deps
├── Files 18-20: evals/harness/*.yaml  ← Depends on blast-radius.yaml, roles.yaml
└── Files 21-22: project_index/*.md    ← No deps

Phase 3 (CLI & Polish)
├── File 23: templates/Makefile (upgrade) ← Depends on guard scripts
├── File 24: harness CLI                   ← Depends on all scripts
└── Files 25-28: Doc updates               ← Depends on all above
```

---

## Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| SC-001: Every feature has complete spec bundle | `specs/*/` contains spec.md, plan.md, tasks.md, eval.md, report.md |
| SC-002: Agents respect blast radius | Guard scripts block unauthorized file touches |
| SC-003: TDD role isolation is enforced | GREEN phase cannot modify test files |
| SC-004: Security scan runs in CI | `.github/workflows/security-scan.yml` passes |
| SC-005: Cross-agent standard exists | `AGENTS.md` at root, generated from `.harness/` |
| SC-006: Harness eval suite runs | All `evals/harness/*.yaml` checks pass on sample project |
| SC-007: Context bundles reduce token usage | `harness context-bundle <feature>` produces <500 tokens of context |
| SC-008: CLI is usable | `harness init`, `harness guard`, `harness verify` work on clean checkout |

---

## Risks

| Risk | Mitigation |
|------|------------|
| spec-kit integration is too tight — Harness becomes spec-kit dependent | AGENTS.md and constitution.md remain spec-kit-agnostic; spec-kit is a recommended but optional execution layer |
| Blast-radius classification is too rigid for rapid prototyping | Add `--skip-guards` flag for prototype/spike branches |
| CLI complexity exceeds value for template repo | Start with bash scripts; migrate to Go/Python only if adoption warrants it |
| AGENTS.md diverges from CLAUDE.md | `harness sync-agent-docs` as part of CI; divergence triggers CI failure |
