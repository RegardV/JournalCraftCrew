"""
Database Integration Tests
Phase 3.1: Database Integration with PostgreSQL
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import db_manager
from app.models.user import User
from app.models.theme import Theme
from app.models.project import Project
from app.models.export import ExportRecord
from datetime import datetime


class TestDatabaseHealth:
    """Test database health and connectivity"""

    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check functionality"""
        health = await db_manager.health_check()
        assert health["status"] == "healthy"
        assert health["database"] == "postgresql"
        assert health["async_driver"] == "asyncpg"

    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """Test basic database connection"""
        result = await db_session.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        assert row[0] == 1


class TestUserModel:
    """Test User model functionality"""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user"""
        user = User(
            email="newuser@example.com",
            hashed_password="hashed_password",
            full_name="New User",
            is_active=True,
            is_verified=False,
            subscription="free",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.subscription == "free"

    @pytest.mark.asyncio
    async def test_user_query(self, db_session: AsyncSession, mock_user):
        """Test querying user from database"""
        result = await db_session.get(User, mock_user.id)
        assert result is not None
        assert result.email == mock_user.email
        assert result.full_name == mock_user.full_name


class TestThemeModel:
    """Test Theme model functionality"""

    @pytest.mark.asyncio
    async def test_create_theme(self, db_session: AsyncSession):
        """Test creating a theme"""
        theme = Theme(
            name="New Theme",
            description="A new test theme",
            category="vintage",
            is_premium=True,
            primary_color="#8B4513",
            secondary_color="#D2691E",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(theme)
        await db_session.commit()
        await db_session.refresh(theme)

        assert theme.id is not None
        assert theme.name == "New Theme"
        assert theme.is_premium is True

    @pytest.mark.asyncio
    async def test_theme_query(self, db_session: AsyncSession, mock_theme):
        """Test querying theme from database"""
        result = await db_session.get(Theme, mock_theme.id)
        assert result is not None
        assert result.name == mock_theme.name
        assert result.category == mock_theme.category


class TestProjectModel:
    """Test Project model functionality"""

    @pytest.mark.asyncio
    async def test_create_project(self, db_session: AsyncSession, mock_user, mock_theme):
        """Test creating a project"""
        project = Project(
            title="Test Project",
            description="A test journal project",
            type="journal",
            status="draft",
            user_id=mock_user.id,
            theme_id=mock_theme.id,
            content={"pages": []},
            settings={"format": "a5", "orientation": "portrait"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        assert project.id is not None
        assert project.title == "Test Project"
        assert project.user_id == mock_user.id
        assert project.theme_id == mock_theme.id

    @pytest.mark.asyncio
    async def test_project_user_relationship(self, db_session: AsyncSession, mock_user, mock_theme):
        """Test project-user relationship"""
        project = Project(
            title="User Project",
            description="Project with user relationship",
            type="journal",
            status="draft",
            user_id=mock_user.id,
            theme_id=mock_theme.id,
            content={"pages": []},
            settings={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Test relationship loading
        await db_session.refresh(project, ["user"])
        assert project.user is not None
        assert project.user.id == mock_user.id


class TestExportModel:
    """Test ExportRecord model functionality"""

    @pytest.mark.asyncio
    async def test_create_export_record(self, db_session: AsyncSession, mock_user, mock_theme):
        """Test creating an export record"""
        # First create a project
        project = Project(
            title="Export Test Project",
            description="Project for export testing",
            type="journal",
            status="draft",
            user_id=mock_user.id,
            theme_id=mock_theme.id,
            content={},
            settings={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Now create export record
        export_record = ExportRecord(
            project_id=project.id,
            user_id=mock_user.id,
            format="pdf",
            status="processing",
            file_size=0,
            settings={"quality": 90, "include_images": True},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_session.add(export_record)
        await db_session.commit()
        await db_session.refresh(export_record)

        assert export_record.id is not None
        assert export_record.project_id == project.id
        assert export_record.format == "pdf"
        assert export_record.status == "processing"


class TestMigrationSystem:
    """Test migration functionality"""

    @pytest.mark.asyncio
    async def test_migration_table_creation(self, db_session: AsyncSession):
        """Test that migration table can be created"""
        from app.core.migrations import MigrationManager

        manager = MigrationManager()
        await manager.create_migration_table(db_session)

        # Check if table exists
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM migrations")
        )
        count = result.fetchone()[0]
        assert count >= 0  # Should not raise error

    @pytest.mark.asyncio
    async def test_migration_tracking(self, db_session: AsyncSession):
        """Test migration tracking functionality"""
        from app.core.migrations import MigrationManager

        manager = MigrationManager()
        await manager.create_migration_table(db_session)

        # Get applied migrations (should be empty initially)
        applied = await manager.get_applied_migrations(db_session)
        initial_count = len(applied)

        # Apply first migration
        first_migration = manager.migrations[0]
        await first_migration.up(db_session)

        # Record migration
        await db_session.execute(
            text("INSERT INTO migrations (version, description) VALUES (:version, :description)"),
            {"version": first_migration.version, "description": first_migration.description}
        )
        await db_session.commit()

        # Check applied migrations
        applied = await manager.get_applied_migrations(db_session)
        assert len(applied) == initial_count + 1
        assert first_migration.version in applied