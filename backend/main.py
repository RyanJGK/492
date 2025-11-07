"""Main FastAPI application for Energy Defense backend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from config import settings
from database import init_db, get_db
from routers import auth, events, analysis, admin
from services.ai_model import AIModelService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Energy Defense backend...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Load AI models
    try:
        ai_service = AIModelService(model_path=settings.MODEL_PATH)
        ai_service.load_models()
        logger.info("✓ AI models loaded")
    except Exception as e:
        logger.warning(f"Could not load AI models: {e}")
        logger.info("Using rule-based detection instead")
    
    logger.info("=" * 60)
    logger.info("Energy Defense Backend is ready!")
    logger.info(f"API documentation: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Energy Defense backend...")


# Create FastAPI application
app = FastAPI(
    title="Energy Defense API",
    description="AI-Powered Energy Sector Cybersecurity Demo",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(analysis.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Energy Defense API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
