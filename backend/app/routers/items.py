"""Items API router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Item, Category, Tag
from ..schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
)
from ..config import get_settings

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
        tags=[tag.name for tag in item.tags],
    )


@router.get("/", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    content_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all items with pagination and filtering."""
    query = select(Item).options(selectinload(Item.category), selectinload(Item.tags))

    # Apply filters
    if category_id:
        query = query.where(Item.category_id == category_id)
    if content_type:
        query = query.where(Item.content_type == content_type)

    # Count total
    count_query = select(func.count(Item.id))
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


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single item by ID."""
    query = (
        select(Item)
        .where(Item.id == item_id)
        .options(selectinload(Item.category), selectinload(Item.tags))
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return _item_to_response(item)


@router.post("/", response_model=ItemResponse)
async def create_item(item_data: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new item (note type)."""
    item = Item(
        title=item_data.title,
        description=item_data.description,
        content_type=item_data.content_type,
        category_id=item_data.category_id,
        url=item_data.url,
        extracted_text=item_data.extracted_text,
        item_metadata=item_data.item_metadata,
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


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an item."""
    query = (
        select(Item)
        .where(Item.id == item_id)
        .options(selectinload(Item.category), selectinload(Item.tags))
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)

    return _item_to_response(item)


@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item."""
    query = select(Item).where(Item.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()

    # TODO: Delete associated files from storage

    return {"message": "Item deleted"}


@router.post("/{item_id}/tags/{tag_name}")
async def add_tag_to_item(
    item_id: int,
    tag_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Add a tag to an item."""
    # Get item
    query = select(Item).where(Item.id == item_id).options(selectinload(Item.tags))
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Get or create tag
    tag_query = select(Tag).where(Tag.name == tag_name)
    tag_result = await db.execute(tag_query)
    tag = tag_result.scalar_one_or_none()

    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)

    # Add tag to item
    if tag not in item.tags:
        item.tags.append(tag)
        await db.commit()

    return {"message": f"Tag '{tag_name}' added to item"}


@router.delete("/{item_id}/tags/{tag_name}")
async def remove_tag_from_item(
    item_id: int,
    tag_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a tag from an item."""
    query = select(Item).where(Item.id == item_id).options(selectinload(Item.tags))
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Find and remove tag
    for tag in item.tags:
        if tag.name == tag_name:
            item.tags.remove(tag)
            await db.commit()
            return {"message": f"Tag '{tag_name}' removed from item"}

    raise HTTPException(status_code=404, detail="Tag not found on item")


class AISummaryResponse(BaseModel):
    """Response schema for AI summary."""
    summary: str
    recommended_category: Optional[str] = None
    recommended_category_id: Optional[int] = None
    confidence: Optional[float] = None


@router.post("/{item_id}/ai-summary", response_model=AISummaryResponse)
async def get_ai_summary(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI summary and category recommendation for an item.
    Supports both Ollama (local) and DeepSeek (cloud) API.
    """
    import httpx

    settings = get_settings()

    # Get item
    query = select(Item).where(Item.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Prepare content for AI
    content = ""
    if item.title:
        content += f"标题: {item.title}\n"
    if item.description:
        content += f"描述: {item.description}\n"
    if item.extracted_text:
        # Limit text to avoid token limits
        content += f"内容: {item.extracted_text[:3000]}\n"

    if not content.strip():
        raise HTTPException(status_code=400, detail="No content available for analysis")

    # Get all categories for recommendation
    cat_result = await db.execute(select(Category))
    categories = cat_result.scalars().all()
    category_names = [cat.name for cat in categories]
    category_map = {cat.name: cat.id for cat in categories}

    # Create prompt for summary and category recommendation
    prompt = f"""请分析以下内容，并完成两个任务：

1. 用中文写一个简洁的摘要（2-3句话）
2. 从以下分类中选择最合适的一个: {', '.join(category_names)}

内容:
{content}

请按以下格式回复：
摘要: [你的摘要]
推荐分类: [分类名称]"""

    try:
        async with httpx.AsyncClient() as client:
            ai_provider = settings.classification.ai_provider.lower()

            if ai_provider == "deepseek":
                # Use DeepSeek API
                api_key = settings.classification.deepseek_api_key
                if not api_key:
                    raise HTTPException(
                        status_code=503,
                        detail="DeepSeek API密钥未配置。请设置环境变量 DEEPSEEK_API_KEY"
                    )

                response = await client.post(
                    settings.classification.deepseek_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.classification.deepseek_model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                    timeout=60.0,
                )

                if response.status_code != 200:
                    error_detail = response.json().get("error", {}).get("message", response.text)
                    raise HTTPException(
                        status_code=503,
                        detail=f"DeepSeek API错误: {error_detail}"
                    )

                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()

            else:
                # Use Ollama (local)
                response = await client.post(
                    f"{settings.classification.ollama_url}/api/generate",
                    json={
                        "model": settings.classification.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60.0,
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Ollama服务不可用 (返回 {response.status_code})"
                    )

                result = response.json()
                ai_response = result.get("response", "").strip()

            # Parse response
            summary = ""
            recommended_category = None
            recommended_category_id = None

            lines = ai_response.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("摘要:") or line.startswith("摘要："):
                    summary = line.split(":", 1)[-1].split("：", 1)[-1].strip()
                elif line.startswith("推荐分类:") or line.startswith("推荐分类："):
                    recommended_category = line.split(":", 1)[-1].split("：", 1)[-1].strip()

            # If parsing failed, use the whole response as summary
            if not summary:
                summary = ai_response

            # Validate recommended category
            if recommended_category and recommended_category in category_map:
                recommended_category_id = category_map[recommended_category]
            elif recommended_category:
                # Try fuzzy match
                for cat_name in category_names:
                    if recommended_category.lower() in cat_name.lower() or cat_name.lower() in recommended_category.lower():
                        recommended_category = cat_name
                        recommended_category_id = category_map[cat_name]
                        break

            return AISummaryResponse(
                summary=summary,
                recommended_category=recommended_category,
                recommended_category_id=recommended_category_id,
                confidence=0.85 if recommended_category_id else None,
            )

    except httpx.ConnectError:
        provider = settings.classification.ai_provider
        if provider.lower() == "deepseek":
            raise HTTPException(
                status_code=503,
                detail="无法连接到DeepSeek API。请检查网络连接"
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="无法连接到Ollama服务。请确保Ollama正在运行 (ollama serve)"
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI服务响应超时，请稍后重试"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI分析失败: {str(e)}"
        )
