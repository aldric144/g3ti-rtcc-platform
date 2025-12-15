# Phase 39: Full System Preview Deployment & Live Frontend Activation

## Overview

Phase 39 prepares the entire G3TI RTCC-UIP platform for public-facing preview, enabling deployment of the frontend and backend into a unified environment. This is the final validation phase before production deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    G3TI RTCC-UIP Pre-Launch Architecture                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Pre-Launch System Integrator                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Module    │  │  WebSocket  │  │     API     │  │Orchestration│  │   │
│  │  │  Validator  │  │  Validator  │  │  Validator  │  │  Validator  │  │   │
│  │  │  (60+ mods) │  │ (80+ chans) │  │ (46+ endpts)│  │  (Phase 38) │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    WebSocket Integration Checker                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │    Ping     │  │  Handshake  │  │  Broadcast  │  │   Stress    │  │   │
│  │  │   Frames    │  │    Test     │  │ Simulation  │  │    Test     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Deployment Score Calculator                      │   │
│  │                                                                        │   │
│  │   Score = (Passed Checks / Total Checks) × 100 + Orchestration Bonus  │   │
│  │                                                                        │   │
│  │   Ready for Deployment: Score ≥ 85%                                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Pre-Launch System Integrator

**Location:** `backend/app/system/prelaunch_integrator.py`

The Pre-Launch System Integrator validates all 60+ modules across the RTCC platform:

**Module Categories:**
- Data (Data Lake, ETL, Repository)
- Analytics (Heatmap, Repeat Offender)
- Intelligence (Orchestration, Correlation)
- Operations (Health Check, Failover)
- Autonomous (Drone, Sensor Grid, Digital Twin, Predictive)
- Fusion (Multi-City, Federation, Shared Intel)
- Threat (Global Threat Intel, Aggregator, Correlation)
- Security (National Security)
- Robotics (Tactical Robotics, Fleet Manager)
- AI (Detective AI, Case Analysis)
- Emergency (Emergency Management, Disaster Response)
- City (City Brain, Prediction, Governance, Autonomy)
- Ethics (Constitution, Legislative, Ethics Guardian, Bias Detection)
- Infrastructure (Enterprise, CJIS Compliance)
- Officer (Officer Assist, Guardrail, Tactical)
- Cyber (Cyber Intel, Quantum Threat)
- Human (Human Stability, Crisis)
- Orchestration (Kernel, Event Router, Workflow Engine, Policy Binding, Resource Manager, Event Bus)

**Features:**
- Module integrity verification
- Response time measurement
- Error aggregation
- Validation history tracking

### 2. WebSocket Integration Checker

**Location:** `backend/app/system/ws_integration_checker.py`

Validates all 80+ WebSocket channels:

**Test Types:**
- Ping frames to all channels
- 2-way handshake test
- Event broadcast simulation
- Stress test (500 simulated events)

**Auto-Repair Suggestions:**
- Ping failure detection
- High latency warnings
- Handshake failure analysis
- Message loss detection

### 3. Frontend Components

**PreLaunchChecklistPanel** (`frontend/app/live-system-check/components/PreLaunchChecklistPanel.tsx`)
- Module Status Grid
- WebSocket Connectivity Matrix
- API Endpoint Validator
- Orchestration Engine Signal Indicator
- "Ready for Deployment" Score (0-100%)

**DeploymentSummaryCard** (`frontend/app/live-system-check/components/DeploymentSummaryCard.tsx`)
- Circular deployment score visualization
- Validation checklist
- Blocking issues display
- Deployment recommendation

**Pages:**
- `/live-system-check` - Complete system check dashboard
- `/system-prelaunch` - Pre-launch diagnostics page

### 4. Deployment Pipeline

**Location:** `.github/workflows/prelaunch-preview-deploy.yml`

**Jobs:**
1. `system-validation` - Run all validation tests
2. `build-frontend` - Build Next.js frontend
3. `build-backend` - Build FastAPI backend
4. `integration-tests` - Run integration tests
5. `deploy-frontend` - Deploy to Vercel
6. `deploy-backend` - Deploy to Fly.io
7. `generate-report` - Generate deployment report
8. `stress-test` - Optional WebSocket stress test

## API Endpoints

### Pre-Launch Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system/prelaunch/status` | GET | Get complete pre-launch status |
| `/api/system/prelaunch/status/detailed` | GET | Get detailed validation results |
| `/api/system/prelaunch/modules` | GET | Get module validation results |
| `/api/system/prelaunch/websockets` | GET | Get WebSocket validation results |
| `/api/system/prelaunch/endpoints` | GET | Get API endpoint validation results |
| `/api/system/prelaunch/orchestration` | GET | Get orchestration engine status |
| `/api/system/prelaunch/websocket-check` | GET | Run WebSocket integration check |
| `/api/system/prelaunch/websocket-check/ping` | GET | Get WebSocket ping results |
| `/api/system/prelaunch/websocket-check/stress` | GET | Run WebSocket stress test |
| `/api/system/prelaunch/websocket-check/repair-suggestions` | GET | Get auto-repair suggestions |
| `/api/system/prelaunch/deployment-score` | GET | Get deployment readiness score |
| `/api/system/prelaunch/statistics` | GET | Get integrator statistics |
| `/api/system/prelaunch/history` | GET | Get validation history |
| `/api/system/prelaunch/validate` | POST | Trigger new validation run |
| `/api/system/prelaunch/health` | GET | Get system health status |

