能做到，**但不是你脑子里那种“跨项目语义复用理解”的神奇 cache**。

更准确地说：

> **Harness 能做的不是“让模型记住所有相似仓库”，而是把 agent 每次请求前半段变得稳定、可重复、可命中、少探索。**

这件事是真的能做，而且很有价值。
但它的价值不是 100% 保证 API cache hit，而是同时带来三种收益：

```text
1. 更高 prompt/cache 命中概率
2. 更少 agent 探索 token
3. 更低误读仓库结构的概率
```

---

# 1. 先讲清楚：LLM cache 到底缓存什么？

主流 prompt caching/cache context 本质上缓存的是：

```text
请求前缀 prefix
```

不是缓存“含义”，不是缓存“这个项目我懂了”，更不是跨用户共享记忆。

DeepSeek 官方说得很直接：如果后续请求和之前请求有 overlapping prefixes，重叠部分可以从缓存里取；但 cache hit 要求后续请求完整匹配已经持久化的 cache prefix unit。它还会在请求边界、共同前缀、固定 token 间隔处持久化 cache prefix unit，并在 usage 里返回 `prompt_cache_hit_tokens` 和 `prompt_cache_miss_tokens`。([DeepSeek API Docs][1])

OpenAI 的 prompt caching 也是 prefix 型：cache hit 依赖 exact prefix matches，建议把静态 instructions/examples 放前面，变量内容放后面；缓存从 1024 tokens 起，以 128-token 增量命中。([OpenAI Platform][2])

Anthropic 的 prompt caching 更显式：它缓存 `tools → system → messages` 这个顺序里的 prompt prefix，直到带 `cache_control` 的 breakpoint；默认缓存时间是 5 分钟，适合大量上下文、固定 instructions、多轮重复任务。([Claude API Docs][3])

所以一句话：

```text
cache 吃的是“稳定前缀”，不是“相似语义”。
```

---

# 2. Harness 到底能优化什么？

一个 coding agent 请求，大概长这样：

```text
[系统指令]
[工具定义]
[agent rules / skills]
[项目协议 AGENTS.md / CLAUDE.md]
[仓库结构说明]
[风险策略]
[任务规范]
[当前 feature spec]
[当前 diff]
[当前报错]
[用户这次的问题]
```

里面有些东西是高度稳定的：

```text
skills/engineering/harness-tdd/SKILL.md
skills/engineering/harness-risk/SKILL.md
AGENTS.md
CACHE.md
blast-radius policy
role policy
task format
Makefile command surface
```

有些东西是半稳定的：

```text
project_index/repo.md
project_index/modules/recommendation.md
docs/ARCHITECTURE.md
specs/001-feature/spec.md
specs/001-feature/plan.md
```

有些东西是极其动态的：

```text
current diff
latest test log
报错堆栈
用户刚刚补充的话
```

**cache engineering 的核心就是：稳定的放前面，动态的放后面，并且永远按同一个顺序拼接。**

也就是：

```text
Stable Prefix
  ↓
Semi-Stable Project Context
  ↓
Active Feature Context
  ↓
Dynamic Suffix
```

Harness 能做的事情，就是把这套顺序标准化。

---

# 3. 一个具体例子

假设没有 Harness，agent 每次工作时 prompt 可能是这样：

```text
这次先读 README
再读 package.json
然后看看 src
哦等等，用户说用 TDD
再临时解释一下测试规范
再找一下 Makefile
再翻一下 docs
再看报错
```

每次顺序都不一样。
cache 很难命中。
agent 也会乱探索。

有 Harness 后，context assembler 永远生成：

```text
00_SYSTEM_AND_TOOLS
01_HARNESS_SKILLS
  - harness-risk/SKILL.md
  - harness-tdd/SKILL.md
  - harness-tasks/SKILL.md

02_PROJECT_PROTOCOL
  - AGENTS.md
  - CACHE.md
  - .harness/policies/blast-radius.yaml
  - .harness/policies/roles.yaml

03_PROJECT_MAP
  - project_index/repo.md
  - project_index/modules/current-module.md

04_ACTIVE_FEATURE
  - specs/001-add-todo/spec.md
  - specs/001-add-todo/plan.md
  - specs/001-add-todo/tasks.md

05_DYNAMIC_SUFFIX
  - current user request
  - current git diff
  - current test log
```

这样前面 01、02、甚至 03 的一部分会在大量请求中保持一致。
如果你用的是 API，provider cache 更容易吃到。
如果你用的是 Claude Code / Cursor / Codex，即使它们内部不暴露 cache，你也减少了 agent 自己找文件、猜规则、重复读项目的成本。

---

# 4. 所以“跨仓库 cache 复用”能不能做？

能，但要分层说。

## 不能做到的

不能指望：

```text
A 仓库写过 Todo API
B 仓库也有 Todo API
所以模型直接 cache 复用 A 的业务理解
```

