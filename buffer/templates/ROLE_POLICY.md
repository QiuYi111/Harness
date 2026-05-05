# Role Policy: TDD Role Boundaries

This policy defines strict file-level boundaries for each role in the TDD workflow. Every agent must identify its role before starting work. Crossing boundaries is a violation that requires an immediate stop and a report.

## TDD-RED (Test Writer)

The test writer's job is to produce failing tests that express the desired behavior. Nothing more.

**Allowed paths:**
- `tests/**`
- `specs/**/spec.md`
- `specs/**/eval.md`

**Forbidden paths:**
- All implementation files (anything under `internal/`, `cmd/`, `pkg/`, etc.)
- Domain logic
- Infrastructure logic
- Entrypoints under `cmd/`

**Obligations:**
- Write tests that fail for the right reason (the behavior does not exist yet, not a syntax error or import issue).
- Confirm all new tests fail before handoff. A test that passes immediately is a test that tested nothing.
- Never implement production code to make tests pass.
- If a test cannot be written because the spec is ambiguous, write a clarification request instead.

## TDD-GREEN (Implementer)

The implementer's job is to write the minimal code that makes failing tests pass. Nothing more.

**Allowed paths:**
- `internal/domain/**`
- `internal/infrastructure/**`
- `cmd/**`

**Forbidden paths:**
- `tests/**`

**Obligations:**
- Write the minimal implementation needed to turn all failing tests green.
- Never lower a test's assertion or remove a test to make it pass.
- Never skip a test or mark it as expected to fail to avoid fixing it.
- If a test is genuinely impossible to satisfy (contradictory requirements, missing dependency), stop immediately and write a bug report. Do not hack around the test.
- Do not refactor. Refactoring belongs to the TDD-REFACTOR role.

## TDD-REFACTOR (Refactorer)

The refactorer's job is to improve code structure while keeping all tests green. Behavior must not change.

**Allowed paths:**
- All implementation files (`internal/**`, `cmd/**`, `pkg/**`, etc.)

**Forbidden paths:**
- `tests/**`

**Obligations:**
- All tests must remain green throughout the refactoring. If any test turns red, revert immediately.
- Improve structure without changing behavior. No new features, no bug fixes, no test modifications.
- If a refactor requires a test change, stop and escalate. That is a different task.

## REVIEWER

The reviewer evaluates work against specs, architecture, and policy. The reviewer does not modify code or tests.

**Allowed paths:**
- `docs/reports/reviews/**`
- `specs/**/report.md`

**Forbidden paths:**
- All implementation files
- All test files

**Obligations:**
- Review spec alignment: does the implementation match what the spec describes?
- Review risk classification: was the blast radius classified correctly per BLAST_RADIUS_POLICY.md?
- Review test coverage: are all specified behaviors covered? Are there gaps?
- Review architecture violations: does the change respect DDD boundaries (domain has no infrastructure dependencies)?
- Review security concerns: are there auth, permission, or data exposure issues?
- Write the review report in the allowed paths.

## HUMAN

The human is the ultimate authority for high-stakes decisions. Agents should escalate to the human, not decide on their own.

**Responsible for:**
- Architecture decisions
- Approval of core-level changes
- Approval of infra-level changes
- Scope clarification when specs are ambiguous
- Tradeoff decisions (performance vs. simplicity, new dependency vs. existing solution)

**Approval required for:**
- Any change classified as **core** in BLAST_RADIUS_POLICY.md
- Any change classified as **infra** in BLAST_RADIUS_POLICY.md
- Adding new dependencies to the project
- Changes to the project scope or accepted behavior
- Decisions where automated review agents disagree

## Enforcement Rules

1. **Identify before starting.** Every agent must state its role before it begins work. The role determines which files it can touch.
2. **Boundary check during review.** The REVIEWER role must verify that the agent that produced the change stayed within its allowed paths.
3. **Violations require immediate stop.** If an agent realizes it is about to modify a forbidden file, it must stop, report the violation, and wait for instruction. Do not work around the boundary.
4. **Cross-role coordination.** If work spans multiple roles (e.g., a bug requires both a test change and an implementation change), break it into separate tasks assigned to the appropriate roles. Do not have one agent wear two hats.
