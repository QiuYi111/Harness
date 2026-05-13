<div align="center">
  <h1>Harness</h1>
  <p>给你的 AI 编程助手加一层 PM。</p>
</div>

---

Harness 做一件事：让 AI 编程助手能够长期自主推进一个产品，同时不失控、不搞乱你的代码库。

你给一个模糊的目标——"帮我做一个记账 App"——Harness 接管剩下的工作：澄清产品定义、拆解任务、委派给工人 Agent 执行、审查产出、更新状态、循环推进。你可以离开，回来的时候看到的是清晰的进展、证据和下一步。

## 它不是什么

不是框架，不是平台，不是另一个项目管理工具。Harness 是一个 skill pack——一组装在你现有编程助手（OpenCode、Claude Code、Codex）里的技能。你的助手加载一个入口 skill，剩下的由路由器自动处理。

不强制走流程。如果你只是想修个 typo，不需要走产品发现。风险分类器会判断你的改动有多大的爆炸半径，然后决定需要多少过程。

## 三条路径

```text
产品进化（PM 循环）          功能构建（工程流）           调试修复（维修流）
───────────────────        ─────────────────         ─────────────────
grill-product → supervisor  specify → plan → tasks     reproduce → evidence → diagnose
  → intern → review           → risk → context → tdd    → patch → regression → review
  → state update → 循环        → eval → report           → (risk ≥ branch 时加 eval + report)
```

三条路径共享同一套风险分类体系，但在过程上有不同的侧重。

## 快速开始

```bash
git clone https://github.com/QiuYi111/Harness
cd Harness
pip install -e .
./scripts/link-skills.sh claude-code
```

然后在你常用的编程助手里输入 `/harness`，或者说一句你想做什么。路由器会检测你处于哪个阶段，加载对应的子技能。

> 目前只支持源码安装（`pip install -e .`）。wheel 打包计划中。

---

## 为什么需要这个

AI 编程助手完成一个明确的任务没问题。但如果你让它自主跑几个小时——修 bug、加功能、重构——很快就会出问题：

- 没有产品合同，Agent 会在第 10 轮开始偏航
- 没有状态追踪，中断后无法恢复
- 没有审查机制，Agent 会悄悄越界改不该改的东西
- 没有失败熔断，一个坏了的任务会反复重试直到烧光 token

Harness 解决这些问题。不是靠更聪明的 prompt，而是靠工程纪律。

---

## 我们做了什么

下面是我们在设计和实现中真正花心思的地方。不是营销话术，是实实在在的工程决策。

### 安全机制

**风险分类不是建议，是强制门禁。**

每一个改动在执行前都要经过爆炸半径分类。我们有四个等级：

| 等级 | 自主权 | 触及什么 | 必须通过的门禁 |
|------|--------|----------|----------------|
| `leaf` | 高 | 文档、测试、独立组件 | lint + 单元测试 |
| `branch` | 中 | 功能、服务、接口 | spec + plan + 测试 + review |
| `core` | 低 | 领域模型、权限、认证 | 人工审 spec + 架构审 + 回滚计划 + 安全审 |
| `infra` | 极低 | 部署、CI/CD、密钥 | 以上全部 + dry run + 明确人工签字 |

这些不是写在 README 里的指南，是机器可解析的策略文件（`blast-radius.yaml`、`gates.yaml`）。CLI 真正会读取它们、检查文件、阻止不符合要求的操作。拿不准的时候，自动升级到更高风险等级。

**连续失败熔断器。** Supervisor 循环追踪连续失败次数。同一个工人连续 3 次提交不合格的报告，循环自动停止，把问题交给人类。不是计数然后继续——是真的停下来。

**12 个停止条件。** 产品定位要变？停。MVP 边界要变？停。核心技栈要变？停。触及 core/infra 风险？停。涉及安全、认证、支付、部署？停。工人报告缺少证据？停。测试过不了且前路不明？停。不是建议性的——是硬停止。

**独立审查。** 当工人的声明具有实质影响（"所有测试通过"、"没有触碰禁止范围"），Supervisor 会启动一个独立的审查 Agent，专门验证这些声明。不是信任工人的报告——是独立核实。

