# Harness Routing Table

Map user intent to the correct Harness skill.

| User Intent | First Skill | Then |
|---|---|---|
| "build this feature" | harness | grill/specify -> plan -> tasks -> risk |
| "fix this bug" | harness-risk | context -> tdd -> eval/report |
| "review this PR" | harness-risk | eval -> report -> architecture-review |
| "make a plan" | harness-plan | tasks |
| "break into tasks" | harness-tasks | risk |
| "use TDD" | harness-tdd | eval/report |
| "this repo is messy" | harness-architecture-review | domain-language |
| "reduce token cost" | harness-cache | context |
| "initialize repo" | harness-init | domain-language |
| "I have an idea" | harness-grill | specify |
| "what's the risk" | harness-risk | (report risk, wait for decision) |
| "is this done" | harness-eval | report |

## How to use this table

1. Match the user's request to the closest intent in column 1.
2. Load the skill in column 2.
3. After that skill runs, proceed to column 3 skills in order.
4. If uncertain between two intents, prefer the more conservative path (more process).
