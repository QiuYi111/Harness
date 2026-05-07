# Execution Flow

## Before Starting

1. Read `.pm/runtime/next-task.md` — this is your primary input.
2. Read every file listed in the task's `Read first` section.
3. Read `.pm/stable/architecture-guardrails.md` — know the boundaries.
4. Read `.pm/stable/acceptance-rubric.md` — know what "done" means.
5. If the task references a Harness context bundle (e.g., `specs/<feature>/context.md`), read it. It contains the minimal relevant spec, plan, and tasks for your work.

## Steps

### 1. Understand the task

Read `next-task.md` carefully:

- **Objective**: What you're trying to accomplish
- **Allowed scope**: What you MAY touch
- **Forbidden scope**: What you MUST NOT touch
- **Acceptance criteria**: How "done" is measured
- **Required Harness process**: What engineering gates to follow

If any part of the task is unclear, check the files in `Read first`. If still unclear, note it in your report under "Problems encountered."

### 2. Risk classify

Determine the blast radius of your proposed changes:

- **leaf**: single file, isolated change → proceed
- **branch**: multi-file, behavioral change → proceed with tests
- **core**: domain model, auth, storage → STOP, report blocker
- **infra**: deployment, CI/CD, secrets, migrations → STOP, report blocker

If risk is `core` or `infra` and the task does NOT explicitly approve it, do NOT proceed. Write a blocker report.

Use `harness classify-risk` if available, or follow the manual decision tree in `subskills/risk/SKILL.md`.

### 3. Plan your approach

Before writing code:

1. Identify which files need to change
2. Verify they are within allowed scope
3. Plan the test strategy (what to test, how)
4. Check if existing tests need updating

### 4. Implement

Follow Harness engineering flow based on task type:

**For feature implementation:**
- Follow the `Required Harness process` specified in the task
- Typically: `harness-risk` → `harness-context` → implement → `harness-tdd` → `harness-eval` → `harness-report`
- For leaf-risk: `harness-tdd` + `harness-report` may suffice
- For branch-risk: full chain
- If the task specifies a Harness context bundle path, read it before implementing

**For spike/investigation:**
- Build minimal prototype
- Collect evidence
- Do NOT treat spike code as production code
- Write to `.pm/runtime/spike-report.md`

**For bug fix:**
- Follow `harness-maintain-debug` flow: reproduce → evidence → diagnose → patch → regression

### 5. Test

- Write tests for your changes
- Run the verification commands specified in the task
- Run `make verify` if available
- If no tests were run, you MUST explicitly state why in your report

### 6. Verify

- Run ALL required verification commands from the task
- Ensure existing tests still pass
- Check for regressions
- Run `harness eval` if the task requires it (specified in `Required Harness process`)
- If `harness eval` fails, do NOT claim completion — report the failure in your report
- Run `make verify` or `make verify-ai` if available
- Attach fresh verification output as evidence in your report

### 7. Write report

Write `.pm/runtime/worker-report.md` using the template structure.

**Required sections — every one must be present:**

```markdown
# Worker Report

## Task summary
[One sentence]

## What was done
[Bulleted list of actions]

## Changed files
[List every file modified, created, or deleted]

## Commands run
[Table of command → result]

## Test results
[Evidence or explicit explanation why no tests]

## Harness results
[Risk classification, gate results]

## Acceptance criteria checklist
- [ ] [Each criterion from the task, marked met or unmet]

## Problems encountered
[Issues found during execution]

## Deviations from task
[Any scope deviation with explanation, or "None"]

## Remaining work
[What was left undone]

## Suggested next step
[What should happen next]

## Evidence
[Concrete proof: test output, git diff stats, verification results]
```

## Common Patterns

### Pattern: Feature task

```
1. Read next-task.md
2. Read files from "Read first" section
3. Classify risk → if core/infra, report blocker
4. Read relevant code context
5. Implement within allowed scope
6. Write tests
7. Run verification
8. Write worker-report.md
```

### Pattern: Spike task

```
1. Read next-task.md (labeled [SPIKE])
2. Read spike question and constraints
3. Build minimal experiment
4. Collect evidence
5. Write spike-report.md
6. Write worker-report.md referencing spike-report.md
```

### Pattern: Bug fix task

```
1. Read next-task.md
2. Reproduce the issue
3. Gather evidence
4. Diagnose root cause
5. Apply minimal fix
6. Run regression tests
7. Write worker-report.md
```
