对，**现在缺的就是一个“入口 skill / bootloader skill”**。

你现在的 12 个 skills 像一组工具函数：

```text
harness-specify
harness-plan
harness-tasks
harness-tdd
harness-risk
harness-eval
harness-report
harness-context
...
```

但缺少一个东西告诉 agent：

```text
现在该用哪个 skill？
是否应该先建 spec？
是否已经有 plan？
是否要 classify-risk？
是否要进入 TDD？
是否已经该 eval/report？
```

所以要加一个总 skill，名字我建议就叫：

```text
harness
```

或者更明确一点：

```text
harness-main
```

但我更推荐 **`harness`**。因为用户最自然会说：

```text
use harness
按 Harness 流程做
帮我用 Harness 接管这个任务
```

---

## 这个总 skill 的定位

它不是第 13 个“大而全 skill”。

它应该是一个 **router / bootloader / autopilot**：

```text
harness = detect phase → load right skill → run deterministic CLI gate → continue
```

它自己不写 SPEC，不写 PLAN，不写 TASKS，不写 REPORT。
它只判断当前任务处在哪一阶段，然后调用对应 skill。

也就是：

```text
harness skill 负责“何时用什么”
子 skill 负责“具体怎么做”
CLI 负责“确定性检查”
```

---

## 应该新增的目录

```text
skills/
└── engineering/
    └── harness/
        ├── SKILL.md
        ├── ROUTING_TABLE.md
        ├── PHASE_DETECTION.md
        └── AUTOPILOT_RULES.md
```

然后 `.claude-plugin/plugin.json` 里把它放在第一个：

```json
{
  "name": "harness-skills",
  "description": "A composable skill pack for governed AI engineering.",
  "skills": [
    "./skills/engineering/harness",
    "./skills/engineering/harness-specify",
    "./skills/engineering/harness-plan",
    "./skills/engineering/harness-tasks",
    "./skills/engineering/harness-tdd",
    "./skills/engineering/harness-risk",
    "./skills/engineering/harness-eval",
    "./skills/engineering/harness-report",
    "./skills/engineering/harness-context",
    "./skills/engineering/harness-cache",
    "./skills/engineering/harness-domain-language",
    "./skills/productivity/harness-grill",
    "./skills/productivity/harness-architecture-review",
    "./skills/misc/harness-init"
  ]
}
```

---

## `harness/SKILL.md` 可以这样写

````markdown
---
name: harness
description: Entry point and router for Harness-governed AI engineering. Use automatically for software engineering tasks, feature implementation, bug fixes, refactors, architecture changes, repository initialization, spec/plan/task workflows, risk classification, TDD, evaluation, reporting, or when the user says "use Harness", "按 Harness 流程", "接管这个任务", "implement this", "fix this", or "review this".
---

# Harness Entry Skill

You are the Harness router. Your job is to detect the current engineering phase, load the appropriate Harness skill, and run deterministic CLI gates when useful.

Do not duplicate the detailed instructions of sub-skills. Route to them.

## First Move

For any coding or repository task:

1. Detect whether the current repository has Harness installed.
2. If not installed, use `harness-init`.
3. If installed, run or suggest:

```bash
harness status
````

4. Identify the current phase:

   * no spec
   * spec exists, no plan
   * plan exists, no tasks
   * tasks exist, implementation needed
   * implementation exists, eval/report needed
   * review/refactor needed
   * architecture unclear
   * context polluted
   * cache/context optimization needed

5. Load the appropriate sub-skill.

## Routing

| Situation                             | Use Skill                               |
| ------------------------------------- | --------------------------------------- |
| New idea / fuzzy feature              | `harness-grill`, then `harness-specify` |
| Feature needs formal spec             | `harness-specify`                       |
| Spec exists, implementation unclear   | `harness-plan`                          |
| Plan exists, work needs decomposition | `harness-tasks`                         |
| About to change code                  | `harness-risk`                          |
| Implementing with tests               | `harness-tdd`                           |
| Need minimal context                  | `harness-context`                       |
| Need cache-friendly context           | `harness-cache`                         |
| Need domain terms / ADRs              | `harness-domain-language`               |
| Implementation finished               | `harness-eval`, then `harness-report`   |
| Architecture feels messy              | `harness-architecture-review`           |
| New repository                        | `harness-init`                          |

## Autopilot Rules

* If the task involves code changes, classify risk before implementation.
* If no spec exists and the change is not trivial leaf work, create a spec first.
* If risk is `core` or `infra`, require human approval before implementation.
* If the user asks for speed, use the shortest safe path, not no process.
* If current context is large or messy, generate a context bundle first.
* If tests are involved, use role-isolated TDD.
* If implementation is done, produce eval and report evidence.

## Deterministic CLI Calls

Use CLI for checks, not reasoning:

```bash
harness status
harness classify-risk
harness verify-ai
harness eval <feature-id>
harness context <feature-id>
harness report <feature-id>
```

## Stop Conditions

Stop and ask for human input when:

* core or infra risk requires approval
* product scope is ambiguous
* acceptance criteria conflict
* the requested change violates role boundaries
* implementation would require changing tests during GREEN

````

---

## 自动化逻辑：agent 应该自己做什么？

你说“应该让 agent 自己自动做”，这个完全对。

但要区分：

```text
可以自动做的
````

和

```text
必须停下来问人的
```

### 可以自动做

```text
1. 检测是否有 Harness 项目结构
2. 检测当前 feature 是否已有 spec/plan/tasks
3. 运行 harness status
4. 运行 harness classify-risk
5. 生成 context bundle
6. 对 leaf/branch 级任务创建 spec/plan/tasks 草案
7. 对 leaf 级修改直接走最短路径
8. 实现后运行 eval/report
```

### 不能自动越过

```text
1. core 风险的人类审查
2. infra 风险的人类批准
3. 产品范围冲突
4. 安全/权限/数据迁移
5. 修改测试来迎合实现
```

所以总 skill 的心智模型应该是：

```text
默认自动推进，遇到风险门禁才停。
```

不是每步都问用户。

---

## `PHASE_DETECTION.md`

这个文件很关键。它告诉 agent 如何判断当前阶段。

```markdown
# Phase Detection

Determine the current Harness phase by checking repository artifacts.

## No Harness

Signals:
- no `.harness/`
- no `AGENTS.md`
- no `specs/`
- no Harness skills installed

Action:
- use `harness-init`

## Intake Phase

Signals:
- user describes idea
- no feature id
- no `specs/<feature>/spec.md`

Action:
- if fuzzy, use `harness-grill`
- then use `harness-specify`

## Spec Phase

Signals:
- `spec.md` exists
- `plan.md` missing or empty

Action:
- use `harness-plan`

## Planning Phase

Signals:
- `plan.md` exists
- `tasks.md` missing or empty

Action:
- use `harness-tasks`

## Implementation Phase

Signals:
- `tasks.md` exists
- code changes requested
- no eval/report yet

Action:
- use `harness-risk`
- use `harness-context`
- use `harness-tdd` if tests are involved

## Verification Phase

Signals:
- implementation exists
- tests pass or user asks if complete
- `eval.md` missing/incomplete

Action:
- use `harness-eval`

## Reporting Phase

Signals:
- eval complete
- PR/review/merge requested
- report missing/incomplete

Action:
- use `harness-report`

## Architecture Review Phase

Signals:
- user says codebase is messy
- large refactor
- unclear module boundaries
- DDD violation suspected

Action:
- use `harness-architecture-review`

## Cache/Context Phase

Signals:
- context is too large
- agent is repeatedly reading same files
- user asks about cache/cost/token reduction
- feature has stable specs but dynamic logs/diffs

Action:
- use `harness-cache`
- then `harness-context`
```

---

## `ROUTING_TABLE.md`

这个更像查表：

```markdown
# Harness Routing Table

| User Intent | First Skill | Then |
|---|---|---|
| “build this feature” | harness | grill/specify → plan → tasks → risk |
| “fix this bug” | harness-risk | context → tdd → eval/report |
| “review this PR” | harness-risk | eval → report → architecture-review |
| “make a plan” | harness-plan | tasks |
| “break into tasks” | harness-tasks | risk |
| “use TDD” | harness-tdd | eval/report |
| “this repo is messy” | harness-architecture-review | domain-language |
| “reduce token cost” | harness-cache | context |
| “initialize repo” | harness-init | domain-language |
```

