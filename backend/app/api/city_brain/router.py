"""
Phase 22: City Brain API Router

API endpoints for the AI City Brain Engine.

Endpoints:
- /city/state - Unified city snapshot
- /city/weather - Weather data
- /city/traffic - Traffic conditions
- /city/utility - Utility status
- /city/incidents - Active incidents
- /city/predictions - City predictions
- /city/events - City events
- /city/simulation/play - Simulation playback
- /city/simulation/forecast/{hours} - Future forecast
- /citybrain/admin/* - Admin input console
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
import asyncio


router = APIRouter(prefix="/api/citybrain", tags=["city-brain"])


class EventType(str, Enum):
    FESTIVAL = "festival"
    PARADE = "parade"
    SCHOOL_DISMISSAL = "school_dismissal"
    UTILITY_MAINTENANCE = "utility_maintenance"
    VIP_VISIT = "vip_visit"
    POLICE_OPERATION = "police_operation"
    ROAD_CLOSURE = "road_closure"
    EMERGENCY_DECLARATION = "emergency_declaration"
    SPORTS_EVENT = "sports_event"
    CONCERT = "concert"
    COMMUNITY_EVENT = "community_event"


class EventPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimelineMode(str, Enum):
    LIVE = "live"
    HISTORICAL = "historical"
    SIMULATION = "simulation"


class CityEventInput(BaseModel):
    """Input model for city events."""
    event_type: EventType
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    location: Optional[dict] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    expected_attendance: Optional[int] = None
    affected_roads: Optional[list[str]] = None
    priority: EventPriority = EventPriority.MEDIUM
    notify_patrol: bool = False
    update_predictions: bool = True


class RoadClosureInput(BaseModel):
    """Input model for road closures."""
    road_name: str
    segment_start: dict
    segment_end: dict
    reason: str
    start_time: datetime
    end_time: Optional[datetime] = None
    detour_available: bool = False
    detour_route: Optional[str] = None
    notify_traffic: bool = True


class EmergencyDeclarationInput(BaseModel):
    """Input model for emergency declarations."""
    emergency_type: str
    severity: str
    affected_areas: list[str]
    description: str
    evacuation_required: bool = False
    evacuation_zones: Optional[list[str]] = None
    shelter_activation: bool = False
    effective_time: datetime
    expected_duration_hours: Optional[int] = None


class SimulationRequest(BaseModel):
    """Request model for simulation."""
    mode: TimelineMode
    target_time: Optional[datetime] = None
    playback_speed: float = 1.0
    hours_ahead: Optional[int] = None


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    prediction_type: str
    target_time: datetime
    parameters: Optional[dict] = None


_city_brain = None
_ingestion_manager = None
_digital_twin = None
_prediction_engine = None


def _get_city_brain():
    """Get or initialize city brain instance."""
    global _city_brain
    if _city_brain is None:
        from backend.app.city_brain import get_city_brain
        _city_brain = get_city_brain()
        _city_brain.start()
    return _city_brain


def _get_ingestion_manager():
    """Get or initialize ingestion manager."""
    global _ingestion_manager
    if _ingestion_manager is None:
        from backend.app.city_brain.ingestion import DataIngestionManager
        _ingestion_manager = DataIngestionManager()
    return _ingestion_manager


def _get_digital_twin():
    """Get or initialize digital twin."""
    global _digital_twin
    if _digital_twin is None:
        from backend.app.city_brain.digital_twin import DigitalTwinManager
        _digital_twin = DigitalTwinManager()
        _digital_twin.initialize()
    return _digital_twin


def _get_prediction_engine():
    """Get or initialize prediction engine."""
    global _prediction_engine
    if _prediction_engine is None:
        from backend.app.city_brain.prediction import CityPredictionEngine
        _prediction_engine = CityPredictionEngine()
        _prediction_engine.initialize()
    return _prediction_engine


@router.get("/city/state")
async def get_city_state():
    """
    Get unified city state snapshot.
    
    Returns comprehensive city state including:
    - Weather conditions
    - Traffic status
    - Utility status
    - Active incidents
    - Population estimates
    - Module health
    """
    try:
        city_brain = _get_city_brain()
        state = city_brain.get_city_state()
        
        return {
            "status": "success",
            "timestamp": state.timestamp.isoformat(),
            "city": "Riviera Beach, FL 33404",
            "weather": state.weather,
            "traffic": state.traffic,
            "utilities": state.utilities,
            "incidents": state.incidents,
            "predictions": state.predictions,
            "population_estimate": state.population_estimate,
            "active_events": state.active_events,
            "module_statuses": state.module_statuses,
            "overall_health": state.overall_health,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/weather")
async def get_weather():
    """
    Get current weather data for Riviera Beach.
    
    Includes:
    - Current conditions
    - Active alerts
    - Marine conditions
    - Air quality
    """
    try:
        ingestion = _get_ingestion_manager()
        
        weather_cond = ingestion.weather.get_current_conditions()
        marine_cond = ingestion.marine.get_marine_conditions()
        air_qual = ingestion.air_quality.get_air_quality()
        alerts = ingestion.weather.get_active_alerts()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "current_conditions": weather_cond.__dict__ if weather_cond else None,
            "marine_conditions": marine_cond.__dict__ if marine_cond else None,
            "air_quality": air_qual.__dict__ if air_qual else None,
            "active_alerts": [a.__dict__ for a in alerts],
            "source": "NWS/NOAA/EPA",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/weather/forecast")
async def get_weather_forecast(hours: int = Query(default=72, ge=1, le=168)):
    """Get weather forecast for specified hours."""
    try:
        ingestion = _get_ingestion_manager()
        forecast = await ingestion.weather.fetch_forecast(hours)
        
        return {
            "status": "success",
            "hours": hours,
            "forecast": forecast,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/weather/marine")
async def get_marine_conditions():
    """Get marine and tide conditions."""
    try:
        ingestion = _get_ingestion_manager()
        marine = await ingestion.marine.fetch_marine_conditions()
        tides = await ingestion.marine.fetch_tide_predictions()
        
        return {
            "status": "success",
            "conditions": marine.__dict__ if marine else None,
            "tide_predictions": tides,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/traffic")
async def get_traffic():
    """
    Get current traffic conditions.
    
    Includes:
    - Road segment conditions
    - Active incidents
    - Congestion levels
    """
    try:
        ingestion = _get_ingestion_manager()
        
        incidents = ingestion.traffic.get_incidents()
        conditions = ingestion.traffic.get_conditions()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "incidents": [i.__dict__ for i in incidents],
            "conditions": [c.__dict__ for c in conditions],
            "summary": {
                "total_incidents": len(incidents),
                "congested_segments": sum(
                    1 for c in conditions
                    if c.congestion_level in ["moderate", "heavy", "gridlock"]
                ),
                "total_segments": len(conditions),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/traffic/incidents")
async def get_traffic_incidents():
    """Get active traffic incidents."""
    try:
        ingestion = _get_ingestion_manager()
        incidents = await ingestion.traffic.fetch_incidents()
        
        return {
            "status": "success",
            "incidents": [i.__dict__ for i in incidents],
            "count": len(incidents),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/utility")
async def get_utility_status():
    """
    Get utility system status.
    
    Includes:
    - Power grid status
    - Water system status
    - Sewer system status
    - Flooding indicators
    """
    try:
        ingestion = _get_ingestion_manager()
        
        power_outages = ingestion.power.get_outages()
        grid_status = ingestion.power.get_grid_status()
        water_status = ingestion.utilities.get_water_status()
        sewer_status = ingestion.utilities.get_sewer_status()
        flooding = ingestion.utilities.get_flooding_indicators()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "power": {
                "grid_status": grid_status,
                "outages": [o.__dict__ for o in power_outages],
            },
            "water": [w.__dict__ for w in water_status],
            "sewer": [s.__dict__ for s in sewer_status],
            "flooding": flooding,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/utility/outages")
async def get_power_outages():
    """Get current power outages."""
    try:
        ingestion = _get_ingestion_manager()
        outages = await ingestion.power.fetch_outages()
        grid = await ingestion.power.fetch_grid_status()
        
        return {
            "status": "success",
            "outages": [o.__dict__ for o in outages],
            "grid_status": grid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/incidents")
async def get_incidents():
    """
    Get active public safety incidents.
    
    Includes:
    - Active CAD calls
    - Unit locations
    - Camera status
    """
    try:
        ingestion = _get_ingestion_manager()
        
        calls = ingestion.public_safety.get_active_calls()
        units = ingestion.public_safety.get_unit_locations()
        cameras = ingestion.public_safety.get_camera_status()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "active_calls": calls,
            "unit_locations": units,
            "cameras": cameras,
            "summary": {
                "total_calls": len(calls),
                "units_available": sum(1 for u in units if u.get("status") == "available"),
                "units_busy": sum(1 for u in units if u.get("status") != "available"),
                "cameras_online": sum(1 for c in cameras if c.get("status") == "online"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions")
async def get_predictions(
    hours_ahead: int = Query(default=24, ge=1, le=72),
):
    """
    Get city predictions.
    
    Returns comprehensive forecast including:
    - Traffic predictions
    - Crime displacement
    - Infrastructure risks
    - Population movement
    """
    try:
        engine = _get_prediction_engine()
        target_time = datetime.utcnow() + timedelta(hours=1)
        
        forecast = engine.get_comprehensive_forecast(
            target_time=target_time,
            hours_ahead=hours_ahead,
        )
        
        return {
            "status": "success",
            "forecast": forecast,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions/traffic")
async def get_traffic_predictions(
    segment_id: Optional[str] = None,
    hours_ahead: int = Query(default=24, ge=1, le=72),
):
    """Get traffic flow predictions."""
    try:
        engine = _get_prediction_engine()
        target_time = datetime.utcnow() + timedelta(hours=1)
        
        if segment_id:
            prediction = engine.traffic.predict_congestion(
                segment_id=segment_id,
                target_time=target_time,
            )
            return {
                "status": "success",
                "prediction": {
                    "segment": prediction.road_segment,
                    "congestion": prediction.predicted_congestion_level,
                    "speed_mph": prediction.predicted_speed_mph,
                    "crash_risk": prediction.crash_risk_score,
                    "reroute_recommended": prediction.reroute_recommended,
                    "alternatives": prediction.alternative_routes,
                },
            }
        else:
            predictions = []
            for segment in engine.traffic.ROAD_SEGMENTS:
                pred = engine.traffic.predict_congestion(
                    segment_id=segment["id"],
                    target_time=target_time,
                )
                predictions.append({
                    "segment_id": segment["id"],
                    "segment": pred.road_segment,
                    "congestion": pred.predicted_congestion_level,
                    "speed_mph": pred.predicted_speed_mph,
                })
            
            return {
                "status": "success",
                "predictions": predictions,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions/crime")
async def get_crime_predictions(
    hours_ahead: int = Query(default=24, ge=1, le=72),
):
    """Get crime displacement predictions."""
    try:
        engine = _get_prediction_engine()
        target_time = datetime.utcnow() + timedelta(hours=1)
        
        prediction = engine.crime.predict_displacement(
            target_time=target_time,
            time_window_hours=hours_ahead,
        )
        
        return {
            "status": "success",
            "prediction": {
                "timestamp": prediction.timestamp.isoformat(),
                "time_window_hours": prediction.time_window_hours,
                "displacement_zones": prediction.displacement_zones,
                "risk_increase_areas": prediction.risk_increase_areas,
                "risk_decrease_areas": prediction.risk_decrease_areas,
                "factors": prediction.contributing_factors,
                "patrol_recommendations": prediction.recommended_patrol_adjustments,
                "confidence": prediction.confidence.value,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions/infrastructure")
async def get_infrastructure_predictions():
    """Get infrastructure risk predictions."""
    try:
        engine = _get_prediction_engine()
        target_time = datetime.utcnow() + timedelta(hours=24)
        
        predictions = engine.infrastructure.predict_all_risks(target_time=target_time)
        
        return {
            "status": "success",
            "predictions": [
                {
                    "element_id": p.element_id,
                    "element_name": p.element_name,
                    "type": p.infrastructure_type,
                    "risk_level": p.risk_level.value,
                    "failure_probability": p.failure_probability,
                    "factors": p.contributing_factors,
                    "actions": p.recommended_actions,
                }
                for p in predictions
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions/population")
async def get_population_predictions(
    hours_ahead: int = Query(default=24, ge=1, le=72),
):
    """Get population movement predictions."""
    try:
        engine = _get_prediction_engine()
        target_time = datetime.utcnow() + timedelta(hours=1)
        
        prediction = engine.population.predict_movement(
            target_time=target_time,
            time_window_hours=hours_ahead,
        )
        
        return {
            "status": "success",
            "prediction": {
                "timestamp": prediction.timestamp.isoformat(),
                "area_predictions": prediction.area_predictions,
                "peak_locations": prediction.peak_density_locations,
                "peak_times": [t.isoformat() for t in prediction.peak_times],
                "special_events": prediction.special_events,
                "traffic_impact": prediction.traffic_impact,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/predictions/disaster/{disaster_type}")
async def get_disaster_prediction(
    disaster_type: str,
    category: Optional[int] = None,
    rainfall_inches: Optional[float] = None,
    temperature_f: Optional[float] = None,
):
    """Get disaster impact predictions."""
    try:
        engine = _get_prediction_engine()
        
        if disaster_type == "hurricane" and category:
            prediction = engine.disaster.predict_hurricane_impact(
                category=category,
                landfall_time=datetime.utcnow() + timedelta(hours=48),
            )
        elif disaster_type == "flood" and rainfall_inches:
            prediction = engine.disaster.predict_flood_impact(
                rainfall_inches=rainfall_inches,
                duration_hours=6,
            )
        elif disaster_type == "heat" and temperature_f:
            prediction = engine.disaster.predict_extreme_heat_impact(
                temperature_f=temperature_f,
                heat_index_f=temperature_f + 10,
                duration_days=3,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid disaster type or missing parameters",
            )
        
        return {
            "status": "success",
            "prediction": {
                "disaster_type": prediction.disaster_type.value,
                "severity": prediction.severity,
                "affected_population": prediction.estimated_affected_population,
                "infrastructure_at_risk": prediction.infrastructure_at_risk,
                "estimated_damage_millions": prediction.estimated_damage_millions,
                "evacuation_recommended": prediction.evacuation_recommended,
                "evacuation_zones": prediction.evacuation_zones,
                "timeline": prediction.timeline,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/events")
async def get_city_events():
    """Get active city events."""
    try:
        city_brain = _get_city_brain()
        events = city_brain.get_active_events()
        
        return {
            "status": "success",
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "priority": e.priority.value,
                    "title": e.title,
                    "description": e.description,
                    "location": e.location,
                    "timestamp": e.timestamp.isoformat(),
                    "expires_at": e.expires_at.isoformat() if e.expires_at else None,
                    "acknowledged": e.acknowledged,
                }
                for e in events
            ],
            "count": len(events),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/city/simulation/play")
async def control_simulation(request: SimulationRequest):
    """
    Control simulation playback.
    
    Modes:
    - live: Real-time city state
    - historical: Playback past events
    - simulation: Future prediction simulation
    """
    try:
        twin = _get_digital_twin()
        
        from backend.app.city_brain.digital_twin import TimelineMode as TLMode
        
        mode_map = {
            TimelineMode.LIVE: TLMode.LIVE,
            TimelineMode.HISTORICAL: TLMode.HISTORICAL,
            TimelineMode.SIMULATION: TLMode.SIMULATION,
        }
        
        twin.timewarp.set_mode(mode_map[request.mode])
        
        if request.playback_speed:
            twin.timewarp.set_playback_speed(request.playback_speed)
        
        if request.mode == TimelineMode.HISTORICAL and request.target_time:
            twin.timewarp.set_playback_time(request.target_time)
        
        if request.mode == TimelineMode.SIMULATION and request.hours_ahead:
            twin.timewarp.set_simulation_time(request.hours_ahead)
            simulation_data = twin.timewarp.simulate_future(request.hours_ahead)
        else:
            simulation_data = None
        
        return {
            "status": "success",
            "mode": request.mode.value,
            "current_time": twin.timewarp.get_current_time().isoformat(),
            "playback_speed": twin.timewarp.get_playback_speed(),
            "simulation_data": simulation_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/simulation/forecast/{hours}")
async def get_simulation_forecast(hours: int):
    """
    Get future simulation forecast.
    
    Simulates city state up to 72 hours ahead.
    """
    if hours < 1 or hours > 72:
        raise HTTPException(
            status_code=400,
            detail="Hours must be between 1 and 72",
        )
    
    try:
        twin = _get_digital_twin()
        simulation = twin.timewarp.simulate_future(hours)
        
        return {
            "status": "success",
            "hours": hours,
            "simulation": simulation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/digital-twin")
async def get_digital_twin_state():
    """Get digital twin render data."""
    try:
        twin = _get_digital_twin()
        render_data = twin.get_render_data()
        
        return {
            "status": "success",
            "digital_twin": render_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/digital-twin/objects")
async def get_digital_twin_objects(
    object_type: Optional[str] = None,
):
    """Get dynamic objects in the digital twin."""
    try:
        twin = _get_digital_twin()
        
        if object_type:
            from backend.app.city_brain.digital_twin import ObjectType
            try:
                ot = ObjectType(object_type)
                objects = twin.objects.get_objects_by_type(ot)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid object type: {object_type}",
                )
        else:
            objects = twin.objects.get_all_objects()
        
        return {
            "status": "success",
            "objects": [
                {
                    "id": o.object_id,
                    "type": o.object_type.value,
                    "name": o.name,
                    "status": o.status.value,
                    "location": {
                        "lat": o.location.latitude,
                        "lng": o.location.longitude,
                    },
                }
                for o in objects
            ],
            "count": len(objects),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/city/digital-twin/overlays")
async def get_digital_twin_overlays():
    """Get active overlays in the digital twin."""
    try:
        twin = _get_digital_twin()
        overlays = twin.overlays.get_active_overlays()
        
        return {
            "status": "success",
            "overlays": [
                {
                    "id": o.overlay_id,
                    "type": o.overlay_type.value,
                    "title": o.title,
                    "description": o.description,
                    "severity": o.severity,
                    "geometry": o.geometry,
                }
                for o in overlays
            ],
            "count": len(overlays),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/events")
async def create_city_event(event: CityEventInput):
    """
    Create a new city event.
    
    This will:
    - Add event to city brain
    - Update predictions if requested
    - Appear in digital twin
    - Inform patrol recommendations
    """
    try:
        city_brain = _get_city_brain()
        
        from backend.app.city_brain import CityEvent, CityEventType, EventPriority as EP
        
        event_type_map = {
            EventType.FESTIVAL: CityEventType.SCHEDULED_EVENT,
            EventType.PARADE: CityEventType.SCHEDULED_EVENT,
            EventType.SCHOOL_DISMISSAL: CityEventType.SCHEDULED_EVENT,
            EventType.UTILITY_MAINTENANCE: CityEventType.SCHEDULED_EVENT,
            EventType.VIP_VISIT: CityEventType.SCHEDULED_EVENT,
            EventType.POLICE_OPERATION: CityEventType.SCHEDULED_EVENT,
            EventType.ROAD_CLOSURE: CityEventType.TRAFFIC_INCIDENT,
            EventType.EMERGENCY_DECLARATION: CityEventType.EMERGENCY_DECLARATION,
            EventType.SPORTS_EVENT: CityEventType.SCHEDULED_EVENT,
            EventType.CONCERT: CityEventType.SCHEDULED_EVENT,
            EventType.COMMUNITY_EVENT: CityEventType.SCHEDULED_EVENT,
        }
        
        priority_map = {
            EventPriority.LOW: EP.LOW,
            EventPriority.MEDIUM: EP.MEDIUM,
            EventPriority.HIGH: EP.HIGH,
            EventPriority.CRITICAL: EP.CRITICAL,
        }
        
        import uuid
        
        city_event = CityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type_map.get(event.event_type, CityEventType.SCHEDULED_EVENT),
            priority=priority_map.get(event.priority, EP.MEDIUM),
            title=event.title,
            description=event.description,
            location=event.location,
            timestamp=event.start_time,
            expires_at=event.end_time,
            data={
                "event_subtype": event.event_type.value,
                "expected_attendance": event.expected_attendance,
                "affected_roads": event.affected_roads,
                "notify_patrol": event.notify_patrol,
            },
        )
        
        city_brain.add_event(city_event)
        
        return {
            "status": "success",
            "event_id": city_event.event_id,
            "message": "Event created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/road-closures")
async def create_road_closure(closure: RoadClosureInput):
    """Create a road closure event."""
    try:
        twin = _get_digital_twin()
        
        from backend.app.city_brain.digital_twin import Location
        
        start_loc = Location(
            latitude=closure.segment_start.get("latitude", 0),
            longitude=closure.segment_start.get("longitude", 0),
        )
        end_loc = Location(
            latitude=closure.segment_end.get("latitude", 0),
            longitude=closure.segment_end.get("longitude", 0),
        )
        
        import uuid
        closure_id = str(uuid.uuid4())[:8]
        
        overlay = twin.overlays.create_road_closure_overlay(
            closure_id=closure_id,
            road_name=closure.road_name,
            reason=closure.reason,
            start_point=start_loc,
            end_point=end_loc,
            detour_available=closure.detour_available,
        )
        
        return {
            "status": "success",
            "closure_id": closure_id,
            "overlay_id": overlay.overlay_id,
            "message": "Road closure created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/emergency-declaration")
async def create_emergency_declaration(declaration: EmergencyDeclarationInput):
    """Create an emergency declaration."""
    try:
        city_brain = _get_city_brain()
        
        from backend.app.city_brain import CityEvent, CityEventType, EventPriority as EP
        import uuid
        
        event = CityEvent(
            event_id=str(uuid.uuid4()),
            event_type=CityEventType.EMERGENCY_DECLARATION,
            priority=EP.EMERGENCY,
            title=f"Emergency Declaration: {declaration.emergency_type}",
            description=declaration.description,
            timestamp=declaration.effective_time,
            expires_at=(
                declaration.effective_time + timedelta(hours=declaration.expected_duration_hours)
                if declaration.expected_duration_hours else None
            ),
            data={
                "emergency_type": declaration.emergency_type,
                "severity": declaration.severity,
                "affected_areas": declaration.affected_areas,
                "evacuation_required": declaration.evacuation_required,
                "evacuation_zones": declaration.evacuation_zones,
                "shelter_activation": declaration.shelter_activation,
            },
        )
        
        city_brain.add_event(event)
        
        return {
            "status": "success",
            "event_id": event.event_id,
            "message": "Emergency declaration created",
            "evacuation_required": declaration.evacuation_required,
            "affected_areas": declaration.affected_areas,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/events/{event_id}")
async def acknowledge_event(event_id: str):
    """Acknowledge and clear an event."""
    try:
        city_brain = _get_city_brain()
        success = city_brain.acknowledge_event(event_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Event {event_id} acknowledged",
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Event {event_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_health():
    """Get city brain health status."""
    try:
        city_brain = _get_city_brain()
        health = city_brain.get_health_status()
        
        return {
            "status": "success",
            "health": health,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_city_profile():
    """Get Riviera Beach city profile."""
    try:
        city_brain = _get_city_brain()
        profile = city_brain.get_profile_loader().get_profile()
        
        return {
            "status": "success",
            "profile": profile,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/districts")
async def get_districts():
    """Get city districts."""
    try:
        city_brain = _get_city_brain()
        districts = city_brain.get_profile_loader().get_districts()
        
        return {
            "status": "success",
            "districts": districts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/infrastructure")
async def get_infrastructure():
    """Get critical infrastructure."""
    try:
        city_brain = _get_city_brain()
        infrastructure = city_brain.get_profile_loader().get_critical_infrastructure()
        
        return {
            "status": "success",
            "infrastructure": infrastructure,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/flood-zones")
async def get_flood_zones():
    """Get flood zone information."""
    try:
        city_brain = _get_city_brain()
        flood_zones = city_brain.get_profile_loader().get_flood_zones()
        
        return {
            "status": "success",
            "flood_zones": flood_zones,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/hurricane-zones")
async def get_hurricane_zones():
    """Get hurricane evacuation zones."""
    try:
        city_brain = _get_city_brain()
        hurricane_zones = city_brain.get_profile_loader().get_hurricane_zones()
        
        return {
            "status": "success",
            "hurricane_zones": hurricane_zones,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_data():
    """Refresh all data from ingestion sources."""
    try:
        ingestion = _get_ingestion_manager()
        results = await ingestion.refresh_all()
        
        city_brain = _get_city_brain()
        aggregated = ingestion.get_aggregated_data()
        
        city_brain.update_weather_data(aggregated.get("weather", {}))
        city_brain.update_traffic_data(aggregated.get("traffic", {}))
        city_brain.update_utility_data({
            "power": aggregated.get("power", {}),
            "water": aggregated.get("utilities", {}).get("water", []),
            "sewer": aggregated.get("utilities", {}).get("sewer", []),
            "flooding": aggregated.get("utilities", {}).get("flooding", []),
        })
        city_brain.update_incident_data(aggregated.get("public_safety", {}))
        
        return {
            "status": "success",
            "message": "Data refreshed from all sources",
            "sources_refreshed": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get overall city brain status."""
    try:
        city_brain = _get_city_brain()
        twin = _get_digital_twin()
        engine = _get_prediction_engine()
        ingestion = _get_ingestion_manager()
        
        return {
            "status": "success",
            "city_brain": city_brain.get_health_status(),
            "digital_twin": twin.get_status(),
            "prediction_engine": engine.get_status(),
            "ingestion": ingestion.get_status_summary(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
