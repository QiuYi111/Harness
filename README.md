<div align="center">
  <h1>Harness</h1>
  <p><em>A root skill with progressively disclosed subskills for governed AI engineering.</em></p>
</div>

## What is Harness?

Harness is a single skill pack — one root `harness` skill that automatically detects your engineering phase, routes to the right internal subskill, and runs deterministic CLI gates.

Most users never need to pick a subskill manually. Invoke `harness`, say "use Harness", or just describe your task. The router handles the rest.

No mandatory pipeline. No framework to submit to. Subskills are internal modules loaded on demand by the router — they are not exposed as standalone entries.

## Quick Start

```bash
git clone https://github.com/QiuYi111/Harness
cd Harness
pip install -e .                    # editable install only (see below)
./scripts/link-skills.sh claude-code
```

Your agent now loads one skill: `harness`. The router inside detcts phases and loads subskills as needed.

> **Note:** Harness currently supports **source/editable install** (`pip install -e .`). Standard wheel packaging is planned but not yet available. The CLI works from the cloned repo directory.

## How It Works

```text
harness (entry router)
  │
  ├─ detect phase ───────────────────────┐
  ├─ route to right subskill              │
  ├─ run CLI gate (classify-risk, etc.)   │ references/ (policies, templates, protocols)
  └─ auto-advance until risk gate         │
                                          │
  subskills/ (loaded on demand) ◄─────────┘
  ├── specify   plan   tasks    tdd   risk
  ├── context   eval   report   cache
  ├── domain-language   grill   architecture-review
  └── init
```

## Core Ideas

- **Entry Router.** The `harness` skill detects your current phase (no spec → intake → planning → implementation → verification) and loads the right subskill. You don't pick subskills; the router routes you.
- **Risk-Classified Autonomy.** Agent freedom scales with blast radius. Leaf changes proceed unattended. Core/infra changes require explicit human approval.
- **TDD Role Isolation.** RED/GREEN/REFACTOR/REVIEWER roles with file-level boundaries enforced by `harness verify-ai`.
- **Cache-Aware Context Assembly.** Stable content first, dynamic content last. `harness context --cache-aware` produces cache-friendly context bundles.
- **DDD Enforcement.** Domain logic depends on nothing. Infrastructure depends on the domain, never the reverse.

## Risk Levels

| Level | Autonomy | What | Required Gates |
|-------|----------|------|----------------|
| `leaf` | High | Docs, tests, isolated components | lint, unit_test |
| `branch` | Medium | Features, services, endpoints | spec, plan, tests, review |
| `core` | Low | Domain model, auth, permissions | human_review, architecture_review, rollback_plan, security_review |
| `infra` | Very Low | Deployment, CI/CD, secrets | dry_run, human_approval, rollback_plan, security_review |

When uncertain, escalate to the higher risk level.

## CLI

The deterministic CLI handles what can be done without judgment:

```bash
harness init                  # Initialize a project
harness install-skills        # Symlink skills to agent dir
harness specify 001-feature   # Create feature skeleton
harness classify-risk         # Classify blast radius from changed files
harness verify-ai             # Check skill-pack integrity + role boundaries
harness eval 001-feature      # Run spec compliance checks
harness context 001-feature   # Generate context bundle
harness context 001-feature --cache-aware --write  # Cache-friendly bundle
harness cache-report          # Token breakdown by cache layer
harness status                # Show active features + gate status
```

CLI commands handle deterministic operations. Skills handle judgment.

## Internal Subskills

These are loaded on demand by the harness router. You can invoke them directly, but you rarely need to:

| Subskill | Purpose |
|----------|---------|
| **specify** | Create feature specs with user stories, scenarios, success criteria |
| **plan** | Implementation plan with architecture impact and risk classification |
| **tasks** | Vertical-slice task DAG with dependencies and parallel markers |
| **tdd** | Role-isolated TDD: RED/GREEN/REFACTOR/REVIEWER with file boundaries |
| **risk** | Classify change by blast radius and determine required gates |
| **eval** | Evaluate implementation against spec and process compliance |
| **report** | Implementation report with evidence, risk, rollback plan |
| **context** | Minimal context bundle to reduce agent context pollution |
| **cache** | Cache-friendly context assembly with stable-first ordering |
| **domain-language** | DDD ubiquitous language, CONTEXT.md, ADR records |
| **grill** | Stress-test plans and specs with pointed questions |
| **architecture-review** | Find shallow modules, DDD violations, testability gaps |
| **init** | Initialize a project with Harness engineering discipline |

## Directory Structure

```
Harness/                   # This IS the harness skill — clone directly
├── SKILL.md               # Root entry point (router/autopilot)
├── subskills/             # Internal progressive-disclosure modules
├── references/            # Shared policies, templates, routing tables
│   ├── policies/          # blast-radius.yaml, gates.yaml, cache-context.yaml
│   ├── templates/         # Project scaffolds (spec, plan, CACHE.md, Makefile…)
│   └── examples/          # Reference projects
├── scripts/               # Installer + thin CLI runtime
│   ├── harness_runtime/   # Python CLI modules
│   └── link-skills.sh     # Skill installer
├── .claude-plugin/        # Plugin registry (registers harness as sole entry)
├── MANIFESTO.md           # Engineering principles
├── README.md
└── VERSION
```

## What Changed from v2

| v2 | v3 |
|---|---|
| Template repo — copy-paste workflow | Skill pack — agent loads harness, router does the rest |
| 18 template files, 12 flat skills | 1 root skill, 13 internal subskills |
| Bash scripts for gates | Python CLI with 9 commands |
| Templates as source of truth | Skills as source of truth, templates as resources |
| Bucket-organized directories | Flat subskills/ + references/ structure |

## License

MIT
