"""
API package for the Todo application.

This package contains all API routers and serves as the entry point
for mounting API routes in the main application.
"""

from fastapi import APIRouter
from .routers import auth, tasks


# Create the main API router
api_router = APIRouter()

# Include all API routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# You can add more routers here as needed
# api_router.include_router(other.router, prefix="/other", tags=["other"])