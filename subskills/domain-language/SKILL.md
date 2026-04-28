---
name: harness-domain-language
description: Extract or maintain a DDD-style ubiquitous language for the project. Identifies ambiguous terms, resolves synonyms, establishes canonical terminology, and writes CONTEXT.md, UBIQUITOUS_LANGUAGE.md, and ADR records. Use when starting a new project, onboarding agents, or when agents use inconsistent terminology.
disable-model-invocation: true
---

# Harness Domain Language

Extract, sharpen, and maintain the project's ubiquitous language. This is a **relentless interview session** — one question at a time, waiting for your answer before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Domain awareness

Before acting, follow the consumer contract in [DOMAIN-AWARENESS.md](../../references/DOMAIN-AWARENESS.md) — read existing `CONTEXT.md`, `CONTEXT-MAP.md`, `UBIQUITOUS_LANGUAGE.md`, and relevant ADRs.

If none of these exist, proceed silently. Create files lazily when terms or decisions are actually resolved.

### File structure

Most repos have a single context: `CONTEXT.md` at root, `docs/adr/` for decisions.

If `CONTEXT-MAP.md` exists at root, the repo has multiple bounded contexts — each with its own `CONTEXT.md` and `docs/adr/`. Infer which context the current topic relates to.

## During the session

### Challenge against the glossary

When you use a term that conflicts with `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When you use vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force you to be precise about the boundaries between concepts.

### Cross-reference with code

When you state how something works, check whether the code agrees. Surface contradictions: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch — capture as they happen. Use the format in [CONTEXT_FORMAT.md](./CONTEXT_FORMAT.md).

Don't couple `CONTEXT.md` to implementation details. Only include terms meaningful to domain experts.

### Write UBIQUITOUS_LANGUAGE.md

When the session resolves DDD term-to-code mappings (aggregate root → struct, domain event → interface, value object → type), write them to `UBIQUITOUS_LANGUAGE.md` at the repo root. Format:

```md
# Ubiquitous Language

**Order** (Aggregate Root) → `src/ordering/domain/order.rs::Order`
**Money** (Value Object) → `src/shared/domain/types.rs::Money`
**OrderPlaced** (Domain Event) → `src/ordering/domain/events.rs::OrderPlaced`
```

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one

If any of the three is missing, skip the ADR. Use the format in [ADR_FORMAT.md](./ADR_FORMAT.md).

### Flag Harness risk terms

When the session touches risk classification, enforce the four blast-radius terms: **leaf**, **branch**, **core**, **infra**. Reject synonyms ("minor", "medium", "critical", "ops").
