from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import tasks as tasks_router
from src.api.routers import auth as auth_router
from src.config.database import create_db_and_tables
import uvicorn
from src.config.settings import settings
from src.middleware.rate_limiter import RateLimitMiddleware
from src.middleware.logging_middleware import LoggingMiddleware
from src.middleware.https_redirect_middleware import HTTPSRedirectMiddleware, add_security_headers

app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    description="Secure multi-user task management API with JWT authentication",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authentication operations using Better Auth"
        },
        {
            "name": "tasks",
            "description": "Task management operations with user-scoped access"
        }
    ]
)

# HTTPS redirect middleware - should be first in the chain for production
app.add_middleware(HTTPSRedirectMiddleware)

# Logging middleware - should be early to capture all requests
app.add_middleware(LoggingMiddleware)

# Rate limiting middleware - should be early to catch requests before processing
app.add_middleware(
    RateLimitMiddleware,
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
)

# CORS middleware - Restrictive configuration for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Add security headers to all responses
@app.middleware("http")
async def add_security_headers_middleware(request, call_next):
    response = await call_next(request)
    return add_security_headers(response)

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()

# Include API routes with proper versioning
app.include_router(tasks_router.router, prefix="/api", tags=["tasks"])
app.include_router(auth_router.router, prefix="/api", tags=["authentication"])

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "todo-backend-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
