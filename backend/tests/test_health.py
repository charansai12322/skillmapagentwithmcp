"""Unit tests for /api/health and root endpoints."""

import pytest
from app.config import get_settings


def test_health_endpoint_success(client):
    """Health check returns 200 OK and expected structure."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert "services" in data
    assert isinstance(data["services"], dict)


def test_health_services_status(client):
    """Health check reports configuration status of dependencies without calling them."""
    response = client.get("/api/health")
    assert response.status_code == 200

    services = response.json()["services"]
    assert "gemini" in services
    assert "rapidapi" in services
    assert "composio" in services
    assert "tavily" in services
    assert services["rapidapi"] in ("configured", "missing")


def test_health_no_secrets_exposed(client):
    """Health response must never reveal raw secret values or keys."""
    settings = get_settings()
    response = client.get("/api/health")
    body_text = response.text

    if settings.RAPIDAPI_KEY:
        assert settings.RAPIDAPI_KEY not in body_text
    if settings.GEMINI_API_KEY:
        assert settings.GEMINI_API_KEY not in body_text
    if settings.COMPOSIO_API_KEY:
        assert settings.COMPOSIO_API_KEY not in body_text
    if settings.TAVILY_API_KEY:
        assert settings.TAVILY_API_KEY not in body_text


def test_root_endpoint(client):
    """Root endpoint returns metadata and documentation routes."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["docs"] == "/docs"
    assert data["health"] == "/api/health"