这不成立。
因为 provider caching 看的是 prefix match，不是“项目相似”。OpenAI 文档明确强调 exact prefix matches；DeepSeek 也是 prefix unit 完整匹配。([OpenAI Platform][2])

## 能做到的

可以让不同仓库共享稳定的工程前缀：

```text
同一套 skill 文本
同一套 risk policy
同一套 role policy
同一套 task format
同一套 Makefile command surface
同一套 spec/plan/tasks/eval/report artifact shape
同一套 context assembly order
```

也就是说：

```text
业务层不一定 cacheable
工程操作层可以 cacheable
```

这就是 Harness 的准确价值。

---

# 5. Cache 管理系统应该怎么 work？

我会把 Harness 的 cache 管理系统设计成 5 个部分。

---

## Part A：`CACHE.md`

每个项目根目录有一个很短的协议文件：

```markdown
# CACHE.md

This repository is optimized for cache-friendly agentic coding.

## Context Order

1. Harness skill instructions
2. AGENTS.md
3. CACHE.md
4. .harness/policies/blast-radius.yaml
5. .harness/policies/roles.yaml
6. project_index/repo.md
7. project_index/modules/*.md
8. active specs/<feature>/spec.md
9. active specs/<feature>/plan.md
10. active specs/<feature>/tasks.md
11. dynamic diff / logs / user request

## Rules

- Stable content goes first.
- Dynamic content goes last.
- Sort file lists lexicographically.
- Do not put timestamps in stable files.
- Do not rewrite stable policy files unless necessary.
- Append ADRs instead of rewriting architecture history.
- Ignore generated folders: node_modules, dist, build, .git, coverage.
```

它的作用不是给人看的，是给 agent 和 context builder 看：

```text
以后你每次拼 prompt，都按这个顺序。
```

---

## Part B：`cache-context.yaml`

机器可读配置：

```yaml
stable_prefix:
  - skills/engineering/harness-risk/SKILL.md
  - skills/engineering/harness-tdd/SKILL.md
  - skills/engineering/harness-tasks/SKILL.md
  - AGENTS.md
  - CACHE.md
  - .harness/policies/blast-radius.yaml
  - .harness/policies/roles.yaml

semi_stable_context:
  - project_index/repo.md
  - project_index/modules/*.md
  - docs/ARCHITECTURE.md
  - docs/adr/*.md

active_feature_context:
  - specs/{feature}/spec.md
  - specs/{feature}/plan.md
  - specs/{feature}/tasks.md

dynamic_suffix:
  - current_user_request
  - git_diff
  - test_logs
  - error_messages

ignore:
  - .git/**
  - node_modules/**
  - dist/**
  - build/**
  - coverage/**
  - 3rdParty/**
```

这个文件就是 Harness 的 cache geometry 配置。

---

## Part C：`harness context`

CLI 负责确定性拼接。

```bash
harness context 001-add-todo --write
```

生成：

```text
specs/001-add-todo/context.md
```

内容不是随便 summary，而是固定结构：

```markdown
# Context Bundle: 001-add-todo

## 00 Stable Harness Prefix

- skills/engineering/harness-risk/SKILL.md
- skills/engineering/harness-tdd/SKILL.md
- skills/engineering/harness-tasks/SKILL.md

## 01 Stable Project Protocol

- AGENTS.md
- CACHE.md
- .harness/policies/blast-radius.yaml
- .harness/policies/roles.yaml

## 02 Semi-Stable Project Map

- project_index/repo.md
- project_index/modules/todo.md

## 03 Active Feature Context

- specs/001-add-todo/spec.md
- specs/001-add-todo/plan.md
- specs/001-add-todo/tasks.md

## 04 Dynamic Suffix

- current user request
- current diff
- latest test logs

## Forbidden Context

- node_modules/
- dist/
- build/
- 3rdParty/
- unrelated specs/
```

关键点是：**顺序稳定**。

---

## Part D：fingerprint

每一层都算 hash：

```json
{
  "stable_prefix_hash": "a12f...",
  "project_protocol_hash": "b91c...",
  "project_map_hash": "c38d...",
  "feature_context_hash": "e71a...",
  "dynamic_suffix_hash": "changes-every-time"
}
```

这有什么用？

它可以告诉 agent：

```text
stable_prefix 没变，不要重读。
project_map 没变，不要重新探索。
feature_context 变了，只需要读 spec/plan/tasks。
dynamic_suffix 变了，只处理当前 diff/log。
```

如果走 API，你也可以用这个 hash 作为类似 `prompt_cache_key` 的组成部分。OpenAI 文档提到 `prompt_cache_key` 可以影响路由并改善共享长前缀请求的 cache hit 率。([OpenAI Platform][2])

---

## Part E：metrics

如果用 API，可以记录：

```text
prompt_cache_hit_tokens
prompt_cache_miss_tokens
cached_tokens
latency
cost
```

