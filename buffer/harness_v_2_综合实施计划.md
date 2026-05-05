# Harness v2 综合实施计划

> **定位**：Spec-Governed Agentic Engineering Harness  
> **路线**：Template-first, policy-aware, minimally executable  
> **状态**：Draft  
> **目标版本**：v2.0.0  
> **核心判断**：v2 先升级为可复制、可执行、可被 agent 理解的模板仓库；v3 再演进为完整 CLI/runtime。  

---

## 0. Executive Summary

Harness v1 已经解决了一个很重要的问题：**如何让 AI 编程从随意 prompt 变成有纪律的工程流程**。它的优势不是“多一个 CLAUDE.md”，而是已经形成了 Contract First、Strict DDD、TDD/BDD、Review Agent、Makefile Gatekeeper 这一整套工程纪律。

但 Harness v1 仍然主要是一个 **personal discipline system**。它能指导 agent，但不能充分约束 agent；它有流程，但还没有 feature-level artifact lifecycle；它有工程理念，但缺少明确的 blast radius policy；它有 Makefile，但缺少最小可执行的 AI-specific verification。

Harness v2 的目标不是把项目做成沉重的 spec-kit wrapper，也不是停留在文档模板合集，而是成为：

```text
Template-first, policy-aware, minimally executable agentic engineering harness.
```

也就是说：

1. **Template-first**：v2 仍然是模板仓库。复制到任何项目里即可使用，不强依赖某个 CLI 或 agent 平台。
2. **Policy-aware**：引入 blast radius、role policy、spec lifecycle、eval/report 等治理结构。
3. **Minimally executable**：至少让 `make spec-init`、`make verify`、`make verify-ai`、`make classify-risk` 真的可运行。

---

## 1. Strategy Decision

### 1.1 Adopt Route C: Pure Template Upgrade

Harness v2 不直接 wrap spec-kit，也不依赖 `specify` CLI。

正确叙事是：

```text
Harness is spec-kit inspired, but agent-governance first.
Spec Kit organizes feature specs.
Harness governs agent behavior, risk, roles, context, and verification.
```

也就是说，Harness v2 可以吸收 Spec Kit 的 artifact lifecycle，但不要把自己定义成 spec-kit wrapper。

### 1.2 Absorb Anthropic/production-vibe-coding lessons

Anthropic 演讲和相关 best practices 对 Harness 最重要的启发不是“更会 vibe coding”，而是：

```text
Human defines architecture and verification boundaries.
Agent executes within a classified blast radius.
System behavior is validated by tests/evals, not by reading every line of generated code.
```

因此 Harness v2 必须新增三个核心机制：

1. **Blast Radius Policy**：不是所有代码都能让 agent 自主改。
2. **Feature Artifact Lifecycle**：每个 feature 都有 spec/plan/tasks/eval/report 闭环。
3. **AI Verification Gate**：除了 `make verify`，还要有 `make verify-ai` 检查 agent workflow 是否合规。

### 1.3 Version boundary

| Version | Scope | Description |
|---|---|---|
| v2.0 | Template-first + minimal executable gates | 当前目标 |
| v2.5 | Add lightweight hooks and policy scripts | 后续增强 |
| v3.0 | Full CLI/runtime/eval runner/context bundle generator | 产品化版本 |

---

## 2. Harness Unique Value

Harness v2 不应该试图复制 Spec Kit。它的独特价值应当非常明确：

### 2.1 DDD Enforcement

Harness 强制区分：

```text
internal/domain/           Pure business logic
internal/infrastructure/   DB / HTTP / RPC / external services
api/                       Contracts
cmd/                       Application entry points
```

核心原则：

```text
domain depends on nothing
infrastructure depends on domain
never reverse
```

### 2.2 TDD Role Isolation

Harness 强制把 TDD 分成角色：

```text
TDD-RED       writes failing tests only
TDD-GREEN     writes minimal implementation, never modifies tests
TDD-REFACTOR  refactors under green tests, never modifies tests
REVIEWER      reviews only, does not implement
HUMAN         approves architecture/core/infra changes
```

这是 Harness 区别于普通 agent prompt 的关键。

### 2.3 Blast Radius Policy

Harness 必须按风险等级决定 agent autonomy：

```text
leaf    high autonomy
branch  medium autonomy
core    low autonomy
infra   very low autonomy
```

这比“让 AI 生成代码”更重要。它定义了：**agent 到底能改什么、改到什么程度、需要过哪些 gate。**

### 2.4 Makefile Gatekeeper

Agent 不应该自己猜命令。所有项目入口必须通过 Makefile 暴露：

```bash
make init
make spec-init FEATURE=001-feature-name
make lint
make test
make typecheck
make contract-test
make security-scan
make verify
make verify-ai
make classify-risk
```

---

## 3. Target Repository Structure

Harness v2 的目标结构：

