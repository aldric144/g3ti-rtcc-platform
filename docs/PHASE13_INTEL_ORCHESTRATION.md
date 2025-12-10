# Phase 13: Intelligence Orchestration Engine

## Overview

The Intelligence Orchestration Engine is the master fusion layer that coordinates all intelligence sources, engines, and subsystems across the entire RTCC-UIP architecture. It serves as the central nervous system for intelligence processing, correlation, prioritization, and distribution.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Intelligence Orchestration Engine                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  AI Engine   │    │   Tactical   │    │ Investigations│                  │
│  │              │    │    Engine    │    │    Engine     │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬────────┘                  │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Signal Ingestion Layer                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │Real-Time│  │  Batch  │  │ Fusion  │  │ Officer │  │  Leads  │    │   │
│  │  │Pipeline │  │Pipeline │  │Pipeline │  │ Safety  │  │Pipeline │    │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │   │
│  └───────┼────────────┼────────────┼────────────┼────────────┼──────────┘   │
│          │            │            │            │            │               │
│          └────────────┴────────────┼────────────┴────────────┘               │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     Correlation Engine                                │   │
│  │  • Entity Matching (People, Vehicles, Weapons, Incidents)            │   │
│  │  • Pattern Detection (Temporal, Geographic, Behavioral)              │   │
│  │  • Threat Trajectory Inference                                        │   │
│  │  • Cross-Engine Anomaly Reconciliation                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Rules Engine (Priority Scoring)                  │   │
│  │  • Engine Confidence Scores                                           │   │
│  │  • Entity Risk Profiles                                               │   │
│  │  • Location Risk Index                                                │   │
│  │  • Officer Safety Modifiers                                           │   │
│  │  • Federal Match Multipliers                                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Alerts Router                                  │   │
│  │  Routes to: Dashboard, Tactical, Investigations, Officer Safety,     │   │
│  │            Dispatch, Mobile/MDT, Bulletins, BOLOs                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          ▼                         ▼                         ▼              │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│  │  WebSocket   │         │  Knowledge   │         │   Audit      │        │
│  │  Broadcast   │         │  Graph Sync  │         │    Log       │        │
│  └──────────────┘         └──────────────┘         └──────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Intelligence Sources

The orchestration engine fuses signals from 13 different intelligence sources:

1. **AI Intelligence Engine** - Pattern recognition, anomaly detection, predictive analytics
2. **Tactical Analytics Engine** - Real-time tactical intelligence
3. **Investigations Engine** - Case-related intelligence
4. **Officer Safety Engine** - Threat assessments for officer protection
5. **Dispatch & Communications Engine** - CAD/911 data integration
6. **Federal Integration Layer** - N-DEx, NCIC, eTrace, DHS-SAR
7. **Federation & Multi-Agency Hub** - Cross-agency intelligence sharing
8. **Data Lake & ETL Pipeline** - Historical analytics and trends
9. **External Feeds** - Third-party intelligence sources
10. **Mobile/MDT Systems** - Field officer intelligence
11. **Surveillance Systems** - LPR, video analytics
12. **Social Media Analysis** - Open source intelligence
13. **Tip Lines** - Community intelligence

## Module Structure

```
backend/app/intel_orchestration/
├── __init__.py              # Module exports
├── orchestrator.py          # Master controller
├── pipelines.py             # Intelligence pipelines
├── correlator.py            # Entity correlation engine
├── rules_engine.py          # Priority scoring rules
├── alerts_router.py         # Alert routing layer
├── knowledge_graph_sync.py  # Neo4j synchronization
└── audit_log.py             # CJIS-grade audit logging
```

## Intelligence Pipelines

### Pipeline Types

| Pipeline | Purpose | Latency | Throughput |
|----------|---------|---------|------------|
| Real-Time | Low-latency signal processing | <50ms | High |
| Batch | High-volume analytics | Minutes | Very High |
| Fusion | Cross-engine correlation | <100ms | Medium |
| Alert Priority | Alert scoring and routing | <25ms | High |
| Officer Safety | Critical threat escalation | <10ms | Highest Priority |
| Investigative Lead | Auto-generated leads | <200ms | Medium |
| Data Lake Feedback | Analytics feedback loop | Minutes | High |

### Pipeline Stages

Each pipeline processes signals through these stages:

1. **INGEST** - Receive raw signal from source
2. **NORMALIZE** - Standardize data format
3. **VALIDATE** - Verify data integrity
4. **ENRICH** - Add contextual information
5. **CORRELATE** - Find related entities/patterns
6. **SCORE** - Calculate priority score
7. **ROUTE** - Send to appropriate destinations
8. **COMPLETE** - Mark processing complete

## Correlation Engine

### Entity Types

