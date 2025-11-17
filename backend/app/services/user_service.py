"""User service for business logic."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """User service for managing users."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User or None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User or None
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: Email address

        Returns:
            User or None
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_in: User creation data

        Returns:
            Created user
        """
        user = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        user_in: UserUpdate
    ) -> User:
        """
        Update user.

        Args:
            db: Database session
            user: User to update
            user_in: Update data

        Returns:
            Updated user
        """
        update_data = user_in.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user.

        Args:
            db: Database session
            username: Username
            password: Plain password

        Returns:
            User if authenticated, None otherwise
        """
        user = await UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user: User to update
        """
        user.last_login = datetime.utcnow()
        await db.commit()

    @staticmethod
    async def get_users_by_role(
        db: AsyncSession,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """
        Get users by role.

        Args:
            db: Database session
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        result = await db.execute(
            select(User)
            .where(User.role == role)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        """
        Count total users.

        Args:
            db: Database session

        Returns:
            Total number of users
        """
        from sqlalchemy import func
        result = await db.execute(select(func.count(User.id)))
        return result.scalar_one()
