"""Database session management for AI agent"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker] = None


def get_database_url() -> str:
    """Convert PostgreSQL URL to async format"""
    url = str(settings.DATABASE_URL)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_db() -> None:
    """Initialize database engine"""
    global _engine, _async_session_factory
    
    database_url = get_database_url()
    
    _engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
    )
    
    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    logger.info("ai_database_initialized", url=database_url)


async def close_db() -> None:
    """Close database connections"""
    global _engine
    
    if _engine:
        await _engine.dispose()
        logger.info("ai_database_closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized")
    
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