### Response Schema

**Pre-Launch Status Response:**
```json
{
  "modules_ok": true,
  "websockets_ok": true,
  "endpoints_ok": true,
  "orchestration_ok": true,
  "database_ok": true,
  "ai_engines_ok": true,
  "latency_ms": 123.45,
  "load_factor": 0.42,
  "deployment_score": 95.5,
  "errors": [],
  "warnings": [],
  "module_count": 61,
  "websocket_count": 84,
  "api_count": 46,
  "validated_at": "2024-01-15T12:00:00Z"
}
```

## Required Environment Variables

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://g3ti-rtcc-preview-api.fly.dev
NEXT_PUBLIC_WS_URL=wss://g3ti-rtcc-preview-api.fly.dev
```

### Backend (Fly.io)
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ELASTICSEARCH_URL=https://...
NEO4J_URI=bolt://...
SECRET_KEY=...
```

### GitHub Actions
```
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
VERCEL_PROJECT_ID=...
FLY_API_TOKEN=...
PREVIEW_API_URL=https://g3ti-rtcc-preview-api.fly.dev
PREVIEW_WS_URL=wss://g3ti-rtcc-preview-api.fly.dev
```

## Running the PreLaunch UI

1. Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to:
- http://localhost:3000/live-system-check
- http://localhost:3000/system-prelaunch

## Interpreting the Deployment Score

| Score Range | Grade | Status | Recommendation |
|-------------|-------|--------|----------------|
| 95-100% | A+ | Excellent | Ready for production |
| 90-94% | A | Very Good | Ready for deployment |
| 85-89% | B+ | Good | Ready for preview |
| 80-84% | B | Acceptable | Minor issues to address |
| 70-79% | C | Warning | Significant issues |
| <70% | F | Critical | Not ready for deployment |

**Score Calculation:**
```
Base Score = (Passed Validations / Total Validations) × 100
Orchestration Bonus = +5 if orchestration_ok
Final Score = min(100, Base Score + Orchestration Bonus)
```

## Expected Behaviors

1. **Real-time WebSocket events appear in UI** - All 80+ channels should show connected status
2. **Orchestration Engine responds within 500ms** - Phase 38 handshake should complete quickly
3. **All 20 workflows are registered** - Workflow engine should report 20 registered workflows
4. **Data Lake → Prediction → UI pipeline validated** - End-to-end data flow should work
5. **Constitutional guardrails are enforced** - Policy binding engine should be operational
6. **Multi-agency coordination is operational** - Fusion cloud should be connected

## Troubleshooting

### Module Validation Failures

**Symptom:** `modules_ok: false`

**Solutions:**
1. Check if all required Python packages are installed
2. Verify module import paths are correct
3. Check for circular import issues
4. Review module initialization errors in logs

### WebSocket Connection Issues

**Symptom:** `websockets_ok: false` or high latency

**Solutions:**
1. Verify WebSocket server is running
2. Check firewall/proxy settings
3. Review WebSocket route configuration
4. Check for connection pool exhaustion

### API Endpoint Failures

**Symptom:** `endpoints_ok: false`

**Solutions:**
1. Verify FastAPI routes are registered
2. Check authentication middleware
3. Review request/response schemas
4. Check database connectivity

### Orchestration Engine Issues

**Symptom:** `orchestration_ok: false`

**Solutions:**
1. Verify Phase 38 modules are properly imported
2. Check OrchestrationKernel initialization
3. Review WorkflowEngine registration
4. Verify PolicyBindingEngine configuration

### Low Deployment Score

**Symptom:** Score < 85%

**Solutions:**
1. Review all error messages in the status response
2. Address critical failures first
3. Run individual validation endpoints to isolate issues
4. Check the validation history for patterns

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── system/
│   │       ├── __init__.py
│   │       └── prelaunch_router.py
│   └── system/
│       ├── __init__.py
│       ├── prelaunch_integrator.py
│       └── ws_integration_checker.py
frontend/
├── app/
│   ├── live-system-check/
│   │   ├── page.tsx
│   │   └── components/
│   │       ├── PreLaunchChecklistPanel.tsx
│   │       └── DeploymentSummaryCard.tsx
│   └── system-prelaunch/
│       └── page.tsx
.github/
└── workflows/
    └── prelaunch-preview-deploy.yml
docs/
└── PHASE39_PRELAUNCH_DEPLOYMENT.md
tests/
└── phase39/
    ├── __init__.py
    ├── test_module_integrity.py
    ├── test_api_schema.py
    ├── test_websocket_validation.py
    ├── test_orchestration_handshake.py
    ├── test_frontend_components.py
    ├── test_deployment_pipeline.py
    ├── test_integration.py
    └── test_e2e_prelaunch.py
```

## Preview Deployment Targets

| Component | Target | URL |
|-----------|--------|-----|
| Frontend | Vercel | https://g3ti-rtcc-preview-ui.vercel.app |
| Backend | Fly.io | https://g3ti-rtcc-preview-api.fly.dev |
| WebSocket Test Panel | Vercel | https://g3ti-rtcc-preview-ui.vercel.app/live-system-check |

## Next Steps (Phase 40)

After Phase 39 is complete and the deployment score is ≥ 85%, proceed to:

**Phase 40: Demo Simulation Mode**
- Live demonstration capabilities
- Simulated incident scenarios
- Real-time data visualization
- Multi-user collaboration testing
