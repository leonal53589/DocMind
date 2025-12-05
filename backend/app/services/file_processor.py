"""File processor service for handling different file types."""

import mimetypes
from pathlib import Path
from typing import Optional
from PIL import Image
import io

from ..config import get_settings
from .storage import StorageService
from ..utils.extractors import extract_text_from_file, get_mime_type


class FileProcessor:
    """Service for processing different file types."""

    # Supported file extensions by category
    DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.rst', '.html', '.htm'}
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
    VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mkv', '.avi', '.mov', '.wmv'}
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.sh', '.bash',
        '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.sql', '.css', '.scss',
    }

    def __init__(self):
        self.settings = get_settings()
        self.storage = StorageService()

    async def process_file(self, file_path: Path) -> dict:
        """
        Process a file and extract metadata.

        Returns:
            Dictionary with file metadata including:
            - title: filename
            - mime_type: MIME type
            - file_size: size in bytes
            - extracted_text: text content (if applicable)
            - thumbnail_data: thumbnail bytes (if applicable)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        mime_type = get_mime_type(file_path)
        ext = file_path.suffix.lower()

        result = {
            'title': file_path.name,
            'mime_type': mime_type,
            'file_size': file_size,
            'extracted_text': None,
            'thumbnail_data': None,
            'metadata': {},
        }

        # Extract text for documents and code
        if self._is_text_extractable(ext, mime_type):
            result['extracted_text'] = await extract_text_from_file(file_path, mime_type)

        # Generate thumbnail for images
        if ext in self.IMAGE_EXTENSIONS:
            result['thumbnail_data'] = await self._generate_image_thumbnail(file_path)
            result['metadata']['dimensions'] = await self._get_image_dimensions(file_path)

        # Extract video metadata
        if ext in self.VIDEO_EXTENSIONS:
            result['metadata']['video'] = True
            # Could add video duration/dimensions extraction with ffprobe

        return result

    def _is_text_extractable(self, ext: str, mime_type: Optional[str]) -> bool:
        """Check if text can be extracted from this file type."""
        if ext in self.DOCUMENT_EXTENSIONS or ext in self.CODE_EXTENSIONS:
            return True
        if mime_type and mime_type.startswith('text/'):
            return True
        return False

    async def _generate_image_thumbnail(
        self,
        file_path: Path,
        max_size: tuple[int, int] = (300, 300),
    ) -> Optional[bytes]:
        """Generate a thumbnail for an image file."""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
        except Exception as e:
            print(f"Error generating thumbnail for {file_path}: {e}")
            return None

    async def _get_image_dimensions(self, file_path: Path) -> Optional[dict]:
        """Get image dimensions."""
        try:
            with Image.open(file_path) as img:
                return {'width': img.width, 'height': img.height}
        except Exception:
            return None

    def get_content_category_hint(self, file_path: Path) -> Optional[str]:
        """
        Get a category hint based on file type.

        Returns category name or None.
        """
        ext = file_path.suffix.lower()

        if ext in self.CODE_EXTENSIONS:
            return "Program Implementation"

        if ext in {'.tex', '.nb', '.m'}:  # LaTeX, Mathematica
            return "Mathematical Principles"

        return None

    @staticmethod
    def is_supported_file(file_path: Path) -> bool:
        """Check if a file type is supported."""
        ext = file_path.suffix.lower()
        all_supported = (
            FileProcessor.DOCUMENT_EXTENSIONS |
            FileProcessor.IMAGE_EXTENSIONS |
            FileProcessor.VIDEO_EXTENSIONS |
            FileProcessor.CODE_EXTENSIONS
        )
        return ext in all_supported
