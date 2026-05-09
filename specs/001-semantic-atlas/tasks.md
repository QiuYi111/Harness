# Tasks: Code Semantic Atlas (001-semantic-atlas)

## Format

```
- [ ] T001 [P] [US1] Description with exact file path
```

## Phase 1: Setup — Directory Structure & Templates

```
- [ ] T001 Create subskill directory: subskills/semantic-atlas/SKILL.md, subskills/semantic-atlas/references/, subskills/semantic-atlas/templates/, subskills/semantic-atlas/examples/
- [ ] T002 [P] Create output structure template: subskills/semantic-atlas/templates/semantic_atlas.md — all 14 sections with placeholder markers
- [ ] T003 [P] Create faithfulness rules doc: subskills/semantic-atlas/references/FAITHFULNESS_RULES.md — extracted from PRD §6.2, §6.3
- [ ] T004 [P] Create risk catalog: subskills/semantic-atlas/references/RISK_CATALOG.md — extracted from PRD §12.10 common risks
- [ ] T005 [P] Create output structure reference: subskills/semantic-atlas/references/OUTPUT_STRUCTURE.md — all 14 sections with field definitions from PRD §12.1–12.14
```

## Phase 2: Core Skill Prompt (SKILL.md)

```
- [ ] T006 [US1] [US2] Write the full SKILL.md prompt: subskills/semantic-atlas/SKILL.md. This is the intellectual core. Must include: role definition, graph>table>text priority, all 14 section specs, faithfulness rules, coverage requirements, Mermaid syntax rules, Chinese output, audit-style writing. Reference OUTPUT_STRUCTURE.md, FAITHFULNESS_RULES.md, RISK_CATALOG.md via relative paths. ~200-300 lines.
```

## Phase 3: CLI Integration

```
- [ ] T007 [US1] Add semantic_atlas module: scripts/harness_runtime/semantic_atlas.py — language detection (extension→language map), output path resolution, template loading, prompt assembly. Functions: detect_language(filepath)→str, resolve_output_path(input_path, output_dir)→Path, load_template()→str, assemble_prompt(source_code, language, template, options)→str.
- [ ] T008 [US1] Add CLI subcommand to scripts/harness_runtime/cli.py — register `semantic-atlas` command with click. Arguments: files (nargs=-1). Options: --spec, --output, --format, --changed-only, --summary, --language, --strict, --verify-mermaid, --diagram-heavy, --no-long-text. Implementation: validate files exist, detect languages, load SKILL.md + template, print assembled prompt, create output dir.
- [ ] T009 [US3] Add Mermaid validation helper: scripts/harness_runtime/mermaid_verify.py — function verify_mermaid_syntax(mermaid_text)→(bool, str). Uses `mmdc` if available, otherwise basic syntax checks (matching braces, valid keywords). Returns (is_valid, error_message).
```

## Phase 4: Routing & Discovery

```
- [ ] T010 [P] Add routing entry to references/ROUTING_TABLE.md — new row in Review/Status or new "Analysis" section: | "semantic atlas" / "audit this code" / "semantic map" / "代码语义地图" | harness-semantic-atlas | (generates atlas, human reviews) |
- [ ] T011 [P] Add skill name to .claude-plugin/plugin.json — register `harness-semantic-atlas` skill entry so the agent discovers the subskill.
```

## Phase 5: Test Fixture & Tests

```
- [ ] T012 [P] Create PID controller fixture: subskills/semantic-atlas/examples/pid_controller.h — minimal C++ header with PIDController class, 5 methods (compute, enable, disable, reset, constructor), 5+ state variables (_integral, _prevError, _output, _enabled, _setpoint + gains).
- [ ] T013 [US4] Create test: tests/test_semantic_atlas_cli.py — test CLI invocation with fixture file, verify output path created, verify language detection, verify template loaded, verify prompt assembled.
- [ ] T014 [P] [US4] Create test: tests/test_semantic_atlas_structure.py — test that output template contains all 14 required section headers, test language detection map covers all MVP extensions, test output path resolution for nested files.
- [ ] T015 [P] [US3] Create test: tests/test_mermaid_verify.py — test basic Mermaid syntax validation (valid flowchart, invalid syntax, stateDiagram-v2).
```

## Phase 6: Verification

```
- [ ] T016 Run `make verify` — ensure existing tests still pass
- [ ] T017 Run `harness semantic-atlas subskills/semantic-atlas/examples/pid_controller.h` — verify CLI works end-to-end
- [ ] T018 Fill eval.md with results
- [ ] T019 Fill report.md with evidence
```

## Dependencies

```
T001 → T002, T003, T004, T005 (setup must exist before content)
T002, T003, T004, T005 → T006 (templates/refs must exist for SKILL.md to reference)
T006 → T007 (SKILL.md must exist for prompt assembly)
T007 → T008 (module must exist before CLI command uses it)
T008 → T010, T011 (CLI must work before routing/discovery)
T012 → T013 (fixture must exist before test uses it)
T001 → T014, T015 (structure must exist for structure tests)
T013, T014, T015 → T016 (tests must exist before verification)
T016 → T017 → T018 → T019 (sequential verification)
```

## Parallel Execution Plan

```
Wave 1: T001 (directory structure)
Wave 2: T002, T003, T004, T005 (parallel — all different files)
Wave 3: T006 (SKILL.md — depends on wave 2 outputs)
Wave 4: T007 (semantic_atlas module — depends on T006)
Wave 5: T008 (CLI command — depends on T007)
Wave 6: T010, T011, T012 (parallel — routing, discovery, fixture — all different files)
Wave 7: T013, T014, T015 (parallel — tests, all different files)
Wave 8: T016 → T017 → T018 → T019 (sequential verification)
```

## Checkpoints

| After Phase | What to verify                                              |
|-------------|-------------------------------------------------------------|
| Phase 1     | All directories and reference files exist                    |
| Phase 2     | SKILL.md is 200+ lines with all section specs               |
| Phase 3     | `harness semantic-atlas --help` prints valid usage          |
| Phase 4     | `harness status` shows the new subskill                     |
| Phase 5     | `make test` passes all new tests                            |
| Phase 6     | `make verify` passes, eval and report filled                |

## Rules

- `[P]` means safe to run in parallel with other `[P]` tasks in the same wave.
- `[P]` tasks must not modify the same file.
- Every implementation task maps to a user story or requirement.
- Every task names exact file paths.
- If a checkpoint fails, stop and fix before moving forward.
