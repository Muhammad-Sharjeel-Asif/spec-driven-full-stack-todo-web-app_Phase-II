from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import tasks
from src.api.v1 import auth
from src.config.database import create_db_and_tables
import uvicorn

app = FastAPI(title="Todo Backend API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()

# Include API routes
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "todo-backend-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
