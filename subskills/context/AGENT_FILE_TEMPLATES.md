# Agent File Templates

Snippets for agent-specific routing files. Paste these into the appropriate config file based on which agent is being used.

## CLAUDE.md Snippet (Claude Code)

```markdown
## Feature: <feature-name>

### Context
Read `specs/<feature>/context.md` before starting work on this feature.

### Rules
- Follow the Must Read list in context.md. Do not read Forbidden Context files.
- Blast radius: <leaf/branch/core/infra>. Gate strictness follows this level.
- Tests must be written during RED phase. Do not modify tests during GREEN.
- Run `make verify` after implementation. Fix all failures before reporting done.

### Key Files
- Spec: `specs/<feature>/spec.md`
- Plan: `specs/<feature>/plan.md`
- Tasks: `specs/<feature>/tasks.md`
```

## AGENTS.md Snippet (Cross-Agent Standard)

```markdown
## <feature-name>

### Before Starting
1. Read `specs/<feature>/context.md`
2. Read all files in the Must Read section
3. Check blast radius level — follow corresponding gates

### Process
1. RED: Write tests against spec acceptance criteria
2. GREEN: Implement minimum code to pass tests
3. REFACTOR: Clean up while keeping tests green
4. REVIEW: Run `make verify` and `make verify-ai`

### Do Not
- Read files listed in Forbidden Context
- Modify tests during GREEN phase
- Skip gates based on blast radius level
- Invent scope not in the spec
```

## Zoom-Out Context Snippet

For agents unfamiliar with the codebase. Add to context.md's Zoom-Out section:

```markdown
## Zoom-Out: <feature-name>

### Where This Lives
<describe the module/directory and its role in the system>

### What Depends On This
<list downstream consumers, APIs, or modules>

### What This Depends On
<list upstream dependencies, services, libraries>

### What Could Break
<list adjacent features or shared code that could be affected>

### System Map
<simple ASCII diagram or prose map showing relationships>
```

## Usage

1. Choose the template matching the target agent (CLAUDE.md for Claude Code, AGENTS.md for others).
2. Replace all `<placeholders>` with actual values from the feature's context.md.
3. Append the snippet to the existing config file — don't overwrite existing content.
4. For Zoom-Out, paste directly into context.md's Zoom-Out section.
