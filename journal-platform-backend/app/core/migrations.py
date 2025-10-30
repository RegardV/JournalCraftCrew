"""
Database Migrations
Phase 3.1: Database Integration with PostgreSQL
"""

import asyncio
from typing import List, Dict, Any
from sqlalchemy import text
from app.core.database import sync_engine, AsyncSessionLocal
from app.models import user, project, theme, export
import logging

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class"""

    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description

    async def up(self, db: AsyncSessionLocal) -> None:
        """Apply migration"""
        raise NotImplementedError

    async def down(self, db: AsyncSessionLocal) -> None:
        """Rollback migration"""
        raise NotImplementedError


class CreateInitialTables(Migration):
    """Create initial database tables"""

    def __init__(self):
        super().__init__("001", "Create initial database tables")

    async def up(self, db: AsyncSessionLocal) -> None:
        """Create all tables"""
        from app.core.database import Base
        from app.models import user, project, theme, export

        async with db.begin():
            await db.run_sync(Base.metadata.create_all)
        logger.info("Created all database tables")

    async def down(self, db: AsyncSessionLocal) -> None:
        """Drop all tables"""
        from app.core.database import Base

        async with db.begin():
            await db.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all database tables")


class SeedInitialData(Migration):
    """Seed initial data for development"""

    def __init__(self):
        super().__init__("002", "Seed initial development data")

    async def up(self, db: AsyncSessionLocal) -> None:
        """Seed initial data"""
        from app.models.user import User, UserSubscription
        from app.models.theme import Theme
        from datetime import datetime

        # Create sample themes
        themes_data = [
            {
                "name": "Classic Minimal",
                "description": "Clean and minimalist design",
                "category": "minimal",
                "is_premium": False,
                "primary_color": "#000000",
                "secondary_color": "#ffffff",
                "accent_color": "#666666",
                "background_color": "#ffffff",
                "text_color": "#333333",
                "border_color": "#e0e0e0",
                "is_seasonal": False,
            },
            {
                "name": "Vintage Leather",
                "description": "Classic leather-bound journal aesthetic",
                "category": "vintage",
                "is_premium": True,
                "primary_color": "#8B4513",
                "secondary_color": "#D2691E",
                "accent_color": "#CD853F",
                "background_color": "#FFF8DC",
                "text_color": "#2F4F4F",
                "border_color": "#8B4513",
                "is_seasonal": False,
            },
            {
                "name": "Spring Blossom",
                "description": "Fresh spring-inspired theme",
                "category": "seasonal",
                "is_premium": True,
                "primary_color": "#FFB6C1",
                "secondary_color": "#98FB98",
                "accent_color": "#87CEEB",
                "background_color": "#FFFAF0",
                "text_color": "#2F4F4F",
                "border_color": "#FFB6C1",
                "is_seasonal": True,
                "season": "spring",
            },
        ]

        for theme_data in themes_data:
            theme = Theme(
                **theme_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(theme)

        await db.commit()
        logger.info(f"Created {len(themes_data)} sample themes")

    async def down(self, db: AsyncSessionLocal) -> None:
        """Remove seeded data"""
        from app.models.theme import Theme

        result = await db.execute(
            text("DELETE FROM themes WHERE name IN (:names)"),
            {"names": ["Classic Minimal", "Vintage Leather", "Spring Blossom"]}
        )
        await db.commit()
        logger.info(f"Removed {result.rowcount} seeded themes")


class MigrationManager:
    """Database migration manager"""

    def __init__(self):
        self.migrations: List[Migration] = [
            CreateInitialTables(),
            SeedInitialData(),
        ]

    async def create_migration_table(self, db: AsyncSessionLocal) -> None:
        """Create migration tracking table"""
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                version VARCHAR(50) PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await db.commit()
        logger.info("Created migrations table")

    async def get_applied_migrations(self, db: AsyncSessionLocal) -> List[str]:
        """Get list of applied migration versions"""
        result = await db.execute(text("SELECT version FROM migrations ORDER BY version"))
        return [row[0] for row in result.fetchall()]

    async def apply_migrations(self, db: AsyncSessionLocal) -> None:
        """Apply all pending migrations"""
        await self.create_migration_table(db)
        applied = await self.get_applied_migrations(db)

        for migration in self.migrations:
            if migration.version not in applied:
                try:
                    logger.info(f"Applying migration {migration.version}: {migration.description}")
                    await migration.up(db)

                    # Record migration
                    await db.execute(
                        text("INSERT INTO migrations (version, description) VALUES (:version, :description)"),
                        {"version": migration.version, "description": migration.description}
                    )
                    await db.commit()
                    logger.info(f"Applied migration {migration.version}")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Failed to apply migration {migration.version}: {e}")
                    raise

    async def rollback_migration(self, db: AsyncSessionLocal, version: str) -> None:
        """Rollback a specific migration"""
        migration = next((m for m in self.migrations if m.version == version), None)
        if not migration:
            raise ValueError(f"Migration {version} not found")

        try:
            logger.info(f"Rolling back migration {version}: {migration.description}")
            await migration.down(db)

            # Remove migration record
            await db.execute(text("DELETE FROM migrations WHERE version = :version"), {"version": version})
            await db.commit()
            logger.info(f"Rolled back migration {version}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to rollback migration {version}: {e}")
            raise

    async def reset_database(self, db: AsyncSessionLocal) -> None:
        """Reset database by dropping and recreating all tables"""
        applied = await self.get_applied_migrations(db)

        # Rollback migrations in reverse order
        for version in reversed(applied):
            try:
                await self.rollback_migration(db, version)
            except Exception as e:
                logger.warning(f"Could not rollback migration {version}: {e}")

        # Apply all migrations
        await self.apply_migrations(db)


# Global migration manager
migration_manager = MigrationManager()


async def run_migrations() -> None:
    """Run database migrations"""
    async with AsyncSessionLocal() as db:
        await migration_manager.apply_migrations(db)


async def reset_database() -> None:
    """Reset database"""
    async with AsyncSessionLocal() as db:
        await migration_manager.reset_database(db)


if __name__ == "__main__":
    """CLI for migration management"""
    import argparse

    async def main():
        parser = argparse.ArgumentParser(description="Database migration manager")
        parser.add_argument("command", choices=["migrate", "reset"], help="Command to run")
        args = parser.parse_args()

        if args.command == "migrate":
            await run_migrations()
            print("Migrations completed successfully")
        elif args.command == "reset":
            await reset_database()
            print("Database reset completed successfully")

    asyncio.run(main())