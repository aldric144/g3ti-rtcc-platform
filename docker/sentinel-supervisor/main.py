"""
AI Sentinel Supervisor Container Entry Point

This container runs the AI Sentinel Supervisor service for:
- System-wide monitoring of all 16 engine types
- Auto-correction of detected issues
- Ethics and legal compliance enforcement
- Sentinel decision engine for alert consolidation
"""

import os
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import SentinelConfig

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sentinel-supervisor")

app = FastAPI(
    title="AI Sentinel Supervisor",
    description="System-Wide Oversight & Ethical Governance for G3TI RTCC-UIP",
    version="33.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = SentinelConfig()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-sentinel-supervisor",
        "version": "33.0",
        "timestamp": datetime.utcnow().isoformat(),
        "config": {
            "auto_correction_enabled": config.auto_correction_enabled,
            "ethics_guard_enabled": config.ethics_guard_enabled,
            "max_autonomy_level": config.max_autonomy_level,
            "alert_threshold": config.alert_threshold,
        }
    }


@app.get("/status")
async def get_status():
    """Get detailed service status."""
    return {
        "service": "ai-sentinel-supervisor",
        "status": "operational",
        "mode": config.sentinel_mode,
        "uptime_seconds": (datetime.utcnow() - config.start_time).total_seconds(),
        "components": {
            "system_monitor": "active",
            "auto_corrector": "active" if config.auto_correction_enabled else "disabled",
            "ethics_guard": "active" if config.ethics_guard_enabled else "disabled",
            "sentinel_engine": "active",
        },
        "metrics": {
            "alerts_processed": 0,
            "corrections_executed": 0,
            "violations_detected": 0,
            "recommendations_generated": 0,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/config")
async def get_config():
    """Get current configuration."""
    return {
        "sentinel_mode": config.sentinel_mode,
        "auto_correction_enabled": config.auto_correction_enabled,
        "ethics_guard_enabled": config.ethics_guard_enabled,
        "max_autonomy_level": config.max_autonomy_level,
        "alert_threshold": config.alert_threshold,
        "correction_cooldown_seconds": config.correction_cooldown_seconds,
        "max_corrections_per_hour": config.max_corrections_per_hour,
    }


@app.post("/config/update")
async def update_config(updates: dict):
    """Update configuration dynamically."""
    allowed_updates = [
        "auto_correction_enabled",
        "ethics_guard_enabled",
        "max_autonomy_level",
        "alert_threshold",
    ]
    
    applied = {}
    for key, value in updates.items():
        if key in allowed_updates:
            setattr(config, key, value)
            applied[key] = value
    
    return {
        "status": "updated",
        "applied": applied,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.websocket("/ws/supervisor")
async def supervisor_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time supervisor updates."""
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe":
                channel = data.get("channel")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel,
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


async def run_health_monitor():
    """Background task for health monitoring."""
    while True:
        logger.debug("Running health monitor check")
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("AI Sentinel Supervisor starting up...")
    logger.info(f"Mode: {config.sentinel_mode}")
    logger.info(f"Auto-correction: {'enabled' if config.auto_correction_enabled else 'disabled'}")
    logger.info(f"Ethics guard: {'enabled' if config.ethics_guard_enabled else 'disabled'}")
    asyncio.create_task(run_health_monitor())


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("AI Sentinel Supervisor shutting down...")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8033"))
    uvicorn.run(app, host="0.0.0.0", port=port)
