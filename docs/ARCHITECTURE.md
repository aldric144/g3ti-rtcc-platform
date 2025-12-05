# G3TI RTCC-UIP Architecture

## Overview

The Real Time Crime Center Unified Intelligence Platform (RTCC-UIP) is a comprehensive law enforcement intelligence system designed to aggregate, analyze, and present real-time data from multiple sources. This document describes the system architecture, component interactions, and design decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RTCC-UIP Platform                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Frontend (Next.js 14)                        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │  Login   │ │Dashboard │ │   Map    │ │ Invest.  │ │  Events  │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │              State Management (Zustand)                      │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │         API Client / WebSocket Client                        │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                    ┌───────────────┴───────────────┐                        │
│                    │         REST API              │                        │
│                    │        WebSocket              │                        │
│                    └───────────────┬───────────────┘                        │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       Backend (FastAPI)                              │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                      API Layer                                │   │    │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │   │    │
│  │  │  │  Auth  │ │Entities│ │Realtime│ │ Invest │ │ System │     │   │    │
│  │  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    Service Layer                              │   │    │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │   │    │
│  │  │  │  Auth  │ │ Graph  │ │ Search │ │ Events │ │   AI   │     │   │    │
│  │  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                  Integration Layer                            │   │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │   │    │
│  │  │  │Milestone│ │  Flock  │ │ShotSpot │ │OneSolut │ ...        │   │    │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│  ┌────────┴────────┐    ┌─────────┴─────────┐    ┌────────┴────────┐       │
│  │     Neo4j       │    │   Elasticsearch   │    │     Redis       │       │
│  │  Graph Database │    │   Search Engine   │    │  Cache/PubSub   │       │
│  └─────────────────┘    └───────────────────┘    └─────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Overview

### Frontend (Next.js 14)

The frontend is built with Next.js 14 using the App Router pattern. It provides a responsive, real-time interface for RTCC operators.

**Key Features:**
- Server-side rendering for initial page loads
- Client-side navigation for smooth transitions
- Real-time updates via WebSocket
- Interactive map with Mapbox GL
- Role-based UI rendering

**Directory Structure:**
```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard page
│   ├── map/               # Geospatial map page
│   ├── investigations/    # Investigation search
│   ├── login/             # Authentication
│   └── components/        # Shared components
├── lib/                   # Utilities and services
│   ├── api/              # API client
│   ├── store/            # Zustand state stores
│   └── websocket/        # WebSocket client
├── styles/               # Global styles
└── public/               # Static assets
```

### Backend (FastAPI)

The backend is built with FastAPI, providing high-performance async APIs with automatic OpenAPI documentation.

**Key Features:**
- Async request handling
- JWT-based authentication
- Role-based access control (RBAC)
- WebSocket support for real-time events
- Comprehensive audit logging

**Directory Structure:**
```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth/        # Authentication endpoints
│   │   ├── entities/    # Entity CRUD operations
│   │   ├── investigations/  # Investigation search
│   │   ├── realtime/    # WebSocket & events
│   │   └── system/      # Health & system info
│   ├── core/            # Core configuration
│   ├── db/              # Database managers
│   ├── schemas/         # Pydantic models
│   ├── services/        # Business logic
│   ├── integrations/    # External system connectors
│   └── utils/           # Utility functions
└── tests/               # Test suite
```

### Data Layer

#### Neo4j (Graph Database)

Neo4j stores entity relationships, enabling complex graph queries for investigative analysis.

**Entity Types:**
- Person
- Vehicle
- Incident
- Weapon
- ShellCasing
- Address
- Camera
- LicensePlate

**Relationship Types:**
- SUSPECT_IN, VICTIM_IN, WITNESS_IN
- OWNS, DRIVES, RESIDES_AT
- OCCURRED_AT, LINKED_TO, ASSOCIATED_WITH
- CAPTURED_BY, USED_IN

#### Elasticsearch

Elasticsearch provides full-text search and analytics capabilities.

**Indices:**
- `rtcc_investigations` - Investigation cases
- `rtcc_incidents` - Incident records
- `rtcc_persons` - Person records
- `rtcc_audit_logs` - Audit trail

#### Redis

Redis serves multiple purposes:
- Session caching
- Rate limiting
- Pub/Sub for real-time events
- Background task queue (Celery broker)

