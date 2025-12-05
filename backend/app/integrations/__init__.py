"""
Integration modules for the G3TI RTCC-UIP Backend.

This module provides integration clients for external systems:
- Milestone: Video Management System (VMS)
- Flock: License Plate Recognition (LPR)
- ShotSpotter: Gunshot Detection
- OneSolution: Records Management System (RMS)
- NESS: National Enforcement Support System
- BWC: Body-Worn Camera Management
- HotSheets: BOLO/Wanted Lists

Each integration module provides:
- Client class for API communication
- Event normalization
- Error handling
- Audit logging
"""

from app.integrations.base import BaseIntegration, IntegrationStatus

__all__ = ["BaseIntegration", "IntegrationStatus"]
