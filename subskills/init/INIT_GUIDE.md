# Init Guide

Detailed reference for the `harness-init` skill. Covers template resolution, file generation, post-init workflows, and edge cases.

## Template resolution

Templates are resolved in this order:

1. **Explicit path**: `--templates-dir <path>` flag
2. **Sibling templates/**: `./templates/` relative to the Harness repo root
3. **Installed skill location**: `skills/harness/subskills/init/../../../../templates/` (walk up to Harness root)
4. **Fail**: print error with expected paths

If a template file is missing, skip it silently and print a note. Missing templates should not block initialization.

## File generation details

### CONTEXT.md skeleton

```md
# {Project Name}

{TODO: One or two sentence description}

## Language

{TODO: Define domain terms here}

## Relationships

{TODO: Define term relationships}

## Example dialogue

{TODO: Write a dialogue demonstrating term usage}

## Flagged ambiguities

{TODO: Flag resolved ambiguities}
```

### UBIQUITOUS_LANGUAGE.md skeleton

```md
# Ubiquitous Language

{TODO: Map domain terms to code locations}

<!-- Format:
**Term** (DDD Type) → `path/to/file.ext::SymbolName`
-->
```

### .harness/config.yaml skeleton

```yaml
project: {project-name}
version: "3.0"
risk_policy: ./BLAST_RADIUS_POLICY.md
skills:
  subskills:
    - harness-domain-language
    - harness-architecture-review
    - harness-tdd
    - harness-specify
    - harness-plan
    - harness-tasks
    - harness-eval
    - harness-report
    - harness-risk
    - harness-context
    - harness-grill
    - harness-init
templates_dir: ./templates
```

### Makefile

Copy from `templates/Makefile`. If the project already has a Makefile, warn and skip. The user should merge the Harness targets into their existing Makefile.

Key targets the Makefile must provide:

- `make init` — re-run initialization (idempotent)
- `make verify` — run all gates (lint, typecheck, tests)
- `make verify-ai` — run AI-specific compliance checks (spec coverage, CONTEXT.md freshness)
- `make spec-init FEATURE=NNN-name` — scaffold a new feature spec directory

## Post-init workflow

After initialization, guide the user through:

1. **Domain language session**: Use `harness-domain-language` to populate `CONTEXT.md` with the project's first domain terms.

2. **First spec**: Create `specs/001-{feature}/spec.md` using `harness-specify`. This exercises the full PRD → SPEC → PLAN → TASKS pipeline.

3. **Verify setup**: Run `make verify` to confirm the Makefile targets work.

4. **Install skills**: Ensure the agent can discover and invoke Harness skills. This typically means updating `CLAUDE.md` or `.claude-plugin/plugin.json` with skill references.

## Edge cases

### Existing codebase

When adopting Harness on an existing project:

- **Never overwrite**: existing `CONTEXT.md`, `CLAUDE.md`, `AGENTS.md`, `Makefile`
- **Merge guidance**: print the diff the user would need to apply manually
- **Adopt incrementally**: suggest starting with `CONTEXT.md` + `docs/adr/` first, then adding spec governance later

### Monorepo

For monorepos with multiple services:

- Create `CONTEXT-MAP.md` at root instead of a single `CONTEXT.md`
- Each service gets its own `CONTEXT.md` and `docs/adr/`
- The root `Makefile` should delegate to service-level Makefiles

### Missing tools

If `make` is not available, print a warning with manual instructions for each step. The Makefile is a convenience, not a requirement.
