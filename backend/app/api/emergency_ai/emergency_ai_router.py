"""
Phase 31: Emergency AI API Router

Endpoints:
- POST /api/emergency-ai/predict
- POST /api/emergency-ai/coordinate
- POST /api/emergency-ai/evac-route
- POST /api/emergency-ai/recovery-plan
- GET /api/emergency-ai/hazards
- GET /api/emergency-ai/resource-status
- GET /api/emergency-ai/shelter-status
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
)
from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
    AgencyType,
    ResourceType,
    TaskPriority,
)
from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    SupplyType,
    InfrastructureType,
)
from backend.app.emergency_ai.communication_intel_engine import (
    CommunicationIntelEngine,
    AlertType,
    AlertPriority,
    Language,
)

router = APIRouter(prefix="/api/emergency-ai", tags=["Emergency AI"])


class HazardPredictionRequest(BaseModel):
    """Request for hazard prediction"""
    hazard_type: str = Field(..., description="Type of hazard to predict")
    noaa_data: Optional[Dict[str, Any]] = Field(None, description="NOAA weather data")
    nhc_data: Optional[Dict[str, Any]] = Field(None, description="NHC hurricane data")
    local_sensor_data: Optional[Dict[str, Any]] = Field(None, description="Local sensor data")
    origin_zone: Optional[str] = Field(None, description="Origin zone for fire/hazmat")
    chemical_name: Optional[str] = Field(None, description="Chemical name for hazmat")
    chemical_class: Optional[str] = Field(None, description="Chemical class for hazmat")
    release_type: Optional[str] = Field(None, description="Release type for hazmat")
    release_quantity_gallons: Optional[float] = Field(None, description="Release quantity")
    infrastructure_type: Optional[str] = Field(None, description="Infrastructure type")
    infrastructure_name: Optional[str] = Field(None, description="Infrastructure name")
    stress_indicators: Optional[Dict[str, Any]] = Field(None, description="Stress indicators")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Weather conditions")


class HazardPredictionResponse(BaseModel):
    """Response for hazard prediction"""
    prediction_id: str
    timestamp: str
    hazard_type: str
    threat_level: int
    threat_level_name: str
    confidence_score: float
    time_to_impact_hours: float
    affected_zones: List[str]
    affected_population: int
    recommended_actions: List[str]
    agencies_required: List[str]
    potential_casualties_prevented: int
    economic_impact_estimate: float
    chain_of_custody_hash: str


class CoordinationRequest(BaseModel):
    """Request for multi-agency coordination"""
    incident_type: str = Field(..., description="Type of incident")
    threat_level: int = Field(..., ge=1, le=5, description="Threat level 1-5")
    affected_zones: List[str] = Field(..., description="List of affected zones")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements")


class CoordinationResponse(BaseModel):
    """Response for multi-agency coordination"""
    plan_id: str
    timestamp: str
    incident_type: str
    threat_level: int
    affected_zones: List[str]
    total_tasks: int
    total_resources_deployed: int
    total_personnel_deployed: int
    estimated_response_time_hours: float
    estimated_completion_time_hours: float
    agency_tasks: List[Dict[str, Any]]
    resource_allocations: List[Dict[str, Any]]
    evacuation_routes: List[Dict[str, Any]]
    shelter_assignments: List[Dict[str, Any]]
    coordination_notes: List[str]
    chain_of_custody_hash: str


class EvacRouteRequest(BaseModel):
    """Request for evacuation route planning"""
    origin_zone: str = Field(..., description="Zone to evacuate from")
    destination_type: str = Field("shelter", description="Destination type")
    special_needs: bool = Field(False, description="Special needs accommodation")
    current_conditions: Optional[Dict[str, Any]] = Field(None, description="Current conditions")


class EvacRouteResponse(BaseModel):
    """Response for evacuation route"""
    route_id: str
    timestamp: str
    origin_zone: str
    destination: str
    destination_type: str
    route_name: str
    distance_miles: float
    estimated_time_minutes: float
    status: str
    road_segments: List[str]
    bridge_crossings: List[str]
    current_traffic_level: str
    flood_risk_segments: List[str]
    capacity_vehicles_per_hour: int
    special_needs_accessible: bool
    alternate_routes: List[str]
    time_to_clear_hours: float
    chain_of_custody_hash: str


class RecoveryPlanRequest(BaseModel):
    """Request for recovery plan"""
    incident_type: str = Field(..., description="Type of incident")
    affected_zones: List[str] = Field(..., description="List of affected zones")
    severity_factor: float = Field(0.5, ge=0.0, le=1.0, description="Severity factor 0-1")


class RecoveryPlanResponse(BaseModel):
    """Response for recovery plan"""
    plan_id: str
    timestamp: str
    incident_type: str
    affected_zones: List[str]
    total_estimated_cost: float
    federal_assistance_estimate: float
    state_assistance_estimate: float
    local_cost_share: float
    insurance_claims_estimate: float
    unmet_needs_estimate: float
    population_affected: int
    housing_units_damaged: int
    businesses_affected: int
    jobs_impacted: int
    economic_impact_estimate: float
    recovery_timeline_days: int
    damage_assessments: List[Dict[str, Any]]
    supply_allocations: List[Dict[str, Any]]
    infrastructure_repairs: List[Dict[str, Any]]
    chain_of_custody_hash: str


class HazardListResponse(BaseModel):
    """Response for active hazards list"""
    timestamp: str
    active_hazards: List[Dict[str, Any]]
    total_count: int
    high_threat_count: int


class ResourceStatusResponse(BaseModel):
    """Response for resource status"""
    timestamp: str
    available_resources: Dict[str, int]
    total_shelter_capacity: int
    total_shelter_occupancy: int
    shelters: List[Dict[str, Any]]


class ShelterStatusResponse(BaseModel):
    """Response for shelter status"""
    timestamp: str
    shelters: List[Dict[str, Any]]
    total_capacity: int
    total_occupancy: int
    available_capacity: int


@router.post("/predict", response_model=HazardPredictionResponse)
async def predict_hazard(request: HazardPredictionRequest) -> HazardPredictionResponse:
    """
    Predict hazard based on type and available data.
    
    Supports:
    - Weather hazards (hurricane, tornado, flooding, storm_surge)
    - Fire hazards (urban_fire, wildfire)
    - Hazmat hazards (hazmat_release, chemical_spill)
    - Infrastructure hazards (bridge_collapse, seawall_failure, power_grid_failure)
    """
    engine = DisasterPredictionEngine()
    
    try:
        hazard_type = HazardType(request.hazard_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hazard type: {request.hazard_type}. Valid types: {[h.value for h in HazardType]}"
        )
    
    kwargs = {}
    
    if hazard_type in [HazardType.HURRICANE, HazardType.TORNADO, HazardType.FLOODING,
                       HazardType.STORM_SURGE, HazardType.SEVERE_THUNDERSTORM]:
        kwargs["noaa_data"] = request.noaa_data
        kwargs["nhc_data"] = request.nhc_data
        kwargs["local_sensor_data"] = request.local_sensor_data
    
    elif hazard_type in [HazardType.URBAN_FIRE, HazardType.WILDFIRE]:
        kwargs["origin_zone"] = request.origin_zone or "Zone_A"
        if request.weather_conditions:
            kwargs["wind_speed_mph"] = request.weather_conditions.get("wind_speed_mph", 10)
            kwargs["humidity_percent"] = request.weather_conditions.get("humidity_percent", 50)
    
    elif hazard_type in [HazardType.HAZMAT_RELEASE, HazardType.CHEMICAL_SPILL]:
        kwargs["chemical_name"] = request.chemical_name or "Unknown"
        kwargs["chemical_class"] = request.chemical_class or "unknown"
        kwargs["release_type"] = request.release_type or "spill"
        kwargs["release_quantity_gallons"] = request.release_quantity_gallons or 100
        kwargs["origin_zone"] = request.origin_zone or "Zone_A"
    
    elif hazard_type in [HazardType.BRIDGE_COLLAPSE, HazardType.SEAWALL_FAILURE,
                         HazardType.POWER_GRID_FAILURE, HazardType.ROADWAY_SUBSIDENCE]:
        kwargs["infrastructure_type"] = request.infrastructure_type or "bridge"
        kwargs["infrastructure_name"] = request.infrastructure_name or "Unknown"
        kwargs["zone"] = request.origin_zone or "Zone_A"
        kwargs["stress_indicators"] = request.stress_indicators
        kwargs["weather_conditions"] = request.weather_conditions
    
    prediction = engine.get_unified_prediction(hazard_type, **kwargs)
    
    return HazardPredictionResponse(
        prediction_id=prediction.prediction_id,
        timestamp=prediction.timestamp.isoformat(),
        hazard_type=prediction.hazard_type.value,
        threat_level=prediction.threat_level.value,
        threat_level_name=prediction.threat_level.name,
        confidence_score=prediction.confidence_score,
        time_to_impact_hours=prediction.time_to_impact_hours,
        affected_zones=prediction.affected_zones,
        affected_population=prediction.affected_population,
        recommended_actions=prediction.recommended_actions,
        agencies_required=prediction.agencies_required,
        potential_casualties_prevented=prediction.potential_casualties_prevented,
        economic_impact_estimate=prediction.economic_impact_estimate,
        chain_of_custody_hash=prediction.chain_of_custody_hash,
    )


@router.post("/coordinate", response_model=CoordinationResponse)
async def coordinate_response(request: CoordinationRequest) -> CoordinationResponse:
    """
    Coordinate multi-agency disaster response.
    
    Automatically coordinates:
    - Police, Fire/Rescue, EMS
    - Public Works, Utilities
    - Hospitals, Red Cross
    - Regional EOCs (for high threat levels)
    """
    engine = ResponseCoordinationEngine()
    
    plan = engine.coordinate_multi_agency_response(
        incident_type=request.incident_type,
        threat_level=request.threat_level,
        affected_zones=request.affected_zones,
        special_requirements=request.special_requirements,
    )
    
    agency_tasks = [
        {
            "task_id": task.task_id,
            "agency": task.agency_type.value,
            "priority": task.priority.value,
            "priority_name": task.priority.name,
            "status": task.status.value,
            "description": task.description,
            "zone": task.location_zone,
            "assigned_units": task.assigned_units,
            "estimated_duration_hours": task.estimated_duration_hours,
        }
        for task in plan.agency_tasks
    ]
    
    resource_allocations = [
        {
            "allocation_id": alloc.allocation_id,
            "resource_type": alloc.resource_type.value,
            "resource_id": alloc.resource_id,
            "zone": alloc.assigned_zone,
            "status": alloc.status,
            "capacity": alloc.capacity,
        }
        for alloc in plan.resource_allocations
    ]
    
    evacuation_routes = [
        {
            "route_id": route.route_id,
            "origin_zone": route.origin_zone,
            "destination": route.destination,
            "route_name": route.route_name,
            "distance_miles": route.distance_miles,
            "estimated_time_minutes": route.estimated_time_minutes,
            "status": route.status.value,
            "time_to_clear_hours": route.time_to_clear_hours,
        }
        for route in plan.evacuation_routes
    ]
    
    shelter_assignments = [
        {
            "shelter_id": shelter.shelter_id,
            "name": shelter.name,
            "zone": shelter.zone,
            "capacity": shelter.capacity,
            "occupancy": shelter.current_occupancy,
            "status": shelter.status,
        }
        for shelter in plan.shelter_assignments
    ]
    
    return CoordinationResponse(
        plan_id=plan.plan_id,
        timestamp=plan.timestamp.isoformat(),
        incident_type=plan.incident_type,
        threat_level=plan.threat_level,
        affected_zones=plan.affected_zones,
        total_tasks=len(plan.agency_tasks),
        total_resources_deployed=plan.total_resources_deployed,
        total_personnel_deployed=plan.total_personnel_deployed,
        estimated_response_time_hours=plan.estimated_response_time_hours,
        estimated_completion_time_hours=plan.estimated_completion_time_hours,
        agency_tasks=agency_tasks,
        resource_allocations=resource_allocations,
        evacuation_routes=evacuation_routes,
        shelter_assignments=shelter_assignments,
        coordination_notes=plan.coordination_notes,
        chain_of_custody_hash=plan.chain_of_custody_hash,
    )


@router.post("/evac-route", response_model=EvacRouteResponse)
async def plan_evacuation_route(request: EvacRouteRequest) -> EvacRouteResponse:
    """
    Plan optimal evacuation route from a zone.
    
    Uses:
    - Road network
    - Live traffic conditions
    - Flood blockages
    - Bridge statuses
    - Special needs accessibility
    """
    engine = ResponseCoordinationEngine()
    
    route = engine.plan_evacuation_route(
        origin_zone=request.origin_zone,
        destination_type=request.destination_type,
        special_needs=request.special_needs,
        current_conditions=request.current_conditions,
    )
    
    return EvacRouteResponse(
        route_id=route.route_id,
        timestamp=route.timestamp.isoformat(),
        origin_zone=route.origin_zone,
        destination=route.destination,
        destination_type=route.destination_type,
        route_name=route.route_name,
        distance_miles=route.distance_miles,
        estimated_time_minutes=route.estimated_time_minutes,
        status=route.status.value,
        road_segments=route.road_segments,
        bridge_crossings=route.bridge_crossings,
        current_traffic_level=route.current_traffic_level,
        flood_risk_segments=route.flood_risk_segments,
        capacity_vehicles_per_hour=route.capacity_vehicles_per_hour,
        special_needs_accessible=route.special_needs_accessible,
        alternate_routes=route.alternate_routes,
        time_to_clear_hours=route.time_to_clear_hours,
        chain_of_custody_hash=route.chain_of_custody_hash,
    )


@router.post("/recovery-plan", response_model=RecoveryPlanResponse)
async def create_recovery_plan(request: RecoveryPlanRequest) -> RecoveryPlanResponse:
    """
    Create comprehensive recovery plan.
    
    Includes:
    - Damage assessments
    - Supply allocations
    - Infrastructure repairs
    - FEMA category mapping
    - Cost and timeline estimation
    """
    planner = RecoveryPlanner()
    
    plan = planner.create_recovery_plan(
        incident_type=request.incident_type,
        affected_zones=request.affected_zones,
        severity_factor=request.severity_factor,
    )
    
    damage_assessments = [
        {
            "assessment_id": assessment.assessment_id,
            "zone": assessment.zone,
            "total_structures": assessment.total_structures_assessed,
            "structures_by_tier": assessment.structures_by_tier,
            "total_damage_estimate": assessment.total_damage_estimate,
            "disaster_impact_index": assessment.disaster_impact_index,
            "displaced_residents": assessment.displaced_residents,
            "priority_repairs": assessment.priority_repairs,
        }
        for assessment in plan.damage_assessments
    ]
    
    supply_allocations = [
        {
            "allocation_id": alloc.allocation_id,
            "supply_type": alloc.supply_type.value,
            "quantity": alloc.quantity,
            "unit": alloc.unit,
            "destination_zone": alloc.destination_zone,
            "beneficiaries_served": alloc.beneficiaries_served,
            "cost": alloc.cost,
        }
        for alloc in plan.supply_allocations
    ]
    
    infrastructure_repairs = [
        {
            "repair_id": repair.repair_id,
            "infrastructure_type": repair.infrastructure_type.value,
            "infrastructure_name": repair.infrastructure_name,
            "zone": repair.zone,
            "estimated_cost": repair.estimated_cost,
            "estimated_days": repair.estimated_days,
            "fema_category": repair.fema_category.value if repair.fema_category else None,
        }
        for repair in plan.infrastructure_repairs
    ]
    
    return RecoveryPlanResponse(
        plan_id=plan.plan_id,
        timestamp=plan.timestamp.isoformat(),
        incident_type=plan.incident_type,
        affected_zones=plan.affected_zones,
        total_estimated_cost=plan.total_estimated_cost,
        federal_assistance_estimate=plan.federal_assistance_estimate,
        state_assistance_estimate=plan.state_assistance_estimate,
        local_cost_share=plan.local_cost_share,
        insurance_claims_estimate=plan.insurance_claims_estimate,
        unmet_needs_estimate=plan.unmet_needs_estimate,
        population_affected=plan.population_affected,
        housing_units_damaged=plan.housing_units_damaged,
        businesses_affected=plan.businesses_affected,
        jobs_impacted=plan.jobs_impacted,
        economic_impact_estimate=plan.economic_impact_estimate,
        recovery_timeline_days=plan.recovery_timeline.total_recovery_days,
        damage_assessments=damage_assessments,
        supply_allocations=supply_allocations,
        infrastructure_repairs=infrastructure_repairs,
        chain_of_custody_hash=plan.chain_of_custody_hash,
    )


@router.get("/hazards", response_model=HazardListResponse)
async def get_active_hazards() -> HazardListResponse:
    """
    Get list of currently active hazards.
    """
    engine = DisasterPredictionEngine()
    
    hazards = engine.get_active_hazards()
    
    high_threat_count = sum(
        1 for h in hazards if h.get("threat_level", 0) >= 4
    )
    
    return HazardListResponse(
        timestamp=datetime.utcnow().isoformat(),
        active_hazards=hazards,
        total_count=len(hazards),
        high_threat_count=high_threat_count,
    )


@router.get("/resource-status", response_model=ResourceStatusResponse)
async def get_resource_status() -> ResourceStatusResponse:
    """
    Get current resource status including available resources and shelters.
    """
    engine = ResponseCoordinationEngine()
    
    status = engine.get_resource_status()
    
    return ResourceStatusResponse(
        timestamp=datetime.utcnow().isoformat(),
        available_resources=status["available_resources"],
        total_shelter_capacity=status["total_shelter_capacity"],
        total_shelter_occupancy=status["total_shelter_occupancy"],
        shelters=status["shelters"],
    )


@router.get("/shelter-status", response_model=ShelterStatusResponse)
async def get_shelter_status() -> ShelterStatusResponse:
    """
    Get detailed shelter status.
    """
    engine = ResponseCoordinationEngine()
    
    shelters = engine.get_shelter_status()
    
    total_capacity = sum(s["capacity"] for s in shelters)
    total_occupancy = sum(s["current_occupancy"] for s in shelters)
    
    return ShelterStatusResponse(
        timestamp=datetime.utcnow().isoformat(),
        shelters=shelters,
        total_capacity=total_capacity,
        total_occupancy=total_occupancy,
        available_capacity=total_capacity - total_occupancy,
    )
