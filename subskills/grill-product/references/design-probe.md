# Design Probe Reference

Used during Gate 6 when user taste is unclear. Extracted from Gate 6 UI Direction.

## Design Probe (if taste is unclear)

If the user cannot articulate taste verbally:

**Step 1: Concept confirmation.** Present 3 one-line concept descriptions:
> "A) Editorial calm — generous whitespace, serif headings, restrained palette."
> "B) Industrial utility — dense data, monospace elements, function-first."
> "C) Playful energy — rounded shapes, bright accents, bouncy interactions."

Get user to pick or blend before generating full descriptions.

**Step 2: Generate detailed variants.** Each variant must include:
- Specific font names (not "sans-serif")
- 3-4 hex colors
- Layout description with content hierarchy
- 2-3 specific interaction patterns
- One anti-pattern it deliberately avoids

**Step 3: Present comparison and collect feedback.** Record in `.pm/design/ui-feedback.md`.

**Step 4: Iteration.** If the user rejects all 3, generate 3 new ones incorporating their feedback. Maximum 2 regeneration rounds. If still no match after 2 rounds, escalate:
> "I'm not finding the right direction. Can you share a screenshot of a product whose visual feel you like?"

**Step 5: Taste memory.** Before generating variants, read any existing `.pm/stable/ui-direction.md` and `.pm/design/ui-feedback.md` from prior sessions. Bias variants toward the user's demonstrated aesthetic preferences.

## Coherence Validation Checklist

After all Gate 6 questions are answered, check:

- Does the aesthetic match the motion? (e.g., Brutalist + bouncy animation = mismatch)
- Does the density match the typography? (e.g., Dense + thin serif = hard to read)
- Does the color approach match the product type? (e.g., Playful + corporate blue = mismatch)
- Does the interaction style match the target user? (e.g., CLI-style for non-technical users = mismatch)

If any mismatches found, flag them and ask the user to resolve.

## Subtraction Check

For every UI element described in Gate 6, ask:
> "Does this earn its pixels? If unsure, cut it."

Feature bloat kills products faster than missing features. When in doubt, subtract.

## Block Rule

If `Open taste questions` remain unresolved in `ui-direction.md`, mark `ui_direction_ready: false`. Supervisor must NOT delegate UI implementation.
