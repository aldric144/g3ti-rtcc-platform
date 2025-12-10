"""
Phase 21: Emergency Management API Router

Comprehensive REST API endpoints for:
- Crisis Detection Engine
- Evacuation AI
- Resource Logistics
- Medical Surge AI
- Multi-Incident Command
- Damage Assessment
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.emergency.crisis_detection_engine import (
    CrisisDetectionEngine,
    CrisisType,
    CrisisSeverity,
)
from backend.app.emergency.evacuation_ai import (
    EvacuationManager,
    EvacuationZone,
    EvacuationPriority,
)
from backend.app.emergency.resource_logistics import (
    ResourceLogisticsManager,
    ShelterStatus,
    ShelterType,
)
from backend.app.emergency.medical_surge_ai import (
    MedicalSurgeManager,
    HospitalStatus,
    TriageLevel,
)
from backend.app.emergency.multi_incident_command import (
    MultiIncidentCommandManager,
    IncidentStatus,
    IncidentPriority,
)
from backend.app.emergency.damage_assessment import (
    DamageAssessmentManager,
    DamageLevel,
)

router = APIRouter(prefix="/api/emergency", tags=["Emergency Management"])

crisis_engine = CrisisDetectionEngine()
evacuation_manager = EvacuationManager()
resource_manager = ResourceLogisticsManager()
medical_manager = MedicalSurgeManager()
command_manager = MultiIncidentCommandManager()
damage_manager = DamageAssessmentManager()


class StormTrackRequest(BaseModel):
    name: str
    category: str
    wind_speed_mph: float
    pressure_mb: float
    position: Dict[str, float]
    movement_direction: str
    movement_speed_mph: float


class FloodPredictionRequest(BaseModel):
    location: Dict[str, Any]
    current_water_level_ft: float
    flood_stage_ft: float
    rainfall_24h_inches: float
    rainfall_forecast_inches: float
    terrain_elevation_ft: float


class FireModelRequest(BaseModel):
    name: str
    origin: Dict[str, float]
    area_acres: float
    containment_percent: float
    wind_speed_mph: float
    wind_direction: str
    humidity_percent: float
    temperature_f: float
    fuel_type: str


class EarthquakeModelRequest(BaseModel):
    magnitude: float
    depth_km: float
    epicenter: Dict[str, float]
    location_description: str


class ExplosionModelRequest(BaseModel):
    location: Dict[str, float]
    explosion_type: str
    estimated_yield_kg_tnt: float
    wind_direction: str
    hazmat_materials: Optional[List[str]] = None


class EvacuationRouteRequest(BaseModel):
    name: str
    origin_zone: str
    destination: Dict[str, Any]
    waypoints: List[Dict[str, float]]
    priority: str = "medium"


class EvacuationOrderRequest(BaseModel):
    zone: str
    priority: str
    reason: str
    effective_at: Optional[datetime] = None


class SpecialNeedsEvacueeRequest(BaseModel):
    name: str
    address: Dict[str, Any]
    categories: List[str]
    medical_equipment: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    caregiver_contact: Optional[Dict[str, str]] = None
    notes: str = ""


class TrafficSimulationRequest(BaseModel):
    scenario_name: str
    zones: List[str]
    duration_hours: float
    vehicle_count: int
    contraflow_enabled: bool = False


class ShelterRequest(BaseModel):
    name: str
    address: Dict[str, Any]
    shelter_type: str
    capacity: int
    amenities: Optional[List[str]] = None
    pet_capacity: int = 0
    medical_capability: bool = False


class SupplyRequest(BaseModel):
    name: str
    category: str
    quantity: int
    unit: str
    location: str
    minimum_stock: int = 0
    supplier: str = ""
    cost_per_unit: float = 0.0


class DeploymentUnitRequest(BaseModel):
    name: str
    deployment_type: str
    personnel_count: int
    equipment: List[str]
    current_location: Dict[str, Any]
    capabilities: Optional[List[str]] = None


class InfrastructureAssetRequest(BaseModel):
    name: str
    infrastructure_type: str
    location: Dict[str, Any]
    capacity: float
    backup_available: bool = False


class HospitalRequest(BaseModel):
    name: str
    address: Dict[str, Any]
    total_beds: int
    icu_beds: int
    er_capacity: int
    trauma_level: int
    specialties: Optional[List[str]] = None


class EMSUnitRequest(BaseModel):
    unit_name: str
    unit_type: str
    current_location: Dict[str, float]
    crew_count: int
    capabilities: Optional[List[str]] = None


class TriagePatientRequest(BaseModel):
    injury_type: str
    injury_description: str
    vital_signs: Dict[str, Any]
    age_group: str
    location_found: Dict[str, Any]


class MedicalSupplyRequest(BaseModel):
    name: str
    category: str
    quantity: int
    unit: str
    location: str
    minimum_stock: int = 0
    critical_threshold: int = 0


class IncidentRoomRequest(BaseModel):
    incident_name: str
    incident_type: str
    priority: str
    location: Dict[str, Any]
    description: str
    commander: str


class TaskRequest(BaseModel):
    room_id: str
    title: str
    description: str
    priority: str
    due_time: Optional[datetime] = None
    dependencies: Optional[List[str]] = None
    resources_required: Optional[List[str]] = None
    location: Optional[Dict[str, Any]] = None


class AgencyRequest(BaseModel):
    name: str
    agency_type: str
    jurisdiction: str
    contact_info: Dict[str, str]
    resources_available: Optional[Dict[str, int]] = None
    personnel_available: int = 0
    capabilities: Optional[List[str]] = None


class DamageAssessmentRequest(BaseModel):
    address: Dict[str, Any]
    structure_type: str
    damage_level: str
    damage_types: List[str]
    damage_description: str
    affected_area_sqft: float
    assessed_by: str


class DroneImageRequest(BaseModel):
    location: Dict[str, float]
    altitude_ft: float
    file_path: str
    resolution: str = "4K"


class RecoveryTimelineRequest(BaseModel):
    area_name: str
    total_structures_affected: int
    damage_summary: Dict[str, int]


@router.get("/metrics")
async def get_emergency_metrics() -> Dict[str, Any]:
    """Get overall emergency management metrics."""
    return {
        "crisis": crisis_engine.get_metrics(),
        "evacuation": evacuation_manager.get_metrics(),
        "resources": resource_manager.get_overall_metrics(),
        "medical": medical_manager.get_overall_metrics(),
        "command": command_manager.get_overall_metrics(),
        "damage": damage_manager.get_overall_metrics(),
    }


@router.post("/crisis/storm")
async def track_storm(request: StormTrackRequest) -> Dict[str, Any]:
    """Track a new storm."""
    storm = crisis_engine.storm_tracker.track_storm(
        name=request.name,
        category=request.category,
        wind_speed_mph=request.wind_speed_mph,
        pressure_mb=request.pressure_mb,
        position=request.position,
        movement_direction=request.movement_direction,
        movement_speed_mph=request.movement_speed_mph,
    )
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "category": storm.category.value,
        "wind_speed_mph": storm.wind_speed_mph,
        "predicted_path": storm.predicted_path,
        "storm_surge_ft": storm.storm_surge_ft,
        "tornado_probability": storm.tornado_probability,
    }


@router.get("/crisis/storms")
async def get_active_storms() -> List[Dict[str, Any]]:
    """Get all active storms."""
    storms = crisis_engine.storm_tracker.get_active_storms()
    return [
        {
            "storm_id": s.storm_id,
            "name": s.name,
            "category": s.category.value,
            "wind_speed_mph": s.wind_speed_mph,
            "current_position": s.current_position,
        }
        for s in storms
    ]


@router.post("/crisis/flood")
async def predict_flood(request: FloodPredictionRequest) -> Dict[str, Any]:
    """Predict flood risk for a location."""
    prediction = crisis_engine.flood_predictor.predict_flood(
        location=request.location,
        current_water_level_ft=request.current_water_level_ft,
        flood_stage_ft=request.flood_stage_ft,
        rainfall_24h_inches=request.rainfall_24h_inches,
        rainfall_forecast_inches=request.rainfall_forecast_inches,
        terrain_elevation_ft=request.terrain_elevation_ft,
    )
    return {
        "prediction_id": prediction.prediction_id,
        "flood_risk": prediction.flood_risk.value,
        "predicted_water_level_ft": prediction.predicted_water_level_ft,
        "time_to_flood_hours": prediction.time_to_flood_hours,
        "evacuation_recommended": prediction.evacuation_recommended,
        "confidence_score": prediction.confidence_score,
    }


@router.post("/crisis/fire")
async def model_fire(request: FireModelRequest) -> Dict[str, Any]:
    """Model fire spread."""
    fire = crisis_engine.fire_model.model_fire(
        name=request.name,
        origin=request.origin,
        area_acres=request.area_acres,
        containment_percent=request.containment_percent,
        wind_speed_mph=request.wind_speed_mph,
        wind_direction=request.wind_direction,
        humidity_percent=request.humidity_percent,
        temperature_f=request.temperature_f,
        fuel_type=request.fuel_type,
    )
    return {
        "fire_id": fire.fire_id,
        "name": fire.name,
        "area_acres": fire.area_acres,
        "spread_rate": fire.spread_rate.value,
        "spread_direction": fire.spread_direction,
        "structures_threatened": fire.structures_threatened,
        "evacuation_zones": fire.evacuation_zones,
    }


@router.get("/crisis/fires")
async def get_active_fires() -> List[Dict[str, Any]]:
    """Get all active fires."""
    fires = crisis_engine.fire_model.get_active_fires()
    return [
        {
            "fire_id": f.fire_id,
            "name": f.name,
            "area_acres": f.area_acres,
            "containment_percent": f.containment_percent,
            "spread_rate": f.spread_rate.value,
        }
        for f in fires
    ]


@router.post("/crisis/earthquake")
async def model_earthquake(request: EarthquakeModelRequest) -> Dict[str, Any]:
    """Model earthquake impact."""
    earthquake = crisis_engine.earthquake_model.model_earthquake(
        magnitude=request.magnitude,
        depth_km=request.depth_km,
        epicenter=request.epicenter,
        location_description=request.location_description,
    )
    return {
        "earthquake_id": earthquake.earthquake_id,
        "magnitude": earthquake.magnitude,
        "depth_km": earthquake.depth_km,
        "shake_intensity": earthquake.shake_intensity,
        "affected_radius_km": earthquake.affected_radius_km,
        "population_affected": earthquake.population_affected,
        "aftershock_probability": earthquake.aftershock_probability,
        "tsunami_risk": earthquake.tsunami_risk,
    }


@router.post("/crisis/explosion")
async def model_explosion(request: ExplosionModelRequest) -> Dict[str, Any]:
    """Model explosion impact."""
    explosion = crisis_engine.explosion_model.model_explosion(
        location=request.location,
        explosion_type=request.explosion_type,
        estimated_yield_kg_tnt=request.estimated_yield_kg_tnt,
        wind_direction=request.wind_direction,
        hazmat_materials=request.hazmat_materials,
    )
    return {
        "explosion_id": explosion.explosion_id,
        "explosion_type": explosion.explosion_type,
        "blast_radius_m": explosion.blast_radius_m,
        "thermal_radius_m": explosion.thermal_radius_m,
        "evacuation_radius_m": explosion.evacuation_radius_m,
        "hazmat_risk": explosion.hazmat_risk,
        "casualties_estimate": explosion.casualties_estimate,
    }


@router.get("/crisis/alerts")
async def get_crisis_alerts(
    crisis_type: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get all crisis alerts."""
    alerts = crisis_engine.get_all_active_alerts()

    if crisis_type:
        ct = CrisisType(crisis_type)
        alerts = [a for a in alerts if a.crisis_type == ct]

    if severity:
        sev = CrisisSeverity(severity)
        alerts = [a for a in alerts if a.severity == sev]

    return [
        {
            "alert_id": a.alert_id,
            "crisis_type": a.crisis_type.value,
            "severity": a.severity.value,
            "alert_level": a.alert_level.value,
            "title": a.title,
            "description": a.description,
            "location": a.location,
            "affected_area_km2": a.affected_area_km2,
            "population_at_risk": a.population_at_risk,
            "recommendations": a.recommendations,
        }
        for a in alerts
    ]


