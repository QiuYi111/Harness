可以。我的建议是：**debugging 不要做成“另一个 feature flow”，而要做成“维护事务 / repair transaction”。**

核心思想：

```text
每一次 debug 都是一条可追踪的维修记录：
症状 → 复现 → 证据 → 根因 → 最小修复 → 回归测试 → diff review → 关闭
```

Superpowers 的 `systematic-debugging` 强在“no fixes before root cause investigation”，很适合作为方法论内核；Harness 则负责把它变成文件、gate、路由和状态机。

---

# 1. 总体定位

原来的 Harness 绿地流是：

```text
spec → plan → tasks → tdd → eval → report
```

新的 debugging flow 应该是：

```text
intake → reproduce → evidence → diagnose → patch → regression → review → close
```

对应关系大概是：

| 绿地工程 | Debug / 维护                |
| -------- | --------------------------- |
| spec     | symptom + expected behavior |
| plan     | hypothesis + diagnosis      |
| tasks    | minimal patch steps         |
| eval     | regression check            |
| report   | maintenance record          |

所以 debugging 不是独立世界，而是 Harness 的维护模式。

---

# 2. Harness 源码里的文件夹设计

在 Harness repo 里加这些：

```text
Harness/
├── subskills/
│   └── harness-maintain-debug/
│       ├── SKILL.md
│       └── references/
│           ├── upstream-systematic-debugging.md
│           ├── root-cause-tracing.md
│           └── dap-debugging-optional.md
│
├── references/
│   ├── templates/
│   │   ├── DEBUG_RECORD_TEMPLATE.md
│   │   ├── DEBUG_INDEX_TEMPLATE.md
│   │   └── DEBUG_REPRO_TEMPLATE.md
│   │
│   ├── policies/
│   │   ├── debug-gates.yaml
│   │   └── blast-radius.yaml
│   │
│   └── licenses/
│       └── MIT-superpowers-systematic-debugging.txt
│
└── scripts/
    └── harness_runtime/
        ├── debug.py          # later
        └── cli.py            # later add debug command
```

第一版最小实现甚至只需要：

```text
subskills/harness-maintain-debug/SKILL.md
references/templates/DEBUG_RECORD_TEMPLATE.md
references/templates/DEBUG_INDEX_TEMPLATE.md
```

`debug.py` 和 CLI 可以晚点再加。先让 skill 跑起来。

---

# 3. 目标项目里的文件夹设计

当某个项目使用 Harness 时，debug 记录放在项目根目录：

```text
project/
├── specs/
│   └── ...
│
├── maintenance/
│   ├── README.md
│   ├── index.md
│   │
│   └── debug/
│       ├── 2026-05-05-cache-aware-write/
│       │   ├── record.md
│       │   ├── repro.md
│       │   ├── evidence/
│       │   │   ├── failure.log
│       │   │   ├── stacktrace.txt
│       │   │   ├── git-diff-before.patch
│       │   │   └── notes.md
│       │   ├── regression.md
│       │   └── review.md
│       │
│       └── 2026-05-06-flaky-login-test/
│           ├── record.md
│           ├── repro.md
│           ├── evidence/
│           ├── regression.md
│           └── review.md
│
├── AGENTS.md
├── CLAUDE.md
└── .harness/
    └── policies/
```

我建议不要把 debug 放进 `specs/`。
原因是：`specs/` 是“我要建什么”；`maintenance/` 是“哪里坏了，怎么修的”。

这两个心智模型不同，别混。

---

# 4. Debug 记录的最小结构

每个 debug 任务一个目录：

```text
maintenance/debug/<date>-<slug>/
```

例如：

```text
maintenance/debug/2026-05-05-cache-aware-context-write/
```

里面核心文件是 `record.md`：