The correlation engine supports fusion across these entity types:

- **Person** - Individuals with identifying information
- **Vehicle** - Vehicles with plate, VIN, description
- **Weapon** - Firearms and other weapons
- **Incident** - Crime incidents and calls for service
- **Pattern** - Detected behavioral patterns
- **Location** - Geographic points and zones
- **Organization** - Groups, gangs, businesses
- **Case** - Investigation cases
- **Federal Record** - Federal database matches
- **Multi-Agency Entity** - Cross-jurisdiction entities

### Correlation Types

| Type | Description |
|------|-------------|
| EXACT_MATCH | Identical identifier match |
| FUZZY_MATCH | Probabilistic name/attribute match |
| TEMPORAL | Time-based correlation |
| GEOGRAPHIC | Location-based correlation |
| BEHAVIORAL | Pattern-based correlation |
| RELATIONAL | Known relationship |
| TRANSACTIONAL | Transaction/interaction link |
| INVESTIGATIVE | Case-based connection |

### Correlation Strength Levels

- **DEFINITE** (≥0.95) - Confirmed match
- **STRONG** (≥0.80) - High confidence match
- **MODERATE** (≥0.60) - Probable match
- **WEAK** (≥0.40) - Possible match
- **POSSIBLE** (<0.40) - Potential match requiring verification

### Geographic Correlation

Uses Haversine formula for distance calculation:

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

## Priority Scoring System

### Score Range: 0-100

| Score Range | Threat Level | Response |
|-------------|--------------|----------|
| 90-100 | CRITICAL | Immediate action required |
| 70-89 | HIGH | Urgent attention needed |
| 50-69 | MEDIUM | Standard priority |
| 30-49 | LOW | Monitor and track |
| 0-29 | MINIMAL | Informational only |

### Scoring Factors

1. **Engine Confidence** (0-20 points)
   - Based on source engine's confidence score

2. **Entity Risk Profile** (0-25 points)
   - Historical risk assessment of involved entities

3. **Location Risk Index** (0-15 points)
   - Crime density and risk level of location

4. **Officer Safety Modifier** (0-20 points)
   - Threat level to responding officers

5. **Federal Match Multiplier** (1.0-2.0x)
   - Multiplier for federal database matches

6. **Historical Trend Deviation** (0-10 points)
   - Deviation from historical patterns

7. **Intelligence Category Weight** (0-10 points)
   - Category-specific importance

### Default Scoring Rules

```python
DEFAULT_RULES = [
    # Engine confidence scoring
    {"name": "high_confidence", "condition": "confidence >= 0.9", "modifier": 15},
    {"name": "medium_confidence", "condition": "confidence >= 0.7", "modifier": 10},
    
    # Entity risk scoring
    {"name": "high_risk_entity", "condition": "entity_risk >= 80", "modifier": 20},
    {"name": "medium_risk_entity", "condition": "entity_risk >= 50", "modifier": 10},
    
    # Location risk scoring
    {"name": "high_risk_location", "condition": "location_risk >= 0.8", "modifier": 12},
    
    # Officer safety
    {"name": "officer_safety_threat", "condition": "officer_safety_flag", "modifier": 25},
    
    # Federal matches
    {"name": "federal_warrant", "condition": "has_federal_warrant", "multiplier": 1.5},
    {"name": "ncic_hit", "condition": "has_ncic_hit", "multiplier": 1.3},
]
```

## Intelligence Tiers

### Tier 1: Immediate Officer Safety Threat
- **Color Code**: Red
- **Response Time**: Immediate
- **Routing**: Officer Safety Alerts, Dispatch, Mobile/MDT
- **Examples**: Active shooter, armed suspect, officer down

### Tier 2: High-Priority Investigative Lead
- **Color Code**: Orange
- **Response Time**: < 15 minutes
- **Routing**: Investigations Dashboard, Tactical Dashboard
- **Examples**: Federal warrant match, pattern break, hot lead

### Tier 3: Tactical Awareness Signal
- **Color Code**: Yellow
- **Response Time**: < 1 hour
- **Routing**: Tactical Dashboard, RTCC Dashboard
- **Examples**: Suspicious activity, vehicle of interest, area alert

### Tier 4: Informational Intelligence
- **Color Code**: Blue
- **Response Time**: Standard
- **Routing**: RTCC Dashboard, Data Lake
- **Examples**: Trend analysis, historical correlation, statistical anomaly

## Routing Layer

### Destinations

