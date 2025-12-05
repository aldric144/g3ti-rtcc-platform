# G3TI RTCC-UIP Data Flow

## Overview

This document describes how data flows through the RTCC-UIP platform, from external sources to end-user interfaces. Understanding these flows is essential for system integration, troubleshooting, and optimization.

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           External Data Sources                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ShotSpotter│ │  Flock   │ │Milestone │ │OneSolut. │ │   CAD    │         │
│  │ Gunshots │ │   LPR    │ │   VMS    │ │   RMS    │ │ Dispatch │         │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘         │
│       │            │            │            │            │                 │
└───────┼────────────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Integration Layer                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Event Normalization                                │   │
│  │                                                                       │   │
│  │  Raw Event ──▶ Validate ──▶ Transform ──▶ Enrich ──▶ Normalized Event│   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Event Processing                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │   Persist   │    │   Index     │    │  Broadcast  │                     │
│  │  to Neo4j   │    │ to Elastic  │    │ via WebSocket│                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Client Applications                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │Dashboard │ │   Map    │ │  Events  │ │ Invest.  │                       │
│  │   View   │ │   View   │ │   Feed   │ │  Search  │                       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Event Ingestion Pipeline

### 1. Source Connection

Each integration maintains a persistent connection to its data source:

```
┌─────────────────┐
│  Data Source    │
│  (e.g., Flock)  │
└────────┬────────┘
         │
         │ Webhook / Polling / Stream
         ▼
┌─────────────────┐
│   Integration   │
│    Adapter      │
└────────┬────────┘
         │
         │ Raw Event
         ▼
┌─────────────────┐
│    Validator    │
└─────────────────┘
```

### 2. Event Normalization

Raw events from different sources are normalized to a common format:

```python
class NormalizedEvent:
    id: str                    # Unique identifier
    event_type: EventType      # Standardized type
    source: EventSource        # Origin system
    priority: EventPriority    # Urgency level
    title: str                 # Human-readable title
    description: str           # Detailed description
    location: GeoLocation      # Lat/lon coordinates
    address: str               # Street address
    timestamp: datetime        # When event occurred
    metadata: dict             # Source-specific data
    tags: list[str]            # Categorization tags
```

### 3. Event Enrichment

Events are enriched with additional context:

```
┌─────────────────┐
│ Normalized Event│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Geocoding       │────▶│ Address Lookup  │
└─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Entity Matching │────▶│ Neo4j Lookup    │
└─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Priority Calc   │────▶│ Rule Engine     │
└─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Enriched Event  │
└─────────────────┘
```

## Real-Time Event Distribution

### WebSocket Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        WebSocket Manager                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. Client Connects                                                       │
│     ┌────────┐                    ┌────────────────┐                     │
│     │ Client │───── WebSocket ───▶│ Connection     │                     │
│     └────────┘                    │ Handler        │                     │
│                                   └───────┬────────┘                     │
│                                           │                               │
│  2. Client Subscribes                     ▼                               │
│     ┌────────────────────────────────────────────────────┐               │
│     │ { type: "subscribe",                                │               │
│     │   payload: { eventTypes: ["gunshot"], ... } }       │               │
│     └────────────────────────────────────────────────────┘               │
│                                           │                               │
│                                           ▼                               │
│                                   ┌───────────────┐                      │
│                                   │ Subscription  │                      │
│                                   │ Registry      │                      │
│                                   └───────────────┘                      │
│                                                                           │
│  3. Event Arrives                                                         │
│     ┌────────────────┐                                                   │
│     │ New Event      │                                                   │
│     └───────┬────────┘                                                   │
│             │                                                             │
│             ▼                                                             │
│     ┌───────────────────────────────────────────────────────────────┐   │
│     │                    Broadcast Manager                           │   │
│     │                                                                │   │
│     │  For each connected client:                                    │   │
│     │    - Check subscription filters                                │   │
│     │    - If match: send event                                      │   │
│     └───────────────────────────────────────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `subscribe` | Client → Server | Subscribe to event filters |
| `unsubscribe` | Client → Server | Remove subscription |
| `acknowledge` | Client → Server | Acknowledge event receipt |
| `ping` | Client → Server | Heartbeat request |
| `event` | Server → Client | New event notification |
| `subscribed` | Server → Client | Subscription confirmation |
| `pong` | Server → Client | Heartbeat response |
| `error` | Server → Client | Error notification |

## Entity Graph Operations

### Creating Entities

```
┌─────────────────┐
│  API Request    │
│  POST /entities │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │
│   (Pydantic)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Authorization  │
│  (RBAC Check)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Neo4j Create   │────▶│  CREATE (n:Type)│
│                 │     │  SET n = props  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Elasticsearch  │────▶│  Index Document │
│  Index          │     │                 │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Audit Log      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Response   │
└─────────────────┘
```

### Querying Entity Networks

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Network Traversal Query                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Input: Entity ID, Depth (1-4)                                          │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  MATCH path = (start)-[*1..{depth}]-(connected)                 │    │
│  │  WHERE start.id = $entity_id                                    │    │
│  │  RETURN nodes(path), relationships(path)                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Output:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  {                                                               │    │
│  │    "nodes": [                                                    │    │
│  │      { "id": "...", "label": "Person", "properties": {...} },   │    │
│  │      { "id": "...", "label": "Vehicle", "properties": {...} }   │    │
│  │    ],                                                            │    │
│  │    "edges": [                                                    │    │
│  │      { "source": "...", "target": "...", "type": "OWNS" }       │    │
│  │    ],                                                            │    │
│  │    "centerNodeId": "..."                                         │    │
│  │  }                                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Search Flow