DeepSeek 会返回 `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`。([DeepSeek API Docs][1])
OpenAI usage 里有 `prompt_tokens_details.cached_tokens`。([OpenAI Platform][2])

Harness 可以做一个命令：

```bash
harness cache-report
```

输出：

```text
Cache Report

Stable prefix: 8,420 tokens
Project protocol: 2,130 tokens
Feature context: 4,800 tokens
Dynamic suffix: 1,200 tokens

Last 20 API calls:
- avg cached tokens: 9,600
- avg miss tokens: 3,100
- estimated cache ratio: 75.6%
```

这才是真正的 cache engineering 闭环。

---

# 6. 这个系统对 Claude Code / Cursor 这种 agent 有用吗？

有用，但收益分两类。

## API 层收益

如果你自己调用 OpenAI / DeepSeek / Anthropic API，并控制 prompt 组装，那么收益最直接：

```text
稳定 prefix → 更高 cache hit → 更低输入成本 / 更低延迟
```

## Agent UI / CLI 层收益

如果你用 Claude Code、Cursor、Codex 这种工具，你不一定能控制它内部怎么拼 prompt，也未必能看到 cache metrics。

但仍然有收益：

```text
1. agent 知道固定读哪些文件
2. agent 少做 repo exploration
3. agent 少重复解释规则
4. agent 更少把动态内容塞进稳定上下文
5. agent 更容易遵守角色和风险边界
```

所以它不是“只有 API 才有用”。
API 下是 cache hit；agent 工具下是 context discipline。

---

# 7. 最重要的工程原则

## 原则 1：stable first

稳定内容放前面：

```text
skills
AGENTS.md
CACHE.md
policies
repo map
```

## 原则 2：dynamic last

动态内容放最后：

```text
diff
logs
error
current user request
```

## 原则 3：append, don’t rewrite

稳定文件不要经常重写。

比如 ADR：

```text
坏：
每次修改 ARCHITECTURE.md 全文

好：
docs/adr/001-storage.md
docs/adr/002-auth.md
docs/adr/003-cache.md
```

append-only 对 cache 更友好。

## 原则 4：sort everything

文件列表固定排序：

```text
AGENTS.md
CACHE.md
project_index/repo.md
project_index/modules/a.md
project_index/modules/b.md
specs/001/spec.md
```

不要让文件顺序随 agent 心情变化。

## 原则 5：separate protocol from evidence

协议稳定：

```text
risk policy
role policy
task format
```

证据动态：

```text
eval result
test output
diff summary
```

不要把动态 test logs 写进 AGENTS.md / CLAUDE.md / policy。

---

# 8. 最小实现版本

你现在不用做大系统。最小可行 cache management 只需要 4 个东西：

```text
1. skills/engineering/harness-cache/SKILL.md
2. resources/templates/CACHE.md
3. resources/policies/cache-context.yaml
4. harness context --cache-aware --write
```

`harness-cache/SKILL.md` 负责告诉 agent：

```text
什么时候优化 cache
怎么组织 context
什么放前面
什么放后面
哪些文件不要乱改
```

`harness context` 负责确定性生成 context bundle。

这就够了。

---

# 9. 这个东西是不是噱头？

如果你说：

```text
Harness 能让所有项目业务代码跨仓库 cache 复用
```

那是噱头。

如果你说：

```text
Harness 标准化 agent 工作时反复读取的工程前缀，
从而减少上下文浪费，提高 prompt cache 命中机会，
降低 agent 探索成本和误改概率。
```

这不是噱头，这很实。

因为 agentic coding 的真实消耗不是只有“写代码”：

```text
读规则
找入口
理解目录
确认测试命令
理解任务格式
确认风险边界
读错误日志
生成修改计划
```

Harness 正是在压缩这些重复成本。

---

# 10. 最终一句话

我会把这个系统叫：

```text
Cache-aware context assembly
```

而不是简单叫 prompt caching。

因为 Harness 真正控制的是：

```text
上下文如何被组织
哪些内容稳定
哪些内容动态
哪些内容跨项目复用
哪些内容必须隔离
```

最准确的定位是：

> **Harness turns repository convention into cache geometry.**

中文：

> **Harness 把仓库规范变成了 agent 的缓存几何。**

再直白点：

> **坏仓库结构，在 agent 时代就是 token 债务。Harness 的作用，就是把这笔债提前还掉。**

[1]: https://api-docs.deepseek.com/guides/kv_cache/?utm_source=chatgpt.com "Context Caching | DeepSeek API Docs"
[2]: https://platform.openai.com/docs/guides/prompt-caching/overview?utm_source=chatgpt.com "Prompt caching - OpenAI API"
[3]: https://docs.anthropic.com/es/docs/build-with-claude/prompt-caching?utm_source=chatgpt.com "Caché de prompts - Anthropic"

