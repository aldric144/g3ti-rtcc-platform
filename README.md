# G3TI RTCC-UIP

**Real Time Crime Center Unified Intelligence Platform**

A comprehensive law enforcement intelligence platform for real-time situational awareness, investigative analysis, and multi-source data integration.

## Overview

The RTCC-UIP platform aggregates data from multiple sources including video management systems, license plate recognition, gunshot detection, records management systems, and more. It provides a unified interface for RTCC analysts, detectives, and officers to monitor events, investigate incidents, and analyze entity relationships.

## Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance async API framework
- **Neo4j** - Graph database for entity relationships
- **Elasticsearch** - Full-text search and analytics
- **Redis** - Caching, rate limiting, and pub/sub
- **Celery** - Background task processing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS framework
- **Mapbox GL** - Interactive geospatial maps
- **Zustand** - Lightweight state management

### DevOps
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Pre-commit** - Code quality hooks

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Poetry (Python package manager)

### Running with Docker

1. Clone the repository:
```bash
git clone https://github.com/your-org/g3ti-rtcc-platform.git
cd g3ti-rtcc-platform
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

### Local Development

#### Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
g3ti-rtcc-platform/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database managers
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── integrations/   # External system connectors
│   │   └── utils/          # Utility functions
│   └── tests/              # Test suite
├── frontend/               # Next.js frontend application
│   ├── app/               # App Router pages
│   ├── lib/               # Utilities and services
│   └── styles/            # Global styles
├── shared/                 # Shared TypeScript schemas
├── docs/                   # Documentation
└── docker-compose.yml      # Docker configuration
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [Data Flow](docs/DATAFLOW.md) - Event and data pipeline documentation
- [Security & CJIS](docs/SECURITY_CJIS.md) - Security measures and compliance
- [Integrations](docs/INTEGRATIONS.md) - External system integration guide
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation

## Features

### Real-Time Monitoring
- Live event feed from multiple sources
- WebSocket-based real-time updates
- Priority-based event filtering
- Event acknowledgment workflow

### Geospatial Intelligence
- Interactive map with live markers
- Layer controls for different data types
- Clustering for high-density areas
- Geospatial search capabilities

### Entity Graph Analysis
- Person, vehicle, incident relationships
- Network visualization
- Multi-hop relationship traversal
- Entity linking and association

### Investigative Search
- Full-text search across all entities
- Advanced filtering options
- Semantic search capabilities
- Search result highlighting

### Security & Compliance
- JWT-based authentication
- Role-based access control (RBAC)
- CJIS-compliant audit logging
- Encryption at rest and in transit

## Roles

| Role | Description |
|------|-------------|
| `admin` | Full system access, user management |
| `supervisor` | Team oversight, report generation |
| `detective` | Investigation management, entity CRUD |
| `rtcc_analyst` | Real-time monitoring, event handling |
| `officer` | View-only access, limited search |

## Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `SECRET_KEY` - JWT signing key (required)
- `NEO4J_URI` - Neo4j connection URI
- `ELASTICSEARCH_HOSTS` - Elasticsearch hosts
- `REDIS_URL` - Redis connection URL

## Testing

### Backend Tests
```bash
cd backend
poetry run pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Run linting and tests
4. Submit a pull request

## License

Proprietary - Global 3 Technology & Intelligence

## Support

For support inquiries, contact: support@g3ti.com
