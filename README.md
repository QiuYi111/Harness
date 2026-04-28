<div align="center">
  <h1>Harness</h1>
  <p><em>Spec-governed, risk-classified engineering for AI agents.</em></p>
</div>

## What is Harness?

Harness is a spec-governed, risk-classified engineering template for AI agents.

It is not another prompt pack. It is a lightweight engineering harness that tells coding agents what to build, what not to touch, how to prove it works, and when to stop.

## Why not just use Spec Kit / CLAUDE.md / AGENTS.md?

Each of those solves one piece of the problem. Spec Kit handles the spec lifecycle, CLAUDE.md governs a single agent, and AGENTS.md sets cross-agent standards. Harness combines all three into one coherent system: specs drive the work, policies bound the agents, and a shared Makefile ties it together. No glue code, no manual wiring.

## Core Ideas

- **Spec-Governed Development.** Every feature follows `PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT`. Agents don't invent scope; they execute what the spec says.
- **DDD Enforcement.** Strict domain/infrastructure isolation. Domain logic depends on nothing. Infrastructure depends on the domain, never the reverse.
- **TDD Role Isolation.** RED/GREEN/REFACTOR/REVIEWER roles with file boundaries. The agent writing tests cannot edit production code. The implementer cannot touch tests.
- **Blast-Radius-Based Autonomy.** Agent freedom scales with risk level. Low-risk work gets full autonomy. Core domain changes require human review.
- **Makefile as Gatekeeper.** All commands exposed through make targets. `make verify` runs the gates. `make verify-ai` checks spec compliance.

## Quick Start

```bash
make init
make spec-init FEATURE=001-first-feature
# Fill specs/001-first-feature/spec.md
# Fill specs/001-first-feature/plan.md
make verify
make verify-ai
```

That's it. Write your spec, fill your plan, run the gates.

## Workflow

```
PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT → REVIEW
```

- **PRD** — What we're building and why. Business context, success criteria.
- **SPEC** — What the feature must do. Inputs, outputs, edge cases, constraints.
- **PLAN** — How we'll build it. Architecture decisions, file changes, dependencies.
- **TASKS** — Execution order. A task DAG that agents can work through independently.
- **IMPLEMENT** — Agents write code against the spec. Tests gate every change.
- **EVAL** — Did it work? Product acceptance + harness compliance checks.
- **REPORT** — Evidence package. What was built, what was tested, what was deferred.
- **REVIEW** — Human signs off or sends it back.

## Template Inventory

All templates live in `templates/`. Copy what you need, customize the placeholders.

| Template | Purpose |
|---|---|
| `PRD_TEMPLATE.md` | Product-level requirements |
| `SPEC_TEMPLATE.md` | Feature-level specification |
| `PLAN_TEMPLATE.md` | Technical implementation plan |
| `TASKS_TEMPLATE.md` | Task DAG for agent execution |
| `EVAL_TEMPLATE.md` | Product + harness evaluation |
| `REPORT_TEMPLATE.md` | Implementation evidence package |
| `BLAST_RADIUS_POLICY.md` | Risk classification policy |
| `ROLE_POLICY.md` | TDD role boundaries |
| `AGENTS.md` | Cross-agent standard |
| `CLAUDE.md` | Claude-specific routing layer |
| `QUICKSTART_TEMPLATE.md` | Getting started guide |
| `CONTRACT_TEMPLATE.md` | API/contract placeholder |
| `DATA_MODEL_TEMPLATE.md` | Entity/schema documentation |
| `CONSTITUTION_TEMPLATE.md` | Project principles |

## Risk Levels

| Level | Autonomy | What |
|---|---|---|
| `leaf` | High | Docs, tests, isolated components |
| `branch` | Medium | Features, services, endpoints |
| `core` | Low | Domain model, auth, permissions |
| `infra` | Very Low | Deployment, CI/CD, secrets |

When uncertain, escalate to the higher risk level.

## Agent Compatibility

Works with Claude Code, Codex, Cursor, Gemini, Windsurf, and any agent that reads `AGENTS.md` or `CLAUDE.md`.

## Roadmap

- **v2.0** — Template-first + minimal executable gates (current)
- **v2.5** — Lightweight hooks and policy scripts
- **v3.0** — Full CLI/runtime/eval runner/context bundle generator
