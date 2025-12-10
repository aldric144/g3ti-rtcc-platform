# Phase 22: AI City Brain Engine

## Overview

Phase 22 implements the AI City Brain Engine for Riviera Beach, Florida (33404). This comprehensive system models the city as a living, dynamically updating digital organism that continuously ingests real-time data from federal, state, and local systems while simulating and predicting city-wide behavior across crime, traffic, utilities, disasters, and population movement.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI City Brain Engine                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ City Brain  │  │   Data      │  │  Digital    │             │
│  │    Core     │──│ Ingestion   │──│    Twin     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Prediction  │  │    API      │  │  WebSocket  │             │
│  │   Engine    │──│   Layer     │──│  Channels   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Modules

### 1. City Brain Core (`backend/app/city_brain/__init__.py`)

The central orchestrator that coordinates all city brain modules.

**Key Classes:**
- `CityBrainCore`: Main orchestrator managing all subsystems
- `CityProfileLoader`: Loads and manages Riviera Beach city profile data
- `EventBus`: Internal event bus for cross-module communication
- `CityEvent`: Represents events in the city brain system
- `CityState`: Current state snapshot of the city
- `ModuleStatus`: Status of a city brain module

**Enums:**
- `CityModuleType`: weather, traffic, utilities, incidents, digital_twin, predictions, ingestion, admin
- `CityEventType`: weather_update, traffic_update, utility_update, incident_update, prediction_update, etc.
- `EventPriority`: LOW, NORMAL, HIGH, CRITICAL

### 2. Data Ingestion (`backend/app/city_brain/ingestion/__init__.py`)

Real-time data ingestion from 7 external sources.

**Ingestors:**
- `NWSWeatherIngestor`: NWS/NOAA weather API (temperature, alerts, precipitation, lightning, marine)
- `NOAAMarineIngestor`: NOAA marine & tide data (tide cycles, rip currents, wave conditions)
- `EPAAirQualityIngestor`: EPA AirNow API (PM2.5, AQI, ozone, health advisories)
- `FDOTTrafficIngestor`: FDOT/Florida 511 traffic (accidents, congestion, road closures, construction)
- `FPLOutageIngestor`: FPL outage feed (power outages, grid stress, restoration times)
- `CityUtilitiesIngestor`: Riviera Beach utilities (water pressure, pump stations, sewer, flooding)
- `PublicSafetyIngestor`: Emergency & public safety (CAD calls, unit locations, camera status)

**Data Classes:**
- `WeatherConditions`, `WeatherAlert`
- `MarineConditions`
- `AirQualityData`
- `TrafficIncident`, `TrafficConditions`
- `PowerOutage`
- `UtilityStatus`
- `IngestionResult`

### 3. Digital Twin (`backend/app/city_brain/digital_twin/__init__.py`)

Enhanced digital twin system for real-time city visualization.

**Components:**
- `DigitalTwinState`: Real-time city state snapshot with traffic grid, environmental conditions, infrastructure status, crime hotspots, population estimates
- `DynamicObjectRenderer`: Renders police units, fire units, EMS, city vehicles, drones, robots, boats with location tracking and history
- `EventOverlayEngine`: Displays overlays for power outages, floods, road closures, police incidents, weather alerts, evacuation routes
- `TimeWarpEngine`: Enables historical playback and future simulation up to 72 hours
- `DigitalTwinManager`: Main coordinator for all digital twin components

**Enums:**
- `ObjectType`: police_unit, fire_unit, ems_unit, city_vehicle, drone, robot, boat
- `ObjectStatus`: available, busy, en_route, on_scene, out_of_service
- `OverlayType`: power_outage, flood_zone, road_closure, police_incident, weather_alert, evacuation_route
- `CongestionLevel`: free_flow, light, moderate, heavy, gridlock
- `TimelineMode`: live, historical, simulation

### 4. Prediction Engine (`backend/app/city_brain/prediction/__init__.py`)

City prediction engine with 5 comprehensive models.