**调试铁律。** 三条，不可违反：

```
1. 没有复现和证据，不写补丁。
2. 没有回归测试，不关闭问题。
3. 连续三个假设失败，停止并上报。
```

违反这些规则就不是在调试，是在瞎猜。第三条特别重要——连续三个补丁失败，说明问题可能出在架构层面，不是修修补补能解决的。这时候应该停下来讨论，而不是继续试。

### 性能

**上下文缓存工程。** LLM 提供商对缓存的前缀 token 收费更低。Harness 把上下文按稳定性分成四层：

```
稳定层（几乎不变）    → SKILL.md、策略文件、领域语言
半稳定层（偶尔变化）  → 架构文档、ADR 记录
活跃层（跟着功能走）  → spec、plan、tasks
动态层（每次调用都变）→ 用户请求、git diff、测试输出
```

顺序很重要：稳定在前，动态在后。这样做的好处是：

- 多轮对话中，前面的稳定内容不会因为后面的变化而失效
- Agent 不需要每轮重新读一遍协议文件
- 长会话中，稳定内容不太可能被上下文窗口截断丢失
- 同一个功能，每次组装出的上下文结构一致，行为可预测

这不是理论上的优化。`harness context --cache-aware` 真的会按照这个顺序组装上下文，`cache-context.yaml` 声明了每一层的文件范围。

**确定性优先。** 能用 CLI 做的事不用 Agent 判断。风险分类、spec 检查、gate 验证——这些都是确定性的，交给 `harness` CLI 命令处理。Agent 只负责需要判断的部分：写代码、理解需求、做产品决策。这样既省 token，又减少不确定性。

### 可恢复性

**状态机设计。** 整个 Supervisor 循环是一个显式的状态机，每一步都有对应的文件：

- `state.yaml` — 当前状态、迭代计数、失败追踪
- `loop-control` — 一个值：`CONTINUE` | `STOP` | `NEEDS_USER_DECISION` | `BLOCKED` | `STAGE_EXIT_REACHED`
- `loop-log.md` — 每次迭代的日志
- `handoff.md` — 当前的完整状态摘要，用于断点恢复

中断后恢复时，Supervisor 读 `handoff.md`、`state.yaml`、最近 3 条 `loop-log.md`，然后从上次停下的地方继续。不是猜测——是从文件中恢复确切的状态。

**工人角色隔离。** Supervisor 是 PM，Intern 是工程师。Supervisor 不写代码，Intern 不做产品决策。Supervisor 可以读 `.pm/` 文件、写任务包、审查报告、更新状态。但不能改产品定位、不能批 core/infra 风险、不能直接实现代码。这些权限边界写在 `authority.md` 里。

**文件写入规则。** 每一次状态变更必须有对应的 loop-log 条目。每一个任务包必须有验收标准。每一次验收审查必须有证据。不能凭空写"accepted"——必须附上验证了什么。

### Atlas：面向人的代码语义图谱

Harness 的大部分工作是让 Agent 更快地产出代码。Atlas 做的是相反的事——让你在不读源码的情况下，快速搞懂一段代码在做什么。

Atlas 把源代码转换成结构化的语义图谱：Mermaid 图、结构化表格、伪代码。14 个 section，从一屏摘要到最终审计结论。它不是代码注释生成器——它是一个代码审计工具。

**为什么这很重要。** PM 循环让 Agent 自动跑，但你是人。你回来的时候需要回答一个问题："这些 Agent 到底干了什么？"读 git diff 不够——你需要理解代码的行为、状态、副作用、风险。Atlas 就是为此设计的。

**忠实性高于完整性。** Atlas 有五条绝对禁止规则：

```
1. 禁止把最佳实践当作已实现代码 — 除非看到对应的 if/else 或 throw
2. 禁止把注释意图当作运行时行为 — 注释是意图，不是证据
3. 禁止为图表完整性编造流程 — 代码里没有的节点、边、分支，不画
4. 禁止省略简单函数 — getter/setter 必须出现在函数表和调用图中
5. 禁止泛泛夸奖式解释 — 每个结论绑定代码证据
```

