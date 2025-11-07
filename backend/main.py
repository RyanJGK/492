"""Main FastAPI application for Energy Defense backend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Energy Defense API",
    description="AI-Powered Energy Sector Cybersecurity Demo",
    version="1.0.0"
)

# Configure CORS - MUST be before route definitions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("=" * 60)
logger.info("Energy Defense Backend is ready!")
logger.info("API documentation: http://localhost:8000/docs")
logger.info("=" * 60)


# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# TODO: Restore database integration after PostgreSQL is running
# TODO: Restore full authentication with database user lookup
# TODO: Restore all routers (events, analysis, admin)
# TODO: Restore AI model loading


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
        "database": "pending"
    }


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Simplified login endpoint for development.
    Returns mock JWT tokens for any valid-looking credentials.
    
    TODO: Replace with real authentication using database
    """
    # Accept demo credentials
    valid_users = {
        "admin": "admin123",
        "analyst": "analyst123",
        "observer": "observer123"
    }
    
    if credentials.username not in valid_users:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if valid_users[credentials.username] != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Determine role based on username
    role_map = {
        "admin": "admin",
        "analyst": "analyst",
        "observer": "observer"
    }
    role = role_map.get(credentials.username, "observer")
    
    # Create mock JWT token (base64 encoded JSON for demo)
    import json
    import base64
    
    # JWT structure: header.payload.signature
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": credentials.username,
        "role": role,
        "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
    }
    
    # Create simple mock token (NOT SECURE - for demo only)
    header_b64 = base64.b64encode(json.dumps(header).encode()).decode()
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    mock_token = f"{header_b64}.{payload_b64}.mock_signature"
    
    logger.info(f"User '{credentials.username}' logged in successfully (role: {role})")
    
    return TokenResponse(
        access_token=mock_token,
        refresh_token=mock_token,
        token_type="bearer"
    )


@app.get("/api/analyze/dashboard")
async def get_dashboard():
    """
    Mock dashboard endpoint.
    TODO: Replace with real AI analysis
    """
    return {
        "threat_level": "info",
        "confidence_score": 0.0,
        "active_threats": 0,
        "affected_systems": [],
        "threat_counts": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "recent_alerts": []
    }


@app.get("/api/events/auth")
async def get_auth_events():
    """
    Mock authentication events endpoint.
    TODO: Replace with real database query
    """
    return []


@app.get("/api/events/network")
async def get_network_logs():
    """
    Mock network logs endpoint.
    TODO: Replace with real database query
    """
    return []


@app.get("/api/events/patches")
async def get_patch_status():
    """
    Mock patch status endpoint.
    TODO: Replace with real database query
    """
    return []


@app.get("/api/events/vulnerabilities")
async def get_vulnerabilities():
    """
    Mock vulnerabilities endpoint.
    TODO: Replace with real database query
    """
    return []


@app.get("/api/analyze/threats")
async def get_threats():
    """
    Mock threats endpoint.
    TODO: Replace with real AI analysis
    """
    return []


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
