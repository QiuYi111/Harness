---
name: harness-specify
description: Create a feature specification with user stories, functional requirements, Given/When/Then acceptance scenarios, success criteria, assumptions, and explicit out-of-scope boundaries. Use when user wants to define a feature, convert an idea into a spec, write a PRD, or start a new implementation workflow.
---

# harness-specify

Convert a feature idea into a structured specification. Produces `specs/<feature-id>/spec.md` and optionally `docs/prd/<feature-id>.md`.

## When to Use

- User describes a feature idea and wants to formalize it
- User says "spec this", "write a spec", "define this feature", "create a PRD"
- Starting a new implementation workflow that needs a specification first

## Before Starting

1. Read `../../references/DOMAIN-AWARENESS.md` for project-specific terminology and constraints.
2. Check if the feature already has a spec in `specs/`. If yes, ask whether to update or create new.

## Steps

1. **Gather context**: Ask the user for the feature name, target users, and core behavior. If the user provides a PRD or loose description, extract the key elements.

2. **Determine feature ID**: Use the existing naming convention in `specs/` (e.g., `001-feature-name`). If no convention exists, ask the user.

3. **Create spec**: Use `SPEC_FORMAT.md` as the template. Fill every section:
   - User scenarios with Given/When/Then acceptance scenarios
   - Functional requirements (each testable)
   - Non-functional requirements with measurable targets
   - Success criteria tied to scenarios
   - Explicit assumptions
   - Mark unresolved items as `[NEEDS CLARIFICATION]`
   - Explicit out-of-scope list (mandatory)

4. **Optional PRD**: If the user requests a PRD or the feature is large enough to warrant one, create `docs/prd/<feature-id>.md` using `PRD_FORMAT.md`.

5. **Validate**: Confirm the spec has at least one user scenario, success criteria, and an out-of-scope section.

## Rules

- Never guess values marked `[NEEDS CLARIFICATION]` — ask the user.
- Every P1 user scenario must have independent test instructions.
- Out-of-scope is mandatory, not optional.
- Write the Summary paragraph last, after all sections are complete.

## Reference Files

- `SPEC_FORMAT.md` — Full spec template with section descriptions
- `PRD_FORMAT.md` — Full PRD template for product-level documents
