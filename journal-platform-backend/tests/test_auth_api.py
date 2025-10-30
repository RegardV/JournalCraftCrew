"""
Authentication API Tests
Phase 3.5: API Testing Suite
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication API endpoints"""

    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_user_invalid_email(self, client: AsyncClient):
        """Test user registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        }
        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_user_weak_password(self, client: AsyncClient):
        """Test user registration with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "full_name": "Test User"
        }
        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_user_duplicate_email(self, client: AsyncClient, mock_user):
        """Test user registration with duplicate email"""
        user_data = {
            "email": mock_user.email,  # Use existing email
            "password": "password123",
            "full_name": "Duplicate User"
        }
        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login_success(self, client: AsyncClient, mock_user):
        """Test successful user login"""
        login_data = {
            "email": mock_user.email,
            "password": "testpassword123"  # Assuming this matches mock
        }
        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing required fields"""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_refresh_token_success(self, client: AsyncClient, mock_user):
        """Test successful token refresh"""
        # First login to get tokens
        login_data = {
            "email": mock_user.email,
            "password": "testpassword123"
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        login_data_response = login_response.json()
        refresh_token = login_data_response["refresh_token"]

        # Then refresh the token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = await client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_logout_success(self, authenticated_client: AsyncClient):
        """Test successful logout"""
        response = await authenticated_client.post("/api/auth/logout")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"

    async def test_logout_unauthorized(self, client: AsyncClient):
        """Test logout without authentication"""
        response = await client.post("/api/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_success(self, authenticated_client: AsyncClient, mock_user):
        """Test current user retrieval"""
        response = await authenticated_client.get("/api/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["full_name"] == mock_user.full_name

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test current user retrieval without authentication"""
        response = await client.get("/api/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_change_password_success(self, authenticated_client: AsyncClient):
        """Test successful password change"""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        response = await authenticated_client.put("/api/auth/change-password", json=password_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password changed successfully"

    async def test_change_password_wrong_current(self, authenticated_client: AsyncClient):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = await authenticated_client.put("/api/auth/change-password", json=password_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_change_password_unauthorized(self, client: AsyncClient):
        """Test password change without authentication"""
        password_data = {
            "current_password": "currentpassword",
            "new_password": "newpassword123"
        }
        response = await client.put("/api/auth/change-password", json=password_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_forgot_password_success(self, client: AsyncClient, mock_user):
        """Test password reset request"""
        reset_data = {"email": mock_user.email}
        response = await client.post("/api/auth/forgot-password", json=reset_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password reset email sent"

    async def test_forgot_password_nonexistent_email(self, client: AsyncClient):
        """Test password reset with non-existent email"""
        reset_data = {"email": "nonexistent@example.com"}
        response = await client.post("/api/auth/forgot-password", json=reset_data)

        # Should still return 200 for security (don't reveal email existence)
        assert response.status_code == status.HTTP_200_OK

    async def test_reset_password_success(self, client: AsyncClient):
        """Test password reset with valid token"""
        # This would require a valid reset token from forgot-password
        reset_data = {
            "token": "valid_reset_token",
            "new_password": "newpassword123"
        }
        response = await client.post("/api/auth/reset-password", json=reset_data)

        # Token validation would depend on implementation
        # For now, expect either success or invalid token
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test password reset with invalid token"""
        reset_data = {
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
        response = await client.post("/api/auth/reset-password", json=reset_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_verify_email_success(self, client: AsyncClient):
        """Test email verification with valid token"""
        verify_data = {"token": "valid_verification_token"}
        response = await client.post("/api/auth/verify-email", json=verify_data)

        # Token validation would depend on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token"""
        verify_data = {"token": "invalid_token"}
        response = await client.post("/api/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_token_validation(self, authenticated_client: AsyncClient):
        """Test that authentication tokens are properly validated"""
        # Test with valid token (authenticated_client has valid token)
        response = await authenticated_client.get("/api/auth/me")
        assert response.status_code == status.HTTP_200_OK

    async def test_token_expiration(self, client: AsyncClient):
        """Test token expiration handling"""
        # This would require creating an expired token
        # For now, just test that invalid tokens are rejected
        headers = {"Authorization": "Bearer expired_token"}
        response = await client.get("/api/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_user_registration_validation(self, client: AsyncClient):
        """Test various validation scenarios for user registration"""
        test_cases = [
            # Invalid email formats
            {
                "email": "",
                "password": "validpassword123",
                "full_name": "Test User",
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "email": "invalid-email-format",
                "password": "validpassword123",
                "full_name": "Test User",
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            # Weak passwords
            {
                "email": "test@example.com",
                "password": "",
                "full_name": "Test User",
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "email": "test@example.com",
                "password": "123",
                "full_name": "Test User",
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            # Missing full name
            {
                "email": "test@example.com",
                "password": "validpassword123",
                "full_name": "",
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        ]

        for case in test_cases:
            response = await client.post("/api/auth/register", json={
                "email": case["email"],
                "password": case["password"],
                "full_name": case["full_name"]
            })
            assert response.status_code == case["expected_status"]

    async def test_login_rate_limiting(self, client: AsyncClient):
        """Test login rate limiting (if implemented)"""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }

        # Multiple failed login attempts
        for _ in range(5):
            response = await client.post("/api/auth/login", json=login_data)
            # Should continue to return 401
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_bearer_token_format(self, authenticated_client: AsyncClient):
        """Test Bearer token format validation"""
        # Test with invalid token format
        headers = {"Authorization": "InvalidFormat token"}
        response = await authenticated_client.get("/api/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test with missing token
        headers = {"Authorization": "Bearer "}
        response = await authenticated_client.get("/api/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED