"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text

from .config import get_settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database, creating all tables."""
    from . import models  # Import models to register them

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Create FTS5 virtual table for full-text search
        await conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
                title, description, extracted_text,
                content='items',
                content_rowid='id'
            )
        """))


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
