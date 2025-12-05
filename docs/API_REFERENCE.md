# G3TI RTCC-UIP API Reference

## Overview

The RTCC-UIP API is a RESTful API built with FastAPI. This document provides a comprehensive reference for all available endpoints.

**Base URL**: `http://localhost:8000/api/v1`

**Interactive Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

All API endpoints (except login) require JWT authentication.

### Headers

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days

---

## Auth Endpoints

### POST /auth/login

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "mfa_code": "string (optional)"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401`: Invalid credentials
- `403`: Account locked
- `422`: Validation error

---

### POST /auth/refresh

Refresh access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### POST /auth/logout

Invalidate current session.

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

### GET /auth/me

Get current user profile.

**Response (200):**
```json
{
  "id": "user-123",
  "username": "jsmith",
  "email": "jsmith@agency.gov",
  "first_name": "John",
  "last_name": "Smith",
  "badge_number": "12345",
  "department": "Investigations",
  "role": "detective",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

---

### PUT /auth/me

Update current user profile.

**Request Body:**
```json
{
  "email": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}
```

---

### POST /auth/me/password

Change password.

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

---

## User Management (Admin Only)

### GET /auth/users

List all users.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `role`: Filter by role
- `is_active`: Filter by active status

**Response (200):**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

---

### POST /auth/users

Create new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "badge_number": "string (optional)",
  "department": "string (optional)",
  "role": "officer|rtcc_analyst|detective|supervisor|admin"
}
```

---

### GET /auth/users/{user_id}

Get user by ID.

---

### PUT /auth/users/{user_id}

Update user.

---

### DELETE /auth/users/{user_id}

Deactivate user.

---

## Entity Endpoints

### GET /entities/{entity_type}

List entities of a specific type.

**Path Parameters:**
- `entity_type`: person, vehicle, incident, weapon, shell_casing, address, camera, license_plate

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `sort_by`: Field to sort by
- `sort_order`: asc or desc

---

### POST /entities/{entity_type}

Create new entity.

**Request Body (Person example):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "aliases": ["Johnny D"],
  "identifiers": ["SSN-XXX-XX-1234"]
}
```

---

### GET /entities/{entity_type}/{entity_id}

Get entity by ID.