```text
Harness/
├── README.md
├── MANIFESTO.md
├── IMPLEMENTATION_GUIDE.md
├── CHANGELOG.md
├── VERSION
│
├── templates/
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── PRD_TEMPLATE.md
│   ├── SPEC_TEMPLATE.md
│   ├── PLAN_TEMPLATE.md
│   ├── TASKS_TEMPLATE.md
│   ├── CONSTITUTION_TEMPLATE.md
│   ├── BLAST_RADIUS_POLICY.md
│   ├── ROLE_POLICY.md
│   ├── CONTRACT_TEMPLATE.md
│   ├── DATA_MODEL_TEMPLATE.md
│   ├── QUICKSTART_TEMPLATE.md
│   ├── EVAL_TEMPLATE.md
│   ├── REPORT_TEMPLATE.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   ├── Makefile
│   └── .pre-commit-config.yaml
│
├── scripts/
│   ├── spec-init.sh
│   ├── classify-risk.sh
│   ├── verify-ai.sh
│   └── check-template-integrity.sh
│
└── examples/
    └── minimal-project/
        ├── AGENTS.md
        ├── CLAUDE.md
        ├── Makefile
        └── specs/
            └── 001-example-feature/
                ├── spec.md
                ├── plan.md
                ├── tasks.md
                ├── eval.md
                └── report.md
```

说明：

- `templates/` 是 v2 的核心资产。
- `scripts/` 只放最小可运行工具，不做完整 runtime。
- `examples/minimal-project/` 用来证明模板不是空谈。

---

## 4. Feature Artifact Lifecycle

Harness v2 引入标准 feature directory：

```text
specs/001-feature-name/
├── spec.md
├── plan.md
├── research.md          # optional in v2
├── contracts/           # optional in v2
├── data-model.md        # optional in v2
├── quickstart.md        # optional in v2
├── tasks.md
├── eval.md
└── report.md
```

v2 的最小必需文件：

```text
spec.md
plan.md
tasks.md
eval.md
report.md
```

完整生命周期：

```text
PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT → REVIEW
```

### 4.1 PRD vs SPEC

PRD 是产品级入口：

```text
What are we building?
Why does it matter?
Who is it for?
What is explicitly out of scope?
```

SPEC 是 feature-level 可执行需求：

```text
User stories
Functional requirements
Acceptance scenarios
Success criteria
Assumptions
Clarification markers
```

### 4.2 PLAN

PLAN 负责技术实现：

```text
architecture
technical context
DDD layer impact
contract impact
risk classification
complexity tracking
```

### 4.3 TASKS

TASKS 是 agent 调度输入，不是普通 TODO：

```text
T001 [P] [US1] Create contract test in tests/contract/...
T002     [US1] Implement domain entity in internal/domain/...
T003 [P] [US2] Add adapter in internal/infrastructure/...
```

每个 task 必须包含：

```text
ID
parallel marker [P] if safe
user story reference
exact file path
checkpoint
```

### 4.4 EVAL

EVAL 验证两个层面：

```text
Product Eval: product behavior meets requirements
Harness Eval: agent followed process and policies
```

### 4.5 REPORT

REPORT 是实现结束后的证据包：

```text
what changed
which files were touched
risk classification
test results
known issues
review summary
rollback plan
```

---

## 5. Blast Radius Policy

新增 `templates/BLAST_RADIUS_POLICY.md`。

它应采用 markdown + YAML frontmatter 格式，既能给人读，也能给未来脚本解析。

```markdown
---
risk_levels:
  leaf:
    description: "Isolated, low-dependency changes"
    autonomy: high
    examples:
      - documentation
      - isolated UI component
      - one-off script
      - test file
      - adapter with existing contract
    required_gates:
      - lint
      - unit_test

  branch:
    description: "Feature-level or multi-file behavior change"
    autonomy: medium
    examples:
      - feature module
      - service layer
      - new endpoint
      - multi-file behavior change
    required_gates:
      - spec
      - plan
      - tests
      - review_agent

  core:
    description: "Domain, auth, storage, permissions, protocol"
    autonomy: low
    examples:
      - domain model
      - auth logic
      - permission system
      - storage schema
      - plugin protocol
      - scheduler
    required_gates:
      - human_spec_review
      - architecture_review
      - rollback_plan
      - security_review

  infra:
    description: "Deployment, CI/CD, secrets, migrations"
    autonomy: very_low
    examples:
      - CI/CD pipeline
      - deployment config
      - database migration
      - secrets management
    required_gates:
      - dry_run
      - explicit_human_approval
      - rollback_plan
      - security_review
---
```

Human-readable section 需要包含：

1. 四个等级解释。
2. 分类决策树。
3. 10 个具体例子。
4. 多文件改动时采用最高风险等级。
5. CLAUDE.md / AGENTS.md 如何引用本 policy。

### 5.1 Classification decision tree

```text
1. Does this touch deployment, CI, secrets, or migration execution?
   → infra

2. Does this touch domain model, auth, permissions, schema, plugin protocol, scheduler?
   → core

3. Does this change multi-file behavior, service layer, endpoint, or feature module?
   → branch

4. Is this docs, tests, one-off script, isolated component, or adapter against existing contract?
   → leaf

5. If uncertain:
   → choose the higher risk level
```

