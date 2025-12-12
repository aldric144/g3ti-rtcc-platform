# Phase 32: Global Situation Awareness Engine (GSAE)

## Overview

The Global Situation Awareness Engine (GSAE) is a comprehensive multi-domain intelligence fusion platform that provides real-time global monitoring, risk assessment, and predictive analytics for the G3TI RTCC-UIP system.

## Architecture

### Backend Modules

#### 1. Multi-Domain Global Sensor Layer (`global_sensor_layer.py`)

The sensor layer ingests data from multiple global sources across 10 domains:

**Sensor Domains:**
- Crisis (GDACS, ReliefWeb, ACLED)
- Conflict (armed conflicts, civil unrest)
- Maritime (AIS vessel tracking)
- Aviation (ADS-B flight tracking)
- Cyber (threat intelligence, CVE feeds)
- Economic (market indicators, trade data)
- Health (WHO, disease outbreaks)
- Environmental (NOAA, USGS, climate data)
- Geopolitical (sanctions, diplomatic events)
- Supply Chain (port activity, shipping)

**Key Features:**
- Real-time signal ingestion from 14+ data sources
- Anomaly detection for maritime (AIS spoofing, dark voyages)
- Anomaly detection for aviation (hijacking, transponder issues)
- Signal validation and correlation
- Chain of custody hashing for all data

#### 2. Global Knowledge Graph Engine (`knowledge_graph_engine.py`)

Builds and maintains a knowledge graph of global entities and relationships:

**Entity Types:**
- Countries, Organizations, Persons
- Locations, Events, Assets
- Threat Actors, Infrastructure
- Commodities, Alliances

**Relationship Types:**
- Political (ally, adversary)
- Economic (partner, competitor)
- Military (ally, adversary)
- Influence, Control, Support

**Features:**
- Entity extraction and linking
- Relationship mapping and strength scoring
- Influence network analysis
- Causal inference modeling

#### 3. Global Risk Fusion Engine (`risk_fusion_engine.py`)

Multi-domain risk scoring and assessment:

**Risk Domains:**
- Climate, Geopolitical, Cyber
- Supply Chain, Health, Conflict
- Economic, Infrastructure
- Social, Environmental

**Features:**
- Domain-specific risk scoring
- Risk interaction modeling
- 7-day and 30-day forecasting
- Automated alert generation
- Mitigation recommendations

#### 4. Global Event Correlation Engine (`event_correlation_engine.py`)

Cause-effect cascade modeling and pattern detection:

**Event Categories:**
- Political, Military, Economic
- Social, Environmental, Technological
- Health, Security

**Features:**
- Automatic event correlation
- Cascade effect prediction
- Pattern detection
- Timeline reconstruction
- Narrative generation

#### 5. Satellite Imagery Analysis Layer (`satellite_analysis_layer.py`)

AI-based satellite imagery analysis:

**Imagery Sources:**
- Sentinel-2, Landsat-8
- Planet, Maxar
- Capella SAR, ICEYE

**Analysis Types:**
- Change detection
- Object detection
- Infrastructure assessment
- Maritime activity monitoring
- Military activity detection

### API Endpoints

Base path: `/api/global-awareness`

**Signal Ingestion:**
- `POST /ingest/crisis` - Ingest crisis events
- `POST /ingest/conflict` - Ingest conflict indicators
- `POST /ingest/maritime` - Ingest maritime AIS data
- `POST /ingest/aviation` - Ingest aviation ADS-B data
- `POST /ingest/cyber` - Ingest cyber threat signals

**Signal Queries:**
- `GET /signals` - Get signals with filters
- `GET /signals/actionable` - Get actionable signals

**Knowledge Graph:**
- `POST /entities` - Create entity
- `GET /entities/{id}` - Get entity
- `GET /entities/{id}/network` - Get entity network
- `POST /relationships` - Create relationship
- `GET /entities/{id}/influence` - Calculate influence

**Risk Assessment:**
- `POST /risk/assess` - Create fused assessment
- `POST /risk/domain` - Assess domain risk
- `GET /risk/summary` - Get regional summary
- `GET /risk/alerts` - Get active alerts

**Event Correlation:**
- `POST /events` - Create event
- `GET /events/{id}` - Get event
- `GET /events/{id}/correlations` - Get correlations
- `POST /events/cascade` - Predict cascade
- `POST /events/timeline` - Reconstruct timeline
- `GET /events/patterns` - Detect patterns

**Satellite Analysis:**
- `POST /satellite/ingest` - Ingest image
- `POST /satellite/detect-changes` - Detect changes
- `POST /satellite/maritime/{id}` - Analyze maritime
- `POST /satellite/infrastructure/{id}` - Assess infrastructure
- `POST /satellite/military/{id}` - Detect military
- `GET /satellite/alerts` - Get alerts
- `GET /satellite/detections` - Get recent detections

**Statistics:**
- `GET /statistics` - Get all module statistics

### WebSocket Channels

- `/ws/global-awareness/signals` - Real-time global signals
- `/ws/global-awareness/risk` - Risk assessment updates
- `/ws/global-awareness/events` - Event correlation updates
- `/ws/global-awareness/satellite` - Satellite detection alerts

### Frontend Pages

**Main Dashboard:** `/global-awareness`

**Tabs:**
1. **World Map** - Global signal visualization with domain filtering
2. **Risk Fusion** - Multi-domain risk assessment dashboard
3. **Satellite Analysis** - Satellite imagery analysis panel
4. **Cyber Intelligence** - Cyber threat monitoring
5. **Event Correlation** - Cause-effect cascade visualization

### DevOps Containers

1. **gsae-crisis-ingest** (Port 8080)
   - Crisis feed ingestion from GDACS, ReliefWeb, ACLED

2. **gsae-cyber-ingest** (Port 8081)
   - Cyber threat intelligence ingestion

3. **gsae-satellite-vision** (Port 8082)
   - AI-based satellite imagery analysis

4. **gsae-fusion-engine** (Port 8083)
   - Multi-domain risk fusion engine

### GitHub Action

`gsae-selftest.yml` runs on push/PR to relevant paths:
- Unit tests for all GSAE modules
- Integration tests for API endpoints
- Docker build verification for all containers
- Security scanning with Bandit
- Linting with Ruff/Black
- Type checking with MyPy

## Data Flow

```
External Sources → Sensor Layer → Signal Validation → Knowledge Graph
                                        ↓
                              Risk Fusion Engine
                                        ↓
                           Event Correlation Engine
                                        ↓
                              Satellite Analysis
                                        ↓
                            WebSocket Broadcasts
                                        ↓
                              Frontend Dashboard
```

## Chain of Custody

All data structures include SHA256 chain of custody hashing:
- Signals, Events, Assessments
- Detections, Correlations, Cascades
- Ensures data integrity and auditability

## Security Considerations

- No private social media data ingestion
- No predictive policing on protected classes
- No demographic profiling
- All predictions include confidence scores
- Human-in-the-loop for critical decisions

## Integration Points

- Integrates with Phase 31 (Emergency AI) for disaster response
- Integrates with Phase 29 (Cyber Intelligence) for threat correlation
- Integrates with Phase 17 (Global Threat Intel) for threat actor data

## Test Coverage

12 test suites covering:
1. Global Sensor Layer
2. Knowledge Graph Engine
3. Risk Fusion Engine
4. Event Correlation Engine
5. Satellite Analysis Layer
6. API Endpoints
7. WebSocket Channels
8. Crisis Ingestion
9. Cyber Ingestion
10. Maritime Analysis
11. Military Detection
12. Neutrality Audits

## Version

- Phase: 32
- Version: 32.0
- Status: Complete
