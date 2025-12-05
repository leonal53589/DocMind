"""Storage service for file management."""

import hashlib
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
import aiofiles
import aiofiles.os

from ..config import get_settings


class StorageService:
    """Service for managing file storage."""

    def __init__(self):
        self.settings = get_settings()
        self.files_path = self.settings.files_path
        self.thumbnails_path = self.settings.thumbnails_path

    async def save_file(
        self,
        file_content: bytes,
        original_filename: str,
        file_hash: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Save a file to storage.

        Returns:
            Tuple of (relative_path, file_hash)
        """
        if not file_hash:
            file_hash = hashlib.sha256(file_content).hexdigest()

        # Organize files by first 2 characters of hash for better filesystem performance
        subdir = file_hash[:2]
        file_dir = self.files_path / subdir
        await aiofiles.os.makedirs(file_dir, exist_ok=True)

        # Keep original extension
        ext = Path(original_filename).suffix
        filename = f"{file_hash}{ext}"
        file_path = file_dir / filename
        relative_path = f"{subdir}/{filename}"

        # Write file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        return relative_path, file_hash

    async def save_file_from_path(self, source_path: Path) -> tuple[str, str, int]:
        """
        Save a file from a local path.

        Returns:
            Tuple of (relative_path, file_hash, file_size)
        """
        # Calculate hash
        hasher = hashlib.sha256()
        file_size = 0

        async with aiofiles.open(source_path, "rb") as f:
            while chunk := await f.read(8192):
                hasher.update(chunk)
                file_size += len(chunk)

        file_hash = hasher.hexdigest()

        # Check if file already exists
        subdir = file_hash[:2]
        ext = source_path.suffix
        filename = f"{file_hash}{ext}"
        file_path = self.files_path / subdir / filename
        relative_path = f"{subdir}/{filename}"

        if not file_path.exists():
            await aiofiles.os.makedirs(file_path.parent, exist_ok=True)
            # Copy file
            shutil.copy2(source_path, file_path)

        return relative_path, file_hash, file_size

    async def get_file_path(self, relative_path: str) -> Path:
        """Get the full path for a stored file."""
        return self.files_path / relative_path

    async def delete_file(self, relative_path: str) -> bool:
        """Delete a file from storage."""
        file_path = self.files_path / relative_path
        if file_path.exists():
            await aiofiles.os.remove(file_path)
            return True
        return False

    async def save_thumbnail(
        self,
        thumbnail_content: bytes,
        item_id: int,
        ext: str = ".jpg",
    ) -> str:
        """
        Save a thumbnail image.

        Returns:
            Relative path to thumbnail
        """
        filename = f"{item_id}{ext}"
        file_path = self.thumbnails_path / filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(thumbnail_content)

        return filename

    async def file_exists(self, file_hash: str, ext: str) -> bool:
        """Check if a file with given hash already exists."""
        subdir = file_hash[:2]
        filename = f"{file_hash}{ext}"
        file_path = self.files_path / subdir / filename
        return file_path.exists()

    @staticmethod
    def calculate_hash(content: bytes) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()
