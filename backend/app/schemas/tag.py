"""Pydantic schemas for Tag API."""

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    """Base tag schema."""
    name: str


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagResponse(TagBase):
    """Schema for tag response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_count: int = 0
