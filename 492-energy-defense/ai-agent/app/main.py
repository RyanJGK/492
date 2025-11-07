"""
AI Agent FastAPI application
Provides threat analysis using TensorFlow models
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import structlog

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.db.session import init_db, close_db
from app.ml.model_manager import ModelManager
from app.api.routes import analysis_router, model_router

# Initialize logging
setup_logging()
logger = structlog.get_logger()
settings = get_settings()

# Global model manager
model_manager: ModelManager = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifecycle management"""
    global model_manager
    
    logger.info("starting_ai_agent", version="1.0.0")
    
    # Initialize database
    await init_db()
    logger.info("database_initialized")
    
    # Initialize ML model
    model_manager = ModelManager()
    await model_manager.initialize()
    app.state.model_manager = model_manager
    logger.info("ml_model_initialized")
    
    yield
    
    # Cleanup
    await close_db()
    logger.info("ai_agent_shutdown")


# Initialize FastAPI
app = FastAPI(
    title="492-Energy-Defense AI Agent",
    description="TensorFlow-based threat analysis service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/ai/docs",
    redoc_url="/ai/redoc",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    logger.info(
        "ai_http_request",
        method=request.method,
        path=request.url.path,
    )
    
    response = await call_next(request)
    
    logger.info(
        "ai_http_response",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "ai_unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(analysis_router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(model_router, prefix="/api/model", tags=["Model"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "492-Energy-Defense AI Agent",
        "version": "1.0.0",
        "status": "operational",
        "model_ready": model_manager is not None and model_manager.is_ready(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model_manager is not None and model_manager.is_ready(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config=None,
    )
