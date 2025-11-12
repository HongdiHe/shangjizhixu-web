"""User management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_superuser, get_current_user
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import (
    PasswordChange,
    User as UserSchema,
    UserCreate,
    UserUpdate,
)
from app.schemas.common import APIResponse
from app.services.user_service import UserService
from app.core.security import verify_password

router = APIRouter()


@router.post("/", response_model=APIResponse[UserSchema])
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> APIResponse[UserSchema]:
    """
    Create a new user (admin only).

    Args:
        user_in: User creation data
        db: Database session
        current_user: Current superuser

    Returns:
        Created user

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    existing_user = await UserService.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = await UserService.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = await UserService.create(db, user_in)

    return APIResponse(
        success=True,
        message="User created successfully",
        data=UserSchema.model_validate(user)
    )


@router.get("/{user_id}", response_model=APIResponse[UserSchema])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[UserSchema]:
    """
    Get user by ID.

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        User information

    Raises:
        HTTPException: If user not found or access denied
    """
    # Users can only view their own profile unless they're superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return APIResponse(
        success=True,
        data=UserSchema.model_validate(user)
    )


@router.put("/{user_id}", response_model=APIResponse[UserSchema])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[UserSchema]:
    """
    Update user.

    Args:
        user_id: User ID
        user_in: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or access denied
    """
    # Users can only update their own profile unless they're superuser
    # Role changes require superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    if user_in.role is not None and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can change user roles"
        )

    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check email uniqueness if changing
    if user_in.email and user_in.email != user.email:
        existing_email = await UserService.get_by_email(db, user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    updated_user = await UserService.update(db, user, user_in)

    return APIResponse(
        success=True,
        message="User updated successfully",
        data=UserSchema.model_validate(updated_user)
    )


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> APIResponse[None]:
    """
    Change user password.

    Args:
        password_data: Password change data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If old password is incorrect
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Update password
    await UserService.update(
        db,
        current_user,
        UserUpdate(password=password_data.new_password)
    )

    return APIResponse(
        success=True,
        message="Password changed successfully"
    )


@router.get("/by-role/{role}", response_model=APIResponse[list[UserSchema]])
async def get_users_by_role(
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> APIResponse[list[UserSchema]]:
    """
    Get users by role (admin only).

    Args:
        role: User role
        db: Database session
        current_user: Current superuser

    Returns:
        List of users with specified role
    """
    users = await UserService.get_users_by_role(db, role)

    return APIResponse(
        success=True,
        data=[UserSchema.model_validate(u) for u in users]
    )