### 5.2 Example classifications

| Change | Level | Reason |
|---|---|---|
| Fix README typo | leaf | docs only |
| Add isolated CLI helper script | leaf | low dependency |
| Add contract test | leaf | test-only |
| Add new REST endpoint | branch | externally visible behavior |
| Add service method across 3 files | branch | feature-level behavior |
| Change domain entity field | core | affects data model |
| Change auth middleware | core | permission/security impact |
| Add database migration | core/infra | schema + deployment risk |
| Modify GitHub Actions deploy job | infra | deployment risk |
| Add `.env` handling | infra | secrets/config risk |

---

## 6. Role Policy

新增 `templates/ROLE_POLICY.md`。

核心角色：

```text
TDD-RED
TDD-GREEN
TDD-REFACTOR
REVIEWER
HUMAN
```

### 6.1 TDD-RED

Allowed:

```text
tests/**
specs/**/spec.md
specs/**/eval.md
```

Forbidden:

```text
implementation files
domain logic
infrastructure logic
cmd entrypoints
```

Obligation:

```text
write failing tests
confirm tests fail before handoff
never implement
```

### 6.2 TDD-GREEN

Allowed:

```text
internal/domain/**
internal/infrastructure/**
cmd/**
```

Forbidden:

```text
tests/**
```

Obligation:

```text
minimal implementation
never lower test requirement
if test is impossible, stop and write bug report
```

### 6.3 TDD-REFACTOR

Allowed:

```text
implementation files
```

Forbidden:

```text
tests/**
```

Obligation:

```text
all tests must remain green
improve structure without changing behavior
```

### 6.4 REVIEWER

Allowed:

```text
docs/reports/reviews/**
specs/**/report.md
```

Forbidden:

```text
implementation changes
test changes
```

Obligation:

```text
review spec alignment
review risk classification
review test coverage
review architecture violations
review security concerns
```

### 6.5 HUMAN

Human is responsible for:

```text
architecture decisions
core changes approval
infra changes approval
scope clarification
tradeoff decisions
```

---

## 7. AGENTS.md Design

新增 `templates/AGENTS.md`。

AGENTS.md 是跨 agent 的通用说明，不包含 Claude-specific 语法。它应该短、硬、可路由。

目标结构：

```markdown
# AGENTS.md

## Project Overview

## Setup

## Development Commands

## Architecture Rules

## Spec-Driven Workflow

## Blast Radius Policy

## Role Boundaries

## Before Commit

## Key References
```

### 7.1 Required commands table

```markdown
| Command | Purpose |
|---|---|
| `make init` | Initialize project |
| `make spec-init FEATURE=001-name` | Create feature spec directory |
| `make lint` | Run lint |
| `make test` | Run tests |
| `make typecheck` | Run type checks |
| `make contract-test` | Run contract tests |
| `make security-scan` | Scan for basic security issues |
| `make verify` | Product verification |
| `make verify-ai` | Harness/process verification |
| `make classify-risk` | Classify current diff risk |
```

### 7.2 Required agent rules

AGENTS.md 必须明确：

```text
1. Do not implement before reading the active spec.
2. Do not modify tests during GREEN/REFACTOR phase.
3. Classify blast radius before implementation.
4. Core/infra changes require human approval.
5. Every feature must end with eval.md and report.md evidence.
6. Run make verify and make verify-ai before commit.
```

---

## 8. CLAUDE.md Refactor

CLAUDE.md 需要保留 Harness 的核心优势，但必须减少臃肿。

目标：`wc -l templates/CLAUDE.md <= 200`。

### 8.1 Target structure

```markdown
# CLAUDE.md

## Persona

## Context Loading Order
1. Read AGENTS.md
2. Read active specs/xxx/spec.md
3. Read specs/xxx/plan.md
4. Read specs/xxx/tasks.md
5. Read BLAST_RADIUS_POLICY.md
6. Read ROLE_POLICY.md

## Development Workflow
- Spec-first
- Plan-first for branch/core/infra
- TDD role isolation
- BDD for flows

## Blast Radius Rules
- leaf / branch / core / infra summary
- when uncertain, escalate risk

## TDD Roles
- RED
- GREEN
- REFACTOR
- REVIEWER

## Verification
- make verify
- make verify-ai
- make classify-risk

## Forbidden Actions
- modify tests during GREEN
- bypass failing tests
- touch core without spec/plan
- touch infra without rollback plan
- introduce secrets

## Error Recovery
- stop and report ambiguity
- write bug report if tests impossible
- ask human for core/infra decision
```

### 8.2 Design principle

CLAUDE.md 不再承载所有细节，而是作为 routing layer。

```text
CLAUDE.md tells the agent what to read and what not to do.
Policy files contain the detailed rules.
Spec artifacts contain the feature-specific truth.
```

---

## 9. Template Inventory

### 9.1 New templates

