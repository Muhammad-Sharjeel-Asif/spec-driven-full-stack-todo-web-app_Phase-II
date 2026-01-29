from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..models.user import User, UserCreate, UserUpdate
from passlib.context import CryptContext
from uuid import UUID


class UserService:
    """
    Service class for handling user-related operations.

    Manages user creation, retrieval, updates, and authentication
    with proper database session handling.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """
        Generate a hash for the given password.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Previously hashed password

        Returns:
            True if passwords match, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            Created User object
        """
        # Hash the password
        hashed_password = self.get_password_hash(user_create.password)

        # Create the user object
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            notification_preferences='{"due_date_reminders": true, "email_notifications": false}'
        )

        # Add to database
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            db: Database session
            email: Email address to search for

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db: Database session
            user_id: User ID to search for

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def update_user(self, db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """
        Update user information.

        Args:
            db: Database session
            user_id: ID of the user to update
            user_update: Updated user data

        Returns:
            Updated User object if successful, None if user not found
        """
        db_user = await self.get_user_by_id(db, user_id)
        if db_user:
            # Update only the fields that are provided in user_update
            if user_update.first_name is not None:
                db_user.first_name = user_update.first_name
            if user_update.last_name is not None:
                db_user.last_name = user_update.last_name
            if user_update.email is not None:
                db_user.email = user_update.email
            if user_update.is_active is not None:
                db_user.is_active = user_update.is_active

            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

        return db_user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(db, email)
        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user