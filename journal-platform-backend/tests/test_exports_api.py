"""
Export API Tests
Phase 3.5: API Testing Suite
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


@pytest.mark.asyncio
class TestExportAPI:
    """Test export API endpoints"""

    async def test_create_export_job_success(self, authenticated_client: AsyncClient, test_project, sample_export_data: dict):
        """Test successful export job creation"""
        export_data = {
            "project_id": test_project.id,
            **sample_export_data
        }
        response = await authenticated_client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "Export job created successfully"
        assert data["export_job"]["project_id"] == test_project.id
        assert data["export_job"]["export_format"] == export_data["export_format"]
        assert "id" in data["export_job"]
        assert "estimated_completion" in data["export_job"]

    async def test_create_export_job_unauthorized(self, client: AsyncClient, test_project, sample_export_data: dict):
        """Test export job creation without authentication"""
        export_data = {"project_id": test_project.id, **sample_export_data}
        response = await client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_export_job_invalid_project(self, authenticated_client: AsyncClient, sample_export_data: dict):
        """Test export job creation with non-existent project"""
        export_data = {"project_id": 99999, **sample_export_data}
        response = await authenticated_client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_export_job_invalid_format(self, authenticated_client: AsyncClient, test_project):
        """Test export job creation with invalid format"""
        export_data = {
            "project_id": test_project.id,
            "export_format": "invalid_format",
            "export_options": {}
        }
        response = await authenticated_client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_export_job_duplicate(self, authenticated_client: AsyncClient, test_project, sample_export_data: dict):
        """Test export job creation duplication prevention"""
        export_data = {"project_id": test_project.id, **sample_export_data}

        # Create first job
        response1 = await authenticated_client.post("/api/exports/jobs", json=export_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate job
        response2 = await authenticated_client.post("/api/exports/jobs", json=export_data)
        assert response2.status_code == status.HTTP_409_CONFLICT

    async def test_get_export_jobs_success(self, authenticated_client: AsyncClient, test_export_job):
        """Test successful export jobs retrieval"""
        response = await authenticated_client.get("/api/exports/jobs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "export_jobs" in data
        assert "pagination" in data
        assert len(data["export_jobs"]) >= 1

    async def test_get_export_jobs_with_project_filter(self, authenticated_client: AsyncClient, test_export_job):
        """Test export jobs retrieval filtered by project"""
        response = await authenticated_client.get(f"/api/exports/jobs?project_id={test_export_job.project_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for job in data["export_jobs"]:
            assert job["project_id"] == test_export_job.project_id

    async def test_get_export_jobs_with_status_filter(self, authenticated_client: AsyncClient, test_export_job):
        """Test export jobs retrieval filtered by status"""
        response = await authenticated_client.get(f"/api/exports/jobs?status_filter={test_export_job.status}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for job in data["export_jobs"]:
            assert job["status"] == test_export_job.status

    async def test_get_export_jobs_unauthorized(self, client: AsyncClient):
        """Test export jobs retrieval without authentication"""
        response = await client.get("/api/exports/jobs")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_export_job_success(self, authenticated_client: AsyncClient, test_export_job):
        """Test successful single export job retrieval"""
        response = await authenticated_client.get(f"/api/exports/jobs/{test_export_job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["export_job"]["id"] == test_export_job.id
        assert data["export_job"]["project_id"] == test_export_job.project_id
        assert data["export_job"]["export_format"] == test_export_job.export_format

    async def test_get_export_job_not_found(self, authenticated_client: AsyncClient):
        """Test export job retrieval with non-existent ID"""
        response = await authenticated_client.get("/api/exports/jobs/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_export_job_unauthorized(self, client: AsyncClient, test_export_job):
        """Test export job retrieval without authentication"""
        response = await client.get(f"/api/exports/jobs/{test_export_job.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_cancel_export_job_success(self, authenticated_client: AsyncClient, test_export_job):
        """Test successful export job cancellation"""
        response = await authenticated_client.put(f"/api/exports/jobs/{test_export_job.id}/cancel")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Export job cancelled successfully"

    async def test_cancel_export_job_not_found(self, authenticated_client: AsyncClient):
        """Test export job cancellation with non-existent ID"""
        response = await authenticated_client.put("/api/exports/jobs/99999/cancel")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_cancel_export_job_unauthorized(self, client: AsyncClient, test_export_job):
        """Test export job cancellation without authentication"""
        response = await client.put(f"/api/exports/jobs/{test_export_job.id}/cancel")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_supported_formats_success(self, authenticated_client: AsyncClient):
        """Test supported formats retrieval"""
        response = await authenticated_client.get("/api/exports/formats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "supported_formats" in data
        assert "pdf" in data["supported_formats"]
        assert "epub" in data["supported_formats"]
        assert "kdp" in data["supported_formats"]

        # Check PDF format details
        pdf_format = data["supported_formats"]["pdf"]
        assert "name" in pdf_format
        assert "description" in pdf_format
        assert "options" in pdf_format
        assert "estimated_time" in pdf_format

    async def test_get_supported_formats_unauthorized(self, client: AsyncClient):
        """Test supported formats retrieval without authentication"""
        response = await client.get("/api/exports/formats")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_preview_kdp_export_success(self, authenticated_client: AsyncClient, test_project):
        """Test KDP export preview"""
        kdp_metadata = {
            "title": "Test KDP Book",
            "author": "Test Author",
            "description": "A test book for KDP",
            "trim_size": "6x9",
            "page_color": "white",
            "categories": ["Biography & Autobiography"],
            "keywords": ["journal", "memoir", "life"]
        }
        response = await authenticated_client.post(f"/api/exports/kdp/preview?project_id={test_project.id}", json=kdp_metadata)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "KDP metadata validated successfully"
        assert data["metadata"]["title"] == kdp_metadata["title"]
        assert data["metadata"]["author"] == kdp_metadata["author"]
        assert "validation_status" in data
        assert "estimated_pages" in data

    async def test_preview_kdp_export_invalid_project(self, authenticated_client: AsyncClient):
        """Test KDP export preview with non-existent project"""
        kdp_metadata = {"title": "Test", "author": "Test", "description": "Test"}
        response = await authenticated_client.post("/api/exports/kdp/preview?project_id=99999", json=kdp_metadata)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_export_statistics_success(self, authenticated_client: AsyncClient, test_export_job):
        """Test export statistics retrieval"""
        response = await authenticated_client.get("/api/exports/statistics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_exports" in data
        assert "format_breakdown" in data
        assert "status_breakdown" in data
        assert "success_rate" in data
        assert "most_used_format" in data

    async def test_get_export_statistics_unauthorized(self, client: AsyncClient):
        """Test export statistics retrieval without authentication"""
        response = await client.get("/api/exports/statistics")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_export_templates_success(self, authenticated_client: AsyncClient):
        """Test export templates retrieval"""
        response = await authenticated_client.get("/api/exports/templates")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "export_templates" in data

        # Check for PDF templates
        assert "pdf" in data["export_templates"]
        pdf_templates = data["export_templates"]["pdf"]
        assert "novel" in pdf_templates
        assert "journal" in pdf_templates
        assert "cookbook" in pdf_templates

        # Check template structure
        novel_template = pdf_templates["novel"]
        assert "name" in novel_template
        assert "description" in novel_template
        assert "options" in novel_template

    async def test_get_export_templates_unauthorized(self, client: AsyncClient):
        """Test export templates retrieval without authentication"""
        response = await client.get("/api/exports/templates")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_export_job_unimplemented(self, authenticated_client: AsyncClient, test_export_job):
        """Test export job deletion (not implemented yet)"""
        response = await authenticated_client.delete(f"/api/exports/jobs/{test_export_job.id}")

        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    @pytest.mark.parametrize("export_format", ["pdf", "epub", "kdp"])
    async def test_create_export_job_all_formats(self, authenticated_client: AsyncClient, test_project, export_format: str):
        """Test export job creation for all supported formats"""
        export_data = {
            "project_id": test_project.id,
            "export_format": export_format,
            "export_options": {"include_toc": True, "include_page_numbers": True}
        }
        response = await authenticated_client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["export_job"]["export_format"] == export_format

    async def test_export_job_with_kdp_metadata(self, authenticated_client: AsyncClient, test_project):
        """Test export job creation with KDP metadata"""
        export_data = {
            "project_id": test_project.id,
            "export_format": "kdp",
            "export_options": {"include_toc": True},
            "kdp_metadata": {
                "title": "My KDP Book",
                "author": "Test Author",
                "description": "Test description",
                "trim_size": "6x9",
                "generate_cover": False
            }
        }
        response = await authenticated_client.post("/api/exports/jobs", json=export_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["export_job"]["export_format"] == "kdp"

    async def test_export_job_progress_tracking(self, authenticated_client: AsyncClient, test_export_job):
        """Test export job progress tracking"""
        response = await authenticated_client.get(f"/api/exports/jobs/{test_export_job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        export_job = data["export_job"]
        assert "progress" in export_job
        assert isinstance(export_job["progress"], int)
        assert 0 <= export_job["progress"] <= 100

    async def test_export_job_pagination(self, authenticated_client: AsyncClient):
        """Test export jobs pagination"""
        response = await authenticated_client.get("/api/exports/jobs?skip=0&limit=5")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["skip"] == 0
        assert data["pagination"]["limit"] == 5
        assert "has_more" in data["pagination"]
        assert "total" in data["pagination"]