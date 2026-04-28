# Contributing to {Project Name}

> **"Pragmatic > Dogmatic. Automation > Manual. Consensus > Command."**

Welcome to the team. This document is not a suggestion; it is the **Law** of this repository. We rely on strict process enforcement to maintain velocity and quality.

## 1. Core Principles

1.  **Environment as Code**: "It works on my machine" is an invalid defense. If it doesn't work in Docker/CI, it doesn't work.
2.  **Contract First**: No backend code is written until the API definition (Protobuf/OpenAPI) is reviewed and merged.
3.  **Strict DDD**:
    -   `internal/domain` depends on NOTHING.
    -   `internal/infrastructure` depends on `domain`.
4.  **TDD & BDD**:
    -   **Pure Logic?** TDD. Write `thing_test.go` before `thing.go`.
    -   **Feature Flow?** BDD. Write Integration Tests before wiring `main.go`.
5.  **Observability**: No `print` statements. Use structured logs with searchable keys.
6.  **AI-First Collaboration**: We leverage AI agents (e.g., Claude Code) governed by `CLAUDE.md`. Humans define the architecture and requirements, Agents assist in the execution. Always ensure AI context is up-to-date.

---

## 2. Development Interface

We do not memorize commands. We use `make`.

| Command | Purpose |
| :--- | :--- |
| `make init` | **Start Here**. Installs tools and hooks. |
| `make up` | Starts the *entire* infrastructure in Docker. |
| `make down` | Tears down infrastructure and cleans volumes. |
| `make proto` | **Generates** code from contracts. |
| `make test` | Runs Unit + Integration tests. |
| `make typecheck` | Runs type checks. |
| `make contract-test` | Runs contract tests. |
| `make security-scan` | Scans for security issues (gitleaks). |
| `make lint` | Runs linters and static checks. |
| `make verify` | **The Gatekeeper**. Runs everything. Run this before push. |
| `make verify-ai` | Harness/process verification (template integrity + policy compliance). |
| `make classify-risk` | Classifies current changes by blast radius risk level. |
| `make spec-init FEATURE=xxx` | Creates feature spec directory with templates. |

---

## 3. The Workflow (The "Golden Path")

When you pick up a ticket, follow this **exact** sequence:

### Phase 0: Context Assembly
1. Read AGENTS.md and CLAUDE.md for project context.
2. Read the active feature spec (specs/xxx/spec.md).

### Phase 1: Specification
3. Create feature spec directory: `make spec-init FEATURE=001-feature-name`
4. Fill `spec.md` with user scenarios and acceptance criteria.
5. Fill `plan.md` with technical approach and DDD impact.
6. Classify blast radius: run `make classify-risk`.

### Phase 2: Task Planning
7. Fill `tasks.md` with task DAG (include [P] parallel markers and [US] story references).

### Phase 3: Implementation
8. Write tests first (TDD-RED role — tests/** only).
9. Implement minimal code (TDD-GREEN role — internal/**, cmd/** only).
10. Refactor if needed (TDD-REFACTOR role — never touch tests).

### Phase 4: Verification
11. Run `make verify` (product verification).
12. Run `make verify-ai` (harness/process verification).

### Phase 5: Evidence & Review
13. Fill `eval.md` with acceptance results and harness evaluation.
14. Fill `report.md` with implementation evidence, files changed, and risk classification.

---

## 4. Coding Standards

-   **Formatting**: Enforced via hook.
-   **Linting**: Zero-tolerance policy.
-   **Errors**: Return semantic errors, not generic strings.
