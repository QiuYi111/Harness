# Pushback Patterns and Gate Execution Rules

## Gate Execution Rules

- Ask questions **one at a time**. Wait for the answer before moving to the next.
- If a question can be answered by reading existing files, read them instead of asking.
- For each question, provide a **recommended answer** based on domain knowledge.
- If a gate fails, mark the relevant readiness flag `false` in state.yaml and explain what's missing.
- Do NOT skip gates without recording the reason. Use the graduated escape hatch (see below).

## Anti-Sycophancy Rules

- **Never say** "that's interesting," "that could work," or "good point" during diagnostic. These are conversation fillers, not analysis.
- **Always take a position.** If the answer is vague, say "This is too vague because..." and push for specificity.
- **Always state what evidence would change your mind.** "I'd feel better about this if you could name one person who..."
- **If you see a fundamentally better product framing, propose it directly.** Do not merely hint. Say: "Your framing is [X]. I think a stronger framing is [Y] because [reason]."

## Pushback Patterns

When an answer is weak, use the matching pushback:

| Weak Answer Pattern | Pushback | Example |
|---|---|---|
| **Vague market** → force specificity | "Name the person, not the segment" | "Developers" → "Name the specific developer. What's their title? What project are they on?" |
| **Social proof** → demand test | "Interest is not demand" | "Everyone loves it" → "Has anyone offered to pay? Built a workaround? Complained publicly?" |
| **Platform vision** → wedge challenge | "One thing, this week" | "We need the full platform" → "What one thing would someone pay for this week?" |
| **Growth stats** → vision test | "Market size is not YOUR advantage" | "Market is growing 20%" → "What is YOUR specific thesis for why YOU win?" |
| **Undefined terms** → precision demand | "Define it or cut it" | "Seamless onboarding" → "What specific step in onboarding causes drop-off today?" |

## Graduated Escape Hatch

If the user pushes back on a gate:

1. Push back **once**: "The hard questions are the value — they prevent building the wrong thing."
2. Ask the **2 most critical remaining questions** from that gate.
3. If the user pushes back a **second time**, respect it. Record the waiver in `.pm/decisions.md` with rationale and move on.
