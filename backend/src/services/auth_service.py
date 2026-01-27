from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.orm import Session
from ..models.user import User
from ..config.database import engine
from ..config.settings import settings


class TokenData(BaseModel):
    """Pydantic model for token data"""
    username: Optional[str] = None


class AuthService:
    """Authentication service class containing user authentication business logic"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password

        Args:
            plain_password: Plain text password to verify
            hashed_password: Previously hashed password to compare against

        Returns:
            True if passwords match, False otherwise
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token (NOT USED - Backend only verifies tokens from Better Auth)

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta (defaults to 15 minutes)

        Returns:
            Encoded JWT token string
        """
        raise NotImplementedError("Backend should not create tokens; only verify tokens from Better Auth")

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """
        Verify a JWT token and return the decoded data

        Args:
            token: JWT token string to verify

        Returns:
            TokenData object if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
            return token_data
        except jwt.PyJWTError:
            return None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password

        Args:
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            User object if authentication successful, None otherwise
        """
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()

            if not user:
                # Even though user doesn't exist, we still verify the password
                # to prevent timing attacks
                AuthService.verify_password(password, "$2b$12$dummy_hash_for_timing_attack_prevention")
                return None

            if not AuthService.verify_password(password, user.hashed_password):
                return None

            return user

    @staticmethod
    def register_user(username: str, email: str, password: str) -> User:
        """
        Register a new user with the provided credentials

        Args:
            username: Desired username
            email: User's email address
            password: Plain text password

        Returns:
            Created User object

        Raises:
            HTTPException: If username or email already exists
        """
        with Session(engine) as session:
            # Check if username already exists
            statement = select(User).where(User.username == username)
            existing_user = session.exec(statement).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )

            # Check if email already exists
            statement = select(User).where(User.email == email)
            existing_email = session.exec(statement).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user
            hashed_password = AuthService.hash_password(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    @staticmethod
    def get_current_user(token: str) -> Optional[User]:
        """
        Get the current user from a JWT token

        Args:
            token: JWT token string

        Returns:
            User object if token is valid and user exists, None otherwise
        """
        token_data = AuthService.verify_token(token)
        if token_data is None:
            return None

        with Session(engine) as session:
            statement = select(User).where(User.username == token_data.username)
            user = session.exec(statement).first()
            return user


# Convenience functions for external use
def get_current_active_user(token: str) -> Optional[User]:
    """
    Get the current active user from a JWT token

    Args:
        token: JWT token string

    Returns:
        User object if token is valid and user exists and is active, None otherwise
    """
    user = AuthService.get_current_user(token)
    if user is None:
        return None
    return user


def create_access_token_for_user(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token specifically for a user (NOT USED - Backend only verifies tokens from Better Auth)

    Args:
        user: User object to create token for
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    raise NotImplementedError("Backend should not create tokens; only verify tokens from Better Auth")