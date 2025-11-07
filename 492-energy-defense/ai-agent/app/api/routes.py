"""Central router imports"""

from app.api.endpoints.analysis import router as analysis_router
from app.api.endpoints.model import router as model_router

__all__ = ["analysis_router", "model_router"]
