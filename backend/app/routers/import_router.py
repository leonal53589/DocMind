"""Import API router for files and URLs."""

import os
import urllib.parse
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Item
from ..schemas.item import ItemResponse, ItemImportRequest, ItemImportResponse
from ..services import StorageService, FileProcessor, WebScraper, Classifier
from ..config import get_settings


def decode_filename(filename: str) -> str:
    """
    Decode filename to handle various encoding scenarios.

    Handles:
    - URL-encoded filenames (e.g., %E8%87%AA%E7%9E%84.pdf -> 自瞄.pdf)
    - RFC 5987 encoded filenames (filename*=UTF-8''...)
    - Regular UTF-8 filenames
    """
    if not filename:
        return filename

    # Try URL decoding first (handles %xx encoding)
    try:
        decoded = urllib.parse.unquote(filename, encoding='utf-8')
        if decoded != filename:
            return decoded
    except Exception:
        pass

    # Handle RFC 5987 encoding (filename*=UTF-8''...)
    if filename.startswith("UTF-8''") or filename.startswith("utf-8''"):
        try:
            encoded_part = filename.split("''", 1)[1]
            return urllib.parse.unquote(encoded_part, encoding='utf-8')
        except Exception:
            pass

    # Return as-is if no decoding needed
    return filename

router = APIRouter()


def _item_to_response(item: Item) -> ItemResponse:
    """Convert Item model to response schema."""
    return ItemResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        category_id=item.category_id,
        content_type=item.content_type,
        file_path=item.file_path,
        original_path=item.original_path,
        url=item.url,
        extracted_text=item.extracted_text,
        file_hash=item.file_hash,
        file_size=item.file_size,
        mime_type=item.mime_type,
        thumbnail_path=item.thumbnail_path,
        confidence=item.confidence,
        item_metadata=item.item_metadata,
        created_at=item.created_at,
        updated_at=item.updated_at,
        category_name=item.category.name if item.category else None,
        tags=[tag.name for tag in item.tags] if item.tags else [],
    )


@router.post("/file", response_model=ItemResponse)
async def import_file(
    file: UploadFile = File(...),
    category_id: Optional[int] = Form(None),
    auto_classify: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    """Import a single file via upload."""
    settings = get_settings()
    storage = StorageService()
    processor = FileProcessor()
    classifier = Classifier()

    # Decode filename to handle URL-encoded or other encoded filenames
    original_filename = decode_filename(file.filename)

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > settings.storage.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.storage.max_file_size} bytes"
        )

    # Check for duplicates
    file_hash = storage.calculate_hash(content)
    existing = await db.execute(
        select(Item).where(Item.file_hash == file_hash)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="File already exists in vault")

    # Save file
    relative_path, _ = await storage.save_file(content, original_filename, file_hash)

    # Process file for metadata and text extraction
    temp_path = settings.files_path / relative_path
    file_data = await processor.process_file(temp_path)

    # Auto-classify if enabled and no category provided
    confidence = None
    if auto_classify and not category_id:
        text_for_classification = file_data.get('extracted_text', '') or original_filename
        category_id, confidence = await classifier.classify(
            text_for_classification,
            file_path=Path(original_filename),
            session=db,
        )

    # Save thumbnail if generated
    thumbnail_path = None
    if file_data.get('thumbnail_data'):
        # Will save after we have item ID
        pass

    # Create item - use original filename as title instead of hash-based filename
    item = Item(
        title=original_filename,
        content_type="file",
        file_path=relative_path,
        original_path=original_filename,
        extracted_text=file_data.get('extracted_text'),
        file_hash=file_hash,
        file_size=len(content),
        mime_type=file_data.get('mime_type'),
        category_id=category_id,
        confidence=confidence,
        item_metadata=file_data.get('metadata'),
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)

    # Save thumbnail with item ID
    if file_data.get('thumbnail_data'):
        thumbnail_path = await storage.save_thumbnail(
            file_data['thumbnail_data'],
            item.id,
        )
        item.thumbnail_path = thumbnail_path
        await db.commit()

    # Reload with relationships
    query = (
        select(Item)
        .where(Item.id == item.id)
        .options(selectinload(Item.category), selectinload(Item.tags))
    )
    result = await db.execute(query)
    item = result.scalar_one()

    return _item_to_response(item)


