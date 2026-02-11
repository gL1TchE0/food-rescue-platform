"""
Integration tests for routes/auth.py – login, register, /me, /ngo endpoints.
"""
import pytest


# ============= POST /api/auth/login =============


class TestLogin:
    """Tests for the login endpoint."""

    def test_login_success(self, client, sample_user):
        """Valid credentials should return 200 with access_token."""
        response = client.post(
            "/api/auth/login",
            json={"email": "testuser@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, sample_user):
        """Wrong password should return 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": "testuser@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Non-existent email should return 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "anything"},
        )
        assert response.status_code == 401


# ============= GET /api/auth/me =============


class TestGetMe:
    """Tests for the /me endpoint."""

    def test_get_me_authenticated(self, client, sample_user, auth_headers):
        """Authenticated request should return user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["role"] == "NGO"

    def test_get_me_unauthenticated(self, client):
        """Request without token should return 403."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401


# ============= GET /api/auth/ngo =============


class TestGetNGO:
    """Tests for the /ngo endpoint."""

    def test_get_ngo_details(self, client, sample_user, sample_ngo, auth_headers):
        """NGO user should be able to get their NGO details."""
        response = client.get("/api/auth/ngo", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test NGO"
        assert data["approval_status"] == "APPROVED"

    def test_get_ngo_non_ngo_user(self, client, donor_user, donor_auth_headers):
        """Non-NGO user should get 403."""
        response = client.get("/api/auth/ngo", headers=donor_auth_headers)
        assert response.status_code == 403
