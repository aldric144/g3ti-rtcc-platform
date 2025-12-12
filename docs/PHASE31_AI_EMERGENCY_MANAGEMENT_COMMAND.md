# Phase 31: AI Emergency Management Command (AI-EMC)

## Overview

Phase 31 implements the AI Emergency Management Command system for the G3TI RTCC-UIP platform. This comprehensive emergency management solution provides autonomous disaster prediction, multi-agency response coordination, recovery planning, and emergency communication intelligence for Riviera Beach, Florida.

## Architecture

### Backend Modules

Located in `backend/app/emergency_ai/`:

1. **disaster_prediction_engine.py** - Multi-Hazard Disaster Prediction Engine
2. **response_coordination_engine.py** - Autonomous Disaster Response Engine
3. **recovery_planner.py** - Autonomous Recovery & Logistics Engine
4. **communication_intel_engine.py** - Emergency Communication Intelligence Engine

### API Endpoints

Located in `backend/app/api/emergency_ai/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/emergency-ai/predict` | POST | Predict hazard based on type and data |
| `/api/emergency-ai/coordinate` | POST | Coordinate multi-agency response |
| `/api/emergency-ai/evac-route` | POST | Plan evacuation route |
| `/api/emergency-ai/recovery-plan` | POST | Create recovery plan |
| `/api/emergency-ai/hazards` | GET | Get active hazards |
| `/api/emergency-ai/resource-status` | GET | Get resource status |
| `/api/emergency-ai/shelter-status` | GET | Get shelter status |

### WebSocket Channels

Located in `backend/app/websockets/emergency_ai_ws.py`:

| Channel | Description |
|---------|-------------|
| `/ws/emergency-ai/hazards` | Real-time hazard updates |
| `/ws/emergency-ai/evac` | Evacuation orders and road closures |
| `/ws/emergency-ai/resources` | Resource and shelter updates |
| `/ws/emergency-ai/recovery` | Damage assessments and recovery updates |

### Frontend Components

Located in `frontend/app/emergency-command-center/`:

1. **DisasterPredictionDashboard** - Storm track map, flooding model, fire prediction, hazard timeline
2. **ResponseCoordinationConsole** - Multi-agency board, auto-tasking feed, evacuation visualizer
3. **ResourceShelterDashboard** - Real-time tracking, capacity meters, supply alerts
4. **RecoveryDamageDashboard** - AI damage assessments, utility outage overlays, cost/timeline
5. **EmergencyMessagingConsole** - Auto-generated alerts, multi-language preview, distribution log

## Features

### 1. Multi-Hazard Disaster Prediction Engine

Predicts and monitors multiple hazard types:

**Weather Hazards:**
- Hurricane tracking with NOAA/NHC data integration
- Tornado prediction and path modeling
- Flooding risk assessment (street-level)
- Storm surge modeling
- Severe thunderstorm tracking

**Fire Hazards:**
- Urban fire spread modeling
- Wildfire prediction
- Wind, humidity, and temperature factors
- Structure vulnerability assessment

**Hazmat Hazards:**
- Chemical plume modeling
- Affected radius calculation
- Evacuation prioritization
- Chemical class identification

**Infrastructure Hazards:**
- Bridge stress monitoring
- Seawall failure prediction
- Power grid instability detection
- Roadway subsidence tracking

**Output Format:**
- Threat Level (1-5): Minimal, Low, Moderate, High, Extreme
- Affected Zones
- Time-to-Impact (hours)
- Recommended Actions
- Agencies Required
- Confidence Score
- Chain of Custody Hash (SHA256)

### 2. Autonomous Disaster Response Engine

Coordinates multi-agency disaster response:

**Agency Types:**
- Police Department
- Fire/Rescue
- EMS
- Public Works
- Utilities
- Hospitals
- Red Cross
- Regional EOCs
- National Guard
- FEMA
- Coast Guard
- State Emergency Management

**Resource Types:**
- Patrol units (25 available)
- Fire engines (8 available)
- Ambulances (12 available)
- Rescue squads (6 available)
- Evacuation buses (15 available)
- Generators (20 available)
- Water trucks (8 available)
- Food trucks (5 available)
- Medical teams (10 available)
- Search & rescue teams (4 available)
- Drones (12 available)
- Boats (6 available)

