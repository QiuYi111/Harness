# Decisions

## 2026-05-07: Delegation mechanism bug (critical)

### Problem

When opencode is the supervisor, `opencode run` fails with "Session not found". This means the canonical delegation path in loop-steps.md (`opencode run "/harness-intern ..."`) is broken in the most common deployment scenario.

### Root cause

The supervisor skill references `subskills/opencode-cli/SKILL.md` as a file path but never actually loads it as a skill. The opencode-cli skill documents three delegation modes:
- `opencode serve` — persistent headless API server
- `opencode run --attach url` — attach to a running server
- Task tool — sub-agent within the same process

The supervisor only knows about `opencode run` (which fails) and manual mode (which requires external triggering).

### Impact

Supervisor falls back to implementing code directly, violating the core principle that supervisor is PM, not engineer. This happened in iteration 8.

### Required fixes

1. Supervisor must `skill("opencode-cli")` at startup to understand available delegation patterns
2. loop-steps.md must document the correct delegation chain: `opencode serve` → `opencode run --attach` OR Task tool fallback
3. When both opencode run AND Task tool fail, supervisor must write BLOCKED or NEEDS_USER_DECISION — NOT implement code
4. The Task tool returned empty in iteration 8 — investigate whether this is a skill loading issue or a prompt issue

### Decision

Record as critical process violation. Fix delegation path as a priority task.