| File | Priority | Purpose |
|---|---:|---|
| `SPEC_TEMPLATE.md` | P0 | Feature-level what/why/acceptance |
| `PLAN_TEMPLATE.md` | P0 | Technical implementation plan |
| `TASKS_TEMPLATE.md` | P0 | Task DAG for agent execution |
| `BLAST_RADIUS_POLICY.md` | P0 | Risk-classified autonomy policy |
| `ROLE_POLICY.md` | P0 | TDD role boundaries |
| `AGENTS.md` | P0 | Cross-agent standard |
| `CONSTITUTION_TEMPLATE.md` | P1 | Project principles/governance |
| `CONTRACT_TEMPLATE.md` | P1 | OpenAPI/protobuf/event contract placeholder |
| `DATA_MODEL_TEMPLATE.md` | P1 | Entity/schema/migration notes |
| `QUICKSTART_TEMPLATE.md` | P1 | Manual + automated validation path |
| `EVAL_TEMPLATE.md` | P1 | Product + harness evaluation |
| `REPORT_TEMPLATE.md` | P1 | Implementation and review evidence |

### 9.2 Modified templates

| File | Priority | Required change |
|---|---:|---|
| `PRD_TEMPLATE.md` | P0 | Add user stories, FR/NFR, success criteria, ambiguities, out-of-scope |
| `CLAUDE.md` | P0 | Refactor under 200 lines; reference policies/spec artifacts |
| `Makefile` | P0 | Add spec-init, verify-ai, classify-risk, security-scan |
| `CONTRIBUTING.md` | P1 | Update Golden Path to spec-first workflow |
| `ARCHITECTURE.md` | P1 | Remove TODOs; map DDD layers to blast radius |
| `.pre-commit-config.yaml` | P1 | Add basic secret scan / commit conventions / test enforcement |

### 9.3 Root docs

| File | Priority | Required change |
|---|---:|---|
| `README.md` | P0 | Rewrite for v2; show workflow and template inventory |
| `IMPLEMENTATION_GUIDE.md` | P1 | Add spec-init and spec lifecycle adoption path |
| `MANIFESTO.md` | P1 | Add Risk-Classified Autonomy principle |
| `CHANGELOG.md` | P2 | Add v2 release notes |
| `VERSION` | P2 | Set `2.0.0` |

---

## 10. Makefile v2

`templates/Makefile` 必须从“说明型”变成“最小可执行”。

### 10.1 Required targets

```makefile
.PHONY: init spec-init up down proto lint typecheck test contract-test security-scan verify verify-ai classify-risk

init:
	@echo "Initializing project..."
	@command -v git >/dev/null || (echo "git not found" && exit 1)
	@command -v python3 >/dev/null || echo "python3 not found; install if needed"
	@echo "Install dependencies here."

spec-init:
	@test -n "$(FEATURE)" || (echo "Usage: make spec-init FEATURE=001-feature-name" && exit 1)
	@mkdir -p specs/$(FEATURE)
	@cp templates/SPEC_TEMPLATE.md specs/$(FEATURE)/spec.md
	@cp templates/PLAN_TEMPLATE.md specs/$(FEATURE)/plan.md
	@cp templates/TASKS_TEMPLATE.md specs/$(FEATURE)/tasks.md
	@cp templates/EVAL_TEMPLATE.md specs/$(FEATURE)/eval.md
	@cp templates/REPORT_TEMPLATE.md specs/$(FEATURE)/report.md
	@echo "Created specs/$(FEATURE)/"

up:
	@echo "Start infrastructure here."

down:
	@echo "Stop infrastructure here."

proto:
	@echo "Generate contract code here."

lint:
	@echo "Run linters here."

typecheck:
	@echo "Run type checks here."

test:
	@echo "Run tests here."

contract-test:
	@echo "Run contract tests here."

security-scan:
	@echo "Running basic security scan..."
	@if command -v gitleaks >/dev/null; then gitleaks detect --no-git -v; else echo "gitleaks not installed; skipping"; fi

verify: proto lint typecheck test contract-test security-scan
	@echo "Product verification passed."

verify-ai:
	@bash scripts/verify-ai.sh

classify-risk:
	@bash scripts/classify-risk.sh
```

### 10.2 Key principle

All targets must be safe as stubs. A fresh cloned template should not fail because a specific project language is missing.

---

## 11. Minimal Scripts

v2 只做 3 个脚本，不做完整 CLI。

```text
scripts/spec-init.sh          optional if Makefile handles it directly
scripts/classify-risk.sh
scripts/verify-ai.sh
```

### 11.1 `scripts/classify-risk.sh`

Minimal path-based classifier.

Pseudo logic:

```bash
changed_files=$(git diff --name-only HEAD 2>/dev/null || git diff --name-only)

risk=leaf

for file in $changed_files; do
  case "$file" in
    .github/*|Dockerfile*|docker-compose*|*.env*) risk=infra ;;
    *auth*|*permission*|*migration*|*schema*|internal/domain/*) risk=max(core) ;;
    internal/infrastructure/*|cmd/*|api/*) risk=max(branch) ;;
    docs/*|*.md|tests/*|scripts/*|templates/*) risk=max(leaf) ;;
    *) risk=max(branch) ;;
  esac
done

echo "Overall risk: $risk"
```

