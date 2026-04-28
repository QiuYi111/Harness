---
name: harness-architecture-review
description: "Find architecture improvement opportunities: shallow modules, deep module candidates, DDD dependency violations, testability gaps. Use periodically to prevent AI-accelerated code rot. Triggers: 'codebase feels complex', 'untestable', 'hard to navigate', 'architecture review'."
---

# Harness Architecture Review

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability, AI-navigability, and DDD compliance.

## Glossary

Use these terms exactly in every suggestion. Consistent language is the point — don't drift into "component," "service," "API," or "boundary." Full definitions in [LANGUAGE.md](./LANGUAGE.md).

- **Module** — anything with an interface and an implementation (function, class, package, slice).
- **Interface** — everything a caller must know to use the module.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place.
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key principles (see [LANGUAGE.md](./LANGUAGE.md)):

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is **informed** by the project's domain model. The domain language gives names to good seams; ADRs record decisions the skill should not re-litigate.

## Process

### 1. Explore

Before exploring, read `CONTEXT.md` and relevant ADRs following the consumer contract in [../../references/DOMAIN-AWARENESS.md](../../references/DOMAIN-AWARENESS.md).

Walk the codebase organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where do tightly-coupled modules leak across their seams?
- **DDD violations**: infrastructure importing from `cmd/`, domain depending on external packages, application layer reaching past ports.
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything suspect. A "yes, concentrates complexity" is the signal you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve

**Use `CONTEXT.md` vocabulary for the domain, and [LANGUAGE.md](./LANGUAGE.md) vocabulary for the architecture.**

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting. Mark it clearly (e.g. _"contradicts ADR-0007 — but worth reopening because…"_).

Do NOT propose interfaces yet. Ask: "Which of these would you like to explore?"

### 3. Grilling loop

Once you pick a candidate, drop into a grilling conversation. Walk the design tree — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term — same discipline as `harness-domain-language` (see [../domain-language/CONTEXT_FORMAT.md](../domain-language/CONTEXT_FORMAT.md)). Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term?** Update `CONTEXT.md` right there.
- **User rejects with a load-bearing reason?** Offer an ADR: _"Want me to record this so future reviews don't re-suggest it?"_ (see [../domain-language/ADR_FORMAT.md](../domain-language/ADR_FORMAT.md)).

Use the deepening methodology in [DEEPENING_GUIDE.md](./DEEPENING_GUIDE.md) when designing the refactored module's dependency strategy.
