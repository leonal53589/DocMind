"""FastAPI application entry point for KnowledgeVault."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routers import items_router, categories_router, import_router, search_router
from .services.init_data import init_default_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_settings()
    settings.ensure_directories()
    await init_db()
    await init_default_categories()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="KnowledgeVault",
    description="A local knowledge repository system for managing files, notes, and web content",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(items_router, prefix="/api/items", tags=["items"])
app.include_router(categories_router, prefix="/api/categories", tags=["categories"])
app.include_router(import_router, prefix="/api/import", tags=["import"])
app.include_router(search_router, prefix="/api/search", tags=["search"])


# Mount static files for serving stored content
settings = get_settings()
if settings.files_path.exists():
    app.mount("/files", StaticFiles(directory=str(settings.files_path)), name="files")
if settings.thumbnails_path.exists():
    app.mount("/thumbnails", StaticFiles(directory=str(settings.thumbnails_path)), name="thumbnails")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "KnowledgeVault",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/stats")
async def get_stats():
    """Get vault statistics."""
    from sqlalchemy import select, func
    from .database import async_session_maker
    from .models import Item, Category, Tag

    async with async_session_maker() as session:
        items_count = await session.scalar(select(func.count(Item.id)))
        categories_count = await session.scalar(select(func.count(Category.id)))
        tags_count = await session.scalar(select(func.count(Tag.id)))

        # Count by content type
        file_count = await session.scalar(
            select(func.count(Item.id)).where(Item.content_type == "file")
        )
        url_count = await session.scalar(
            select(func.count(Item.id)).where(Item.content_type == "url")
        )
        note_count = await session.scalar(
            select(func.count(Item.id)).where(Item.content_type == "note")
        )

        # Total storage size
        total_size = await session.scalar(
            select(func.sum(Item.file_size)).where(Item.file_size.isnot(None))
        ) or 0

    return {
        "total_items": items_count or 0,
        "total_categories": categories_count or 0,
        "total_tags": tags_count or 0,
        "items_by_type": {
            "file": file_count or 0,
            "url": url_count or 0,
            "note": note_count or 0,
        },
        "total_storage_bytes": total_size,
    }