| Destination | Description | Tier Support |
|-------------|-------------|--------------|
| RTCC_DASHBOARD | Main RTCC live feed | All tiers |
| TACTICAL_DASHBOARD | Tactical operations view | 1, 2, 3 |
| INVESTIGATIONS_DASHBOARD | Case management | 2, 3, 4 |
| OFFICER_SAFETY_ALERTS | Critical officer alerts | 1 only |
| DISPATCH_COMMS | CAD/Dispatch overlay | 1, 2 |
| MOBILE_MDT | Field officer devices | 1, 2, 3 |
| COMMAND_CENTER | Command staff view | 1, 2 |
| AUTO_BULLETIN | Automated bulletins | 2, 3 |
| BOLO_GENERATOR | BOLO creation | 1, 2 |
| FEDERAL_SYSTEMS | Federal agency sharing | 1, 2 |
| FEDERATION_HUB | Multi-agency sharing | All tiers |
| DATA_LAKE | Historical storage | All tiers |
| KNOWLEDGE_GRAPH | Neo4j graph database | All tiers |
| AUDIT_LOG | Compliance logging | All tiers |

## WebSocket Channels

### Channel Endpoints

| Channel | Endpoint | Purpose |
|---------|----------|---------|
| Fused Intelligence | `/ws/intel/fused` | Real-time fused intelligence feed |
| Alerts | `/ws/intel/alerts` | High-priority alert notifications |
| Priority Queue | `/ws/intel/priority` | Priority-scored items |
| Pipeline Status | `/ws/intel/pipelines` | Pipeline metrics and status |

### Message Format

```json
{
  "type": "fused_intelligence",
  "channel": "fused",
  "data": {
    "id": "fused-12345",
    "tier": "tier2",
    "title": "Pattern Match - Serial Burglary",
    "summary": "AI detected correlation across 5 incidents",
    "priority_score": 78,
    "confidence": 0.85,
    "sources": ["AI Engine", "Tactical Engine"],
    "entities": [
      {"type": "pattern", "id": "pat-123", "name": "Burglary Series"}
    ],
    "correlations": 5
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "message_id": "msg-67890"
}
```

### Client Message Types

| Type | Description |
|------|-------------|
| `ping` | Keep-alive ping |
| `subscribe` | Subscribe to topics |
| `unsubscribe` | Unsubscribe from topics |
| `acknowledge` | Acknowledge alert |
| `request_status` | Request channel status |

## Knowledge Graph Synchronization

### Node Types

- Person, Vehicle, Weapon, Incident, Location
- Pattern, Organization, Case, Alert, Intelligence

### Relationship Types

- OWNS, DRIVES, POSSESSES, INVOLVED_IN
- LOCATED_AT, ASSOCIATED_WITH, RELATED_TO
- CORRELATED_WITH, PART_OF, GENERATED

### Sync Operations

```python
# Example Cypher query for node creation
MERGE (n:Person {id: $id})
SET n.name = $name,
    n.risk_score = $risk_score,
    n.last_updated = datetime()
RETURN n

# Example relationship creation
MATCH (a:Person {id: $person_id})
MATCH (b:Vehicle {id: $vehicle_id})
MERGE (a)-[r:OWNS]->(b)
SET r.confidence = $confidence,
    r.source = $source
RETURN r
```

## Audit Logging

### CJIS Compliance

The audit log module provides CJIS-grade logging with:

- **Immutable Records**: Hash-chained entries for tamper detection
- **7-Year Retention**: Configurable retention period (default 2555 days)
- **Sensitive Data Masking**: Automatic masking of PII fields
- **Chain Verification**: Cryptographic verification of log integrity

### Audit Actions

| Category | Actions |
|----------|---------|
| Orchestration | initialized, started, stopped, paused, resumed |
| Signal | ingested, processed, dropped, enriched |
| Fusion | created, processed, routed |
| Correlation | found, created, pattern_detected |
| Scoring | priority_calculated, threat_assessed |
| Routing | alert_created, alert_routed, alert_delivered |
| Access | data_accessed, data_exported, data_queried |
| Configuration | config_changed, rule_added, rule_modified |

### Audit Entry Format

```json
{
  "id": "audit-12345",
  "timestamp": "2024-01-15T10:30:00Z",
  "action": "signal_ingested",
  "severity": "info",
  "category": "intelligence",
  "user_id": "user-123",
  "source_system": "intel_orchestration",
  "target_type": "signal",
  "target_id": "sig-67890",
  "details": {
    "source": "ai_engine",
    "category": "pattern"
  },
  "payload_hash": "sha256:abc123...",
  "previous_entry_hash": "sha256:def456...",
  "entry_hash": "sha256:ghi789..."
}
```

## Frontend Components

### Intel Hub Page (`/intel-hub`)

The Intel Hub provides a unified view of all intelligence orchestration activities.

#### Components

