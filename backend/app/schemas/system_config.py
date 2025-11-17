"""System configuration schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SystemConfigBase(BaseModel):
    """Base system config schema."""

    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    is_secret: bool = False


class SystemConfigCreate(SystemConfigBase):
    """Schema for creating a system config."""

    pass


class SystemConfigUpdate(BaseModel):
    """Schema for updating a system config."""

    value: Optional[str] = None


class SystemConfigInDB(SystemConfigBase):
    """System config schema with all database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SystemConfig(SystemConfigInDB):
    """Full system config response schema."""

    pass


class SystemConfigPublic(BaseModel):
    """Public system config schema (hides secret values)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    value: Optional[str] = None  # Will be masked if is_secret=True
    description: Optional[str] = None
    is_secret: bool
    updated_at: datetime
