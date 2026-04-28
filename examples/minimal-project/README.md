# Example: Todo API

This is a worked example showing how the Harness v2 spec-governed templates look when filled in for a real feature. It is not a runnable project. It contains only the lifecycle documents (spec, plan, tasks, eval, report) that demonstrate the Harness methodology in practice.

## What's inside

The example walks through one feature: **Add Todo Item** (FEAT-001), a POST /todos endpoint for creating todo items with a title and optional description.

```
specs/001-add-todo/
  spec.md   -- Feature specification with user scenarios and acceptance criteria
  plan.md   -- Technical implementation plan with architecture impact and blast radius
  tasks.md  -- Task DAG with dependencies, parallel execution plan, and checkpoints
  eval.md   -- Product and harness evaluation results
  report.md -- Implementation evidence, files changed, and rollback plan
```

## Template copies

Three files in this directory are exact copies from the Harness templates:

- `AGENTS.md` -- copied from `templates/AGENTS.md`, with only the Project Overview section filled in
- `CLAUDE.md` -- copied from `templates/CLAUDE.md`, no modifications
- `Makefile` -- copied from `templates/Makefile`, no modifications

These files are runtime configs that users copy into their projects as-is. The only customization is the project name in AGENTS.md.

## How to use this example

1. Read `specs/001-add-todo/spec.md` to see how requirements are structured.
2. Read `specs/001-add-todo/plan.md` to see how technical decisions are documented.
3. Read `specs/001-add-todo/tasks.md` to see how work is broken down for agents.
4. Read `specs/001-add-todo/eval.md` and `report.md` to see how evidence is collected.
5. Copy `templates/AGENTS.md`, `templates/CLAUDE.md`, and `templates/Makefile` into your own project to get started.
