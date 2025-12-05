"""Pydantic schemas for Category API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    item_count: int = 0


class CategoryWithChildren(CategoryResponse):
    """Category response with nested children."""
    children: list["CategoryWithChildren"] = []


CategoryWithChildren.model_rebuild()
