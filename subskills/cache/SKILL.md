---
name: harness-cache
description: >
  Optimize agent context for cache-friendly assembly. Standardizes prompt prefix
  ordering (stable → semi-stable → active → dynamic), generates cache geometry
  configuration, and produces cache-aware context bundles. Use when context is
  too large, agent is repeatedly reading same files, user asks about cache/cost/
  token reduction, or before implementation to minimize context pollution.
  Triggers: "cache context", "optimize context", "reduce tokens", "context too
  large", "cache-friendly", "prompt cache", "token optimization", "context order".
---

# harness-cache

Optimize agent context for prompt cache efficiency. Standardizes prefix ordering
so stable content is reused across API calls and dynamic content stays at the end.

## When to activate

- Before implementation when context is large or the agent will make many API calls
- Agent is repeatedly reading the same stable files (skills, policies, AGENTS.md)
- User mentions cache, cost, tokens, or context optimization
- `harness context --cache-aware` should be used instead of plain `harness context`
- Entry skill routes here when phase is "Cache/Context"

## Prerequisites

- `../../references/DOMAIN-AWARENESS.md` for terminology
- [CACHE_GUIDE.md](../../references/CACHE_GUIDE.md) for the full cache strategy

## Principles

1. **Stable first, dynamic last.** Content that never changes (skill instructions,
   policies) goes at the top. Content that changes every call (diffs, logs, user
   request) goes at the bottom. This maximizes prefix cache reuse.

2. **Append, do not rewrite.** Add ADRs and log lines by appending. Never rewrite
   stable policy files unless the policy itself changes.

3. **Sort everything.** File lists within each layer are sorted lexicographically.
   Same feature must produce the same prompt shape every time.

4. **Separate protocol from evidence.** Protocol files (CACHE.md, policies) are
   stable and go in the prefix. Evidence files (eval reports, diffs) are dynamic.

5. **Layer boundaries are explicit.** Each of the four layers (stable prefix,
   semi-stable context, active feature context, dynamic suffix) has a clear
   delimiter in the assembled context so agents can reason about what changed.

## Steps

### 1. Check for CACHE.md

If `CACHE.md` does not exist at the project root, generate it from
`resources/templates/CACHE.md`. This declares the context ordering protocol.

### 2. Check for cache-context.yaml

If `.harness/policies/cache-context.yaml` does not exist, generate it from
`resources/policies/cache-context.yaml`. This defines the four-layer cache
geometry and the ignore list.

### 3. Run cache-aware context assembly

```bash
harness context <feature-id> --cache-aware --write
```

Reads `CACHE.md` and `cache-context.yaml`, assembles context in stable-to-dynamic
order, includes content hashes per layer, and writes to `specs/<feature>/context.md`.

### 4. Optionally run cache report

```bash
harness cache-report
```

Outputs token estimates per layer and cache hit ratio if API metrics are
available. See [CACHE_METRICS.md](./CACHE_METRICS.md) for interpretation.

## Reference

- [CACHE_GUIDE.md](../../references/CACHE_GUIDE.md) -- detailed cache strategy and the four layers
- [CACHE_METRICS.md](./CACHE_METRICS.md) -- metrics collection and provider notes
- `../domain-language/DOMAIN-AWARENESS.md` -- domain terminology
