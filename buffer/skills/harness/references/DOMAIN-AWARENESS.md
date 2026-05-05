# Domain Awareness

Consumer rules for any Harness skill that explores a codebase. Producer rules (writing `CONTEXT.md`, offering ADRs) live in `harness-domain-language/SKILL.md`.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per bounded context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The producer skill (`harness-domain-language`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (most repos):

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (presence of `CONTEXT-MAP.md` at the root):

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in a spec, a task description, a test name, an issue title), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `harness-domain-language`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_

## Harness-specific: UBIQUITOUS_LANGUAGE.md

In addition to `CONTEXT.md`, Harness projects may have a `UBIQUITOUS_LANGUAGE.md` that maps DDD terms to their code representations. If it exists, read it before acting on any domain-related task.

## Harness-specific: Risk-aware terminology

When the skill touches risk classification (harness-risk, harness-plan, harness-tasks), use the four blast-radius terms consistently:

- **leaf** — isolated, low-dependency changes (not "minor" or "trivial")
- **branch** — feature-level, multi-file behavior change (not "medium" or "normal")
- **core** — domain, auth, storage, permissions, protocol (not "critical" or "high-risk")
- **infra** — deployment, CI/CD, secrets, migrations (not "infrastructure" or "ops")
