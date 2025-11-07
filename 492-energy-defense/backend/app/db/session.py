"""
Database session management with async SQLAlchemy
Provides connection pooling and transaction management
"""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# SQLAlchemy Base for models
Base = declarative_base()

# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker] = None


def get_database_url() -> str:
    """Convert PostgreSQL URL to async format"""
    url = str(settings.DATABASE_URL)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_db() -> None:
    """Initialize database engine and session factory"""
    global _engine, _async_session_factory
    
    database_url = get_database_url()
    
    _engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    logger.info("database_engine_initialized", url=database_url)


async def close_db() -> None:
    """Close database connections"""
    global _engine
    
    if _engine:
        await _engine.dispose()
        logger.info("database_connections_closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session
    Automatically handles transaction commit/rollback
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine() -> AsyncEngine:
    """Get the database engine instance"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine
