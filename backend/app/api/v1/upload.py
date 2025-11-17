"""File upload API endpoints."""
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.upload import ImageUploadResponse, MultiImageUploadResponse
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.

    Args:
        file: Uploaded file

    Raises:
        HTTPException: If file is invalid
    """
    # Check content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.ALLOWED_IMAGE_TYPES}"
        )

    # Check file size (if we can)
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )


def generate_object_name(filename: str, user_id: int) -> str:
    """
    Generate unique object name for storage.

    Args:
        filename: Original filename
        user_id: User ID

    Returns:
        str: Object name for storage
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    # Keep extension
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    return f"questions/{user_id}/{timestamp}.{ext}"


@router.post("/image", response_model=APIResponse[ImageUploadResponse])
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[ImageUploadResponse]:
    """
    Upload a single image file.

    Args:
        file: Image file
        current_user: Current authenticated user

    Returns:
        Image upload response with URL

    Raises:
        HTTPException: If upload fails
    """
    # Validate file
    validate_image_file(file)

    try:
        # Generate object name
        object_name = generate_object_name(file.filename, current_user.id)

        # Upload to storage
        file_content = await file.read()
        from io import BytesIO
        file_data = BytesIO(file_content)

        url = storage_service.upload_file(
            file_data=file_data,
            object_name=object_name,
            content_type=file.content_type,
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename
            }
        )

        logger.info(
            f"Image uploaded successfully: {object_name} by user {current_user.id}"
        )

        return APIResponse(
            success=True,
            message="Image uploaded successfully",
            data=ImageUploadResponse(
                url=url,
                filename=file.filename,
                size=len(file_content)
            )
        )

    except Exception as e:
        logger.error(f"Error uploading image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )
    finally:
        await file.close()


@router.post("/images", response_model=APIResponse[MultiImageUploadResponse])
async def upload_multiple_images(
    files: List[UploadFile] = File(..., description="Multiple image files"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[MultiImageUploadResponse]:
    """
    Upload multiple image files.

    Args:
        files: List of image files
        current_user: Current authenticated user

    Returns:
        Multiple image upload response with URLs

    Raises:
        HTTPException: If upload fails
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed per request"
        )

    uploaded_images = []
    failed_uploads = []

    for file in files:
        try:
            # Validate file
            validate_image_file(file)

            # Generate object name
            object_name = generate_object_name(file.filename, current_user.id)

            # Upload to storage
            file_content = await file.read()
            from io import BytesIO
            file_data = BytesIO(file_content)

            url = storage_service.upload_file(
                file_data=file_data,
                object_name=object_name,
                content_type=file.content_type,
                metadata={
                    "user_id": str(current_user.id),
                    "original_filename": file.filename
                }
            )

            uploaded_images.append(
                ImageUploadResponse(
                    url=url,
                    filename=file.filename,
                    size=len(file_content)
                )
            )

            logger.info(
                f"Image uploaded: {object_name} by user {current_user.id}"
            )

        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {e}")
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })

        finally:
            await file.close()

    if not uploaded_images and failed_uploads:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"All uploads failed: {failed_uploads}"
        )

    message = f"Successfully uploaded {len(uploaded_images)} images"
    if failed_uploads:
        message += f", {len(failed_uploads)} failed"

    return APIResponse(
        success=True,
        message=message,
        data=MultiImageUploadResponse(
            images=uploaded_images,
            total=len(uploaded_images)
        )
    )
