"""Pydantic schemas for Item API."""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, HttpUrl


class ItemBase(BaseModel):
    """Base item schema."""
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    content_type: str = "note"
    url: Optional[str] = None
    extracted_text: Optional[str] = None
    item_metadata: Optional[dict[str, Any]] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item."""
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    extracted_text: Optional[str] = None
    item_metadata: Optional[dict[str, Any]] = None
    is_favorite: Optional[bool] = None


class AssociatedItemBrief(BaseModel):
    """Brief info for associated items."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content_type: str
    thumbnail_path: Optional[str] = None


class ItemResponse(ItemBase):
    """Schema for item response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    file_path: Optional[str] = None
    original_path: Optional[str] = None
    url: Optional[str] = None
    extracted_text: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    thumbnail_path: Optional[str] = None
    confidence: Optional[float] = None
    item_metadata: Optional[dict[str, Any]] = None
    is_favorite: bool = False
    favorite_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Nested
    category_name: Optional[str] = None
    tags: list[str] = []
    associated_items: list[AssociatedItemBrief] = []


class ItemListResponse(BaseModel):
    """Schema for paginated item list."""
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ItemImportRequest(BaseModel):
    """Schema for importing items."""
    path: Optional[str] = None  # Local file/directory path
    url: Optional[str] = None   # Web URL to import
    category_id: Optional[int] = None
    auto_classify: bool = True


class ItemImportResponse(BaseModel):
    """Schema for import response."""
    success: bool
    items_imported: int
    items_skipped: int
    errors: list[str] = []
    items: list[ItemResponse] = []


class ItemAssociationRequest(BaseModel):
    """Schema for adding/removing item associations."""
    associated_item_id: int
