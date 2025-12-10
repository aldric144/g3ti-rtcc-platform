# Phase 14: Operational Continuity Engine

## Overview

Phase 14 implements the Operational Continuity Engine for the G3TI RTCC-UIP platform, providing 24/7 mission-critical stability through redundancy, failover, health checks, diagnostics, and distributed uptime guarantees.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RTCC Operations Center                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Health Grid │  │  Latency    │  │  Failover   │  │  Vendor     │        │
│  │             │  │  Panel      │  │  Status     │  │  Map        │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │ Diagnostics │  │  Uptime     │  │  Alerts     │                         │
│  │ Timeline    │  │  Analytics  │  │  Feed       │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WebSocket Channels                                   │
│  /ws/ops/health    /ws/ops/failover    /ws/ops/diagnostics                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REST API Endpoints                                   │
│  /api/ops/health         /api/ops/failover/status                           │
│  /api/ops/health/deep    /api/ops/redundancy/status                         │
│  /api/ops/diagnostics/report    /api/ops/audit/logs                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Operational Continuity Engine                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │ Health Check  │  │   Failover    │  │  Redundancy   │                   │
│  │   Service     │  │   Manager     │  │   Manager     │                   │
│  └───────────────┘  └───────────────┘  └───────────────┘                   │
│  ┌───────────────┐  ┌───────────────┐                                       │
│  │  Diagnostics  │  │  Ops Audit    │                                       │
│  │    Engine     │  │     Log       │                                       │
│  └───────────────┘  └───────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Monitored Services                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │  Neo4j  │  │Elastic- │  │  Redis  │  │Postgres │  │   WS    │          │
│  │ Primary │  │ search  │  │ Primary │  │         │  │ Broker  │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │  Neo4j  │  │  Redis  │  │  N-DEx  │  │  NCIC   │  │ eTrace  │          │
│  │Secondary│  │Secondary│  │ Federal │  │ Federal │  │ Federal │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Health Check Service (`healthchecks.py`)

Deep service monitoring for all RTCC infrastructure components.

**Monitored Services:**
- Neo4j (Primary & Secondary)
- Elasticsearch Cluster
- Redis (Primary & Secondary)
- PostgreSQL
- WebSocket Broker
- Federal Endpoints (N-DEx, NCIC, eTrace, DHS-SAR)
- Vendor Integrations (LPR, ShotSpotter, CAD, RMS)
- Internal Engines (AI, Tactical, Intel Orchestrator)

**Features:**
- Latency metrics with configurable thresholds
- Rolling 1h/24h health snapshots
- Uptime percentage tracking
- Consecutive failure detection
- Service-specific health checks

**Configuration:**
```python
HealthConfig(
    check_interval_seconds=30,
    latency_threshold_ms=1000,
    failure_threshold=3,
    snapshot_retention_hours=24,
)
```

### 2. Failover Manager (`failover_manager.py`)

Automatic detection and handling of service failures.

**Capabilities:**
- Auto-detection of failing services
- Fallback routing (e.g., Redis → in-memory cache)
- Queue buffering during outages
- Health-based service switching
- Manual failover/recovery triggers

**Failover States:**
- `normal`: All services operational
- `degraded`: Some services using fallbacks
- `failover`: Active failover in progress
- `emergency`: Multiple critical failures

**Example Failover Flow:**
```
1. Health check detects Neo4j primary failure
2. Failover manager receives health update
3. Consecutive failures exceed threshold (3)
4. Automatic failover to Neo4j secondary
5. Operations buffered during transition
6. WebSocket broadcast: failover_activated
7. Audit log entry created
8. Recovery monitoring begins
```

### 3. Redundancy Manager (`redundancy_manager.py`)

Hot/warm standby support with connection pool management.

**Features:**
- Primary/secondary connection pools
- Automatic reconnection logic
- State synchronization across redundant services
- Manual failover/failback controls

**Redundancy Modes:**
- `hot`: Secondary always connected, instant failover
- `warm`: Secondary on standby, quick activation
- `cold`: Secondary offline, manual activation required

**Connection Pool States:**
- `disconnected`: Not connected
- `connecting`: Connection in progress
- `connected`: Active and healthy
- `failed`: Connection failed
- `draining`: Graceful shutdown

### 4. Diagnostics Engine (`diagnostics.py`)

Comprehensive RTCC diagnostics suite.

**Capabilities:**
- Error classification (network/database/federal/vendor/internal)
- Predictive failure detection
- Slow query detection and analysis
- Escalation rule processing

**Diagnostic Categories:**
- `network`: Connection timeouts, DNS failures
- `database`: Query errors, connection pool exhaustion
- `federal`: N-DEx/NCIC/eTrace API failures
- `vendor`: Third-party integration issues
- `internal`: Application errors, memory issues

