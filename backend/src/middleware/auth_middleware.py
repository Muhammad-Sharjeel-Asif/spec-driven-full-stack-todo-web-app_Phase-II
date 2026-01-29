from fastapi import Request, HTTPException, status
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from ..utils.jwt_utils import validate_better_auth_token
from typing import Optional, Dict, Any
from ..models.user import User


class JWTBearer(HTTPBearer):
    """
    JWT Bearer authentication middleware for FastAPI.

    Validates JWT tokens issued by Better Auth and extracts user information.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Validate the JWT token from the request and return the decoded payload.

        Args:
            request: The incoming FastAPI request

        Returns:
            Decoded token payload if valid, raises HTTPException otherwise
        """
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)

        if credentials:
            if not credentials.scheme or credentials.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme."
                )

            token = credentials.credentials

            # Validate the token using Better Auth validation
            payload = validate_better_auth_token(token)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token."
                )

            # Store the user info in the request state for later use
            request.state.user = self.extract_user_from_payload(payload)

            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication token provided."
            )

    def extract_user_from_payload(self, payload: Dict[str, Any]) -> User:
        """
        Extract user information from the JWT payload.

        Args:
            payload: The decoded JWT payload

        Returns:
            User object with extracted information
        """
        user_data = payload.get('user', {})

        # Extract user information from the payload
        user_id = user_data.get('id') or payload.get('sub') or payload.get('id')
        email = user_data.get('email') or payload.get('email', '')

        # Create a User object with the available information
        user = User(
            id=user_id,
            email=email,
            hashed_password=''  # Not available from token
        )

        return user


# Function to get current user from request
async def get_current_user_from_request(request: Request) -> Optional[User]:
    """
    Extract the current user from the request state.

    This function can be used as a dependency in route handlers to get the current user.

    Args:
        request: The FastAPI request object

    Returns:
        User object if available in request state, None otherwise
    """
    return getattr(request.state, 'user', None)


# Alternative implementation for checking authentication without auto-error
class OptionalJWTBearer:
    """
    Optional JWT Bearer authentication that doesn't automatically return 401.
    Useful for routes that can be accessed by both authenticated and unauthenticated users.
    """

    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Attempt to validate JWT token from request, but don't raise exception if missing.

        Args:
            request: The incoming FastAPI request

        Returns:
            Decoded token payload if valid, None if no token or invalid
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials and scheme.lower() == "bearer"):
            return None

        # Validate the token using Better Auth validation
        payload = validate_better_auth_token(credentials)
        if payload is not None:
            # Store the user info in the request state for later use
            request.state.user = self.extract_user_from_payload(payload)
            return payload
        else:
            return None

    def extract_user_from_payload(self, payload: Dict[str, Any]) -> User:
        """
        Extract user information from the JWT payload.

        Args:
            payload: The decoded JWT payload

        Returns:
            User object with extracted information
        """
        user_data = payload.get('user', {})

        # Extract user information from the payload
        user_id = user_data.get('id') or payload.get('sub') or payload.get('id')
        email = user_data.get('email') or payload.get('email', '')

        # Create a User object with the available information
        user = User(
            id=user_id,
            email=email,
            hashed_password=''  # Not available from token
        )

        return user