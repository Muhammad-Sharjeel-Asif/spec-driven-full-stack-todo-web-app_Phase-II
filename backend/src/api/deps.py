from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.jwt import validate_and_decode_token
import logging

from src.config.database import AsyncSessionLocal
from src.models.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Async database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency function to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials containing the JWT token
        session: Database session for user lookup

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid, expired, or user doesn't exist
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Verify JWT token using Better Auth
        token_data = validate_and_decode_token(token)

        # Extract user_id from token data
        user_id = token_data.user_id if token_data else None

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = token_data.user_id

        # Query user from database
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Dependency function to get the current user if authenticated, or None.

    Args:
        credentials: Optional HTTP authorization credentials
        session: Database session for user lookup

    Returns:
        User: The authenticated user object or None if not authenticated
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        token_data = validate_and_decode_token(token)

        if not token_data:
            return None

        user_id = token_data.user_id
        user = await session.get(User, user_id)

        return user
    except Exception as e:
        logger.warning(f"Failed to get optional user: {str(e)}")
        return None


from src.services.task_service import TaskService


async def get_task_service(session: AsyncSession = Depends(get_db_session)) -> TaskService:
    """
    Dependency function to get the task service with database session.

    Args:
        session: Database session for the task service

    Returns:
        TaskService: Instance of the task service with the database session
    """
    return TaskService(session)


# Common dependency aliases
CurrentUser = Depends(get_current_user)
OptionalUser = Depends(get_optional_user)
DBSession = Depends(get_db_session)