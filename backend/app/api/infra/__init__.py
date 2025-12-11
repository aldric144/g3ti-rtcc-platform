"""
Phase 27: Infrastructure API Module

Provides REST API endpoints for enterprise infrastructure management including:
- Service health monitoring
- Failover management
- CJIS compliance checking
- Zero-trust access control
- Infrastructure audit logging
"""

from app.api.infra.infra_router import router

__all__ = ["router"]
