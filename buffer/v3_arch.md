
我现在更倾向于你说的：**应该放在 `skills/harness/subskills/`，而不是 `skills/engineering/`。**

原因很简单：这些 subskills 不是一组平级公开 skills，而是 `harness` root skill 的渐进式披露模块。既然 agent 默认只加载 `harness` 一个入口，那么它们在语义上就应该是 **Harness 内部模块**，而不是散落在全局 skill taxonomy 里。

我之前说 `skills/engineering/`，主要是沿用了 mattpocock/skills 那种按领域 bucket 分类的方式。但你的项目已经不只是“很多独立 skills 的集合”，而是：

```text
一个 root skill
  + 一组 internal subskills
  + 一套 resources
  + 一个 thin CLI
```

所以更好的结构是：

```text
skills/
└── harness/
    ├── SKILL.md                 # 唯一默认入口
    ├── ROUTING_TABLE.md
    ├── PHASE_DETECTION.md
    ├── AUTOPILOT_RULES.md
    ├── CACHE_GEOMETRY.md
    │
    └── subskills/
        ├── specify/
        │   ├── SKILL.md
        │   ├── SPEC_FORMAT.md
        │   └── PRD_FORMAT.md
        ├── plan/
        │   ├── SKILL.md
        │   ├── PLAN_FORMAT.md
        │   └── RISK_GUIDE.md
        ├── tasks/
        │   ├── SKILL.md
        │   ├── TASKS_FORMAT.md
        │   └── VERTICAL_SLICE_GUIDE.md
        ├── tdd/
        │   ├── SKILL.md
        │   ├── ROLE_POLICY.md
        │   └── TESTING_GUIDE.md
        ├── risk/
        │   ├── SKILL.md
        │   └── BLAST_RADIUS_GUIDE.md
        ├── context/
        │   ├── SKILL.md
        │   └── CONTEXT_GUIDE.md
        ├── cache/
        │   ├── SKILL.md
        │   ├── CONTEXT_ORDER.md
        │   └── EXAMPLES.md
        ├── eval/
        ├── report/
        ├── domain-language/
        ├── grill/
        ├── architecture-review/
        └── init/
```

这样有几个明显好处。

第一，**符合 progressive disclosure**。
agent 只看到：

```text
skills/harness/SKILL.md
```

然后 root skill 里明确说：

```text
When planning is needed, read subskills/plan/SKILL.md.
When TDD is needed, read subskills/tdd/SKILL.md.
When cache/context optimization is needed, read subskills/cache/SKILL.md.
```

这比在 plugin registry 里暴露 12 个平级 skills 更干净。

第二，**避免 skill discovery 噪声**。
如果全部放在 `skills/engineering/harness-*`，agent 或插件系统可能会把它们都当成可独立触发技能。那就会出现：

```text
用户说“实现这个功能”
agent 可能直接触发 harness-tdd
也可能触发 harness-plan
也可能触发 harness-tasks
也可能触发 harness
```

这会让路由变混乱。
而 `skills/harness/subskills/` 语义上就是：**这些不是入口，它们是 root skill 的内部工具。**

第三，**cache geometry 更稳定**。
稳定前缀只需要：

```text
skills/harness/SKILL.md
skills/harness/ROUTING_TABLE.md
skills/harness/PHASE_DETECTION.md
```

子技能按需读。
如果 12 个 skills 都放在顶层 buckets，agent 可能会在 skill discovery 阶段加载/比较多个 descriptions，前缀就会变脏。

第四，**项目品牌更统一**。
`skills/engineering/` 看起来像“这个仓库是很多工程 skills 的合集”。
`skills/harness/` 看起来像“这是一个完整的 Harness system”。
你现在的定位显然是后者。

所以我建议改成：

```text
skills/harness/
├── SKILL.md
├── subskills/
└── references/
```

更进一步，甚至可以把 root-level references 和 subskills 分开：

```text
skills/harness/
├── SKILL.md
├── references/
│   ├── ROUTING_TABLE.md
│   ├── PHASE_DETECTION.md
│   ├── AUTOPILOT_RULES.md
│   └── CACHE_GEOMETRY.md
└── subskills/
    ├── specify/
    ├── plan/
    ├── tasks/
    ├── risk/
    ├── context/
    ├── cache/
    ├── tdd/
    ├── eval/
    ├── report/
    ├── grill/
    ├── domain-language/
    ├── architecture-review/
    └── init/
```

`plugin.json` 就应该只暴露一个：

```json
{
  "name": "harness",
  "description": "Cache-friendly engineering governance for AI coding agents.",
  "skills": [
    "./skills/harness"
  ]
}
```

如果某些 agent 的机制要求每个 skill 都注册，才做兼容版：

```json
{
  "skills": [
    "./skills/harness",
    "./skills/harness/subskills/specify",
    "./skills/harness/subskills/plan",
    "./skills/harness/subskills/tasks"
  ]
}
```

但文档上必须声明：

```text
The root `harness` skill is the only public entry point.
Subskills are internal modules and should be loaded only when routed by `harness`.
```

一句话：
**`skills/engineering/` 是 skill collection 的结构；`skills/harness/subskills/` 是 skill system 的结构。**

你现在做的是 Harness system，不是散装 skills collection。所以应该用后者。

