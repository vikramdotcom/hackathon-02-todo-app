"""
File Upload and Storage Management

Handle file uploads with multiple storage backends.
"""

import logging
import os
import hashlib
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class FileMetadata:
    """File metadata."""

    def __init__(
        self,
        filename: str,
        size: int,
        content_type: str,
        checksum: str,
        storage_path: str,
        uploaded_by: Optional[int] = None
    ):
        """Initialize file metadata."""
        self.filename = filename
        self.size = size
        self.content_type = content_type
        self.checksum = checksum
        self.storage_path = storage_path
        self.uploaded_by = uploaded_by
        self.uploaded_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "size": self.size,
            "content_type": self.content_type,
            "checksum": self.checksum,
            "storage_path": self.storage_path,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat()
        }


class StorageBackend:
    """Base storage backend."""

    async def save(self, file: BinaryIO, path: str) -> str:
        """Save file."""
        raise NotImplementedError

    async def load(self, path: str) -> bytes:
        """Load file."""
        raise NotImplementedError

    async def delete(self, path: str):
        """Delete file."""
        raise NotImplementedError

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage."""

    def __init__(self, base_path: str = "uploads"):
        """Initialize local storage."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: BinaryIO, path: str) -> str:
        """Save file to local filesystem."""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(file.read())

        return str(full_path)

    async def load(self, path: str) -> bytes:
        """Load file from local filesystem."""
        full_path = self.base_path / path

        with open(full_path, 'rb') as f:
            return f.read()

    async def delete(self, path: str):
        """Delete file from local filesystem."""
        full_path = self.base_path / path

        if full_path.exists():
            full_path.unlink()

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        full_path = self.base_path / path
        return full_path.exists()


class S3StorageBackend(StorageBackend):
    """AWS S3 storage."""

    def __init__(self, bucket: str, region: str = "us-east-1"):
        """Initialize S3 storage."""
        self.bucket = bucket
        self.region = region

    async def save(self, file: BinaryIO, path: str) -> str:
        """Save file to S3."""
        # In production, use boto3
        logger.info(f"Would upload to S3: s3://{self.bucket}/{path}")
        return f"s3://{self.bucket}/{path}"

    async def load(self, path: str) -> bytes:
        """Load file from S3."""
        # In production, use boto3
        logger.info(f"Would download from S3: s3://{self.bucket}/{path}")
        return b""

    async def delete(self, path: str):
        """Delete file from S3."""
        # In production, use boto3
        logger.info(f"Would delete from S3: s3://{self.bucket}/{path}")

    async def exists(self, path: str) -> bool:
        """Check if file exists in S3."""
        # In production, use boto3
        return False


class FileUploadManager:
    """Manage file uploads."""

    def __init__(self, storage: StorageBackend, max_size: int = 10 * 1024 * 1024):
        """Initialize upload manager."""
        self.storage = storage
        self.max_size = max_size
        self.allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "text/plain",
            "text/csv"
        ]

    def validate_file(self, filename: str, size: int, content_type: str):
        """Validate file upload."""
        # Check size
        if size > self.max_size:
            raise ValueError(f"File too large: {size} bytes (max: {self.max_size})")

        # Check content type
        if content_type not in self.allowed_types:
            raise ValueError(f"File type not allowed: {content_type}")

        # Check filename
        if not filename or ".." in filename:
            raise ValueError("Invalid filename")

    def generate_storage_path(self, filename: str, user_id: Optional[int] = None) -> str:
        """Generate storage path."""
        # Create path with date structure
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")

        # Generate unique filename
        ext = Path(filename).suffix
        unique_name = f"{now.timestamp()}_{hashlib.md5(filename.encode()).hexdigest()[:8]}{ext}"

        if user_id:
            return f"{user_id}/{date_path}/{unique_name}"
        else:
            return f"public/{date_path}/{unique_name}"

    def calculate_checksum(self, file: BinaryIO) -> str:
        """Calculate file checksum."""
        md5 = hashlib.md5()
        file.seek(0)

        while chunk := file.read(8192):
            md5.update(chunk)

        file.seek(0)
        return md5.hexdigest()

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> FileMetadata:
        """Upload file."""
        # Detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        # Get file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        # Validate
        self.validate_file(filename, size, content_type)

        # Calculate checksum
        checksum = self.calculate_checksum(file)

        # Generate storage path
        storage_path = self.generate_storage_path(filename, user_id)

        # Save file
        await self.storage.save(file, storage_path)

        # Create metadata
        metadata = FileMetadata(
            filename=filename,
            size=size,
            content_type=content_type,
            checksum=checksum,
            storage_path=storage_path,
            uploaded_by=user_id
        )

        logger.info(
            f"File uploaded: {filename}",
            extra={
                "filename": filename,
                "size": size,
                "user_id": user_id,
                "storage_path": storage_path
            }
        )

        return metadata

    async def download(self, storage_path: str) -> bytes:
        """Download file."""
        return await self.storage.load(storage_path)

    async def delete(self, storage_path: str):
        """Delete file."""
        await self.storage.delete(storage_path)

        logger.info(f"File deleted: {storage_path}")


# Global upload manager
upload_manager = FileUploadManager(LocalStorageBackend())


# Helper functions
async def upload_file(file: BinaryIO, filename: str, user_id: Optional[int] = None) -> FileMetadata:
    """Upload file."""
    return await upload_manager.upload(file, filename, user_id=user_id)


async def download_file(storage_path: str) -> bytes:
    """Download file."""
    return await upload_manager.download(storage_path)


async def delete_file(storage_path: str):
    """Delete file."""
    await upload_manager.delete(storage_path)
