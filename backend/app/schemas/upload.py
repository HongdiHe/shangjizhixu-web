"""File upload schemas."""
from typing import List
from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """Image upload response schema."""

    url: str = Field(..., description="Uploaded image URL")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")


class MultiImageUploadResponse(BaseModel):
    """Multiple image upload response schema."""

    images: List[ImageUploadResponse]
    total: int