Do not implement complex YAML parsing in v2.

### 11.2 `scripts/verify-ai.sh`

Minimal checks:

```text
1. AGENTS.md exists or templates/AGENTS.md exists
2. CLAUDE.md exists or templates/CLAUDE.md exists
3. PRD_TEMPLATE.md exists
4. SPEC_TEMPLATE.md / PLAN_TEMPLATE.md / TASKS_TEMPLATE.md exist
5. BLAST_RADIUS_POLICY.md exists
6. ROLE_POLICY.md exists
7. EVAL_TEMPLATE.md and REPORT_TEMPLATE.md exist
8. CLAUDE.md is <= 200 lines
9. No Neural-Grid references remain
10. No TODO remains in templates
```

Optional checks:

```text
1. If specs/* exists, each feature should have spec.md / plan.md / tasks.md / eval.md / report.md
2. If git diff touches core/infra paths, print warning requiring human review
```

### 11.3 `scripts/check-template-integrity.sh`

Can be same as `verify-ai.sh` or called by it.

---

## 12. PRD_TEMPLATE Upgrade

`templates/PRD_TEMPLATE.md` 必须从技术骨架升级成产品 + spec 入口。

Required sections:

```markdown
# Product Requirement Document: [Project Name]

## 1. Vision & Scope
### 1.1 Core Definition
- What:
- Input:
- Output:
- Core Logic:

### 1.2 MVP Goals

### 1.3 Out of Scope

## 2. User Stories
### US-001: [Title] (Priority: P1)
Description:
Why this priority:
Independent Test:
Acceptance Scenarios:
- Given ..., When ..., Then ...

## 3. Functional Requirements
- FR-001:
- FR-002:
- FR-003: [NEEDS CLARIFICATION: ...]

## 4. Non-Functional Requirements
### Performance
### Security
### Privacy
### Observability
### Compatibility

## 5. Key Entities

## 6. System Architecture
### Core Pattern
### Tech Stack

## 7. Interfaces
### Contract
### Data Schema

## 8. Success Criteria
- SC-001:
- SC-002:

## 9. Assumptions & Ambiguities
### Assumptions
### Ambiguities
- [NEEDS CLARIFICATION: ...]

## 10. Hard Truths / Risks
```

Rules:

```text
- Every user story must be independently testable.
- Every ambiguity must be marked with [NEEDS CLARIFICATION].
- Agent must not guess values marked [NEEDS CLARIFICATION].
- Out of Scope is mandatory.
```

---

## 13. SPEC_TEMPLATE

`SPEC_TEMPLATE.md` is feature-level, not project-level.

Required sections:

```markdown
# Feature Spec: [Feature Name]

## Metadata
Feature ID:
Branch:
Status:
Owner:
Date:

## Summary

## User Scenarios
### US-001: [Title]
Priority:
Independent Test:
Acceptance Scenarios:
- Given ..., When ..., Then ...

## Requirements
### Functional Requirements
### Non-Functional Requirements

## Success Criteria

## Assumptions

## Clarifications
- [NEEDS CLARIFICATION: ...]

## Out of Scope

## Risk Notes
```

Acceptance:

```text
- Every spec must have at least one user story.
- Every P1 story must have independent test instructions.
- Every feature must define success criteria.
```

---

## 14. PLAN_TEMPLATE

`PLAN_TEMPLATE.md` describes how the feature will be implemented.

Required sections:

```markdown
# Implementation Plan: [Feature Name]

## Inputs
- spec.md:
- PRD:
- related contracts:

## Technical Context
Language:
Framework:
Storage:
External dependencies:

## Architecture Impact
### DDD Layer Impact
- domain:
- infrastructure:
- api:
- cmd:

### Contract Impact

### Data Model Impact

## Blast Radius Classification
Level: leaf / branch / core / infra
Reason:
Required gates:

## Constitution Check
- Contract-first:
- DDD direction:
- TDD/BDD:
- Observability:
- Security:

## Implementation Strategy

## Test Strategy

## Rollback Plan

## Complexity Tracking
```

Rules:

```text
- core/infra plan must include rollback plan.
- branch/core/infra must include test strategy.
- core/infra requires human review marker.
```

---

## 15. TASKS_TEMPLATE

`TASKS_TEMPLATE.md` is a task DAG.

Required format:

```markdown
# Tasks: [Feature Name]

## Format
- [ ] T001 [P] [US1] Description with exact file path

## Phase 1: Setup
- [ ] T001 Create directory ...

## Phase 2: Tests First
- [ ] T002 [US1] Create failing test in tests/...

## Phase 3: Implementation
- [ ] T003 [US1] Implement domain logic in internal/domain/...

## Phase 4: Integration
- [ ] T004 [US1] Wire infrastructure in internal/infrastructure/...

## Phase 5: Verification
- [ ] T005 Run make verify
- [ ] T006 Run make verify-ai

## Dependencies

## Parallel Execution Plan

## Checkpoints
```

