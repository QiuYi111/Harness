# Feature Spec: Code Semantic Atlas

## Metadata

| Field      | Value                                  |
|------------|----------------------------------------|
| Feature ID | `001-semantic-atlas`                   |
| Branch     | `feat/001-semantic-atlas`              |
| Status     | Draft                                  |
| Owner      | jingyi                                 |
| Date       | 2026-05-09                             |
| Risk       | branch                                 |

## Summary

Code Semantic Atlas is a new Harness subskill that converts source code files into semantic audit documentation — Mermaid diagrams, structured tables, and minimal natural language pseudocode — enabling humans to rapidly verify whether code behavior matches requirements. It serves as the first quality gate after AI-generated code: graph > table > text. MVP supports single-file analysis with Markdown output for Python, TypeScript/JavaScript, and C++.

## User Scenarios

### US-001: Single-File Semantic Audit

**Priority**: P1

**Independent Test**: Run `harness semantic-atlas <file>` on a known C++ PID controller header. Verify output contains all 13 required sections and that Mermaid diagrams are syntactically valid.

**Acceptance Scenarios**:
- Given a Python file with 1 class and 5+ functions, When `harness semantic-atlas file.py` is invoked, Then output Markdown contains: Dashboard, module framework diagram, core flow diagram, data flow diagram, state diagram (if applicable), function call diagram, state variable table, function contract table, side-effect matrix, risk matrix, coverage matrix, pseudocode for core functions, and final audit conclusion.
- Given a C++ header file, When `harness semantic-atlas pid_controller.h` is invoked, Then output is written to `docs/semantic_atlas/<rel_path>.semantic_atlas.md` with all functions appearing in the function contract table and all state variables in the state variable table.
- Given a TypeScript file, When analyzed, Then language is auto-detected as `typescript` and all symbols (classes, functions, methods, variables, imports) are extracted.

### US-002: AI Code Quality Gate

**Priority**: P1

**Independent Test**: Generate code via AI, run semantic atlas, verify a human can determine code-requirement alignment from the output in under 2 minutes.

**Acceptance Scenarios**:
- Given AI-generated code, When semantic atlas output is reviewed, Then a human can answer: what the file does, how input becomes output, which state is read/modified, which functions have side effects, where boundary conditions and risks exist — without reading the source code.

### US-003: Mermaid Diagram Verification

**Priority**: P2

**Independent Test**: Run with `--verify-mermaid` flag. Confirm all Mermaid blocks pass syntax validation or are degraded to table descriptions after 2 retry attempts.

**Acceptance Scenarios**:
- Given `--verify-mermaid` flag, When Mermaid syntax errors exist, Then the system auto-fixes and retries up to 2 times; if still failing, the diagram is replaced with a table description and an error note.

### US-004: Coverage Completeness Check

**Priority**: P1

**Independent Test**: Analyze a file with known functions and state variables. Verify the coverage matrix reports 100% coverage for all code elements.

**Acceptance Scenarios**:
- Given a file with 10 functions and 5 state variables, When semantic atlas is generated, Then the coverage matrix shows all 10 functions in the function table and all 5 state variables in the state table; any missing element is flagged as "uncovered".

### US-005: Strict Mode Audit

**Priority**: P2

**Independent Test**: Run with `--strict` flag on a file where function bodies are partially visible. Verify all uncertain content is explicitly labeled.

**Acceptance Scenarios**:
- Given `--strict` mode and a header file with only declarations (no bodies), When semantic atlas is generated, Then every claim is either "code explicitly implements" or labeled "speculation" / "cannot determine"; no unmarked assumptions exist.

### US-006: Diagram-Heavy Output Mode

**Priority**: P2

**Independent Test**: Run with `--diagram-heavy` flag. Verify output content ratio: diagrams + tables >= 80% of content, long-form text <= 20%.

**Acceptance Scenarios**:
- Given `--diagram-heavy` flag, When output is generated, Then Mermaid diagrams and structured tables dominate the output; no per-function essay explanations exist; only pseudocode and conclusion use paragraph text.

## Requirements

### Functional Requirements