@router.post("/url", response_model=ItemResponse)
async def import_url(
    url: str,
    category_id: Optional[str] = None,
    auto_classify: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Import content from a URL."""
    # Convert category_id from string to int, handling empty strings
    category_id_int: Optional[int] = None
    if category_id and category_id.strip():
        try:
            category_id_int = int(category_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="category_id must be a valid integer")

    scraper = WebScraper()
    classifier = Classifier()

    try:
        # Scrape URL
        page_data = await scraper.scrape_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    finally:
        await scraper.close()

    # Check for duplicates
    existing = await db.execute(
        select(Item).where(Item.url == page_data['url'])
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="URL already exists in vault")

    # Auto-classify if enabled
    confidence = None
    if auto_classify and not category_id_int:
        text_for_classification = (
            f"{page_data['title']} {page_data.get('description', '')} "
            f"{page_data.get('extracted_text', '')[:2000]}"
        )
        category_id_int, confidence = await classifier.classify(
            text_for_classification,
            session=db,
        )

    # Create item
    item = Item(
        title=page_data['title'],
        content_type="url",
        url=page_data['url'],
        description=page_data.get('description'),
        extracted_text=page_data.get('extracted_text'),
        category_id=category_id_int,
        confidence=confidence,
        item_metadata=page_data.get('metadata'),
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)

    # Reload with relationships
    query = (
        select(Item)
        .where(Item.id == item.id)
        .options(selectinload(Item.category), selectinload(Item.tags))
    )
    result = await db.execute(query)
    item = result.scalar_one()

    return _item_to_response(item)


@router.post("/path", response_model=ItemImportResponse)
async def import_from_path(
    request: ItemImportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import files from a local path (file or directory)."""
    if not request.path:
        raise HTTPException(status_code=400, detail="Path is required")

    source_path = Path(request.path).expanduser().resolve()

    if not source_path.exists():
        raise HTTPException(status_code=400, detail=f"Path not found: {source_path}")

    storage = StorageService()
    processor = FileProcessor()
    classifier = Classifier()
    settings = get_settings()

    imported_items = []
    skipped = 0
    errors = []

    # Get list of files to import
    if source_path.is_file():
        files_to_import = [source_path]
    else:
        # Recursively get all files
        files_to_import = [
            f for f in source_path.rglob("*")
            if f.is_file() and processor.is_supported_file(f)
        ]

    for file_path in files_to_import:
        try:
            # Check file size
            if file_path.stat().st_size > settings.storage.max_file_size:
                errors.append(f"File too large: {file_path.name}")
                skipped += 1
                continue

            # Save file and get hash
            relative_path, file_hash, file_size = await storage.save_file_from_path(file_path)

            # Check for duplicates
            existing = await db.execute(
                select(Item).where(Item.file_hash == file_hash)
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            # Process file
            stored_path = settings.files_path / relative_path
            file_data = await processor.process_file(stored_path)

            # Classify
            category_id = request.category_id
            confidence = None

            if request.auto_classify and not category_id:
                text_for_classification = file_data.get('extracted_text', '') or file_path.name
                category_id, confidence = await classifier.classify(
                    text_for_classification,
                    file_path=file_path,
                    session=db,
                )

            # Create item
            item = Item(
                title=file_data['title'],
                content_type="file",
                file_path=relative_path,
                original_path=str(file_path),
                extracted_text=file_data.get('extracted_text'),
                file_hash=file_hash,
                file_size=file_size,
                mime_type=file_data.get('mime_type'),
                category_id=category_id,
                confidence=confidence,
                item_metadata=file_data.get('metadata'),
            )

            db.add(item)
            await db.flush()  # Get item ID

            # Save thumbnail
            if file_data.get('thumbnail_data'):
                thumbnail_path = await storage.save_thumbnail(
                    file_data['thumbnail_data'],
                    item.id,
                )
                item.thumbnail_path = thumbnail_path

            imported_items.append(item)

        except Exception as e:
            errors.append(f"Error importing {file_path.name}: {str(e)}")
            skipped += 1

    await db.commit()

    # Reload items with relationships
    item_responses = []
    for item in imported_items:
        query = (
            select(Item)
            .where(Item.id == item.id)
            .options(selectinload(Item.category), selectinload(Item.tags))
        )
        result = await db.execute(query)
        loaded_item = result.scalar_one()
        item_responses.append(_item_to_response(loaded_item))

    return ItemImportResponse(
        success=len(errors) == 0,
        items_imported=len(imported_items),
        items_skipped=skipped,
        errors=errors,
        items=item_responses,
    )


@router.post("/{item_id}/reclassify", response_model=ItemResponse)
async def reclassify_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Re-classify an existing item."""
    query = (
        select(Item)
        .where(Item.id == item_id)
        .options(selectinload(Item.category), selectinload(Item.tags))
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    classifier = Classifier()

    # Build text for classification
    text_parts = [item.title]
    if item.description:
        text_parts.append(item.description)
    if item.extracted_text:
        text_parts.append(item.extracted_text[:2000])

    text_for_classification = ' '.join(text_parts)

    # Get file path hint if available
    file_path = Path(item.original_path) if item.original_path else None

    # Classify
    category_id, confidence = await classifier.classify(
        text_for_classification,
        file_path=file_path,
        session=db,
    )

    item.category_id = category_id
    item.confidence = confidence

    await db.commit()
    await db.refresh(item)

    return _item_to_response(item)
