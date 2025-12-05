"""Categories API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Category, Item
from ..schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren
)

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all categories with item counts."""
    # Get categories with item counts using a subquery
    item_count_subquery = (
        select(Item.category_id, func.count(Item.id).label('count'))
        .group_by(Item.category_id)
        .subquery()
    )

    query = (
        select(Category, item_count_subquery.c.count)
        .outerjoin(item_count_subquery, Category.id == item_count_subquery.c.category_id)
        .order_by(Category.name)
    )

    result = await db.execute(query)
    rows = result.all()

    categories = []
    for category, count in rows:
        cat_response = CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            color=category.color,
            icon=category.icon,
            created_at=category.created_at,
            item_count=count or 0,
        )
        categories.append(cat_response)

    return categories


@router.get("/tree", response_model=list[CategoryWithChildren])
async def get_category_tree(db: AsyncSession = Depends(get_db)):
    """Get categories as a tree structure."""
    query = select(Category).options(selectinload(Category.children))
    result = await db.execute(query)
    all_categories = result.scalars().all()

    # Build tree from root nodes
    root_categories = [c for c in all_categories if c.parent_id is None]

    def build_tree(category: Category) -> CategoryWithChildren:
        return CategoryWithChildren(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            color=category.color,
            icon=category.icon,
            created_at=category.created_at,
            children=[build_tree(child) for child in category.children],
        )

    return [build_tree(cat) for cat in root_categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single category by ID."""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Get item count
    count_query = select(func.count(Item.id)).where(Item.category_id == category_id)
    item_count = await db.scalar(count_query)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        color=category.color,
        icon=category.icon,
        created_at=category.created_at,
        item_count=item_count or 0,
    )


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new category."""
    # Check if name already exists
    existing = await db.execute(
        select(Category).where(Category.name == category_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Category name already exists")

    # Validate parent if provided
    if category_data.parent_id:
        parent = await db.execute(
            select(Category).where(Category.id == category_data.parent_id)
        )
        if not parent.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Parent category not found")

    category = Category(
        name=category_data.name,
        description=category_data.description,
        parent_id=category_data.parent_id,
        color=category_data.color,
        icon=category_data.icon,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        color=category.color,
        icon=category.icon,
        created_at=category.created_at,
        item_count=0,
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check name uniqueness if changing
    if category_data.name and category_data.name != category.name:
        existing = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Category name already exists")

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    # Get item count
    count_query = select(func.count(Item.id)).where(Item.category_id == category_id)
    item_count = await db.scalar(count_query)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        color=category.color,
        icon=category.icon,
        created_at=category.created_at,
        item_count=item_count or 0,
    )


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a category (items will be uncategorized)."""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Set items to uncategorized
    await db.execute(
        Item.__table__.update()
        .where(Item.category_id == category_id)
        .values(category_id=None)
    )

    # Delete category
    await db.delete(category)
    await db.commit()

    return {"message": "Category deleted"}