```md
# Debug Record: cache-aware context write

## Status

- [ ] Intake
- [ ] Reproduced
- [ ] Evidence collected
- [ ] Root cause identified
- [ ] Minimal patch applied
- [ ] Regression verified
- [ ] Diff reviewed
- [ ] Closed

## Symptom

What is visibly wrong?

## Expected Behavior

What should happen?

## Actual Behavior

What actually happens?

## Reproduction

Exact command, input, environment, and observed output.

## Evidence

Logs, stack traces, debugger observations, failing tests, git diff, or runtime state.

## Root Cause

The real cause, not just the symptom.

## Hypotheses Tried

| # | Hypothesis | Evidence | Result |
|---|---|---|---|
| 1 | | | |

## Minimal Patch

What changed, and why this is the smallest sufficient change.

## Regression Test

What fails before the patch and passes after the patch?

## Diff Review

- [ ] No unrelated refactor
- [ ] No unrelated formatting
- [ ] No public API change, or API change is documented
- [ ] Existing tests still pass
- [ ] Regression test added or documented
- [ ] Rollback path is obvious

## Risk

leaf / branch / core / infra

## Follow-up

Things intentionally not fixed in this patch.
```

这个文件就是 debug 版的 `report.md`，但更轻。

---

# 5. 工作流设计

## Phase 0：Intake / 建立维修单

触发条件：

```text
bug
test failure
regression
not working
unexpected behavior
debug this
修一下
为什么失败
```

Harness router 应该进入：

```text
harness-maintain-debug
```

然后做两件事：

```text
1. 确定 debug id
2. 创建 maintenance/debug/<id>/record.md
```

命名规则：

```text
YYYY-MM-DD-short-slug
```

例如：

```text
2026-05-05-cache-aware-write
2026-05-05-failing-router-test
2026-05-06-openai-api-timeout
```

---

## Phase 1：Reproduce / 复现

第一条铁律：

```text
不能复现，不能修。
```

当然有些 bug 是 flaky 或环境依赖，这时候也不是马上修，而是进入 evidence gathering。

输出格式：

```text
Reproduction status:
- deterministic / flaky / not reproduced

Command:
...

Expected:
...

Actual:
...
```

对应文件：

```text
maintenance/debug/<id>/repro.md
```

可以写：

```md
# Reproduction

## Command

```bash
harness context demo --cache-aware --write
```

## Expected

Generated `context.md` should contain cache-aware layers and fingerprints.

## Actual

Generated `context.md` uses normal context formatting.

## Determinism

Reproduces every time.

```

---

## Phase 2：Evidence / 证据收集

第二条铁律：

```text
先证据，后假设。
```

证据可以是：

```text
error log
stack trace
failing test
git diff
runtime state
debugger breakpoint
call stack
nearby working example
```

对应目录：

```text
maintenance/debug/<id>/evidence/
```

比如：

```text
evidence/
├── failure.log
├── stacktrace.txt
├── relevant-files.md
├── git-diff-before.patch
└── debugger-notes.md
```

对于小 bug，可以不拆文件，直接写在 `record.md` 的 Evidence 部分。

---

## Phase 3：Diagnose / 根因定位

这一步必须输出一个明确根因：

```text
Root cause:
...
```

以及至少一个假设：

```text
Hypothesis:
I think X is the root cause because Y.

Prediction:
If X is true, then observing Z should confirm it.
```

如果有多个假设，必须逐个测试，不允许一次性改一堆。

规则：

```text
一个假设 → 一个最小验证
失败就回到 Evidence
不能叠 patch
```

这里直接吸收 Superpowers 的精神：在完成 root cause investigation 前，不允许提出修复。

---

## Phase 4：Patch / 最小修复

第三条铁律：

```text
只修根因，不做顺手重构。
```

Patch 输出必须包含：

```text
Patch intent:
Changed files:
Behavior changed:
Behavior preserved:
Why this is minimal:
```

禁止：

```text
顺手重构
顺手格式化
顺手升级依赖
顺手改 API
顺手重命名
删除测试换绿色
```

这一步可以调用原来的 Harness risk：