**Severity Levels:**
- `info`: Informational events
- `warning`: Potential issues requiring attention
- `error`: Errors affecting functionality
- `critical`: Critical failures requiring immediate action

**Predictive Analysis:**
```python
# Example predictive alert
PredictiveAlert(
    category=DiagnosticCategory.DATABASE,
    prediction_type="connection_exhaustion",
    confidence=0.78,
    predicted_failure_time=datetime.now() + timedelta(hours=1),
    indicators=[
        "Connection pool growth rate: 15%/hour",
        "Current utilization: 75%",
        "Historical pattern match: 82%",
    ],
    recommended_actions=[
        "Increase connection pool size",
        "Review connection leak sources",
        "Enable connection timeout",
    ],
)
```

### 5. Ops Audit Log (`ops_audit_log.py`)

CJIS-aligned operational audit trail.

**Features:**
- Chain-verified audit entries
- Sensitive data masking
- Retention policy enforcement
- Compliance report generation

**Audit Actions:**
- `health_check`: Health check performed
- `failover_activated`: Failover triggered
- `failover_recovered`: Service recovered
- `redundancy_sync`: State synchronized
- `diagnostic_event`: Diagnostic logged
- `escalation`: Alert escalated
- `manual_intervention`: Manual action taken
- `config_change`: Configuration modified

**Chain Verification:**
Each audit entry includes a hash of the previous entry, creating a tamper-evident chain:
```python
entry.chain_hash = hashlib.sha256(
    f"{prev_entry.entry_id}:{prev_entry.timestamp}:{prev_entry.action}"
).hexdigest()
```

## API Endpoints

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ops/health` | GET | Current health summary |
| `/api/ops/health/deep` | GET | Detailed health check |
| `/api/ops/health/service/{type}` | GET | Service-specific health |
| `/api/ops/health/snapshots` | GET | Historical snapshots |

### Failover Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ops/failover/status` | GET | Current failover status |
| `/api/ops/failover/trigger/{type}` | POST | Manual failover |
| `/api/ops/failover/recover/{type}` | POST | Manual recovery |

### Redundancy Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ops/redundancy/status` | GET | Redundancy status |
| `/api/ops/redundancy/pool/{name}` | GET | Pool details |
| `/api/ops/redundancy/failover/{pool}` | POST | Pool failover |
| `/api/ops/redundancy/failback/{pool}` | POST | Pool failback |

### Diagnostics Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ops/diagnostics/report` | GET | Diagnostics report |
| `/api/ops/diagnostics/events` | GET | Diagnostic events |
| `/api/ops/diagnostics/slow-queries` | GET | Slow query events |
| `/api/ops/diagnostics/alerts` | GET | Predictive alerts |

### Audit Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ops/audit/logs` | GET | Audit log entries |
| `/api/ops/audit/report` | GET | Compliance report |
| `/api/ops/audit/status` | GET | Audit service status |

## WebSocket Channels

### `/ws/ops/health`
Real-time health status updates.

**Event Types:**
- `health_update`: Full health snapshot
- `service_status_change`: Individual service change
- `service_degraded`: Service degradation
- `service_failure`: Service failure

### `/ws/ops/failover`
Failover and recovery events.

**Event Types:**
- `failover_event`: Failover state change
- `failover_activated`: Failover triggered
- `recovery_completed`: Service recovered
- `emergency_state`: Multiple failures

### `/ws/ops/diagnostics`
Diagnostic events and alerts.

**Event Types:**
- `diagnostic_event`: New diagnostic
- `slow_query`: Slow query detected
- `predictive_alert`: Failure prediction
- `vendor_unavailable`: Vendor offline
- `federal_interruption`: Federal feed issue
- `etl_stall`: ETL pipeline stall

## Alerting Rules

### Escalation Thresholds

| Condition | Severity | Action |
|-----------|----------|--------|
| Service unresponsive > 10s | Degraded | Yellow alert |
| 2+ dependencies failed | Critical | Red alert |
| Federal endpoint offline > 5min | Priority 1 | Command Center |
| Neo4j write failure | Emergency | All dashboards |
| ETL pipeline stall | High | Ops Center |
| WebSocket drop > 20% | Degraded | Yellow alert |

### Alert Routing

- **RTCC Live Dashboard**: All alerts
- **Ops Center Page**: All alerts
- **Tactical Dashboard**: Critical and above
- **Command Center**: Tier 1 only

## Uptime SLAs

| Service Category | Target SLA | Measurement Period |
|------------------|------------|-------------------|
| Core Infrastructure | 99.99% | Monthly |
| Federal Integrations | 99.5% | Monthly |
| Vendor Integrations | 99.0% | Monthly |
| Internal Engines | 99.9% | Monthly |

## Recovery Sequences

### Database Failover Recovery

