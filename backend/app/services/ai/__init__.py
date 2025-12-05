"""
AI/ML services for the G3TI RTCC-UIP Backend.

This module provides AI-powered capabilities including:
- Entity extraction from narratives
- Pattern recognition and anomaly detection
- Predictive analytics
- Natural language query processing
- Embedding generation for semantic search

Note: This is the foundation module. AI model integrations
will be added in future phases.
"""

from app.services.ai.embeddings import EmbeddingsService

__all__ = ["EmbeddingsService"]