```bash
harness classify-risk
```

如果风险升到 `core` 或 `infra`，debug flow 自动中断，要求人工确认。Harness 已经有 risk-classified autonomy 的设计。

---

## Phase 5：Regression / 回归验证

第四条铁律：

```text
修 bug 必须留下防复发证据。
```

优先级：

```text
1. 自动化测试：最好
2. deterministic repro script：可以接受
3. 手动检查：只能作为临时证据，不能长期依赖
```

对应文件：

```text
maintenance/debug/<id>/regression.md
```

模板：

```md
# Regression

## Failing-before condition

Before the patch, this command failed:

```bash
...
```

## Passing-after condition

After the patch, this command passes:

```bash
...
```

## Test Added

* file:
* test name:
* what it protects:

## Remaining Blind Spots

...

```

---

## Phase 6：Diff Review / 审查

第五条铁律：

```text
debug 完成前必须审 diff。
```

要求 agent 运行或读取：

```bash
git diff
```

然后回答：

```text
1. 有没有无关文件？
2. 有没有无关格式化？
3. 有没有 public API 变化？
4. 有没有删除旧行为？
5. 有没有新增 regression？
6. rollback 怎么做？
```

对应文件：

```text
maintenance/debug/<id>/review.md
```

模板：

```md
# Debug Diff Review

## Changed Files

| File | Reason |
|---|---|

## Unrelated Changes

None / List here.

## Public API Impact

None / Describe.

## Compatibility Impact

None / Describe.

## Test Evidence

...

## Rollback

Revert commit / revert files / disable flag.

## Reviewer Notes

...
```

---

## Phase 7：Close / 关闭维修单

关闭条件：

```text
- bug 可复现，或者不可复现原因已记录
- 根因写清楚
- patch 是最小的
- regression 通过
- diff review 完成
- 风险级别明确
```

关闭时更新：

```text
maintenance/index.md
```

例如：

```md
# Maintenance Index

| Date | ID | Type | Status | Risk | Summary |
|---|---|---|---|---|---|
| 2026-05-05 | cache-aware-write | debug | closed | leaf | Fixed cache-aware context write formatting |
```

---

# 6. 状态机设计

Debug record 可以有状态：

```text
intake
reproducing
not-reproduced
reproduced
diagnosing
root-caused
patching
regression
review
closed
escalated
```

状态流：

```text
intake
  ↓
reproducing
  ├─ not-reproduced → evidence-needed
  └─ reproduced
        ↓
diagnosing
        ↓
root-caused
        ↓
patching
        ↓
regression
        ↓
review
        ↓
closed
```

失败升级：

```text
hypothesis failed once → return to evidence
hypothesis failed twice → re-read code and compare working examples
three failed patches → escalate to architecture-review
```

这条很重要。debug 最怕 AI 连续糊墙。

---

# 7. Router 规则

更新：

```text
references/ROUTING_TABLE.md
```

加入：

```md
| User Intent | First Skill | Then |
|---|---|---|
| "debug this" | harness-maintain-debug | reproduce -> evidence -> diagnose -> patch -> regression -> review |
| "test failed" | harness-maintain-debug | reproduce -> diagnose -> regression |
| "bug" | harness-maintain-debug | reproduce -> evidence -> minimal patch |
| "regression" | harness-maintain-debug | compare recent changes -> reproduce -> patch -> regression |
| "flaky" | harness-maintain-debug | collect evidence -> isolate nondeterminism -> add stability check |
```

Phase detection 也要加：

```md
## Maintenance Debug Phase

Signals:
- user mentions bug, failing test, regression, unexpected behavior
- existing codebase
- fix request without new feature intent
- stack trace / error log present

Action:
- use `harness-maintain-debug`
- create or update `maintenance/debug/<id>/record.md`
```

---

# 8. CLI 设计：先轻后重

第一版不建议上复杂 CLI。
但可以设计接口，后面再实现。

## MVP CLI

