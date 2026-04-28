# Context Guide

Format for `specs/<feature>/context.md`. This file tells agents what to load and what to skip.

## Structure

```markdown
# Context: <feature-name>

## Feature

- **Spec**: <path>
- **Plan**: <path> (if exists)
- **Tasks**: <path> (if exists)
- **Blast radius**: leaf / branch / core / infra

## Must Read

Files the agent MUST read before starting work:

- <path> — <reason>
- <path> — <reason>
...

## Read If Relevant

Files to read only if the work touches these areas:

- <path> — <trigger condition>
...

## Forbidden Context

Files the agent MUST NOT read (context pollution):

- <path> — <reason>
...

## ADRs

Architecture decisions relevant to this feature:

- <adr-path> — <summary>
...

## Domain Language

Key terms from CONTEXT.md / UBIQUITOUS_LANGUAGE.md:

| Term | Definition | Code Location |
|------|-----------|---------------|
| <term> | <definition> | <file:line> |

## Zoom-Out

_Broad context on how this feature fits in the system (optional)._

<system-map>

## Agent Routing

Snippets to paste into agent config files. See AGENT_FILE_TEMPLATES.md for full templates.
```

## Rules

1. **Must Read** should be ≤10 files. If more, narrow the scope.
2. **Forbidden Context** must include a reason for each entry.
3. **ADRs** should only include decisions that directly affect this feature.
4. **Domain Language** should only include terms used in the spec.
5. **Zoom-Out** is optional. Include when the feature spans multiple modules or when the implementer is unfamiliar with the codebase.
6. Paths must be relative to repo root.
7. Regenerate if the spec or plan changes significantly.
