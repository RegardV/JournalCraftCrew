"""
Database Session Management
Phase 3.1: Database Integration with PostgreSQL
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import asyncio
from typing import AsyncGenerator

from app.core.config import settings

# Create async engine for database operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)

# Create sync engine for migrations and admin tasks
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# Create sync session factory for migrations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Create declarative base for models
Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session for migrations and admin tasks"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import user, project, theme, export

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    await async_engine.dispose()


class DatabaseManager:
    """Database connection manager for lifecycle management"""

    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal

    async def create_tables(self):
        """Create database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all tables (for testing only)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        """Get database session"""
        return self.session_factory()

    async def health_check(self) -> dict:
        """Check database health"""
        try:
            async with self.get_session() as session:
                # Simple health check query
                await session.execute("SELECT 1")
                return {
                    "status": "healthy",
                    "database": "postgresql",
                    "async_driver": "asyncpg"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "postgresql",
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()