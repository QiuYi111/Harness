---
name: harness-context
description: >
  Create a minimal context bundle for a feature so coding agents read only the relevant spec,
  plan, tasks, policies, project language, ADRs, and forbidden context list. Use before
  implementation or review to reduce agent context pollution. Triggers: "context bundle",
  "what should I read", "prepare context", "agent context", "context for agent",
  "zoom out", "what's relevant", "narrow context", "context window".
---

# harness-context

Generates a `context.md` that tells agents exactly what to read and what to ignore for a specific feature.

## When to activate

- Before starting implementation (most common)
- Before code review
- When an agent is loading too much or too little context
- When someone asks "what should I read?" or "zoom out on this area"

## Prerequisites

- A feature spec exists at `specs/*/spec.md`
- Read `../../references/DOMAIN-AWARENESS.md` for terminology

## Steps

### 1. Identify the feature

Determine which feature area from `specs/` is the target. If ambiguous, ask.

### 2. Build Must Read list

Scan the repo and collect:

- **Spec**: `specs/<feature>/spec.md`
- **Plan**: `specs/<feature>/plan.md` (if exists)
- **Tasks**: `specs/<feature>/tasks.md` (if exists)
- **Policies**: `ROLE_POLICY.md`, `BLAST_RADIUS_POLICY.md` (if they exist)
- **Language docs**: `CONTEXT.md` or `CONTEXT-MAP.md` at repo root
- **ADRs**: `docs/adr/` entries touching the feature area
- **Domain language**: `UBIQUITOUS_LANGUAGE.md` if present

### 3. Build Forbidden Context list

Identify files the agent should NOT read:

- Unrelated specs from other features
- Old reports and evals from previous iterations
- Large raw data files (fixtures, dumps, exports)
- Generated files (build output, coverage reports)
- Any file >500 lines that isn't directly relevant

### 4. Generate agent-specific files (optional)

If the agent needs a routing layer, generate snippets from [AGENT_FILE_TEMPLATES.md](./AGENT_FILE_TEMPLATES.md):

- `CLAUDE.md` snippet for Claude Code
- `AGENTS.md` snippet for cross-agent standard
- Zoom-out context section for unfamiliar code areas

### 5. Write context.md

Follow the format in [CONTEXT_GUIDE.md](./CONTEXT_GUIDE.md).

## Zoom-out mode

When asked to "zoom out" on an unfamiliar area: provide a high-level map of the system, how the target area fits in, what depends on it, and what it depends on. Include this as a section in `context.md`.

## Output

Write `specs/<feature>/context.md` using the format in [CONTEXT_GUIDE.md](./CONTEXT_GUIDE.md).

## Reference

- [CONTEXT_GUIDE.md](./CONTEXT_GUIDE.md) — output format and structure
- [AGENT_FILE_TEMPLATES.md](./AGENT_FILE_TEMPLATES.md) — templates for CLAUDE.md / AGENTS.md snippets
- `../../references/DOMAIN-AWARENESS.md` — domain terminology and risk vocabulary
