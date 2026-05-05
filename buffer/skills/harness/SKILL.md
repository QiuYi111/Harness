---
name: harness
description: >
  Entry point and router for Harness-governed AI engineering. Use automatically for
  software engineering tasks, feature implementation, bug fixes, refactors, architecture
  changes, repository initialization, spec/plan/task workflows, risk classification,
  TDD, evaluation, reporting, or when the user says "use Harness", "按 Harness 流程",
  "接管这个任务", "implement this", "fix this", or "review this".
---

# Harness Entry Skill

You are the Harness router. Detect phase, load sub-skill, run CLI gates.

## First Move

1. Check whether Harness is installed in this repo (look for `.harness/`, `AGENTS.md`, `specs/`).
2. If not installed, load and execute `harness-init`.
3. If installed, run `harness status` to see active features and gate status.
4. Identify the current phase using `./references/PHASE_DETECTION.md`.
5. Load the appropriate sub-skill using `./references/ROUTING_TABLE.md`.

## Autopilot

For leaf and branch risk work with clear requirements, proceed through all phases without stopping. Core and infra risk gates always require human approval. See `./references/AUTOPILOT_RULES.md` for full auto-advance rules.

## Deterministic CLI Calls

Use these CLI commands for checks that do not require judgment:

- `harness status` -- show active features and gate status
- `harness classify-risk` -- path-based blast radius classifier
- `harness verify-ai` -- check spec compliance and role boundaries
- `harness eval <feature-id>` -- run spec compliance checks
- `harness context <feature-id>` -- generate minimal context bundle
- `harness report` -- produce implementation report

## Stop Conditions

Stop and ask the human before proceeding when:

- Risk classification returns **core** or **infra** (requires explicit approval)
- Product scope is ambiguous or conflicting
- Acceptance criteria contradict each other
- The requested change violates role boundaries (e.g., test changes during GREEN phase)
- Security, permission, or data-migration implications exist
- You cannot infer the answer from available context

## Reference

- `./references/ROUTING_TABLE.md` -- intent-to-skill mapping
- `./references/PHASE_DETECTION.md` -- how to detect current phase from repo artifacts
- `./references/AUTOPILOT_RULES.md` -- auto-advance rules per risk level
- `./references/DOMAIN-AWARENESS.md` -- domain terminology and DDD rules
