# Quickstart Guide: Todo Backend API

## Prerequisites

- Python 3.11+
- uv package manager
- Access to Neon Serverless PostgreSQL instance
- BETTER_AUTH_SECRET for JWT signing

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set up Virtual Environment
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv pip install -r backend/requirements.txt
uv pip install -r backend/dev-requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
```

### 5. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 6. Start the Development Server
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Available Endpoints

#### Tasks Management
- `GET /api/v1/tasks` - List user's tasks (with optional filtering)
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update a task (with optimistic locking)
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `PATCH /api/v1/tasks/{task_id}/toggle-complete` - Toggle task completion status

#### Filtering Parameters (for GET /api/v1/tasks)
- `completed`: boolean - filter by completion status
- `date_from`: string (ISO date) - filter by creation date range
- `date_to`: string (ISO date) - filter by creation date range

## Testing

### Run Unit Tests
```bash
cd backend
pytest tests/unit/ -v
```

### Run Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

### Run All Tests with Coverage
```bash
cd backend
pytest --cov=src --cov-report=html --cov-report=term
```

## Development Workflow

1. Make changes to the codebase
2. Run tests to ensure functionality: `pytest`
3. Check code quality: `flake8 src/` and `mypy src/`
4. Commit changes with descriptive messages
5. Push to the feature branch

## Troubleshooting

### Common Issues
- **Database connection errors**: Verify DATABASE_URL is correctly set in .env
- **JWT authentication failures**: Ensure BETTER_AUTH_SECRET matches the one used by the frontend
- **Migration errors**: Run `alembic upgrade head` to ensure database schema is up to date

### Development Tips
- Use `--reload` flag with uvicorn for automatic restart on code changes
- Check the API documentation at `/docs` when server is running
- Monitor logs for any authentication or database errors