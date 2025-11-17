"""Object storage service using MinIO."""
import logging
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing object storage with MinIO."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise

    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a file to storage.

        Args:
            file_data: File data as binary stream
            object_name: Name/path of the object in storage
            content_type: MIME type of the file
            metadata: Optional metadata to attach

        Returns:
            str: URL of the uploaded file

        Raises:
            S3Error: If upload fails
        """
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Seek back to start

            # Upload file
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                file_size,
                content_type=content_type,
                metadata=metadata
            )

            # Return URL
            url = self.get_url(object_name)
            logger.info(f"Uploaded file: {object_name}")
            return url

        except S3Error as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            raise

    def upload_from_path(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a file from local path.

        Args:
            file_path: Path to local file
            object_name: Name in storage (defaults to filename)
            content_type: MIME type

        Returns:
            str: URL of uploaded file
        """
        if object_name is None:
            object_name = Path(file_path).name

        with open(file_path, "rb") as file_data:
            return self.upload_file(file_data, object_name, content_type)

    def download_file(self, object_name: str, output_path: str) -> None:
        """
        Download a file from storage.

        Args:
            object_name: Name/path of object in storage
            output_path: Local path to save file

        Raises:
            S3Error: If download fails
        """
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                output_path
            )
            logger.info(f"Downloaded file: {object_name} to {output_path}")
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            raise

    def download_as_bytes(self, object_name: str) -> bytes:
        """
        Download a file as bytes.

        Args:
            object_name: Name/path of object in storage

        Returns:
            bytes: File content

        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            raise

    def delete_file(self, object_name: str) -> None:
        """
        Delete a file from storage.

        Args:
            object_name: Name/path of object to delete

        Raises:
            S3Error: If deletion fails
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            raise

    def delete_files(self, object_names: list[str]) -> None:
        """
        Delete multiple files from storage.

        Args:
            object_names: List of object names to delete
        """
        for object_name in object_names:
            try:
                self.delete_file(object_name)
            except S3Error:
                # Continue deleting other files even if one fails
                continue

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            object_name: Name/path of object

        Returns:
            bool: True if file exists
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def get_url(self, object_name: str) -> str:
        """
        Get the URL for an object.

        Args:
            object_name: Name/path of object

        Returns:
            str: URL to access the object
        """
        # For public access (if bucket is public)
        if settings.MINIO_SECURE:
            protocol = "https"
        else:
            protocol = "http"

        # Use localhost for external access
        endpoint = settings.MINIO_ENDPOINT.replace("minio:", "localhost:")
        return f"{protocol}://{endpoint}/{self.bucket_name}/{object_name}"

    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Get a presigned URL for temporary access.

        Args:
            object_name: Name/path of object
            expires: Expiration time

        Returns:
            str: Presigned URL

        Raises:
            S3Error: If URL generation fails
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL for {object_name}: {e}")
            raise

    def list_files(self, prefix: str = "", recursive: bool = False) -> list[str]:
        """
        List files in storage.

        Args:
            prefix: Filter by prefix
            recursive: Whether to list recursively

        Returns:
            list[str]: List of object names
        """
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=recursive
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            raise

    def get_file_info(self, object_name: str) -> Optional[dict]:
        """
        Get file information.

        Args:
            object_name: Name/path of object

        Returns:
            Optional[dict]: File info or None if not found
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                "name": object_name,
                "size": stat.size,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata
            }
        except S3Error as e:
            logger.error(f"Error getting file info for {object_name}: {e}")
            return None


# Singleton instance
storage_service = StorageService()
