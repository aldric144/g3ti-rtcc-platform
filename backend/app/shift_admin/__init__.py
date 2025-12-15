"""
RTCC Shift Management Module - Supervisor Tools

This module provides:
- Shift open/close management
- Personnel tracking
- Major event recording
- Supervisor sign-off
"""

from .shift_model import Shift, ShiftOperator, MajorEvent, OperatorRole
from .shift_service import ShiftService, get_shift_service
from .shift_api import router as shift_router

__all__ = [
    "Shift",
    "ShiftOperator",
    "MajorEvent",
    "OperatorRole",
    "ShiftService",
    "get_shift_service",
    "shift_router",
]
