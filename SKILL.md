---
name: harness
description: >
  Entry point and router for Harness-governed AI engineering. Use automatically for
  software engineering tasks, feature implementation, bug fixes, refactors, architecture
  changes, repository initialization, spec/plan/task workflows, risk classification,
  TDD, evaluation, reporting, debugging, product definition, supervisor PM loops,
  code semantic auditing, or when the user says "use Harness", "按 Harness 流程",
  "接管这个任务", "implement this", "fix this", "debug this", "review this",
  "product idea", "worth building", "goal", "supervisor", "atlas", "语义地图",
  "语义审计", "audit this code".
---

# Harness Entry Skill

You are the Harness router. Detect phase, load sub-skill, run CLI gates.

**⚠️  The `subskills/` directory contains internal modules. They are NOT loaded into your context automatically. You only see this SKILL.md, `references/`, and `subskills/` file names. Read a subskill's SKILL.md only when the routing table tells you to.**

## First Move

1. **Check user intent first.** Route by priority:
   - **Product discovery** ("I have an idea", "worth building", "product definition", "MVP", "UI direction") → `harness-grill-product` immediately — even if Harness is not installed. Product discovery does NOT require `.harness/` or `specs/`.
   - **Code audit** ("atlas", "semantic map", "audit this code", "代码语义地图", "语义审计", "帮我搞懂这段代码") → `harness-atlas` immediately — does not require Harness to be installed.
   - **PM loop** ("goal", "supervisor", "advance", "keep going", "PM loop") → `harness-supervisor` — requires `.pm/` directory.
   - **Worker execution** ("execute task", "run next-task.md", "worker") → `harness-intern` — requires `.pm/runtime/next-task.md`.
   - **Architecture review** ("codebase messy", "complex", "untestable", "hard to navigate", "architecture review") → `harness-architecture-review`.
   - **Domain language** ("terminology inconsistent", "ubiquitous language", "define domain terms", "naming ambiguity") → `harness-domain-language`.
   - **Cache optimization** ("reduce token cost", "context too large", "optimize context", "cache") → `harness-cache`.
2. If no special intent matched, check whether Harness is installed in this repo (look for `.harness/`, `AGENTS.md`, `specs/`).
3. If not installed and user intent is engineering (implement, debug, refactor), load and execute `harness-init`.
4. If installed, run `harness status` to see active features and gate status.
5. Identify the current phase using `./references/PHASE_DETECTION.md`.
6. Load the appropriate sub-skill using `./references/ROUTING_TABLE.md`.

## Autopilot

For leaf and branch risk work with clear requirements, proceed through all phases without stopping. Core and infra risk gates always require human approval. See `./references/AUTOPILOT_RULES.md` for full auto-advance rules.

## Deterministic CLI Calls

Use these CLI commands for checks that do not require judgment:

- `harness status` -- show active features and gate status
- `harness classify-risk` -- path-based blast radius classifier
- `harness verify-ai` -- check spec compliance and role boundaries
- `harness eval <feature-id>` -- run spec compliance checks
- `harness context <feature-id>` -- generate minimal context bundle
- `harness context <feature-id> --cache-aware --write` -- cache-friendly context bundle
- `harness cache-report` -- token breakdown by cache layer
- `harness report` -- produce implementation report
- `harness pm-status` -- PM runtime health-check
- `harness pm-next` -- deterministic next-action decision for supervisor
- `harness pm-resume` -- resume context for interrupted PM loops
- `harness pm-branch-plan` -- read-only branch correction plan
- `harness pm-summary` -- audit summary of a supervisor loop run
- `harness atlas <path>` -- generate code semantic atlas

## Interpreting `harness status`

When `harness status` returns output, interpret it as follows:

1. **Feature list** — each active feature with its lifecycle phase (spec → plan → tasks → implement → eval → report → review)
2. **Gate status** — for each feature, which gates have passed and which are pending
3. **Risk level** — the classified blast radius for each feature
4. **Blocked features** — any feature with status `blocked` requires investigation
5. **Action** — the earliest missing artifact determines the next skill to load (see `PHASE_DETECTION.md`)

If no features are active, report "No active features. Start with `harness-specify` to create a new feature, `harness-grill-product` for product discovery, `harness-atlas` for code semantic auditing, or `harness-domain-language` to establish project terminology."

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
- `./references/CACHE_GUIDE.md` -- cache engineering guide (4-layer context ordering)
- `./references/DOMAIN-AWARENESS.md` -- domain terminology and DDD rules

## Path Convention

All paths in Harness skill references are relative to the **Harness repository root** (the directory containing this `SKILL.md`), unless explicitly prefixed with `./` (current working directory) or `.pm/` (project PM directory). Subskills reference each other using repo-root paths like `subskills/risk/SKILL.md`, not relative paths like `../risk/SKILL.md`.