**Predictors:**
- `TrafficFlowPredictor`: Predicts congestion, reroutes, crash risk, evacuation flow for 8 road segments
- `CrimeDisplacementPredictor`: Predicts crime displacement based on weather, events, police presence across 6 zones
- `InfrastructureRiskPredictor`: Predicts failure probability for 8 infrastructure elements (water treatment, pump stations, substations, lift stations, water mains)
- `DisasterImpactModel`: Models hurricane (Cat 1-5), flooding, extreme heat impacts with timeline predictions
- `PopulationMovementModel`: Predicts crowd sizes, school traffic, church attendance, marina density across 6 zones
- `CityPredictionEngine`: Main coordinator for all prediction models

**Enums:**
- `PredictionConfidence`: low, medium, high, very_high
- `RiskLevel`: minimal, low, moderate, high, severe, extreme
- `DisasterType`: hurricane, flood, tornado, storm_surge, extreme_heat, marine_hazard

### 5. API Layer (`backend/app/api/city_brain/router.py`)

Comprehensive REST API with 40+ endpoints.

**GET Endpoints:**
- `/city/state` - Unified city snapshot
- `/city/weather` - Current weather data
- `/city/weather/forecast` - Weather forecast
- `/city/weather/marine` - Marine and tide conditions
- `/city/traffic` - Traffic conditions
- `/city/traffic/incidents` - Active traffic incidents
- `/city/utility` - Utility system status
- `/city/utility/outages` - Power outages
- `/city/incidents` - Active public safety incidents
- `/city/predictions` - Comprehensive city predictions
- `/city/predictions/traffic` - Traffic flow predictions
- `/city/predictions/crime` - Crime displacement predictions
- `/city/predictions/infrastructure` - Infrastructure risk predictions
- `/city/predictions/population` - Population movement predictions
- `/city/predictions/disaster/{disaster_type}` - Disaster impact predictions
- `/city/events` - Active city events
- `/city/digital-twin` - Digital twin render data
- `/city/digital-twin/objects` - Dynamic objects in digital twin
- `/city/digital-twin/overlays` - Active overlays in digital twin
- `/city/simulation/forecast/{hours}` - Future simulation forecast
- `/health` - City brain health status
- `/profile` - Riviera Beach city profile
- `/profile/districts` - City districts
- `/profile/infrastructure` - Critical infrastructure
- `/profile/flood-zones` - Flood zone information
- `/profile/hurricane-zones` - Hurricane evacuation zones
- `/status` - Overall city brain status

**POST Endpoints:**
- `/admin/events` - Create city event (festivals, parades, school dismissals, utility maintenance, VIP visits, police operations, sports events, concerts, community events)
- `/admin/road-closures` - Create road closure event
- `/admin/emergency-declaration` - Create emergency declaration
- `/city/simulation/play` - Control simulation playback (live, historical, simulation modes)
- `/refresh` - Refresh all data from ingestion sources

**DELETE Endpoints:**
- `/admin/events/{event_id}` - Acknowledge and clear an event

### 6. WebSocket Channels (`backend/app/websockets/city_brain.py`)

Real-time streaming channels for live updates.

**Channels:**
- `/ws/city/state` - City state updates
- `/ws/city/weather` - Weather updates
- `/ws/city/traffic` - Traffic updates
- `/ws/city/digital-twin` - Digital twin updates
- `/ws/city/predictions` - Prediction updates
- `/ws/city/events` - Event updates
- `/ws/city/alerts` - Alert and emergency broadcasts

**Message Types:**
- `state_update`, `weather_update`, `traffic_update`
- `incident_update`, `utility_update`, `prediction_update`
- `digital_twin_update`, `object_position_update`, `overlay_update`
- `event_created`, `event_updated`, `event_cleared`
- `alert`, `emergency`, `system_status`

## City Profile: Riviera Beach, FL 33404

### Geographic Data
- **Coordinates**: 26.7753°N, 80.0583°W
- **Area**: 9.76 square miles
- **Population**: 37,964
- **County**: Palm Beach County
- **State**: Florida

### Districts
1. Downtown/Marina District
2. Singer Island
3. Westside
4. Central Business District
5. Industrial/Port Area
6. North Riviera Beach

### Critical Infrastructure
- Water Treatment Plant
- Wastewater Treatment Plant
- Singer Island Substation
- Port of Palm Beach
- Riviera Beach Marina
- Blue Heron Bridge
- City Hall Complex

### Flood Zones
- Zone AE (Coastal High Hazard)
- Zone VE (Velocity Zone)
- Zone X (Moderate Risk)
- Zone AH (Shallow Flooding)
- Zone A (100-Year Flood)

