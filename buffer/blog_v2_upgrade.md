# Harness v2.0.0: 从提示词包到规格驱动的工程化体系

## 一句话总结

Harness v2 把 AI 编程代理从「读提示词干活」升级为「按规格书施工」，用模板、策略和自动化门禁取代了零散的 agent 指令。

## 为什么要做 v2

v1 的问题很明确：一套提示词打包成 repo，代理读完就开干。没有规格约束，没有风险评估，没有验证门禁。代码质量全靠代理的「自觉」。

具体来说：

- **没有规格书**。代理自己理解需求，自己决定做什么、不做什么。理解偏差不会被检测到。
- **没有风险分级**。改一行文档和改核心领域模型用同一套流程。要么过度审批，要么完全没有审批。
- **没有验证闭环**。写完代码直接提交。没有证据证明规格被遵守，没有证据证明测试确实覆盖了需求。
- **只绑定一个代理**。CLAUDE.md 写死了 Claude 的行为，换一个代理就失效。

v2 的目标：让任何 AI 代理都能按照同一套工程纪律工作，并且这个过程是可以验证的。

## v2 的核心设计

### 1. 规格驱动生命周期

每个功能必须走完这条链路：

```
PRD → SPEC → PLAN → TASKS → IMPLEMENT → EVAL → REPORT → REVIEW
```

代理不能跳步。没有 SPEC 就不能写 PLAN，没有 PLAN 就不能写 TASKS，没有 TASKS 就不能写代码。每一步都有对应的模板文件，填写过程就是在把模糊的需求变成可执行的工作单元。

### 2. 爆炸半径风险分级

不是所有改动都需要同等程度的审批。v2 用四级分类把代理的自主权和审批要求绑定在一起：

| 风险等级 | 自主权 | 触发条件 | 必须通过的门禁 |
|---------|--------|---------|--------------|
| `leaf` | 高 | 文档、测试、独立组件 | lint + 单元测试 |
| `branch` | 中 | 功能模块、API 端点 | 规格 + 计划 + 测试 + 代码审查 |
| `core` | 低 | 领域模型、权限、核心业务逻辑 | 人工审查 + 架构审查 + 回滚方案 |
| `infra` | 极低 | 部署、CI/CD、密钥、数据库迁移 | 演练 + 人工批准 + 回滚方案 + 安全审查 |

不确定时向上升级。涉及多个文件时取最高风险等级。

### 3. TDD 角色隔离

代理在开始工作前必须声明自己的角色，角色决定了能碰哪些文件：

- **RED**：只写测试。不能碰实现代码。
- **GREEN**：只写实现让测试通过。不能碰测试。
- **REFACTOR**：只重构，不改行为。测试变红就回滚。
- **REVIEWER**：只写报告，不碰代码和测试。

这防止了「自己写测试自己过」的问题。写测试的和写实现的是不同的角色边界。

### 4. Makefile 作为唯一接口

所有操作都通过 `make` 目标暴露：

```bash
make init                                    # 初始化环境
make spec-init FEATURE=001-add-todo          # 从模板创建功能规格目录
make verify                                  # 产品验证（lint + 测试 + 类型检查 + 契约测试 + 安全扫描）
make verify-ai                               # Harness 验证（模板完整性 + 策略合规）
make classify-risk                           # 对当前改动做风险分级
```

`verify-ai` 是 v2 的关键创新。它检查的不是代码质量，而是工程纪律：模板是否齐全？规格是否在代码之前存在？有没有遗留的 TODO？有没有旧品牌的残留？

### 5. 跨代理兼容

AGENTS.md 是代理无关的标准。CLAUDE.md 是 Claude 特定的路由层。其他代理只需要读 AGENTS.md 就能理解项目规则。

## 实际长什么样

`examples/minimal-project/` 里有一个完整的 Todo API 示例。结构：

```
examples/minimal-project/
├── AGENTS.md          # 填好项目信息的跨代理标准
├── CLAUDE.md          # 从模板直接复制的 Claude 路由层
├── Makefile           # 从模板直接复制的标准 Makefile
└── specs/
    └── 001-add-todo/
        ├── spec.md    # 功能规格：2 个用户场景，3 个功能需求
        ├── plan.md    # 技术方案：Go + chi + PostgreSQL，branch 级风险
        ├── tasks.md   # 任务 DAG：12 个任务，5 个并行波次
        ├── eval.md    # 评估：所有验收条件通过
        └── report.md  # 报告：10 个文件变更，3 个架构决策
```

这不是空壳。每个文件都填了具体的、可读的内容。新用户看完这个例子就知道 Harness 怎么用。

## v2 包含什么

**18 个模板文件**（全部在 `templates/`）：

核心生命周期模板（6 个）：PRD、SPEC、PLAN、TASKS、EVAL、REPORT

治理模板（2 个）：BLAST_RADIUS_POLICY、ROLE_POLICY

代理模板（2 个）：AGENTS.md（跨代理）、CLAUDE.md（Claude 路由层）

支撑模板（4 个）：QUICKSTART、CONTRACT、DATA_MODEL、CONSTITUTION

基础设施（4 个）：Makefile、.pre-commit-config.yaml、ARCHITECTURE.md、CONTRIBUTING.md

**2 个脚本**：classify-risk.sh（路径风险分类器）、verify-ai.sh（模板完整性检查器）

**1 个示例项目**：examples/minimal-project/（Todo API 完整生命周期示例）

## 快速上手

```bash
# 克隆仓库
git clone <repo-url> my-project
cd my-project

# 初始化
make init

# 创建第一个功能
make spec-init FEATURE=001-my-feature

# 填写 specs/001-my-feature/ 下的模板文件
# spec.md → 写用户场景和验收条件
# plan.md → 写技术方案和风险分级
# tasks.md → 写任务 DAG

# 验证
make verify
make verify-ai
```

## 和 v1 的对比

| 维度 | v1 | v2 |
|------|----|----|
| 驱动方式 | 提示词驱动 | 规格书驱动 |
| 需求管理 | 靠代理理解 | 模板强制填写 |
| 风险管理 | 无 | 四级爆炸半径分类 |
| 质量保证 | 靠代理自觉 | TDD 角色隔离 + 自动化门禁 |
| 代理兼容 | 仅 Claude | 任何读 AGENTS.md 的代理 |
| 可验证性 | 无 | make verify + make verify-ai |
| 示例项目 | 无 | 完整的 Todo API 示例 |

## 下一步

- **v2.5**：轻量级 hooks 和策略脚本
- **v3.0**：完整的 CLI / 运行时 / 评估器 / 上下文包生成器

---

*Harness v2.0.0 — Spec-governed, risk-classified engineering for AI agents.*
