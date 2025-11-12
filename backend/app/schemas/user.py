"""User schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.enums import UserRole


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.OCR_EDITOR


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInDB(UserBase):
    """User schema with database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserInDB):
    """Public user schema (response)."""

    pass


class UserWithStats(User):
    """User schema with statistics."""

    total_ocr_tasks: int = 0
    completed_ocr_tasks: int = 0
    total_rewrite_tasks: int = 0
    completed_rewrite_tasks: int = 0


# Authentication schemas
class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str
    exp: int
    type: str


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class PasswordChange(BaseModel):
    """Password change request schema."""

    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