**Response (200):**
```json
{
  "id": "person-123",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### PUT /entities/{entity_type}/{entity_id}

Update entity.

---

### DELETE /entities/{entity_type}/{entity_id}

Delete entity.

---

### GET /entities/{entity_type}/{entity_id}/relationships

Get entity relationships.

**Response (200):**
```json
{
  "relationships": [
    {
      "type": "OWNS",
      "direction": "outgoing",
      "target_type": "Vehicle",
      "target_id": "vehicle-456",
      "properties": {}
    }
  ]
}
```

---

### POST /entities/{entity_type}/{entity_id}/relationships

Create relationship.

**Request Body:**
```json
{
  "relationship_type": "OWNS",
  "target_type": "Vehicle",
  "target_id": "vehicle-456",
  "properties": {}
}
```

---

### GET /entities/{entity_type}/{entity_id}/network

Get entity network (graph traversal).

**Query Parameters:**
- `depth`: Traversal depth (1-4, default: 2)

**Response (200):**
```json
{
  "nodes": [
    {
      "id": "person-123",
      "label": "Person",
      "properties": {"name": "John Doe"}
    },
    {
      "id": "vehicle-456",
      "label": "Vehicle",
      "properties": {"plate": "ABC-1234"}
    }
  ],
  "edges": [
    {
      "source": "person-123",
      "target": "vehicle-456",
      "type": "OWNS",
      "properties": {}
    }
  ],
  "center_node_id": "person-123"
}
```

---

### POST /entities/{entity_type}/search

Search entities.

**Request Body:**
```json
{
  "query": "John Doe",
  "filters": {
    "date_of_birth_from": "1980-01-01",
    "date_of_birth_to": "2000-12-31"
  },
  "page": 1,
  "page_size": 20
}
```

---

## Investigation Endpoints

### POST /investigations/search

Search investigations.

**Request Body:**
```json
{
  "query": "robbery downtown",
  "entity_types": ["incident", "person"],
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "location": {
    "latitude": 29.7604,
    "longitude": -95.3698
  },
  "radius_miles": 5,
  "page": 1,
  "page_size": 20
}
```

**Response (200):**
```json
{
  "query": "robbery downtown",
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3,
  "items": [
    {
      "id": "incident-123",
      "entity_type": "incident",
      "title": "Armed Robbery - 123 Main St",
      "description": "...",
      "score": 0.95,
      "highlights": {
        "description": ["<em>robbery</em> at <em>downtown</em> location"]
      }
    }
  ],
  "facets": {
    "entity_type": {"incident": 30, "person": 15},
    "status": {"open": 20, "closed": 25}
  },
  "suggestions": ["robbery suspect", "downtown incidents"],
  "took_ms": 45
}
```

---

### GET /investigations

List investigations.

---

### POST /investigations

Create investigation.

---

### GET /investigations/{investigation_id}

Get investigation details.

---

### PUT /investigations/{investigation_id}

Update investigation.

---

## Real-Time Endpoints

### WebSocket /realtime/ws/events

Connect to real-time event stream.

**Query Parameters:**
- `token`: JWT access token

**Message Types (Client → Server):**

Subscribe:
```json
{
  "type": "subscribe",
  "payload": {
    "event_types": ["gunshot", "lpr_hit"],
    "sources": ["shotspotter", "flock"],
    "priorities": ["critical", "high"]
  }
}
```

Unsubscribe:
```json
{
  "type": "unsubscribe",
  "payload": {}
}
```

Acknowledge:
```json
{
  "type": "acknowledge",
  "payload": {
    "event_id": "event-123",
    "notes": "Dispatched unit 42"
  }
}
```

Ping:
```json
{
  "type": "ping",
  "payload": {}
}
```

**Message Types (Server → Client):**

Event:
```json
{
  "type": "event",
  "payload": {
    "id": "event-123",
    "event_type": "gunshot",
    "source": "shotspotter",
    "priority": "critical",
    "title": "Gunshot Detected",
    "description": "3 rounds detected",
    "location": {"latitude": 29.76, "longitude": -95.37},
    "address": "1200 Main St",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

---

### GET /realtime/events

Get recent events.

**Query Parameters:**
- `event_types`: Comma-separated event types
- `sources`: Comma-separated sources
- `priorities`: Comma-separated priorities
- `acknowledged`: true/false
- `start_time`: ISO datetime
- `end_time`: ISO datetime
- `page`: Page number
- `page_size`: Items per page

---

### GET /realtime/events/{event_id}

Get event details.

---

### POST /realtime/events/{event_id}/acknowledge

Acknowledge event.

**Request Body:**
```json
{
  "notes": "string (optional)"
}
```

---

### GET /realtime/stats

Get real-time statistics.

**Response (200):**
```json
{
  "connected_clients": 15,
  "events_last_hour": 127,
  "events_by_type": {
    "gunshot": 3,
    "lpr_hit": 45,
    "camera_alert": 79
  },
  "events_by_priority": {
    "critical": 5,
    "high": 22,
    "medium": 50,
    "low": 50
  }
}
```

---

## System Endpoints

### GET /system/health

Get system health status.

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "neo4j": {"status": "healthy"},
    "elasticsearch": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

---

### GET /system/health/live

Liveness probe (Kubernetes).

**Response (200):**
```json
{
  "status": "alive"
}
```

---

### GET /system/health/ready

Readiness probe (Kubernetes).

**Response (200):**
```json
{
  "status": "ready"
}
```

---

### GET /system/info

Get system information.

**Response (200):**
```json
{
  "name": "G3TI RTCC-UIP",
  "version": "1.0.0",
  "environment": "production",
  "api_version": "v1"
}
```

---

### GET /system/config (Admin Only)

Get system configuration.

---

### GET /system/metrics (Admin Only)

Get system metrics.

**Response (200):**
```json
{
  "uptime_seconds": 86400,
  "request_count": 125000,
  "error_count": 150,
  "active_connections": 45,
  "database_connections": {
    "neo4j": 10,
    "elasticsearch": 5,
    "redis": 20
  }
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "error": "Invalid email format"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-123"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid username or password |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `INVALID_TOKEN` | 401 | JWT token is invalid |
| `ACCOUNT_LOCKED` | 403 | Account is locked |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required role |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `DUPLICATE` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| POST /auth/login | 5/minute |
| General API | 100/minute |
| Search endpoints | 30/minute |
| Export endpoints | 10/hour |

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312200
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (1-indexed)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "items": [...],
  "total": 500,
  "page": 1,
  "page_size": 20,
  "pages": 25
}
```

---

## Filtering & Sorting

### Filtering

Most list endpoints support filtering via query parameters:

```
GET /entities/person?gender=male&is_active=true
```

### Sorting

```
GET /entities/person?sort_by=last_name&sort_order=asc
```

---

## Versioning

The API is versioned via URL path:

- Current version: `/api/v1`
- Future versions: `/api/v2`, etc.

The `Accept` header can also specify version:
```
Accept: application/vnd.rtcc.v1+json
```
