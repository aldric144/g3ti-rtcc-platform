"""
AI Personas Service Configuration

Phase 34: Apex AI Officers
"""

import os
from typing import List


class Settings:
    """Service configuration settings."""
    
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8034"))
    
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://localhost:8034"
    ).split(",")
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    PERSONA_ENGINE_ENABLED: bool = os.getenv("PERSONA_ENGINE_ENABLED", "true").lower() == "true"
    INTERACTION_ENGINE_ENABLED: bool = os.getenv("INTERACTION_ENGINE_ENABLED", "true").lower() == "true"
    MISSION_REASONER_ENABLED: bool = os.getenv("MISSION_REASONER_ENABLED", "true").lower() == "true"
    COMPLIANCE_LAYER_ENABLED: bool = os.getenv("COMPLIANCE_LAYER_ENABLED", "true").lower() == "true"
    
    MAX_SESSIONS_PER_PERSONA: int = int(os.getenv("MAX_SESSIONS_PER_PERSONA", "10"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    MEMORY_SHORT_TERM_LIMIT: int = int(os.getenv("MEMORY_SHORT_TERM_LIMIT", "100"))
    MEMORY_MISSION_LIMIT: int = int(os.getenv("MEMORY_MISSION_LIMIT", "50"))
    MEMORY_CONTEXT_LIMIT: int = int(os.getenv("MEMORY_CONTEXT_LIMIT", "200"))
    MEMORY_LEARNED_LIMIT: int = int(os.getenv("MEMORY_LEARNED_LIMIT", "500"))
    
    COMPLIANCE_CHECK_ENABLED: bool = os.getenv("COMPLIANCE_CHECK_ENABLED", "true").lower() == "true"
    COMPLIANCE_STRICT_MODE: bool = os.getenv("COMPLIANCE_STRICT_MODE", "true").lower() == "true"
    
    WEBSOCKET_HEARTBEAT_INTERVAL: int = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30"))
    WEBSOCKET_MAX_CONNECTIONS: int = int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "100"))


settings = Settings()
