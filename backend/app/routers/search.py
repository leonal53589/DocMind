"""Search API router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Item, Category
from ..schemas.item import ItemResponse, ItemListResponse

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


@router.get("/", response_model=ItemListResponse)
async def search_items(
    q: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search items using full-text search.

    Searches across title, description, and extracted_text fields.
    """
    # Build base query with search
    # Using LIKE for simple search (FTS5 would be better for large datasets)
    search_pattern = f"%{q}%"

    query = (
        select(Item)
        .where(
            or_(
                Item.title.ilike(search_pattern),
                Item.description.ilike(search_pattern),
                Item.extracted_text.ilike(search_pattern),
            )
        )
        .options(selectinload(Item.category), selectinload(Item.tags))
    )

    # Apply filters
    if category_id:
        query = query.where(Item.category_id == category_id)
    if content_type:
        query = query.where(Item.content_type == content_type)

    # Count total matching items
    count_query = (
        select(func.count(Item.id))
        .where(
            or_(
                Item.title.ilike(search_pattern),
                Item.description.ilike(search_pattern),
                Item.extracted_text.ilike(search_pattern),
            )
        )
    )
    if category_id:
        count_query = count_query.where(Item.category_id == category_id)
    if content_type:
        count_query = count_query.where(Item.content_type == content_type)

    total = await db.scalar(count_query)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Item.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return ItemListResponse(
        items=[_item_to_response(item) for item in items],
        total=total or 0,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0,
    )


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get search suggestions based on item titles."""
    search_pattern = f"%{q}%"

    query = (
        select(Item.title)
        .where(Item.title.ilike(search_pattern))
        .limit(limit)
    )

    result = await db.execute(query)
    titles = result.scalars().all()

    return {"suggestions": list(set(titles))}


@router.get("/by-category", response_model=dict)
async def get_items_grouped_by_category(
    limit_per_category: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get recent items grouped by category."""
    categories_result = await db.execute(select(Category))
    categories = categories_result.scalars().all()

    result = {}

    for category in categories:
        query = (
            select(Item)
            .where(Item.category_id == category.id)
            .options(selectinload(Item.category), selectinload(Item.tags))
            .order_by(Item.created_at.desc())
            .limit(limit_per_category)
        )

        items_result = await db.execute(query)
        items = items_result.scalars().all()

        result[category.name] = {
            "category_id": category.id,
            "color": category.color,
            "icon": category.icon,
            "items": [_item_to_response(item) for item in items],
        }

    # Also get uncategorized items
    uncategorized_query = (
        select(Item)
        .where(Item.category_id.is_(None))
        .options(selectinload(Item.category), selectinload(Item.tags))
        .order_by(Item.created_at.desc())
        .limit(limit_per_category)
    )

    uncategorized_result = await db.execute(uncategorized_query)
    uncategorized_items = uncategorized_result.scalars().all()

    if uncategorized_items:
        result["Uncategorized"] = {
            "category_id": None,
            "color": "#6B7280",
            "icon": "folder",
            "items": [_item_to_response(item) for item in uncategorized_items],
        }

    return result