---

## `AUTOPILOT_RULES.md`

这个文件最有价值。它让 agent 不用每一步都问你。

```markdown
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

For leaf changes such as docs, typo fixes, tests, isolated scripts:

- Do not force full SPEC → PLAN → TASKS lifecycle.
- Classify risk.
- Make change.
- Run relevant verification.
- Write short report only if user asks or PR requires it.

## Branch Path

For feature-level work:

- spec required
- plan required
- tasks required
- eval/report required before merge

## Core Path

For domain/auth/schema/permission changes:

- spec required
- plan required
- rollback plan required
- human approval required before implementation
- eval/report required

## Infra Path

For CI/CD/deployment/secrets/migration:

- dry run required
- rollback plan required
- explicit human approval required
- security review required

## Never Ask If You Can Infer

Do not ask the user for:
- feature id if one can be generated
- file paths if repo structure reveals them
- test command if Makefile exposes it
- risk level if classify-risk can determine it
- context files if context bundle can be generated

Ask only when:
- scope is ambiguous
- risk gate requires human approval
- business/product decision is unclear
- tests and requirements conflict
```

这段非常符合你想要的“agent 自己自动做”。

---

## 总 skill 和 cache engineering 的关系

你刚才说 cache engineering，这里正好嵌进去。

总 skill 的第一步不应该是“读所有东西”，而是：

```text
先确定阶段 → 再加载最小 skill → 再生成 cache-aware context
```

也就是说：

```text
harness entry skill
  ↓
phase detection
  ↓
route to sub-skill
  ↓
harness-context / harness-cache
  ↓
implementation
```

这样不会每次把 12 个 skills 全塞进上下文。
总 skill 只做 **稳定小前缀**，其它按需加载。

这才是真正的 cache-friendly skill system。

---

## 总 skill 的 description 要非常小心

它要足够宽，能自动触发；但不能大到让 agent 每次闲聊都加载。

我建议 description 写成：

```yaml
description: Entry point and router for Harness-governed software engineering. Use automatically for coding tasks, feature implementation, bug fixes, refactors, architecture reviews, repository initialization, spec/plan/task workflows, TDD, risk classification, evaluation, reporting, context management, or when the user asks to use Harness.
```

这个范围够宽，但仍限定在 software engineering。

---

## PR #1 应该怎么改

在当前 PR 上加一个 commit：

```text
feat: add Harness entry skill and autopilot router
```

改动：

```text
1. 新增 skills/engineering/harness/
2. 新增 SKILL.md / ROUTING_TABLE.md / PHASE_DETECTION.md / AUTOPILOT_RULES.md
3. plugin.json 把 harness 放第一位
4. README 加 “Entry Skill / Autopilot” 小节
5. harness-init 或 README 说明：agent 应先加载 harness，再由 harness 路由
```

README 里加这段：

```markdown
## Entry Skill

Most users do not need to choose a skill manually.

Invoke `harness`, or let your agent load it automatically for software engineering tasks. The entry skill detects the current phase, routes to the right sub-skill, and runs deterministic CLI gates where useful.

Harness is therefore both composable and automatic:

- composable when you know exactly what you need
- automatic when you just want the agent to proceed safely
```

---

## 最终架构变成这样

```text
harness                  # entry/router/autopilot skill
├── harness-grill         # clarify fuzzy requirements
├── harness-specify       # write spec
├── harness-plan          # write plan
├── harness-tasks         # task DAG
├── harness-risk          # classify blast radius
├── harness-context       # assemble context
├── harness-cache         # stabilize prefix/cache geometry
├── harness-tdd           # role-isolated implementation
├── harness-eval          # verify product + process
├── harness-report        # evidence package
├── harness-domain-language
└── harness-architecture-review
```

这就完整了。

---

## 一句话

你现在缺的不是更多 subskills，而是一个 **Harness bootloader**。

它的职责是：

```text
自动判断阶段，自动选择 skill，自动运行 gate，遇到高风险再停下来。
```

这样 Harness 才不是“12 个散装技能”，而是一套真正能被 agent 自动执行的工程操作系统。

