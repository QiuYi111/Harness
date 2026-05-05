# Autopilot Rules

Harness should proceed automatically unless a stop condition is reached.

## Default Autopilot

If a task is leaf or branch risk and requirements are clear:

1. Create or update spec artifacts if missing.
2. Create plan and tasks if missing.
3. Classify risk.
4. Generate context bundle.
5. Execute implementation using appropriate TDD role.
6. Run verify-ai.
7. Produce eval/report.

## Fast Path for Leaf Work

For leaf changes (docs, typo fixes, tests, isolated scripts, templates):

- Do NOT force full SPEC -> PLAN -> TASKS lifecycle.
- Classify risk.
- Make change.
- Run relevant verification.
- Write short report only if user asks or PR requires it.

## Branch Path

For feature-level work (services, endpoints, new features):

- SPEC required
- PLAN required
- TASKS required
- EVAL/REPORT required before merge

## Core Path

For domain/auth/schema/permission changes:

- SPEC required
- PLAN required
- Rollback plan required
- Human approval required BEFORE implementation
- EVAL/REPORT required
- Architecture review recommended

## Infra Path

For CI/CD/deployment/secrets/migration:

- Dry run required
- Rollback plan required
- Explicit human approval required
- Security review required
- No auto-merge

## Debug Autopilot

### Leaf Debug (fast path)

For leaf-risk bugs (isolated component, no downstream dependents):
1. Create record.md
2. Reproduce
3. Gather evidence (can be brief for simple bugs)
4. Diagnose root cause
5. Patch with failing test first
6. Verify regression test passes
7. Review diff
8. Close — no eval/report required

Full autopilot. No human stops.

### Branch Debug

For feature-level bug fixes (multi-file, bounded behavior change):
1. Full 7-phase debug flow (autopilot through all phases)
2. After close: load `harness-eval`, then `harness-report`

### Core/Infra Debug

For domain/auth/schema/permission/deployment bug fixes:
1. Full 7-phase debug flow
2. **STOP at Phase 4 (patch): require human approval before patching**
3. After close: load `harness-eval`, then `harness-report`
4. Architecture review may be required

### Emergency Hotfix

For P0 production incidents:
1. Use debug flow but compress Phase 2 (evidence) and Phase 3 (diagnose) — gather minimum viable evidence
2. Classify risk immediately. If leaf: proceed. If branch+: require human approval.
3. Phase 4 (patch) always requires human approval for hotfixes, regardless of risk
4. Phase 5 (regression) is mandatory — no exceptions, even in emergencies
5. Phase 6 (review) can be post-merged but must happen within same session

## Never Ask If You Can Infer

Do NOT ask the user for:
- Feature ID if one can be generated from context
- File paths if repo structure reveals them
- Test command if Makefile exposes it
- Risk level if classify-risk can determine it
- Context files if context bundle can be generated

## Always Ask For

Stop and ask human input when:
- Core or infra risk requires approval
- Product scope is ambiguous
- Acceptance criteria conflict
- The requested change violates role boundaries
- Implementation would require changing tests during GREEN phase
- Security/permission/data-migration implications exist

## Verification Before Claims

Before claiming any status or expressing satisfaction, run the verification gate:

```
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim
```

Red flags — STOP and verify before proceeding:
- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit/push/PR without verification
- Trusting agent success reports without independent check
- Thinking "just this once" is acceptable

| Claim | Requires | Not Sufficient |
|---|---|---|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check |
| Build succeeds | Build command: exit 0 | Linter passing |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
