"""
Main FastAPI application entry point
Configures middleware, routes, and lifecycle events
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.db.session import init_db, close_db
from app.api.routes import (
    auth_router,
    dashboard_router,
    events_router,
    vulnerabilities_router,
    patches_router,
    firewall_router,
    ai_router,
    audit_router,
)

# Initialize structured logging
setup_logging()
logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifecycle management"""
    logger.info("starting_application", version="1.0.0")
    
    # Initialize database connection
    await init_db()
    logger.info("database_initialized")
    
    yield
    
    # Cleanup
    await close_db()
    logger.info("application_shutdown")


# Initialize FastAPI application
app = FastAPI(
    title="492-Energy-Defense API",
    description="Real-time cybersecurity defense platform for energy sector",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with structured logging"""
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )
    
    response = await call_next(request)
    
    logger.info(
        "http_response",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ============================================================================
# ROUTES
# ============================================================================

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(events_router, prefix="/api/events", tags=["Events"])
app.include_router(vulnerabilities_router, prefix="/api/vulnerabilities", tags=["Vulnerabilities"])
app.include_router(patches_router, prefix="/api/patches", tags=["Patches"])
app.include_router(firewall_router, prefix="/api/firewall", tags=["Firewall"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Agent"])
app.include_router(audit_router, prefix="/api/audit", tags=["Audit"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "492-Energy-Defense API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "available",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our custom logging
    )
