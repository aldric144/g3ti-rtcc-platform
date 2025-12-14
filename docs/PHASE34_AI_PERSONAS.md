# Phase 34: AI Personas Framework (Apex AI Officers)

## Overview

Phase 34 introduces the AI Personas Framework, implementing fully autonomous "Apex AI Officers" - specialized operational AI units that assist every domain of the G3TI RTCC-UIP system. These AI personas serve as virtual teammates with stable roles, memory, reasoning, and mission logic.

## Architecture

### Core Components

#### 1. Persona Architecture Layer (`persona_engine.py`)

The foundation module providing persona lifecycle management:

- **PersonaEngine**: Singleton class managing all personas
- **PersonaMemory**: Multi-tiered memory system (short-term, mission, context, learned)
- **BehaviorModel**: Role-based behavior definitions with capabilities and limitations
- **SafetyConstraint**: Constitutional, policy, ethical, and operational constraints

#### 2. Persona Interaction Engine (`interaction_engine.py`)

Handles natural language interactions:

- Natural language to operational intent pipeline
- Domain routing (intel, patrol, robotics, crisis, etc.)
- Multi-turn conversation memory
- Emotion and urgency detection
- Role-appropriate responses
- Full explainability trace

#### 3. Mission Reasoning Engine (`mission_reasoner.py`)

Converts tasks into actionable mission steps:

- Risk and obstacle prediction
- Task assignment to drones, robots, or units
- Legal/policy violation checking
- Human approval requests when required
- Outcome evaluation (branch prediction)

#### 4. Compliance Integration Layer (`compliance_layer.py`)

Integrates with governance frameworks:

- Phase 28 Constitutional Guardrails
- Phase 33 AI Sentinel Supervisor
- Phase 24 City Autonomy Policy Engine
- Every persona decision runs through validation

## Persona Types

### 1. APEX_PATROL - Officer Alpha
Real-time patrol assistance for field officers:
- Traffic stop guidance
- Suspicious activity analysis
- Backup coordination
- Route optimization

### 2. APEX_COMMAND - Commander Sigma
Decision support for commanders:
- Resource allocation recommendations
- Incident command support
- Strategic planning assistance
- Multi-unit coordination

### 3. APEX_INTEL - Analyst Omega
Advanced analysis and pattern fusion:
- Threat assessment
- Pattern recognition
- Data correlation
- Intelligence briefings

### 4. APEX_CRISIS - Counselor Delta
De-escalation and mental health assistance:
- Crisis intervention guidance
- De-escalation talking points
- Mental health resource coordination
- Hostage negotiation support

### 5. APEX_ROBOTICS - Coordinator Theta
Drone and robotics coordination:
- Drone deployment planning
- Ground robot tasking
- Sensor coordination
- Autonomous asset management

### 6. APEX_INVESTIGATIONS - Detective Gamma
Case building and evidence analysis:
- Timeline construction
- Evidence graphing
- Witness correlation
- Cold case analysis

## Memory System

### Memory Types

1. **Short-term Memory**: Expires after 24 hours, used for immediate context
2. **Mission Memory**: Persistent for mission duration
3. **Context Memory**: Operational context and situational awareness
4. **Learned Memory**: Long-term learning from interactions

### Memory Features

- Importance scoring for prioritization
- Embedding-based search capability
- Automatic expiration management
- Memory load tracking and limits

## Safety Constraints

### Constitutional Constraints
- 4th Amendment: No warrantless searches
- 5th Amendment: Due process requirements
- 14th Amendment: Equal protection, no profiling

### Policy Constraints
- Human approval for critical actions
- Supervisor authorization requirements
- FAA compliance for drone operations

### Ethical Constraints
- Bias prevention
- Transparency and explainability
- Privacy protection

### Operational Constraints
- Escalation thresholds
- Risk level limits
- Resource constraints

## API Endpoints

### Persona Management
- `GET /api/personas` - List all personas
- `GET /api/personas/{id}` - Get persona details
- `GET /api/personas/{id}/status` - Get persona status
- `PUT /api/personas/{id}/status` - Update persona status
- `PUT /api/personas/{id}/emotional-state` - Update emotional state

### Interaction
- `POST /api/personas/{id}/ask` - Send message to persona
- `GET /api/sessions/active` - Get active sessions
- `GET /api/sessions/{id}` - Get session history
- `POST /api/sessions/{id}/end` - End session

### Missions
- `POST /api/personas/{id}/mission` - Create mission
- `GET /api/missions` - List all missions
- `GET /api/missions/{id}` - Get mission details
- `POST /api/missions/{id}/start` - Start mission
- `POST /api/missions/{id}/complete` - Complete mission

### Approvals
- `GET /api/approvals/pending` - Get pending approvals
- `POST /api/approvals/{id}/approve` - Approve request
- `POST /api/approvals/{id}/deny` - Deny request

### Compliance
- `POST /api/personas/{id}/validate` - Validate action
- `GET /api/compliance/summary` - Get compliance summary
- `GET /api/compliance/violations` - Get active violations
- `POST /api/compliance/violations/{id}/resolve` - Resolve violation

### Memory
- `POST /api/personas/{id}/memory/clear` - Clear persona memory

## WebSocket Channels

### Chat Channel
`/ws/personas/{persona_id}/chat`
- Real-time conversation with persona
- Automatic session management
- Response streaming

