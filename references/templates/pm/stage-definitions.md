# Stage Definitions

## product_definition

### Goal

Define what to build, for whom, and why it matters.

### Inputs required

- User's raw product idea or existing notes
- Any existing README or product documentation

### Allowed work

- Product discovery interviews (grill-product)
- UX research and journey mapping
- UI direction exploration
- Evidence collection and validation
- MVP boundary definition

### Forbidden work

- Code implementation
- Architecture decisions beyond guardrails
- Dependency installation

### Exit criteria

- All .pm/stable/ files complete
- state.yaml readiness flags set to true where applicable

### Required verification

- evidence.md status is passed or waived_by_user
- ui-direction.md approved if UI-facing product

---

## feasibility

### Goal

Validate that the chosen approach is technically viable.

### Inputs required

- product.md
- architecture-guardrails.md

### Allowed work

- Technical spikes
- Prototyping
- Proof-of-concept experiments
- Dependency evaluation

### Forbidden work

- Production implementation
- Schema changes
- Deployment changes

### Exit criteria

- spike-report.md produced with clear recommendation
- feasibility_ready: true in state.yaml

### Required verification

- Spike demonstrates core technical question resolved
- No blocking unknowns remain

---

## delivery

### Goal

Implement bounded tasks that advance the current roadmap stage.

### Inputs required

- next-task.md with clear scope and acceptance criteria
- All relevant .pm/stable/ files

### Allowed work

- Feature implementation within task scope
- Test writing
- Debugging within task scope
- Documentation updates

### Forbidden work

- Changing product positioning
- Expanding MVP boundary
- Changing core tech stack
- Core/infra/security/payment/auth changes without approval

### Exit criteria

- Task acceptance criteria met
- worker-report.md produced
- Tests pass

### Required verification

- harness-eval for the task
- Evidence in worker-report.md