Rules:

```text
- [P] means safe to run in parallel.
- [P] tasks must not modify the same file.
- Every implementation task should map to a story or requirement.
- Every task must name exact file paths.
```

---

## 16. EVAL_TEMPLATE

`EVAL_TEMPLATE.md` validates both product and harness behavior.

Required sections:

```markdown
# Eval: [Feature Name]

## Product Evaluation
### Acceptance Scenario Validation
| Scenario | Expected | Actual | Pass? | Evidence |

### Functional Requirement Validation
| FR | Expected | Actual | Pass? | Evidence |

### Edge Cases

### Error Handling

### Non-Functional Checks
- Performance:
- Security:
- Observability:

## Harness Evaluation
| Check | Expected | Actual | Pass? |
|---|---|---|---|
| Spec existed before implementation | yes | | |
| Plan existed before implementation | yes | | |
| Tasks generated | yes | | |
| Blast radius classified | yes | | |
| Tests not modified during GREEN | yes | | |
| Review report produced | yes | | |
| make verify passed | yes | | |
| make verify-ai passed | yes | | |

## Verdict
- [ ] Ready to merge
- [ ] Needs changes
```

---

## 17. REPORT_TEMPLATE

`REPORT_TEMPLATE.md` is the implementation evidence package.

Required sections:

```markdown
# Implementation Report: [Feature Name]

## Summary

## Files Changed
| File | Change | Risk Level | Reason |

## Architecture Decisions

## Tests
| Suite | Result | Evidence |

## Verification
- make verify:
- make verify-ai:
- classify-risk:

## Review Summary

## Known Issues

## Rollback Plan

## Final Verdict
```

Rules:

```text
- core/infra changes must include rollback plan.
- report must include risk classification.
- report must include verification evidence.
```

---

## 18. CONTRIBUTING.md Upgrade

Golden Path 更新为：

```text
0. Read AGENTS.md / CLAUDE.md
1. Define PRD
2. Create feature spec directory
3. Fill spec.md
4. Fill plan.md
5. Classify blast radius
6. Generate tasks.md
7. Write tests first
8. Implement according to role
9. Run make verify
10. Run make verify-ai
11. Fill eval.md
12. Fill report.md
13. Review
14. Merge
```

CONTRIBUTING.md 必须新增：

```text
- feature artifact lifecycle
- blast radius classification step
- role-based TDD workflow
- review requirements for core/infra
- required Makefile commands
```

---

## 19. ARCHITECTURE.md Upgrade

ARCHITECTURE.md 必须清理所有 TODO，并新增：

### 19.1 DDD to blast radius mapping

| Layer | Risk Level | Reason |
|---|---|---|
| docs | leaf | no runtime behavior |
| tests | leaf | verification only |
| scripts | leaf/branch | depends on usage |
| api/contracts | branch/core | external behavior |
| internal/infrastructure | branch | service behavior |
| internal/domain | core | business invariant |
| auth/permissions | core | security boundary |
| migrations/schema | core/infra | data/deployment boundary |
| CI/CD/deploy | infra | production execution |

### 19.2 Dependency direction

```text
domain → nothing
infrastructure → domain
cmd → domain + infrastructure
api → generated boundary
```

---

## 20. README Upgrade

README must communicate v2 in one minute.

Required sections:

```markdown
# Harness

## What is Harness?

## Why not just use Spec Kit / CLAUDE.md / AGENTS.md?

## Core Ideas
- Spec-governed development
- DDD enforcement
- TDD role isolation
- Blast-radius-based autonomy
- Makefile as gatekeeper

## Quick Start
make init
make spec-init FEATURE=001-first-feature

## Workflow
PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT

## Template Inventory

## Risk Levels
leaf / branch / core / infra

## Agent Compatibility
Claude Code / Codex / Cursor / Gemini / Windsurf

## Roadmap
v2 template-first
v2.5 hooks
v3 CLI/runtime
```

README must remove all old inconsistent branding.

---

## 21. Implementation Phases

### Phase 0: Identity Cleanup [P0]

**Goal**: 清理历史命名和明显不一致。

Tasks:

```text
T001 Remove all "Neural-Grid" references.
T002 Rename inconsistent "Framework" wording to "Harness" where appropriate.
T003 Fix typos such as "ComprehensiveaREADEME".
T004 Add VERSION = 2.0.0.
T005 Create CHANGELOG.md.
```

Acceptance:

```text
grep -R "Neural-Grid" . returns zero relevant hits.
README title is Harness.
MANIFESTO and IMPLEMENTATION_GUIDE use consistent naming.
```

---

### Phase 1: Core Spec Templates [P0]

**Goal**: 建立 feature-level artifact lifecycle。

Tasks:

```text
T006 Rewrite PRD_TEMPLATE.md.
T007 Create SPEC_TEMPLATE.md.
T008 Create PLAN_TEMPLATE.md.
T009 Create TASKS_TEMPLATE.md.
```

Acceptance:

