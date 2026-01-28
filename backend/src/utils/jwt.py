from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from src.config.settings import settings
from src.schemas.auth import TokenData
import uuid
from fastapi import HTTPException, status


# Note: Backend only verifies tokens issued by Better Auth, does not issue its own tokens
# The following functions are kept for compatibility but should not be used for issuing tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create access token with expiration (NOT USED - Backend only verifies tokens from Better Auth)

    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional custom expiration time for the token

    Returns:
        Encoded JWT token as string
    """
    raise NotImplementedError("Backend should not create tokens; only verify tokens from Better Auth")


def create_refresh_token(data: dict) -> str:
    """
    Create refresh token with longer expiration (NOT USED - Backend only verifies tokens from Better Auth)

    Args:
        data: Dictionary containing claims to encode in the token

    Returns:
        Encoded JWT token as string
    """
    raise NotImplementedError("Backend should not create tokens; only verify tokens from Better Auth")


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode access token and return token data

    Args:
        token: JWT token string to decode

    Returns:
        TokenData object if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],  # Better Auth typically uses HS256
            options={"verify_exp": True}
        )
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id_str is None or email is None:
            return None

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            # If user_id is not a valid UUID string, return None
            return None

        token_data = TokenData(user_id=user_id, email=email)
        return token_data
    except ExpiredSignatureError:
        # Token has expired
        return None
    except InvalidTokenError:
        # Token is malformed or invalid
        return None
    except Exception:
        # Any other error during decoding
        return None


def verify_access_token(token: str) -> bool:
    """
    Verify if the access token is valid (not expired and properly formatted)

    Args:
        token: JWT token string to verify

    Returns:
        Boolean indicating if token is valid
    """
    try:
        jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],  # Better Auth typically uses HS256
            options={"verify_exp": True}
        )
        return True
    except (ExpiredSignatureError, InvalidTokenError):
        return False
    except Exception:
        return False


def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode token payload without verification (for debugging purposes)
    WARNING: This does not validate the token signature or expiration

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing token payload if decoding succeeds, None otherwise
    """
    try:
        # Decode without verification for inspection only
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],  # Better Auth typically uses HS256
            options={"verify_signature": False}
        )
        return payload
    except Exception:
        return None


def validate_and_decode_token(token: str) -> Optional[TokenData]:
    """
    Validate and decode token with comprehensive error handling

    Args:
        token: JWT token string to validate and decode

    Returns:
        TokenData object if token is valid, raises HTTPException otherwise
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]  # Better Auth typically uses HS256
        )
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id_str is None or email is None:
            raise credentials_exception

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            # If user_id is not a valid UUID string, raise credentials exception
            raise credentials_exception

        # Check if token is expired
        exp_time = payload.get("exp")
        if exp_time and datetime.fromtimestamp(exp_time) < datetime.utcnow():
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email)
        return token_data

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise credentials_exception


def create_better_auth_compatible_token(user_id: uuid.UUID, username: str) -> Dict[str, str]:
    """
    Create tokens compatible with Better Auth expectations (NOT USED - Backend only verifies tokens from Better Auth)

    Args:
        user_id: User identifier as UUID
        username: Username

    Returns:
        Dictionary containing access and refresh tokens
    """
    raise NotImplementedError("Backend should not create tokens; only verify tokens from Better Auth")


def get_user_from_token(token: str) -> Optional[uuid.UUID]:
    """
    Extract user ID from token

    Args:
        token: JWT token string

    Returns:
        User ID as UUID if found and token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]  # Better Auth typically uses HS256
        )
        user_id_str = payload.get("sub")
        if user_id_str:
            try:
                return uuid.UUID(user_id_str)
            except ValueError:
                # If user_id is not a valid UUID string, return None
                return None
        return None
    except Exception:
        return None