**Evacuation Routing:**
- Road network analysis
- Live traffic integration
- Flood blockage detection
- Bridge status monitoring
- Crowd density tracking
- Special needs accommodation

**Pre-configured Shelters:**
1. Riviera Beach Community Center (Zone_A) - 500 capacity
2. Marina Event Center (Zone_E) - 350 capacity
3. High School Gymnasium (Zone_C) - 800 capacity
4. Recreation Center (Zone_G) - 400 capacity
5. Church Fellowship Hall (Zone_B) - 250 capacity

### 3. Autonomous Recovery & Logistics Engine

Manages post-disaster recovery:

**Damage Assessment AI:**
- Drone imagery analysis
- Sensor grid data
- Citizen reports
- LPR data integration
- Fire/EMS reports
- Structure damage tiers (None, Minor, Moderate, Major, Destroyed)

**Humanitarian Supply Optimizer:**
- Food allocation
- Water distribution
- Medical supplies
- Generators
- Fuel
- Shelter kits
- Hygiene kits
- Blankets
- Tarps
- Tools

**Cost & Recovery Timeline:**
- Infrastructure repair estimation
- Financial loss calculation
- FEMA category mapping (A-G)
- Federal/State/Local cost sharing (75%/12.5%/12.5%)
- Recovery phase planning (Immediate, Short-term, Intermediate, Long-term)

### 4. Emergency Communication Intelligence Engine

Manages emergency communications:

**Automated Emergency Messaging:**
- Reverse 911
- Text alerts
- Email notifications
- Social media posts
- Siren activation
- Radio broadcasts
- TV alerts
- Website updates
- Mobile app notifications

**Alert Types:**
- Evacuation Order
- Evacuation Advisory
- Shelter in Place
- Shelter Update
- Road Closure
- Water Advisory
- Boil Water Notice
- Power Outage
- Hazmat Warning
- Weather Warning
- All Clear
- Curfew

**Multi-Language Support:**
- English
- Spanish
- Haitian Creole

**Social Signal Extraction:**
- Public post monitoring
- Crisis keyword detection
- Resource request identification
- Rumor detection
- Misinformation flagging
- Sentiment analysis

## City Configuration

**Agency:**
- ORI: FL0500400
- City: Riviera Beach
- State: Florida
- ZIP: 33404
- County: Palm Beach

**Zones:**
| Zone | Population | Elevation (ft) |
|------|------------|----------------|
| Zone_A | 3,500 | 8.2 |
| Zone_B | 4,200 | 6.5 |
| Zone_C | 3,800 | 12.1 |
| Zone_D | 2,900 | 15.3 |
| Zone_E | 4,500 | 4.8 |
| Zone_F | 3,200 | 9.7 |
| Zone_G | 2,800 | 11.4 |
| Zone_H | 3,600 | 7.3 |
| Zone_I | 4,100 | 5.9 |
| Zone_J | 3,400 | 6.1 |

## Chain of Custody

All predictions, tasks, allocations, and communications include SHA256 chain of custody hashing for evidence integrity:

```python
def _generate_hash(self) -> str:
    data = f"{self.id}:{self.timestamp.isoformat()}:{self.type}:{self.value}"
    return hashlib.sha256(data.encode()).hexdigest()
```

## Ethical Safeguards

1. **Privacy Protection:**
   - No private social media data access
   - Only public posts analyzed
   - No demographic profiling
   - No predictive policing on protected classes

2. **Transparency:**
   - All predictions include confidence scores
   - Chain of custody on all decisions
   - Audit trail for all actions

3. **Human Oversight:**
   - Critical decisions require human approval
   - Override capabilities for all automated actions
   - Clear escalation paths

## API Usage Examples

### Predict Hazard

```bash
curl -X POST http://localhost:8000/api/emergency-ai/predict \
  -H "Content-Type: application/json" \
  -d '{
    "hazard_type": "hurricane",
    "noaa_data": {
      "wind_speed_mph": 85,
      "rainfall_inches": 8,
      "pressure_mb": 975
    },
    "nhc_data": {
      "storm_name": "Hurricane Alpha",
      "category": 1,
      "storm_surge_feet": 5
    }
  }'
```