- **FR-001**: Language Detection — System auto-detects language from file extension. MVP supports: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.c`, `.h`, `.cpp`, `.hpp`, `.cc`, `.rs`, `.go`. Priority: Python > TypeScript > C++.
- **FR-002**: Symbol Extraction — System extracts: classes, structs, functions, methods, constructors/destructors, member variables, global variables, constants, enums, imports/includes. Implementation priority: tree-sitter/AST > language server > regex fallback > LLM inference.
- **FR-003**: State Variable Identification — System identifies: object state (members), module state (module-level mutable), global state, static state, external state (files/network/hardware), temporary state (local in core flows).
- **FR-004**: Function Read/Write Analysis — System identifies per function: state reads, state writes, function calls, return values, error paths, I/O operations.
- **FR-005**: Mermaid Diagram Generation — System generates 5 required diagram types: module framework (flowchart LR), core execution flow (flowchart TD), data flow (flowchart LR), state machine (stateDiagram-v2 when applicable), function call graph (flowchart TD).
- **FR-006**: Structured Table Generation — System generates 8 required tables: Dashboard, state variable table, function contract table, side-effect matrix, risk matrix, coverage matrix, final conclusion table. Plus optional: requirements compliance matrix.
- **FR-007**: Natural Language Pseudocode — System generates numbered-step pseudocode for core functions only. Non-core functions included only if: complex branching, modifies critical state, high-risk side effects, or user-specified.
- **FR-008**: Mermaid Syntax Verification — When `--verify-mermaid` is enabled: validate all Mermaid blocks, auto-fix and retry up to 2 times, degrade to table on persistent failure.
- **FR-009**: Strict Mode — `--strict` mode enforces: all unconfirmed behavior labeled "cannot determine", all speculation explicitly marked, diagram content limited to code-confirmed facts, risk suggestions bound to code evidence, no generalizations.
- **FR-010**: Output Structure — Output Markdown follows fixed 14-section structure (sections 0–13 as defined in PRD section 11).
- **FR-011**: Output Path — Default: `docs/semantic_atlas/<relative_path>.semantic_atlas.md`. Customizable via `--output`.
- **FR-012**: CLI Integration — Command `harness semantic-atlas <file_or_glob> [options]` registered as subcommand in the Harness CLI.
- **FR-013**: Faithfulness — System strictly separates: "code explicitly implements", "inferred from naming/comments" (labeled "speculation"), "cannot determine from current fragment". Never: treat best practices as implemented code, treat comment intent as runtime fact, fabricate flows for diagram completeness.
- **FR-014**: Coverage Tracking — Coverage matrix must check: all functions in function table, all state variables in state table, all state-modifying functions in side-effect matrix, core functions have flow diagrams, core data in data flow diagrams.

### Non-Functional Requirements

- **NFR-001**: Readability — Output is scannable. Diagrams + tables >= 80% of content (with `--diagram-heavy`). No per-function essay explanations. Stable section structure.
- **NFR-002**: Faithfulness — No fabrication. Uncertainty is labeled. Comment intent ≠ code behavior. Simple functions (getters/setters) are not skipped. Evidence-bound conclusions.
- **NFR-003**: Maintainability — Implementation is modular: `subskills/semantic-atlas/` with `SKILL.md`, `templates/`, `examples/` subdirectories.
- **NFR-004**: Extensibility — Architecture supports future additions: `--spec` flag, `--changed-only`, JSON output, multi-file analysis, CI gate — without rearchitecting.
- **NFR-005**: Performance — Single-file analysis completes in one LLM invocation pass (no multi-turn loops for MVP). Symbol extraction via AST/regex is non-LLM.
- **NFR-006**: Testability — Each output section has a verification check. Acceptance tests use fixture files with known expected outputs.

## Success Criteria

| #   | Criterion                                                                 | Measured By                                          |
|-----|---------------------------------------------------------------------------|------------------------------------------------------|
| SC-1 | Single-file analysis produces all 14 sections for Python/TS/C++ files    | Fixture-based acceptance test: `make test-atlas`     |
| SC-2 | All functions appear in function contract table (coverage = 100%)         | Coverage matrix self-check in output                 |
| SC-3 | All state variables appear in state variable table (coverage = 100%)     | Coverage matrix self-check in output                 |
| SC-4 | Mermaid diagrams are syntactically valid                                  | `--verify-mermaid` flag + Mermaid CLI validation     |
| SC-5 | CLI `harness semantic-atlas` works as subcommand                          | Integration test                                     |
| SC-6 | Diagram + table content >= 80% with `--diagram-heavy`                    | Content ratio check on fixture output                |
| SC-7 | No fabrication: all uncertainty labeled in `--strict` mode               | Manual review + regex check for unmarked assumptions |

## Assumptions

- The subskill is primarily LLM-driven for semantic analysis; AST/regex pre-processing supplements symbol extraction but is not the core engine.
- MVP targets single-file analysis only; cross-file tracing is V2+.
- The Harness project itself serves as the host; the subskill integrates into the existing `subskills/` structure.
- Mermaid CLI (`mmdc`) may not be installed on all systems; `--verify-mermaid` is opt-in.
- Python is the primary implementation language (matching existing Harness runtime).
- The skill operates read-only on source files — no code modification.

## Clarifications

- None — PRD is comprehensive and MVP scope is well-defined.

## Out of Scope (V1 MVP)

- `--spec` flag and requirements compliance matrix
- `--changed-only` / PR summary / diff analysis
- JSON output format
- Mermaid CLI auto-fix (verification only, degradation path)
- Multi-file / cross-module analysis
- IDE plugin (VS Code)
- Test coverage mapping
- CI gate / merge blocking
- `--max-depth` cross-file tracing
- `--include-tests` test file analysis
- `--risk-level` granularity control
- `--summary` project overview mode

## Risk Notes

| Risk                                              | Likelihood | Impact | Mitigation                                                    |
|---------------------------------------------------|-----------|--------|---------------------------------------------------------------|
| LLM hallucination in semantic analysis            | Medium    | High   | Strict faithfulness rules, coverage matrix, `--strict` mode   |
| Mermaid syntax errors in generated diagrams        | Medium    | Medium | `--verify-mermaid` flag, auto-retry, table degradation        |
| Incomplete symbol extraction for some languages    | Medium    | Medium | Fallback chain: AST > LSP > regex > LLM; explicit "cannot determine" labels |
| Output too verbose for human quick-scan            | Low       | Medium | `--diagram-heavy` mode, graph > table > text priority, no essays |
| Adding subcommand to existing CLI breaks it        | Low       | High   | Test existing commands after integration                      |

## Rules

- Every spec must have at least one user scenario.
- Every P1 scenario must have independent test instructions.
- Every feature must define success criteria.
- Agent must not guess values marked [NEEDS CLARIFICATION].
