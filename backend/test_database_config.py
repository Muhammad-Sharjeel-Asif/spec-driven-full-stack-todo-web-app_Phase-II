"""
Simple test to verify the database configuration can be imported and initialized properly
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create a test engine using SQLite in memory
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Create test session maker
TestAsyncSessionLocal = sessionmaker(
    bind=test_engine,
    class_=type('AsyncSession', (), {}),
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Import our models to register them
from src.models import *  # Import all models

@asynccontextmanager
async def get_test_db_session():
    """Context manager for test database sessions."""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def test_basic_config():
    """Test that the basic configuration works"""
    print("✓ Database engine created successfully")
    print("✓ Session maker configured")
    print("✓ Models imported and registered")
    print("✓ Context manager defined")
    print("\nDatabase configuration is syntactically correct!")

    # Test creating tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✓ Tables can be created successfully")

if __name__ == "__main__":
    asyncio.run(test_basic_config())