# Changelog

All notable changes to Harness are documented here.

## [4.0.0] — 2025-05-13

### Breaking Changes

- **Supervisor PM Loop replaces single-feature flow.** Harness is no longer just a spec→plan→task pipeline. It now governs long-running product delivery through a supervisor–intern delegation model with `.pm/` state management.
- **Plugin registers one skill, not twelve.** `.claude-plugin/plugin.json` now exposes only `harness` as the sole entry point. All subskills are internal progressive-disclosure modules loaded by the router.
- **CLI module moved.** `harness_runtime/` relocated to `scripts/harness_runtime/`. Any external imports will break.

### New Features

#### Product Evolution (PM Loop)

- **`harness-grill-product`** — Seven-gate product discovery skill. Determines whether a product is worth building, freezes a `.pm/stable/` product contract, and initializes `.pm/runtime/state.yaml`. Routes to supervisor on completion.
- **`harness-supervisor`** — Low-token PM loop skill. Reads `.pm/` state files, generates bounded task packets, delegates to OpenCode Intern via Task tool or `opencode run`, reviews worker reports, and updates state. Includes iteration limits, consecutive failure breaker, branch correction plans, and hard review gates.
- **`harness-intern`** — Worker execution skill. Reads `next-task.md`, follows Harness engineering process (risk classify → implement → test → verify → report), writes structured `worker-report.md`. Cannot make product decisions or expand scope.
- **`opencode-cli`** — CLI reference subskill for programmatic OpenCode invocation. Covers `serve`, `run --attach`, non-interactive mode, and delegation from Codex/Claude Code.

#### PM Runtime Helpers (CLI)

- `harness pm-status` — Runtime health-check
- `harness pm-next` — Deterministic next-action decision
- `harness pm-resume` — Resume context for interrupted loops
- `harness pm-branch-plan` — Read-only branch correction plan
- `harness pm-summary` — Audit summary of a supervisor loop run

#### Debug Flow

- **`harness-maintain-debug`** — Systematic debugging as a tracked maintenance transaction with 3 Iron Laws: no patch without evidence, no close without regression, escalate after 3 failed hypotheses. Full state machine with resumability.
- Debug record templates: `DEBUG_INDEX_TEMPLATE.md`, `DEBUG_RECORD_TEMPLATE.md`

#### Code Semantic Atlas

- **`harness-atlas`** — Converts source code into structured semantic atlases for human verification without reading source code. Produces 14 sections: dashboard summary, module diagrams, execution flowcharts, data flow diagrams, state machine diagrams, call graphs, state variable tables, function contract tables, side-effect matrices, risk matrices, requirement conformance, coverage matrices, pseudocode, and audit conclusions.
- **Faithfulness system** — Five absolute prohibitions (no best-practice-as-code, no comment-as-behavior, no fabricated flows, no omitted simple functions, no vague praise). Three-level confidence annotation (confirmed / inferred / unknown). Seven cross-section consistency rules ensuring no contradictions across the 14 sections.
- **`--strict` mode** — Inferred content banned from Mermaid diagrams (text-only), all unconfirmed behaviors must be annotated, risk recommendations must bind to code evidence.
- **`--diagram-heavy` mode** — Graphs + tables ≥ 80% of output, natural language minimized.
- **`--spec <path>`** — Audit against explicit requirement specification for requirement conformance matrix.
- **Risk catalog** (`references/RISK_CATALOG.md`) — 16 risk categories with detection hints, common scenarios, and suggested tests.
- **Output template** (`templates/semantic_atlas.md`) — Full 14-section template with placeholder guidance.
- **Faithfulness rules** (`references/FAITHFULNESS_RULES.md`) — 265-line reference covering confidence classification, absolute prohibitions, graph faithfulness, coverage rules, and strict mode additions.
- **Language support** — Python, TypeScript/JavaScript, C/C++, Rust, Go with language-specific extraction rules.

#### Cache-Aware Context

- **Cache engineering guide** (`references/CACHE_GUIDE.md`) — Four-layer context ordering (stable → semi-stable → active → dynamic) for prompt cache optimization.
- `cache-context.yaml` policy declaring layer membership.
- `harness cache-report` — Token breakdown by cache layer.
- `harness context <id> --cache-aware --write` — Cache-friendly context bundle.

#### Reference Documentation

- **`references/GETTING_STARTED.md`** — Zero-to-running guide (Chinese). Covers OpenCode setup, AI provider selection, Harness installation, first project, debugging.
- **`references/PHASE_DETECTION.md`** — Deterministic phase detection from repo artifacts. Covers all phases: no-Harness, product discovery, supervisor loop, worker execution, feature lifecycle, debug, planning.
- **`references/ROUTING_TABLE.md`** — Complete intent-to-skill mapping table covering product evolution, feature lifecycle, debug, refactor, review, and planning intents.
- **`references/AUTOPILOT_RULES.md`** — Auto-advance rules by risk level. Fast path for leaf work, standard path for branch, mandatory gates for core/infra.

#### Templates & Examples

- PM templates: `references/templates/pm/` — 24 templates covering product contracts, stage definitions, state files, loop logs, worker configs, acceptance rubrics, handoff notes, and more.
- Minimal project example: `references/examples/minimal-project/` — Complete example with AGENTS.md, Makefile, spec, plan, tasks, eval, and report.
- Project `Makefile` with targets: `test`, `verify-ai`, `pm-status`, `pm-next`, `pm-resume`, `pm-branch-plan`, `pm-summary`, `verify`.

#### Testing

- `tests/test_pm_runtime.py` — 1,590 lines of PM runtime validation tests covering state management, loop control, delegation routing, and health checks.

### Improvements

- **Risk classification hardened.** Unknown paths now default to `branch` risk (not `leaf`). Blast-radius policy expanded with explicit path patterns.
- **Installer writes absolute paths.** `link-skills.sh` no longer produces relative symlinks that break when cwd changes.
- **Subskills are NOT auto-loaded.** Root SKILL.md now explicitly warns that `subskills/` are internal modules. Router loads them on demand only.
- **Supervisor protocol hardened.** Slash-command routing, environment-aware delegation (Task tool vs `opencode run`), independent review gate before delegation.
- **Worker report validation strengthened.** Supervisor rejects reports with missing sections, verifies evidence, and can request rework.
- **Consecutive failure breaker.** Supervisor stops the loop after consecutive failed iterations, preventing runaway delegation.
- **Branch correction plans.** Supervisor can generate read-only plans to course-correct when branches diverge from expected state.

### Removed

- `IMPLEMENTATION_GUIDE.md` — Replaced by `references/GETTING_STARTED.md`
- `templates/` directory (top-level) — Moved to `references/templates/`
- `resources/` directory — Merged into `references/`
- Old bucket-organized skill directories (`skills/engineering/`, `skills/productivity/`, `skills/misc/`) — Flattened into `subskills/`
- `.pre-commit-config.yaml` template — Removed from templates

### Commits Since v3.0.0

50 commits, 181 files changed, 12,255 insertions, 2,477 deletions.

---

## [3.0.0] — 2026-04-28

### Changed

- Restructured from bucket-organized directories to flat `subskills/` + `references/`.
- Plugin registers single `harness` entry point instead of 12 separate skills.
- Python CLI with 9 commands replacing bash scripts.
- Templates as resources, skills as source of truth.
- Added debug flow with 3 Iron Laws and 7-phase state machine.

---

## [2.0.0] — 2026-04-27

### Changed

- Spec-governed, risk-classified engineering harness.
- 12 flat skills, 18 template files.
