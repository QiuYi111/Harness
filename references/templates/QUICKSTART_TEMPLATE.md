# Quickstart: [Project Name]

> Get up and running with Harness v2 in under 10 minutes.

## Prerequisites

- **Make** (4.0+)
- **Git** (2.30+)
- A code editor or IDE
- (Optional) Docker, if your project uses containerized dependencies

## Manual Path

Follow these steps if you want to understand what each piece does before automating.

### 1. Copy templates to project root

Copy the core Harness templates into your project:

```
templates/
  PRD_TEMPLATE.md
  SPEC_TEMPLATE.md
  PLAN_TEMPLATE.md
  TASKS_TEMPLATE.md
  EVAL_TEMPLATE.md
  REPORT_TEMPLATE.md
```

Create the specs directory structure:

```
specs/
  CLAUDE.md          <-- agent instructions for this feature
  spec.md            <-- what we're building
  plan.md            <-- how we're building it
  tasks.md           <-- checklist of work items
  reports/           <-- implementation report and evals
```

### 2. Set up directory structure

Organize your code following the layered architecture:

```
internal/
  domain/       <-- entities, value objects, repository interfaces
  app/          <-- use cases / application services
  infra/        <-- repository implementations, external services
  interface/    <-- HTTP handlers, CLI, message consumers
```

### 3. Configure agent instructions

Add a `CLAUDE.md` at the project root with your project's rules, coding conventions, and any language or framework-specific guidance the AI agent should follow.

### 4. Create your first feature spec

Copy `SPEC_TEMPLATE.md` into `specs/001-first-feature/spec.md` and fill in the feature description, acceptance criteria, and non-functional requirements.

### 5. Implement and verify

Write code following your plan. Run verification before requesting review.

## Automated Path

If your project includes a Harness Makefile, the setup is two commands:

```bash
# Initialize Harness in the project
make init

# Scaffold a new feature
make spec-init FEATURE=001-first-feature
```

Then fill in the generated files:

```bash
# Edit these files with your feature details
specs/001-first-feature/spec.md
specs/001-first-feature/plan.md
```

Generate tasks from the plan:

```bash
make tasks FEATURE=001-first-feature
```

After implementation, verify everything:

```bash
make verify
make verify-ai
```

## First Feature Walkthrough

Here's a concrete example: adding a "user profile" feature.

**Spec** (`specs/001-user-profile/spec.md`):
- Describe the profile entity (name, bio, avatar URL).
- List acceptance criteria (create, read, update, delete).
- Note non-functional requirements (response time under 200ms, PII encryption at rest).

**Plan** (`specs/001-user-profile/plan.md`):
- Define the `UserProfile` entity in the domain layer.
- Create a `UserProfileRepository` interface.
- Implement the PostgreSQL repository in the infra layer.
- Write a `GetProfile` use case in the app layer.
- Add a `GET /users/:id/profile` endpoint in the interface layer.

**Tasks** (`specs/001-user-profile/tasks.md`):
- [ ] Create domain entity and repository interface
- [ ] Write failing tests for the repository
- [ ] Implement repository with PostgreSQL
- [ ] Write failing tests for the use case
- [ ] Implement use case service
- [ ] Write failing tests for the HTTP handler
- [ ] Implement handler and wire routing
- [ ] Run `make verify` and `make verify-ai`

**Eval** (`specs/001-user-profile/reports/eval.md`):
- Fill out the eval template after all tasks are complete.

## Verification

Confirm Harness is set up correctly:

1. **Directory structure exists**: `ls specs/` should show your feature directories.
2. **Templates are in place**: `ls templates/` should list all template files.
3. **Make targets work**: `make verify` should run without errors (even on an empty project, it should exit cleanly or tell you what's missing, not crash).
4. **Agent can read instructions**: Open your AI coding tool and confirm it picks up `CLAUDE.md` at the project root.
