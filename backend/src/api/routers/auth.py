from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ...config.database import get_db_session  # Use async database session
from ...models.user import User, UserCreate, UserRead
from ...services.user_service import UserService
from ...utils.jwt_utils import create_access_token
from datetime import timedelta
from ...config.settings import settings


router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserRead)
async def register_user(user_create: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Register a new user.

    Creates a new user account with the provided information.
    The password will be hashed before storing.
    """
    user_service = UserService()

    # Check if user already exists
    existing_user = await user_service.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create the user
    user = await user_service.create_user(db, user_create)
    return user


@router.post("/login")
async def login_user(request: Request, user_credentials: dict, db: AsyncSession = Depends(get_db_session)):
    """
    Login a user and return an access token.

    Authenticates the user with the provided credentials.
    Returns an access token that can be used for subsequent requests.
    """
    email = user_credentials.get("email")
    password = user_credentials.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    user_service = UserService()
    user = await user_service.authenticate_user(db, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token that expires in settings
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user) if hasattr(UserRead, 'model_validate') else UserRead.model_construct(**user.__dict__)
    }


@router.post("/logout")
async def logout_user():
    """
    Logout the current user.

    Performs server-side logout operations if needed.
    Client should discard the access token after this call.
    """
    # In a stateless JWT system, the server doesn't maintain session state
    # So logout is primarily a client-side operation
    # But we could implement token blacklisting if needed
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the current user's information.

    Returns the user information for the authenticated user.
    Requires a valid access token in the Authorization header.
    """
    # Get the user from the request state (set by authentication middleware)
    current_user = getattr(request.state, 'user', None)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch the user from the database to ensure we have the latest information
    user_service = UserService()
    db_user = await user_service.get_user_by_id(db, current_user.id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user