# Loop Steps Reference

Each iteration follows exactly these 8 steps, in order.

## Step 1: OBSERVE

Read these files in order:

1. `.pm/runtime/state.yaml` — current state
2. `.pm/runtime/active-stage.md` — current stage
3. `.pm/stable/roadmap.md` — where we're headed
4. `.pm/stable/product.md` — what we're building
5. `.pm/runtime/worker-report.md` — if present (from last iteration)
6. `.pm/runtime/acceptance-review.md` — if present
7. `.pm/runtime/loop-control` — if present

Do NOT read the full codebase. Only read specific code files if a worker report contains a contradiction that cannot be resolved from the report alone.

**Iteration limit check**: If `max_iterations` is set and `loop_iteration >= max_iterations`, stop. Write `STOP` to loop-control with reason "Iteration limit reached."

## Step 2: CHECK_READINESS

Before delegating ANY implementation work, verify:

| Readiness Flag               | Required For                                                                                                                                                                                 |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `product_definition_ready` | All work                                                                                                                                                                                     |
| `roadmap_ready`            | All work                                                                                                                                                                                     |
| `ux_ready`                 | Product-facing work                                                                                                                                                                          |
| `ux_depth`                 | Product-facing work —`missing`: no UI-facing delivery; `light`: prototypes only, no formal UI implementation; `full`: UI implementation allowed; `not_applicable`: CLI/backend-only |
| `ui_direction_ready`       | UI-facing work                                                                                                                                                                               |
| `feasibility_ready`        | Delivery loop (Stage 2+)                                                                                                                                                                     |

**If not ready:**

- Missing product definition → set `next_action.type: grill_product` and stop.
- Missing feasibility → set `next_action.type: feasibility_spike` and create a spike task.
- Missing UI direction → set `next_action.type: request_user_decision` and ask user to resolve taste.
- Do NOT delegate implementation when readiness is incomplete.

## Step 3: DECIDE

Choose exactly ONE next action:

| Action                    | When                                                        |
| ------------------------- | ----------------------------------------------------------- |
| `grill_product`         | Product definition incomplete                               |
| `feasibility_spike`     | Technical path uncertain                                    |
| `delegate`              | Ready to delegate bounded task                              |
| `review`                | Worker report exists, needs review                          |
| `request_rework`        | Worker report rejected, needs rework with specific feedback |
| `request_user_decision` | Product/MVP/tech/taste/risk decision needed                 |
| `stop`                  | Stage exit reached or stop condition triggered              |

Only ONE action per iteration. Do not combine.

## Step 4: WRITE_TASK

If action is `delegate` or `feasibility_spike`, write `.pm/runtime/next-task.md`.

**Task requirements (all must be present):**

1. **Bounded**: one task, one objective, clear done condition
2. **Verifiable**: acceptance criteria are testable
3. **Scoped**: explicit allowed and forbidden scope
4. **Connected**: tied to current roadmap stage
5. **Constrained**: includes forbidden scope to prevent scope creep
6. **Reported**: specifies `.pm/runtime/worker-report.md` as output
7. **Harness process**: specifies which Harness gates to follow (risk → context → tdd → eval → report, or subset)
8. **Verification commands**: specifies exact commands to run for proof

**For spike tasks:**

- Label the task as `[SPIKE]` in the objective
- State the technical question
- Define minimal prototype or experiment
- Define evidence to collect
- Define stop condition
- Require `.pm/runtime/spike-report.md` output

**For delivery tasks:**

- Specify `Required Harness process` field in the task packet
- Include which subskills to use: typically `harness-risk` → `harness-context` → `harness-tdd` → `harness-eval` → `harness-report`
- For leaf-risk: `harness-tdd` + `harness-report` may suffice
- For branch-risk: full chain

**Template**: Use `references/templates/pm/next-task.md` structure (repo-root relative).

## Step 5: DELEGATE_TO_OPENCODE

Read `.pm/runtime/worker-config.yaml` for execution mode. Default is `manual` if file is missing.

### Delegation routing by supervisor environment

The supervisor must detect its runtime environment and choose the correct delegation method:

**If supervisor is OpenCode** (you have the `Task` tool available):
- Use the **Task tool** with `subagent_type: "general"`.
- The prompt MUST load the harness-intern skill first via the skill tool, then point to the task file. This ensures the intern gets the full skill definition: role, execution flow, scope guardrails, and report format.
- Do NOT use `opencode run` — it will fail with "Session not found" because you are already inside an opencode session.
- Do NOT write raw implementation instructions in the prompt — the skill defines the execution flow.
- Correct example:
  ```
  Task(
    subagent_type="general",
    description="Execute harness-intern task",
    prompt='Load the harness-intern skill using the skill tool with name="harness-intern", then read and execute .pm/runtime/next-task.md exactly. Write .pm/runtime/worker-report.md and create one git commit for your task changes only. Return the worker-report.md content and verification command outputs.'
  )
  ```
  Task(
    subagent_type="general",
    description="Execute harness-intern task",
    prompt="Read .pm/runtime/next-task.md at /path/to/project and execute it exactly. ... [full task instructions] ... Return make test output, make verify output, and git log."
  )
  ```

**If supervisor is Codex or Claude Code** :

- Use the **opencode CLI** via shell execution.
- The canonical method is `opencode serve` for persistent delegation, or `opencode run` for one-shot:
  ```bash
  opencode run "/harness-intern Read and execute .pm/runtime/next-task.md exactly. Write .pm/runtime/worker-report.md and create one git commit for your task changes only." --file .pm/runtime/next-task.md
  ```
- For exact CLI syntax, see `subskills/opencode-cli/SKILL.md` and `subskills/opencode-cli/references/patterns.md`.

### Execution modes

**manual mode** — Write `.pm/runtime/next-task.md`, then set `current_phase: worker_running` in state.yaml and STOP. The worker is triggered separately. Supervisor will check for the report on the next iteration.

**sync mode (OpenCode)** — Delegate via Task tool with `subagent_type: "general"`. Prompt MUST load harness-intern skill via `skill(name="harness-intern")` first. The skill defines role, execution flow, scope guardrails, and report format — do not duplicate these in the prompt. Wait for the task result. On failure, fall back to manual mode.

**sync mode (Codex/Claude Code)** — Execute the worker via the `/harness-intern` slash command using `opencode run`. On failure, fall back to manual mode.

**poll mode** — Write task, set `current_phase: worker_running`. On next iteration, check for worker-report.md. If `timeout_minutes` exceeded, set `NEEDS_USER_DECISION` in loop-control.

### Fallback chain

1. Primary delegation method (Task tool or opencode CLI, based on environment)
2. If primary fails → manual mode (write task, stop, wait for external trigger)
3. Do NOT implement code directly — this is a protocol violation.

**Critical**: Do NOT assume the worker succeeded. Wait for `.pm/runtime/worker-report.md` to exist and be updated.

## Step 6: REVIEW_REPORT

Read `.pm/runtime/worker-report.md`.

**Reject the report immediately if any required section is missing:**

- [ ] Changed files listed
- [ ] Commands run listed
- [ ] Test results present (or explicit explanation why no tests)
- [ ] Acceptance criteria checklist present
- [ ] Problems encountered present
- [ ] Deviations from task present

**If report is rejected:**

- Set `next_action.type: request_rework` in acceptance-review.md
- List specific missing sections
- Do NOT update loop_iteration until a valid report is reviewed
- **Increment `consecutive_failures` in state.yaml**
- **Update `failure_tracking`** in state.yaml:
  - Set `last_failure_signature` to one of: `missing_report_sections | tests_failed | scope_violation | forbidden_files_touched | no_evidence | blocked_dependency`
  - Set `last_failure_reason` to a one-line description
  - If signature matches previous, increment `same_failure_count`; otherwise reset to 1

**Verification (required for branch+ risk or when worker claims are material; recommended otherwise):**

- Check `git diff --stat` against expectations
- Run `harness eval` if applicable — the Intern should have run this, but verify independently
- Run `harness context <feature-id>` to generate minimal context if the task touched multiple files
- Verify no forbidden scope was touched via `git diff` against allowed scope
- If `harness eval` was run by Intern, read its output and verify the claims
- If `harness report` was generated, include its summary in the acceptance review
- **Independent review via `/harness review`**: For branch+ risk or when worker claims are material (e.g., "all tests pass", "no forbidden scope touched"), run an independent OpenCode review agent:
  ```bash
  opencode run "/harness review Review the diff on the current branch for safety, scope compliance, and evidence quality." --file .pm/runtime/next-task.md
  ```
- **Parallel independent reviewers**: When the review questions are separable (e.g., scope compliance vs test coverage vs security), spawn multiple independent review agents in parallel rather than sequential reviews. Each agent should focus on one concern and produce a focused verdict.

**If report is accepted:**

- **Reset `consecutive_failures` to 0** in state.yaml
- Increment `iteration_valid_count` if all 3 artifacts (task, report, review) are valid

## Step 7: UPDATE_STATE

After writing acceptance review, update ALL of these files:

1. `.pm/runtime/acceptance-review.md` — verdict, evidence, next action
2. `.pm/runtime/state.yaml` — increment `loop_iteration`, update `current_phase`, update `next_action`, update `consecutive_failures`, update `iteration_valid_count`/`iteration_total_count`
3. `.pm/runtime/loop-log.md` — append iteration entry
4. `.pm/runtime/handoff.md` — current state summary for resume
5. `.pm/runtime/loop-control` — write one of: CONTINUE, STOP, NEEDS_USER_DECISION, BLOCKED, STAGE_EXIT_REACHED

**State update rules:**

- `loop_iteration` increments ONLY after a completed review (valid report accepted or rejected with rework).
- `iteration_total_count` increments every iteration.
- `current_phase` must always reflect the NEXT expected action.
- Valid phase values: `product_definition | feasibility | ready_to_delegate | worker_running | review_pending | needs_rework | needs_user_decision | blocked | stage_exit_reached | stopped`
- `last_updated` must be set to current timestamp on every state write.
- `last_verified` must be updated with commit hash, test command, and result when evidence exists.

## Step 8: CONTINUE_OR_STOP

Write one value to `.pm/runtime/loop-control`:

| Value                   | When                                                        |
| ----------------------- | ----------------------------------------------------------- |
| `CONTINUE`            | Task accepted, next iteration should run                    |
| `STOP`                | Stage exit reached, unrecoverable error, or iteration limit |
| `NEEDS_USER_DECISION` | Product/MVP/tech/taste/risk decision required               |
| `BLOCKED`             | External blocker that Supervisor cannot resolve             |
| `STAGE_EXIT_REACHED`  | Current stage exit criteria met, ready for next stage       |
