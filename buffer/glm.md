# Harness v2 Implementation Plan

> Spec-Governed Agentic Engineering Harness — Template Repository Upgrade

**Branch**: `harness-v2` | **Date**: 2026-04-28 | **Status**: DRAFT

## Strategy Decision

**Route C: Pure Template Upgrade** — Merge the best patterns from Spec Kit, Anthropic best practices, and AGENTS.md into Harness's own `templates/` directory. No dependency on `specify` CLI. Users copy templates, fill placeholders, done.

**Harness's Unique Value** (things NOT available in Spec Kit):
1. DDD enforcement (domain isolation, dependency direction rules)
2. TDD role isolation (RED/GREEN/REFACTOR with agent boundaries)
3. Blast radius policy (risk-classified agent autonomy)

**Borrowed Patterns** (from Spec Kit, adapted):
1. Feature-level spec artifact lifecycle (specs/xxx/ directory structure)
2. Structured PRD with user stories, acceptance criteria, clarification markers
3. Task DAG with parallel-safe markers and checkpoints
4. Constitution/project principles template

---

## File Inventory

### New Files to Create (11)

| # | File | Lines (est.) | Source |
|---|------|-------------|--------|
| 1 | `templates/SPEC_TEMPLATE.md` | ~140 | Adapted from spec-kit spec-template.md |
| 2 | `templates/PLAN_TEMPLATE.md` | ~110 | Adapted from spec-kit plan-template.md |
| 3 | `templates/TASKS_TEMPLATE.md` | ~200 | Adapted from spec-kit tasks-template.md |
| 4 | `templates/CONSTITUTION_TEMPLATE.md` | ~80 | Adapted from spec-kit constitution-template.md |
| 5 | `templates/BLAST_RADIUS_POLICY.md` | ~60 | Original (Harness unique value) |
| 6 | `templates/AGENTS.md` | ~100 | Original (cross-agent compatibility) |
| 7 | `templates/CONTRACT_TEMPLATE.md` | ~40 | Original (API contract placeholder) |
| 8 | `templates/DATA_MODEL_TEMPLATE.md` | ~40 | Original (data model placeholder) |
| 9 | `templates/QUICKSTART_TEMPLATE.md` | ~60 | Adapted from spec-kit quickstart pattern |
| 10 | `templates/REPORT_TEMPLATE.md` | ~50 | Original (implementation + review report) |
| 11 | `templates/EVAL_TEMPLATE.md` | ~40 | Original (expected behavior + graders) |

### Files to Modify (6)

| # | File | Change |
|---|------|--------|
| 1 | `templates/PRD_TEMPLATE.md` | Major rewrite: add user stories, FRs, acceptance criteria, ambiguities, out-of-scope |
| 2 | `templates/CLAUDE.md` | Refactor: extract details to referenced files, add hooks/guards section, stay <200 lines |
| 3 | `templates/Makefile` | Add real targets: `spec-init`, `security-scan`, `contract-test`, `verify-all` |
| 4 | `templates/CONTRIBUTING.md` | Update workflow to reference new spec artifacts, add blast radius references |
| 5 | `templates/.pre-commit-config.yaml` | Add: gitleaks, conventional commits, branch naming |
| 6 | `templates/ARCHITECTURE.md` | Remove TODO, sync with IMPLEMENTATION_GUIDE |

### Root Files to Update (3)

| # | File | Change |
|---|------|--------|
| 1 | `README.md` | Rewrite: reflect v2 structure, new templates, updated workflow |
| 2 | `IMPLEMENTATION_GUIDE.md` | Update adoption steps to include new spec artifacts |
| 3 | `MANIFESTO.md` | Minor: add blast radius principle, update quality standards |

---

## Phase Breakdown

### Phase 0: Identity Cleanup (1 task)

**Purpose**: Resolve naming inconsistencies before adding new content.

- [ ] T001 Rename "Neural-Grid Framework" → "Harness" consistently across all files. Remove "Neural-Grid" branding. Fix typos ("ComprehensiveaREADEME" → "Comprehensive README"). Ensure repo name, README title, and MANIFESTO all say "Harness".

**Deliverable**: All files use consistent "Harness" branding. Zero references to "Neural-Grid".

---

### Phase 1: PRD Template Rewrite [P0] (1 task)

**Purpose**: Fix the entry point. The PRD template is the first artifact users create. Currently 42 lines of tech-focused scaffolding. Must become a product-focused spec with anti-hallucination fields.

