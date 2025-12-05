"""Initialize default data."""

from sqlalchemy import select
from ..database import async_session_maker
from ..models import Category


DEFAULT_CATEGORIES = [
    {
        "name": "Mathematical Principles",
        "description": "Theorems, proofs, equations, formulas, and mathematical concepts",
        "color": "#3B82F6",  # Blue
        "icon": "calculator",
    },
    {
        "name": "Ideas & Concepts",
        "description": "Concepts, hypotheses, theories, and creative ideas",
        "color": "#8B5CF6",  # Purple
        "icon": "lightbulb",
    },
    {
        "name": "Program Implementation",
        "description": "Code, algorithms, implementations, and software projects",
        "color": "#10B981",  # Green
        "icon": "code",
    },
    {
        "name": "Affairs & Tasks",
        "description": "Tasks, meetings, schedules, deadlines, and administrative matters",
        "color": "#F59E0B",  # Amber
        "icon": "clipboard-list",
    },
]


async def init_default_categories():
    """Initialize default categories if they don't exist."""
    async with async_session_maker() as session:
        for cat_data in DEFAULT_CATEGORIES:
            # Check if category exists
            result = await session.execute(
                select(Category).where(Category.name == cat_data["name"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                category = Category(**cat_data)
                session.add(category)

        await session.commit()
