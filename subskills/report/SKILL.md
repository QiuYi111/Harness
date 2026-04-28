---
name: harness-report
description: >
  Produce an implementation report with changed files, risk classification, test evidence,
  review findings, known issues, and rollback plan. Use after implementation or before PR
  review to create an evidence package. Triggers: "report", "implementation report",
  "evidence package", "what changed", "ship report", "create report", "generate report",
  "PR report", "rollback plan".
---

# harness-report

Aggregates outputs from other Harness skills into a self-contained implementation report.

## When to activate

- After implementation completes
- Before PR review
- When someone asks "what changed?" or "create a report"
- After `harness-eval` has run (recommended but not required)

## Prerequisites

- Implementation code exists on the current branch
- Read `../../references/DOMAIN-AWARENESS.md` for terminology

## Steps

### 1. Gather inputs

Collect from other skills' outputs (read if they exist, skip if not):

- **Diff summary**: `git diff --stat` against base branch
- **Risk classification**: from `harness-plan` or `classify-risk` output
- **Test results**: from `make verify` and test runner output
- **Eval results**: from `specs/*/eval.md`
- **Review findings**: from review reports
- **Known issues**: from TODOs, deferred items in eval

### 2. Classify risk

If not already classified, determine blast radius:

- **leaf** — isolated, low-dependency changes
- **branch** — feature-level, multi-file behavior changes
- **core** — domain, auth, storage, permissions
- **infra** — deployment, CI/CD, secrets, migrations

### 3. Write report

Follow the format in [REPORT_FORMAT.md](./REPORT_FORMAT.md).

Enforce these rules:
- core/infra changes **must** include a rollback plan
- Report **must** include risk classification
- Report **must** include verification evidence (`make verify`, `make verify-ai`)

### 4. Zoom-out summary (optional)

If the user asks for broader context on the changes, include a zoom-out section: what area of the system this affects, how it relates to adjacent features, and what could break downstream.

## Output

Write `specs/<feature>/report.md` using the format in [REPORT_FORMAT.md](./REPORT_FORMAT.md).

## Reference

- [REPORT_FORMAT.md](./REPORT_FORMAT.md) — output template with sections and tables
- `../../references/DOMAIN-AWARENESS.md` — domain terminology and risk vocabulary
