"""Item model for stored content."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import json

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .category import Category
    from .tag import Tag


# Junction table for many-to-many relationship between items (associations)
ItemAssociation = Table(
    "item_associations",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("associated_item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
)


class Item(Base):
    """Content item stored in the vault."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # file, url, note

    # File information
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    # Content
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File metadata
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Classification
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Favorites
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    favorite_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Flexible metadata as JSON
    item_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="items"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="item_tags", back_populates="items"
    )

    # Self-referential many-to-many for item associations
    associated_items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary=ItemAssociation,
        primaryjoin=id == ItemAssociation.c.item_id,
        secondaryjoin=id == ItemAssociation.c.associated_item_id,
        backref="associated_by",
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title='{self.title[:50]}...', type='{self.content_type}')>"

    @property
    def is_file(self) -> bool:
        return self.content_type == "file"

    @property
    def is_url(self) -> bool:
        return self.content_type == "url"

    @property
    def is_note(self) -> bool:
        return self.content_type == "note"