- [ ] T002 Rewrite `templates/PRD_TEMPLATE.md` based on spec-kit's spec-template.md patterns.

**Required fields** (new):

```markdown
## 1. Vision & Scope (keep, enhance)
  - What / Input / Output / Core Logic (existing)
  - MVP Goals (existing)

## 2. User Stories (NEW — from spec-kit)
  - US-001 through US-NNN
  - Each with: Priority (P1/P2/P3), Independent Test, Given/When/Then acceptance scenarios
  - Why this priority (rationale)

## 3. Requirements (NEW — from spec-kit)
  - Functional Requirements: FR-001, FR-002, ...
  - Non-Functional Requirements: Performance, Security, Privacy, Observability, Compatibility
  - Key Entities (if data involved)

## 4. System Architecture (keep)
  - Core Pattern, Tech Stack (existing)

## 5. Interfaces (keep, enhance)
  - Contract (API) — reference to contracts/ directory
  - Data Schema — reference to data-model.md

## 6. Success Criteria (NEW — from spec-kit)
  - SC-001 through SC-NNN (measurable outcomes)

## 7. Ambiguities (NEW — anti-hallucination)
  - [NEEDS CLARIFICATION: ...] markers
  - Explicit assumptions list

## 8. Out of Scope (NEW — anti-hallucination)
  - What this feature will NOT do

## 9. Hard Truths / Risks (keep)
```

**Constraints**:
- Template must work with placeholder replacement (no CLI dependency)
- Keep Chinese comments style consistent with existing CLAUDE.md
- Include instructions for AI agents on how to fill each section
- Total length: ~120-150 lines (dense, not padded)

**Acceptance**: New PRD_TEMPLATE.md has all 9 sections. Each section has placeholder text and AI-agent-readable instructions. No section is empty/TODO.

---

### Phase 2: Feature-Level Spec Artifacts [P0] (3 tasks)

**Purpose**: Create the `specs/xxx/` directory template system. Each feature gets its own closed-loop artifact set.

- [ ] T003 [P] Create `templates/SPEC_TEMPLATE.md` — Feature specification (what/why/acceptance)
  - Adapted from spec-kit spec-template.md
  - Sections: User Scenarios, Requirements, Success Criteria, Assumptions
  - Includes Given/When/Then acceptance format
  - Includes `[NEEDS CLARIFICATION]` markers

- [ ] T004 [P] Create `templates/PLAN_TEMPLATE.md` — Technical implementation plan (how/architecture)
  - Adapted from spec-kit plan-template.md
  - Sections: Summary, Technical Context, Constitution Check, Project Structure, Complexity Tracking
  - References: spec.md (input), data-model.md, contracts/, research.md
  - Includes DDD layer constraints from Harness

- [ ] T005 Create `templates/TASKS_TEMPLATE.md` — Task DAG with parallel markers
  - Adapted from spec-kit tasks-template.md
  - Format: `[ID] [P?] [Story] Description`
  - Phases: Setup → Foundational → User Story N → Polish
  - Each phase has checkpoint
  - Explicit dependency section
  - Parallel execution strategy section
  - Each task includes exact file path

**Constraints for all three**:
- Must be usable by copying into `specs/001-feature-name/`
- No dependency on `specify` CLI
- Placeholders use `[BRACKETS]` for manual fill or AI fill
- Each template has a header pointing to its role in the lifecycle

**Acceptance**: Three new template files exist. Each has concrete placeholder content (not just section headers). The three files form a coherent lifecycle: SPEC → PLAN → TASKS.

---

### Phase 3: Supporting Spec Artifacts [P1] (5 tasks)

**Purpose**: Fill out the full spec artifact set.

- [ ] T006 [P] Create `templates/CONSTITUTION_TEMPLATE.md` — Project governance principles
  - Core principles section (5-7 slots)
  - Governance rules (quality gates, review requirements)
  - Version/ratification tracking
  - Adapted from spec-kit constitution-template

- [ ] T007 [P] Create `templates/CONTRACT_TEMPLATE.md` — API contract placeholder
  - OpenAPI 3.0 stub structure
  - Protobuf stub structure
  - Event schema stub
  - Instructions for which to use when

- [ ] T008 [P] Create `templates/DATA_MODEL_TEMPLATE.md` — Data model placeholder
  - Entity definitions with relationships
  - Schema stubs (SQL, NoSQL)
  - Migration notes

- [ ] T009 [P] Create `templates/QUICKSTART_TEMPLATE.md` — Manual + automated validation path
  - Prerequisites checklist
  - Step-by-step verification path
  - Expected outcomes at each step

