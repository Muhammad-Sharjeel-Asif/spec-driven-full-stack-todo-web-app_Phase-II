from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .settings import settings
from sqlmodel import SQLModel
from ..models.user import User
from ..models.task import Task
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize engine only when not running alembic migrations
import os
if os.environ.get('RUNNING_ALEMBIC_MIGRATION'):
    # Create a mock engine for migration generation to avoid connecting to the database
    from sqlalchemy.ext.asyncio import create_async_engine
    # Use postgresql+asyncpg as a placeholder to match the async engine requirement
    engine: AsyncEngine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")  # Temporary for migration
else:
    # Convert string settings to appropriate types for database connection
    db_echo_bool = settings.DB_ECHO.lower() == "true"

    # Convert database URL to asyncpg format if using PostgreSQL
    database_url = settings.DATABASE_URL

    # Initialize ssl_params for all database types
    ssl_params = {}

    if database_url.startswith("sqlite:///"):
        # For SQLite, convert to async SQLite format
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Parse URL and handle asyncpg-specific SSL settings (only for PostgreSQL)
        from urllib.parse import urlparse, parse_qs, urlencode
        parsed = urlparse(database_url)

        # Extract query parameters and handle SSL settings for asyncpg
        query_params = parse_qs(parsed.query)

        # Handle sslmode specially for asyncpg
        if 'sslmode' in query_params:
            sslmode = query_params.pop('sslmode')[0]
            # asyncpg uses ssl parameter instead of sslmode
            if sslmode.lower() in ['require', 'prefer']:
                ssl_params['ssl'] = True
            elif sslmode.lower() == 'disable':
                ssl_params['ssl'] = False

        # Remove channel_binding parameter as it's not supported by asyncpg
        query_params.pop('channel_binding', None)

        # Reconstruct the URL without problematic parameters for asyncpg
        new_query = urlencode(query_params, doseq=True)
        database_url = parsed._replace(query=new_query).geturl()
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Parse URL and handle asyncpg-specific SSL settings (only for PostgreSQL)
        from urllib.parse import urlparse, parse_qs, urlencode
        parsed = urlparse(database_url)

        # Extract query parameters and handle SSL settings for asyncpg
        query_params = parse_qs(parsed.query)

        # Handle sslmode specially for asyncpg
        if 'sslmode' in query_params:
            sslmode = query_params.pop('sslmode')[0]
            # asyncpg uses ssl parameter instead of sslmode
            if sslmode.lower() in ['require', 'prefer']:
                ssl_params['ssl'] = True
            elif sslmode.lower() == 'disable':
                ssl_params['ssl'] = False

        # Remove channel_binding parameter as it's not supported by asyncpg
        query_params.pop('channel_binding', None)

        # Reconstruct the URL without problematic parameters for asyncpg
        new_query = urlencode(query_params, doseq=True)
        database_url = parsed._replace(query=new_query).geturl()
    else:
        # For other database types, use the URL as-is
        pass

    # Set up connect_args based on database type
    if database_url.startswith("postgresql+asyncpg://"):
        connect_args = {
            "server_settings": {
                "application_name": "todo-backend-api",
            },
            **ssl_params
        }
    else:
        # For SQLite and other databases, use minimal connect_args
        connect_args = ssl_params if ssl_params else {}

    engine: AsyncEngine = create_async_engine(
        database_url,
        echo=db_echo_bool,  # Set to True in settings to enable SQL logging
        pool_size=int(settings.DB_POOL_SIZE),
        max_overflow=int(settings.DB_MAX_OVERFLOW),
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=int(settings.DB_POOL_RECYCLE),  # Recycle connections after N seconds
        pool_timeout=int(settings.DB_POOL_TIMEOUT),
        connect_args=connect_args
    )

# Async session maker for database operations
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)

@asynccontextmanager
async def get_db_session():
    """
    Context manager for database sessions.
    Provides an async database session and ensures proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_db_and_tables():
    """
    Creates all database tables defined in the models.
    This function should be called on application startup.
    """
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)

async def ping_db():
    """
    Simple health check to verify database connectivity.
    """
    try:
        async with engine.begin() as conn:
            # Execute a simple query to test connection
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False

# Utility function to get raw connection if needed
async def get_raw_connection():
    """
    Gets a raw database connection for advanced operations.
    Remember to close the connection manually.
    """
    return await engine.connect()