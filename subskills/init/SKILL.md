---
name: harness-init
description: Initialize a new project with Harness engineering discipline. Creates directory structure, copies templates, sets up Makefile, installs skills. Use when starting a new project or adopting Harness on an existing codebase.
---

# Harness Init

Bootstrap a project with the full Harness engineering stack: spec governance, DDD enforcement, TDD role isolation, and blast-radius-based autonomy.

## What it creates

### Directory structure

```
{project_root}/
├── .harness/
│   └── config.yaml
├── .pm/
│   ├── stable/
│   ├── runtime/
│   └── design/
│       └── generated-concepts/
├── specs/
├── maintenance/
│   ├── debug/
│   └── index.md
├── docs/
│   └── adr/
├── CONTEXT.md
├── CLAUDE.md
├── AGENTS.md
└── Makefile
```

### Files copied from templates

| Template | Destination | Purpose |
|---|---|---|
| `Makefile` | `./Makefile` | Gatekeeper targets (`verify`, `verify-ai`) |
| `CONSTITUTION_TEMPLATE.md` | `./CONSTITUTION.md` | Project principles |
| `AGENTS.md` | `./AGENTS.md` | Cross-agent standards |
| `CLAUDE.md` | `./CLAUDE.md` | Claude-specific routing layer |
| `CACHE.md` | `./CACHE.md` | Cache geometry protocol (stable-first context order) |

### Scripts copied from Harness

| Source | Destination | Purpose |
|---|---|---|
| `scripts/verify-ai.sh` | `./scripts/verify-ai.sh` | TDD role boundary enforcement |
| `scripts/classify-risk.sh` | `./scripts/classify-risk.sh` | Path-based blast radius classifier |

### Skeleton files created

- **`CONTEXT.md`** — empty glossary stub with the format from `../domain-language/CONTEXT_FORMAT.md`
- **`UBIQUITOUS_LANGUAGE.md`** — empty DDD term mapping stub
- **`.harness/config.yaml`** — project config (project name, risk policy path, skill paths)
- **`specs/`** — empty directory for feature specs
- **`maintenance/debug/`** — empty directory for debug records
- **`maintenance/index.md`** — empty maintenance index (from DEBUG_INDEX_TEMPLATE.md)
- **`docs/adr/`** — empty directory for architecture decision records

### PM directory skeleton (with `--pm` flag)

When `--pm` is specified, additionally create:

- **`.pm/stable/`** — copy all templates from `references/templates/pm/` (product.md, evidence.md, value-proposition.md, ux-principles.md, user-journeys.md, ui-direction.md, roadmap.md, stage-definitions.md, architecture-guardrails.md, acceptance-rubric.md)
- **`.pm/runtime/`** — copy runtime templates (state.yaml, active-stage.md, next-task.md, worker-report.md, acceptance-review.md, spike-report.md, blockers.md, loop-log.md, handoff.md, loop-control)
- **`.pm/design/`** — empty directory for design probes and UI feedback
- **`.pm/decisions.md`** — decision log template
- **`.pm/runtime/loop-control`** — initialized with `CONTINUE`

## Process

### 1. Detect project state

Check if this is a greenfield project (empty directory) or an existing codebase. If existing, scan for conflicts with existing files before overwriting.

### 2. Resolve template paths

Templates live in the Harness repo at `templates/`. If running from an installed skill, resolve relative to the skill's install location. For details, see [INIT_GUIDE.md](./INIT_GUIDE.md).

### 3. Create directories and copy files

Create the directory tree. Copy templates. Copy Harness scripts (`verify-ai.sh`, `classify-risk.sh`) to `./scripts/`. Generate skeleton files.

**Never overwrite existing files.** If a file already exists (e.g., the project already has a `Makefile`), print a warning and skip. The user can merge manually.

### 4. Install skills

Run `harness install-skills` (or equivalent) to wire skill references into the agent's config.

### 5. Print next steps

```
✅ Harness initialized. Next steps:
1. Fill CONTEXT.md with your domain terms (use harness-domain-language)
2. Write your first spec: specs/001-{feature}/spec.md
3. Debug issues go to: maintenance/debug/
4. Run make verify to check setup
```

## Options

- `--force` — overwrite existing files (use with caution)
- `--minimal` — only create `CONTEXT.md`, `docs/adr/`, and `Makefile` (skip templates)
- `--pm` — additionally create `.pm/` directory with all PM file templates for product evolution
- `--templates-dir <path>` — use custom template directory instead of built-in

For the full initialization guide including template resolution and post-init workflows, see [INIT_GUIDE.md](./INIT_GUIDE.md).

## PM Init (standalone)

If a project already has Harness but needs PM support, `harness-grill-product` will create missing `.pm/` files on first run. Alternatively, manually create the structure:

```bash
mkdir -p .pm/stable .pm/runtime .pm/design/generated-concepts
# Copy templates from references/templates/pm/ into .pm/stable/ and .pm/runtime/
```
