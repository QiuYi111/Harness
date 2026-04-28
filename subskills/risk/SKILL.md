---
name: harness-risk
description: Classify a proposed change by blast radius (leaf/branch/core/infra) and determine required gates. Use when planning a change that touches multiple files, core logic, infrastructure, auth, schema, or deployment config. Triggers on "risk level", "blast radius", "classify change", "what gates do I need", or "is this safe to auto-merge".
---

# Harness Risk

Classify a proposed change by blast radius and determine required gates.

## Prerequisites

Read before starting:
- `../../references/DOMAIN-AWARENESS.md` for risk-aware terminology
- [BLAST_RADIUS_GUIDE.md](BLAST_RADIUS_GUIDE.md) for the full classification guide

## Risk Levels

| Level | Autonomy | Scope | Gates |
|-------|----------|-------|-------|
| **leaf** | High | Isolated, single-file, no downstream dependents | lint + unit_test |
| **branch** | Medium | Feature-level, multi-file, bounded behavioral change | spec + plan + tests + review |
| **core** | Low | Domain model, auth, storage, permissions, protocols | human_spec_review + architecture_review + rollback + security |
| **infra** | Very Low | Deployment, CI/CD, secrets, migrations, config | dry_run + human_approval + rollback + security |

## Classification Process

### Option A: Deterministic Classifier (Preferred)

```bash
harness classify-risk --base=main          # diff against main
harness classify-risk --base=HEAD~3       # diff against 3 commits ago
```

Returns: risk level, affected files, required gates, HITL required (boolean).

### Option B: Manual Decision Tree

If `harness classify-risk` is unavailable, walk this tree:

1. **Does the change touch deployment, CI/CD, secrets, or database migrations?**
   → Yes: **infra**
   → No: continue

2. **Does the change touch auth, permissions, domain model, or cross-cutting protocols?**
   → Yes: **core**
   → No: continue

3. **Does the change span more than one file or affect a user-facing behavior?**
   → Yes: **branch**
   → No: continue

4. **Is the change isolated to a single file with no downstream dependents?**
   → Yes: **leaf**
   → No: **branch** (default safe escalation)

**When in doubt, escalate.** Classifying a branch change as leaf is an error. Classifying a leaf change as branch is cautious and acceptable.

## Output Format

```markdown
## Risk Classification

**Level:** [leaf|branch|core|infra]
**HITL Required:** [true|false]
**Affected Files:**
- `path/to/file1.go` (create)
- `path/to/file2.go` (modify)

**Required Gates:**
- [ ] gate 1
- [ ] gate 2

**Rationale:** [one sentence explaining why this level was chosen]
```

## HITL Determination

| Risk Level | HITL Required? | Exception |
|-----------|---------------|-----------|
| leaf | No | — |
| branch | No | If spec says "human review required" |
| core | Yes | — |
| infra | Yes | — |

## Usage in Other Skills

- `harness-tasks` uses risk level to set HITL/AFK classification
- `harness-tdd` uses risk level to determine if REVIEWER report requires human sign-off
- `harness-plan` uses risk level to determine plan depth requirements

## Terminology

Use the four terms exactly: **leaf**, **branch**, **core**, **infra**. Do not substitute synonyms like "minor", "medium", "critical", or "infrastructure". See `DOMAIN-AWARENESS.md` for the full glossary.
