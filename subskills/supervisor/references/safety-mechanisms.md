# Safety Mechanisms Reference

## Agent-Loop Safety

The supervisor loop is bounded by safety mechanisms to prevent runaway execution.

### Iteration Limit

- `state.yaml` contains `max_iterations`. If set, the loop MUST stop when `loop_iteration >= max_iterations`.
- For unbounded `/goal` sessions, `max_iterations` is `null` (no hard limit), but the consecutive failure breaker still applies.
- For agent-loop feasibility testing, set `max_iterations: 5`.

### Consecutive Failure Breaker

- `state.yaml` tracks `consecutive_failures` and `max_consecutive_failures` (default: 3).
- If a worker report is rejected (needs_rework), increment `consecutive_failures`.
- If a worker report is accepted, reset `consecutive_failures` to 0.
- If `consecutive_failures >= max_consecutive_failures`, STOP. Write `NEEDS_USER_DECISION` to loop-control with the reason: "Worker failed [N] consecutive times on similar tasks. Escalating to user."

### Agent-Loop Feasibility Validation

Before enabling unbounded `/goal` loops, run a bounded test:

```yaml
max_iterations: 5
```

Pass requirements (all must be met to enable unbounded mode):

1. At least 4 out of 5 iterations produce valid `next-task.md`.
2. At least 4 out of 5 iterations produce valid `worker-report.md`.
3. At least 4 out of 5 iterations produce valid `acceptance-review.md`.
4. State is updated every iteration.
5. Supervisor does not change product direction without permission.
6. Intern does not exceed task scope without reporting deviation.
7. Stop conditions work when triggered.

Track these in `state.yaml`:
- `iteration_valid_count`: incremented when an iteration produces all 3 valid files + state update
- `iteration_total_count`: incremented every iteration

After bounded test completes, check: `iteration_valid_count / iteration_total_count >= 0.8`. If not, the loop is not safe for unbounded mode.

## Stop Conditions

**You MUST stop and request user input when:**

1. Product positioning would change
2. MVP boundary would change
3. Core tech stack would change
4. Harness risk classification is `core` or `infra`
5. Security, auth, payment, deployment, or data migration is involved
6. UI taste question remains unresolved
7. Worker fails the same class of task `max_consecutive_failures` times (default 3)
8. Worker report lacks evidence after being asked to provide it
9. Tests cannot pass and the path forward is unclear
10. Stage exit criteria are met
11. User decision is explicitly required by state.yaml
12. Iteration limit reached (`loop_iteration >= max_iterations` when `max_iterations` is set)

**When stopping for user decision:**
- Write `NEEDS_USER_DECISION` to loop-control
- Update handoff.md with the question and context
- Present the decision to the user with options

## File Writing Rules

1. Every state change MUST have a corresponding loop-log entry.
2. Every task packet MUST have acceptance criteria AND Harness process specification.
3. Every acceptance review MUST have evidence.
4. Never write "accepted" without attaching what was verified.
5. Never increment loop_iteration without a completed review.
6. Never reset consecutive_failures to 0 without a genuinely accepted report.
7. `last_updated` must always reflect the current write time.
