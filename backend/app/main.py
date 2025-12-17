"""
Main FastAPI application for the G3TI RTCC-UIP Backend.

This module initializes the FastAPI application with all middleware,
routers, and lifecycle events.

The RTCC-UIP (Real Time Crime Center Unified Intelligence Platform)
provides a comprehensive backend for law enforcement intelligence
operations with CJIS-compliant security and audit logging.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai_engine import get_ai_manager
from app.api import api_router
from app.api.cameras import router as cameras_router
from app.crime_analysis import crime_router
from app.crime_analysis.websocket_handler import crime_alerts_websocket
from app.camera_network.camera_ingestion_engine import get_ingestion_engine
from app.camera_network.camera_health_monitor import get_health_monitor
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    EntityNotFoundError,
    RateLimitExceededError,
    RTCCBaseException,
    ValidationError,
)
from app.core.logging import audit_logger, get_logger, setup_logging
from app.db.elasticsearch import close_elasticsearch, get_elasticsearch
from app.db.neo4j import close_neo4j, get_neo4j
from app.db.redis import close_redis, get_redis
from app.services.events.websocket_manager import get_websocket_manager

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the application,
    including database connections and background services.
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        safe_mode=settings.safe_mode,
        demo_auth_mode=settings.demo_auth_mode,
    )

    # SAFE_MODE: Skip ALL database initialization to avoid memory overhead
    if settings.safe_mode:
        logger.warning(
            "SAFE_MODE_ACTIVE",
            message="Skipping ALL database initialization - Neo4j, Elasticsearch, Redis",
            demo_auth_mode=settings.demo_auth_mode,
        )
        if settings.demo_auth_mode:
            logger.warning("DEMO_AUTH_ENABLED", message="Demo authentication active (admin/admin123)")
    else:
        # Initialize database connections only when NOT in SAFE_MODE
        try:
            neo4j = await get_neo4j()
            if neo4j._driver is not None:
                await neo4j.initialize_schema()
                logger.info("neo4j_initialized")
            else:
                logger.warning("neo4j_running_in_demo_mode")
        except Exception as e:
            logger.warning("neo4j_init_failed", error=str(e))

        try:
            es = await get_elasticsearch()
            if es._client is not None:
                await es.initialize_indices()
                logger.info("elasticsearch_initialized")
            else:
                logger.warning("elasticsearch_running_in_demo_mode")
        except Exception as e:
            logger.warning("elasticsearch_init_failed", error=str(e))

        try:
            redis_mgr = await get_redis()
            if redis_mgr._client is not None:
                logger.info("redis_initialized")
            else:
                logger.warning("redis_running_in_demo_mode")
        except Exception as e:
            logger.warning("redis_init_failed", error=str(e))

    # Start WebSocket manager (lightweight, always start)
    ws_manager = get_websocket_manager()
    await ws_manager.start()
    logger.info("websocket_manager_started")

    # Initialize AI Engine only when NOT in SAFE_MODE
    if not settings.safe_mode:
        try:
            ai_manager = get_ai_manager()
            await ai_manager.initialize()
            logger.info("ai_engine_initialized")
        except Exception as e:
            logger.warning("ai_engine_init_failed", error=str(e))
    else:
        logger.info("ai_engine_skipped_safe_mode")

    # Initialize Camera Ingestion Engine (enabled in all modes for FDOT visibility)
    # This is lightweight and doesn't require database connections
    try:
        ingestion_engine = get_ingestion_engine()
        stats = ingestion_engine.ingest_all()
        logger.info(
            "camera_ingestion_initialized",
            total_cameras=stats.get("total_count", 0),
            rbpd_count=stats.get("rbpd_count", 0),
            fdot_count=stats.get("fdot_count", 0),
            safe_mode=settings.safe_mode,
        )
    except Exception as e:
        logger.warning("camera_ingestion_init_failed", error=str(e))

    # Log startup complete
    audit_logger.log_system_event(
        "application_started",
        details={
            "version": settings.app_version,
            "environment": settings.environment,
            "safe_mode": settings.safe_mode,
            "demo_auth_mode": settings.demo_auth_mode,
        },
    )

    logger.info("application_started")

    yield

    # Shutdown
    logger.info("application_stopping")

    # Stop WebSocket manager
    await ws_manager.stop()

    # Close database connections only if NOT in SAFE_MODE
    if not settings.safe_mode:
        await close_neo4j()
        await close_elasticsearch()
        await close_redis()

    audit_logger.log_system_event(
        "application_stopped", details={"reason": "normal_shutdown"}
    )

    logger.info("application_stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    G3TI Real Time Crime Center Unified Intelligence Platform (RTCC-UIP) API.

    This API provides comprehensive backend services for law enforcement
    intelligence operations including:

    - **Authentication**: JWT-based authentication with role-based access control
    - **Entities**: Graph-based entity management (persons, vehicles, incidents, etc.)
    - **Investigations**: Case management and investigative search
    - **Real-time**: WebSocket-based real-time event streaming
    - **System**: Health checks and system monitoring

    All operations are logged for CJIS compliance.
    """,
    version=settings.app_version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

