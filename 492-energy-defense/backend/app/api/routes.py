"""
Central router imports for main application
"""

from fastapi import APIRouter

# Import all routers
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.dashboard import router as dashboard_router
from app.api.endpoints.events import router as events_router
from app.api.endpoints.vulnerabilities import router as vulnerabilities_router
from app.api.endpoints.patches import router as patches_router
from app.api.endpoints.firewall import router as firewall_router
from app.api.endpoints.ai import router as ai_router
from app.api.endpoints.audit import router as audit_router

__all__ = [
    "auth_router",
    "dashboard_router",
    "events_router",
    "vulnerabilities_router",
    "patches_router",
    "firewall_router",
    "ai_router",
    "audit_router",
]
