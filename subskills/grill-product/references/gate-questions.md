# Gate Questions Reference

Full question lists, recommended answers, outputs, and pass conditions for all 7 gates.

---

## Gate 1: Demand Reality

**Goal**: Determine whether the idea corresponds to real demand.

**Methodology**: Inspired by The Mom Test and gstack /office-hours. Ask about past behavior, not hypothetical praise. Surveys lie. Demos are theater.

**Skip condition**: If product already has paying customers, skip to Gate 4.

### Questions (ask one at a time)

1. **Who specifically has this problem?**
   - Recommended: Name a specific role, context, and situation. "A solo founder managing 5+ projects who loses context between sessions" is good. "Developers" is not.
   - Push further: "What gets this person promoted? What gets them fired? What keeps them up at night?"

2. **What are they doing today instead?**
   - Recommended: Name the specific tool, spreadsheet, workflow, or hack. If they can't name one, the problem may not be real.

3. **When was the last concrete occurrence?**
   - Recommended: "Yesterday when I had to re-read 3 chat sessions to remember what I was building." Not "it happens all the time."

4. **What did the user lose?**
   - Recommended: Be specific — time (how much?), money (how much?), attention, status, emotional energy, a deadline.

5. **What makes existing alternatives insufficient?**
   - Recommended: Identify the specific gap. "Notion is too flexible" or "Jira is too heavy for solo use."

6. **What is the strongest evidence that someone actually wants this — not 'is interested', not 'signed up for a waitlist', but would be genuinely upset if it disappeared tomorrow?**
   - Recommended: External signals — complaints online, forum threads, people already building workarounds, paying for inferior solutions.
   - Red flags that are NOT evidence: "People say it's interesting," "We got waitlist signups," "Investors are excited about the space."

7. **Have you watched a real person struggle with this problem? What did they do that surprised you?**
   - Recommended: Observation beats surveys and interviews. "Users did X when we expected Y" is gold.
   - Red flags: "We sent a survey," "We did demo calls," "Nothing surprising, went as expected." If nothing surprised you, you weren't really looking.

### Outputs

- `.pm/stable/evidence.md`
- Relevant sections in `.pm/stable/product.md`

### Pass condition

- Target user is specific (role + context + incentive structure).
- Existing alternative is named.
- Pain or desire is concrete (not abstract).
- A narrow wedge can be identified.
- At least one signal of real demand (not just interest).

### If not passed

- Mark `evidence_ready: false` in `state.yaml`.
- Use graduated escape hatch. If user waives, set `evidence_ready: true` with status `waived_by_user` in evidence.md and record in decisions.md.

---

## Gate 2: Product Reframe

**Goal**: Avoid implementing the literal feature request when a better product framing exists.

**Methodology**: Inspired by gstack /plan-ceo-review and Jobs To Be Done. Look for the 10x version hiding behind the obvious request.

**Skip condition**: Builder mode skips this gate. Startup mode with paying customers can skip if the reframe already happened.

### Ambition Check

Before the questions, ask:

> **"How ambitious should we be here?"**
>
> **A) Dream big** — find the cathedral. What's the 10x version?
> **B) Stay focused** — make the current scope bulletproof.
> **C) Cut to the bone** — find the minimum viable version.

This sets the lens for all reframe questions.

### Questions (ask one at a time)

1. **Is the requested product actually a proxy for a deeper user job?**
   - Recommended: "I want a kanban board" might mean "I want to stop losing track of what matters across projects." Look for the struggling moment.
   - If YOU can see the deeper job, name it directly: "You're asking for [X]. I think the deeper need is [Y] because [reason]."

2. **What is the 10x version hidden behind the obvious request?**
   - Recommended: Don't just build the thing they described. Ask: what if the product made the problem disappear entirely?
   - Bonus push: "What if the user didn't have to do anything at all to get value? No login, no setup, no integration. What would that look like?"

3. **What would make users say "this is exactly what I needed"?**
   - Recommended: Focus on the specific moment of delight, not the feature list.

4. **What should NOT be built even if technically easy?**
   - Recommended: List the tempting but distracting features. Every "yes" to these is a "no" to the core product.

5. **Does this product become more essential or less if the world changes in 3 years? Why specifically?**
   - Recommended: Not "the market is growing" — that's not a thesis. What specific change makes this MORE needed?
   - Red flag: "AI will make everything better" is not a product thesis.

### Outputs

- `.pm/stable/product.md` (Problem, Jobs to be done, Core use cases, Non-goals, Anti-goals)
- `.pm/stable/value-proposition.md`
- `.pm/decisions.md` (record reframing decisions)

---

## Gate 3: User and Scenario Specificity

**Goal**: Define first users and core scenario with desperate specificity.

**Methodology**: Inspired by gstack /office-hours "narrowest wedge" and "desperate specificity" forcing questions.

### Questions (ask one at a time)

1. **Who is the first narrow user segment?**
   - Recommended: "Solo founders managing 3+ AI-assisted projects" not "developers."
   - Push further: "What gets this person promoted? What gets them fired? What keeps them up at night?"

