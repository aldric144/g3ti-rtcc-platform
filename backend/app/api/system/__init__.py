"""
System API router for the G3TI RTCC-UIP Backend.

This module provides:
- Health check endpoints
- System status and metrics
- Configuration endpoints (admin only)
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import RequireAdmin
from app.core.config import settings
from app.core.logging import get_logger
from app.db.elasticsearch import get_elasticsearch
from app.db.neo4j import get_neo4j
from app.db.redis import get_redis
from app.schemas.common import HealthCheck

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """
    System health check endpoint.

    Returns the overall system status and individual component health.
    This endpoint does not require authentication.
    """
    components: dict[str, dict[str, Any]] = {}
    overall_status = "healthy"

    # Check Neo4j
    try:
        neo4j = await get_neo4j()
        neo4j_healthy = await neo4j.health_check()
        components["neo4j"] = {
            "status": "healthy" if neo4j_healthy else "unhealthy",
            "message": "Connected" if neo4j_healthy else "Connection failed",
        }
        if not neo4j_healthy:
            overall_status = "degraded"
    except Exception as e:
        components["neo4j"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "degraded"

    # Check Elasticsearch
    try:
        es = await get_elasticsearch()
        es_healthy = await es.health_check()
        components["elasticsearch"] = {
            "status": "healthy" if es_healthy else "unhealthy",
            "message": "Connected" if es_healthy else "Connection failed",
        }
        if not es_healthy:
            overall_status = "degraded"
    except Exception as e:
        components["elasticsearch"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "degraded"

    # Check Redis
    try:
        redis = await get_redis()
        redis_healthy = await redis.health_check()
        components["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "message": "Connected" if redis_healthy else "Connection failed",
        }
        if not redis_healthy:
            overall_status = "degraded"
    except Exception as e:
        components["redis"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "degraded"

    return HealthCheck(
        status=overall_status,
        version=settings.app_version,
        timestamp=datetime.now(UTC),
        components=components,
    )


@router.get("/health/live")
async def liveness_probe() -> dict[str, str]:
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe() -> dict[str, str]:
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the application is ready to receive traffic.
    """
    # In a full implementation, this would check if all
    # required services are connected and ready
    return {"status": "ready"}


@router.get("/info")
async def system_info() -> dict[str, Any]:
    """
    Get system information.

    Returns basic system information. Does not require authentication.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "api_version": "v1",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/config", dependencies=[Depends(RequireAdmin)])
async def get_config(token: RequireAdmin) -> dict[str, Any]:
    """
    Get system configuration (admin only).

    Returns non-sensitive configuration values.
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_prefix": settings.api_v1_prefix,
        "cors_origins": settings.cors_origins,
        "ws_heartbeat_interval": settings.ws_heartbeat_interval,
        "ws_max_connections": settings.ws_max_connections,
        "audit_log_enabled": settings.audit_log_enabled,
        "audit_log_retention_days": settings.audit_log_retention_days,
        # Integration status (without credentials)
        "integrations": {
            "milestone": settings.milestone_api_url is not None,
            "flock": settings.flock_api_url is not None,
            "shotspotter": settings.shotspotter_api_url is not None,
        },
    }


@router.get("/metrics", dependencies=[Depends(RequireAdmin)])
async def get_metrics(token: RequireAdmin) -> dict[str, Any]:
    """
    Get system metrics (admin only).

    Returns current system metrics and statistics.
    """
        from app.services.events.websocket_manager import get_websocket_manager

        ws_manager = get_websocket_manager()

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "websocket": {
                "active_connections": ws_manager.get_connection_count(),
            },
            "uptime": "N/A",  # Would track actual uptime in production
        }


    from .prelaunch_router import router as prelaunch_router

    __all__ = ["router", "prelaunch_router"]