# Configure CORS - Allow all origins for demo mode
# This ensures the frontend can always connect regardless of deployment URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers


@app.exception_handler(RTCCBaseException)
async def rtcc_exception_handler(request: Request, exc: RTCCBaseException) -> JSONResponse:
    """Handle RTCC-specific exceptions."""
    logger.warning(
        "rtcc_exception", error_code=exc.error_code, message=exc.message, path=str(request.url.path)
    )

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, EntityNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, RateLimitExceededError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS

    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning("validation_error", errors=exc.errors(), path=str(request.url.path))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": exc.errors()},
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {} if not settings.debug else {"error": str(exc)},
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = datetime.now(UTC)

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

    # Log request
    logger.info(
        "http_request",
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        client_ip=request.client.host if request.client else "unknown",
    )

    return response


# ============================================================================
# ULTRA-SAFE MODE ENDPOINTS
# These endpoints are defined BEFORE the main API router so they take precedence
# They have NO dependencies and return static responses instantly
# This prevents OOM crashes on low-memory machines
# ============================================================================

ULTRA_SAFE_MODE = settings.safe_mode and settings.demo_auth_mode

if ULTRA_SAFE_MODE:
    from app.schemas.auth import Token, LoginRequest
    from app.core.security import SecurityManager
    
    logger.warning("ULTRA_SAFE_MODE_ACTIVE", message="Auth endpoints will return static responses")
    
    # Create a single SecurityManager instance for token generation
    _ultra_safe_security = SecurityManager()
    
    @app.post(f"{settings.api_v1_prefix}/auth/login", response_model=Token, tags=["Authentication (Ultra-Safe)"])
    async def login_ultra_safe(login_data: LoginRequest) -> Token:
        """
        ULTRA-SAFE MODE login endpoint.
        
        Returns a valid JWT token without any database lookups.
        The token is properly signed so the frontend can decode it.
        
        Accepts: admin/admin123 or demo/demo123
        """
        logger.info("ultra_safe_login_attempt", username=login_data.username)
        
        # Static credential check with user info
        valid_credentials = {
            "admin": ("admin123", "demo-admin-001", "admin"),
            "demo": ("demo123", "demo-user-001", "admin"),
        }
        
        if login_data.username in valid_credentials:
            expected_password, user_id, role = valid_credentials[login_data.username]
            if login_data.password == expected_password:
                logger.warning("ULTRA_SAFE_MODE_LOGIN_SUCCESS", username=login_data.username)
                
                # Generate valid JWT tokens
                token_data = {
                    "sub": user_id,
                    "username": login_data.username,
                    "role": role,
                }
                access_token = _ultra_safe_security.create_access_token(token_data)
                refresh_token = _ultra_safe_security.create_refresh_token(token_data)
                
                return Token(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=settings.access_token_expire_minutes * 60,
                )
        
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail="Invalid demo credentials. Use admin/admin123 or demo/demo123",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    @app.get(f"{settings.api_v1_prefix}/auth/me", tags=["Authentication (Ultra-Safe)"])
    async def get_current_user_ultra_safe() -> dict:
        """
        ULTRA-SAFE MODE /me endpoint.
        
        Returns a static demo user without any token validation,
        database lookups, or heavy initialization.
        
        This endpoint has NO dependencies - it returns instantly.
        """
        logger.info("ultra_safe_me_called")
        return {
            "id": "demo-admin-001",
            "username": "admin",
            "email": "admin@g3ti-demo.com",
            "first_name": "Demo",
            "last_name": "Admin",
            "badge_number": "DEMO-001",
            "department": "System Administration",
            "role": "admin",
            "is_active": True,
            "permissions": ["all"],
            "status": "ok",
        }

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Include cameras router at /api/cameras for direct access (alias)
app.include_router(cameras_router, prefix="/api", tags=["Cameras (alias)"])

# Include crime analysis router
app.include_router(crime_router)


# WebSocket endpoint for crime alerts
from fastapi import WebSocket

@app.websocket("/ws/crime/alerts")
async def crime_alerts_ws_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time crime alerts."""
    await crime_alerts_websocket(websocket)


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "api_docs": f"{settings.api_v1_prefix}/docs",
        "health": f"{settings.api_v1_prefix}/system/health",
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Simple health endpoint for SAFE_MODE status
@app.get("/health")
async def simple_health() -> dict:
    """
    Simple health endpoint showing SAFE_MODE and DEMO_AUTH status.
    
    This endpoint is lightweight and doesn't require any database connections.
    Always returns HTTP 200 to prevent Fly.io machine restarts in DEMO mode.
    """
    return {
        "status": "ok",
        "safe_mode": settings.safe_mode,
        "demo_mode": settings.demo_mode,
        "demo_auth": settings.demo_auth_mode,
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Fly.io healthcheck endpoint - always returns 200
@app.get("/healthz")
async def flyio_healthcheck() -> dict:
    """
    Fly.io healthcheck endpoint.
    
    Always returns HTTP 200 to prevent machine restarts due to missing DB connections.
    This is critical for DEMO mode operation.
    """
    return {
        "status": "healthy",
        "demo_mode": settings.demo_mode,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
