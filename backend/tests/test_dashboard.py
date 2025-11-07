"""
Tests for dashboard endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_summary(client: AsyncClient, auth_headers):
    """Test getting dashboard summary."""
    response = await client.get(
        "/api/v1/dashboard/summary",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "auth_events" in data
    assert "vulnerabilities" in data
    assert "firewall" in data


@pytest.mark.asyncio
async def test_get_vulnerabilities(client: AsyncClient, auth_headers):
    """Test getting vulnerabilities list."""
    response = await client.get(
        "/api/v1/dashboard/vulnerabilities",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient):
    """Test that dashboard requires authentication."""
    response = await client.get("/api/v1/dashboard/summary")
    assert response.status_code == 403