@router.get("/crisis/critical")
async def get_critical_alerts() -> List[Dict[str, Any]]:
    """Get critical and emergency level alerts."""
    alerts = crisis_engine.get_critical_alerts()
    return [
        {
            "alert_id": a.alert_id,
            "crisis_type": a.crisis_type.value,
            "severity": a.severity.value,
            "title": a.title,
            "population_at_risk": a.population_at_risk,
        }
        for a in alerts
    ]


@router.post("/evacuation/route")
async def create_evacuation_route(request: EvacuationRouteRequest) -> Dict[str, Any]:
    """Create an evacuation route."""
    route = evacuation_manager.route_optimizer.create_route(
        name=request.name,
        origin_zone=request.origin_zone,
        destination=request.destination,
        waypoints=request.waypoints,
        priority=request.priority,
    )
    return {
        "route_id": route.route_id,
        "name": route.name,
        "origin_zone": route.origin_zone.value,
        "distance_miles": route.distance_miles,
        "estimated_time_minutes": route.estimated_time_minutes,
        "capacity_vehicles_per_hour": route.capacity_vehicles_per_hour,
        "status": route.status.value,
    }


@router.get("/evacuation/routes")
async def get_evacuation_routes(zone: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get evacuation routes."""
    zone_enum = EvacuationZone(zone) if zone else None
    routes = evacuation_manager.route_optimizer.get_routes(zone_enum)
    return [
        {
            "route_id": r.route_id,
            "name": r.name,
            "origin_zone": r.origin_zone.value,
            "distance_miles": r.distance_miles,
            "status": r.status.value,
        }
        for r in routes
    ]


@router.post("/evacuation/route/{route_id}/contraflow")
async def enable_contraflow(route_id: str) -> Dict[str, Any]:
    """Enable contraflow on a route."""
    route = evacuation_manager.route_optimizer.enable_contraflow(route_id)
    return {
        "route_id": route.route_id,
        "contraflow_enabled": route.contraflow_enabled,
        "capacity_vehicles_per_hour": route.capacity_vehicles_per_hour,
    }


@router.post("/evacuation/order")
async def issue_evacuation_order(request: EvacuationOrderRequest) -> Dict[str, Any]:
    """Issue an evacuation order."""
    order = evacuation_manager.issue_evacuation_order(
        zone=request.zone,
        priority=request.priority,
        reason=request.reason,
        effective_at=request.effective_at,
    )
    return {
        "order_id": order.order_id,
        "zone": order.zone.value,
        "priority": order.priority.value,
        "affected_population": order.affected_population,
        "recommended_routes": order.recommended_routes,
        "shelter_assignments": order.shelter_assignments,
        "special_instructions": order.special_instructions,
    }


@router.get("/evacuation/orders")
async def get_evacuation_orders() -> List[Dict[str, Any]]:
    """Get active evacuation orders."""
    orders = evacuation_manager.get_active_orders()
    return [
        {
            "order_id": o.order_id,
            "zone": o.zone.value,
            "priority": o.priority.value,
            "affected_population": o.affected_population,
            "is_active": o.is_active,
        }
        for o in orders
    ]


@router.post("/evacuation/special-needs")
async def register_special_needs_evacuee(request: SpecialNeedsEvacueeRequest) -> Dict[str, Any]:
    """Register a special needs evacuee."""
    evacuee = evacuation_manager.special_needs_planner.register_evacuee(
        name=request.name,
        address=request.address,
        categories=request.categories,
        medical_equipment=request.medical_equipment,
        medications=request.medications,
        caregiver_contact=request.caregiver_contact,
        notes=request.notes,
    )
    return {
        "evacuee_id": evacuee.evacuee_id,
        "name": evacuee.name,
        "categories": [c.value for c in evacuee.categories],
        "transport_requirements": [t.value for t in evacuee.transport_requirements],
        "evacuation_status": evacuee.evacuation_status,
    }


@router.get("/evacuation/special-needs")
async def get_special_needs_evacuees(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get special needs evacuees."""
    evacuees = evacuation_manager.special_needs_planner.get_evacuees(status=status)
    return [
        {
            "evacuee_id": e.evacuee_id,
            "name": e.name,
            "categories": [c.value for c in e.categories],
            "evacuation_status": e.evacuation_status,
            "assigned_transport": e.assigned_transport,
        }
        for e in evacuees
    ]


@router.post("/evacuation/simulation")
async def run_traffic_simulation(request: TrafficSimulationRequest) -> Dict[str, Any]:
    """Run traffic simulation."""
    simulation = evacuation_manager.traffic_simulator.run_simulation(
        scenario_name=request.scenario_name,
        zones=request.zones,
        duration_hours=request.duration_hours,
        vehicle_count=request.vehicle_count,
        contraflow_enabled=request.contraflow_enabled,
    )
    return {
        "simulation_id": simulation.simulation_id,
        "scenario_name": simulation.scenario_name,
        "total_vehicles": simulation.total_vehicles,
        "average_speed_mph": simulation.average_speed_mph,
        "clearance_time_hours": simulation.clearance_time_hours,
        "bottleneck_locations": simulation.bottleneck_locations,
        "recommendations": simulation.recommendations,
    }


@router.get("/evacuation/metrics")
async def get_evacuation_metrics() -> Dict[str, Any]:
    """Get evacuation metrics."""
    return evacuation_manager.get_metrics()


@router.post("/resources/shelter")
async def register_shelter(request: ShelterRequest) -> Dict[str, Any]:
    """Register a shelter."""
    shelter = resource_manager.shelter_registry.register_shelter(
        name=request.name,
        address=request.address,
        shelter_type=request.shelter_type,
        capacity=request.capacity,
        amenities=request.amenities,
        pet_capacity=request.pet_capacity,
        medical_capability=request.medical_capability,
    )
    return {
        "shelter_id": shelter.shelter_id,
        "name": shelter.name,
        "shelter_type": shelter.shelter_type.value,
        "capacity": shelter.capacity,
        "status": shelter.status.value,
    }


@router.post("/resources/shelter/{shelter_id}/open")
async def open_shelter(shelter_id: str, staff_count: int) -> Dict[str, Any]:
    """Open a shelter."""
    shelter = resource_manager.shelter_registry.open_shelter(shelter_id, staff_count)
    return {
        "shelter_id": shelter.shelter_id,
        "status": shelter.status.value,
        "staff_count": shelter.staff_count,
    }


@router.put("/resources/shelter/{shelter_id}/occupancy")
async def update_shelter_occupancy(shelter_id: str, occupancy: int) -> Dict[str, Any]:
    """Update shelter occupancy."""
    shelter = resource_manager.shelter_registry.update_occupancy(shelter_id, occupancy)
    return {
        "shelter_id": shelter.shelter_id,
        "current_occupancy": shelter.current_occupancy,
        "capacity": shelter.capacity,
        "status": shelter.status.value,
    }


@router.get("/resources/shelters")
async def get_shelters(
    status: Optional[str] = None,
    shelter_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get shelters."""
    status_enum = ShelterStatus(status) if status else None
    type_enum = ShelterType(shelter_type) if shelter_type else None
    shelters = resource_manager.shelter_registry.get_shelters(status_enum, type_enum)
    return [
        {
            "shelter_id": s.shelter_id,
            "name": s.name,
            "shelter_type": s.shelter_type.value,
            "capacity": s.capacity,
            "current_occupancy": s.current_occupancy,
            "status": s.status.value,
        }
        for s in shelters
    ]


@router.get("/resources/shelters/capacity")
async def get_shelter_capacity() -> Dict[str, Any]:
    """Get available shelter capacity."""
    return {
        "available_capacity": resource_manager.shelter_registry.get_available_capacity(),
        "metrics": resource_manager.shelter_registry.get_metrics(),
    }


@router.post("/resources/supply")
async def add_supply(request: SupplyRequest) -> Dict[str, Any]:
    """Add supply to inventory."""
    item = resource_manager.supply_chain.add_inventory(
        name=request.name,
        category=request.category,
        quantity=request.quantity,
        unit=request.unit,
        location=request.location,
        minimum_stock=request.minimum_stock,
        supplier=request.supplier,
        cost_per_unit=request.cost_per_unit,
    )
    return {
        "item_id": item.item_id,
        "name": item.name,
        "category": item.category.value,
        "quantity": item.quantity,
        "status": item.status.value,
    }


@router.get("/resources/supplies")
async def get_supplies(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get supplies."""
    from backend.app.emergency.resource_logistics import SupplyCategory
    cat_enum = SupplyCategory(category) if category else None
    items = resource_manager.supply_chain.get_inventory(cat_enum)
    return [
        {
            "item_id": i.item_id,
            "name": i.name,
            "category": i.category.value,
            "quantity": i.quantity,
            "status": i.status.value,
        }
        for i in items
    ]


@router.get("/resources/supplies/low-stock")
async def get_low_stock_supplies() -> List[Dict[str, Any]]:
    """Get low stock supplies."""
    items = resource_manager.supply_chain.get_low_stock_items()
    return [
        {
            "item_id": i.item_id,
            "name": i.name,
            "quantity": i.quantity,
            "minimum_stock": i.minimum_stock,
        }
        for i in items
    ]


@router.post("/resources/deployment")
async def register_deployment_unit(request: DeploymentUnitRequest) -> Dict[str, Any]:
    """Register a deployment unit."""
    unit = resource_manager.deployment_allocator.register_unit(
        name=request.name,
        deployment_type=request.deployment_type,
        personnel_count=request.personnel_count,
        equipment=request.equipment,
        current_location=request.current_location,
        capabilities=request.capabilities,
    )
    return {
        "unit_id": unit.unit_id,
        "name": unit.name,
        "deployment_type": unit.deployment_type.value,
        "personnel_count": unit.personnel_count,
        "status": unit.status.value,
    }


@router.post("/resources/deployment/{unit_id}/deploy")
async def deploy_unit(
    unit_id: str,
    location: Dict[str, Any],
    mission: str,
    duration_hours: float,
) -> Dict[str, Any]:
    """Deploy a unit."""
    unit = resource_manager.deployment_allocator.deploy_unit(
        unit_id, location, mission, duration_hours
    )
    return {
        "unit_id": unit.unit_id,
        "status": unit.status.value,
        "assigned_location": unit.assigned_location,
    }


@router.get("/resources/deployments")
async def get_deployment_units() -> List[Dict[str, Any]]:
    """Get deployment units."""
    units = resource_manager.deployment_allocator.get_units()
    return [
        {
            "unit_id": u.unit_id,
            "name": u.name,
            "deployment_type": u.deployment_type.value,
            "status": u.status.value,
        }
        for u in units
    ]


@router.post("/resources/infrastructure")
async def register_infrastructure(request: InfrastructureAssetRequest) -> Dict[str, Any]:
    """Register infrastructure asset."""
    asset = resource_manager.infrastructure_monitor.register_asset(
        name=request.name,
        infrastructure_type=request.infrastructure_type,
        location=request.location,
        capacity=request.capacity,
        backup_available=request.backup_available,
    )
    return {
        "asset_id": asset.asset_id,
        "name": asset.name,
        "infrastructure_type": asset.infrastructure_type.value,
        "status": asset.status.value,
    }


@router.put("/resources/infrastructure/{asset_id}/status")
async def update_infrastructure_status(
    asset_id: str,
    status: str,
    affected_population: int = 0,
) -> Dict[str, Any]:
    """Update infrastructure status."""
    asset = resource_manager.infrastructure_monitor.update_status(
        asset_id, status, affected_population
    )
    return {
        "asset_id": asset.asset_id,
        "status": asset.status.value,
        "affected_population": asset.affected_population,
    }


@router.get("/resources/infrastructure/outages")
async def get_infrastructure_outages() -> List[Dict[str, Any]]:
    """Get infrastructure outages."""
    return resource_manager.infrastructure_monitor.get_outages()


@router.get("/resources/metrics")
async def get_resource_metrics() -> Dict[str, Any]:
    """Get resource logistics metrics."""
    return resource_manager.get_overall_metrics()


@router.post("/medical/hospital")
async def register_hospital(request: HospitalRequest) -> Dict[str, Any]:
    """Register a hospital."""
    hospital = medical_manager.hospital_predictor.register_hospital(
        name=request.name,
        address=request.address,
        total_beds=request.total_beds,
        icu_beds=request.icu_beds,
        er_capacity=request.er_capacity,
        trauma_level=request.trauma_level,
        specialties=request.specialties,
    )
    return {
        "hospital_id": hospital.hospital_id,
        "name": hospital.name,
        "status": hospital.status.value,
        "total_beds": hospital.total_beds,
        "available_beds": hospital.available_beds,
    }


@router.put("/medical/hospital/{hospital_id}/status")
async def update_hospital_status(
    hospital_id: str,
    available_beds: Optional[int] = None,
    icu_available: Optional[int] = None,
    er_current: Optional[int] = None,
    ambulance_divert: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update hospital status."""
    hospital = medical_manager.hospital_predictor.update_hospital_status(
        hospital_id, available_beds, icu_available, er_current, ambulance_divert
    )
    return {
        "hospital_id": hospital.hospital_id,
        "status": hospital.status.value,
        "available_beds": hospital.available_beds,
        "ambulance_divert": hospital.ambulance_divert,
    }


@router.post("/medical/hospital/{hospital_id}/predict")
async def predict_hospital_load(
    hospital_id: str,
    incident_type: str,
    estimated_casualties: int,
    hours_ahead: int = 24,
) -> Dict[str, Any]:
    """Predict hospital load."""
    prediction = medical_manager.hospital_predictor.predict_load(
        hospital_id, incident_type, estimated_casualties, hours_ahead
    )
    return {
        "prediction_id": prediction.prediction_id,
        "predicted_er_arrivals": prediction.predicted_er_arrivals,
        "predicted_admissions": prediction.predicted_admissions,
        "predicted_icu_demand": prediction.predicted_icu_demand,
        "predicted_surge_level": prediction.predicted_surge_level.value,
        "recommendations": prediction.recommendations,
    }


@router.get("/medical/hospitals")
async def get_hospitals(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get hospitals."""
    status_enum = HospitalStatus(status) if status else None
    hospitals = medical_manager.hospital_predictor.get_hospitals(status_enum)
    return [
        {
            "hospital_id": h.hospital_id,
            "name": h.name,
            "status": h.status.value,
            "available_beds": h.available_beds,
            "ambulance_divert": h.ambulance_divert,
        }
        for h in hospitals
    ]


@router.get("/medical/capacity")
async def get_regional_capacity() -> Dict[str, Any]:
    """Get regional hospital capacity."""
    return medical_manager.hospital_predictor.get_regional_capacity()


@router.post("/medical/ems")
async def register_ems_unit(request: EMSUnitRequest) -> Dict[str, Any]:
    """Register an EMS unit."""
    unit = medical_manager.ems_forecaster.register_unit(
        unit_name=request.unit_name,
        unit_type=request.unit_type,
        current_location=request.current_location,
        crew_count=request.crew_count,
        capabilities=request.capabilities,
    )
    return {
        "unit_id": unit.unit_id,
        "unit_name": unit.unit_name,
        "status": unit.status.value,
    }


@router.post("/medical/ems/forecast")
async def forecast_ems_demand(
    incident_type: str,
    affected_population: int,
    duration_hours: int,
) -> Dict[str, Any]:
    """Forecast EMS demand."""
    forecast = medical_manager.ems_forecaster.forecast_demand(
        incident_type, affected_population, duration_hours
    )
    return {
        "forecast_id": forecast.forecast_id,
        "predicted_calls": forecast.predicted_calls,
        "predicted_transports": forecast.predicted_transports,
        "predicted_als_calls": forecast.predicted_als_calls,
        "peak_hours": forecast.peak_hours,
        "recommended_staging": forecast.recommended_staging,
    }


@router.post("/medical/triage")
async def triage_patient(request: TriagePatientRequest) -> Dict[str, Any]:
    """Triage a patient."""
    patient = medical_manager.triage_model.triage_patient(
        injury_type=request.injury_type,
        injury_description=request.injury_description,
        vital_signs=request.vital_signs,
        age_group=request.age_group,
        location_found=request.location_found,
    )
    return {
        "patient_id": patient.patient_id,
        "triage_level": patient.triage_level.value,
        "injury_type": patient.injury_type.value,
        "transport_status": patient.transport_status,
    }


@router.get("/medical/triage/immediate")
async def get_immediate_patients() -> List[Dict[str, Any]]:
    """Get patients requiring immediate care."""
    patients = medical_manager.triage_model.get_immediate_patients()
    return [
        {
            "patient_id": p.patient_id,
            "triage_level": p.triage_level.value,
            "injury_type": p.injury_type.value,
            "transport_status": p.transport_status,
        }
        for p in patients
    ]


@router.post("/medical/supply")
async def add_medical_supply(request: MedicalSupplyRequest) -> Dict[str, Any]:
    """Add medical supply."""
    supply = medical_manager.supply_tracker.add_supply(
        name=request.name,
        category=request.category,
        quantity=request.quantity,
        unit=request.unit,
        location=request.location,
        minimum_stock=request.minimum_stock,
        critical_threshold=request.critical_threshold,
    )
    return {
        "supply_id": supply.supply_id,
        "name": supply.name,
        "category": supply.category.value,
        "quantity": supply.quantity,
    }


@router.get("/medical/supplies/critical")
async def get_critical_medical_supplies() -> List[Dict[str, Any]]:
    """Get critical medical supplies."""
    supplies = medical_manager.supply_tracker.get_critical_supplies()
    return [
        {
            "supply_id": s.supply_id,
            "name": s.name,
            "quantity": s.quantity,
            "critical_threshold": s.critical_threshold,
        }
        for s in supplies
    ]


@router.get("/medical/metrics")
async def get_medical_metrics() -> Dict[str, Any]:
    """Get medical surge metrics."""
    return medical_manager.get_overall_metrics()


@router.get("/medical/critical-status")
async def get_medical_critical_status() -> Dict[str, Any]:
    """Get critical medical status."""
    return medical_manager.get_critical_status()


@router.post("/command/room")
async def create_incident_room(request: IncidentRoomRequest) -> Dict[str, Any]:
    """Create an incident command room."""
    room = command_manager.room_manager.create_room(
        incident_name=request.incident_name,
        incident_type=request.incident_type,
        priority=request.priority,
        location=request.location,
        description=request.description,
        commander=request.commander,
    )
    return {
        "room_id": room.room_id,
        "incident_name": room.incident_name,
        "status": room.status.value,
        "priority": room.priority.value,
    }


@router.put("/command/room/{room_id}/status")
async def update_room_status(
    room_id: str,
    status: str,
    affected_population: Optional[int] = None,
    casualties: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Update incident room status."""
    room = command_manager.room_manager.update_room_status(
        room_id, status, affected_population, casualties
    )
    return {
        "room_id": room.room_id,
        "status": room.status.value,
        "affected_population": room.affected_population,
        "casualties": room.casualties,
    }


@router.post("/command/room/{room_id}/agency")
async def add_agency_to_room(room_id: str, agency_name: str) -> Dict[str, Any]:
    """Add an agency to the incident room."""
    room = command_manager.room_manager.add_agency(room_id, agency_name)
    return {
        "room_id": room.room_id,
        "agencies_involved": room.agencies_involved,
    }


@router.get("/command/rooms")
async def get_incident_rooms(
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get incident rooms."""
    status_enum = IncidentStatus(status) if status else None
    priority_enum = IncidentPriority(priority) if priority else None
    rooms = command_manager.room_manager.get_rooms(status_enum, priority_enum)
    return [
        {
            "room_id": r.room_id,
            "incident_name": r.incident_name,
            "status": r.status.value,
            "priority": r.priority.value,
            "affected_population": r.affected_population,
        }
        for r in rooms
    ]


@router.post("/command/room/{room_id}/brief")
async def generate_incident_brief(
    room_id: str,
    brief_type: str = "situation",
) -> Dict[str, Any]:
    """Generate an incident brief."""
    brief = command_manager.brief_builder.generate_brief(room_id, brief_type)
    return {
        "brief_id": brief.brief_id,
        "title": brief.title,
        "situation_summary": brief.situation_summary,
        "key_developments": brief.key_developments,
        "immediate_priorities": brief.immediate_priorities,
        "pending_decisions": brief.pending_decisions,
    }


@router.post("/command/task")
async def create_task(request: TaskRequest) -> Dict[str, Any]:
    """Create a task."""
    task = command_manager.task_engine.create_task(
        room_id=request.room_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_time=request.due_time,
        dependencies=request.dependencies,
        resources_required=request.resources_required,
        location=request.location,
    )
    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
    }


@router.post("/command/task/{task_id}/assign")
async def assign_task(
    task_id: str,
    assigned_to: str,
    assigned_agency: str,
) -> Dict[str, Any]:
    """Assign a task."""
    task = command_manager.task_engine.assign_task(task_id, assigned_to, assigned_agency)
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "assigned_to": task.assigned_to,
        "assigned_agency": task.assigned_agency,
    }


@router.post("/command/task/{task_id}/complete")
async def complete_task(task_id: str, notes: str = "") -> Dict[str, Any]:
    """Complete a task."""
    task = command_manager.task_engine.complete_task(task_id, notes)
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@router.get("/command/room/{room_id}/tasks")
async def get_room_tasks(room_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get tasks for a room."""
    from backend.app.emergency.multi_incident_command import TaskStatus
    status_enum = TaskStatus(status) if status else None
    tasks = command_manager.task_engine.get_room_tasks(room_id, status_enum)
    return [
        {
            "task_id": t.task_id,
            "title": t.title,
            "status": t.status.value,
            "priority": t.priority.value,
            "assigned_to": t.assigned_to,
        }
        for t in tasks
    ]


@router.post("/command/timeline/event")
async def add_timeline_event(
    room_id: str,
    event_type: str,
    title: str,
    description: str,
    source: str = "System",
) -> Dict[str, Any]:
    """Add a timeline event."""
    event = command_manager.timeline.add_event(
        room_id, event_type, title, description, source=source
    )
    return {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "title": event.title,
        "timestamp": event.timestamp.isoformat(),
    }


@router.get("/command/room/{room_id}/timeline")
async def get_room_timeline(room_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get timeline for a room."""
    events = command_manager.timeline.get_recent_events(room_id, limit)
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type.value,
            "title": e.title,
            "description": e.description,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events
    ]


@router.post("/command/agency")
async def register_agency(request: AgencyRequest) -> Dict[str, Any]:
    """Register an agency."""
    agency = command_manager.eoc_coordinator.register_agency(
        name=request.name,
        agency_type=request.agency_type,
        jurisdiction=request.jurisdiction,
        contact_info=request.contact_info,
        resources_available=request.resources_available,
        personnel_available=request.personnel_available,
        capabilities=request.capabilities,
    )
    return {
        "agency_id": agency.agency_id,
        "name": agency.name,
        "agency_type": agency.agency_type.value,
    }


@router.post("/command/eoc/activate")
async def activate_eoc(name: str, activation_level: int) -> Dict[str, Any]:
    """Activate the EOC."""
    eoc = command_manager.eoc_coordinator.activate_eoc(name, activation_level)
    return {
        "eoc_id": eoc.eoc_id,
        "name": eoc.name,
        "activation_level": eoc.activation_level,
        "status": eoc.status,
    }


@router.post("/command/eoc/join")
async def join_eoc(agency_id: str, liaison_officer: str) -> Dict[str, Any]:
    """Add an agency to the EOC."""
    agency = command_manager.eoc_coordinator.join_eoc(agency_id, liaison_officer)
    return {
        "agency_id": agency.agency_id,
        "name": agency.name,
        "liaison_officer": agency.liaison_officer,
    }


@router.get("/command/eoc/status")
async def get_eoc_status() -> Dict[str, Any]:
    """Get EOC status."""
    eoc = command_manager.eoc_coordinator.get_eoc_status()
    if not eoc:
        return {"status": "not_activated"}
    return {
        "eoc_id": eoc.eoc_id,
        "name": eoc.name,
        "activation_level": eoc.activation_level,
        "status": eoc.status,
        "agencies_present": eoc.agencies_present,
        "active_incidents": eoc.active_incidents,
    }


@router.get("/command/metrics")
async def get_command_metrics() -> Dict[str, Any]:
    """Get command metrics."""
    return command_manager.get_overall_metrics()


@router.get("/command/summary")
async def get_command_summary() -> Dict[str, Any]:
    """Get command summary."""
    return command_manager.get_command_summary()


@router.post("/damage/assessment")
async def create_damage_assessment(request: DamageAssessmentRequest) -> Dict[str, Any]:
    """Create a damage assessment."""
    assessment = damage_manager.create_assessment(
        address=request.address,
        structure_type=request.structure_type,
        damage_level=request.damage_level,
        damage_types=request.damage_types,
        damage_description=request.damage_description,
        affected_area_sqft=request.affected_area_sqft,
        assessed_by=request.assessed_by,
    )
    return {
        "assessment_id": assessment.assessment_id,
        "structure_type": assessment.structure_type.value,
        "damage_level": assessment.damage_level.value,
        "habitability": assessment.habitability,
    }


@router.get("/damage/assessments")
async def get_damage_assessments(
    damage_level: Optional[str] = None,
    structure_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get damage assessments."""
    from backend.app.emergency.damage_assessment import StructureType
    level_enum = DamageLevel(damage_level) if damage_level else None
    type_enum = StructureType(structure_type) if structure_type else None
    assessments = damage_manager.get_assessments(level_enum, type_enum)
    return [
        {
            "assessment_id": a.assessment_id,
            "structure_type": a.structure_type.value,
            "damage_level": a.damage_level.value,
            "habitability": a.habitability,
        }
        for a in assessments
    ]


@router.post("/damage/drone-image")
async def upload_drone_image(request: DroneImageRequest) -> Dict[str, Any]:
    """Upload a drone image."""
    image = damage_manager.drone_classifier.upload_image(
        location=request.location,
        altitude_ft=request.altitude_ft,
        file_path=request.file_path,
        resolution=request.resolution,
    )
    return {
        "image_id": image.image_id,
        "location": image.location,
        "processed": image.processed,
    }


@router.post("/damage/drone-image/{image_id}/process")
async def process_drone_image(image_id: str) -> Dict[str, Any]:
    """Process a drone image."""
    image = damage_manager.drone_classifier.process_image(image_id)
    return {
        "image_id": image.image_id,
        "processed": image.processed,
        "damage_detected": image.damage_detected,
        "damage_classifications": image.damage_classifications,
        "confidence_scores": image.confidence_scores,
    }


@router.get("/damage/drone-images")
async def get_drone_images(processed_only: bool = False) -> List[Dict[str, Any]]:
    """Get drone images."""
    images = damage_manager.drone_classifier.get_images(processed_only)
    return [
        {
            "image_id": i.image_id,
            "location": i.location,
            "processed": i.processed,
            "damage_detected": i.damage_detected,
        }
        for i in images
    ]


@router.post("/damage/recovery-timeline")
async def create_recovery_timeline(request: RecoveryTimelineRequest) -> Dict[str, Any]:
    """Create a recovery timeline."""
    timeline = damage_manager.recovery_engine.create_timeline(
        area_name=request.area_name,
        total_structures_affected=request.total_structures_affected,
        damage_summary=request.damage_summary,
    )
    return {
        "timeline_id": timeline.timeline_id,
        "area_name": timeline.area_name,
        "current_phase": timeline.current_phase.value,
        "estimated_completion": timeline.estimated_completion.isoformat(),
        "phases": timeline.phases,
        "milestones": timeline.milestones,
    }


@router.put("/damage/recovery-timeline/{timeline_id}/progress")
async def update_recovery_progress(
    timeline_id: str,
    structures_repaired: Optional[int] = None,
    structures_demolished: Optional[int] = None,
    current_phase: Optional[str] = None,
) -> Dict[str, Any]:
    """Update recovery progress."""
    timeline = damage_manager.recovery_engine.update_progress(
        timeline_id, structures_repaired, structures_demolished, current_phase
    )
    return {
        "timeline_id": timeline.timeline_id,
        "current_phase": timeline.current_phase.value,
        "structures_repaired": timeline.structures_repaired,
        "structures_demolished": timeline.structures_demolished,
    }


@router.get("/damage/recovery-timelines")
async def get_recovery_timelines() -> List[Dict[str, Any]]:
    """Get recovery timelines."""
    timelines = damage_manager.recovery_engine.get_timelines()
    return [
        {
            "timeline_id": t.timeline_id,
            "area_name": t.area_name,
            "current_phase": t.current_phase.value,
            "total_structures_affected": t.total_structures_affected,
            "structures_repaired": t.structures_repaired,
        }
        for t in timelines
    ]


@router.get("/damage/area-summary/{area_name}")
async def get_area_damage_summary(area_name: str) -> Dict[str, Any]:
    """Get damage summary for an area."""
    summary = damage_manager.create_area_summary(area_name)
    return {
        "area_id": summary.area_id,
        "area_name": summary.area_name,
        "total_structures": summary.total_structures,
        "by_damage_level": summary.by_damage_level,
        "by_structure_type": summary.by_structure_type,
        "total_estimated_cost": summary.total_estimated_cost,
        "population_displaced": summary.population_displaced,
        "businesses_affected": summary.businesses_affected,
    }


@router.get("/damage/high-risk")
async def get_high_risk_structures(threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Get high risk structures."""
    risks = damage_manager.risk_scorer.get_high_risk_structures(threshold)
    return [
        {
            "risk_id": r.risk_id,
            "structure_id": r.structure_id,
            "risk_score": r.risk_score,
            "evacuation_required": r.evacuation_required,
            "demolition_recommended": r.demolition_recommended,
            "immediate_hazards": r.immediate_hazards,
        }
        for r in risks
    ]


@router.get("/damage/metrics")
async def get_damage_metrics() -> Dict[str, Any]:
    """Get damage assessment metrics."""
    return damage_manager.get_overall_metrics()