2. **Who is explicitly NOT the first user?**
   - Recommended: "Enterprise teams," "non-technical users," "open-source maintainers." Be explicit about who you're ignoring.

3. **What is the first core use case?**
   - Recommended: One sentence. "Resume work on a project I haven't touched in 2 weeks without losing context."

4. **What is the user's context before opening the product?**
   - Recommended: Where are they? What were they just doing? What's on their mind?

5. **What does success look like after using the product?**
   - Recommended: Observable outcome. "I completed one task and knew what to do next."

### Outputs

- `.pm/stable/product.md` (Target users, Core use cases)
- `.pm/stable/user-journeys.md` (Primary journey)

---

## Gate 4: MVP Wedge

**Goal**: Define the smallest useful product slice.

**Methodology**: Inspired by gstack /office-hours "narrowest wedge" and /plan-ceo-review scope discipline.

### Questions (ask one at a time)

1. **What is the smallest experience that proves the product direction?**
   - Recommended: Not the full product. The smallest thing that makes one user say "yes, this."

2. **What can be cut from the first version?**
   - Recommended: List everything that's tempting but not essential for the first proof.

3. **What must exist for the product to feel real?**
   - Recommended: The minimum without which it's a toy, not a product.

4. **Is the first version a demo, dogfood tool, beta, or production release?**
   - Recommended: Be honest about the target. Dogfood tool has different bar than production.

### Outputs

- `.pm/stable/product.md` (MVP boundary with Included/Excluded)
- `.pm/stable/roadmap.md` (Stage 0 and Stage 1 defined at minimum)
- `.pm/runtime/active-stage.md`

---

## Gate 5: UX Journey

**Goal**: Define user experience before code.

**Methodology**: Inspired by Don't Make Me Think (Krug), Design Sprint, and gstack /plan-design-review. Define first-screen clarity, obvious next action, all interaction states, and the emotional arc.

### Questions (ask one at a time)

1. **What is the first thing the user sees?**
   - Recommended: Not a logo or landing page. The first useful thing.

2. **What is the first user action?**
   - Recommended: One clear action. If there are multiple, the design is wrong.

3. **Where is the aha moment?**
   - Recommended: The specific instant where the user's mental model shifts from "what is this?" to "oh, this is exactly what I needed."

4. **Map the emotional arc: Before opening → First screen → Aha moment → After. What does the user feel at each stage?**
   - Recommended: Every moment is a scene with a mood, not just a screen with a layout. The arc must be intentional.

5. **What are loading, empty, error, and success states?**
   - Recommended: Each state must have: (1) what the user sees, (2) what the user can do next, (3) how it makes them feel. "Loading..." is not a design. "No items found." is not a design. Every empty state needs warmth, a primary action, and context.

6. **What does the user feel in the first 5 seconds (gut reaction)? After 5 minutes (does it feel natural)? After 5 months (does it feel trustworthy)?**
   - Recommended: Visceral (first 5 sec) → Behavioral (5 min) → Reflective (5 months). Each level needs intentional design.

7. **Where might the user get confused?**
   - Recommended: List every point where the user might think "wait, what?" and how to prevent it.

8. **How does the product recover from confusion?**
   - Recommended: Error recovery is not "show a message." It's "guide the user back to the happy path."

9. **What does the mobile experience look like? Not "stacked desktop" — what specifically changes and why?**
   - Recommended: Responsive is not "stacked on mobile." Each viewport gets intentional design.

10. **What accessibility requirements exist? (Keyboard navigation, screen readers, color contrast, touch targets.)**
    - Recommended: Accessibility is not optional. Minimum: WCAG AA contrast, 44px touch targets, keyboard-navigable core flow.

### Outputs

- `.pm/stable/user-journeys.md` (all journeys with emotional arc, aha moments, failure points, recovery paths)
- `.pm/stable/ux-principles.md`

---

## Gate 6: UI Direction and Design Probe

**Goal**: Define visual and interaction taste before implementation.

**Methodology**: Inspired by gstack /design-consultation and /design-shotgun. Generate options, get user approval, record taste. For non-designers, provide vocabulary and examples.

### For UI-facing products only

If the product is CLI/library/backend-only, ask:
> "Does this product need a visual UI?"
If no: set `ui_direction_required: false` in state.yaml and skip to Gate 7.

### Questions (ask one at a time)

1. **What feeling should the product communicate?**
   - Recommended: "Calm confidence" or "playful energy" — not "modern" or "clean" (those are meaningless).

2. **Which aesthetic direction resonates?** (Present the 10 options from ui-direction.md template)
   - Recommended: Non-designers need vocabulary. Present: Brutally Minimal, Editorial/Magazine, Retro-Futuristic, Luxury/Refined, Playful/Toy-like, Brutalist/Raw, Organic/Natural, Industrial/Utilitarian, Maximalist Chaos. User picks 1-2.

3. **What visual density is appropriate?**
   - Recommended: Sparse (luxury, focus), Moderate (productivity), Dense (power user tools). Pick one.