### Hurricane Evacuation Zones
- Zone A: Singer Island, Marina District (mandatory for Cat 1+)
- Zone B: Coastal areas (mandatory for Cat 2+)
- Zone C: Low-lying inland areas (mandatory for Cat 3+)

## Frontend Components

### Main Page (`frontend/app/city-brain/page.tsx`)

Dashboard with 9 tabs:
1. **Dashboard** - Overview with system health, population, events, module status
2. **Digital Twin** - 3D city visualization with dynamic objects and overlays
3. **Live Heatmap** - Real-time heatmaps for crime, traffic, population, temperature, air quality
4. **Environment** - Weather, marine conditions, air quality monitoring
5. **Traffic** - Traffic flow monitoring and incident tracking
6. **Utilities** - Power grid, water system, sewer, flood monitoring
7. **Predictions** - Traffic, crime, infrastructure, population predictions
8. **Simulator** - Event impact simulation (hurricane, flood, major event, outage, traffic incident)
9. **Admin Console** - Manual event input, road closures, emergency declarations

### Components
- `CityBrainDashboard` - Main dashboard overview
- `DigitalTwin3DView` - Digital twin visualization
- `LiveCityHeatmap` - Multi-layer heatmap viewer
- `EnvironmentalPanel` - Weather and environmental data
- `TrafficFlowPanel` - Traffic monitoring
- `UtilityGridPanel` - Utility system status
- `PredictionConsole` - Prediction viewer
- `EventImpactSimulator` - Scenario simulation
- `CityAdminInputForm` - Admin input forms

## DevOps

### Docker Services
- `city-brain` - Main city brain service
- `city-brain-ingestion` - Data ingestion workers
- `city-brain-prediction` - Prediction engine (GPU-enabled)

### GitHub Actions
- `city-brain-selftest.yml` - CI workflow for Phase 22 tests

## Testing

Test suites in `tests/phase22/`:
- `test_city_brain_core.py` - City Brain Core tests
- `test_data_ingestion.py` - Data Ingestion tests
- `test_digital_twin.py` - Digital Twin tests
- `test_prediction_engine.py` - Prediction Engine tests
- `test_city_brain_api.py` - API endpoint tests
- `test_city_brain_websockets.py` - WebSocket channel tests

## Integration with Previous Phases

### Phase 14 (Ops Continuity)
- Health status reporting via `get_health_status()`
- Registration with diagnostics system via `register_with_diagnostics()`

### Phase 15 (Digital Twin)
- Enhanced digital twin with Riviera Beach-specific features
- TimeWarp engine for historical playback and simulation

### Phase 21 (Emergency Management)
- Integration with crisis detection engine
- Evacuation route planning
- Shelter activation coordination

## Usage Examples

### Get City State
```python
from backend.app.city_brain import get_city_brain

brain = get_city_brain()
state = brain.get_city_state()
print(f"Population: {state.population_estimate}")
print(f"Health: {state.overall_health}")
```

### Refresh Data
```python
from backend.app.city_brain.ingestion import DataIngestionManager

manager = DataIngestionManager()
results = await manager.refresh_all()
```

### Get Predictions
```python
from backend.app.city_brain.prediction import CityPredictionEngine

engine = CityPredictionEngine()
forecast = engine.get_comprehensive_forecast(hours_ahead=24)
```

### Create Event via API
```bash
curl -X POST /api/citybrain/admin/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "festival",
    "title": "Summer Festival",
    "description": "Annual summer festival at the marina",
    "start_time": "2024-07-04T10:00:00Z",
    "expected_attendance": 5000,
    "priority": "medium"
  }'
```

## Security Considerations

- All admin endpoints require authentication
- Emergency declarations require elevated permissions
- Sensitive infrastructure data is access-controlled
- WebSocket connections require valid session tokens
- Audit logging for all administrative actions

## Performance

- Data ingestion runs on configurable intervals (default: 5 minutes)
- Predictions are cached and refreshed on demand
- Digital twin updates stream at 1 Hz for object positions
- WebSocket broadcasts are batched for efficiency

## Future Enhancements

- Machine learning model integration for improved predictions
- Real-time video feed integration from city cameras
- Citizen reporting integration
- Smart traffic signal control
- Automated emergency response recommendations
