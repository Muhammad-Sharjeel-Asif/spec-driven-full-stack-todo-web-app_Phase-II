# Todo Backend API - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Authentication](#authentication)
5. [Security Features](#security-features)
6. [Database Schema](#database-schema)
7. [Deployment](#deployment)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

## Overview

The Todo Backend API is a secure, scalable task management system built with FastAPI and PostgreSQL. It provides user-isolated task management with robust authentication, comprehensive security measures, and optimized performance.

### Features
- **Multi-User Support**: Each user has isolated tasks that cannot be accessed by other users
- **JWT Authentication**: Secure authentication using Better Auth-compatible JWT tokens
- **User-Scoped Endpoints**: All task operations are scoped to the authenticated user
- **Comprehensive Security**: Rate limiting, CORS protection, and detailed logging
- **RESTful API**: Well-structured endpoints following REST conventions
- **OpenAPI Documentation**: Auto-generated API documentation available at `/docs`
- **Soft Delete**: Tasks can be soft-deleted with 30-day retention
- **Notifications**: Task reminder and notification system
- **Caching**: Optimized performance with caching for frequently accessed data

## Architecture

### Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT with python-jose
- **Caching**: In-memory cache with TTL support
- **Database**: Neon Serverless PostgreSQL
- **Migration**: Alembic for database migrations

### Project Structure
```
backend/
├── src/
│   ├── api/              # API routes and endpoints
│   │   └── routers/      # Individual route files
│   ├── models/           # Database models (SQLModel)
│   ├── services/         # Business logic layer
│   │   ├── task_service.py     # Task-related operations
│   │   ├── user_service.py     # User-related operations
│   │   ├── notification_service.py  # Notification system
│   │   └── cache_service.py    # Caching functionality
│   ├── middleware/       # Authentication and other middleware
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration settings
│   └── database/         # Database session management
├── alembic/              # Database migration files
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # Project overview
```

### Data Flow
1. **Request**: Client sends request with JWT token
2. **Authentication**: Middleware validates JWT and extracts user
3. **Authorization**: Service layer verifies user has access to requested resource
4. **Business Logic**: Service processes request with proper user scoping
5. **Database**: Operations performed on user-specific data
6. **Response**: Formatted response returned to client

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and get JWT token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user's profile

### Task Endpoints
- `GET /api/{user_id}/tasks` - Get all tasks for a user with filtering and pagination
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{task_id}` - Soft delete a specific task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle task completion status
- `GET /api/{user_id}/tasks/stats` - Get user's task statistics
- `GET /api/{user_id}/tasks/deleted` - Get soft-deleted tasks
- `POST /api/{user_id}/tasks/{task_id}/restore` - Restore a soft-deleted task

### Parameters
#### Common Query Parameters
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100, max: 1000)
- `status` (string): Filter by completion status (`all`, `completed`, `pending`)
- `priority` (string): Filter by priority (`low`, `medium`, `high`)
- `due_date_from` (datetime): Filter tasks with due date on or after this date
- `due_date_to` (datetime): Filter tasks with due date on or before this date
- `sort_by` (string): Field to sort by (`created_at`, `updated_at`, `due_date`, `priority`)
- `sort_order` (string): Sort order (`asc`, `desc`)

## Authentication

### JWT Implementation
The API uses JWT (JSON Web Tokens) for authentication, compatible with Better Auth standards.

#### Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1640995200
}
```

#### Obtaining Tokens
1. Register a user via `POST /api/auth/register`
2. Login via `POST /api/auth/login` to receive a JWT token
3. Include token in requests using `Authorization: Bearer <token>`

#### Token Validation
- Tokens are validated using the `BETTER_AUTH_SECRET` from environment variables
- Expired tokens are rejected with 401 Unauthorized
- Invalid tokens are rejected with 401 Unauthorized

## Security Features

### Rate Limiting
- **Tasks endpoints**: 100 requests per minute
- **Specific task endpoints**: 50 requests per minute
- **Login endpoint**: 5 attempts per 5 minutes
- **Registration endpoint**: 2 attempts per hour
- **Profile endpoint**: 20 requests per minute

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when rate limit resets

### CORS Protection
- Restricted to safe origins defined in configuration
- Credentials allowed only for trusted origins
- Specific HTTP methods and headers allowed

### User Isolation
- Each user can only access their own tasks
- Attempting to access another user's resources results in 403 Forbidden
- User ID validation performed on every request

### Input Validation
- All inputs validated using Pydantic models
- SQL injection prevented through ORM usage
- Cross-site scripting prevented through proper output encoding

## Database Schema

### Task Model
```python
class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=5)  # 1-5 scale
    due_date: Optional[datetime] = Field(default=None)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)  # For soft deletes
    notification_settings: Optional[str] = Field(default='{"reminder_enabled": false, "reminder_time": null}')
    version: int = Field(default=1)  # For optimistic locking
```

### User Model
```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notification_preferences: str = Field(default='{"due_date_reminders": true, "email_notifications": false}')
```

### Recommended Database Indexes
- `idx_tasks_user_id` - Index on `user_id` column in `tasks` table
- `idx_tasks_completed` - Index on `is_completed` column in `tasks` table
- `idx_tasks_priority` - Index on `priority` column in `tasks` table
- `idx_tasks_due_date` - Index on `due_date` column in `tasks` table
- `idx_tasks_deleted_at` - Index on `deleted_at` column in `tasks` table
- `idx_tasks_user_completed` - Composite index on `(user_id, is_completed)`
- `idx_tasks_user_priority` - Composite index on `(user_id, priority)`
- `idx_tasks_user_due_date` - Composite index on `(user_id, due_date)`
- `idx_tasks_user_deleted` - Composite index on `(user_id, deleted_at)`

## Deployment

### Environment Variables
Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/todo_app

# Authentication Configuration
BETTER_AUTH_SECRET=your_jwt_secret_key_here
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000

# Rate Limiting
RATE_LIMIT_TASKS_PER_MINUTE=100
RATE_LIMIT_LOGIN_ATTEMPTS=5

# Security
SSL_REDIRECT=true
SECURE_SSL_REDIRECT=true
USE_HTTPS_INSTEAD_OF_SSL=true
```

### Production Deployment Steps
1. Set up PostgreSQL database (Neon Serverless recommended)
2. Configure environment variables
3. Run database migrations: `alembic upgrade head`
4. Start the application: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
5. Set up reverse proxy (nginx) with SSL termination
6. Configure monitoring and logging

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing

### Unit Tests
Run all unit tests:
```bash
pytest tests/unit/ -v
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Integration Tests
Run integration tests:
```bash
pytest tests/integration/ -v
```

### Test Structure
```
tests/
├── unit/                 # Unit tests for individual functions/classes
│   ├── test_task_service.py
│   ├── test_user_service.py
│   ├── test_notification_service.py
│   └── test_cache_service.py
├── integration/          # Integration tests for API endpoints
│   └── test_api_integration.py
├── conftest.py           # Test configuration and fixtures
└── requirements-test.txt # Test dependencies
```

### Test Coverage Targets
- **Minimum coverage**: 80%
- **Critical paths**: 100% coverage required
- **Authentication**: 100% coverage required
- **User isolation**: 100% coverage required

## Error Handling

### HTTP Status Codes
- `200 OK` - Successful GET, PUT, PATCH requests
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## Performance Optimization

### Caching Strategy
- **User profiles**: Cached for 10 minutes
- **Task lists**: Cached for 5 minutes per user
- **Statistics**: Cached for 1 minute
- **Configuration data**: Cached for 1 hour

### Database Optimization
- Use connection pooling with appropriate settings
- Implement proper indexing strategy
- Use pagination for large datasets
- Avoid N+1 query problems with proper relationship loading

### API Performance Targets
- **Response time**: <200ms for 95th percentile
- **Throughput**: Handle 1000+ concurrent requests
- **Memory usage**: <512MB under normal load

## Monitoring and Logging

### Log Format
All logs follow JSON format for easy parsing:
```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "uuid",
  "method": "GET",
  "path": "/api/users/123/tasks",
  "status_code": 200,
  "duration_ms": 150,
  "user_id": "user-uuid"
}
```

### Metrics Collected
- Request rate (requests per second)
- Response time percentiles (p50, p95, p99)
- Error rates (4xx, 5xx responses)
- Database connection pool usage
- Cache hit/miss ratios
- Active users count

## Troubleshooting

### Common Issues

#### 500 Internal Server Error
1. Check application logs for detailed error message
2. Verify database connection
3. Check environment variables are set correctly
4. Look for missing dependencies

#### 401 Unauthorized
1. Verify JWT token is included in request header
2. Check token hasn't expired
3. Ensure token was obtained from login endpoint
4. Verify `BETTER_AUTH_SECRET` matches between frontend and backend

#### 403 Forbidden
1. Confirm user_id in URL matches authenticated user
2. Verify task belongs to authenticated user
3. Check user account is active

#### Slow Response Times
1. Check database performance
2. Verify proper indexing is in place
3. Review for N+1 query issues
4. Consider caching frequently accessed data

### Debugging Tips
- Enable DEBUG mode in development environment
- Use FastAPI's built-in documentation at `/docs`
- Check database connection with `SELECT 1` query
- Monitor rate limit headers in responses
- Use logging to trace request flow

### Performance Monitoring
- Monitor database query times
- Track cache effectiveness
- Watch for memory leaks
- Measure API response times

## Maintenance

### Regular Tasks
- Rotate authentication secrets monthly
- Archive old soft-deleted tasks
- Update dependencies quarterly
- Review and update security measures
- Clean up old logs periodically

### Backup Strategy
- Database backups daily
- Configuration backups version controlled
- Secrets stored securely (not in code)
- Recovery procedures documented and tested

## Support

### Contact Information
- **Development Team**: [contact email]
- **Production Issues**: [support email]
- **Documentation**: [documentation URL]
- **Issue Tracker**: [issue tracker URL]

### Escalation Process
1. Check logs for error details
2. Verify issue is reproducible
3. Contact development team if needed
4. Follow incident response procedures
5. Document resolution for future reference