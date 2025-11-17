"""System configuration API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_admin
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.system_config import (
    SystemConfigPublic,
    SystemConfigUpdate,
)
from app.services.system_config_service import SystemConfigService

router = APIRouter()


@router.get("/", response_model=APIResponse[List[SystemConfigPublic]])
async def get_all_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[List[SystemConfigPublic]]:
    """
    Get all system configurations (admin only).

    Args:
        db: Database session
        current_user: Current admin user

    Returns:
        List of all system configurations with secret values masked
    """
    configs = await SystemConfigService.get_all(db)

    # Mask secret values
    public_configs = []
    for config in configs:
        if config.is_secret and config.value:
            # Create a copy with masked value
            public_config = SystemConfigPublic(
                id=config.id,
                key=config.key,
                value="••••••••",
                description=config.description,
                is_secret=config.is_secret,
                updated_at=config.updated_at
            )
        else:
            public_config = SystemConfigPublic.model_validate(config)
        public_configs.append(public_config)

    return APIResponse(
        success=True,
        data=public_configs
    )


@router.get("/{key}", response_model=APIResponse[SystemConfigPublic])
async def get_config_by_key(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[SystemConfigPublic]:
    """
    Get system configuration by key (admin only).

    Args:
        key: Configuration key
        db: Database session
        current_user: Current admin user

    Returns:
        System configuration with secret value masked if applicable
    """
    config = await SystemConfigService.get_by_key(db, key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{key}' not found"
        )

    # Mask secret value
    if config.is_secret and config.value:
        public_config = SystemConfigPublic(
            id=config.id,
            key=config.key,
            value="••••••••",
            description=config.description,
            is_secret=config.is_secret,
            updated_at=config.updated_at
        )
    else:
        public_config = SystemConfigPublic.model_validate(config)

    return APIResponse(
        success=True,
        data=public_config
    )


@router.put("/{key}", response_model=APIResponse[SystemConfigPublic])
async def update_config(
    key: str,
    config_in: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin)
) -> APIResponse[SystemConfigPublic]:
    """
    Update system configuration (admin only).

    Args:
        key: Configuration key
        config_in: Configuration update data
        db: Database session
        current_user: Current admin user

    Returns:
        Updated system configuration
    """
    config = await SystemConfigService.get_by_key(db, key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration '{key}' not found"
        )

    updated_config = await SystemConfigService.update(db, config, config_in)

    # Mask secret value
    if updated_config.is_secret and updated_config.value:
        public_config = SystemConfigPublic(
            id=updated_config.id,
            key=updated_config.key,
            value="••••••••",
            description=updated_config.description,
            is_secret=updated_config.is_secret,
            updated_at=updated_config.updated_at
        )
    else:
        public_config = SystemConfigPublic.model_validate(updated_config)

    return APIResponse(
        success=True,
        message="Configuration updated successfully",
        data=public_config
    )
