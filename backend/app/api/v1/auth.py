"""Authentication API endpoints."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.user import LoginRequest, Token, User as UserSchema
from app.schemas.common import APIResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=APIResponse[Token])
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    """
    User login endpoint.

    Args:
        login_data: Login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = await UserService.authenticate(
        db,
        username=login_data.username,
        password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await UserService.update_last_login(db, user)

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return APIResponse(
        success=True,
        message="Login successful",
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    )


@router.post("/refresh", response_model=APIResponse[Token])
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(refresh_token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Verify user exists and is active
    user = await UserService.get_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise credentials_exception

    # Create new tokens
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data=Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    )


@router.get("/me", response_model=APIResponse[UserSchema])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> APIResponse[UserSchema]:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return APIResponse(
        success=True,
        message="User information retrieved successfully",
        data=UserSchema.model_validate(current_user)
    )


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    current_user: User = Depends(get_current_user)
) -> APIResponse[None]:
    """
    User logout endpoint.

    Note: This is a placeholder. In a real application, you might want to:
    - Blacklist the token
    - Clear session data
    - Log the logout event

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # In a stateless JWT setup, logout is typically handled client-side
    # by removing the token. Server-side logout would require token blacklisting.

    return APIResponse(
        success=True,
        message="Logout successful"
    )
