# Roadmap

## Stage 0: Product definition

### Goal

Define what to build, for whom, and why. Establish product contract.

### Exit criteria

- [ ] product.md complete
- [ ] evidence.md passed or waived
- [ ] ux-principles.md complete
- [ ] user-journeys.md complete
- [ ] ui-direction.md complete if required
- [ ] value-proposition.md complete
- [ ] roadmap.md complete
- [ ] state.yaml initialized with readiness flags

---

## Stage 1: Feasibility validation

### Goal

Prove the technical and product path is viable before committing to full build.

### Exit criteria

- [ ] Technical spike completed (if needed)
- [ ] spike-report.md produced with recommendation: continue
- [ ] feasibility_ready: true in state.yaml

---

## Stage 2: MVP scaffold

### Goal

Create the minimal running skeleton: project structure, core models, basic routing, empty states.

### Exit criteria

- [ ] Project builds and runs
- [ ] Core models exist
- [ ] Basic navigation works
- [ ] Empty/loading states render
- [ ] CI pipeline green

---

## Stage 3: Core loop implementation

### Goal

Implement the primary user journey end-to-end with working logic and real data flow.

### Exit criteria

- [ ] Primary journey works end-to-end
- [ ] Tests cover happy path and main failure modes
- [ ] harness-eval passes
- [ ] No critical UX gaps

---

## Stage 4: UX polish

### Goal

Refine interaction, motion, error states, responsive behavior, and visual consistency.

### Exit criteria

- [ ] Error states handled for all failure points in user-journeys.md
- [ ] Loading states implemented
- [ ] Responsive layouts verified
- [ ] UI matches approved ui-direction.md
- [ ] No AI slop patterns detected

---

## Stage 5: Dogfood

### Goal

Use the product yourself. Find and fix friction before anyone else sees it.

### Exit criteria

- [ ] At least 3 complete dogfood sessions completed
- [ ] All found issues logged and resolved or deferred
- [ ] Performance acceptable on target devices
- [ ] Ready for external user testing
