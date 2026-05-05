看完了。**方向非常对，但我不建议现在 merge。**
这个 PR 已经把 Harness 从“模板仓库”真正 pivot 到了 **skill pack + thin deterministic CLI**，这一步是对的；但当前实现里有几个 P0 级路径/打包/策略加载问题，merge 后大概率会出现“README 很漂亮，但 CLI 一跑就找不到模板/资源”的情况。

我的 review 结论是：

```text
Architecture: APPROVE
Implementation: REQUEST CHANGES
Merge readiness: Not yet
```

---

## 这次 PR 做对了什么

首先，PR 的大方向是对的。PR 描述里已经把 v3 定义成 12 个 composable skills、thin deterministic CLI、Claude plugin registry、machine-parseable policies、skill installer、resources/templates，这正好对应我们刚刚讨论的“skills 负责判断，CLI 负责确定性门禁”。

README 的定位也改对了：从 “spec-governed template” 变成 “composable skill pack for governed AI engineering”，并且明确说它不是一个强制性 framework，而是一组可调用工具，没有 mandatory pipeline。这个叙事比 v2 强很多。

skills 的组织也基本对。比如 `harness-specify` 用 YAML frontmatter 写清楚 name/description/触发场景，并把 spec creation 拆成 context gathering、feature ID、SPEC_FORMAT、PRD_FORMAT、validation 这些明确步骤。

`harness-tasks` 吸收了 Matt Pocock 那套 vertical slice / tracer bullet 思想，明确禁止 horizontal slicing，并要求 exact file paths、parallel-safe `[P]`、HITL/AFK 分类。这个非常好，是 Harness 区别于普通 Spec Kit 的关键。

`harness-tdd` 也抓住了你自己的核心差异化：RED/GREEN/REFACTOR/REVIEWER 不是口号，而是 file-level boundaries，并且要求用 `harness verify-ai` 检查。

所以：**理念层、目录层、skill 层，我基本认可。问题主要在 runtime 和 packaging。**

---

## P0：必须修，否则不要 merge

### 1. CLI 仍然在找旧的 `templates/`，但 PR 已经迁到 `resources/templates/`

这是最严重的问题。

`cli.py` 里写的是：

```python
HARNESS_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = HARNESS_ROOT / "templates"
RESOURCES_DIR = HARNESS_ROOT / "resources"
POLICIES_DIR = RESOURCES_DIR / "policies"
SPECS_DIR = HARNESS_ROOT / "specs"
```

然后 `init()`、`specify()`、`verify-ai()` 都在读 `TEMPLATES_DIR`。但这个 PR 的实际文件已经迁到了 `resources/templates/`，而且很多核心 SPEC/PLAN/TASKS 资源是在 skills 目录里，不在旧的 `templates/` 下。结果是 `harness specify 001-x` 很可能只会创建空文件，并打印 “template not found”。

建议改成两个 root：

```python
DIST_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = git_root_or_cwd()

RESOURCES_DIR = DIST_ROOT / "resources"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
SKILLS_DIR = DIST_ROOT / "skills"
PROJECT_SPECS_DIR = PROJECT_ROOT / "specs"
```

CLI 的规则应该是：

```text
读 Harness 自带资源：DIST_ROOT/resources, DIST_ROOT/skills
写用户项目文件：PROJECT_ROOT/specs, PROJECT_ROOT/.harness
```

现在这两个概念混在一起了。

---

### 2. `init()` 会初始化 Harness 仓库本身，而不是当前用户项目

现在 `init()` 在 `HARNESS_ROOT` 下创建 `specs/ docs/ scripts/`，而 `HARNESS_ROOT` 是 `Path(__file__).resolve().parent.parent`。如果用户 `pip install -e .`，它大概率指向 Harness 源码仓库；如果未来打包安装，可能指向 site-packages 附近。总之，它不是用户当前项目。

`harness init` 应该默认初始化当前 git root 或当前工作目录：

```python
project_root = _git_root()
```

最好支持：

```bash
harness init .
harness init /path/to/project
```

并且只把少量项目内核写进去：

```text
.harness/
AGENTS.md
CLAUDE.md
Makefile
specs/
```

不要把 Harness 自己的 repo 当成 project root。

---

### 3. `verify-ai` 还是 v2 模板检查，不适配 skill-pack 架构

`verify.py` 现在还在检查这些旧文件：

```python
REQUIRED_TEMPLATES = [
    "AGENTS.md", "CLAUDE.md",
    "PRD_TEMPLATE.md", "SPEC_TEMPLATE.md", "PLAN_TEMPLATE.md",
    "TASKS_TEMPLATE.md", "BLAST_RADIUS_POLICY.md", "ROLE_POLICY.md",
    "EVAL_TEMPLATE.md", "REPORT_TEMPLATE.md",
]
```

