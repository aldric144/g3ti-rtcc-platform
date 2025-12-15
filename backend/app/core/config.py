"""
Configuration management for the G3TI RTCC-UIP Backend.

This module provides centralized configuration management using Pydantic Settings,
supporting environment variables, .env files, and secure defaults for all system
components including database connections, authentication, and external integrations.

CJIS Compliance Note:
- All sensitive configuration values should be loaded from environment variables
- No secrets should be hardcoded or logged
- Configuration changes should be audited
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables with the same name
    (case-insensitive). For nested settings, use double underscores.

    Example:
        NEO4J_URI=bolt://localhost:7687
        REDIS_URL=redis://localhost:6379
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = "G3TI RTCC-UIP"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode (disable in production)")
    environment: Literal["development", "staging", "production"] = "development"

    # API Settings
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security Settings
    secret_key: str = Field(
        default="CHANGE-THIS-IN-PRODUCTION-USE-SECURE-RANDOM-KEY",
        description="Secret key for JWT signing - MUST be changed in production",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=30, description="JWT access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="JWT refresh token expiration time in days"
    )

    # CORS Settings
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "https://g3ti-rtcc-preview-ui.vercel.app",
            "https://session-recovery-app-i18v0ake.devinapps.com",
        ],
        description="Allowed CORS origins",
    )
    
    # Safe Mode - graceful degradation when external services unavailable
    safe_mode: bool = Field(
        default=True,
        description="Enable safe mode for graceful degradation when services unavailable",
    )
    
    # Demo Mode - full demo mode with mock data (superset of safe_mode)
    demo_mode: bool = Field(
        default=True,
        description="Enable full demo mode with mock datasets and simulated data",
    )
    
    # Demo Auth Mode - enable demo authentication when in SAFE_MODE
    demo_auth_mode: bool = Field(
        default=True,
        description="Enable demo authentication mode (admin/admin123, demo/demo123) when in SAFE_MODE",
    )
    
    # API Timeout for fail-safe responses
    api_timeout_seconds: float = Field(
        default=2.5,
        description="Timeout in seconds before returning demo response",
    )

    # Neo4j Database Settings
    neo4j_uri: str = Field(default="bolt://neo4j:7687", description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(
        default="password", description="Neo4j password - MUST be changed in production"
    )
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")

    # Elasticsearch Settings
    elasticsearch_hosts: list[str] = Field(
        default=["http://elasticsearch:9200"], description="Elasticsearch host URLs"
    )
    elasticsearch_index_prefix: str = Field(
        default="rtcc", description="Prefix for all Elasticsearch indices"
    )
    elasticsearch_user: str | None = Field(default=None, description="Elasticsearch username")
    elasticsearch_password: str | None = Field(default=None, description="Elasticsearch password")

    # Redis Settings
    redis_url: str = Field(default="redis://redis:6379/0", description="Redis connection URL")
    redis_password: str | None = Field(default=None, description="Redis password")

    # Celery Settings
    celery_broker_url: str = Field(default="redis://redis:6379/1", description="Celery broker URL")
    celery_result_backend: str = Field(
        default="redis://redis:6379/2", description="Celery result backend URL"
    )

    # WebSocket Settings
    ws_heartbeat_interval: int = Field(
        default=30, description="WebSocket heartbeat interval in seconds"
    )
    ws_max_connections: int = Field(
        default=1000, description="Maximum concurrent WebSocket connections"
    )

    # Audit Logging Settings
    audit_log_enabled: bool = Field(default=True, description="Enable CJIS-compliant audit logging")
    audit_log_retention_days: int = Field(
        default=365, description="Audit log retention period in days"
    )

    # Integration Settings (placeholders for vendor integrations)
    milestone_api_url: str | None = Field(default=None, description="Milestone VMS API URL")
    milestone_api_key: str | None = Field(default=None, description="Milestone API key")

    flock_api_url: str | None = Field(default=None, description="Flock Safety API URL")
    flock_api_key: str | None = Field(default=None, description="Flock Safety API key")

    shotspotter_api_url: str | None = Field(default=None, description="ShotSpotter API URL")
    shotspotter_api_key: str | None = Field(default=None, description="ShotSpotter API key")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",")]
        else:
            origins = list(v)
        
        # Always ensure critical origins are included
        critical_origins = [
            "https://session-recovery-app-i18v0ake.devinapps.com",
            "http://localhost:3000",
        ]
        for origin in critical_origins:
            if origin not in origins:
                origins.append(origin)
        
        return origins

    @field_validator("elasticsearch_hosts", mode="before")
    @classmethod
    def parse_elasticsearch_hosts(cls, v: str | list[str]) -> list[str]:
        """Parse Elasticsearch hosts from comma-separated string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses LRU cache to ensure settings are only loaded once per process.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance for convenience
settings = get_settings()
