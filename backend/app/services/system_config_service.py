"""System configuration service."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class SystemConfigService:
    """Service for managing system configurations."""

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[SystemConfig]:
        """
        Get configuration by key.

        Args:
            db: Database session
            key: Configuration key

        Returns:
            SystemConfig or None
        """
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.key == key)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SystemConfig]:
        """
        Get all configurations.

        Args:
            db: Database session

        Returns:
            List of SystemConfig
        """
        result = await db.execute(select(SystemConfig))
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession,
        config_in: SystemConfigCreate
    ) -> SystemConfig:
        """
        Create a new configuration.

        Args:
            db: Database session
            config_in: Configuration creation data

        Returns:
            Created SystemConfig
        """
        config = SystemConfig(
            key=config_in.key,
            value=config_in.value,
            description=config_in.description,
            is_secret=config_in.is_secret
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def update(
        db: AsyncSession,
        config: SystemConfig,
        config_in: SystemConfigUpdate
    ) -> SystemConfig:
        """
        Update a configuration.

        Args:
            db: Database session
            config: Configuration to update
            config_in: Update data

        Returns:
            Updated SystemConfig
        """
        if config_in.value is not None:
            config.value = config_in.value

        config.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def delete(db: AsyncSession, config: SystemConfig) -> None:
        """
        Delete a configuration.

        Args:
            db: Database session
            config: Configuration to delete
        """
        await db.delete(config)
        await db.commit()

    @staticmethod
    def mask_secret_value(config: SystemConfig) -> SystemConfig:
        """
        Mask secret configuration values.

        Args:
            config: Configuration to mask

        Returns:
            Configuration with masked value if secret
        """
        if config.is_secret and config.value:
            config.value = "••••••••"
        return config
