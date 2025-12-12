"""
GSAE Crisis Ingestion Service

Ingests crisis data from GDACS, ReliefWeb, and ACLED feeds.
"""

import asyncio
import hashlib
import os
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="GSAE Crisis Ingestion Service",
    description="Phase 32: Crisis feed ingestion for Global Situation Awareness Engine",
    version="32.0",
)


class CrisisEvent(BaseModel):
    event_type: str
    severity: int
    lat: float
    lon: float
    country: str
    region: str
    affected_population: int = 0
    casualties: int = 0
    displaced: int = 0
    description: str = ""
    source: str = "gdacs"


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    version: str


class IngestResponse(BaseModel):
    status: str
    event_id: str
    chain_of_custody_hash: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="gsae-crisis-ingest",
        timestamp=datetime.utcnow().isoformat(),
        version="32.0",
    )


@app.post("/ingest/crisis", response_model=IngestResponse)
async def ingest_crisis(event: CrisisEvent):
    event_id = f"CE-{hashlib.sha256(f'{event.event_type}:{event.lat}:{event.lon}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"

    chain_hash = hashlib.sha256(
        f"{event_id}:{event.event_type}:{event.severity}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    return IngestResponse(
        status="ingested",
        event_id=event_id,
        chain_of_custody_hash=chain_hash,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/sources")
async def list_sources():
    return {
        "sources": [
            {"id": "gdacs", "name": "Global Disaster Alert and Coordination System", "status": "active"},
            {"id": "reliefweb", "name": "ReliefWeb", "status": "active"},
            {"id": "acled", "name": "Armed Conflict Location & Event Data", "status": "active"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