但 v3 已经不是 `templates/` 为中心，而是 `skills/*/*/SKILL.md + resources/policies + resources/templates` 为中心。这个 verify 会误判新的 v3 结构失败。

v3 的 `verify-ai` 应改成检查：

```text
1. skills/*/*/SKILL.md exists
2. every SKILL.md has YAML frontmatter with name + description
3. description <= 1024 chars
4. .claude-plugin/plugin.json lists existing skill directories
5. resources/policies/blast-radius.yaml exists and parses
6. resources/policies/gates.yaml exists and parses
7. resources/templates/ contains required supporting templates
8. CLI commands are importable
9. no stale v2 template paths remain
```

保留对项目内 `specs/<feature>/spec.md/plan.md/tasks.md/eval.md/report.md` 的检查，但不要再要求 root `templates/PRD_TEMPLATE.md` 这种旧结构。

---

### 4. `risk.py` 没有真正使用 `blast-radius.yaml`

PR 里已经有 machine-parseable `resources/policies/blast-radius.yaml`，格式也不错：每个 risk level 有 priority、autonomy、pattern_groups、required_gates。

但 `risk.py` 里分类逻辑还是写死的 `PATTERNS`，并没有从这个 YAML 读取 pattern_groups。更糟的是，`get_gates()` 期待 YAML 里有 `risk_gate_map`，但实际 YAML 是 `risk_levels -> required_gates`，所以 gates 也不会按 policy 文件生效。

建议直接让 policy 成为 single source of truth：

```python
def load_blast_policy(path):
    data = yaml.safe_load(path.read_text())
    return data["risk_levels"]

def classify_file(path, policy):
    for level, spec in policy.items():
        for group in spec["pattern_groups"]:
            for pattern in group["patterns"]:
                if fnmatch.fnmatch(path, pattern):
                    return level, group["name"], pattern
    return "branch", "default", "*"
```

`required_gates` 也从同一个 risk level 里取。

---

### 5. packaging 当前会导致 resources / skills 不可用

`pyproject.toml` 只声明了 package `harness_runtime*`，并试图把 `../resources/policies/*.yaml` 作为 `harness_runtime` 的 package-data。这个写法很脆，wheel 构建时大概率不会把 repo root 下的 `skills/`、`resources/templates/`、`.claude-plugin/` 正确打进去。

如果 v3 是 skill pack，推荐两条路线选一条：

**路线 A：源码安装优先**

README 明确说：

```bash
git clone ...
cd Harness
pip install -e .
harness install-skills
```

这种情况下 CLI 可以从 repo root 读 `skills/` 和 `resources/`。

**路线 B：正式包内资源**

把资源移入 package：

```text
harness_runtime/
├── resources/
├── skills/
└── plugin/
```

然后用 `importlib.resources.files()` 读取，而不是 `Path(__file__).parent.parent`。

我建议当前先走路线 A，更符合你这个项目早期形态。等稳定后再做 pipx/uvx 分发。

---

### 6. skill 里的命令和 CLI 参数不一致

`harness-tdd` 里示例写的是：

```bash
harness verify-ai --role=TDD-RED --diff=HEAD~1
harness verify-ai --role=TDD-GREEN --diff=HEAD~1
```

但 `cli.py` 里的 `verify-ai` 只有 `--role`，没有 `--diff`。这会让 agent 按 skill 执行时直接报错。

要么删掉 `--diff`，要么实现：

```bash
harness verify-ai --role TDD-GREEN --base HEAD~1
```

我建议实现 `--base`，因为 TDD role boundary 最好就是检查上一 commit/diff：

```bash
harness verify-ai --role TDD-GREEN --base HEAD~1
harness classify-risk --base main
```

---

### 7. context command 还不是真正的 context bundle

`context.py` 目前只是读取 `spec.md/plan.md/tasks.md/eval.md/report.md`，截取前 500 bytes 打印。它没有生成 `context.md`，也没有包含 Must Read / Forbidden Context / policy / project_index / domain language。

这不是 blocker，但和 README 中 “minimal context bundle” 的承诺有差距。建议最小修成：

```bash
harness context 001-feature --write
```

生成：

```text
specs/001-feature/context.md
```

内容至少包含：

```text
Must Read:
- AGENTS.md
- skills/engineering/harness-*/SKILL.md relevant to phase
- specs/001-feature/spec.md
- specs/001-feature/plan.md
- specs/001-feature/tasks.md
- resources/policies/blast-radius.yaml

Forbidden Context:
- archived/
- 3rdParty/
- unrelated specs/
- generated build artifacts
```

