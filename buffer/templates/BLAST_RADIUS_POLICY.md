---
risk_levels:
  leaf:
    description: "Isolated, low-dependency changes"
    autonomy: high
    examples:
      - documentation
      - isolated UI component
      - one-off script
      - test file
      - adapter with existing contract
    required_gates:
      - lint
      - unit_test
  branch:
    description: "Feature-level or multi-file behavior change"
    autonomy: medium
    examples:
      - feature module
      - service layer
      - new endpoint
      - multi-file behavior change
    required_gates:
      - spec
      - plan
      - tests
      - review_agent
  core:
    description: "Domain, auth, storage, permissions, protocol"
    autonomy: low
    examples:
      - domain model
      - auth logic
      - permission system
      - storage schema
      - plugin protocol
      - scheduler
    required_gates:
      - human_spec_review
      - architecture_review
      - rollback_plan
      - security_review
  infra:
    description: "Deployment, CI/CD, secrets, migrations"
    autonomy: very_low
    examples:
      - CI/CD pipeline
      - deployment config
      - database migration
      - secrets management
    required_gates:
      - dry_run
      - explicit_human_approval
      - rollback_plan
      - security_review
---

# Blast Radius Policy

This policy governs how much autonomy an agent has based on the risk classification of a proposed change. Higher blast radius means stricter gates and less freedom to act independently.

## Risk Levels

### Leaf (High Autonomy)

Isolated, low-dependency changes. The agent can proceed with minimal oversight.

- **Autonomy**: High. Agent may act independently after standard checks pass.
- **Required gates**: lint, unit_test
- **Typical changes**: documentation, isolated UI components, one-off scripts, test files, adapters conforming to an existing contract.

### Branch (Medium Autonomy)

Feature-level or multi-file behavior changes. The agent must plan before executing and produce test coverage.

- **Autonomy**: Medium. Agent must produce a spec and plan before implementation. An automated review agent validates the result.
- **Required gates**: spec, plan, tests, review_agent
- **Typical changes**: feature modules, service layer changes, new endpoints, multi-file behavior changes.

### Core (Low Autonomy)

Changes that touch domain logic, authentication, storage, permissions, or internal protocols. These have wide-reaching impact and require human review.

- **Autonomy**: Low. Agent must get human spec review and architecture review before starting. A rollback plan is mandatory.
- **Required gates**: human_spec_review, architecture_review, rollback_plan, security_review
- **Typical changes**: domain model changes, auth logic, permission system, storage schema, plugin protocol, scheduler.

### Infra (Very Low Autonomy)

Changes to deployment, CI/CD, secrets, or database migrations. These affect the entire system and can cause outages.

- **Autonomy**: Very low. Every step requires explicit human approval. Dry-run is mandatory before any execution.
- **Required gates**: dry_run, explicit_human_approval, rollback_plan, security_review
- **Typical changes**: CI/CD pipeline, deployment config, database migration, secrets management.

## Classification Decision Tree

Answer these questions in order. Stop at the first match.

1. **Does the change touch deployment, CI/CD, secrets, or database migrations?**
   - Yes: classify as **infra**.
2. **Does the change touch domain models, auth logic, permissions, storage schema, plugin protocol, or the scheduler?**
   - Yes: classify as **core**.
3. **Does the change alter behavior across multiple files, touch the service layer, add an endpoint, or implement a feature module?**
   - Yes: classify as **branch**.
4. **Is the change limited to docs, tests, a one-off script, an isolated component, or an adapter working against an existing contract?**
   - Yes: classify as **leaf**.
5. **Still uncertain?**
   - Choose the **higher** risk level. It is always safer to over-classify than to under-classify.

## Classification Examples

| Change | Level | Reason |
|--------|-------|--------|
| Fix README typo | leaf | docs only, zero runtime impact |
| Add isolated CLI helper | leaf | low dependency, self-contained |
| Add contract test | leaf | test-only, no production code |
| Add new REST endpoint | branch | externally visible behavior change |
| Add service method across 3 files | branch | feature-level behavior change |
| Change domain entity field | core | affects data model and all consumers |
| Change auth middleware | core | permission and security impact |
| Add database migration | core/infra | schema change plus deployment risk |
| Modify GitHub Actions deploy job | infra | deployment pipeline risk |
| Add .env handling | infra | secrets and config risk |

## Multi-File Rule

When a change touches multiple files, classify it at the **highest** risk level represented by any file in the change set. A pull request that modifies a README (leaf) and an auth middleware (core) is classified as **core**.

## Usage in AGENTS.md / CLAUDE.md

Agent instruction files should reference this policy to set autonomy boundaries. Example phrasing:

```
Before starting any work, classify the blast radius of the proposed change using the decision tree in templates/BLAST_RADIUS_POLICY.md. Apply the required gates for that risk level. Do not skip gates. Do not self-promote to a higher autonomy level.
```

The YAML frontmatter at the top of this file is machine-parseable. A future `classify-risk.sh` script can read it directly to enforce gates in CI/CD pipelines.
