"""Text extraction utilities for various file types."""

import mimetypes
from pathlib import Path
from typing import Optional
import io


async def extract_text_from_file(file_path: Path, mime_type: Optional[str] = None) -> Optional[str]:
    """
    Extract text content from a file based on its type.

    Supports:
    - Plain text files (.txt, .md, .py, .js, etc.)
    - PDF files (.pdf)
    - Word documents (.docx)
    - HTML files (.html, .htm)
    """
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(str(file_path))

    if not mime_type:
        # Try to guess from extension
        ext = file_path.suffix.lower()
        text_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb',
            '.php', '.swift', '.kt', '.scala', '.sh', '.bash', '.zsh',
            '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg',
            '.css', '.scss', '.sass', '.less', '.sql', '.r', '.lua',
        }
        if ext in text_extensions:
            mime_type = 'text/plain'

    if not mime_type:
        return None

    try:
        if mime_type.startswith('text/') or mime_type in ['application/json', 'application/xml']:
            return await _extract_text_plain(file_path)

        elif mime_type == 'application/pdf':
            return await _extract_text_pdf(file_path)

        elif mime_type in [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]:
            return await _extract_text_docx(file_path)

        elif mime_type == 'text/html':
            return await _extract_text_html(file_path)

    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None

    return None


async def _extract_text_plain(file_path: Path) -> str:
    """Extract text from plain text files."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk', 'gb2312']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    # Fallback: read as binary and decode with errors='replace'
    with open(file_path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace')


async def _extract_text_pdf(file_path: Path) -> Optional[str]:
    """Extract text from PDF files using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF not installed, skipping PDF extraction")
        return None

    text_parts = []
    doc = fitz.open(file_path)

    for page in doc:
        text_parts.append(page.get_text())

    doc.close()
    return '\n\n'.join(text_parts)


async def _extract_text_docx(file_path: Path) -> Optional[str]:
    """Extract text from Word documents."""
    try:
        from docx import Document
    except ImportError:
        print("python-docx not installed, skipping DOCX extraction")
        return None

    doc = Document(file_path)
    text_parts = []

    for para in doc.paragraphs:
        text_parts.append(para.text)

    return '\n\n'.join(text_parts)


async def _extract_text_html(file_path: Path) -> Optional[str]:
    """Extract text from HTML files."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("BeautifulSoup not installed, skipping HTML extraction")
        return None

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()

    return soup.get_text(separator='\n', strip=True)


def get_mime_type(file_path: Path) -> Optional[str]:
    """Get MIME type for a file."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type