1. **FusionFeed** - Real-time fused intelligence stream with tier-based color coding
2. **PriorityQueue** - Priority-scored items requiring attention
3. **SignalGraphView** - Visual representation of signal flow
4. **PipelineStatusView** - Pipeline health and metrics
5. **EntityCorrelationViewer** - Entity relationship visualization
6. **AutoLeadsPanel** - Auto-generated investigative leads

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/intel/status` | Get orchestration status |
| POST | `/api/intel/start` | Start orchestration engine |
| POST | `/api/intel/stop` | Stop orchestration engine |
| POST | `/api/intel/signals` | Ingest new signal |
| POST | `/api/intel/signals/batch` | Batch signal ingestion |
| GET | `/api/intel/pipelines` | Get all pipeline status |
| GET | `/api/intel/pipelines/{name}` | Get specific pipeline |
| POST | `/api/intel/correlations/query` | Query correlations |
| POST | `/api/intel/scoring/calculate` | Calculate priority score |
| GET | `/api/intel/alerts` | Get alerts |
| POST | `/api/intel/alerts` | Create alert |
| GET | `/api/intel/audit/entries` | Query audit log |
| GET | `/api/intel/health` | Health check |

## Configuration

### Orchestration Config

```python
OrchestrationConfig(
    enabled=True,
    max_concurrent_pipelines=10,
    signal_buffer_size=10000,
    batch_size=100,
    batch_interval_seconds=5.0,
    enable_correlation=True,
    enable_priority_scoring=True,
    enable_websocket_broadcast=True,
    enable_audit_logging=True,
    default_jurisdiction="Metro PD",
)
```

### Pipeline Config

```python
PipelineConfig(
    name="real_time_pipeline",
    pipeline_type=PipelineType.REAL_TIME,
    enabled=True,
    workers=8,
    queue_size=1000,
    batch_size=10,
    timeout_seconds=30.0,
    retry_attempts=3,
)
```

## Performance Metrics

### Key Metrics

- **Signals Received**: Total signals ingested
- **Signals Processed**: Successfully processed signals
- **Fusions Created**: Fused intelligence items generated
- **Alerts Routed**: Alerts sent to destinations
- **Processing Latency**: Average signal processing time
- **Throughput**: Signals processed per second
- **Error Rate**: Failed signal percentage

### Monitoring

All metrics are exposed via:
- `/api/intel/metrics` - JSON metrics endpoint
- WebSocket `/ws/intel/pipelines` - Real-time metrics stream
- Audit log entries - Historical performance data

## Security Considerations

1. **Authentication**: All API endpoints require valid JWT tokens
2. **Authorization**: Role-based access control for sensitive operations
3. **Encryption**: TLS for all communications
4. **Audit Trail**: Complete logging of all intelligence access
5. **Data Masking**: Automatic PII masking in logs
6. **Rate Limiting**: Protection against abuse

## Integration Examples

### Ingesting a Signal

```python
from intel_orchestration import IntelOrchestrator, IntelSignal, IntelSource, IntelCategory

orchestrator = IntelOrchestrator()
await orchestrator.start()

signal = IntelSignal(
    source=IntelSource.AI_ENGINE,
    category=IntelCategory.PATTERN,
    jurisdiction="Metro PD",
    confidence=0.85,
    data={
        "pattern_type": "burglary_series",
        "incidents": ["inc-1", "inc-2", "inc-3"],
        "confidence": 0.85,
    },
)

await orchestrator.ingest_signal(signal)
```

### Querying Correlations

```python
from intel_orchestration import CorrelationEngine, EntityReference, EntityType

engine = CorrelationEngine()

entity = EntityReference(
    entity_id="person-123",
    entity_type=EntityType.PERSON,
    attributes={"name": "John Doe", "dob": "1985-03-15"},
)

result = await engine.correlate_entity(entity)
print(f"Found {len(result.entity_correlations)} correlations")
```

### Calculating Priority Score

```python
from intel_orchestration import RulesEngine

engine = RulesEngine()

score = await engine.calculate_priority(
    signal_data={
        "confidence": 0.9,
        "category": "violent_crime",
        "officer_safety_flag": True,
    },
    entity_id="person-123",
)

print(f"Priority Score: {score.total_score}")
print(f"Threat Level: {score.threat_level}")
```

## Troubleshooting

### Common Issues

1. **High Queue Backlog**
   - Increase worker count
   - Check downstream system availability
   - Review batch size settings

2. **Low Correlation Accuracy**
   - Adjust correlation thresholds
   - Review entity attribute quality
   - Check temporal/geographic windows

3. **WebSocket Disconnections**
   - Verify network stability
   - Check connection timeout settings
   - Review server resource utilization

4. **Audit Log Growth**
   - Configure retention policies
   - Enable log rotation
   - Archive old entries to cold storage
