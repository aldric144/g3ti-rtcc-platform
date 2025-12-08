"""
Officer Safety & Situational Awareness Engine

This module provides comprehensive officer safety capabilities including:
- Real-time officer location telemetry ingestion
- Officer safety scoring based on environmental threats
- Threat proximity detection and alerting
- Ambush pattern detection using AI anomalies
- Scene intelligence for field operations
- Dynamic perimeter and approach route generation
- Officer down / SOS emergency detection

All components integrate with:
- Neo4j for entity relationships
- Elasticsearch for historical data
- Redis for real-time state and pub/sub
- Phase 3 AI Engine for anomaly detection
- Phase 5 Tactical Engine for risk zones
"""

from app.officer_safety.officer_safety_manager import OfficerSafetyManager

__all__ = ["OfficerSafetyManager"]
