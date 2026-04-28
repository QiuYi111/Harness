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
├── specs/
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

### Skeleton files created

- **`CONTEXT.md`** — empty glossary stub with the format from `../domain-language/CONTEXT_FORMAT.md`
- **`UBIQUITOUS_LANGUAGE.md`** — empty DDD term mapping stub
- **`.harness/config.yaml`** — project config (project name, risk policy path, skill paths)
- **`specs/`** — empty directory for feature specs
- **`docs/adr/`** — empty directory for architecture decision records

## Process

### 1. Detect project state

Check if this is a greenfield project (empty directory) or an existing codebase. If existing, scan for conflicts with existing files before overwriting.

### 2. Resolve template paths

Templates live in the Harness repo at `templates/`. If running from an installed skill, resolve relative to the skill's install location. For details, see [INIT_GUIDE.md](./INIT_GUIDE.md).

### 3. Create directories and copy files

Create the directory tree. Copy templates. Generate skeleton files.

**Never overwrite existing files.** If a file already exists (e.g., the project already has a `Makefile`), print a warning and skip. The user can merge manually.

### 4. Install skills

Run `harness install-skills` (or equivalent) to wire skill references into the agent's config.

### 5. Print next steps

```
✅ Harness initialized. Next steps:
1. Fill CONTEXT.md with your domain terms (use harness-domain-language)
2. Write your first spec: specs/001-{feature}/spec.md
3. Run make verify to check setup
```

## Options

- `--force` — overwrite existing files (use with caution)
- `--minimal` — only create `CONTEXT.md`, `docs/adr/`, and `Makefile` (skip templates)
- `--templates-dir <path>` — use custom template directory instead of built-in

For the full initialization guide including template resolution and post-init workflows, see [INIT_GUIDE.md](./INIT_GUIDE.md).