- [ ] T010 [P] Create `templates/REPORT_TEMPLATE.md` — Implementation + review report
  - What was implemented (diff summary)
  - Decisions made (rationale)
  - Known issues / tech debt
  - Review agent findings
  - Verification evidence (test results, lint output)

**Acceptance**: 5 new template files. Each has concrete structure (not just a title and "fill this in").

---

### Phase 4: Blast Radius Policy [P0] (1 task)

**Purpose**: Create the risk classification system that determines agent autonomy. This is Harness's most important unique contribution.

- [ ] T011 Create `templates/BLAST_RADIUS_POLICY.md`

**Structure**:

```yaml
# Machine-parseable frontmatter (YAML block in markdown)
risk_levels:
  leaf:     # isolated, low-dependency changes
    examples: [isolated UI component, one-off script, adapter with existing contract]
    autonomy: high
    required_gates: [lint, unit_test]
  
  branch:   # feature-level, multi-file changes
    examples: [feature module, service layer, multi-file behavior]
    autonomy: medium
    required_gates: [spec, plan, tests, review_agent]
  
  core:     # domain/auth/storage/protocol changes
    examples: [domain model, auth, permission, storage schema, plugin protocol]
    autonomy: low
    required_gates: [human_spec_review, architecture_review, rollback_plan, security_review]
  
  infra:    # CI/CD/deployment/secrets changes
    examples: [CI/CD, deployment, database migration, secrets]
    autonomy: very_low
    required_gates: [dry_run, rollback_plan, explicit_human_approval]
```

**Human-readable section** after YAML:
- Explanation of each level
- How to classify a change (decision tree)
- How CLAUDE.md references this policy
- Example classifications for common scenarios

**Constraints**:
- YAML block must be parseable by a future hook script
- Must be referenced from CLAUDE.md (not duplicated)
- Keep under 80 lines total

**Acceptance**: File exists with 4 risk levels, each with examples/autonomy/gates. YAML is valid. A developer can read the decision tree and classify their change correctly.

---

### Phase 5: CLAUDE.md Refactor [P0] (1 task)

**Purpose**: Keep CLAUDE.md under 200 lines while adding references to new artifacts. Extract details to referenced files instead of inlining.

- [ ] T012 Refactor `templates/CLAUDE.md`

**Changes**:

1. **Keep**: ROLE section, Branch Strategy, TDD/BDD roles (core value)
2. **Keep**: Review Agent pipeline (core value)
3. **Add**: Reference to `CONSTITUTION_TEMPLATE.md` → "Read `.specify/memory/constitution.md` if exists"
4. **Add**: Reference to `BLAST_RADIUS_POLICY.md` → "Classify changes before implementing"
5. **Add**: Reference to spec artifacts → "Read `specs/xxx/spec.md` and `specs/xxx/plan.md` before TDD"
6. **Add**: Reference to `TASKS_TEMPLATE.md` → "Follow task DAG for parallel-safety"
7. **Remove/Extract**: Detailed BDD section → shorten to 3 lines + reference CONTRIBUTING.md
8. **Remove/Extract**: Documentation Writing details → shorten to reference docs/ structure
9. **Simplify**: Context & Prerequisites → "Read AGENTS.md, then project_index, then spec artifacts"

**Target structure** (~180 lines):
```
# System Prompt & Persona (15 lines)
## ROLE (10 lines)
## Context Loading (10 lines)

# Development Workflow (60 lines)
## Spec-First Development (15 lines) — NEW: reference spec artifacts
## Blast Radius Classification (10 lines) — NEW: reference policy
## TDD Strict Paradigms (35 lines) — KEPT: core value

# Quality Pipeline (50 lines)
## Verification (5 lines)
## Autonomous Review (20 lines) — KEPT
## Documentation (10 lines) — SIMPLIFIED
## Commit & Merge (15 lines) — KEPT

# Guard Rails (25 lines)
## Forbidden Actions (15 lines) — NEW: hard boundaries
## Error Recovery (10 lines) — NEW
```

**Acceptance**: `wc -l templates/CLAUDE.md` ≤ 200. All 10 references to new templates are correct. TDD role isolation rules are preserved verbatim. No content loss (details moved to referenced files, not deleted).

---

### Phase 6: AGENTS.md [P1] (1 task)

**Purpose**: Cross-agent compatibility for Codex, Cursor, Gemini, etc.

- [ ] T013 Create `templates/AGENTS.md`

