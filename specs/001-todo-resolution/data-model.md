# Data Model for Todo Resolution Feature

## Entity: User
- **Fields**:
  - id (UUID/string): Unique identifier for the user
  - email (string): User's email address for authentication
  - password_hash (string): Hashed password for authentication
  - jwt_token (string): Current JWT token for session management
  - notification_preferences (JSON/object): User's notification settings
  - created_at (datetime): Timestamp when user account was created
  - updated_at (datetime): Timestamp when user account was last updated

- **Validation rules**:
  - Email must be valid email format
  - Password must meet security requirements (length, complexity)
  - ID must be unique across all users

- **Relationships**:
  - One-to-many with Task entity (one user can have many tasks)

## Entity: Task
- **Fields**:
  - id (UUID/string): Unique identifier for the task
  - title (string): Title of the task
  - description (string): Detailed description of the task
  - completed (boolean): Whether the task is completed
  - priority_level (enum: 'high', 'medium', 'low'): Priority level of the task
  - due_date (datetime): Date when the task is due
  - user_id (UUID/string): Foreign key linking to the owning user
  - notification_settings (JSON/object): Notification settings for this task
  - created_at (datetime): Timestamp when task was created
  - updated_at (datetime): Timestamp when task was last updated
  - deleted_at (datetime, nullable): Timestamp when task was soft-deleted (for 30-day retention)

- **Validation rules**:
  - Title is required
  - User_id must correspond to an existing user
  - Priority_level must be one of the allowed values
  - Due date must be in the future if provided

- **State transitions**:
  - Active → Completed (when task is marked complete)
  - Completed → Active (when task is marked incomplete)
  - Active → Soft-deleted (when task is deleted, retained for 30 days)
  - Soft-deleted → Permanently deleted (after 30 days)

- **Relationships**:
  - Many-to-one with User entity (many tasks belong to one user)

## Entity: AuthenticationToken
- **Fields**:
  - token (string): The JWT token string
  - user_id (UUID/string): Foreign key linking to the user
  - issued_at (datetime): When the token was issued
  - expires_at (datetime): When the token expires
  - is_revoked (boolean): Whether the token has been revoked

- **Validation rules**:
  - Token must be valid JWT format
  - User_id must correspond to an existing user
  - Expires_at must be in the future when created

- **Relationships**:
  - Many-to-one with User entity

## Entity: APISession
- **Fields**:
  - id (UUID/string): Unique identifier for the session
  - user_id (UUID/string): Foreign key linking to the user
  - ip_address (string): IP address of the client
  - user_agent (string): User agent string of the client
  - created_at (datetime): When the session was started
  - last_accessed_at (datetime): When the session was last used
  - expires_at (datetime): When the session expires

- **Validation rules**:
  - User_id must correspond to an existing user
  - Expiry time must be in the future

- **Relationships**:
  - Many-to-one with User entity