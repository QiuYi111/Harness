# Cache Engineering Guide

## Why Cache Engineering Matters

- **Token savings.** LLM providers charge less for cached prefix tokens. A
well-ordered prompt can reduce repeated-prefix cost in multi-turn sessions
when provider prompt caching is active. Exact savings depend on cache
semantics and prompt assembly.
  implementation sessions.
- **Reduced exploration.** When the agent's context starts with stable protocol
  files (policies, skill instructions, domain language), it spends fewer tokens
  re-reading files it already saw in previous turns.
- **Lower misread risk.** Stable content at the top is less likely to be
  truncated or lost when context windows fill up during long sessions.
- **Deterministic assembly.** Same feature, same prompt shape, every time. This
  makes debugging easier and behavior more predictable.

## The Four Layers

Context is divided into four layers, ordered from most stable to most dynamic.

### 1. Stable Prefix

Content that almost never changes during a feature lifecycle.

- Harness skill instructions (SKILL.md files for active skills)
- AGENTS.md
- CACHE.md (this file, declaring the ordering protocol)
- Policy files: blast-radius.yaml, roles.yaml, cache-context.yaml
- Domain language files: CONTEXT.md, UBIQUITOUS_LANGUAGE.md

These files form the reusable cache prefix. They should be written once and
rarely modified.

### 2. Semi-Stable Context

Content that changes occasionally (between features or milestones).

- project_index/repo.md and module docs
- Architecture documentation (ARCHITECTURE.md)
- ADR records in docs/adr/
- Cross-cutting design decisions

These change when the project structure evolves, not every turn.

### 3. Active Feature Context

Content tied to the current feature being implemented.

- specs/<feature>/spec.md
- specs/<feature>/plan.md
- specs/<feature>/tasks.md
- Feature-specific context.md

This layer changes when switching between features but stays stable within a
single feature's implementation session.

### 4. Dynamic Suffix

Content that changes every API call.

- Current user request or instruction
- Git diff (staged or recent changes)
- Test output and error messages
- Agent-generated intermediate artifacts

This layer must be last. Anything here invalidates cache for all content after
it, so only truly per-turn content belongs here.

## Five Principles

### Stable first, dynamic last

Arrange context so that content which is identical across API calls occupies
the longest possible prefix. This is the single most impactful optimization.
Even without provider-level cache metrics, a stable prefix reduces the tokens
the agent needs to re-read each turn.

### Append, do not rewrite

When adding new information (a new ADR, a new context entry, a new log line),
append to the relevant file or section. Rewriting a stable file shifts every
byte that follows it in the prompt, invalidating cache for the entire suffix.

### Sort everything

File lists, section headings, and entry ordering should be deterministic.
Lexicographic sort is the default. This ensures the same feature always
produces the same prompt structure, which is required for consistent cache hits.

### Separate protocol from evidence

Protocol files (how the project works, what the rules are) are stable.
Evidence files (what happened, what the test output was) are dynamic. Keep
them in separate layers so evidence changes do not invalidate protocol cache.

### Layer boundaries are explicit

In the assembled context, each layer starts with a clear section marker. This
allows both agents and tooling to identify what changed between calls without
re-reading the entire context.

## cache-context.yaml Format

The `cache-context.yaml` file (installed to `.harness/policies/`) defines the
machine-parseable cache geometry:

- **stable_prefix**: list of file globs for the stable layer
- **semi_stable_context**: list of file globs for the semi-stable layer
- **active_feature_context**: template patterns with `{feature}` placeholder
- **dynamic_suffix**: reserved tokens for per-turn content
- **ignore**: glob patterns for files to exclude from context assembly

The CLI reads this file to determine ordering. Agents should not parse it
directly -- use `harness context --cache-aware` instead.

## CACHE.md Protocol

`CACHE.md` at the project root is the human-readable declaration of context
ordering rules. It serves as the contract between agents and the project:

- It tells agents what order to read files in
- It declares which files are stable and which are dynamic
- It lists the ignore rules for generated and build artifacts

All agents working in the repository should read CACHE.md and follow its
ordering. The CLI enforces this ordering when `--cache-aware` is used.

## Integration

- **harness-context** uses cache-aware ordering when `--cache-aware` is passed.
  Without the flag, it assembles context without layer separation.
- **harness-init** copies CACHE.md and cache-context.yaml into new projects
  during initialization.
- **harness (entry skill)** routes to harness-cache when the detected phase
  is "Cache/Context" or when the user mentions token/cost optimization.
