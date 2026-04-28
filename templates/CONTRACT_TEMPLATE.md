# Contract: [Service/Feature Name]

> Defines the interface between this service/feature and its consumers. Treat this as the source of truth for integration.

## Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Draft / Proposed / Active / Deprecated |
| Owner | [Team or individual responsible] |
| Last Updated | [Date] |
| Review Status | Pending review / Approved / Needs revision |

## Interface Definition

```
[Insert API definition here]

Examples:
- OpenAPI: yaml definition
- Protobuf: .proto file reference
- Event: JSON schema
```

### Example: OpenAPI snippet

```yaml
openapi: 3.0.3
info:
  title: User Service API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
```

### Example: Event schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "event_type": { "type": "string", "const": "user.created" },
    "user_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": { "$ref": "#/definitions/UserPayload" }
  },
  "required": ["event_type", "user_id", "timestamp", "payload"]
}
```

## Endpoints / Operations

| Name | Method | Path | Description |
|------|--------|------|-------------|
| GetUser | GET | /users/{id} | Retrieve a user by their unique ID |
| CreateUser | POST | /users | Create a new user account |
| UpdateUser | PATCH | /users/{id} | Partially update user fields |
| DeleteUser | DELETE | /users/{id} | Soft-delete a user account |
| ListUsers | GET | /users | Paginated list of users with filtering |

## Data Types

| Type | Description | Used In |
|------|-------------|---------|
| `User` | Core user representation with identity fields | GetUser, CreateUser, UpdateUser |
| `UserPayload` | Event payload for user lifecycle events | user.created, user.updated |
| `PaginationMeta` | Page info (total, page, per_page) | ListUsers |
| `ErrorResponse` | Standard error envelope with code and message | All error responses |

## Versioning

- **Breaking changes** (field removals, type changes, endpoint removals) require a major version bump and a deprecation window of at least 2 release cycles.
- **Additive changes** (new fields, new endpoints) are backward-compatible and ship as minor versions.
- **Deprecated fields** return a `Sunset` header with the removal date.
- **Version in URL path**: `/v1/users`, `/v2/users`. Old versions receive security patches only for 6 months after deprecation.

## Consumers

| Consumer | How It Uses This Contract | Contact |
|----------|--------------------------|---------|
| Frontend web app | Calls REST endpoints for user CRUD | [Team/person] |
| Notification service | Subscribes to `user.created` and `user.updated` events | [Team/person] |
| Analytics pipeline | Consumes `user.*` events for reporting | [Team/person] |
| Mobile app | Calls REST endpoints via API gateway | [Team/person] |
