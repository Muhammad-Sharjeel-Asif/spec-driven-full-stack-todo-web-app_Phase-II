import bcrypt
from typing import Union
from ..config.settings import settings


def hash_password(password: Union[str, bytes], rounds: int = None) -> str:
    """
    Hash a password using bcrypt with proper salt generation.

    Args:
        password: The plain text password to hash
        rounds: The cost factor for bcrypt (default: from settings.BCRYPT_ROUNDS)

    Returns:
        The hashed password as a string
    """
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')
    elif not isinstance(password, bytes):
        raise TypeError("Password must be a string or bytes")

    # Use configured bcrypt rounds if not specified
    if rounds is None:
        rounds = settings.BCRYPT_ROUNDS

    # Generate salt and hash the password
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password, salt)

    # Return the hashed password as a string (bcrypt returns bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: Union[str, bytes], hashed_password: Union[str, bytes]) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if the passwords match, False otherwise
    """
    # Convert inputs to bytes if they're strings
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    elif not isinstance(plain_password, bytes):
        raise TypeError("Plain password must be a string or bytes")

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    elif not isinstance(hashed_password, bytes):
        raise TypeError("Hashed password must be a string or bytes")

    # Verify the password
    return bcrypt.checkpw(plain_password, hashed_password)