**Structure** (~100 lines, table-of-contents pattern):
```markdown
# Project Overview (5 lines)
# Toolchain (15 lines) — make commands, test framework, lint tools
# Architecture (15 lines) — DDD layers, dependency rules
# Development Workflow (20 lines) — spec → plan → tasks → implement → verify
# Judgment Boundaries (15 lines) — what NOT to do (blast radius summary)
# Key References (10 lines) — pointers to docs/, specs/, templates/
```

**Constraints**:
- Must be valid for Claude Code, Codex CLI, Cursor, Gemini CLI
- No Claude-specific syntax (no @imports, no skills references)
- Cross-references CLAUDE.md for Claude-specific behavior
- Keep under 120 lines (AGENTS.md best practice: concise pointers, not encyclopedic content)

**Acceptance**: AGENTS.md exists at `templates/AGENTS.md`. Contains no Claude-specific syntax. A developer could give this file to Codex CLI or Cursor and get correct behavior. References CLAUDE.md for agent-specific details.

---

### Phase 7: Makefile + Pre-commit Upgrade [P1] (2 tasks)

- [ ] T014 [P] Upgrade `templates/Makefile`

**New/changed targets**:

| Target | Change |
|--------|--------|
| `init` | Add: check for Python 3.11+, uv, git. Install pre-commit. |
| `spec-init` | NEW: Create `specs/001-first-feature/` from templates (bash function) |
| `proto` | Keep as stub but with clearer placeholder comments |
| `lint` | Keep as stub |
| `test` | Keep as stub |
| `typecheck` | NEW: stub for type checking |
| `contract-test` | NEW: stub for contract tests |
| `security-scan` | NEW: call gitleaks if installed, else warn |
| `verify` | Upgrade: `up proto lint typecheck test contract-test security-scan` |
| `verify-ai` | NEW: check spec coverage, task completion, blast radius classification |

**Constraints**:
- All new targets must work as stubs (echo + placeholder)
- `spec-init` should be functional (create directory + copy templates)
- Total Makefile stays under 120 lines

- [ ] T015 [P] Upgrade `templates/.pre-commit-config.yaml`

**Additions**:
- Gitleaks (secret detection) — conditional on install
- Conventional commit message format — via `commitlint` or custom hook
- Domain test enforcement — make the existing `require-tests` hook actually block (not just warn)

**Acceptance**: `make init` installs all hooks. `make spec-init` creates a feature spec directory. `make verify` runs all stubs without error.

---

### Phase 8: CONTRIBUTING.md + ARCHITECTURE.md Update [P1] (2 tasks)

- [ ] T016 [P] Update `templates/CONTRIBUTING.md`

**Changes**:
- Add Phase 0.5: "Spec & Plan" between Contract and Domain TDD
- Reference blast radius policy in workflow
- Update Golden Path to: Define → Spec → Plan → Contract → Test → Implement → Verify
- Add section on spec artifact lifecycle
- Add blast radius classification step

- [ ] T017 [P] Fix `templates/ARCHITECTURE.md`

**Changes**:
- Remove "TODO: sync with guide" on line 10
- Add section on how DDD layers map to blast radius levels
- Add reference to blast radius policy

**Acceptance**: CONTRIBUTING.md workflow references spec artifacts. ARCHITECTURE.md has zero TODOs.

---

### Phase 9: Root Documentation Update [P2] (3 tasks)

- [ ] T018 [P] Rewrite `README.md`

**Changes**:
- Consistent "Harness" branding (remove "Neural-Grid" and "Framework")
- Update template inventory to include all 17 templates
- Update Golden Path to reflect spec-first workflow
- Add section on blast radius policy
- Fix typos ("ComprehensiveaREADEME")
- Update "Working With the Framework" section to reflect v2 workflow
- Add reference to Spec Kit as upstream inspiration (not dependency)

- [ ] T019 [P] Update `IMPLEMENTATION_GUIDE.md`

**Changes**:
- Add step for creating first spec (`make spec-init`)
- Add step for filling constitution template
- Update directory structure to show `specs/` directory
- Reference blast radius policy in architecture step

- [ ] T020 [P] Update `MANIFESTO.md`

**Changes**:
- Add principle: "Risk-Classified Autonomy" (blast radius)
- Update Quality Standards to mention spec-driven development
- Update Gatekeeper to mention `verify-ai`

**Acceptance**: README accurately describes all v2 templates. IMPLEMENTATION_GUIDE creates a working project when followed step-by-step. MANIFESTO reflects v2 principles.

---

### Phase 10: Eval Template [P2] (1 task)