## Authentication & Authorization

### JWT Token Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  Login   │────▶│  Verify  │
└──────────┘     │ Endpoint │     │ Password │
                 └──────────┘     └────┬─────┘
                                       │
                      ┌────────────────┘
                      ▼
              ┌──────────────┐
              │ Generate JWT │
              │ Access Token │
              │Refresh Token │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │   Return     │
              │   Tokens     │
              └──────────────┘
```

### Role Hierarchy

```
admin (5)
  └── supervisor (4)
        └── detective (3)
              └── rtcc_analyst (2)
                    └── officer (1)
```

Higher roles inherit all permissions of lower roles.

## Real-Time Event System

### WebSocket Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Manager                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Client Registry │    │ Subscription    │                │
│  │                 │    │ Manager         │                │
│  │ - Connection ID │    │ - Event Types   │                │
│  │ - User Info     │    │ - Sources       │                │
│  │ - Subscriptions │    │ - Priorities    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Broadcast Manager                       │   │
│  │                                                      │   │
│  │  Event ──▶ Filter by Subscription ──▶ Send to Client │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Event Flow

1. External system generates event (e.g., ShotSpotter alert)
2. Integration adapter normalizes event to standard format
3. Event processor validates and enriches event
4. Broadcast manager distributes to subscribed clients
5. Clients receive event via WebSocket

## Integration Architecture

### Adapter Pattern

Each external system has a dedicated integration adapter:

```python
class BaseIntegration(ABC):
    @abstractmethod
    async def connect(self) -> bool: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
    
    @abstractmethod
    def normalize_event(self, raw_event: dict) -> NormalizedEvent: ...
```

### Supported Integrations

| System | Type | Description |
|--------|------|-------------|
| Milestone XProtect | VMS | Video management system |
| Flock Safety | LPR | License plate recognition |
| ShotSpotter | Gunshot | Acoustic gunshot detection |
| OneSolution | RMS | Records management system |
| NESS | NCIC | National crime database |
| BWC | Video | Body-worn camera system |
| HotSheets | BOLO | Be-on-lookout lists |

## Deployment Architecture

### Docker Compose (Development)

```yaml
services:
  backend:     # FastAPI application
  frontend:    # Next.js application
  neo4j:       # Graph database
  elasticsearch: # Search engine
  redis:       # Cache & message broker
  celery-worker: # Background tasks
  celery-beat:   # Scheduled tasks
```

### Production Considerations

- Load balancer for horizontal scaling
- Kubernetes for container orchestration
- Separate database clusters
- CDN for static assets
- WAF for security

## Security Architecture

### Defense in Depth

1. **Network Layer**: Firewall, VPN, network segmentation
2. **Application Layer**: Authentication, authorization, input validation
3. **Data Layer**: Encryption at rest, encryption in transit
4. **Audit Layer**: Comprehensive logging, anomaly detection

### CJIS Compliance

The platform is designed to meet CJIS Security Policy requirements:
- Advanced authentication (MFA support)
- Encryption (AES-256, TLS 1.3)
- Audit logging (all access logged)
- Session management (automatic timeout)
- Access control (role-based)

## Performance Considerations

### Caching Strategy

- **L1 Cache**: In-memory (application level)
- **L2 Cache**: Redis (distributed)
- **Query Cache**: Elasticsearch query caching

### Optimization Techniques

- Connection pooling for databases
- Async I/O for non-blocking operations
- Batch processing for bulk operations
- Pagination for large result sets
- WebSocket for real-time updates (vs polling)

## Monitoring & Observability

### Metrics

- Request latency (P50, P95, P99)
- Error rates by endpoint
- Database query performance
- WebSocket connection count
- Integration health status

### Logging

- Structured JSON logging
- Correlation IDs for request tracing
- Audit logs for compliance
- Error logs with stack traces

### Health Checks

- `/api/v1/system/health` - Overall health
- `/api/v1/system/health/live` - Liveness probe
- `/api/v1/system/health/ready` - Readiness probe

## Future Considerations

### Planned Enhancements

1. **AI/ML Integration**: Predictive analytics, anomaly detection
2. **Mobile Support**: Native mobile applications
3. **Multi-tenancy**: Support for multiple agencies
4. **Federation**: Cross-agency data sharing
5. **Advanced Analytics**: Crime pattern analysis, hotspot prediction