### Coordinate Response

```bash
curl -X POST http://localhost:8000/api/emergency-ai/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "hurricane",
    "threat_level": 4,
    "affected_zones": ["Zone_A", "Zone_B", "Zone_E"]
  }'
```

### Create Recovery Plan

```bash
curl -X POST http://localhost:8000/api/emergency-ai/recovery-plan \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "hurricane",
    "affected_zones": ["Zone_A", "Zone_B"],
    "severity_factor": 0.6
  }'
```

## Testing

Run Phase 31 tests:

```bash
pytest tests/phase31/ -v
```

Individual test suites:
- `test_disaster_prediction.py` - Disaster prediction engine tests
- `test_response_coordination.py` - Response coordination tests
- `test_recovery_planner.py` - Recovery planner tests
- `test_communication_intel.py` - Communication intelligence tests
- `test_emergency_api.py` - API endpoint tests
- `test_emergency_websockets.py` - WebSocket channel tests
- `test_weather_models.py` - Weather hazard model validation
- `test_fire_models.py` - Fire spread model validation
- `test_hazmat_models.py` - Hazmat model validation
- `test_infrastructure_models.py` - Infrastructure model validation
- `test_evacuation_routing.py` - Evacuation routing tests
- `test_shelter_assignment.py` - Shelter assignment tests
- `test_damage_assessment.py` - Damage assessment tests
- `test_supply_optimization.py` - Supply optimization tests
- `test_chain_of_custody.py` - Chain of custody validation

## Dependencies

- Python 3.11+
- FastAPI
- Pydantic
- hashlib (standard library)
- uuid (standard library)
- datetime (standard library)

## Files Added

### Backend (12 files)
- `backend/app/emergency_ai/__init__.py`
- `backend/app/emergency_ai/disaster_prediction_engine.py`
- `backend/app/emergency_ai/response_coordination_engine.py`
- `backend/app/emergency_ai/recovery_planner.py`
- `backend/app/emergency_ai/communication_intel_engine.py`
- `backend/app/api/emergency_ai/__init__.py`
- `backend/app/api/emergency_ai/emergency_ai_router.py`
- `backend/app/websockets/emergency_ai_ws.py`

### Frontend (6 files)
- `frontend/app/emergency-command-center/page.tsx`
- `frontend/app/emergency-command-center/components/DisasterPredictionDashboard.tsx`
- `frontend/app/emergency-command-center/components/ResponseCoordinationConsole.tsx`
- `frontend/app/emergency-command-center/components/ResourceShelterDashboard.tsx`
- `frontend/app/emergency-command-center/components/RecoveryDamageDashboard.tsx`
- `frontend/app/emergency-command-center/components/EmergencyMessagingConsole.tsx`

### DevOps (1 file)
- `.github/workflows/emergency-ai-selftest.yml`

### Documentation (1 file)
- `docs/PHASE31_AI_EMERGENCY_MANAGEMENT_COMMAND.md`

### Tests (15 files)
- `tests/phase31/__init__.py`
- `tests/phase31/test_disaster_prediction.py`
- `tests/phase31/test_response_coordination.py`
- `tests/phase31/test_recovery_planner.py`
- `tests/phase31/test_communication_intel.py`
- `tests/phase31/test_emergency_api.py`
- `tests/phase31/test_emergency_websockets.py`
- `tests/phase31/test_weather_models.py`
- `tests/phase31/test_fire_models.py`
- `tests/phase31/test_hazmat_models.py`
- `tests/phase31/test_infrastructure_models.py`
- `tests/phase31/test_evacuation_routing.py`
- `tests/phase31/test_shelter_assignment.py`
- `tests/phase31/test_damage_assessment.py`
- `tests/phase31/test_supply_optimization.py`
- `tests/phase31/test_chain_of_custody.py`

## Version

- Phase: 31
- Version: 1.0.0
- Date: December 2025
- Author: Devin AI

## Related Phases

- Phase 21: AI Emergency Management & Disaster Response Engine (AEMDRE)
- Phase 30: Human Stability Intelligence Engine (HSI-E)
