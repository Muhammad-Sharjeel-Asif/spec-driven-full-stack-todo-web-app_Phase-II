# Data Model: Frontend for Phase II Todo Full-Stack Web Application

## Task Entity

**Fields:**
- id: string (UUID) - Unique identifier for the task
- title: string (required) - Title of the task (min 1 character)
- description: string (optional) - Detailed description of the task (max 1000 characters)
- completed: boolean - Completion status of the task (default: false)
- dueDate: Date (optional) - Due date for the task (ISO 8601 format)
- createdAt: Date (ISO 8601 format) - Timestamp when the task was created (matches "creation timestamp" from spec)
- updatedAt: Date - Timestamp when the task was last updated (ISO 8601 format)
- userId: string - Foreign key linking to the user who owns the task

**Validation Rules:**
- Title must be between 1 and 200 characters
- Description, if provided, must be between 1 and 1000 characters
- Due date, if provided, must be a valid future date
- userId must correspond to an authenticated user

**State Transitions:**
- Active → Completed: When user toggles completion status
- Completed → Active: When user toggles completion status back
- Created → Active: When task is initially created
- Any state → Deleted: When user deletes the task

## User Entity

**Fields:**
- id: string (UUID) - Unique identifier for the user
- email: string (required) - User's email address (unique, valid format)
- name: string (required) - User's display name (min 1 character)
- createdAt: Date (ISO 8601 format) - Timestamp when the user account was created (matches "creation timestamp" from spec)
- updatedAt: Date - Timestamp when the user account was last updated
- emailVerified: boolean - Whether the user's email has been verified

**Validation Rules:**
- Email must be unique and in valid email format
- Name must be between 1 and 100 characters
- Email must be verified before full access to task features

## Authentication Session Entity

**Fields:**
- token: string (JWT) - The authentication token
- userId: string - Reference to the authenticated user
- expiresAt: Date - Expiration timestamp for the token
- createdAt: Date - When the session was created

**Validation Rules:**
- Token must be a valid JWT
- Session must be renewed before expiration
- Token must correspond to a valid user account