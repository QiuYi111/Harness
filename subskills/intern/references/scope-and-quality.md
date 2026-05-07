# Scope Discipline and Quality Rules

## Scope Discipline

### You MUST:

- Follow task scope exactly
- Report blockers instead of inventing scope
- Write tests for your changes
- Run verification before claiming completion
- List every changed file
- Explain any deviation from the task

### You MUST NOT:

- Modify `.pm/stable/product.md` unless the task explicitly asks
- Modify `.pm/stable/ui-direction.md` unless the task explicitly asks
- Change MVP boundary
- Change core tech stack
- Perform infra/security/payment/auth changes without explicit approval in the task
- Claim success without test or verification evidence
- Implement features "while you're at it" that weren't in the task
- Add dependencies not specified in the task
- Refactor unrelated code

## Blocker Behavior

If you cannot complete the task:

1. Write `.pm/runtime/blockers.md` with:
   - What is blocking
   - Why it blocks progress
   - What you tried
   - What options exist to unblock

2. Write `.pm/runtime/worker-report.md` with:
   - What you accomplished before blocking
   - The blocker details
   - Deviations set to "Blocked: [reason]"

3. Do NOT:
   - Invent a product direction to work around the blocker
   - Change scope silently to avoid the blocker
   - Claim the task is complete when it is not

## Quality Rules

1. **No completion without evidence.** Run verification commands. Attach output.
2. **No silent scope changes.** Every deviation must be documented.
3. **No guessing.** If unsure about scope, report it as a problem.
4. **No shortcuts on tests.** If the task requires tests, write real tests.
5. **No orphan changes.** Every changed file must be listed in the report.
