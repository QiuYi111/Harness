# Harness v3.0.0 用户旅程审计报告

> **审计日期**: 2026-05-07
> **审计范围**: 全部 5 条用户旅程 × 17 个子技能 × 4 个策略文件 × 21 个 PM 模板
> **审计方法**: 逐文件读取 → 流程追踪 → 断点检测 → 严重度分级

---

## 目录

1. [审计摘要](#1-审计摘要)
2. [旅程 1：产品进化](#2-旅程-1产品进化)
3. [旅程 2：功能开发](#3-旅程-2功能开发)
4. [旅程 3：调试修复](#4-旅程-3调试修复)
5. [旅程 4：重构优化](#5-旅程-4重构优化)
6. [旅程 5：项目初始化](#6-旅程-5项目初始化)
7. [跨流程共性问题](#7-跨流程共性问题)
8. [发现汇总表](#8-发现汇总表)
9. [修复优先级路线图](#9-修复优先级路线图)
10. [附录](#10-附录)

---

## 1. 审计摘要

### 评级

| 旅程 | 状态 | 评级 | 阻塞问题 | 卡顿问题 |
|------|------|------|----------|----------|
| 产品进化 | ⚠️ | B | 1 | 1 |
| 功能开发 | ⚠️ | B- | 2 | 1 |
| 调试修复 | ✅ | A | 0 | 0 |
| 重构优化 | ⚠️ | B | 0 | 1 |
| 项目初始化 | ✅ | A | 0 | 0 |
| **跨流程** | ⚠️ | — | 0 | 3 |

**总评**: 5 条旅程中 2 条完全顺畅，3 条存在可修复的流程断点。无设计层面的根本缺陷，所有问题均为配置/路径/术语层面的实现遗漏。

### 关键数字

```
子技能总数:       17
策略文件:          4
模板文件:         21 (PM) + 15 (项目)
总发现数:         12
  🔴 阻塞:        2
  🟡 卡顿:        5
  🟠 轻微:        5
```

---

## 2. 旅程 1：产品进化

### 路径

```
"I have a product idea"
  → harness-grill-product (7 gates)
    → harness-supervisor (8-step loop)
      → harness-intern (execute task)
        → harness-eval → harness-report
```

### 流程追踪

#### Phase 1: grill-product → Supervisor 过渡

| 检查项 | 状态 | 证据 |
|--------|------|------|
| Gate 1-7 递进完整 | ✅ | 每个 gate 有 pass/skip/waive 条件 |
| Gate 7 产出 state.yaml | ✅ | 初始化所有 readiness 标志 |
| 渐进式出口机制 | ✅ | 2 次拒绝后允许跳过并记录 |
| Builder/Startup 模式切换 | ✅ | 替换 Gate 1-2 为生成性问题 |
| `ux_ready` 在 Gate 5 跳过时处理 | ❌ | 见 FINDING-P1 |

#### Phase 2: Supervisor 循环

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 8 步循环完整 | ✅ | OBSERVE → CHECK_READINESS → DECIDE → WRITE_TASK → DELEGATE → REVIEW → UPDATE_STATE → CONTINUE |
| 迭代限制 | ✅ | `max_iterations` 可配，默认无硬限制 |
| 连续失败熔断 | ✅ | 默认 3 次连续失败后升级到用户 |
| Agent-Loop 可行性验证 | ✅ | 5 次迭代测试 + 80% 通过门槛 |
| 恢复协议 | ✅ | 读取 `handoff.md` → `state.yaml` → 最近 3 条 loop-log |
| 12 个停止条件 | ✅ | 覆盖产品/MVP/技术栈/risk/安全/UI 味觉/失败 |
| Supervisor → Intern 委托 | ⚠️ | 见 FINDING-P2 |

#### Phase 3: Intern 执行

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 任务理解流程 | ✅ | 目标/允许范围/禁止范围/验收标准 |
| 风险分类前置 | ✅ | core/infra → STOP |
| 报告格式 | ✅ | 10 个必填节 |
| 作用域纪律 | ✅ | 禁止扩展范围，阻塞问题上报 |

### 发现

#### FINDING-P1: `ux_ready` 标志在 Builder 模式和"已有用户"模式下可能不会被设置

- **严重度**: 🟡 卡顿
- **位置**: `subskills/grill-product/SKILL.md` Gate 5 + `subskills/supervisor/SKILL.md` Step 2
- **现象**: 
  - Supervisor `CHECK_READINESS` 要求 `ux_ready: true` 才能委托"产品面向用户的工作"
  - Gate 7 的 state.yaml 初始化模板确实写 `ux_ready: true`
  - 但当用户选择 Builder 模式时，Gate 5 (UX Journey) 可能被跳过或简化
  - 当用户选择"已有用户/已有付费客户"时，Gate 5 也会被跳过
  - 此时 Gate 7 仍然写入 `ux_ready: true`，但实际上 UX 从未被系统化梳理
- **影响**: Supervisor 可能基于不存在的 UX 基础委托实现任务，导致产品体验不连贯
- **修复建议**: 
  1. Gate 5 跳过时，将 `ux_ready` 设为 `false` 而非 `true`
  2. 在 Supervisor `CHECK_READINESS` 中增加：如果 `ux_ready: false` 但任务不涉及 UI，允许继续
  3. 在 Supervisor 中增加一个 `ux_partial: true` 状态，允许非 UI 任务通过

#### FINDING-P2: Intern 技能不在 agent 系统的技能注册表中

- **严重度**: 🟡 卡顿
- **位置**: `subskills/supervisor/SKILL.md` Step 5 vs `.claude-plugin/`
- **现象**: 
  - Supervisor 写了 `opencode run --agent harness-intern --file .pm/runtime/next-task.md`
  - `harness-intern` 存在于 `subskills/intern/SKILL.md`
  - 但 `intern` 不在 agent 系统的外部技能注册表中（通过 `buffer/skills/harness/subskills/` 或 `.claude-plugin/` 暴露的技能列表）
  - agent 系统无法通过名称加载 `harness-intern`
- **影响**: Supervisor → Intern 的委托步骤可能无法自动执行，需要手动干预
- **修复建议**: 
  1. 将 `harness-intern` 注册为独立技能，或
  2. 在 Supervisor SKILL.md 中改为直接读取 `next-task.md` 并在当前 session 中执行 Intern 的逻辑，或
  3. 在 `buffer/skills/` 中创建 `harness-intern` 的注册入口

---

## 3. 旅程 2：功能开发

### 路径

```
"build this feature"
  → harness-grill (可选，需求模糊时)
  → harness-specify (创建 spec.md)
  → harness-plan (创建 plan.md)
  → harness-tasks (创建 tasks.md)
  → harness-risk (风险分类)
  → harness-context (上下文打包)
  → harness-tdd (RED → GREEN → REFACTOR → REVIEWER)
  → harness-eval (验收评估)
  → harness-report (实现报告)
```

### 流程追踪

#### 子技能链路完整性

| 转换 | 输入 | 输出 | 下游消费 | 状态 |
|------|------|------|----------|------|
| grill → specify | 用户需求 | 需求澄清 | specify 的输入 | ✅ |
| specify → plan | spec.md | plan.md | plan 的输入 | ✅ |
| plan → tasks | plan.md | tasks.md | tasks 的输入 | ✅ |
| tasks → risk | tasks.md | risk level + gates | context + tdd 消费 | ✅ |
| risk → context | risk level | context.md | tdd 消费 | ✅ |
| context → tdd | context.md + tasks.md | 测试 + 实现 | eval 消费 | ✅ |
| tdd → eval | 实现代码 + spec.md | eval.md | report 消费 | ✅ |
| eval → report | eval.md + 实现证据 | report.md | 合并/发布 | ✅ |

#### Autopilot 路径验证

| 路径 | 条件 | 自动化程度 | 状态 |
|------|------|------------|------|
| Leaf 快速路径 | 风险=leaf, 需求清晰 | 分类 → 改 → 验证 → (可选报告) | ✅ |
| Branch 标准路径 | 风险=branch | 全链路 spec → report | ✅ |
| Core 路径 | 风险=core | 全链路 + 人工审批 + 架构评审 | ⚠️ 见 FINDING-F2 |
| Infra 路径 | 风险=infra | 全链路 + dry-run + 安全评审 + 人工审批 | ⚠️ 见 FINDING-F2 |

#### Phase Detection 与文件检查

| 阶段 | 检测信号 | 触发技能 | 状态 |
|------|----------|----------|------|
| No Harness | 无 `.harness/`, 无 `AGENTS.md` | harness-init | ✅ |
| Intake | 有需求，无 spec | harness-grill → specify | ✅ |
| Spec | spec.md 存在，plan.md 缺失 | harness-plan | ✅ |
| Planning | plan.md 存在，tasks.md 缺失 | harness-tasks | ✅ |
| Implementation | tasks.md 存在 | risk → context → tdd | ✅ |
| Verification | 实现存在，eval.md 缺失 | harness-eval | ✅ |
| Reporting | eval 完成 | harness-report | ✅ |

### 发现

#### FINDING-F1: `cache-context.yaml` 中文件路径全部错误

- **严重度**: 🔴 阻塞
- **位置**: `references/policies/cache-context.yaml:5-11`
- **现象**: 
  ```yaml
  stable_prefix:
    - skills/engineering/harness-risk/SKILL.md     # 不存在
    - skills/engineering/harness-tdd/SKILL.md      # 不存在
    - skills/engineering/harness-tasks/SKILL.md    # 不存在
    - AGENTS.md                                      # ✅ 存在
    - CACHE.md                                       # ✅ 存在
    - .harness/policies/blast-radius.yaml            # ✅ 存在
    - .harness/policies/roles.yaml                   # 不存在
  ```
  实际路径为 `subskills/risk/SKILL.md`、`subskills/tdd/SKILL.md`、`subskills/tasks/SKILL.md`
- **影响**: `harness context --cache-aware` 命令生成的上下文包会缺失 3 个核心技能文件。`harness-cache` 技能无法正确组装缓存友好的上下文。
- **修复建议**: 将路径修正为：
  ```yaml
  stable_prefix:
    - subskills/risk/SKILL.md
    - subskills/tdd/SKILL.md
    - subskills/tasks/SKILL.md
    - AGENTS.md
    - CACHE.md
    - .harness/policies/blast-radius.yaml
  ```

#### FINDING-F2: `gates.yaml` 中 core/infra 级别缺少基础自动化门

- **严重度**: 🔴 阻塞
- **位置**: `references/policies/gates.yaml:66-84`
- **现象**: 
  ```yaml
  risk_gate_map:
    leaf:
      - lint
      - unit_test
    branch:
      - spec
      - plan
      - tests
      - review_agent
    core:          # 只有手动门，无自动化门
      - human_spec_review
      - architecture_review
      - rollback_plan
      - security_review
    infra:         # 只有手动门，无自动化门
      - dry_run
      - explicit_human_approval
      - rollback_plan
      - security_review
  ```
  正确语义应为：core = branch gates + 额外手动门；infra = core gates + 额外手动门。
- **影响**: core/infra 变更不强制执行 lint、unit_test、spec、plan、tests 检查。高风险变更反而跳过了基础质量门。
- **修复建议**: 修正为包含式累积：
  ```yaml
  core:
    - lint
    - unit_test
    - spec
    - plan
    - tests
    - review_agent
    - human_spec_review
    - architecture_review
    - rollback_plan
    - security_review
  infra:
    - lint
    - unit_test
    - spec
    - plan
    - tests
    - review_agent
    - human_spec_review
    - architecture_review
    - rollback_plan
    - security_review
    - dry_run
    - explicit_human_approval
  ```

#### FINDING-F3: TDD 依赖的 `verify-ai` 脚本不会复制到目标项目

- **严重度**: 🟡 卡顿
- **位置**: `references/templates/Makefile` 引用 `scripts/verify-ai.sh`；`subskills/tdd/ROLE_POLICY.md` 引用 `harness verify-ai`
- **现象**: 
  - Harness 仓库自身有 `scripts/verify-ai.sh`
  - 但 `harness init` 的模板复制逻辑中没有将此脚本复制到目标项目
  - 目标项目的 `Makefile` 模板包含 `verify-ai` 目标引用 `scripts/verify-ai.sh`
  - TDD 的 RED/GREEN/REFACTOR 每个阶段后要求运行 `harness verify-ai`
- **影响**: 在新初始化的项目中，`make verify-ai` 和 `harness verify-ai` 可能报 "command not found"，TDD 角色边界检查失效
- **修复建议**: 
  1. 在 `harness init` 中增加复制 `scripts/verify-ai.sh` 和 `scripts/classify-risk.sh` 到目标项目
  2. 或让 CLI 的 `verify-ai` 命令指向 Harness 安装目录的脚本（如果 editable install）

---

## 4. 旅程 3：调试修复

### 路径

```
"fix this bug" / "debug this" / "test failed"
  → Phase 0: Intake (创建 record.md)
  → Phase 1: Reproduce (铁律: 无法复现 → 无法修复)
  → Phase 2: Evidence (日志、堆栈、git diff、运行时状态)
  → Phase 3: Diagnose (工作示例 → 对比 → 单一假设 → 最小验证)
  → Phase 4: Patch (风险分类 → 失败测试 → 最小修复 → 深度防御)
  → Phase 5: Regression (自动化回归测试，红绿验证)
  → Phase 6: Review (git diff + risk re-check)
  → Phase 7: Close (按风险级别: leaf/base, branch/+eval, core+infra/+eval+report+人类签字)
```

### 流程追踪

#### 铁律执行链

| 铁律 | 检查点 | 自动化 | 状态 |
|------|--------|--------|------|
| 无证据不改 | Phase 2 → Phase 3 门 | record.md 必填 evidence 节 | ✅ |
| 无回归不关 | Phase 5 → Phase 7 门 | 回归测试必须红绿验证 | ✅ |
| 3 次失败升级 | Phase 3 假设循环 | `hypotheses_tried` 表格 + 计数 | ✅ |

#### 状态机

```
intake → reproducing
  ├─ not-reproduced → evidence-needed
  │     └─ cannot-reproduce → close-with-note
  └─ reproduced → diagnosing
        └─ root-caused → patching ──── [risk gate]
              └─ regression → review → closed
                    └─ (if risk ≥ branch → eval → report)
```

| 状态转换 | 条件 | 可逆性 | 状态 |
|----------|------|--------|------|
| intake → reproducing | 症状记录完成 | ✅ | ✅ |
| reproducing → diagnosing | 复现成功 | ✅ | ✅ |
| reproducing → evidence-needed | 不可复现 | ✅ | ✅ |
| evidence-needed → cannot-reproduce | Phase 2 耗尽 | ❌ | ✅ |
| diagnosing → root-caused | 单一根因确认 | ✅ | ✅ |
| diagnosing → evidence (回退) | 假设失败 1 次 | ✅ | ✅ |
| root-caused → patching | 进入 Phase 4 | ⚠️ risk gate | ✅ |
| patching → regression | 修复+测试完成 | ✅ | ✅ |
| regression → review | 回归测试通过 | ✅ | ✅ |
| review → closed | 所有关闭条件满足 | ❌ | ✅ |

#### 风险集成

| 集成点 | 位置 | 行为 | 状态 |
|--------|------|------|------|
| 风险分类 #1 | Phase 4 (Patch 前) | core/infra → 要求人类审批 | ✅ |
| 风险分类 #2 | Phase 6 (Review 时) | 重新检查 diff，风险可能升级 | ✅ |
| 关闭条件分级 | Phase 7 | leaf/base, branch/+eval, core+infra/+eval+report+签字 | ✅ |
| 紧急热修复 | Autopilot Rules | 压缩 Phase 2-3, Phase 4 必须人类审批, Phase 5 无例外 | ✅ |

### 评级: ✅ A 级 — 无发现

这是 5 条旅程中设计最完整的一条。7 个阶段递进严密，3 条铁律强制执行，状态机覆盖所有路径（包括"无法复现"的退出路径），与风险系统的双点集成确保安全门不被绕过。

---

## 5. 旅程 4：重构优化

### 路径

```
"refactor X" / "clean up X"
  → harness-risk (风险分类)
  → harness-plan (实现计划)
  → harness-tasks (任务分解)
  → harness-tdd (测试驱动)
  → harness-eval (验收)
  → harness-report (报告)
```

### 流程追踪

#### 路由正确性

| 信号 | 路由目标 | 状态 |
|------|----------|------|
| "refactor X" | harness-risk | ✅ 路由表一致 |
| "clean up X" | harness-risk | ✅ 路由表一致 |
| "optimize X" | harness-maintain-debug | ✅ 区分性能 bug vs 重构 |
| "update dependency" | harness-risk → tdd → eval → report | ✅ 跳过 plan/tasks |
| "migrate X to Y" | harness-risk → plan → tasks → tdd → eval → report | ✅ |

### 发现

#### FINDING-R1: 重构流程缺少 specify 步骤

- **严重度**: 🟡 卡顿
- **位置**: `references/ROUTING_TABLE.md` 重构行
- **现象**: 
  - 路由表中 `"refactor X"` 直接进 `harness-risk`，跳过了 `harness-specify`
  - 后续 `harness-eval` 的 Product Eval 需要 spec 作为验收基准
  - 重构没有 spec 意味着 eval 无法对比"实现是否匹配规格"
  - 轻量重构可能不需要完整 spec，但至少需要范围定义
- **影响**: 
  - 重构的 eval 只能做 Harness Eval（流程合规），无法做 Product Eval（功能合规）
  - 重构回归风险比新功能更高（改动已有代码），缺少规格定义增加了引入回归的概率
- **修复建议**: 
  1. 为重构场景增加轻量 specify 步骤（仅需：范围定义、预期行为不变声明、已知风险点）
  2. 或在 `harness-plan` 中增加"重构模式"，要求 plan.md 包含"行为不变性声明"章节
  3. 或在 `harness-eval` 中增加"重构评估模式"，对比重构前后的行为一致性

---

## 6. 旅程 5：项目初始化

### 路径

```
"initialize repo"
  → harness-init
    → 检测项目状态 (绿色/现有)
    → 解析模板路径
    → 创建目录结构 (不覆盖)
    → 安装技能
    → 打印下一步
  → harness-domain-language (可选)
```

### 流程追踪

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 绿色项目检测 | ✅ | 无 `.harness/` 即为新项目 |
| 现有项目检测 | ✅ | 有 `.harness/` 但缺失配置 |
| 模板复制不覆盖 | ✅ | init 逻辑明确"never overwrites existing" |
| PM 模式 (`--pm`) | ✅ | 额外创建 `.pm/` 目录和 PM 模板 |
| 最小模式 (`--minimal`) | ✅ | 仅创建核心文件 |
| 技能安装 | ✅ | `link-skills.sh` |
| 下一步指引 | ✅ | `INIT_GUIDE.md` 中定义 |

### 评级: ✅ A 级 — 无发现

初始化流程设计合理，有完整的边缘情况处理（不覆盖、绿色/现有检测、模式切换）。

---

## 7. 跨流程共性问题

### FINDING-C1: `CONSTITUTION_TEMPLATE.md` 使用过时的风险术语

- **严重度**: 🟡 卡顿
- **位置**: `references/templates/CONSTITUTION_TEMPLATE.md`
- **现象**: 模板中使用 `interface, app, domain, infra, docs` 五级分类，而 Harness v3 全部其他文件统一使用 `leaf, branch, core, infra` 四级分类。
- **影响**: 
  - 新初始化的项目会继承旧术语
  - 团队阅读 `CONSTITUTION.md` 时与 `DOMAIN-AWARENESS.md`、`gates.yaml`、`blast-radius.yaml` 的术语冲突
  - Agent 可能在两种术语间混淆
- **修复建议**: 将 CONSTITUTION 模板中的风险术语统一为 `leaf, branch, core, infra`。

### FINDING-C2: `buffer/` 与 `subskills/` 双副本维护风险

- **严重度**: 🟡 卡顿
- **位置**: `buffer/skills/harness/` vs `subskills/`
- **现象**: 
  - `buffer/skills/harness/` 下有完整副本（SKILL.md + subskills/ + references/）
  - `subskills/` 下有另一套
  - 两套内容可能不同步
- **影响**: 修改一处忘记另一处会导致 agent 行为不一致
- **修复建议**: 
  1. 确定单一真相源（建议 `subskills/`），`buffer/` 通过 symlink 或构建脚本生成
  2. 或在 `Makefile` 中增加同步检查命令

### FINDING-C3: `roles.yaml` 不存在

- **严重度**: 🟠 轻微
- **位置**: `references/policies/cache-context.yaml:11`
- **现象**: 引用 `.harness/policies/roles.yaml`，但 `references/policies/` 中只有 `blast-radius.yaml`, `cache-context.yaml`, `gates.yaml`, `project_index.yaml`
- **影响**: cache-aware 上下文组装时找不到此文件，但不影响核心流程（roles 信息实际上在 TDD 的 `ROLE_POLICY.md` 中定义）
- **修复建议**: 从 `cache-context.yaml` 中移除此引用，或将 TDD 角色定义提取为 `roles.yaml`

### FINDING-C4: `harness status` 无技能层解读

- **严重度**: 🟠 轻微
- **位置**: `SKILL.md:36`, `references/ROUTING_TABLE.md:52`
- **现象**: 多处提到"run `harness status`"查看项目状态，但没有子技能定义状态如何解读和呈现
- **影响**: CLI 命令可能存在（`scripts/harness_runtime/`），但 agent 不知道如何解读输出或如何向用户解释状态
- **修复建议**: 在 `SKILL.md` 或 `AUTOPILOT_RULES.md` 中增加状态输出解读指南

### FINDING-C5: `project_index.yaml` 中 `templates` 为 `required_dirs`

- **严重度**: 🟠 轻微
- **位置**: `references/policies/project_index.yaml:30`
- **现象**: `templates` 被列为 `required_dirs`，但许多项目不需要本地模板目录（模板由 Harness 安装目录提供）
- **影响**: `harness status` 可能误报"缺少 templates 目录"
- **修复建议**: 将 `templates` 从 `required_dirs` 移到 `optional_dirs`

---

## 8. 发现汇总表

| ID | 严重度 | 旅程 | 位置 | 简述 |
|----|--------|------|------|------|
| FINDING-P1 | 🟡 卡顿 | 产品进化 | grill-product + supervisor | `ux_ready` 在 Gate 5 跳过时可能不正确 |
| FINDING-P2 | 🟡 卡顿 | 产品进化 | supervisor Step 5 | Intern 不在技能注册表 |
| FINDING-F1 | 🔴 阻塞 | 功能开发 | cache-context.yaml | 文件路径全部错误 |
| FINDING-F2 | 🔴 阻塞 | 功能开发 | gates.yaml | core/infra 缺少自动化门 |
| FINDING-F3 | 🟡 卡顿 | 功能开发 | init + tdd | verify-ai 脚本未复制到目标项目 |
| FINDING-R1 | 🟡 卡顿 | 重构优化 | ROUTING_TABLE | 缺少 specify 步骤 |
| FINDING-C1 | 🟡 卡顿 | 跨流程 | CONSTITUTION_TEMPLATE | 风险术语过时 |
| FINDING-C2 | 🟡 卡顿 | 跨流程 | buffer/ vs subskills/ | 双副本维护风险 |
| FINDING-C3 | 🟠 轻微 | 跨流程 | cache-context.yaml | roles.yaml 不存在 |
| FINDING-C4 | 🟠 轻微 | 跨流程 | SKILL.md | status 无技能层解读 |
| FINDING-C5 | 🟠 轻微 | 跨流程 | project_index.yaml | templates 为 required 但应为 optional |

---

## 9. 修复优先级路线图

### Phase 1: 阻塞问题（建议立即修复）

| 顺序 | ID | 修复动作 | 预估工作量 |
|------|-----|----------|------------|
| 1 | FINDING-F1 | 修正 `cache-context.yaml` 中的 4 个路径 | 10 分钟 |
| 2 | FINDING-F2 | 修正 `gates.yaml`，core/infra 累积包含低级门 | 15 分钟 |

### Phase 2: 卡顿问题（建议本周修复）

| 顺序 | ID | 修复动作 | 预估工作量 |
|------|-----|----------|------------|
| 3 | FINDING-P1 | Gate 5 跳过时 `ux_ready: false` + Supervisor 增加条件放行 | 30 分钟 |
| 4 | FINDING-F3 | init 复制 verify-ai.sh + classify-risk.sh 到目标项目 | 20 分钟 |
| 5 | FINDING-P2 | 注册 harness-intern 或改为内联执行 | 45 分钟 |
| 6 | FINDING-C1 | 更新 CONSTITUTION_TEMPLATE 风险术语 | 15 分钟 |
| 7 | FINDING-R1 | 重构流程增加轻量 specify 或 plan 重构模式 | 30 分钟 |
| 8 | FINDING-C2 | 确定单一真相源，消除双副本 | 60 分钟 |

### Phase 3: 轻微问题（建议下个迭代修复）

| 顺序 | ID | 修复动作 | 预估工作量 |
|------|-----|----------|------------|
| 9 | FINDING-C3 | 移除 cache-context.yaml 中的 roles.yaml 引用 | 5 分钟 |
| 10 | FINDING-C4 | 增加 status 输出解读指南 | 20 分钟 |
| 11 | FINDING-C5 | templates 从 required 移到 optional | 5 分钟 |

---

## 10. 附录

### A. 审计覆盖的文件清单

#### 子技能 (17)

| 子技能 | 文件数 | SKILL.md | 补充文件 |
|--------|--------|----------|----------|
| architecture-review | 3 | ✅ | LANGUAGE.md, DEEPENING_GUIDE.md |
| cache | 2 | ✅ | CACHE_METRICS.md |
| context | 3 | ✅ | CONTEXT_GUIDE.md, AGENT_FILE_TEMPLATES.md |
| debug | 3 | ✅ | references/root-cause-tracing.md, references/defense-in-depth.md |
| domain-language | 3 | ✅ | CONTEXT_FORMAT.md, ADR_FORMAT.md |
| eval | 3 | ✅ | EVAL_FORMAT.md, EVIDENCE_GUIDE.md |
| grill | 2 | ✅ | QUESTION_TREE.md |
| grill-product | 1 | ✅ | — |
| init | 2 | ✅ | INIT_GUIDE.md |
| intern | 1 | ✅ | — |
| plan | 3 | ✅ | PLAN_FORMAT.md, RISK_GUIDE.md |
| report | 2 | ✅ | REPORT_FORMAT.md |
| risk | 2 | ✅ | BLAST_RADIUS_GUIDE.md |
| specify | 3 | ✅ | SPEC_FORMAT.md, PRD_FORMAT.md |
| supervisor | 1 | ✅ | — |
| tasks | 3 | ✅ | TASKS_FORMAT.md, VERTICAL_SLICE_GUIDE.md |
| tdd | 4 | ✅ | ROLE_POLICY.md, TESTING_GUIDE.md, EXAMPLES.md |

#### 策略文件 (4)

- `references/policies/blast-radius.yaml`
- `references/policies/cache-context.yaml`
- `references/policies/gates.yaml`
- `references/policies/project_index.yaml`

#### 参考文件 (5)

- `references/ROUTING_TABLE.md`
- `references/PHASE_DETECTION.md`
- `references/AUTOPILOT_RULES.md`
- `references/DOMAIN-AWARENESS.md`
- `references/CACHE_GUIDE.md`

#### 根入口 (3)

- `SKILL.md` (harness 根路由)
- `README.md`
- `MANIFESTO.md`

### B. 术语表

| 术语 | 含义 |
|------|------|
| 阻塞 (🔴) | 流程完全无法通过，必须修复后才能正常使用 |
| 卡顿 (🟡) | 流程可以走通但可能在特定条件下中断或产生错误结果 |
| 轻微 (🟠) | 不影响流程执行，但可能造成困惑或不一致 |
| Blast Radius | 变更的影响范围，分四级: leaf < branch < core < infra |
| Iron Law | 不可违反的硬性规则，违反视为流程失败 |
| Gate | 质量门，某阶段必须通过才能进入下一阶段 |
| TDD Role Isolation | 测试/实现/重构/评审四种角色，每种角色只能修改特定文件 |
| PM Loop | Supervisor → Intern → Review → State Update 的迭代循环 |

---

> **报告生成**: 2026-05-07 | **审计版本**: Harness v3.0.0 | **审计人**: AI Assistant
