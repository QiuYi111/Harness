# Harness Routing Table

Map user intent to the correct Harness skill.

## Feature Lifecycle

| User Intent | First Skill | Then |
|---|---|---|
| "build this feature" | harness | grill/specify → plan → tasks → risk → context → tdd → eval → report |
| "I have an idea" | harness-grill | specify → plan → tasks → risk → context → tdd → eval → report |

## Debug / Maintenance

| User Intent | First Skill | Then |
|---|---|---|
| "fix this bug" | harness-maintain-debug | reproduce → evidence → diagnose → patch → regression → review → (eval → report if risk ≥ branch) |
| "test failed" | harness-maintain-debug | reproduce → diagnose → regression |
| "debug this" | harness-maintain-debug | reproduce → evidence → diagnose → patch → regression → review → (eval → report if risk ≥ branch) |
| "regression" | harness-maintain-debug | compare recent changes → reproduce → patch → regression |
| "flaky test" | harness-maintain-debug | collect evidence → isolate nondeterminism → add stability check |
| "hotfix" / "production is down" | harness-maintain-debug | reproduce → diagnose → patch (leaf risk only, fast path) → regression |

## Refactor / Improvement

| User Intent | First Skill | Then |
|---|---|---|
| "refactor X" | harness-risk | plan → tasks → tdd → eval → report |
| "clean up X" / "remove dead code" | harness-risk | plan → tasks → tdd → eval → report |
| "optimize X" / "X is slow" | harness-maintain-debug | reproduce → diagnose → (if perf bug: patch → regression; if redesign needed: plan → tdd) |
| "update dependency X" | harness-risk | tdd → eval → report |
| "migrate X to Y" | harness-risk | plan → tasks → tdd → eval → report |

## Review / Status

| User Intent | First Skill | Then |
|---|---|---|
| "review this PR" | harness-eval | report → (architecture-review if core/infra) |
| "what's the risk" | harness-risk | (report risk, wait for decision) |
| "is this done" | harness-eval | report |
| "what's the status" | harness | (run `harness status`, report) |
| "security review" | harness-architecture-review | risk → report |

## Planning / Setup

| User Intent | First Skill | Then |
|---|---|---|
| "make a plan" | harness-plan | tasks |
| "break into tasks" | harness-tasks | risk |
| "use TDD" | harness-tdd | eval → report |
| "reduce token cost" | harness-cache | context |
| "initialize repo" | harness-init | domain-language |
| "this repo is messy" | harness-architecture-review | domain-language |
| "rollback this change" | harness-risk | (identify rollback target, verify revert) |

## How to use this table

1. Match the user's request to the closest intent in column 1.
2. Load the skill in column 2.
3. After that skill runs, proceed to column 3 skills in order.
4. If uncertain between two intents, prefer the more conservative path (more process).
5. For leaf-risk work, skip steps marked "if risk ≥ branch".
6. The full feature lifecycle after risk is: `risk → context → tdd → eval → report`. The autopilot rules (AUTOPILOT_RULES.md) govern which steps can be skipped.
