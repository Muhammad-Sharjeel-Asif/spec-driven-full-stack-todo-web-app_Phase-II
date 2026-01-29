# Quickstart Guide for Todo Resolution Feature

## Prerequisites
- Python 3.9+
- Node.js 18+
- uv package manager
- PostgreSQL (or Neon Serverless PostgreSQL)

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install uv if not already installed
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to include your secrets:
# - BETTER_AUTH_SECRET
# - DATABASE_URL
```

### 3. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Verify Neon Serverless connection
python -c "import sqlalchemy; print('Database connection successful')"
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URLs
```

### 5. Run Applications

#### Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
uvicorn main:app --reload
```

#### Frontend
```bash
# Start the Next.js development server
npm run dev
```

## Key Configuration Files

### Backend Configuration
- `main.py`: FastAPI application entry point
- `models/task.py`: Task data model with user scoping
- `routers/tasks.py`: API routes with {user_id} path parameters
- `middleware/auth.py`: JWT authentication middleware
- `config/settings.py`: Application settings and environment variables

### Frontend Configuration
- `tailwind.config.js`: Tailwind CSS configuration for styling fixes
- `postcss.config.js`: PostCSS configuration
- `services/api.js`: API client with JWT headers and {user_id} paths
- `components/Tasks/TaskList.jsx`: Component with user-scoped task display

## API Endpoints

### User-Scoped Task Operations
- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

## Environment Variables

### Backend (.env)
```
BETTER_AUTH_SECRET=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
UV_ENVIRONMENT=your-uv-environment-path
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret
```

## Testing
```bash
# Backend tests
pytest tests/

# Frontend tests
npm run test

# Run all tests with coverage
# Backend
pytest --cov=src tests/
# Frontend
npm run test:coverage
```

## Troubleshooting

### Common Issues
1. **Styling not rendering**: Verify tailwind.config.js content paths include all components
2. **JWT authentication failing**: Check that BETTER_AUTH_SECRET matches between frontend and backend
3. **CORS errors**: Verify that allowed origins match your frontend URL
4. **Database connection issues**: Check Neon Serverless connection string format