```text
PRD has user stories, FR/NFR, success criteria, ambiguities, out-of-scope.
SPEC/PLAN/TASKS form a coherent lifecycle.
TASKS uses ID + [P] + [US] + exact file path format.
```

Parallel:

```text
T007 and T008 can run in parallel.
T009 should run after T007/T008.
```

---

### Phase 2: Governance Templates [P0]

**Goal**: 把 agent 自主度和角色边界写成明确 policy。

Tasks:

```text
T010 Create BLAST_RADIUS_POLICY.md.
T011 Create ROLE_POLICY.md.
T012 Create AGENTS.md.
T013 Refactor CLAUDE.md under 200 lines.
```

Acceptance:

```text
BLAST_RADIUS_POLICY has 4 levels and machine-readable frontmatter.
ROLE_POLICY defines RED/GREEN/REFACTOR/REVIEWER/HUMAN.
AGENTS.md contains no Claude-specific syntax.
CLAUDE.md <= 200 lines and references policy/spec artifacts.
```

Parallel:

```text
T010 and T011 can run in parallel.
T012 depends on T010/T011.
T013 depends on T010/T011/T012.
```

---

### Phase 3: Eval and Report Artifacts [P1]

**Goal**: 让每个 feature 有验证和复盘证据。

Tasks:

```text
T014 Create EVAL_TEMPLATE.md.
T015 Create REPORT_TEMPLATE.md.
T016 Create QUICKSTART_TEMPLATE.md.
T017 Create CONTRACT_TEMPLATE.md.
T018 Create DATA_MODEL_TEMPLATE.md.
T019 Create CONSTITUTION_TEMPLATE.md.
```

Acceptance:

```text
EVAL_TEMPLATE includes Product Eval and Harness Eval.
REPORT_TEMPLATE includes files changed, risk, tests, verification, rollback.
QUICKSTART_TEMPLATE includes manual + automated validation path.
CONTRACT/DATA_MODEL templates are concrete enough to fill.
CONSTITUTION_TEMPLATE captures project principles and governance rules.
```

Parallel:

```text
All tasks in Phase 3 can run in parallel.
```

---

### Phase 4: Minimal Executable Layer [P0]

**Goal**: v2 不是纯文档，必须有最小可运行入口。

Tasks:

```text
T020 Upgrade templates/Makefile.
T021 Create scripts/classify-risk.sh.
T022 Create scripts/verify-ai.sh.
T023 Add spec-init functionality.
T024 Upgrade .pre-commit-config.yaml.
```

Acceptance:

```text
make spec-init FEATURE=001-example works.
make verify runs stubs safely.
make verify-ai checks template integrity.
make classify-risk outputs leaf/branch/core/infra.
Fresh clone does not fail because project-specific dependencies are missing.
```

---

### Phase 5: Documentation Sync [P1]

**Goal**: 根文档和模板文档一致。

Tasks:

```text
T025 Rewrite README.md.
T026 Update IMPLEMENTATION_GUIDE.md.
T027 Update MANIFESTO.md.
T028 Update CONTRIBUTING.md.
T029 Update ARCHITECTURE.md.
```

Acceptance:

```text
README explains v2 in one minute.
IMPLEMENTATION_GUIDE can create a working project step-by-step.
MANIFESTO includes Risk-Classified Autonomy.
CONTRIBUTING uses updated Golden Path.
ARCHITECTURE has no TODO and maps DDD to blast radius.
```

---

### Phase 6: Example Project [P1]

**Goal**: 证明 Harness v2 模板可用。

Tasks:

```text
T030 Create examples/minimal-project/.
T031 Add example AGENTS.md / CLAUDE.md / Makefile.
T032 Add specs/001-example-feature/.
T033 Fill spec.md / plan.md / tasks.md / eval.md / report.md with concrete toy feature.
T034 Run make verify-ai on example project.
```

Acceptance:

```text
A new user can inspect examples/minimal-project and understand how Harness is used.
Example feature is not empty placeholder.
verify-ai passes on example.
```

---

## 22. Execution Order

```text
Phase 0: Identity Cleanup
    ↓
Phase 1: Core Spec Templates
    ↓
Phase 2: Governance Templates
    ↓
Phase 4: Minimal Executable Layer
    ↓
Phase 3: Eval/Report/Supporting Artifacts
    ↓
Phase 5: Documentation Sync
    ↓
Phase 6: Example Project
```

Why Phase 4 before Phase 3?

Because executable commands shape the templates. If `make spec-init` and `make verify-ai` are designed too late, templates may drift into pure documentation.

---

## 23. Parallel Execution Plan

| Group | Tasks | Why parallel-safe |
|---|---|---|
| A | T007 SPEC, T008 PLAN | different files |
| B | T010 BLAST, T011 ROLE | different policy files |
| C | T014-T019 supporting templates | independent templates |
| D | T025 README, T026 GUIDE, T027 MANIFESTO | separate root docs, but final sync needed |
| E | T028 CONTRIBUTING, T029 ARCHITECTURE | separate docs |

Not parallel-safe:

