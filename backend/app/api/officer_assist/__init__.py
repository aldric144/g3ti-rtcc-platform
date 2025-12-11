"""
Phase 28: Officer Assist API Layer

API endpoints for the AI Officer Assist Suite including:
- Constitutional guardrail checks
- Use-of-force risk assessment
- Tactical advice
- Officer intent interpretation
- Officer status monitoring
- Alert management
"""

from .officer_assist_router import OfficerAssistRouter

__all__ = ["OfficerAssistRouter"]
