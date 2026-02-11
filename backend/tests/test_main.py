"""
Tests for main.py – root and health check endpoints.
"""
import pytest


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_returns_api_info(self, client):
        """Root endpoint should return API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Food Rescue Platform API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"


class TestHealthCheck:
    """Tests for GET /health"""

    def test_health_check(self, client):
        """Health check should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Food Rescue Platform API"
