"""
Phase 18: National Security API Endpoints

Provides REST API endpoints for:
- Cyber Intelligence
- Insider Threat Detection
- Geopolitical Risk Assessment
- Financial Crime Intelligence
- National Risk Fusion
- National Security Alerts
"""

from app.api.national_security.router import router

__all__ = ["router"]