```bash
harness debug new cache-aware-write
harness debug status
harness debug check cache-aware-write
```

### `harness debug new <slug>`

生成：

```text
maintenance/debug/YYYY-MM-DD-<slug>/
├── record.md
├── repro.md
├── evidence/
├── regression.md
└── review.md
```

### `harness debug status`

输出所有 debug 记录：

```text
open:
  2026-05-05-cache-aware-write    reproduced    leaf
  2026-05-06-login-flaky          diagnosing     branch

closed:
  ...
```

### `harness debug check <id>`

检查：

```text
record.md exists
reproduction section non-empty
evidence section non-empty
root cause section non-empty
regression section non-empty
review section non-empty
```

先不要做太智能。确定性检查就够。

---

# 9. Debug gates 设计

新增：

```text
references/policies/debug-gates.yaml
```

内容可以这样：

```yaml
debug_gates:
  reproduce:
    required_before: patch
    checks:
      - maintenance/debug/{id}/record.md contains "## Reproduction"
      - maintenance/debug/{id}/repro.md exists

  evidence:
    required_before: patch
    checks:
      - maintenance/debug/{id}/record.md contains "## Evidence"

  root_cause:
    required_before: patch
    checks:
      - maintenance/debug/{id}/record.md contains "## Root Cause"

  regression:
    required_before: close
    checks:
      - maintenance/debug/{id}/regression.md exists
      - maintenance/debug/{id}/record.md contains "## Regression Test"

  diff_review:
    required_before: close
    checks:
      - maintenance/debug/{id}/review.md exists
      - maintenance/debug/{id}/record.md contains "## Diff Review"

  escalation:
    rule: "if failed_patch_attempts >= 3, require architecture_review"
```

不要一开始做成太复杂的 evaluator。
先用文本 presence check，后面再升级成语义检查。

---

# 10. 和原有 Harness risk 的关系

Debug flow 自己不替代 risk。

它应该在两个点调用 risk：

## Patch 前

```bash
harness classify-risk
```

判断这次修复会不会从小 bug 变成大改。

## Review 前

再次检查 diff：

```bash
harness classify-risk
harness verify-ai
```

如果改动文件属于 `core` / `infra`，即使是 debug，也必须升级 gate。

规则：

```text
debug 不是低风险豁免。
bug fix 也可能是 core/infra change。
```

---

# 11. 推荐的最小落地版本

你现在不要一下子做完整系统。
我建议第一版只做这 4 个文件：

```text
subskills/harness-maintain-debug/SKILL.md
references/templates/DEBUG_RECORD_TEMPLATE.md
references/templates/DEBUG_INDEX_TEMPLATE.md
references/ROUTING_TABLE.md
```

项目侧只生成：

```text
maintenance/debug/<id>/record.md
```

不用拆 `repro.md / regression.md / review.md`。
等你自己用几次发现记录变长，再拆。

MVP 项目结构：

```text
project/
└── maintenance/
    ├── index.md
    └── debug/
        └── 2026-05-05-cache-aware-write.md
```

成熟后再升级为：

```text
project/
└── maintenance/
    └── debug/
        └── 2026-05-05-cache-aware-write/
            ├── record.md
            ├── repro.md
            ├── evidence/
            ├── regression.md
            └── review.md
```

---

# 12. 最终推荐形态

我会把 debugging flow 定义成 Harness 的第二条主线：

```text
Harness Feature Flow:
idea → spec → plan → tasks → implementation → eval → report

Harness Debug Flow:
symptom → reproduce → evidence → root cause → minimal patch → regression → review
```

一个负责“造东西”，一个负责“修东西”。

最重要的规则就三条：

```text
1. No patch before reproduction/evidence.
2. No completion before regression.
3. No continued patching after repeated failed hypotheses; escalate.
```

这样 Harness 就不会只是绿地开工系统，而会变成你真正需要的东西：

> **AI coding 的个人维修日志 + 变更控制台。**
>
