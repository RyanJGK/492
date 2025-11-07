"""
Main AI Agent service application.
Provides AI-powered security analysis via OpenRouter API.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.analyzer import security_analyzer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered security analysis service for energy sector cybersecurity",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalysisRequest(BaseModel):
    """Request model for AI analysis."""
    analysis_type: str = Field(
        ...,
        pattern="^(threat_correlation|risk_assessment|anomaly_detection|trend_analysis|incident_prediction)$"
    )
    source_data: Dict[str, Any]
    weight_config: Dict[str, Any]
    query: str | None = None


class AnalysisResponse(BaseModel):
    """Response model for AI analysis."""
    analysis_type: str
    response: str
    confidence_score: float | None
    severity: str | None
    recommendations: str
    weight_config: Dict[str, Any]
    model_used: str
    tokens_used: int
    timestamp: str
    cached: bool


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "model": settings.DEFAULT_MODEL,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "cache_enabled": settings.CACHE_ENABLED
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Perform AI-powered security analysis.
    
    Args:
        request: Analysis request with type, data, and configuration
        
    Returns:
        AnalysisResponse: AI analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    logger.info(f"Received analysis request: {request.analysis_type}")
    
    try:
        result = await security_analyzer.analyze(
            analysis_type=request.analysis_type,
            source_data=request.source_data,
            weight_config=request.weight_config,
            query=request.query
        )
        
        return AnalysisResponse(**result)
        
    except ValueError as e:
        logger.error(f"Invalid analysis request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


@app.post("/api/v1/cache/clear")
async def clear_cache():
    """
    Clear all cached analysis results.
    
    Returns:
        dict: Number of entries cleared
    """
    from app.services.cache import cache_service
    
    count = await cache_service.clear()
    logger.info(f"Cache cleared: {count} entries removed")
    
    return {
        "message": "Cache cleared successfully",
        "entries_cleared": count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
