# Todo Backend API

A secure multi-user task management API built with FastAPI, featuring JWT authentication, user-scoped operations, and comprehensive security measures.

## Features

- **Multi-User Support**: Each user has isolated tasks that cannot be accessed by other users
- **JWT Authentication**: Secure authentication using Better Auth-compatible JWT tokens
- **User-Scoped Endpoints**: All task operations are scoped to the authenticated user
- **Comprehensive Security**: Rate limiting, CORS protection, and detailed logging
- **RESTful API**: Well-structured endpoints following REST conventions
- **OpenAPI Documentation**: Auto-generated API documentation available at `/docs`
- **Soft Delete**: Tasks can be soft-deleted with 30-day retention
- **Notifications**: Task reminder and notification system
- **Caching**: Optimized performance with caching for frequently accessed data

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and get JWT token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user's profile

### Tasks
- `GET /api/{user_id}/tasks` - Get all tasks for a user with filtering and pagination
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{task_id}` - Soft delete a specific task (30-day retention)
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle task completion status
- `GET /api/{user_id}/tasks/stats` - Get user's task statistics
- `GET /api/{user_id}/tasks/deleted` - Get soft-deleted tasks
- `POST /api/{user_id}/tasks/{task_id}/restore` - Restore a soft-deleted task

## Authentication Flows

### Registration Flow
1. User submits registration data (email, password, optional name)
2. System creates new user account with hashed password
3. Returns user profile data (excluding sensitive information)

### Login Flow
1. User submits email and password
2. System verifies credentials
3. Generates JWT token with user information
4. Returns access token and user profile

### Protected Endpoint Flow
1. Client includes JWT token in `Authorization: Bearer <token>` header
2. Authentication middleware validates token and extracts user ID
3. Endpoint verifies user has permission to access requested resource
4. Only allows operations on user's own data

### Token Refresh
- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days (if implemented)
- Better Auth handles token lifecycle on frontend

## Integration Notes

### Frontend Integration
- Use Better Auth for frontend authentication
- Pass JWT tokens from Better Auth to backend requests
- Include user ID in API paths: `/api/{user_id}/tasks`
- Handle 401/403 responses appropriately
- Implement optimistic updates for task completion

### Backend Integration Points
- **Database**: Neon Serverless PostgreSQL with connection pooling
- **Authentication**: Compatible with Better Auth JWT tokens
- **Caching**: In-memory cache with TTL for frequently accessed data
- **Notifications**: Configurable notification system with email/push options
- **Logging**: Structured logging with request tracing

### Error Handling Integration
- Standardized error responses with consistent structure
- Detailed error messages for debugging
- Rate limit headers for client-side throttling
- Proper HTTP status codes for all responses

## Security Features

### Authentication
All endpoints (except auth endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Rate Limiting
- Tasks endpoints: 100 requests per minute
- Specific task endpoints: 50 requests per minute
- Login endpoint: 5 attempts per 5 minutes
- Registration endpoint: 2 attempts per hour
- Profile endpoint: 20 requests per minute

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when rate limit resets

### CORS Protection
Restricted to safe origins by default. Configure in environment variables.

### User Isolation
Each user can only access their own tasks. Attempting to access another user's resources results in a 403 Forbidden error.

### Database Security
- Soft deletes with 30-day retention period
- User ID validation on all database queries
- Parameterized queries to prevent SQL injection
- Row-level security for multi-tenant isolation

## Environment Variables

Create a `.env` file in the backend root with the following variables:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your_jwt_secret_key_here
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DB_ECHO=false
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DEBUG=false
