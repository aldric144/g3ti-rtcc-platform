"""
Phase 26: Ethics Guardian API Layer

API endpoints for:
- Bias detection
- Use-of-force risk assessment
- Civil rights compliance
- Ethics scoring
- Explainability
- Audit logging
- Protected community safeguards
"""

from app.api.ethics_guardian.ethics_router import router as ethics_router

__all__ = ["ethics_router"]