三级置信度标注：代码明确实现（无标签）、推断自命名（`推测`）、无法从当前片段判断（`无法判断`）。每一条不确定的内容都必须标注——不是可选的。

**14 个 section 的设计哲学是"图 > 表 > 文"。** Mermaid 图用于展示模块关系、执行流程、数据流、状态机、调用图。结构化表格用于状态变量、函数契约、副作用、风险。自然语言文本只用于伪代码步骤和审计结论。绝对禁止为每个函数写散文式解释。

**7 条跨 section 一致性规则。** 函数调用图的函数集合 = 函数契约总表的函数集合。状态变量表的变量必须出现在数据流图中。风险矩阵的涉及函数必须存在于函数契约总表中。Dashboard 的风险等级必须与风险矩阵最高等级一致。这些规则确保 14 个 section 之间不自相矛盾。

Atlas 支持两个粒度：单个文件级别和整个项目级别。用法：

```bash
harness atlas src/pid_controller.h              # 单文件
harness atlas src/auth.py --strict               # 严格模式（推测内容不得出现在图表中）
harness atlas lib/*.ts --diagram-heavy           # 图表占比 ≥ 80%
harness atlas src/main.go --spec docs/reqs.md    # 对照需求规格审计
```

### 测试

我们写了 1,590 行测试来验证 PM runtime 的行为——状态解析、循环控制、委派路由、健康检查、工人报告校验、分支策略验证、失败断路器、恢复上下文生成。每一个安全机制都有对应的测试。

---

## 子技能

以下是 Harness 内部的 19 个子技能。你不需要手动选择——路由器会根据你的阶段自动加载。

### 产品进化

| 子技能 | 做什么 |
|--------|--------|
| **grill-product** | 7 道关卡的产品发现，确认值不值得做、给谁做、做什么、不做什么 |
| **supervisor** | PM 循环：观察 → 决策 → 写任务 → 委派 → 审查报告 → 更新状态 |
| **intern** | 工人：读任务 → 风险分类 → 实现 → 测试 → 验证 → 写报告 |
| **opencode-cli** | 编程式调用 OpenCode 的命令参考，用于跨 Agent 委派 |

### 功能构建

| 子技能 | 做什么 |
|--------|--------|
| **specify** | 写功能规格——用户故事、场景、验收标准 |
| **plan** | 实现计划——架构影响、DDD 层影响、回滚方案 |
| **tasks** | 纵切任务图——依赖关系、可并行标记、精确文件路径 |
| **tdd** | 角色隔离的 TDD——RED/GREEN/REFACTOR/REVIEWER，文件边界强制执行 |
| **eval** | 对照规格评估实现，检查过程合规性 |
| **report** | 实现报告——改了什么、风险多高、怎么回滚 |

### 调试修复

| 子技能 | 做什么 |
|--------|--------|
| **maintain-debug** | 系统化调试——7 阶段状态机、3 条铁律、可追踪的维修记录 |

### 横切关注点

| 子技能 | 做什么 |
|--------|--------|
| **risk** | 爆炸半径分类，决定需要走哪些门禁 |
| **context** | 最小上下文打包，减少 Agent 的上下文污染 |
| **cache** | 缓存友好的上下文组装，稳定内容优先 |
| **domain-language** | DDD 统一语言、CONTEXT.md、ADR 记录 |
| **grill** | 用尖锐的问题压力测试你的计划或规格 |
| **architecture-review** | 找浅模块、DDD 依赖违规、可测试性缺陷 |
| **init** | 用 Harness 工程纪律初始化一个项目 |
| **atlas** | 代码语义图谱——把源码转换成 Mermaid 图 + 表格 + 伪代码，让人不读源码也能审计代码行为 |

---

## CLI

确定性的操作交给 CLI，不需要 Agent 判断的就不让 Agent 判断。

