---
name: harness-eval
description: >
  Evaluate whether an implementation satisfies the spec (Product Eval) and whether the agent
  followed Harness process gates (Harness Eval). Use before merge, after implementation, or
  when asked to "eval", "evaluate", "check compliance", "verify against spec", "did we follow
  process", "is this ready to merge", "run eval", "product eval", "harness eval".
---

# harness-eval

Two-part evaluation: **Product Eval** (does the code match the spec?) and **Harness Eval** (did the agent follow the process?).

## When to activate

- Before merging a feature branch
- After implementation completes
- When someone asks "is this correct?" or "did we follow the process?"
- Before running `harness-report`

## Prerequisites

- A spec file (`specs/*/spec.md`) must exist for Product Eval
- Implementation code must be present
- Read `../../references/DOMAIN-AWARENESS.md` for terminology

## Steps

### 1. Product Eval

Run tests and check acceptance criteria:

- Read the spec's acceptance scenarios → verify each one passes
- Read the spec's functional requirements → verify implementation matches
- Check edge cases and error handling from the spec
- Run non-functional checks (performance, security, observability) if spec defines them
- Run `make verify` — must pass

### 2. Harness Eval

Check process compliance:

- Did a spec exist before implementation started?
- Did a plan exist and was it followed?
- Were tasks generated from the plan?
- Was blast radius classified? (leaf / branch / core / infra)
- Were tests written during RED and not modified during GREEN?
- Was a review produced?
- Did `make verify` pass?
- Did `make verify-ai` pass?

Call `harness eval` for deterministic gate checks if available.

### 3. Write eval.md

Follow the format in [EVAL_FORMAT.md](./EVAL_FORMAT.md).

Every pass/fail entry needs evidence. See [EVIDENCE_GUIDE.md](./EVIDENCE_GUIDE.md) for what counts.

### 4. Verdict

- **Ready to merge** — all Product Eval criteria pass, all required Harness gates pass for the blast radius level
- **Needs changes** — any criterion fails. List what must change.

Gate strictness scales with blast radius:
- **leaf**: lint, unit_test
- **branch**: spec, plan, tests, review_agent
- **core**: + human_spec_review, architecture_review, rollback_plan, security_review
- **infra**: + dry_run, human_approval, rollback_plan, security_review

## Output

Write `specs/<feature>/eval.md` using the format in [EVAL_FORMAT.md](./EVAL_FORMAT.md).

## Reference

- [EVAL_FORMAT.md](./EVAL_FORMAT.md) — output template with tables and checklists
- [EVIDENCE_GUIDE.md](./EVIDENCE_GUIDE.md) — what counts as valid evidence for each criterion
- `../../references/DOMAIN-AWARENESS.md` — domain terminology and risk vocabulary
