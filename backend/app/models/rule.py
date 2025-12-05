"""Classification rule model."""

from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ClassificationRule(Base):
    """Rule for automatic content classification."""

    __tablename__ = "classification_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # keyword, regex, file_type, path_pattern
    pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    category = relationship("Category")

    def __repr__(self) -> str:
        return f"<ClassificationRule(id={self.id}, type='{self.rule_type}', pattern='{self.pattern}')>"
