from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Request
from ..config.settings import settings
from ..models.user import User
import json


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token using the BETTER_AUTH_SECRET.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        # Decode the token using the secret key
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except InvalidTokenError:
        return None


def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid.

    Args:
        token: The JWT token string to verify

    Returns:
        True if token is valid, False otherwise
    """
    return decode_token(token) is not None


def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Extract user information from a JWT token.

    Args:
        token: The JWT token string

    Returns:
        User object if token is valid and contains user info, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None

    # Extract user information from the token
    # Better Auth tokens typically contain user information in the 'user' claim
    user_data = payload.get('user')
    if not user_data:
        # If no 'user' claim, try to get other identifying information
        user_id = payload.get('sub') or payload.get('id')
        if user_id:
            # Create a minimal user object with the available information
            return User(
                id=user_id,
                email=payload.get('email', ''),
                hashed_password=''  # Not available from token
            )
        return None

    # Create a User object from the extracted data
    return User(
        id=user_data.get('id'),
        email=user_data.get('email', ''),
        hashed_password=''  # Not available from token
    )


def validate_better_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a token issued by Better Auth specifically.

    Args:
        token: The JWT token string from Better Auth

    Returns:
        Decoded token payload if valid Better Auth token, None otherwise
    """
    try:
        # Decode the token using the BETTER_AUTH_SECRET as configured
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            # Optionally, add audience verification if Better Auth sets aud claim
            # audience=[settings.NEXT_PUBLIC_BETTER_AUTH_URL],
        )

        # Verify token hasn't expired
        exp = payload.get('exp')
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        # Verify issuer if present (Better Auth may include iss claim)
        # iss = payload.get('iss')
        # if iss and iss != settings.NEXT_PUBLIC_BETTER_AUTH_URL:
        #     return None

        return payload
    except InvalidTokenError:
        return None


async def get_current_user(request: Request) -> Optional[User]:
    """
    Extract the current user from the Authorization header.

    Args:
        request: The FastAPI request object

    Returns:
        User object if valid token found in Authorization header, None otherwise
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]  # Remove "Bearer " prefix
    return get_current_user_from_token(token)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token with the provided data.

    NOTE: This function is provided for compatibility but should not be used to
    issue tokens that will be recognized by Better Auth. Only Better Auth should
    issue valid authentication tokens. This is provided for potential internal
    use or for systems that need to issue their own tokens.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default 15 minutes

    to_encode.update({"exp": expire.timestamp()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

    return encoded_jwt