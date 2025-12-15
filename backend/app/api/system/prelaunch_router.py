"""
G3TI RTCC-UIP Pre-Launch API Router
Endpoints for system validation, deployment readiness, and integration checks.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/system/prelaunch", tags=["System Pre-Launch"])


@router.get("/status")
async def get_prelaunch_status() -> Dict[str, Any]:
    """
    Get complete pre-launch system status.
    Returns module integrity, WebSocket connectivity, API validation, and orchestration status.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return {
        "modules_ok": status.modules_ok,
        "websockets_ok": status.websockets_ok,
        "endpoints_ok": status.endpoints_ok,
        "orchestration_ok": status.orchestration_ok,
        "database_ok": status.database_ok,
        "ai_engines_ok": status.ai_engines_ok,
        "latency_ms": status.latency_ms,
        "load_factor": status.load_factor,
        "deployment_score": status.deployment_score,
        "errors": status.errors,
        "warnings": status.warnings,
        "module_count": len(status.module_validations),
        "websocket_count": len(status.websocket_validations),
        "api_count": len(status.api_validations),
        "validated_at": status.validated_at.isoformat(),
    }


@router.get("/status/detailed")
async def get_detailed_prelaunch_status() -> Dict[str, Any]:
    """
    Get detailed pre-launch status with all validation results.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return status.to_dict()


@router.get("/modules")
async def get_module_validations() -> Dict[str, Any]:
    """
    Get module validation results.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return {
        "total_modules": len(status.module_validations),
        "modules_ok": status.modules_ok,
        "modules": [v.to_dict() for v in status.module_validations],
    }


@router.get("/websockets")
async def get_websocket_validations() -> Dict[str, Any]:
    """
    Get WebSocket channel validation results.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return {
        "total_websockets": len(status.websocket_validations),
        "websockets_ok": status.websockets_ok,
        "websockets": [v.to_dict() for v in status.websocket_validations],
    }


@router.get("/endpoints")
async def get_endpoint_validations() -> Dict[str, Any]:
    """
    Get API endpoint validation results.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return {
        "total_endpoints": len(status.api_validations),
        "endpoints_ok": status.endpoints_ok,
        "endpoints": [v.to_dict() for v in status.api_validations],
    }


@router.get("/orchestration")
async def get_orchestration_status() -> Dict[str, Any]:
    """
    Get orchestration engine status and responsiveness.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    result = await integrator.validate_orchestration_engine()

    return result


@router.get("/websocket-check")
async def get_websocket_integration_check(
    include_stress_test: bool = Query(True, description="Include stress test with 500 events")
) -> Dict[str, Any]:
    """
    Run WebSocket integration check with ping, handshake, and broadcast tests.
    """
    from app.system.ws_integration_checker import get_ws_integration_checker

    checker = get_ws_integration_checker()
    status = await checker.run_full_check(include_stress_test=include_stress_test)

    return status.to_dict()


@router.get("/websocket-check/ping")
async def get_websocket_ping_results() -> Dict[str, Any]:
    """
    Get WebSocket ping test results.
    """
    from app.system.ws_integration_checker import get_ws_integration_checker

    checker = get_ws_integration_checker()
    status = await checker.run_full_check(include_stress_test=False)

    return {
        "total_channels": len(status.ping_results),
        "passed": len([p for p in status.ping_results if p.status.value == "passed"]),
        "failed": len([p for p in status.ping_results if p.status.value == "failed"]),
        "avg_latency_ms": status.avg_latency_ms,
        "results": [p.to_dict() for p in status.ping_results],
    }


@router.get("/websocket-check/stress")
async def run_websocket_stress_test(
    event_count: int = Query(500, ge=100, le=10000, description="Number of events to simulate")
) -> Dict[str, Any]:
    """
    Run WebSocket stress test with simulated events.
    """
    from app.system.ws_integration_checker import get_ws_integration_checker

    checker = get_ws_integration_checker()
    result = await checker.run_stress_test(event_count=event_count)

    return result.to_dict()


@router.get("/websocket-check/repair-suggestions")
async def get_repair_suggestions() -> Dict[str, Any]:
    """
    Get auto-repair suggestions for WebSocket issues.
    """
    from app.system.ws_integration_checker import get_ws_integration_checker

    checker = get_ws_integration_checker()
    status = await checker.run_full_check(include_stress_test=False)

    return {
        "total_suggestions": len(status.repair_suggestions),
        "suggestions": [s.to_dict() for s in status.repair_suggestions],
    }


@router.get("/deployment-score")
async def get_deployment_score() -> Dict[str, Any]:
    """
    Get deployment readiness score (0-100%).
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    ready_for_deployment = status.deployment_score >= 85

    return {
        "deployment_score": status.deployment_score,
        "ready_for_deployment": ready_for_deployment,
        "modules_ok": status.modules_ok,
        "websockets_ok": status.websockets_ok,
        "endpoints_ok": status.endpoints_ok,
        "orchestration_ok": status.orchestration_ok,
        "errors": status.errors,
        "warnings": status.warnings,
        "recommendation": "Ready for deployment" if ready_for_deployment else "Address errors before deployment",
    }


@router.get("/statistics")
async def get_prelaunch_statistics() -> Dict[str, Any]:
    """
    Get pre-launch integrator statistics.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator
    from app.system.ws_integration_checker import get_ws_integration_checker

    integrator = get_prelaunch_integrator()
    ws_checker = get_ws_integration_checker()

    return {
        "integrator": integrator.get_statistics(),
        "ws_checker": ws_checker.get_statistics(),
    }


@router.get("/history")
async def get_validation_history(
    limit: int = Query(10, ge=1, le=100, description="Number of history entries to return")
) -> Dict[str, Any]:
    """
    Get validation history.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    history = integrator.get_validation_history(limit=limit)

    return {
        "total_entries": len(history),
        "history": [s.to_dict() for s in history],
    }


@router.post("/validate")
async def trigger_validation() -> Dict[str, Any]:
    """
    Trigger a new validation run.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    status = await integrator.run_full_validation()

    return {
        "status": "completed",
        "deployment_score": status.deployment_score,
        "modules_ok": status.modules_ok,
        "websockets_ok": status.websockets_ok,
        "endpoints_ok": status.endpoints_ok,
        "orchestration_ok": status.orchestration_ok,
        "latency_ms": status.latency_ms,
        "validated_at": status.validated_at.isoformat(),
    }


@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """
    Get overall system health status.
    """
    from app.system.prelaunch_integrator import get_prelaunch_integrator

    integrator = get_prelaunch_integrator()
    
    return {
        "status": "healthy",
        "module_count": integrator.get_module_count(),
        "websocket_count": integrator.get_websocket_count(),
        "endpoint_count": integrator.get_endpoint_count(),
        "timestamp": datetime.utcnow().isoformat(),
    }
