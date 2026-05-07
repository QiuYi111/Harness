# Architecture Guardrails

## Tech stack

[Language, framework, database, deployment target. Specific versions if it matters.]

## Architectural principles

[3-7 principles that constrain all technical decisions.]

## Allowed changes without user approval

- Leaf-risk code changes within existing patterns
- Test additions
- Documentation updates
- Dependency patch updates
- Bug fixes within existing scope

## Changes requiring user approval

- Core tech stack changes (language, framework, database)
- New dependencies above patch level
- Schema changes
- API contract changes
- Authentication/authorization changes
- Deployment target changes
- Performance-critical architectural decisions

## Forbidden changes

- [Explicitly listed patterns or technologies that must never be introduced.]

## Risk areas

[Parts of the system that are fragile, complex, or have high blast radius.]