### Full-Text Search

```
┌─────────────────┐
│  Search Query   │
│  "John Smith"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query Parser   │
│  - Tokenize     │
│  - Analyze      │
│  - Build Query  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Elasticsearch Query                               │
├─────────────────────────────────────────────────────────────────────────┤
│  {                                                                       │
│    "query": {                                                            │
│      "bool": {                                                           │
│        "should": [                                                       │
│          { "match": { "first_name": "John" } },                         │
│          { "match": { "last_name": "Smith" } },                         │
│          { "match": { "aliases": "John Smith" } }                       │
│        ],                                                                │
│        "filter": [                                                       │
│          { "term": { "entity_type": "person" } }                        │
│        ]                                                                 │
│      }                                                                   │
│    },                                                                    │
│    "highlight": { "fields": { "*": {} } }                               │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Search Results │
│  - Ranked hits  │
│  - Highlights   │
│  - Facets       │
└─────────────────┘
```

### Geospatial Search

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Geospatial Query                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Input: Center Point (lat, lon), Radius (miles)                         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  {                                                               │    │
│  │    "query": {                                                    │    │
│  │      "geo_distance": {                                           │    │
│  │        "distance": "5mi",                                        │    │
│  │        "location": { "lat": 29.76, "lon": -95.37 }              │    │
│  │      }                                                           │    │
│  │    },                                                            │    │
│  │    "sort": [                                                     │    │
│  │      { "_geo_distance": { "location": {...}, "order": "asc" } } │    │
│  │    ]                                                             │    │
│  │  }                                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Authentication Flow

### Login Flow

```
┌────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│ Client │────▶│   Login    │────▶│  Validate  │────▶│  Check     │
│        │     │  Request   │     │  Input     │     │  Rate Limit│
└────────┘     └────────────┘     └────────────┘     └─────┬──────┘
                                                           │
                    ┌──────────────────────────────────────┘
                    ▼
              ┌────────────┐     ┌────────────┐     ┌────────────┐
              │  Lookup    │────▶│  Verify    │────▶│  Check     │
              │  User      │     │  Password  │     │  Account   │
              └────────────┘     └────────────┘     │  Status    │
                                                    └─────┬──────┘
                    ┌──────────────────────────────────────┘
                    ▼
              ┌────────────┐     ┌────────────┐     ┌────────────┐
              │  Generate  │────▶│  Log       │────▶│  Return    │
              │  Tokens    │     │  Audit     │     │  Tokens    │
              └────────────┘     └────────────┘     └────────────┘
```

### Token Refresh Flow

```
┌────────┐     ┌────────────┐     ┌────────────┐
│ Client │────▶│  Refresh   │────▶│  Validate  │
│        │     │  Request   │     │  Refresh   │
└────────┘     └────────────┘     │  Token     │
                                  └─────┬──────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
              ┌────────────┐                         ┌────────────┐
              │  Valid     │                         │  Invalid   │
              │  Token     │                         │  Token     │
              └─────┬──────┘                         └─────┬──────┘
                    │                                       │
                    ▼                                       ▼
              ┌────────────┐                         ┌────────────┐
              │  Generate  │                         │  Return    │
              │  New Tokens│                         │  401 Error │
              └────────────┘                         └────────────┘
```

## Audit Logging Flow

### Audit Event Creation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Audit Log Entry                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Every significant action generates an audit log:                        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  {                                                               │    │
│  │    "timestamp": "2024-01-15T10:30:00Z",                         │    │
│  │    "event_type": "ENTITY_ACCESS",                               │    │
│  │    "user_id": "user-123",                                       │    │
│  │    "username": "jsmith",                                        │    │
│  │    "role": "detective",                                         │    │
│  │    "action": "VIEW",                                            │    │
│  │    "resource_type": "Person",                                   │    │
│  │    "resource_id": "person-456",                                 │    │
│  │    "ip_address": "192.168.1.100",                               │    │
│  │    "user_agent": "Mozilla/5.0...",                              │    │
│  │    "success": true,                                             │    │
│  │    "details": { "fields_accessed": ["name", "dob"] }            │    │
│  │  }                                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Storage:                                                                │
│  - Elasticsearch (searchable, analytics)                                │
│  - File system (backup, compliance)                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Background Task Flow

### Celery Task Processing

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  API Request    │────▶│  Create Task    │────▶│  Redis Queue    │
│  (Async Job)    │     │                 │     │  (Broker)       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Celery Worker  │
                                                │  - Pick Task    │
                                                │  - Execute      │
                                                │  - Store Result │
                                                └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Redis Result   │
                                                │  Backend        │
                                                └─────────────────┘
```

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `cleanup_expired_tokens` | Every hour | Remove expired JWT tokens |
| `sync_integrations` | Every 5 min | Poll external systems |
| `generate_reports` | Daily 2 AM | Generate daily reports |
| `archive_old_events` | Weekly | Archive events older than 90 days |

## Data Retention

### Retention Policies

| Data Type | Retention Period | Archive Strategy |
|-----------|------------------|------------------|
| Events | 90 days active | Archive to cold storage |
| Audit Logs | 7 years | Immutable storage |
| Investigations | Indefinite | Regular backups |
| Session Data | 24 hours | Auto-expire |
| Cache | 1 hour | Auto-expire |
