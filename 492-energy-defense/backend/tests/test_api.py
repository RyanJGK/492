"""
Integration tests for backend API
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns service info"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "492-Energy-Defense API"
        assert "version" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_switch_role():
    """Test role switching functionality"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/switch-role",
            json={"role": "admin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
        assert "username" in data


@pytest.mark.asyncio
async def test_get_roles():
    """Test getting available roles"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/auth/roles")
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert len(data["roles"]) == 3


@pytest.mark.asyncio
async def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "critical_threats" in data
        assert "last_updated" in data


# Add more tests as needed
pytest_plugins = ('pytest_asyncio',)
