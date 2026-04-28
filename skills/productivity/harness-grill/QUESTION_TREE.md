# Question Tree

Interrogation framework for stress-testing specs and plans. Walk each branch one question at a time. Skip branches that don't apply, but call out why you're skipping.

## Branch 1: Problem & Scope

1. What problem does this solve and for whom?
2. What happens if we don't build this?
3. What is the smallest version of this that delivers value?
4. What did you explicitly decide NOT to include? Why?
5. Who are the users? Are there different roles with different needs?

## Branch 2: Inputs & Outputs

1. What are the primary inputs? Where do they come from?
2. What are the primary outputs? Who consumes them?
3. What is the happy path from input to output?
4. What happens when input is missing, malformed, or partial?
5. Are there rate limits, size limits, or format constraints?

## Branch 3: Edge Cases & Failure Modes

1. What happens when the system is under load?
2. What happens when a dependency is unavailable?
3. What happens when two users act on the same resource simultaneously?
4. What are the most likely ways this breaks in production?
5. What data states are illegal or impossible? How are they prevented?

## Branch 4: State & Data

1. What state does this feature introduce or modify?
2. Where does state live? How long is it retained?
3. Are there migrations? What happens to existing data?
4. What are the read vs write patterns?
5. Is there a cleanup or archival strategy?

## Branch 5: Security & Permissions

1. Who is allowed to do what? Are there role boundaries?
2. What sensitive data is touched? How is it protected?
3. Are there audit or compliance requirements?
4. What would a malicious user try to do with this feature?
5. Are there any trust boundaries being crossed?

## Branch 6: Integration & Dependencies

1. What existing systems does this touch?
2. Are there API contracts that change? Who depends on them?
3. Are there third-party dependencies? What if they change or disappear?
4. Does this require coordination with other teams or services?
5. What is the blast radius if this change goes wrong?

## Branch 7: Observability & Operations

1. How will you know this is working correctly in production?
2. What metrics should be monitored?
3. What alerts should be set up?
4. How would you debug a failure in this feature?
5. What is the rollback plan?

## Branch 8: Testing & Acceptance

1. How do you verify this works end-to-end?
2. What are the critical test scenarios?
3. Are there performance benchmarks to hit?
4. How do you test the failure modes?
5. What does "done" look like? What are the acceptance criteria?

## Branch 9: Assumptions & Unknowns

1. What are you assuming that might be wrong?
2. What decisions were made without full information?
3. What would change your mind about the approach?
4. Are there any `[NEEDS CLARIFICATION]` items that are blocking?
5. What is the most dangerous unknown?

## How to Use

- Start with Branch 1 and work through sequentially.
- Within each branch, ask questions one at a time. Wait for the answer before moving to the next.
- If the user's answer raises a new question, follow that thread before returning to the tree.
- For each question, provide a recommended answer based on the codebase, spec, or domain knowledge.
- Skip branches only when the feature clearly doesn't intersect with that domain. State why.
- Summarize findings at the end: clarified items, new `[NEEDS CLARIFICATION]` markers, and recommended spec updates.