```text
CLAUDE.md refactor should wait for AGENTS + policies.
README final rewrite should wait for template inventory to stabilize.
Example project should wait for Makefile and spec templates.
```

---

## 24. Overall Acceptance Criteria

Harness v2 is complete when:

```text
[ ] All old inconsistent branding is removed.
[ ] templates/ contains all required v2 templates.
[ ] PRD_TEMPLATE has user stories, FR/NFR, success criteria, ambiguity markers, out-of-scope.
[ ] SPEC/PLAN/TASKS templates form a coherent lifecycle.
[ ] BLAST_RADIUS_POLICY has leaf/branch/core/infra with parseable frontmatter.
[ ] ROLE_POLICY defines RED/GREEN/REFACTOR/REVIEWER/HUMAN boundaries.
[ ] AGENTS.md is cross-agent and contains no Claude-specific syntax.
[ ] CLAUDE.md is <= 200 lines.
[ ] Makefile has spec-init, verify, verify-ai, classify-risk.
[ ] make spec-init FEATURE=001-example creates a valid feature folder.
[ ] make verify-ai runs on clean checkout.
[ ] README explains v2 accurately.
[ ] IMPLEMENTATION_GUIDE can be followed step-by-step.
[ ] examples/minimal-project exists and is coherent.
[ ] No TODO remains in templates.
```

---

## 25. Out of Scope for v2

Explicitly deferred:

```text
1. Full harness CLI.
2. Full YAML policy engine.
3. Complete eval runner.
4. Automated context bundle generator.
5. Claude Code PreToolUse/PostToolUse hooks.
6. Multi-agent orchestration.
7. Git worktree scheduler.
8. Spec drift detection.
9. Full GitHub Actions CI suite.
10. Mandatory spec-kit integration.
```

Reason:

```text
v2 must stay copyable and immediately useful.
Runtime productization belongs to v3.
```

---

## 26. v2.5 Candidates

After v2 lands, v2.5 can add:

```text
1. Simple pre-commit guard for no test edit during GREEN.
2. Optional .harness/ directory.
3. Basic spec drift checker.
4. Lightweight context-bundle script.
5. GitHub Actions template for verify-ai.
6. Optional Claude hooks template.
```

---

## 27. v3 Candidates

v3 can become a real runtime:

```text
harness init
harness specify
harness plan
harness tasks
harness classify-risk
harness verify
harness eval
harness review
harness report
harness sync-agent-docs
```

v3 architecture:

```text
.harness/
├── constitution.md
├── state.json
├── policies/
│   ├── blast-radius.yaml
│   ├── roles.yaml
│   └── permissions.yaml
├── hooks/
├── evals/
└── context/
```

But v3 should only happen after v2 proves useful in real projects.

---

## 28. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| v2 becomes too document-heavy | Medium | High | make spec-init / verify-ai / classify-risk must run |
| v2 becomes too complex | Medium | High | defer full CLI/runtime to v3 |
| CLAUDE.md becomes too long | High | High | hard cap 200 lines |
| Blast radius policy is too abstract | Medium | High | include concrete examples and decision tree |
| AGENTS.md conflicts with CLAUDE.md | Low | Medium | AGENTS is general; CLAUDE is Claude-specific |
| Templates drift from Spec Kit inspiration | Medium | Low | add version/inspiration note, but do not depend on spec-kit |
| Makefile stubs feel fake | Medium | Medium | ensure spec-init/verify-ai/classify-risk are real |
| Users ignore eval/report | Medium | Medium | make verify-ai warn when missing |
| Too many templates overwhelm users | Medium | Medium | README quickstart only requires five core artifacts |

---

## 29. Recommended First PR

First PR should be small and high-signal:

```text
PR 1: Harness v2 foundation
```

Include only:

```text
1. Rename/branding cleanup.
2. PRD_TEMPLATE rewrite.
3. SPEC_TEMPLATE / PLAN_TEMPLATE / TASKS_TEMPLATE.
4. BLAST_RADIUS_POLICY.
5. ROLE_POLICY.
6. AGENTS.md.
7. CLAUDE.md refactor.
8. Makefile with spec-init / verify-ai / classify-risk.
9. scripts/verify-ai.sh and scripts/classify-risk.sh.
10. README quick update.
```

Do not include everything in first PR. Supporting templates and example project can be second PR.

---

## 30. Final Positioning

Harness v2 的一句话定位：

```text
Harness is a spec-governed, risk-classified engineering template for AI agents.
```

更有 builder 气质的版本：

```text
Harness is not another prompt pack.
It is a lightweight engineering harness that tells coding agents what to build, what not to touch, how to prove it works, and when to stop.
```

中文版本：

```text
Harness 不是 prompt 模板集合，而是一套轻量工程约束系统：
它规定 agent 先读什么、能改什么、不能改什么、如何验证、何时交给人类。
```

最终路线：

```text
Use GLM's template-first route as the skeleton.
Borrow DeepSeek's governance/runtime ideas as selective muscles.
Ship v2 as a usable template system.
Grow v3 only after real-world usage proves which constraints matter.
```

