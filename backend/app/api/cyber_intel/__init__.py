"""
Phase 29: Cyber Intelligence API Layer

Provides REST API endpoints for cyber threat detection, quantum threat analysis,
and information warfare monitoring.

Endpoints:
- GET  /api/cyber-intel/overview
- GET  /api/cyber-intel/threats
- POST /api/cyber-intel/scan/network
- POST /api/cyber-intel/scan/quantum
- POST /api/cyber-intel/scan/deepfake
- POST /api/cyber-intel/scan/info-warfare
- GET  /api/cyber-intel/alerts

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from .cyber_intel_router import router as cyber_intel_router

__all__ = ["cyber_intel_router"]