### Alerts Channel
`/ws/personas/alerts`
- System-wide persona alerts
- Escalation notifications
- Compliance violations

### Reasoning Channel
`/ws/personas/reasoning`
- Mission reasoning updates
- Decision trace streaming

### Missions Channel
`/ws/personas/missions`
- Mission status updates
- Task progress notifications

## Frontend Components

### AI Persona Operations Center (`/personas-center`)

1. **PersonaListPanel**: List of all Apex AI Officers with status indicators
2. **PersonaChatConsole**: Real-time multi-turn chat interface
3. **MissionBoard**: Active missions and task tracking
4. **DecisionTraceViewer**: Legal/ethical reasoning explanation
5. **PersonaPerformancePanel**: Accuracy metrics and response times
6. **SupervisorOverridePanel**: Commander approvals and overrides

## Governance Integration

### Phase 28 Integration
All persona actions are validated against Constitutional Guardrails:
- 4th Amendment compliance
- 5th Amendment compliance
- 14th Amendment compliance

### Phase 33 Integration
AI Sentinel Supervisor oversight:
- Action validation
- Autonomy level enforcement
- Compliance score tracking

### Phase 24 Integration
City Autonomy Policy Engine:
- Policy rule enforcement
- Authorization requirements
- Operational constraints

## Chain of Custody

All persona decisions include SHA256 hashing for evidence integrity:
- Session records
- Interaction traces
- Mission logs
- Compliance checks
- Violation records

## Multi-Agent Cooperation

Personas can work together on complex tasks:
- Cooperation protocol establishment
- Task distribution
- Information sharing
- Coordinated responses

## Configuration

### Environment Variables

```
PERSONA_ENGINE_ENABLED=true
INTERACTION_ENGINE_ENABLED=true
MISSION_REASONER_ENABLED=true
COMPLIANCE_LAYER_ENABLED=true
MAX_SESSIONS_PER_PERSONA=10
SESSION_TIMEOUT_MINUTES=30
MEMORY_SHORT_TERM_LIMIT=100
MEMORY_MISSION_LIMIT=50
MEMORY_CONTEXT_LIMIT=200
MEMORY_LEARNED_LIMIT=500
COMPLIANCE_CHECK_ENABLED=true
COMPLIANCE_STRICT_MODE=true
```

## Docker Deployment

```bash
docker build -t g3ti-personas-service -f docker/personas-service/Dockerfile .
docker run -p 8034:8034 g3ti-personas-service
```

## Testing

Run all Phase 34 tests:
```bash
pytest tests/phase34/ -v
```

Individual test suites:
- `test_persona_engine.py` - Persona lifecycle tests
- `test_interaction_engine.py` - Interaction tests
- `test_mission_reasoner.py` - Mission planning tests
- `test_compliance_integration.py` - Compliance tests
- `test_personas_api.py` - API endpoint tests
- `test_personas_websockets.py` - WebSocket tests
- `test_multi_agent_cooperation.py` - Cooperation tests
- `test_persona_memory.py` - Memory system tests
- `test_safety_constraints.py` - Safety constraint tests
- `test_e2e_personas.py` - End-to-end tests

## Security Considerations

1. All persona actions are logged with chain of custody
2. Constitutional constraints are enforced at all times
3. Human oversight required for critical decisions
4. Compliance violations trigger automatic blocks
5. No persona can bypass governance frameworks

## Future Enhancements

- Voice interaction support
- Advanced emotion recognition
- Predictive persona recommendations
- Cross-agency persona sharing
- Enhanced learning capabilities

## Files Added

### Backend
- `backend/app/personas/__init__.py`
- `backend/app/personas/persona_engine.py`
- `backend/app/personas/interaction_engine.py`
- `backend/app/personas/mission_reasoner.py`
- `backend/app/personas/compliance_layer.py`
- `backend/app/api/personas/__init__.py`
- `backend/app/api/personas/persona_router.py`
- `backend/app/websockets/personas_ws.py`

### Frontend
- `frontend/app/personas-center/page.tsx`
- `frontend/app/personas-center/components/PersonaListPanel.tsx`
- `frontend/app/personas-center/components/PersonaChatConsole.tsx`
- `frontend/app/personas-center/components/MissionBoard.tsx`
- `frontend/app/personas-center/components/DecisionTraceViewer.tsx`
- `frontend/app/personas-center/components/PersonaPerformancePanel.tsx`
- `frontend/app/personas-center/components/SupervisorOverridePanel.tsx`

### DevOps
- `.github/workflows/personas-service.yml`
- `docker/personas-service/Dockerfile`
- `docker/personas-service/requirements.txt`
- `docker/personas-service/main.py`
- `docker/personas-service/config.py`

### Documentation
- `docs/PHASE34_AI_PERSONAS.md`

### Tests
- `tests/phase34/__init__.py`
- `tests/phase34/test_persona_engine.py`
- `tests/phase34/test_interaction_engine.py`
- `tests/phase34/test_mission_reasoner.py`
- `tests/phase34/test_compliance_integration.py`
- `tests/phase34/test_personas_api.py`
- `tests/phase34/test_personas_websockets.py`
- `tests/phase34/test_multi_agent_cooperation.py`
- `tests/phase34/test_persona_memory.py`
- `tests/phase34/test_safety_constraints.py`
- `tests/phase34/test_e2e_personas.py`
