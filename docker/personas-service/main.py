"""
AI Personas Service - Main Entry Point

Phase 34: Apex AI Officers
Standalone service for AI Personas operations.
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("personas-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Personas Service...")
    logger.info(f"Service version: {settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    yield
    
    logger.info("Shutting down AI Personas Service...")


app = FastAPI(
    title="AI Personas Service",
    description="Phase 34: Apex AI Officers - Operational AI Personas for G3TI RTCC-UIP",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "personas-service",
        "version": settings.VERSION,
        "phase": 34,
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "service": "AI Personas Service",
        "description": "Apex AI Officers - Phase 34",
        "version": settings.VERSION,
        "endpoints": {
            "health": "/health",
            "personas": "/api/personas",
            "missions": "/api/missions",
            "compliance": "/api/compliance",
            "websocket_chat": "/ws/personas/{persona_id}/chat",
            "websocket_alerts": "/ws/personas/alerts",
        },
    }


@app.get("/api/personas")
async def get_personas() -> Dict[str, Any]:
    """Get all registered personas."""
    try:
        from backend.app.personas.persona_engine import PersonaEngine
        engine = PersonaEngine()
        personas = engine.get_all_personas()
        return {
            "personas": [p.to_dict() for p in personas],
            "total": len(personas),
            "active": len([p for p in personas if p.status.value == "active"]),
        }
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/personas/{persona_id}")
async def get_persona(persona_id: str) -> Dict[str, Any]:
    """Get persona details."""
    try:
        from backend.app.personas.persona_engine import PersonaEngine
        engine = PersonaEngine()
        persona = engine.get_persona(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona not found: {persona_id}")
        return persona.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/personas/{persona_id}/status")
async def get_persona_status(persona_id: str) -> Dict[str, Any]:
    """Get persona status."""
    try:
        from backend.app.personas.persona_engine import PersonaEngine
        engine = PersonaEngine()
        persona = engine.get_persona(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona not found: {persona_id}")
        return {
            "persona_id": persona.persona_id,
            "name": persona.name,
            "status": persona.status.value,
            "emotional_state": persona.emotional_state.value,
            "active_sessions": len(persona.active_sessions),
            "compliance_score": persona.get_compliance_score(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/missions")
async def get_missions() -> Dict[str, Any]:
    """Get all missions."""
    try:
        from backend.app.personas.mission_reasoner import MissionReasoner
        reasoner = MissionReasoner()
        missions = reasoner.get_all_missions()
        return {
            "missions": [m.to_dict() for m in missions],
            "total": len(missions),
            "active": len([m for m in missions if m.status.value == "in_progress"]),
        }
    except Exception as e:
        logger.error(f"Error getting missions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance/summary")
async def get_compliance_summary() -> Dict[str, Any]:
    """Get compliance summary."""
    try:
        from backend.app.personas.compliance_layer import ComplianceIntegrationLayer
        layer = ComplianceIntegrationLayer()
        return layer.get_compliance_summary()
    except Exception as e:
        logger.error(f"Error getting compliance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get overall statistics."""
    try:
        from backend.app.personas.persona_engine import PersonaEngine
        from backend.app.personas.interaction_engine import InteractionEngine
        from backend.app.personas.mission_reasoner import MissionReasoner
        from backend.app.personas.compliance_layer import ComplianceIntegrationLayer
        
        return {
            "personas": PersonaEngine().get_statistics(),
            "interactions": InteractionEngine().get_statistics(),
            "missions": MissionReasoner().get_statistics(),
            "compliance": ComplianceIntegrationLayer().get_statistics(),
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/personas/{persona_id}/chat")
async def websocket_chat(websocket: WebSocket, persona_id: str):
    """WebSocket endpoint for persona chat."""
    await websocket.accept()
    logger.info(f"WebSocket connection opened for persona: {persona_id}")
    
    try:
        from backend.app.personas.persona_engine import PersonaEngine
        from backend.app.personas.interaction_engine import InteractionEngine, InteractionType
        
        engine = PersonaEngine()
        interaction_engine = InteractionEngine()
        
        persona = engine.get_persona(persona_id)
        if not persona:
            await websocket.send_json({"error": f"Persona not found: {persona_id}"})
            await websocket.close()
            return
        
        session = interaction_engine.create_session(
            persona_id=persona_id,
            user_id="websocket_user",
            interaction_type=InteractionType.WEBSOCKET,
        )
        
        await websocket.send_json({
            "type": "welcome",
            "persona_id": persona.persona_id,
            "persona_name": persona.name,
            "session_id": session.session_id,
            "message": f"Connected to {persona.name}. How can I assist you?",
        })
        
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if message:
                response = interaction_engine.process_input(session.session_id, message)
                await websocket.send_json({
                    "type": "response",
                    "response_id": response.response_id,
                    "content": response.content,
                    "emotional_tone": response.emotional_tone.value,
                    "confidence": response.confidence,
                    "action_items": response.action_items,
                    "follow_up_questions": response.follow_up_questions,
                    "escalation_required": response.escalation_required,
                    "escalation_reason": response.escalation_reason,
                    "response_time_ms": response.response_time_ms,
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for persona: {persona_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()


@app.websocket("/ws/personas/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for system alerts."""
    await websocket.accept()
    logger.info("WebSocket connection opened for alerts")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "alerts",
            "message": "Connected to alerts channel",
        })
        
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": asyncio.get_event_loop().time(),
            })
    
    except WebSocketDisconnect:
        logger.info("WebSocket alerts connection closed")
    except Exception as e:
        logger.error(f"WebSocket alerts error: {e}")


def handle_shutdown(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
