"""
Investigations Engine Module.

This module provides the core functionality for the Investigations Engine,
including case building, incident linking, timeline generation, entity
correlation, evidence collection, and report generation.
"""

from app.investigations_engine.investigations_manager import InvestigationsManager

__all__ = [
    "InvestigationsManager",
]
