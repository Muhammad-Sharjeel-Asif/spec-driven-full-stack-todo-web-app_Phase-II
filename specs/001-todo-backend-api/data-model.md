# Data Model: Todo Backend API

## Entity Definitions

### User
**Description**: Represents an authenticated user in the system
**Fields**:
- `id`: Integer (Primary Key, Auto-increment)
- `email`: String (Unique, Max length: 255, Required)
- `hashed_password`: String (Max length: 255, Required)
- `created_at`: DateTime (Default: now(), Required)
- `updated_at`: DateTime (Default: now(), Required)
- `is_active`: Boolean (Default: True, Required)

**Relationships**:
- One-to-Many: User → Task (via user_id foreign key)

### Task
**Description**: Represents a todo item owned by a user
**Fields**:
- `id`: Integer (Primary Key, Auto-increment)
- `title`: String (Max length: 255, Required)
- `description`: Text (Optional)
- `is_completed`: Boolean (Default: False, Required)
- `created_at`: DateTime (Default: now(), Required)
- `updated_at`: DateTime (Default: now(), Required)
- `user_id`: Integer (Foreign Key → User.id, Required)
- `version`: Integer (Default: 1, Required) - for optimistic locking

**Indexes**:
- Index on `user_id` for efficient user-based queries
- Index on `is_completed` for filtering by completion status
- Composite index on `(user_id, is_completed)` for common combined queries

**Validation Rules**:
- Title must be 1-255 characters
- User_id must reference an existing user
- Cannot modify another user's task

## State Transitions

### Task State Transitions
- **Creation**: New task starts with `is_completed = False`
- **Toggle Complete**: `is_completed` flips between True/False
- **Update**: Updates increment the `version` field for optimistic locking
- **Deletion**: Task is removed from database (soft delete could be implemented later if needed)

## Relationships

### User ↔ Task
- One user can own many tasks
- Tasks are deleted when user is deleted (CASCADE delete)
- All queries must filter by user_id to ensure isolation

## API Contract Implications

### Request/Response Objects

**TaskCreateRequest**:
```json
{
  "title": "string (1-255 chars)",
  "description": "string (optional)",
}
```

**TaskUpdateRequest**:
```json
{
  "title": "string (1-255 chars, optional)",
  "description": "string (optional)",
  "is_completed": "boolean (optional)",
  "version": "integer (required for optimistic locking)"
}
```

**TaskResponse**:
```json
{
  "id": "integer",
  "title": "string",
  "description": "string (nullable)",
  "is_completed": "boolean",
  "created_at": "datetime ISO string",
  "updated_at": "datetime ISO string",
  "user_id": "integer",
  "version": "integer"
}
```

**ErrorResponse** (RFC 7807 compliant):
```json
{
  "type": "string (URI to error type)",
  "title": "string (error title)",
  "status": "integer (HTTP status code)",
  "detail": "string (detailed error message)",
  "instance": "string (URI to specific occurrence)"
}
```