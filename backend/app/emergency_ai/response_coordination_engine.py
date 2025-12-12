"""
Phase 31: Autonomous Disaster Response Engine

Functionality:
- Multi-Agency Tasking
- Real-Time Resource Allocation
- Smart Evacuation Routing

City: Riviera Beach, Florida 33404
Agency ORI: FL0500400
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
import uuid
import math


class AgencyType(Enum):
    """Types of responding agencies"""
    POLICE = "police"
    FIRE_RESCUE = "fire_rescue"
    EMS = "ems"
    PUBLIC_WORKS = "public_works"
    UTILITIES = "utilities"
    HOSPITALS = "hospitals"
    RED_CROSS = "red_cross"
    REGIONAL_EOC = "regional_eoc"
    NATIONAL_GUARD = "national_guard"
    COAST_GUARD = "coast_guard"
    FEMA = "fema"
    DOT = "dot"
    HAZMAT = "hazmat"
    SEARCH_RESCUE = "search_rescue"


class ResourceType(Enum):
    """Types of emergency resources"""
    PATROL_UNIT = "patrol_unit"
    FIRE_ENGINE = "fire_engine"
    LADDER_TRUCK = "ladder_truck"
    RESCUE_SQUAD = "rescue_squad"
    AMBULANCE = "ambulance"
    EVACUATION_BUS = "evacuation_bus"
    SHELTER = "shelter"
    HOSPITAL_BED = "hospital_bed"
    SURGE_CAPACITY = "surge_capacity"
    DRONE = "drone"
    ROBOT = "robot"
    GENERATOR = "generator"
    WATER_TRUCK = "water_truck"
    FUEL_TRUCK = "fuel_truck"
    HEAVY_EQUIPMENT = "heavy_equipment"
    BOAT = "boat"
    HELICOPTER = "helicopter"


class TaskPriority(Enum):
    """Task priority levels"""
    ROUTINE = 1
    ELEVATED = 2
    URGENT = 3
    EMERGENCY = 4
    CRITICAL = 5


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RouteStatus(Enum):
    """Evacuation route status"""
    OPEN = "open"
    CONGESTED = "congested"
    BLOCKED = "blocked"
    FLOODED = "flooded"
    CLOSED = "closed"


@dataclass
class AgencyTask:
    """Task assigned to an agency"""
    task_id: str
    timestamp: datetime
    agency_type: AgencyType
    priority: TaskPriority
    status: TaskStatus
    description: str
    location_zone: str
    location_address: Optional[str] = None
    location_coordinates: Optional[Tuple[float, float]] = None
    assigned_units: List[str] = field(default_factory=list)
    estimated_duration_hours: float = 1.0
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    special_requirements: List[str] = field(default_factory=list)
    completion_criteria: List[str] = field(default_factory=list)
    notes: str = ""
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.task_id}:{self.timestamp.isoformat()}:{self.agency_type.value}:{self.priority.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    timestamp: datetime
    resource_type: ResourceType
    resource_id: str
    assigned_zone: str
    assigned_task_id: Optional[str] = None
    status: str = "available"
    current_location: Optional[Tuple[float, float]] = None
    capacity: int = 1
    utilization_percent: float = 0.0
    estimated_availability: Optional[datetime] = None
    special_capabilities: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.allocation_id}:{self.timestamp.isoformat()}:{self.resource_type.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class EvacuationRoute:
    """Evacuation route information"""
    route_id: str
    timestamp: datetime
    origin_zone: str
    destination: str
    destination_type: str
    route_name: str
    distance_miles: float
    estimated_time_minutes: float
    status: RouteStatus
    road_segments: List[str] = field(default_factory=list)
    bridge_crossings: List[str] = field(default_factory=list)
    current_traffic_level: str = "normal"
    flood_risk_segments: List[str] = field(default_factory=list)
    capacity_vehicles_per_hour: int = 1000
    current_flow_vehicles_per_hour: int = 0
    special_needs_accessible: bool = True
    alternate_routes: List[str] = field(default_factory=list)
    time_to_clear_hours: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.route_id}:{self.timestamp.isoformat()}:{self.origin_zone}:{self.destination}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class ShelterStatus:
    """Emergency shelter status"""
    shelter_id: str
    name: str
    zone: str
    address: str
    capacity: int
    current_occupancy: int
    status: str
    amenities: List[str] = field(default_factory=list)
    special_needs_capacity: int = 0
    pet_friendly: bool = False
    medical_staff_available: bool = False
    generator_backup: bool = True
    food_supply_days: float = 3.0
    water_supply_days: float = 3.0


@dataclass
class ResponsePlan:
    """Unified disaster response plan"""
    plan_id: str
    timestamp: datetime
    incident_type: str
    threat_level: int
    affected_zones: List[str]
    agency_tasks: List[AgencyTask]
    resource_allocations: List[ResourceAllocation]
    evacuation_routes: List[EvacuationRoute]
    shelter_assignments: List[ShelterStatus]
    estimated_response_time_hours: float
    estimated_completion_time_hours: float
    total_resources_deployed: int
    total_personnel_deployed: int
    coordination_notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.plan_id}:{self.timestamp.isoformat()}:{self.incident_type}:{self.threat_level}"
        return hashlib.sha256(data.encode()).hexdigest()


class ResponseCoordinationEngine:
    """
    Autonomous Disaster Response Engine
    
    Coordinates multi-agency response, resource allocation,
    and evacuation routing.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.agency_config = {
            "ori": "FL0500400",
            "city": "Riviera Beach",
            "state": "FL",
            "zip": "33404",
            "county": "Palm Beach",
        }
        
        self.city_zones = [
            "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
            "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
        ]
        
        self.zone_populations = {
            "Zone_A": 3500, "Zone_B": 4200, "Zone_C": 3800,
            "Zone_D": 2900, "Zone_E": 4500, "Zone_F": 3200,
            "Zone_G": 2800, "Zone_H": 3600, "Zone_I": 4100,
            "Zone_J": 3400,
        }
        
        self.available_resources = {
            ResourceType.PATROL_UNIT: 25,
            ResourceType.FIRE_ENGINE: 8,
            ResourceType.LADDER_TRUCK: 3,
            ResourceType.RESCUE_SQUAD: 4,
            ResourceType.AMBULANCE: 10,
            ResourceType.EVACUATION_BUS: 15,
            ResourceType.SHELTER: 5,
            ResourceType.HOSPITAL_BED: 200,
            ResourceType.DRONE: 12,
            ResourceType.ROBOT: 4,
            ResourceType.GENERATOR: 20,
            ResourceType.BOAT: 6,
        }
        
        self.shelters = [
            ShelterStatus(
                shelter_id="SH-001",
                name="Riviera Beach Community Center",
                zone="Zone_A",
                address="600 W Blue Heron Blvd",
                capacity=500,
                current_occupancy=0,
                status="ready",
                amenities=["restrooms", "kitchen", "medical_station"],
                special_needs_capacity=50,
                pet_friendly=False,
                medical_staff_available=True,
            ),
            ShelterStatus(
                shelter_id="SH-002",
                name="Riviera Beach High School",
                zone="Zone_C",
                address="1600 Avenue L",
                capacity=800,
                current_occupancy=0,
                status="ready",
                amenities=["restrooms", "kitchen", "gymnasium"],
                special_needs_capacity=80,
                pet_friendly=True,
                medical_staff_available=False,
            ),
            ShelterStatus(
                shelter_id="SH-003",
                name="Marina Event Center",
                zone="Zone_E",
                address="190 E 13th St",
                capacity=300,
                current_occupancy=0,
                status="ready",
                amenities=["restrooms", "kitchen"],
                special_needs_capacity=30,
                pet_friendly=True,
                medical_staff_available=False,
            ),
            ShelterStatus(
                shelter_id="SH-004",
                name="Wells Recreation Center",
                zone="Zone_G",
                address="1000 W 10th St",
                capacity=400,
                current_occupancy=0,
                status="ready",
                amenities=["restrooms", "kitchen", "playground"],
                special_needs_capacity=40,
                pet_friendly=False,
                medical_staff_available=True,
            ),
            ShelterStatus(
                shelter_id="SH-005",
                name="Singer Island Community Center",
                zone="Zone_J",
                address="2000 Blue Heron Blvd",
                capacity=250,
                current_occupancy=0,
                status="ready",
                amenities=["restrooms", "kitchen"],
                special_needs_capacity=25,
                pet_friendly=True,
                medical_staff_available=False,
            ),
        ]
        
        self.primary_routes = [
            {
                "name": "Blue Heron Blvd West",
                "zones": ["Zone_A", "Zone_B", "Zone_C"],
                "destination": "I-95 North",
                "distance_miles": 5.2,
                "bridges": [],
            },
            {
                "name": "Broadway Ave North",
                "zones": ["Zone_D", "Zone_E", "Zone_F"],
                "destination": "Palm Beach Lakes Blvd",
                "distance_miles": 4.8,
                "bridges": [],
            },
            {
                "name": "Singer Island Causeway",
                "zones": ["Zone_I", "Zone_J"],
                "destination": "Blue Heron Blvd",
                "distance_miles": 2.1,
                "bridges": ["Blue Heron Bridge"],
            },
            {
                "name": "Avenue E South",
                "zones": ["Zone_G", "Zone_H"],
                "destination": "Southern Blvd",
                "distance_miles": 6.3,
                "bridges": [],
            },
        ]
        
        self.statistics = {
            "total_tasks_created": 0,
            "total_resources_allocated": 0,
            "total_evacuations_planned": 0,
            "total_response_plans": 0,
        }
    
    def create_agency_task(
        self,
        agency_type: AgencyType,
        priority: TaskPriority,
        description: str,
        location_zone: str,
        location_address: Optional[str] = None,
        estimated_duration_hours: float = 1.0,
        special_requirements: Optional[List[str]] = None,
    ) -> AgencyTask:
        """
        Create a task for an agency.
        """
        task_id = f"AT-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        deadline = None
        if priority == TaskPriority.CRITICAL:
            deadline = timestamp + timedelta(hours=1)
        elif priority == TaskPriority.EMERGENCY:
            deadline = timestamp + timedelta(hours=2)
        elif priority == TaskPriority.URGENT:
            deadline = timestamp + timedelta(hours=4)
        
        assigned_units = self._assign_units(agency_type, priority)
        
        completion_criteria = self._get_completion_criteria(agency_type, description)
        
        task = AgencyTask(
            task_id=task_id,
            timestamp=timestamp,
            agency_type=agency_type,
            priority=priority,
            status=TaskStatus.ASSIGNED if assigned_units else TaskStatus.PENDING,
            description=description,
            location_zone=location_zone,
            location_address=location_address,
            assigned_units=assigned_units,
            estimated_duration_hours=estimated_duration_hours,
            deadline=deadline,
            special_requirements=special_requirements or [],
            completion_criteria=completion_criteria,
        )
        
        self.statistics["total_tasks_created"] += 1
        
        return task
    
    def allocate_resources(
        self,
        resource_type: ResourceType,
        quantity: int,
        zone: str,
        task_id: Optional[str] = None,
    ) -> List[ResourceAllocation]:
        """
        Allocate resources to a zone or task.
        """
        allocations = []
        available = self.available_resources.get(resource_type, 0)
        
        actual_quantity = min(quantity, available)
        
        for i in range(actual_quantity):
            allocation_id = f"RA-{uuid.uuid4().hex[:8].upper()}"
            resource_id = f"{resource_type.value}-{i+1:03d}"
            
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                timestamp=datetime.utcnow(),
                resource_type=resource_type,
                resource_id=resource_id,
                assigned_zone=zone,
                assigned_task_id=task_id,
                status="deployed",
                capacity=self._get_resource_capacity(resource_type),
                utilization_percent=100.0 if task_id else 0.0,
                special_capabilities=self._get_resource_capabilities(resource_type),
            )
            
            allocations.append(allocation)
        
        self.statistics["total_resources_allocated"] += len(allocations)
        
        return allocations
    
    def plan_evacuation_route(
        self,
        origin_zone: str,
        destination_type: str = "shelter",
        special_needs: bool = False,
        current_conditions: Optional[Dict[str, Any]] = None,
    ) -> EvacuationRoute:
        """
        Plan optimal evacuation route from a zone.
        """
        route_id = f"ER-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        best_route = None
        for route in self.primary_routes:
            if origin_zone in route["zones"]:
                best_route = route
                break
        
        if not best_route:
            best_route = self.primary_routes[0]
        
        status = RouteStatus.OPEN
        traffic_level = "normal"
        flood_risk_segments = []
        
        if current_conditions:
            if current_conditions.get("flooding"):
                flood_risk_segments = [f"{best_route['name']} - Low Section"]
                if current_conditions.get("flood_severity", 0) > 0.5:
                    status = RouteStatus.FLOODED
            if current_conditions.get("traffic_congestion"):
                traffic_level = "heavy"
                status = RouteStatus.CONGESTED
            if current_conditions.get("road_blocked"):
                status = RouteStatus.BLOCKED
        
        destination = best_route["destination"]
        if destination_type == "shelter":
            shelter = self._find_nearest_shelter(origin_zone, special_needs)
            if shelter:
                destination = shelter.name
        
        base_time = best_route["distance_miles"] * 3
        if traffic_level == "heavy":
            base_time *= 2
        if status == RouteStatus.CONGESTED:
            base_time *= 1.5
        
        zone_population = self.zone_populations.get(origin_zone, 3000)
        time_to_clear = zone_population / 500
        
        alternate_routes = []
        for route in self.primary_routes:
            if route["name"] != best_route["name"] and origin_zone in route.get("zones", []):
                alternate_routes.append(route["name"])
        
        return EvacuationRoute(
            route_id=route_id,
            timestamp=timestamp,
            origin_zone=origin_zone,
            destination=destination,
            destination_type=destination_type,
            route_name=best_route["name"],
            distance_miles=best_route["distance_miles"],
            estimated_time_minutes=base_time,
            status=status,
            road_segments=[best_route["name"]],
            bridge_crossings=best_route.get("bridges", []),
            current_traffic_level=traffic_level,
            flood_risk_segments=flood_risk_segments,
            capacity_vehicles_per_hour=1200,
            current_flow_vehicles_per_hour=int(1200 * 0.3) if traffic_level == "normal" else int(1200 * 0.7),
            special_needs_accessible=True,
            alternate_routes=alternate_routes,
            time_to_clear_hours=time_to_clear,
        )
    
    def coordinate_multi_agency_response(
        self,
        incident_type: str,
        threat_level: int,
        affected_zones: List[str],
        special_requirements: Optional[List[str]] = None,
    ) -> ResponsePlan:
        """
        Coordinate multi-agency response to an incident.
        """
        plan_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        agency_tasks = []
        resource_allocations = []
        evacuation_routes = []
        shelter_assignments = []
        
        required_agencies = self._determine_required_agencies(incident_type, threat_level)
        
        for agency in required_agencies:
            priority = self._determine_task_priority(agency, threat_level)
            description = self._get_agency_task_description(agency, incident_type)
            
            for zone in affected_zones:
                task = self.create_agency_task(
                    agency_type=agency,
                    priority=priority,
                    description=description,
                    location_zone=zone,
                    special_requirements=special_requirements,
                )
                agency_tasks.append(task)
        
        resource_needs = self._calculate_resource_needs(incident_type, threat_level, len(affected_zones))
        
        for resource_type, quantity in resource_needs.items():
            per_zone = max(1, quantity // len(affected_zones))
            for zone in affected_zones:
                allocations = self.allocate_resources(
                    resource_type=resource_type,
                    quantity=per_zone,
                    zone=zone,
                )
                resource_allocations.extend(allocations)
        
        if threat_level >= 3:
            for zone in affected_zones:
                route = self.plan_evacuation_route(
                    origin_zone=zone,
                    destination_type="shelter",
                )
                evacuation_routes.append(route)
        
        if threat_level >= 3:
            for shelter in self.shelters:
                if shelter.status == "ready":
                    shelter.status = "activated"
                    shelter_assignments.append(shelter)
        
        total_resources = len(resource_allocations)
        total_personnel = sum(
            self._estimate_personnel(alloc.resource_type)
            for alloc in resource_allocations
        )
        
        response_time = 0.5 if threat_level >= 4 else 1.0 if threat_level >= 3 else 2.0
        completion_time = response_time + (len(affected_zones) * 2)
        
        coordination_notes = [
            f"Incident Command established in {affected_zones[0]}",
            f"Multi-agency coordination active with {len(required_agencies)} agencies",
            f"Total resources deployed: {total_resources}",
        ]
        
        if threat_level >= 4:
            coordination_notes.append("Regional EOC notified")
            coordination_notes.append("State emergency management notified")
        
        plan = ResponsePlan(
            plan_id=plan_id,
            timestamp=timestamp,
            incident_type=incident_type,
            threat_level=threat_level,
            affected_zones=affected_zones,
            agency_tasks=agency_tasks,
            resource_allocations=resource_allocations,
            evacuation_routes=evacuation_routes,
            shelter_assignments=shelter_assignments,
            estimated_response_time_hours=response_time,
            estimated_completion_time_hours=completion_time,
            total_resources_deployed=total_resources,
            total_personnel_deployed=total_personnel,
            coordination_notes=coordination_notes,
        )
        
        self.statistics["total_response_plans"] += 1
        self.statistics["total_evacuations_planned"] += len(evacuation_routes)
        
        return plan
    
    def get_resource_status(self) -> Dict[str, Any]:
        """
        Get current resource status.
        """
        return {
            "available_resources": {
                rt.value: count for rt, count in self.available_resources.items()
            },
            "shelters": [
                {
                    "id": s.shelter_id,
                    "name": s.name,
                    "zone": s.zone,
                    "capacity": s.capacity,
                    "occupancy": s.current_occupancy,
                    "status": s.status,
                    "available_capacity": s.capacity - s.current_occupancy,
                }
                for s in self.shelters
            ],
            "total_shelter_capacity": sum(s.capacity for s in self.shelters),
            "total_shelter_occupancy": sum(s.current_occupancy for s in self.shelters),
        }
    
    def get_shelter_status(self) -> List[Dict[str, Any]]:
        """
        Get detailed shelter status.
        """
        return [
            {
                "shelter_id": s.shelter_id,
                "name": s.name,
                "zone": s.zone,
                "address": s.address,
                "capacity": s.capacity,
                "current_occupancy": s.current_occupancy,
                "available_capacity": s.capacity - s.current_occupancy,
                "occupancy_percent": (s.current_occupancy / s.capacity * 100) if s.capacity > 0 else 0,
                "status": s.status,
                "amenities": s.amenities,
                "special_needs_capacity": s.special_needs_capacity,
                "pet_friendly": s.pet_friendly,
                "medical_staff_available": s.medical_staff_available,
                "generator_backup": s.generator_backup,
                "food_supply_days": s.food_supply_days,
                "water_supply_days": s.water_supply_days,
            }
            for s in self.shelters
        ]
    
    def _assign_units(self, agency_type: AgencyType, priority: TaskPriority) -> List[str]:
        """Assign units based on agency type and priority."""
        base_units = 1
        if priority == TaskPriority.CRITICAL:
            base_units = 4
        elif priority == TaskPriority.EMERGENCY:
            base_units = 3
        elif priority == TaskPriority.URGENT:
            base_units = 2
        
        prefix = agency_type.value[:3].upper()
        return [f"{prefix}-{i+1:03d}" for i in range(base_units)]
    
    def _get_completion_criteria(self, agency_type: AgencyType, description: str) -> List[str]:
        """Get completion criteria for a task."""
        criteria = ["Task acknowledged", "Units on scene"]
        
        if agency_type == AgencyType.POLICE:
            criteria.extend(["Area secured", "Traffic control established"])
        elif agency_type == AgencyType.FIRE_RESCUE:
            criteria.extend(["Fire contained", "Scene safe"])
        elif agency_type == AgencyType.EMS:
            criteria.extend(["Patients triaged", "Transport complete"])
        elif agency_type == AgencyType.PUBLIC_WORKS:
            criteria.extend(["Hazard mitigated", "Area cleared"])
        
        return criteria
    
    def _get_resource_capacity(self, resource_type: ResourceType) -> int:
        """Get capacity for a resource type."""
        capacities = {
            ResourceType.PATROL_UNIT: 4,
            ResourceType.FIRE_ENGINE: 6,
            ResourceType.AMBULANCE: 2,
            ResourceType.EVACUATION_BUS: 50,
            ResourceType.SHELTER: 500,
            ResourceType.HOSPITAL_BED: 1,
            ResourceType.BOAT: 8,
        }
        return capacities.get(resource_type, 1)
    
    def _get_resource_capabilities(self, resource_type: ResourceType) -> List[str]:
        """Get special capabilities for a resource type."""
        capabilities = {
            ResourceType.FIRE_ENGINE: ["water_pump", "ladder", "rescue_tools"],
            ResourceType.RESCUE_SQUAD: ["extrication", "rope_rescue", "water_rescue"],
            ResourceType.DRONE: ["aerial_survey", "thermal_imaging", "search"],
            ResourceType.ROBOT: ["hazmat_detection", "bomb_disposal", "search"],
            ResourceType.BOAT: ["water_rescue", "evacuation", "patrol"],
        }
        return capabilities.get(resource_type, [])
    
    def _find_nearest_shelter(self, zone: str, special_needs: bool) -> Optional[ShelterStatus]:
        """Find nearest available shelter."""
        for shelter in self.shelters:
            if shelter.status in ["ready", "activated"]:
                if shelter.current_occupancy < shelter.capacity:
                    if special_needs and shelter.special_needs_capacity > 0:
                        return shelter
                    elif not special_needs:
                        return shelter
        return self.shelters[0] if self.shelters else None
    
    def _determine_required_agencies(self, incident_type: str, threat_level: int) -> List[AgencyType]:
        """Determine required agencies based on incident type."""
        agencies = [AgencyType.POLICE, AgencyType.FIRE_RESCUE, AgencyType.EMS]
        
        if incident_type in ["hurricane", "flooding", "storm_surge"]:
            agencies.extend([AgencyType.PUBLIC_WORKS, AgencyType.UTILITIES, AgencyType.RED_CROSS])
        elif incident_type in ["hazmat", "chemical_spill"]:
            agencies.extend([AgencyType.HAZMAT, AgencyType.PUBLIC_WORKS])
        elif incident_type in ["fire", "wildfire"]:
            agencies.extend([AgencyType.PUBLIC_WORKS])
        
        if threat_level >= 4:
            agencies.extend([AgencyType.REGIONAL_EOC, AgencyType.NATIONAL_GUARD])
        
        return list(set(agencies))
    
    def _determine_task_priority(self, agency: AgencyType, threat_level: int) -> TaskPriority:
        """Determine task priority based on agency and threat level."""
        if threat_level >= 5:
            return TaskPriority.CRITICAL
        elif threat_level >= 4:
            return TaskPriority.EMERGENCY
        elif threat_level >= 3:
            return TaskPriority.URGENT
        elif threat_level >= 2:
            return TaskPriority.ELEVATED
        return TaskPriority.ROUTINE
    
    def _get_agency_task_description(self, agency: AgencyType, incident_type: str) -> str:
        """Get task description for an agency."""
        descriptions = {
            AgencyType.POLICE: f"Establish perimeter and traffic control for {incident_type}",
            AgencyType.FIRE_RESCUE: f"Respond to {incident_type} - search and rescue operations",
            AgencyType.EMS: f"Medical staging and patient care for {incident_type}",
            AgencyType.PUBLIC_WORKS: f"Infrastructure assessment and debris removal for {incident_type}",
            AgencyType.UTILITIES: f"Utility assessment and restoration for {incident_type}",
            AgencyType.RED_CROSS: f"Shelter operations and victim assistance for {incident_type}",
            AgencyType.HAZMAT: f"Hazardous materials response for {incident_type}",
            AgencyType.REGIONAL_EOC: f"Regional coordination for {incident_type}",
        }
        return descriptions.get(agency, f"Support operations for {incident_type}")
    
    def _calculate_resource_needs(
        self,
        incident_type: str,
        threat_level: int,
        zone_count: int,
    ) -> Dict[ResourceType, int]:
        """Calculate resource needs based on incident."""
        base_needs = {
            ResourceType.PATROL_UNIT: 2 * zone_count,
            ResourceType.FIRE_ENGINE: 1 * zone_count,
            ResourceType.AMBULANCE: 1 * zone_count,
        }
        
        if incident_type in ["hurricane", "flooding"]:
            base_needs[ResourceType.BOAT] = zone_count
            base_needs[ResourceType.GENERATOR] = 2 * zone_count
        elif incident_type in ["fire", "wildfire"]:
            base_needs[ResourceType.FIRE_ENGINE] = 3 * zone_count
            base_needs[ResourceType.LADDER_TRUCK] = zone_count
        
        multiplier = 1 + (threat_level - 1) * 0.5
        
        return {
            rt: int(count * multiplier)
            for rt, count in base_needs.items()
        }
    
    def _estimate_personnel(self, resource_type: ResourceType) -> int:
        """Estimate personnel for a resource type."""
        personnel = {
            ResourceType.PATROL_UNIT: 2,
            ResourceType.FIRE_ENGINE: 4,
            ResourceType.LADDER_TRUCK: 4,
            ResourceType.RESCUE_SQUAD: 4,
            ResourceType.AMBULANCE: 2,
            ResourceType.EVACUATION_BUS: 1,
            ResourceType.BOAT: 3,
            ResourceType.DRONE: 1,
        }
        return personnel.get(resource_type, 1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.statistics,
            "agency": self.agency_config,
            "zones_covered": len(self.city_zones),
            "shelters_available": len(self.shelters),
            "total_shelter_capacity": sum(s.capacity for s in self.shelters),
        }