---

### 8. installer 支持声明不一致

`scripts/link-skills.sh` 的注释说支持 `claude-code, codex, cursor, windsurf`，但 `case` 里没有 `windsurf`，未知 agent 会报错。Python 版 installer 也只支持 `claude-code/codex/cursor`。

要么加 windsurf，要么删掉文档里的 windsurf。小问题，但属于“信任感”问题。

---

## P1：merge 前最好补，但不一定阻塞

第一，补一个最小 smoke test。当前 PR 没看到测试/CI 状态，CLI 这种东西没有 smoke test 很危险。最低限度写：

```bash
python -m harness_runtime.cli --help
harness --help
harness classify-risk
harness verify-ai
harness specify 001-demo
```

第二，给 skill pack 做一个 integrity check：

```text
每个 skill 目录必须有 SKILL.md
每个 SKILL.md 必须有 name/description frontmatter
plugin.json 中每个 skill path 必须存在
skills bucket README 中列出的 skill 必须存在
```

第三，把 `harness eval` 从“文件是否存在”升级到“读 gates.yaml”。当前 `evals.py` 只检查五个 artifact 是否存在、tasks 里有没有 test 字符串、plan 有没有 rollback。作为第一版可以接受，但既然已经有 `resources/policies/gates.yaml`，就应该至少读它。

---

## 我会怎么改这个 PR

不要推倒重来。这个 PR 的架构形态已经对了，只需要做一个 “runtime correction pass”。

建议新增一个 commit：

```text
fix: align CLI runtime with skill-pack resources
```

内容包括：

```text
1. 把 HARNESS_ROOT 拆成 DIST_ROOT 和 PROJECT_ROOT。
2. 所有资源读取改到 resources/ 和 skills/。
3. specify() 从 resources/templates 或 skill reference templates 创建 specs。
4. verify-ai 改成 skill-pack integrity check。
5. risk.py 改为读取 resources/policies/blast-radius.yaml。
6. get_gates() 改为读取 risk_levels[level].required_gates。
7. 加 --base 参数，替代 skill 中的 --diff 说法。
8. 修 README / SKILL.md 中不一致的 CLI 参数。
9. 加最小 smoke test。
```

做完这一个 commit，我认为这个 PR 就可以 merge。

---

## 适合贴到 PR 里的 review comment

```markdown
Great direction. The architecture pivot to “skill pack + thin deterministic CLI” is the right move. The skill structure, plugin registry, vertical-slice tasking, TDD role isolation, and README positioning all match the intended v3 direction.

I would not merge this yet because the runtime still has several v2/template-era assumptions:

1. `harness_runtime/cli.py` defines `TEMPLATES_DIR = HARNESS_ROOT / "templates"`, but v3 moved assets into `resources/templates/` and skill directories. `harness specify` will likely create empty artifacts because it cannot find the old templates.
2. `init()` writes to `HARNESS_ROOT`, which is the Harness distribution/source root, not the user project root. It should write to the current git root or an explicit target path.
3. `verify-ai` still checks v2-style root templates (`SPEC_TEMPLATE.md`, `PLAN_TEMPLATE.md`, etc.) instead of validating skill-pack integrity (`skills/*/*/SKILL.md`, frontmatter, plugin registry paths, resources/policies).
4. `risk.py` hardcodes `PATTERNS` and does not actually use `resources/policies/blast-radius.yaml`. `get_gates()` expects `risk_gate_map`, but the policy file defines `risk_levels[].required_gates`.
5. `pyproject.toml` probably does not package `skills/`, `resources/templates/`, or `.claude-plugin/`, so installed CLI usage may not find the assets.
6. Skill docs call `harness verify-ai --diff=HEAD~1`, but the CLI does not support `--diff`. Either implement `--base` or remove that argument.
7. `context` currently prints artifact previews; it does not yet generate the promised context bundle with Must Read / Forbidden Context.

Recommended fix: add one runtime-correction commit that separates `DIST_ROOT` from `PROJECT_ROOT`, loads resources from `resources/`, validates skill-pack structure in `verify-ai`, reads `blast-radius.yaml` as the single source of truth, and adds a minimal smoke test.

Direction approved; implementation needs these fixes before merge.
```

---

## 最终判断

**这个 PR 值得保留，不要重写。**
它已经把 Harness 带到了正确产品形态：**skills 是认知层，CLI 是门禁层，project files 是证据层。**

但现在还不能 merge，因为 CLI 还停留在“旧模板仓库”的路径假设上。把 runtime 和 skill-pack 结构对齐后，这个 PR 就是一个很好的 v3 基线。

