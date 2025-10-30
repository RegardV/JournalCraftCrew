"""
Project API Tests
Phase 3.5: API Testing Suite
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


@pytest.mark.asyncio
class TestProjectAPI:
    """Test project API endpoints"""

    async def test_create_project_success(self, authenticated_client: AsyncClient, sample_project_data: dict):
        """Test successful project creation"""
        response = await authenticated_client.post("/api/projects/", json=sample_project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "Project created successfully"
        assert data["project"]["title"] == sample_project_data["title"]
        assert data["project"]["type"] == sample_project_data["type"]
        assert "id" in data["project"]

    async def test_create_project_unauthorized(self, client: AsyncClient, sample_project_data: dict):
        """Test project creation without authentication"""
        response = await client.post("/api/projects/", json=sample_project_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_project_invalid_data(self, authenticated_client: AsyncClient):
        """Test project creation with invalid data"""
        invalid_data = {"title": "", "type": "invalid_type"}
        response = await authenticated_client.post("/api/projects/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_projects_success(self, authenticated_client: AsyncClient, test_project):
        """Test successful projects retrieval"""
        response = await authenticated_client.get("/api/projects/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "projects" in data
        assert "pagination" in data
        assert len(data["projects"]) >= 1
        assert data["projects"][0]["title"] == test_project.title

    async def test_get_projects_with_pagination(self, authenticated_client: AsyncClient, test_project):
        """Test projects retrieval with pagination"""
        response = await authenticated_client.get("/api/projects/?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["skip"] == 0
        assert data["pagination"]["limit"] == 10

    async def test_get_projects_with_search(self, authenticated_client: AsyncClient, test_project):
        """Test projects retrieval with search"""
        response = await authenticated_client.get(f"/api/projects/?search={test_project.title}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["projects"]) >= 1
        assert test_project.title in data["projects"][0]["title"]

    async def test_get_project_success(self, authenticated_client: AsyncClient, test_project):
        """Test successful single project retrieval"""
        response = await authenticated_client.get(f"/api/projects/{test_project.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project"]["id"] == test_project.id
        assert data["project"]["title"] == test_project.title

    async def test_get_project_not_found(self, authenticated_client: AsyncClient):
        """Test project retrieval with non-existent ID"""
        response = await authenticated_client.get("/api/projects/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_project_unauthorized(self, client: AsyncClient, test_project):
        """Test project retrieval without authentication"""
        response = await client.get(f"/api/projects/{test_project.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_project_success(self, authenticated_client: AsyncClient, test_project):
        """Test successful project update"""
        update_data = {
            "title": "Updated Project Title",
            "description": "Updated description",
            "status": "in_progress"
        }
        response = await authenticated_client.put(f"/api/projects/{test_project.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project"]["title"] == update_data["title"]
        assert data["project"]["description"] == update_data["description"]
        assert data["project"]["status"] == update_data["status"]

    async def test_update_project_not_found(self, authenticated_client: AsyncClient):
        """Test project update with non-existent ID"""
        update_data = {"title": "Updated Title"}
        response = await authenticated_client.put("/api/projects/99999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_project_unauthorized(self, client: AsyncClient, test_project):
        """Test project update without authentication"""
        update_data = {"title": "Updated Title"}
        response = await client.put(f"/api/projects/{test_project.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_project_success(self, authenticated_client: AsyncClient, test_project):
        """Test successful project deletion"""
        response = await authenticated_client.delete(f"/api/projects/{test_project.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify project is deleted
        get_response = await authenticated_client.get(f"/api/projects/{test_project.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_project_not_found(self, authenticated_client: AsyncClient):
        """Test project deletion with non-existent ID"""
        response = await authenticated_client.delete("/api/projects/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_project_unauthorized(self, client: AsyncClient, test_project):
        """Test project deletion without authentication"""
        response = await client.delete(f"/api/projects/{test_project.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_duplicate_project_success(self, authenticated_client: AsyncClient, test_project):
        """Test successful project duplication"""
        response = await authenticated_client.post(f"/api/projects/{test_project.id}/duplicate")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["project"]["title"] == f"Copy of {test_project.title}"
        assert data["project"]["description"] == f"Copy of {test_project.title}"

    async def test_duplicate_project_not_found(self, authenticated_client: AsyncClient):
        """Test project duplication with non-existent ID"""
        response = await authenticated_client.post("/api/projects/99999/duplicate")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_project_statistics(self, authenticated_client: AsyncClient, test_project):
        """Test project statistics retrieval"""
        response = await authenticated_client.get("/api/projects/statistics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_projects" in data
        assert "status_breakdown" in data
        assert "total_word_count" in data
        assert "completion_rate" in data

    async def test_create_project_with_theme(self, authenticated_client: AsyncClient, test_project, mock_theme):
        """Test project creation with theme assignment"""
        project_data = {
            "title": "Project with Theme",
            "description": "Test project with theme",
            "type": "personal",
            "theme_id": mock_theme.id
        }
        response = await authenticated_client.post("/api/projects/", json=project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["project"]["theme_id"] == mock_theme.id

    async def test_update_project_theme(self, authenticated_client: AsyncClient, test_project, mock_theme):
        """Test updating project theme"""
        update_data = {"theme_id": mock_theme.id}
        response = await authenticated_client.put(f"/api/projects/{test_project.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project"]["theme_id"] == mock_theme.id

    async def test_project_word_count_calculation(self, authenticated_client: AsyncClient, test_project):
        """Test project word count calculation"""
        # Create project with content
        project_data = {
            "title": "Word Count Test",
            "description": "Testing word count",
            "type": "personal",
            "settings": {
                "format": "a5",
                "orientation": "portrait",
                "margins": "standard",
                "page_numbers": True,
                "table_of_contents": False
            }
        }
        response = await authenticated_client.post("/api/projects/", json=project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "word_count" in data["project"]
        assert isinstance(data["project"]["word_count"], int)

    @pytest.mark.parametrize("status_filter", ["draft", "in_progress", "completed", "archived"])
    async def test_get_projects_by_status(self, authenticated_client: AsyncClient, test_project, status_filter: str):
        """Test projects retrieval filtered by status"""
        # Update project status first
        update_data = {"status": status_filter}
        await authenticated_client.put(f"/api/projects/{test_project.id}", json=update_data)

        # Then filter by status
        response = await authenticated_client.get(f"/api/projects/?status_filter={status_filter}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for project in data["projects"]:
            assert project["status"] == status_filter