```bash
harness status                     # 查看当前活跃功能和门禁状态
harness classify-risk              # 根据修改文件分类爆炸半径
harness verify-ai                  # 检查 skill pack 完整性 + 角色边界
harness init                       # 初始化项目
harness specify 001-feature        # 创建功能骨架
harness eval 001-feature           # 规符合规性检查
harness context 001-feature        # 生成最小上下文包
harness context 001-feature --cache-aware --write  # 缓存友好的上下文包
harness cache-report               # 按缓存层级拆解 token 用量
harness pm-status                  # PM 循环健康检查
harness pm-next                    # 确定性的下一步决策
harness pm-resume                  # 中断后的恢复上下文
harness pm-branch-plan             # 只读的分支纠正计划
harness pm-summary                 # 循环运行的审计摘要
harness atlas src/controller.py    # 生成代码语义图谱（单文件）
harness atlas src/ --diagram-heavy # 生成项目级语义图谱（图表优先）
```

---

## 目录结构

```
Harness/
├── SKILL.md                  # 入口路由器
├── subskills/                # 19 个内部子技能（按需加载）
│   ├── grill-product/        # 产品发现（7 道关卡）
│   ├── supervisor/           # PM 循环（8 步迭代）
│   │   └── references/       # 权限矩阵、循环步骤、安全机制
│   ├── intern/               # 工人执行
│   ├── atlas/               # 代码语义图谱（14 section，5 条忠实性铁律）
│   ├── maintain-debug/       # 调试流（7 阶段，3 铁律）
│   ├── tdd/                  # 角色隔离 TDD
│   └── ...                   # specify, plan, tasks, risk, context, cache,
│                              # eval, report, grill, architecture-review,
│                              # domain-language, init, opencode-cli
├── references/               # 共享策略、模板、路由表
│   ├── ROUTING_TABLE.md      # 意图→技能映射
│   ├── PHASE_DETECTION.md    # 阶段检测规则
│   ├── AUTOPILOT_RULES.md    # 各风险等级的自动推进规则
│   ├── CACHE_GUIDE.md        # 缓存工程指南
│   ├── GETTING_STARTED.md    # 从零开始指南
│   ├── policies/             # blast-radius, gates, cache-context, project_index
│   ├── templates/            # 项目脚手架模板
│   │   └── pm/               # 24 个 PM 循环状态模板
│   └── examples/             # 最小项目示例
├── scripts/
│   ├── harness_runtime/      # Python CLI 模块
│   └── link-skills.sh        # 技能安装脚本
├── tests/                    # PM runtime 测试（1,590 行）
├── Makefile                  # test, verify-ai, pm-status, …
├── .claude-plugin/           # 插件注册（harness 为唯一入口）
├── CHANGELOG.md
├── VERSION
└── README.md
```

---

## 它怎么工作

```
用户说"帮我做个记账 App"
        │
        ▼
  harness 路由器检测阶段
        │
        ▼
  产品定义缺失 → 加载 grill-product
        │
        ▼
  7 道关卡跑完 → 冻结 .pm/stable/ 产品合同
        │
        ▼
  加载 supervisor，开始 PM 循环
        │
   ┌────┴────┐
   │         │
   ▼         ▼
 写任务包   检查就绪状态
   │         │
   ▼         │
 委派给     │
 intern ────┘
   │
   ▼
 intern 执行：风险分类 → 实现 → 测试 → 验证 → 写报告
   │
   ▼
 supervisor 审查报告
   │
   ├── 通过 → 更新状态 → 下一轮迭代
   ├── 不通过 → 写返工意见 → consecutive_failures++
   └── 连续 3 次不通过 → 停止，交给人类
```

---

## v3 → v4 变了什么

| v3 | v4 |
|---|---|
| 功能流 + 调试流 | 产品进化流 + 功能流 + 调试流 |
| 单功能管道 | Supervisor–Intern 委派模型 + `.pm/` 状态管理 |
| 14 个子技能 | 19 个子技能（+grill-product, supervisor, intern, opencode-cli, atlas） |
| 没有 PM 循环 | 24 个 PM 模板、5 个 PM CLI 命令、1,590 行测试 |
| 9 个 CLI 命令 | 14 个 CLI 命令 |
| 没有缓存工程 | 四层上下文排序 + `harness cache-report` |
| 只有英文文档 | 中文入门指南（586 行） |

50 个 commit，181 个文件变更，+12,255 / -2,477 行。

详细变更记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 许可

MIT