4. **What should the product NOT look like?**
   - Recommended: Name specific products or patterns the user dislikes. This is often more useful than likes.

5. **What interaction style should dominate?**
   - Recommended: Direct manipulation, form-driven, command-line-like, card-based, etc.

6. **What AI-generated UI clichés must be avoided?** (Check all that apply):
   - [ ] Purple/violet gradient backgrounds
   - [ ] 3-column feature grid with icons in colored circles
   - [ ] Centered everything with uniform spacing
   - [ ] Uniform bubbly border-radius on all elements
   - [ ] Gradient buttons as primary CTA
   - [ ] Stock-photo hero sections
   - [ ] "Built for X" / "Designed for Y" / "Seamless Z" copy
   - [ ] Carousel anything
   - [ ] Other (user specifies)

7. **Provide visual references you like.**
   - Ask the user to share screenshots, links, or describe specific products they like.

8. **Provide visual references you dislike.**
   - Same — screenshots, links, or descriptions.

9. **For typography: which font personality fits?** (Present options from ui-direction.md)
   - Recommended: Guide non-designers with specific font names per role (Display, Body, Data). Warn about overused fonts (Inter, Roboto, etc.).

10. **What accessibility requirements exist?**
    - Recommended: Minimum WCAG AA contrast, 44px touch targets, keyboard navigation for core flow.

### Coherence validation

After all questions are answered, check:

- Does the aesthetic match the motion? (e.g., Brutalist + bouncy animation = mismatch)
- Does the density match the typography? (e.g., Dense + thin serif = hard to read)
- Does the color approach match the product type? (e.g., Playful + corporate blue = mismatch)
- Does the interaction style match the target user? (e.g., CLI-style for non-technical users = mismatch)

If any mismatches found, flag them and ask the user to resolve.

### Subtraction check

For every UI element described in this gate, ask:
> "Does this earn its pixels? If unsure, cut it."

Feature bloat kills products faster than missing features. When in doubt, subtract.

### Design probe (if taste is unclear)

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

### Outputs

- `.pm/stable/ui-direction.md` (with aesthetic direction, SAFE/RISK breakdown, font choices, accessibility)
- `.pm/design/ui-feedback.md` (if design probe was used)

### Block rule

If `Open taste questions` remain unresolved in `ui-direction.md`, mark `ui_direction_ready: false`. Supervisor must NOT delegate UI implementation.

---

## Gate 7: Product Contract Freeze

**Goal**: Freeze enough product definition for Supervisor to enter delivery loop.

### Required files check

Verify all required files exist and are substantive (not just templates):

1. `.pm/stable/product.md` — all sections filled, no `[NEEDS CLARIFICATION]` blockers
2. `.pm/stable/evidence.md` — status is passed or waived_by_user
3. `.pm/stable/value-proposition.md` — all sections filled
4. `.pm/stable/ux-principles.md` — all sections filled
5. `.pm/stable/user-journeys.md` — at least primary journey complete
6. `.pm/stable/ui-direction.md` — complete if `ui_direction_required: true`
7. `.pm/stable/roadmap.md` — at least Stage 0 defined with exit criteria
8. `.pm/stable/stage-definitions.md` — if not present, guide creation: define `product_definition`, `feasibility`, and `delivery` stages with goal, allowed/forbidden work, exit criteria
9. `.pm/stable/architecture-guardrails.md` — if not present, guide creation: ask about tech stack, architectural principles, allowed/forbidden changes, risk areas
10. `.pm/stable/acceptance-rubric.md` — if not present, copy from template

### State initialization

Write `.pm/runtime/state.yaml`:

```yaml
readiness:
  product_definition_ready: true
  evidence_ready: true  # or false
  ux_ready: true
  ux_depth: full  # full | light | not_applicable
  ui_direction_ready: true  # or false
  roadmap_ready: true
  feasibility_ready: false  # will be validated in Stage 1
```

**`ux_depth` values:**
- `full`: Gate 5 completed with all 10 UX questions answered. UX journey fully defined.
- `light`: Builder mode or "has users" mode — Gate 5 was simplified or replaced with generative questions. UX journey partially defined.
- `not_applicable`: CLI/library/backend-only product with no visual UI.

Write initial `.pm/runtime/active-stage.md` based on current roadmap stage.

Write initial `.pm/runtime/loop-log.md` with Iteration 0.

Write initial `.pm/runtime/handoff.md`.

Write initial `.pm/runtime/loop-control` with `CONTINUE`.

### Final gate check

If ANY required readiness value is false:
- List exactly what is missing.
- Supervisor must NOT enter autonomous delivery.
- User must resolve or explicitly waive each gap.

### Summary output

After Gate 7, present to the user:

> **Product contract frozen.**
> 
> - Product: [one-sentence summary]
> - Target user: [specific user]
> - MVP wedge: [smallest useful slice]
> - Evidence status: [passed/waived]
> - UI direction: [ready/not required/pending]
> - Readiness: [N/N flags true]
> 
> Next step: Supervisor can enter delivery loop to advance Stage [X].