**Purpose**: Template for capturing expected behavior and verification criteria. Not a full eval suite — just the artifact template.

- [ ] T021 Create `templates/EVAL_TEMPLATE.md`

**Structure**:
```markdown
## Product Evaluation
- User journey checks (manual)
- Edge case coverage
- API contract compliance
- Error message quality

## Harness Evaluation
- Was spec written before code?
- Were tasks generated?
- Did implementer modify tests?
- Was blast radius classified?
- Was review report produced?
```

**Acceptance**: Template exists with both product and harness evaluation sections. Each section has concrete checklist items.

---

## Execution Order

```
Phase 0 (T001)
    │
    ▼
Phase 1 (T002) ──────────────────────────────────────────────┐
    │                                                          │
    ▼                                                          │
Phase 2 (T003 [P], T004 [P], T005) ◄── T003/T004 parallel    │
    │                                                          │
    ▼                                                          │
Phase 3 (T006-T010, all [P]) ◄── all 5 parallel              │
    │                                                          │
    ▼                                                          │
Phase 4 (T011) + Phase 5 (T012) ◄── can parallel              │
    │                                                          │
    ▼                                                          │
Phase 6 (T013) + Phase 7 (T014 [P], T015 [P]) ◄── parallel    │
    │                                                          │
    ▼                                                          │
Phase 8 (T016 [P], T017 [P]) ◄── parallel                     │
    │                                                          │
    ▼                                                          │
Phase 9 (T018 [P], T019 [P], T020 [P]) ◄── all 3 parallel     │
    │                                                          │
    ▼                                                          │
Phase 10 (T021)
    │
    ▼
DONE
```

## Parallel Opportunities

| Group | Tasks | Why Parallel |
|-------|-------|-------------|
| 2A | T003, T004 | Different files, no cross-references |
| 3A | T006, T007, T008, T009, T010 | All independent template files |
| 4+5 | T011, T012 | Blast radius is referenced by CLAUDE.md but doesn't block writing it |
| 6+7 | T013, T014, T015 | AGENTS.md, Makefile, pre-commit are independent |
| 8A | T016, T017 | CONTRIBUTING.md and ARCHITECTURE.md updates are independent |
| 9A | T018, T019, T020 | README, IMPLEMENTATION_GUIDE, MANIFESTO are independent |

## Out of Scope (Explicitly Deferred)

These are acknowledged needs but NOT part of v2:

| Item | Why Deferred |
|------|-------------|
| Custom eval suite with automated runners | Needs real project to test against; template is enough for v2 |
| Context bundle generator | Needs real specs/ content to optimize; manual references sufficient |
| Claude Code hooks (PreToolUse) | Requires Python scripts that won't work in freshly copied templates; document the hooks in CLAUDE.md as recommendations for users to implement |
| Multi-agent orchestration | Premature; AGENTS.md covers compatibility |
| Security scanning beyond gitleaks | Use existing tools; don't reinvent |
| Spec drift detection | Needs CI integration; template-only can't do this |
| `specify` CLI integration | Chose Route C explicitly; no CLI dependency |
| CLI productization (`harness` command) | v2 stays as template repo; CLI is v3 |

## Acceptance Criteria (Overall)

- [ ] `ls templates/` shows 17 files (6 existing + 11 new)
- [ ] `wc -l templates/CLAUDE.md` ≤ 200
- [ ] PRD_TEMPLATE.md has all 9 sections with concrete placeholders
- [ ] BLAST_RADIUS_POLICY.md has 4 risk levels with YAML parseable block
- [ ] AGENTS.md has no Claude-specific syntax
- [ ] Makefile has `spec-init` target that creates a feature directory
- [ ] Zero references to "Neural-Grid" in any file
- [ ] Zero TODOs in any template file
- [ ] All templates have consistent header format (purpose, input, output)
- [ ] README accurately describes all templates and their relationships

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| CLAUDE.md exceeds 200 lines | Medium | High — models stop following | Strict line budget per section |
| Templates too opinionated for general use | Medium | Medium — users won't adopt | Keep placeholders flexible, add "omit if not applicable" guidance |
| Manual Spec Kit tracking drifts | High | Low — templates become outdated | Add version pin comment in each adapted template header |
| Blast radius policy too abstract | Medium | High — won't be used | Include 10+ concrete classification examples |
| AGENTS.md conflicts with CLAUDE.md | Low | Medium — conflicting instructions | AGENTS.md defers to CLAUDE.md for Claude-specific behavior |
