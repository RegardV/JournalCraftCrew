"""
Pytest Configuration and Fixtures
Phase 3.5: Comprehensive API Testing Suite
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_async_session, Base
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from httpx import AsyncClient
from app.main import app

# Test database URL (using separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/journal_platform", "/journal_platform_test")

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database"""
    async with test_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def mock_user(db_session: AsyncSession):
    """Create a mock user for testing"""
    from app.models.user import User
    from datetime import datetime

    user = User(
        email="test@example.com",
        hashed_password="$2b$12$hashedpassword",  # Mock hash
        full_name="Test User",
        is_active=True,
        is_verified=True,
        subscription="free",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def mock_theme(db_session: AsyncSession):
    """Create a mock theme for testing"""
    from app.models.theme import Theme
    from datetime import datetime

    theme = Theme(
        name="Test Theme",
        description="A test theme",
        category="minimal",
        is_premium=False,
        primary_color="#000000",
        secondary_color="#ffffff",
        background_color="#ffffff",
        text_color="#333333",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(theme)
    await db_session.commit()
    await db_session.refresh(theme)

    return theme


# Override database dependency for testing
@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency for tests"""
    async def _override_get_db():
        async with db_session.begin():
            yield db_session

    return _override_get_db


@pytest.fixture
async def authenticated_client(db_session: AsyncSession, mock_user) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated test client"""

    def override_get_db():
        return db_session

    app.dependency_overrides[get_async_session] = override_get_db

    # Create access token
    access_token = create_access_token(data={"sub": mock_user.email})

    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.headers.update({"Authorization": f"Bearer {access_token}"})
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_project(db_session: AsyncSession, mock_user):
    """Create test project"""
    from app.models.project import Project
    from datetime import datetime

    project = Project(
        user_id=mock_user.id,
        title="Test Journal Project",
        description="A test journal for testing purposes",
        type="personal",
        status="draft",
        content={"pages": [{"title": "Entry 1", "content": "Test content"}]},
        settings={
            "format": "a5",
            "orientation": "portrait",
            "margins": "standard",
            "page_numbers": True,
            "table_of_contents": False
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return project


@pytest.fixture
async def test_export_job(db_session: AsyncSession, mock_user, test_project):
    """Create test export job"""
    from app.models.export import ExportJob
    from datetime import datetime

    export_job = ExportJob(
        user_id=mock_user.id,
        project_id=test_project.id,
        export_format="pdf",
        status="pending",
        progress=0,
        export_options={"include_toc": True, "include_page_numbers": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db_session.add(export_job)
    await db_session.commit()
    await db_session.refresh(export_job)

    return export_job


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "title": "My Test Journal",
        "description": "A journal entry for testing",
        "type": "personal",
        "settings": {
            "format": "a5",
            "orientation": "portrait",
            "margins": "standard",
            "page_numbers": True,
            "table_of_contents": False
        }
    }


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing"""
    return {
        "name": "Custom Test Theme",
        "description": "A custom theme created during testing",
        "category": "custom",
        "primary_color": "#FF5733",
        "secondary_color": "#FFFFFF",
        "accent_color": "#28A745",
        "background_color": "#F8F9FA",
        "text_color": "#212529",
        "border_color": "#DEE2E6"
    }


@pytest.fixture
def sample_export_data():
    """Sample export job data for testing"""
    return {
        "export_format": "pdf",
        "export_options": {
            "include_toc": True,
            "include_page_numbers": True,
            "font_size": 12,
            "margin_size": "standard"
        },
        "kdp_metadata": {
            "title": "My Journal Book",
            "author": "Test Author",
            "description": "A journal published as a book",
            "trim_size": "6x9",
            "generate_cover": False
        }
    }