```
1. Detect primary failure (3 consecutive checks)
2. Activate secondary connection pool
3. Buffer pending write operations
4. Switch read traffic to secondary
5. Replay buffered operations
6. Monitor secondary health
7. Attempt primary reconnection
8. Sync state when primary recovers
9. Gradual traffic migration back
10. Deactivate failover mode
```

### Federal Endpoint Recovery

```
1. Detect federal endpoint failure
2. Enable queue buffering
3. Notify federal liaison (if > 5min)
4. Retry with exponential backoff
5. Switch to degraded mode
6. Process buffered requests on recovery
7. Verify data consistency
8. Resume normal operations
```

### ETL Pipeline Recovery

```
1. Detect pipeline stall
2. Identify stall point
3. Checkpoint current state
4. Restart pipeline from checkpoint
5. Process backlog
6. Verify data integrity
7. Resume normal ingestion
```

## Runbook

### Service Degradation

1. Check `/api/ops/health/deep` for affected services
2. Review `/api/ops/diagnostics/events` for root cause
3. If database: Check connection pool utilization
4. If federal: Verify network connectivity
5. If vendor: Contact vendor support
6. Monitor recovery via WebSocket channels

### Manual Failover

1. Verify secondary service health
2. POST to `/api/ops/failover/trigger/{service}`
3. Monitor failover progress
4. Verify application functionality
5. Document reason in audit log

### Emergency Response

1. Identify affected services
2. Activate incident response team
3. Enable emergency mode if needed
4. Prioritize critical operations
5. Communicate status to stakeholders
6. Document all actions in audit log

## Docker Configuration

### Healthcheck Directives

All services include Docker healthchecks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/ops/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Redundancy Profile

Enable redundancy services:

```bash
docker compose --profile redundancy up -d
```

### Monitoring Profile

Enable ops monitoring:

```bash
docker compose --profile monitoring up -d
```

## Testing

### Test Suites

1. **Health Check Tests**: Service monitoring validation
2. **Failover Tests**: Failover activation and recovery
3. **Redundancy Tests**: Connection pool management
4. **Diagnostics Tests**: Error classification and prediction
5. **Audit Log Tests**: Chain verification and compliance
6. **API Tests**: Endpoint functionality
7. **WebSocket Tests**: Real-time event broadcasting
8. **Integration Tests**: End-to-end scenarios

### Running Tests

```bash
# All ops continuity tests
pytest tests/ops_continuity/ -v

# Specific module
pytest tests/ops_continuity/test_healthchecks.py -v

# With coverage
pytest tests/ops_continuity/ --cov=app/ops_continuity
```

## Frontend Components

### Operations Center Page (`/operations-center`)

- **HealthGrid**: Service health status grid
- **ServiceLatencyPanel**: Latency monitoring charts
- **FailoverStatusCard**: Failover state and controls
- **VendorIntegrationMap**: Vendor connection status
- **DiagnosticsTimeline**: Diagnostic event timeline
- **UptimeAnalytics**: Uptime metrics and SLA compliance
- **OpsAlertsFeed**: Real-time alerts feed

### Status Colors

- **Green**: Optimal/Healthy
- **Yellow**: Degraded/Warning
- **Red**: Outage/Critical
- **Grey**: Offline/Not Configured

### Alert Tiers

- **Tier 1**: Immediate officer safety threat
- **Tier 2**: High-priority investigative lead
- **Tier 3**: Tactical awareness signal
- **Tier 4**: Informational intelligence

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPS_HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | 30 |
| `OPS_FAILOVER_THRESHOLD` | Failures before failover | 3 |
| `OPS_REDUNDANCY_MODE` | Redundancy mode (hot/warm/cold) | hot |
| `OPS_ALERT_WEBHOOK_URL` | Alert webhook URL | - |
| `NEO4J_SECONDARY_URI` | Secondary Neo4j URI | - |
| `REDIS_SECONDARY_URL` | Secondary Redis URL | - |

## Metrics

### Health Metrics

- `total_checks`: Total health checks performed
- `failed_checks`: Failed health checks
- `avg_latency_ms`: Average service latency
- `uptime_percent`: Overall uptime percentage

### Failover Metrics

- `total_failovers`: Total failover events
- `auto_failovers`: Automatic failovers
- `manual_failovers`: Manual failovers
- `avg_recovery_time_seconds`: Average recovery time

### Diagnostics Metrics

- `total_events`: Total diagnostic events
- `events_by_category`: Events per category
- `events_by_severity`: Events per severity
- `slow_queries_detected`: Slow queries found
- `predictive_alerts_generated`: Predictions made

### Audit Metrics

- `total_entries`: Total audit entries
- `entries_by_action`: Entries per action
- `entries_by_severity`: Entries per severity
- `chain_verified`: Chain integrity status
