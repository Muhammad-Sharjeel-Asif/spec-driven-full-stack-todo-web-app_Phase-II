# Todo Backend API

This is the backend API for the Todo Web Application built with FastAPI and SQLModel.

## Features

- FastAPI-based REST API
- SQLModel for database modeling
- JWT-based authentication
- Async database operations
- Alembic for database migrations
- Comprehensive error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Run the application:
```bash
python src/main.py
```

## Endpoints

- `GET /api/v1/tasks/` - Get all tasks
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}` - Get a specific task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
