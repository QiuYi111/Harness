---
name: harness-grill-product
description: >
  High-level product definition and UX discovery skill. Runs seven gates to determine
  whether a product is worth building, who it's for, what experience should exist, what
  the MVP boundary is, and what UI/UX direction should guide implementation.
  Produces .pm/stable/ files and initializes .pm/runtime/state.yaml.
  Use when: product idea, "worth building", "product definition", "define this product",
  user journey, UX principles, UI direction, MVP boundary.
---

# harness-grill-product

Seven-gate product discovery. Each gate must pass before the next begins. The goal is to freeze a product contract that Supervisor can use to drive delivery.

## Before Starting

1. Check for existing `.pm/stable/` files. If they exist, ask whether to update or start fresh.
2. If `.pm/` directory does not exist, create it with subdirectories `stable/`, `runtime/`, `design/`, `design/generated-concepts/`.
3. Read any existing README, product notes, or design references the user provides.
4. **Assess product maturity**: ask the user which stage applies:
   - **Pre-product** (idea only): Run all 7 gates. This is the default.
   - **Has users** (launched, has real users): Skip Gate 1 demand validation. Focus on Gate 4-6 for next iteration.
   - **Has paying customers**: Skip Gates 1-2. Focus on Gate 4 (MVP wedge for next version) and Gate 5-6.
   - **Hackathon/learning project**: Switch to Builder mode (see below).

## Mode Selection

At the start, ask the user:

> **"What kind of project is this?"**
>
> **A) Startup** — I want to build something people will use or pay for. Scrutinize the idea hard.
> **B) Builder** — I'm building to learn, experiment, or for fun. Help me think bigger, but keep it fun.

**Startup mode** (default): Runs all applicable gates with full diagnostic pressure. Push back on weak evidence. Be the critical investor.

**Builder mode**: Replace Gates 1-2 with generative questions:
- "What's the coolest version of this you can imagine?"
- "What would make someone say 'whoa' when they see this?"
- "If you had no constraints, what would this become?"
Keep Gates 3-7 for structural discipline (you still need to know who it's for and what it looks like).

## Gates

| Gate | Goal | Output |
|------|------|--------|
| 1. Demand Reality | Determine if the idea corresponds to real demand | `evidence.md`, `product.md` sections |
| 2. Product Reframe | Find the 10x version hiding behind the obvious request | `product.md`, `value-proposition.md`, `decisions.md` |
| 3. User & Scenario Specificity | Define first users and core scenario with desperate specificity | `product.md` sections, `user-journeys.md` |
| 4. MVP Wedge | Define the smallest useful product slice | `product.md` MVP boundary, `roadmap.md`, `active-stage.md` |
| 5. UX Journey | Define user experience before code | `user-journeys.md`, `ux-principles.md` |
| 6. UI Direction & Design Probe | Define visual and interaction taste before implementation | `ui-direction.md`, `ui-feedback.md` |
| 7. Product Contract Freeze | Freeze enough product definition for Supervisor to enter delivery loop | `state.yaml`, runtime files, all stable files validated |

See `references/gate-questions.md` for full question lists, recommended answers, outputs, and pass conditions for each gate.

## Reference Files

- `references/gate-questions.md` — Full question lists, outputs, and pass conditions for all 7 gates
- `references/pushback-patterns.md` — Anti-sycophancy rules, pushback patterns, graduated escape hatch, gate execution rules
- `references/cognitive-principles.md` — Inversion Reflex, Focus as Subtraction, Proxy Skepticism, Temporal Depth, Subtraction Default
- `references/design-probe.md` — Design probe steps, coherence validation, subtraction check, block rule
- Templates: `references/templates/pm/` — all .pm file templates
- Existing grill: `subskills/grill/QUESTION_TREE.md` — technical question tree (separate from this product grill)
- `../../references/DOMAIN-AWARENESS.md` — project terminology
