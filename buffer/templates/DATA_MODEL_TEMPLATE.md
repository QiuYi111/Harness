# Data Model: [Feature Name]

> Defines the entities, relationships, and persistence details for this feature. Write this before implementing the domain layer.

## Entities

| Entity | Description | DDD Layer |
|--------|-------------|-----------|
| User | Core identity: email, name, role, timestamps | domain |
| UserProfile | Extended profile: bio, avatar, preferences | domain |
| Session | Active authentication session with tokens | domain |

## Entity Definitions

### User

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | yes | Primary key, generated on creation |
| email | string (320) | yes | Unique, validated, lowercase |
| name | string (200) | yes | Display name |
| role | enum (admin, member, viewer) | yes | Authorization role |
| created_at | timestamp | yes | Set once on creation |
| updated_at | timestamp | yes | Updated on every write |

**Invariants**:
- Email must be unique across all users.
- Role can only be escalated by an admin.
- `created_at` is immutable after creation.

### UserProfile

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | yes | Primary key |
| user_id | UUID | yes | Foreign key to User, one-to-one |
| bio | text | no | Free-text biography |
| avatar_url | string (500) | no | URL to avatar image |
| preferences | jsonb | no | Key-value user preferences |
| updated_at | timestamp | yes | Updated on every write |

**Invariants**:
- `user_id` must reference an existing User.
- A User can have at most one UserProfile.

### Session

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | yes | Primary key |
| user_id | UUID | yes | Foreign key to User |
| refresh_token_hash | string (64) | yes | SHA-256 hash of refresh token |
| expires_at | timestamp | yes | Token expiry time |
| created_at | timestamp | yes | Session creation time |
| revoked_at | timestamp | no | Set when session is terminated |

**Invariants**:
- Expired sessions are not valid for refresh.
- Revoked sessions cannot be unrevoked.

## Relationships

```
User 1 ─── 1 UserProfile
User 1 ─── * Session
```

- **User → UserProfile**: One-to-one. Deleting a User cascades to their profile.
- **User → Session**: One-to-many. A user can have multiple active sessions across devices. Deleting a User cascades to all sessions.

## Schema / Migration Notes

- All tables use UUID primary keys (no auto-increment).
- Timestamps stored in UTC with microsecond precision.
- Soft deletes use a `deleted_at` nullable timestamp column where applicable.
- Migrations must be backward-compatible: additive changes only in shared branches.
- Each migration file is prefixed with a sequential number: `001_`, `002_`, etc.

## Indexes

| Table | Index | Type | Rationale |
|-------|-------|------|-----------|
| users | `idx_users_email` | UNIQUE, B-tree | Lookup by email during login, must be unique |
| users | `idx_users_role` | B-tree | Admin dashboard filters by role |
| sessions | `idx_sessions_user_id` | B-tree | Fetch all sessions for a user during logout-all |
| sessions | `idx_sessions_expires_at` | B-tree | Cleanup job deletes expired sessions |
| user_profiles | `idx_profiles_user_id` | UNIQUE, B-tree | One-to-one constraint enforcement |

## Constraints

- **users.email**: UNIQUE, NOT NULL, CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')
- **users.role**: CHECK (role IN ('admin', 'member', 'viewer'))
- **sessions.expires_at**: CHECK (expires_at > created_at)
- **user_profiles.user_id**: UNIQUE, NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE
- **sessions.user_id**: NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE
