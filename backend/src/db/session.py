from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config.settings import settings
from sqlmodel import Session
import contextlib


# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO.lower() == "true",  # Convert string to boolean
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)


# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function that yields a database session.

    This function is designed to be used as a FastAPI dependency
    to provide database sessions to route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextlib.contextmanager
def get_db_context():
    """
    Context manager for database sessions.

    Provides a database session and ensures it's properly closed.
    Useful for non-FastAPI contexts where you need a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.

    This function should be called during application startup
    to ensure all required tables exist.
    """
    from ..models import SQLModel  # Import here to avoid circular imports

    # Create all tables defined in the models
    SQLModel.metadata.create_all(bind=engine)