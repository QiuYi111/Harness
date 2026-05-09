# Implementation Plan: Code Semantic Atlas

## Inputs

| Source            | Reference                                          |
|-------------------|----------------------------------------------------|
| Spec              | `specs/001-semantic-atlas/spec.md`                  |
| PRD               | `human.md`                                          |
| Related Contracts | None                                                 |

## Technical Context

| Dimension             | Value                                      |
|-----------------------|--------------------------------------------|
| Language              | Python + Markdown (skill prompts)          |
| Framework             | Click CLI, Harness skill-pack architecture |
| Storage               | Filesystem (Markdown output)               |
| External Dependencies | tree-sitter (optional, for AST extraction) |

## Architecture Impact

### DDD Layer Impact

| Layer            | Change                                          |
|------------------|-------------------------------------------------|
| `subskills/`     | New `semantic-atlas/` subskill directory         |
| `scripts/`       | Add `semantic_atlas.py` module to `harness_runtime/` |
| `references/`    | Add routing entries to ROUTING_TABLE.md, PHASE_DETECTION.md |
| `SKILL.md` (root)| No change — router auto-discovers new subskill  |

### Contract Impact

- New CLI subcommand: `harness semantic-atlas <file> [options]`
- New skill registered: `harness-semantic-atlas`

### Data Model Impact

- None — read-only analysis producing Markdown files.

## Blast Radius Classification

| Field           | Value                                                                                  |
|-----------------|----------------------------------------------------------------------------------------|
| Level           | `branch`                                                                               |
| Reason          | Adds new subskill directory, modifies CLI, and touches routing configuration. No core domain changes. |
| Required Gates  | spec + plan + tests + review                                                            |

## Constitution Check

| Check          | Pass | Notes                                          |
|----------------|------|------------------------------------------------|
| Contract-first | Yes  | CLI subcommand follows existing click pattern   |
| DDD direction  | Yes  | New subskill is isolated, no domain coupling    |
| TDD/BDD        | Yes  | Fixture-based acceptance tests for each section  |
| Observability  | N/A  | No runtime service, file-based output           |
| Security       | Yes  | Read-only analysis, no code modification        |

## Implementation Strategy

The subskill is primarily a **structured LLM prompt** — the core "implementation" is the SKILL.md prompt that instructs an LLM to analyze code and produce the atlas. CLI support provides the user-facing interface and file I/O scaffolding.

Build order:

1. **Foundation**: Create subskill directory structure + output template
2. **Core Prompt**: Write SKILL.md with the full semantic atlas generation instructions
3. **CLI Integration**: Add `harness semantic-atlas` subcommand to the click CLI
4. **Routing**: Register the subskill in ROUTING_TABLE.md and PHASE_DETECTION.md
5. **Example Fixture**: Create a test fixture (PID controller) with expected output
6. **Verification**: Tests for CLI invocation, output structure, and Mermaid validity

### Step 1: Directory Structure

```
subskills/semantic-atlas/
  SKILL.md                     # Main subskill prompt
  references/
    OUTPUT_STRUCTURE.md         # Full output structure spec (extracted from PRD §11-12)
    FAITHFULNESS_RULES.md       # Faithfulness/audit rules (extracted from PRD §6)
    RISK_CATALOG.md             # Common risk checklist (extracted from PRD §12.10)
  templates/
    semantic_atlas.md           # Output template with all 14 sections
  examples/
    pid_controller.h            # Test fixture: C++ PID controller header
    pid_controller.semantic_atlas.md  # Expected output for fixture
```

### Step 2: SKILL.md Core Prompt

The SKILL.md is the heart of the subskill. It must contain:
- Role definition ("You are a Code Semantic Atlas generator")
- Output priority: graph > table > text
- All 14 section specifications from PRD §12
- Faithfulness rules from PRD §6.2
- Coverage requirements from PRD §6.4
- Mermaid syntax rules
- Chinese output requirement
- Audit-style writing guidelines

This is a ~200-300 line SKILL.md that encodes the full PRD behavior spec as LLM instructions.

### Step 3: CLI Integration

Add to `scripts/harness_runtime/cli.py`:

```python
@main.command("semantic-atlas")
@click.argument("files", nargs=-1, required=True)
@click.option("--spec", default=None, help="Requirements spec for compliance matrix")
@click.option("--output", default=None, help="Custom output directory")
@click.option("--format", "fmt", type=click.Choice(["md", "json"]), default="md")
@click.option("--changed-only", is_flag=True, help="Analyze only git-changed files")
@click.option("--summary", is_flag=True, help="Generate multi-file overview")
@click.option("--language", default=None, help="Override language detection")
@click.option("--strict", is_flag=True, help="Strict faithfulness mode")
@click.option("--verify-mermaid", is_flag=True, help="Validate Mermaid syntax")
@click.option("--diagram-heavy", is_flag=True, help="Maximize diagram/table ratio")
@click.option("--no-long-text", is_flag=True, help="No paragraph explanations")
def semantic_atlas(files, spec, output, fmt, changed_only, summary, language, strict, verify_mermaid, diagram_heavy, no_long_text):
```

The CLI command:
1. Resolves file paths and detects languages
2. Reads the SKILL.md prompt and output template
3. Reads the input source file(s)
4. Constructs a full prompt with the source code + template
5. Outputs instructions for the agent to generate the atlas
6. Writes output to `docs/semantic_atlas/`

For MVP, the CLI is a thin wrapper that:
- Validates inputs (file exists, language supported)
- Reads the skill prompt
- Prints the assembled prompt for the agent to execute
- Creates the output directory

### Step 4: Routing Updates

**ROUTING_TABLE.md** — Add new row:
```
| "semantic atlas" / "audit this code" / "semantic map" | harness-semantic-atlas | (generates atlas, human reviews) |
```

**PHASE_DETECTION.md** — No change needed (subskill is invoked directly via CLI, not auto-detected).

### Step 5: Test Fixture

Use a minimal C++ PID controller header as the canonical test fixture. Expected output validates:
- All 14 sections present
- All functions in function contract table
- All state variables in state variable table
- Mermaid diagrams syntactically valid
- Coverage matrix shows 100% for all elements

## Test Strategy

### Unit Tests

- `tests/test_semantic_atlas_cli.py`: CLI invocation, argument parsing, output path resolution
- `tests/test_semantic_atlas_structure.py`: Output template validation (all 14 sections defined)
- `tests/test_language_detection.py`: File extension to language mapping

### Integration Tests

- `tests/test_semantic_atlas_fixture.py`: Run `harness semantic-atlas` on `pid_controller.h` fixture, verify output structure
- `tests/test_mermaid_validity.py`: Parse output Mermaid blocks, verify syntax basics

### Edge Cases

- Header-only files with no function bodies → all "cannot determine"
- Empty files → graceful handling
- Unsupported language extensions → clear error message
- Files with no state variables → state diagram section notes "no explicit state machine"

## Rollback Plan

1. `git revert` the feature branch
2. Remove `subskills/semantic-atlas/` directory
3. Revert CLI changes in `scripts/harness_runtime/cli.py`
4. Revert routing entries in `references/ROUTING_TABLE.md`
5. No data migration needed — output is file-based and additive

## Complexity Tracking

| Field      | Value                                           |
|------------|-------------------------------------------------|
| Estimated  | Medium                                          |
| Rationale  | Primarily a prompt/skill implementation. CLI integration is mechanical. Template and prompt are the intellectual core. No complex algorithms, no state management, no external dependencies beyond optional tree-sitter. |
