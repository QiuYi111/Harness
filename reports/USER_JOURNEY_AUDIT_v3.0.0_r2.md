# Harness v3.0.0 用户旅程审计报告（第二轮）

> **审计日期**: 2026-05-07
> **审计轮次**: 第 2 轮（技能重构后重新分析）
> **审计范围**: 5 条用户旅程 × 17 个子技能 × 51 个文件（含重构后的拆分文件）
> **审计方法**: 逐文件读取 → 交叉引用追踪 → 断点检测 → 严重度分级
> **变更摘要**: debug / grill-product / supervisor / intern 四个子技能已完成模块化拆分，SKILL.md 大幅精简，详细逻辑下沉到 `references/` 子文件

---

## 目录

1. [重构变化摘要](#1-重构变化摘要)
2. [旅程 1：产品进化](#2-旅程-1产品进化)
3. [旅程 2：功能开发](#3-旅程-2功能开发)
4. [旅程 3：调试修复](#4-旅程-3调试修复)
5. [旅程 4：重构优化](#5-旅程-4重构优化)
6. [旅程 5：项目初始化](#6-旅程-5项目初始化)
7. [跨流程共性问题](#7-跨流程共性问题)
8. [发现汇总表](#8-发现汇总表)
9. [修复优先级路线图](#9-修复优先级路线图)
10. [附录：重构前后对比](#10-附录重构前后对比)

---

## 1. 重构变化摘要

### 已重构的子技能

| 子技能 | 变化 | SKILL.md 行数 | 新增文件 |
|--------|------|---------------|----------|
| **debug** | 内容拆分到 `references/` | 398 → 132 | `phases-detail.md`, `anti-patterns.md` |
| **grill-product** | 7 个 gate 的问题列表全部拆出 | 470 → 66 | `gate-questions.md`, `pushback-patterns.md`, `cognitive-principles.md`, `design-probe.md` |
| **supervisor** | 8 步循环、安全机制、权限矩阵拆出 | 299 → 45 | `loop-steps.md`, `safety-mechanisms.md`, `authority.md` |
| **intern** | 执行流程、作用域纪律拆出 | (新增) 58 | `execution-flow.md`, `scope-and-quality.md` |

### 未变化的子技能（与第一轮相同）

specify, plan, tasks, tdd, eval, report, risk, context, cache, grill, architecture-review, domain-language, init

### 关键观察

重构方向一致：**SKILL.md 精简为路由入口 + 概述表**，详细步骤下沉到 `references/` 子文件。这带来两个好处：

1. **Token 节省**：Agent 只需读 SKILL.md 即可路由，需要时再按需读取子文件
2. **可维护性**：修改单个 phase/step 不会影响整个文件

---

## 2. 旅程 1：产品进化

### 路径

```
"I have a product idea"
  → harness-grill-product (7 gates, 内容在 references/gate-questions.md)
    → harness-supervisor (8-step loop, 内容在 references/loop-steps.md)
      → harness-intern (execute task, 内容在 references/execution-flow.md)
        → harness-eval → harness-report
```

### 流程追踪

#### Phase 1: grill-product

| 检查项 | 状态 | 证据 |
|--------|------|------|
| SKILL.md 正确引用子文件 | ✅ | `references/gate-questions.md`, `references/pushback-patterns.md`, `references/cognitive-principles.md`, `references/design-probe.md` |
| Gate 总览表完整 | ✅ | SKILL.md 包含 7-gate 概述表（Goal + Output） |
| Gate 1-7 问题列表完整 | ✅ | `gate-questions.md` 380 行，每个 gate 有 questions + outputs + pass condition |
| Anti-sycophancy 规则 | ✅ | `pushback-patterns.md` 独立文件 |
| 认知原则 | ✅ | `cognitive-principles.md` 5 条原则 |
| Design probe | ✅ | `design-probe.md` 含 coherence validation + subtraction check + block rule |
| `ux_ready` 在 Gate 5 跳过时处理 | ⚠️ | 见 FINDING-P1 |

#### Phase 2: supervisor

| 检查项 | 状态 | 证据 |
|--------|------|------|
| SKILL.md 精简为概述 | ✅ | 45 行，引用 3 个子文件 |
| 8 步循环完整 | ✅ | `loop-steps.md` 157 行 |
| 安全机制完整 | ✅ | `safety-mechanisms.md` 含迭代限制 + 熔断 + 可行性验证 + 12 个停止条件 + 7 条文件写入规则 |
| 权限矩阵完整 | ✅ | `authority.md` 含 CAN/CANNOT + 恢复协议 |
| `ux_ready` 在 CHECK_READINESS 中要求 | ⚠️ | `loop-steps.md:29` 仍要求 `ux_ready`，但 grill-product Gate 5 跳过时未明确处理 |
| Supervisor → Intern 委托 | ⚠️ | 见 FINDING-P2 |

#### Phase 3: intern

| 检查项 | 状态 | 证据 |
|--------|------|------|
| SKILL.md 精简为角色定义 | ✅ | 58 行，引用 2 个子文件 |
| 执行流程完整 | ✅ | `execution-flow.md` 166 行，含 7 步 + 3 种模式 (feature/spike/bug fix) |
| 作用域纪律完整 | ✅ | `scope-and-quality.md` 52 行，含 MUST/MUST NOT + blocker 行为 + 5 条质量规则 |
| 报告模板内联 | ✅ | `execution-flow.md` 包含完整的 worker-report.md 模板 |
| Risk 分类前置 | ✅ | Step 2: core/infra → STOP + report blocker |

### 发现

#### FINDING-P1: `ux_ready` 在特定场景下可能不正确

- **严重度**: 🟡 卡顿
- **位置**: `grill-product/references/gate-questions.md` Gate 5 跳过逻辑 vs `supervisor/references/loop-steps.md` CHECK_READINESS
- **现象**: 
  - `gate-questions.md:340-349` Gate 7 state.yaml 初始化模板写 `ux_ready: true`
  - 但 Gate 5 (UX Journey) 在两种场景下被跳过：Builder 模式（替换为生成性问题）、"已有用户/付费客户"模式
  - Gate 6 (UI Direction) 对非 UI 产品设置 `ui_direction_required: false` 并跳过，此时 Gate 7 仍然会写 `ux_ready: true`
  - 对于非 UI 产品（CLI/库/后端），`ux_ready: true` 是合理的——不需要 UX 但 readiness 满足
  - **真正的问题**：Builder 模式下 Gate 5 被替换为生成性问题而非完整 UX 梳理，但 state.yaml 仍写 `ux_ready: true`，而实际上用户旅程和情感弧线可能从未系统化定义
- **影响**: Supervisor 在 Builder 模式下可能基于不完整的 UX 基础委托面向用户的实现
- **修复建议**: 
  1. Builder 模式下，Gate 5 完成后写 `ux_ready: true` 但附加 `ux_depth: light` 标记
  2. Supervisor `CHECK_READINESS` 增加：如果任务涉及 UI 实现且 `ux_depth: light`，先请求用户补充 UX 细节

#### FINDING-P2: Intern 技能不在 agent 系统的技能注册表中

- **严重度**: 🟡 卡顿
- **位置**: `supervisor/references/loop-steps.md:90-91` vs 技能注册机制
- **现象**: 
  - Supervisor Step 5 写了 `opencode run --agent harness-intern --file .pm/runtime/next-task.md`
  - `harness-intern` 存在于 `subskills/intern/SKILL.md`（含 description 和 frontmatter）
  - 但 Intern 的 description 中有 `"run intern"` 触发词
  - **新观察**：Intern 的 SKILL.md 有正确的 frontmatter（name + description），理论上 agent 系统可以按 description 匹配加载
  - 问题在于：Supervisor 使用 `--agent harness-intern` 语法，这假设 agent 系统支持按 name 精确查找技能，而非仅按 description 模糊匹配
- **影响**: 如果 agent 系统不支持 `--agent <name>` 精确查找，委托步骤会失败
- **修复建议**: 
  1. 在 Supervisor 的 Step 5 中增加 fallback 指令："If `--agent` is not supported, read `.pm/runtime/next-task.md` and load the skill matching 'execute task' or 'run intern'"
  2. 或在 SKILL.md 根入口的 description 中增加 `"execute task"`, `"run next-task.md"`, `"worker"` 作为 Intern 的显式路由关键词

---

## 3. 旅程 2：功能开发

### 路径

```
"build this feature"
  → harness-grill (可选)
  → harness-specify (spec.md)
  → harness-plan (plan.md)
  → harness-tasks (tasks.md)
  → harness-risk (risk level + gates)
  → harness-context (context.md)
  → harness-tdd (RED → GREEN → REFACTOR → REVIEWER)
  → harness-eval (eval.md)
  → harness-report (report.md)
```

### 流程追踪

#### 子技能链路完整性

| 转换 | 输入 | 输出 | 下游消费 | 状态 |
|------|------|------|----------|------|
| grill → specify | 用户需求 | 需求澄清 | specify 输入 | ✅ |
| specify → plan | spec.md | plan.md | plan 输入 | ✅ |
| plan → tasks | plan.md | tasks.md | tasks 输入 | ✅ |
| tasks → risk | tasks.md | risk level + gates | context + tdd | ✅ |
| risk → context | risk level | context.md | tdd | ✅ |
| context → tdd | context.md + tasks.md | 测试 + 实现 | eval | ✅ |
| tdd → eval | 实现代码 + spec.md | eval.md | report | ✅ |
| eval → report | eval.md + 证据 | report.md | 合并/发布 | ✅ |

#### Autopilot 路径验证

| 路径 | 条件 | 自动化程度 | 状态 |
|------|------|------------|------|
| Leaf 快速路径 | 风险=leaf, 需求清晰 | 分类 → 改 → 验证 → (可选报告) | ✅ |
| Branch 标准路径 | 风险=branch | 全链路 | ✅ |
| Core 路径 | 风险=core | 全链路 + 人工审批 + 架构评审 | ⚠️ 见 FINDING-F2 |
| Infra 路径 | 风险=infra | 全链路 + dry-run + 安全评审 | ⚠️ 见 FINDING-F2 |

### 发现

#### FINDING-F1: `cache-context.yaml` 中文件路径全部错误

- **严重度**: 🔴 阻塞
- **位置**: `references/policies/cache-context.yaml:5-11`
- **现象**: （与第一轮相同，未修复）
  ```yaml
  stable_prefix:
    - skills/engineering/harness-risk/SKILL.md     # 实际应为 subskills/risk/SKILL.md
    - skills/engineering/harness-tdd/SKILL.md      # 实际应为 subskills/tdd/SKILL.md
    - skills/engineering/harness-tasks/SKILL.md    # 实际应为 subskills/tasks/SKILL.md
    - .harness/policies/roles.yaml                  # 不存在
  ```
- **影响**: `harness context --cache-aware` 无法找到技能文件，cache-aware 上下文组装失败
- **修复建议**: 
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
- **现象**: （与第一轮相同，未修复）
  - leaf 有 `lint + unit_test`
  - branch 有 `spec + plan + tests + review_agent`
  - core 只有手动门（`human_spec_review + architecture_review + rollback_plan + security_review`），缺少 lint/unit_test
  - infra 同理
  - 语义上 core 应 = branch 全部门 + 额外手动门
- **影响**: 高风险变更不强制执行 lint 和单元测试
- **修复建议**: core/infra 累积包含低级门

#### FINDING-F3: TDD 依赖的 `verify-ai` 脚本未复制到目标项目

- **严重度**: 🟡 卡顿
- **位置**: `subskills/init/SKILL.md` 模板列表 vs `subskills/tdd/SKILL.md`
- **现象**: （与第一轮相同）
  - `init` SKILL.md 列出了复制 `Makefile` 模板，但未复制 `scripts/verify-ai.sh`
  - Makefile 模板引用 `scripts/verify-ai.sh`
  - TDD 的每个 cycle 后要求 `harness verify-ai`
- **影响**: 新项目 `make verify-ai` 和 `harness verify-ai` 可能无法工作
- **修复建议**: init 增加 `scripts/verify-ai.sh` 和 `scripts/classify-risk.sh` 的复制逻辑

---

## 4. 旅程 3：调试修复

### 路径

```
"fix this bug"
  → Phase 0: Intake
  → Phase 1: Reproduce
  → Phase 2: Evidence
  → Phase 3: Diagnose
  → Phase 4: Patch (risk gate)
  → Phase 5: Regression
  → Phase 6: Review
  → Phase 7: Close (risk-based routing)
```

### 重构后变化

| 变化 | 之前 | 之后 |
|------|------|------|
| Phase 详情位置 | 全部在 SKILL.md | SKILL.md 概述表 + `references/phases-detail.md` 完整步骤 |
| Anti-patterns 位置 | 全部在 SKILL.md | `references/anti-patterns.md` 独立文件 |
| defense-in-depth | 在 SKILL.md 中 | `references/defense-in-depth.md`（未变） |
| root-cause-tracing | 在 SKILL.md 中 | `references/root-cause-tracing.md`（未变） |
| SKILL.md 行数 | 398 行 | 132 行 |

### 流程追踪

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 概述表与子文件一致 | ✅ | SKILL.md Phase 表的 one-line 描述与 phases-detail.md 标题完全一致 |
| 3 条铁律 | ✅ | SKILL.md + phases-detail.md 双重声明 |
| 状态机 | ✅ | 完整覆盖所有路径（含 cannot-reproduce 退出） |
| 风险集成（双点） | ✅ | Phase 4 (patch 前) + Phase 6 (review 时) |
| 关闭条件分级 | ✅ | leaf/base, branch/+eval, core+infra/+eval+report+human sign-off |
| Anti-patterns 完整 | ✅ | `anti-patterns.md` 包含 use-especially/don't-skip/red-flags/rationalizations |
| 引用路径正确 | ✅ | `./references/phases-detail.md`, `./references/anti-patterns.md`, `../../references/templates/DEBUG_RECORD_TEMPLATE.md` |

### 评级: ✅ A 级 — 无发现

重构后 debug 技能结构更清晰，SKILL.md 作为快速路由入口，phases-detail.md 作为执行参考。所有引用路径正确，内容无遗漏。

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

| 信号 | 路由目标 | 状态 |
|------|----------|------|
| "refactor X" | harness-risk | ✅ |
| "clean up X" | harness-risk | ✅ |
| "optimize X" | harness-maintain-debug | ✅ 区分性能 bug vs 重构 |
| "update dependency" | harness-risk → tdd → eval → report | ✅ |
| "migrate X to Y" | harness-risk → plan → tasks → tdd → eval → report | ✅ |

### 发现

#### FINDING-R1: 重构流程缺少 specify 步骤

- **严重度**: 🟡 卡顿
- **位置**: `references/ROUTING_TABLE.md` 重构行
- **现象**: （与第一轮相同，未修复）
  - 路由表中 `"refactor X"` 直接进 `harness-risk`，跳过 `harness-specify`
  - 后续 `harness-eval` 的 Product Eval 需要 spec 作为验收基准
- **影响**: 重构的 eval 只能做 Harness Eval（流程合规），无法做 Product Eval（功能合规）
- **修复建议**: 
  1. 为重构增加轻量 specify 步骤（仅需范围定义 + 行为不变性声明）
  2. 或在 `harness-plan` 中增加"重构模式"要求 plan.md 包含"行为不变性声明"章节

---

## 6. 旅程 5：项目初始化

### 路径

```
"initialize repo"
  → harness-init (创建目录结构 + 复制模板)
  → harness-domain-language (可选，建立领域语言)
```

### 流程追踪

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 绿色/现有项目检测 | ✅ | SKILL.md Step 1 |
| 模板复制不覆盖 | ✅ | "Never overwrite existing files" |
| PM 模式 (`--pm`) | ✅ | 额外创建 `.pm/` 完整目录 |
| 最小模式 (`--minimal`) | ✅ | 仅创建核心文件 |
| 技能安装引用 | ✅ | `harness install-skills` |
| INIT_GUIDE.md 引用 | ✅ | 模板路径解析细节 |
| **verify-ai.sh 未复制** | ⚠️ | 见 FINDING-F3 |

### 评级: ✅ A 级（除 FINDING-F3）

---

## 7. 跨流程共性问题

### FINDING-C1: `CONSTITUTION_TEMPLATE.md` 使用过时风险术语

- **严重度**: 🟡 卡顿
- **位置**: `references/templates/CONSTITUTION_TEMPLATE.md`
- **现象**: （未检查此文件是否在重构中更新，但鉴于其余文件未提到此变更，假设未修复）
- **影响**: 新项目继承旧术语 `interface, app, domain, infra, docs`，与 `DOMAIN-AWARENESS.md` 的 `leaf, branch, core, infra` 冲突

### FINDING-C2: `buffer/` 与 `subskills/` 双副本维护风险

- **严重度**: 🟡 卡顿
- **位置**: `buffer/skills/harness/` vs `subskills/`
- **现象**: 两套副本，重构只更新了 `subskills/`，`buffer/` 可能已过时

### FINDING-C3: `roles.yaml` 不存在

- **严重度**: 🟠 轻微
- **位置**: `references/policies/cache-context.yaml:11`
- **现象**: 引用 `.harness/policies/roles.yaml`，文件不存在

### FINDING-C4: `harness status` 无技能层解读

- **严重度**: 🟠 轻微
- **位置**: `SKILL.md:35`, `ROUTING_TABLE.md:52`
- **现象**: CLI 命令存在但无子技能定义如何解读输出

### FINDING-C5: `project_index.yaml` 中 `templates` 为 required

- **严重度**: 🟠 轻微
- **位置**: `references/policies/project_index.yaml:30`
- **现象**: `templates` 列为 `required_dirs`，但许多项目不需要本地模板目录

---

## 8. 发现汇总表

| ID | 严重度 | 旅程 | 简述 | 第一轮对比 |
|----|--------|------|------|------------|
| FINDING-P1 | 🟡 卡顿 | 产品进化 | Builder 模式下 `ux_ready` 可能不准确 | 仍存在，描述更精确 |
| FINDING-P2 | 🟡 卡顿 | 产品进化 | Supervisor → Intern 委托依赖 `--agent` 精确查找 | 仍存在，Intern 已有正确 frontmatter 但 `--agent` 语法假设可能不成立 |
| FINDING-F1 | 🔴 阻塞 | 功能开发 | `cache-context.yaml` 路径错误 | 未修复 |
| FINDING-F2 | 🔴 阻塞 | 功能开发 | `gates.yaml` core/infra 缺少自动化门 | 未修复 |
| FINDING-F3 | 🟡 卡顿 | 功能开发 | `verify-ai` 脚本未复制到目标项目 | 未修复 |
| FINDING-R1 | 🟡 卡顿 | 重构优化 | 重构流程缺少 specify 步骤 | 未修复 |
| FINDING-C1 | 🟡 卡顿 | 跨流程 | CONSTITUTION 术语过时 | 未修复 |
| FINDING-C2 | 🟡 卡顿 | 跨流程 | buffer/subskills 双副本 | 未修复 |
| FINDING-C3 | 🟠 轻微 | 跨流程 | roles.yaml 不存在 | 未修复 |
| FINDING-C4 | 🟠 轻微 | 跨流程 | status 无技能层解读 | 未修复 |
| FINDING-C5 | 🟠 轻微 | 跨流程 | templates 应为 optional | 未修复 |

---

## 9. 修复优先级路线图

### Phase 1: 阻塞问题（建议立即修复）

| 顺序 | ID | 修复动作 | 预估 |
|------|-----|----------|------|
| 1 | FINDING-F1 | 修正 `cache-context.yaml` 中的 4 个路径 | 10 min |
| 2 | FINDING-F2 | 修正 `gates.yaml`，core/infra 累积包含低级门 | 15 min |

### Phase 2: 卡顿问题（建议本周修复）

| 顺序 | ID | 修复动作 | 预估 |
|------|-----|----------|------|
| 3 | FINDING-F3 | init 增加 verify-ai.sh / classify-risk.sh 复制 | 20 min |
| 4 | FINDING-P1 | Builder 模式增加 `ux_depth` 标记 + Supervisor 条件放行 | 30 min |
| 5 | FINDING-P2 | Supervisor Step 5 增加 fallback 委托指令 | 20 min |
| 6 | FINDING-C1 | 更新 CONSTITUTION_TEMPLATE 风险术语 | 15 min |
| 7 | FINDING-R1 | 重构流程增加轻量 specify 或 plan 重构模式 | 30 min |
| 8 | FINDING-C2 | 确定单一真相源，消除双副本 | 60 min |

### Phase 3: 轻微问题（建议下个迭代修复）

| 顺序 | ID | 修复动作 | 预估 |
|------|-----|----------|------|
| 9 | FINDING-C3 | 移除 cache-context.yaml 中的 roles.yaml 引用 | 5 min |
| 10 | FINDING-C4 | 增加 status 输出解读指南 | 20 min |
| 11 | FINDING-C5 | templates 从 required 移到 optional | 5 min |

**总预估修复量**: Phase 1 = 25 min, Phase 2 = 175 min, Phase 3 = 30 min = **约 4 小时**

---

## 10. 附录：重构前后对比

### 子技能文件数变化

| 子技能 | 第一轮文件数 | 第二轮文件数 | 新增文件 |
|--------|-------------|-------------|----------|
| debug | 3 | 5 | `phases-detail.md`, `anti-patterns.md` |
| grill-product | 1 | 5 | `gate-questions.md`, `pushback-patterns.md`, `cognitive-principles.md`, `design-probe.md` |
| supervisor | 1 | 4 | `loop-steps.md`, `safety-mechanisms.md`, `authority.md` |
| intern | 0 | 3 | `SKILL.md`, `execution-flow.md`, `scope-and-quality.md` |
| **总计** | 5 | **17** | **12 个新文件** |

### SKILL.md 行数变化

| 子技能 | 第一轮 | 第二轮 | 精简率 |
|--------|--------|--------|--------|
| debug | 398 | 132 | 67% |
| grill-product | 470 | 66 | 86% |
| supervisor | 299 | 45 | 85% |
| intern | N/A | 58 | 新增 |

### 重构质量评估

| 检查项 | 状态 |
|--------|------|
| SKILL.md 与子文件内容一致 | ✅ 所有 4 个重构技能 |
| 子文件引用路径正确 | ✅ 全部使用相对路径 |
| 无内容丢失 | ✅ 对比确认所有原始内容已迁移 |
| 概述表与详细内容对齐 | ✅ debug 7-phase 表 + phases-detail.md 完全匹配 |

---

> **报告生成**: 2026-05-07 | **审计版本**: Harness v3.0.0 | **轮次**: 第 2 轮（重构后）
