<div align="center">
  <h1>Harness</h1>
  <p><em>A composable skill pack for governed AI engineering.</em></p>
</div>

## What is Harness?

Harness is a skill pack of 12 composable engineering skills for AI coding agents. Each skill does one job. Use them individually or compose them into a full spec-governed workflow.

It is not a framework you submit to. It is a set of tools you invoke. No mandatory pipeline, no orchestration layer.

## Quick Start

```bash
# Install Harness skills into your agent
./scripts/link-skills.sh claude-code

# Or use the CLI
pip install -e .
harness init
harness install-skills
```

Your agent now sees all 12 skills. Invoke them by name when you need them.

## The Skills

### Engineering (Core Workflow)

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| **harness-specify** | Create a feature spec with user stories, Given/When/Then scenarios, success criteria | "spec this", "write a PRD", "define this feature" |
| **harness-plan** | Create an implementation plan with architecture impact and blast-radius classification | "plan this", "turn spec into plan" |
| **harness-tasks** | Break a plan into vertical-slice tasks with dependencies and parallel markers | "break this down", "create task list" |
| **harness-tdd** | Role-isolated TDD: RED/GREEN/REFACTOR/REVIEWER with file-level boundaries | "TDD this", "test-first", "red green refactor" |
| **harness-risk** | Classify a change by blast radius (leaf/branch/core/infra) and determine required gates | "what's the risk", "classify this change" |
| **harness-eval** | Evaluate implementation against spec + process compliance | "did it work", "check compliance" |
| **harness-report** | Produce an implementation report with evidence, risk classification, rollback plan | "write it up", "create evidence package" |
| **harness-context** | Create a minimal context bundle to reduce agent context pollution | "what should I read", "reduce my context" |
| **harness-domain-language** | Extract and maintain a DDD ubiquitous language, CONTEXT.md, and ADR records | "define our terms", "ubiquitous language" |

### Productivity

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| **harness-grill** | Stress-test a plan or spec with pointed questions, one at a time | "grill me", "challenge this plan", "requirements fuzzy" |
| **harness-architecture-review** | Find shallow modules, DDD violations, and testability gaps | "review architecture", "codebase feels complex" |

### Utility

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| **harness-init** | Initialize a project with Harness engineering discipline | "new project", "adopt Harness" |

## Core Ideas

- **Spec-Governed Development.** Every feature follows `SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT`. Agents don't invent scope; they execute what the spec says.
- **DDD Enforcement.** Strict domain/infrastructure isolation. Domain logic depends on nothing. Infrastructure depends on the domain, never the reverse.
- **TDD Role Isolation.** RED/GREEN/REFACTOR/REVIEWER roles with file-level boundaries enforced by `harness verify-ai`.
- **Blast-Radius-Based Autonomy.** Agent freedom scales with risk level. Leaf changes get full autonomy. Core changes require human review.
- **Skills Are Tools, Not a Pipeline.** Invoke any skill independently. No mandatory workflow. `harness-grill` works without `harness-specify`. `harness-risk` works without any other skill.

## Risk Levels

| Level | Autonomy | What | Required Gates |
|-------|----------|------|----------------|
| `leaf` | High | Docs, tests, isolated components | lint, unit_test |
| `branch` | Medium | Features, services, endpoints | spec, plan, tests, review |
| `core` | Low | Domain model, auth, permissions | human_review, architecture_review, rollback_plan, security_review |
| `infra` | Very Low | Deployment, CI/CD, secrets | dry_run, human_approval, rollback_plan, security_review |

When uncertain, escalate to the higher risk level.

## CLI

The thin deterministic CLI handles what can be done without judgment:

```bash
harness init                    # Create directory structure
harness install-skills          # Symlink skills to agent dirs
harness specify 001-feature     # Create specs/001-feature/ skeleton
harness classify-risk           # Path-based blast radius classifier
harness verify-ai               # Check spec compliance + role boundaries
harness eval 001-feature        # Run spec compliance checks
harness context 001-feature     # Generate minimal context bundle
harness status                  # Show active features + gate status
```

## The Deterministic Line

CLI commands handle deterministic operations. Skills handle judgment.

| Can be done without an LLM? | Goes in |
|---|---|
| Yes | `harness` CLI |
| No | Skill (SKILL.md) |

## Design Philosophy

Harness is inspired by [mattpocock/skills](https://github.com/mattpocock/skills) — small, composable, single-purpose skills with progressive disclosure (description → SKILL.md → reference files). What Harness adds on top:

- **Risk classification** — every change is leaf/branch/core/infra
- **Role isolation** — TDD with file-level enforcement, not just process
- **Evidence requirements** — eval and report produce auditable evidence
- **Domain language** — DDD ubiquitous language + ADRs as first-class artifacts

## Agent Compatibility

Works with Claude Code, Codex, Cursor, Windsurf, and any agent that reads SKILL.md files. The `link-skills.sh` installer symlinks skills into agent-specific directories.

## What Changed from v2

v2 was a template repo — copy templates, fill placeholders. v3 is a skill pack — agents load skills on demand, follow structured instructions, and produce governed artifacts.

| v2 | v3 |
|---|---|
| 18 template files | 12 composable skills |
| Copy-paste workflow | Agent-invoked skills |
| Bash scripts for gates | Python CLI |
| Templates as source of truth | Skills as source of truth, templates as resources |

## Directory Structure

```
Harness/
├── skills/              # 12 composable skills
│   ├── engineering/     # 9 core workflow skills
│   ├── productivity/    # 2 process skills
│   └── misc/            # 1 utility skill
├── harness_runtime/     # Thin deterministic CLI
├── resources/
│   ├── templates/       # Supporting templates
│   └── policies/        # Machine-parseable policies
├── scripts/             # Installer script
└── .claude-plugin/      # Plugin registry
```

## License

MIT
