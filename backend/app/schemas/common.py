"""Common schemas for API responses."""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20

    def get_offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        """Get limit for database query."""
        return self.page_size
