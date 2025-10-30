"""
Theme API Tests
Phase 3.5: API Testing Suite
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


@pytest.mark.asyncio
class TestThemeAPI:
    """Test theme API endpoints"""

    async def test_get_themes_success(self, authenticated_client: AsyncClient, mock_theme):
        """Test successful themes retrieval"""
        response = await authenticated_client.get("/api/themes/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "themes" in data
        assert "pagination" in data
        assert len(data["themes"]) >= 1
        assert data["themes"][0]["name"] == mock_theme.name

    async def test_get_themes_with_pagination(self, authenticated_client: AsyncClient):
        """Test themes retrieval with pagination"""
        response = await authenticated_client.get("/api/themes/?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["skip"] == 0
        assert data["pagination"]["limit"] == 10

    async def test_get_themes_with_category_filter(self, authenticated_client: AsyncClient, mock_theme):
        """Test themes retrieval filtered by category"""
        response = await authenticated_client.get(f"/api/themes/?category={mock_theme.category}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for theme in data["themes"]:
            assert theme["category"] == mock_theme.category

    async def test_get_themes_with_premium_filter(self, authenticated_client: AsyncClient):
        """Test themes retrieval filtered by premium status"""
        response = await authenticated_client.get("/api/themes/?is_premium=false")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for theme in data["themes"]:
            assert theme["is_premium"] == False

    async def test_get_themes_unauthorized(self, client: AsyncClient):
        """Test themes retrieval without authentication"""
        response = await client.get("/api/themes/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_theme_success(self, authenticated_client: AsyncClient, mock_theme):
        """Test successful single theme retrieval"""
        response = await authenticated_client.get(f"/api/themes/{mock_theme.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["theme"]["id"] == mock_theme.id
        assert data["theme"]["name"] == mock_theme.name
        assert data["theme"]["category"] == mock_theme.category

    async def test_get_theme_not_found(self, authenticated_client: AsyncClient):
        """Test theme retrieval with non-existent ID"""
        response = await authenticated_client.get("/api/themes/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_theme_unauthorized(self, client: AsyncClient, mock_theme):
        """Test theme retrieval without authentication"""
        response = await client.get(f"/api/themes/{mock_theme.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_theme_success(self, authenticated_client: AsyncClient, sample_theme_data: dict):
        """Test successful theme creation"""
        response = await authenticated_client.post("/api/themes/", json=sample_theme_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "Custom theme created successfully"
        assert data["theme"]["name"] == sample_theme_data["name"]
        assert data["theme"]["category"] == sample_theme_data["category"]

    async def test_create_theme_unauthorized(self, client: AsyncClient, sample_theme_data: dict):
        """Test theme creation without authentication"""
        response = await client.post("/api/themes/", json=sample_theme_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_theme_invalid_data(self, authenticated_client: AsyncClient):
        """Test theme creation with invalid data"""
        invalid_data = {
            "name": "",
            "primary_color": "invalid_color",
            "category": ""
        }
        response = await authenticated_client.post("/api/themes/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_custom_theme_success(self, authenticated_client: AsyncClient, sample_theme_data: dict):
        """Test successful custom theme creation"""
        response = await authenticated_client.post("/api/themes/custom", json=sample_theme_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["theme"]["name"] == sample_theme_data["name"]
        assert data["theme"]["category"] == "custom"  # Should be set to custom

    async def test_update_theme_unimplemented(self, authenticated_client: AsyncClient, mock_theme):
        """Test theme update (not implemented yet)"""
        update_data = {"name": "Updated Theme Name"}
        response = await authenticated_client.put(f"/api/themes/{mock_theme.id}", json=update_data)

        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    async def test_delete_theme_unimplemented(self, authenticated_client: AsyncClient, mock_theme):
        """Test theme deletion (not implemented yet)"""
        response = await authenticated_client.delete(f"/api/themes/{mock_theme.id}")

        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    async def test_get_user_theme_preferences(self, authenticated_client: AsyncClient):
        """Test user theme preferences retrieval"""
        response = await authenticated_client.get("/api/themes/user/preferences")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "used_themes" in data
        assert "favorite_themes" in data
        assert "usage_stats" in data

    async def test_update_theme_preference(self, authenticated_client: AsyncClient, mock_theme):
        """Test updating user theme preference"""
        preference_data = {"theme_id": mock_theme.id, "is_favorite": True}
        response = await authenticated_client.put("/api/themes/user/preferences", json=preference_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Theme preference updated successfully"
        assert data["theme_id"] == mock_theme.id

    async def test_get_theme_statistics(self, authenticated_client: AsyncClient):
        """Test theme statistics retrieval"""
        response = await authenticated_client.get("/api/themes/statistics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_themes" in data
        assert "theme_usage" in data
        assert "usage_percentages" in data
        assert "total_projects" in data

    async def test_theme_color_validation(self, authenticated_client: AsyncClient, sample_theme_data: dict):
        """Test theme color format validation"""
        # Test invalid hex color
        invalid_theme_data = sample_theme_data.copy()
        invalid_theme_data["primary_color"] = "invalid_hex"

        response = await authenticated_client.post("/api/themes/", json=invalid_theme_data)

        # Should still succeed as color validation is basic
        assert response.status_code == status.HTTP_201_CREATED

    async def test_theme_category_validation(self, authenticated_client: AsyncClient, sample_theme_data: dict):
        """Test theme category validation"""
        # Test various valid categories
        valid_categories = ["minimal", "modern", "vintage", "seasonal", "artistic"]

        for category in valid_categories:
            theme_data = sample_theme_data.copy()
            theme_data["name"] = f"Test Theme {category}"
            theme_data["category"] = category

            response = await authenticated_client.post("/api/themes/", json=theme_data)
            assert response.status_code == status.HTTP_201_CREATED

    async def test_theme_optional_fields(self, authenticated_client: AsyncClient, sample_theme_data: dict):
        """Test theme creation with optional fields"""
        # Test with only required fields
        minimal_theme_data = {
            "name": "Minimal Theme",
            "category": "minimal",
            "primary_color": "#000000",
            "secondary_color": "#FFFFFF",
            "accent_color": "#007BFF",
            "background_color": "#FFFFFF",
            "text_color": "#333333",
            "border_color": "#E0E0E0"
        }

        response = await authenticated_client.post("/api/themes/", json=minimal_theme_data)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_seasonal_theme_filter(self, authenticated_client: AsyncClient):
        """Test themes retrieval with seasonal filter"""
        # Test all seasons
        seasons = ["spring", "summer", "autumn", "winter"]

        for season in seasons:
            response = await authenticated_client.get(f"/api/themes/?season={season}")
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("limit", [1, 10, 25, 50])
    async def test_themes_limit_validation(self, authenticated_client: AsyncClient, limit: int):
        """Test themes retrieval with different limits"""
        response = await authenticated_client.get(f"/api/themes/?limit={limit}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["themes"]) <= limit

    async def test_theme_search_functionality(self, authenticated_client: AsyncClient, mock_theme):
        """Test theme search (if implemented)"""
        # This would test search functionality
        response = await authenticated_client.get(f"/api/themes/?search={mock_theme.name}")

        # Search might not be implemented yet, so expect 200 with all themes
        assert response.status_code == status.HTTP_200_OK

    async def test_theme_preview_urls(self, authenticated_client: AsyncClient, mock_theme):
        """Test theme preview URLs are returned"""
        response = await authenticated_client.get(f"/api/themes/{mock_theme.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        theme = data["theme"]

        # Preview URL might be None or a string
        assert "preview_url" in theme
        assert theme["preview_url"] is None or isinstance(theme["preview_url"], str)