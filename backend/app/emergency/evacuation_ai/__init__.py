"""
Phase 21: Evacuation AI Module

Dynamic evacuation route optimization, population movement prediction,
special needs evacuation planning, and traffic simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid
import math
import heapq


class EvacuationZone(Enum):
    ZONE_A = "zone_a"
    ZONE_B = "zone_b"
    ZONE_C = "zone_c"
    ZONE_D = "zone_d"
    ZONE_E = "zone_e"


class EvacuationPriority(Enum):
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VOLUNTARY = "voluntary"


class RoadStatus(Enum):
    OPEN = "open"
    CONGESTED = "congested"
    PARTIALLY_BLOCKED = "partially_blocked"
    CLOSED = "closed"
    FLOODED = "flooded"
    DAMAGED = "damaged"


class SpecialNeedsCategory(Enum):
    MOBILITY_IMPAIRED = "mobility_impaired"
    MEDICAL_DEPENDENT = "medical_dependent"
    ELDERLY = "elderly"
    PEDIATRIC = "pediatric"
    HEARING_IMPAIRED = "hearing_impaired"
    VISION_IMPAIRED = "vision_impaired"
    COGNITIVE_DISABILITY = "cognitive_disability"
    NON_ENGLISH_SPEAKER = "non_english_speaker"
    NO_VEHICLE = "no_vehicle"
    PET_OWNER = "pet_owner"


class TransportMode(Enum):
    PERSONAL_VEHICLE = "personal_vehicle"
    BUS = "bus"
    AMBULANCE = "ambulance"
    PARATRANSIT = "paratransit"
    HELICOPTER = "helicopter"
    BOAT = "boat"
    WALKING = "walking"


@dataclass
class EvacuationRoute:
    route_id: str
    name: str
    origin_zone: EvacuationZone
    destination: Dict[str, Any]
    waypoints: List[Dict[str, float]]
    distance_miles: float
    estimated_time_minutes: float
    capacity_vehicles_per_hour: int
    current_flow_vehicles_per_hour: int
    road_segments: List[Dict[str, Any]]
    contraflow_enabled: bool
    priority: EvacuationPriority
    status: RoadStatus
    alternate_routes: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoadSegment:
    segment_id: str
    name: str
    start_point: Dict[str, float]
    end_point: Dict[str, float]
    length_miles: float
    lanes: int
    speed_limit_mph: int
    current_speed_mph: float
    status: RoadStatus
    capacity_vehicles_per_hour: int
    current_volume: int
    incidents: List[Dict[str, Any]]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PopulationMovement:
    movement_id: str
    zone: EvacuationZone
    total_population: int
    evacuated_count: int
    remaining_count: int
    evacuation_rate_per_hour: int
    estimated_completion_hours: float
    compliance_rate: float
    vehicle_count: int
    special_needs_count: int
    shelter_destinations: Dict[str, int]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SpecialNeedsEvacuee:
    evacuee_id: str
    name: str
    address: Dict[str, Any]
    categories: List[SpecialNeedsCategory]
    medical_equipment: List[str]
    medications: List[str]
    caregiver_contact: Optional[Dict[str, str]]
    transport_requirements: List[TransportMode]
    destination_preference: Optional[str]
    evacuation_status: str
    assigned_transport: Optional[str]
    pickup_time: Optional[datetime]
    notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrafficSimulation:
    simulation_id: str
    scenario_name: str
    start_time: datetime
    duration_hours: float
    zones_included: List[EvacuationZone]
    total_vehicles: int
    average_speed_mph: float
    bottleneck_locations: List[Dict[str, Any]]
    clearance_time_hours: float
    contraflow_impact: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvacuationOrder:
    order_id: str
    zone: EvacuationZone
    priority: EvacuationPriority
    issued_at: datetime
    effective_at: datetime
    reason: str
    affected_population: int
    recommended_routes: List[str]
    shelter_assignments: Dict[str, str]
    special_instructions: List[str]
    is_active: bool = True


class EvacRouteOptimizer:
    """
    Optimizes evacuation routes considering road closures, traffic, and capacity.
    Uses dynamic routing algorithms to find optimal paths.
    """

    def __init__(self):
        self._routes: Dict[str, EvacuationRoute] = {}
        self._road_segments: Dict[str, RoadSegment] = {}
        self._road_closures: List[Dict[str, Any]] = []

    def create_route(
        self,
        name: str,
        origin_zone: str,
        destination: Dict[str, Any],
        waypoints: List[Dict[str, float]],
        priority: str = "medium",
    ) -> EvacuationRoute:
        """Create a new evacuation route."""
        route_id = f"route-{uuid.uuid4().hex[:8]}"

        zone = EvacuationZone(origin_zone) if origin_zone in [z.value for z in EvacuationZone] else EvacuationZone.ZONE_A
        prio = EvacuationPriority(priority) if priority in [p.value for p in EvacuationPriority] else EvacuationPriority.MEDIUM

        distance = self._calculate_distance(waypoints)
        segments = self._create_road_segments(waypoints)
        capacity = self._calculate_route_capacity(segments)
        time = self._estimate_travel_time(distance, segments)

        route = EvacuationRoute(
            route_id=route_id,
            name=name,
            origin_zone=zone,
            destination=destination,
            waypoints=waypoints,
            distance_miles=distance,
            estimated_time_minutes=time,
            capacity_vehicles_per_hour=capacity,
            current_flow_vehicles_per_hour=0,
            road_segments=segments,
            contraflow_enabled=False,
            priority=prio,
            status=RoadStatus.OPEN,
            alternate_routes=[],
        )

        self._routes[route_id] = route
        return route

    def _calculate_distance(self, waypoints: List[Dict[str, float]]) -> float:
        """Calculate total route distance in miles."""
        if len(waypoints) < 2:
            return 0.0

        total = 0.0
        for i in range(len(waypoints) - 1):
            lat1, lon1 = waypoints[i].get("lat", 0), waypoints[i].get("lon", 0)
            lat2, lon2 = waypoints[i + 1].get("lat", 0), waypoints[i + 1].get("lon", 0)

            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            total += 3959 * c

        return total

    def _create_road_segments(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Create road segments from waypoints."""
        segments = []
        for i in range(len(waypoints) - 1):
            segments.append({
                "segment_id": f"seg-{uuid.uuid4().hex[:6]}",
                "start": waypoints[i],
                "end": waypoints[i + 1],
                "status": "open",
                "lanes": 2,
                "speed_limit": 45,
            })
        return segments

    def _calculate_route_capacity(self, segments: List[Dict[str, Any]]) -> int:
        """Calculate route capacity based on segments."""
        if not segments:
            return 1000
        min_lanes = min(s.get("lanes", 2) for s in segments)
        return min_lanes * 1800

    def _estimate_travel_time(self, distance: float, segments: List[Dict[str, Any]]) -> float:
        """Estimate travel time in minutes."""
        if not segments:
            return distance * 2
        avg_speed = sum(s.get("speed_limit", 45) for s in segments) / len(segments)
        return (distance / avg_speed) * 60

    def optimize_route(
        self,
        route_id: str,
        current_conditions: Dict[str, Any],
    ) -> EvacuationRoute:
        """Optimize route based on current conditions."""
        route = self._routes.get(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        congestion_factor = current_conditions.get("congestion_factor", 1.0)
        road_closures = current_conditions.get("road_closures", [])

        for closure in road_closures:
            for segment in route.road_segments:
                if segment.get("segment_id") in closure.get("affected_segments", []):
                    segment["status"] = "closed"

        route.estimated_time_minutes *= congestion_factor
        route.current_flow_vehicles_per_hour = int(route.capacity_vehicles_per_hour / congestion_factor)
        route.updated_at = datetime.utcnow()

        return route

    def find_optimal_route(
        self,
        origin: Dict[str, float],
        destination: Dict[str, float],
        avoid_zones: Optional[List[str]] = None,
    ) -> Optional[EvacuationRoute]:
        """Find optimal evacuation route using A* algorithm."""
        available_routes = [
            r for r in self._routes.values()
            if r.status == RoadStatus.OPEN
        ]

        if not available_routes:
            return None

        best_route = min(
            available_routes,
            key=lambda r: r.estimated_time_minutes + (r.distance_miles * 0.5)
        )

        return best_route

    def enable_contraflow(self, route_id: str) -> EvacuationRoute:
        """Enable contraflow on a route to increase capacity."""
        route = self._routes.get(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        route.contraflow_enabled = True
        route.capacity_vehicles_per_hour *= 2
        route.updated_at = datetime.utcnow()

        return route

    def add_road_closure(
        self,
        segment_id: str,
        reason: str,
        estimated_duration_hours: float,
    ) -> Dict[str, Any]:
        """Add a road closure."""
        closure = {
            "closure_id": f"closure-{uuid.uuid4().hex[:8]}",
            "segment_id": segment_id,
            "reason": reason,
            "start_time": datetime.utcnow(),
            "estimated_duration_hours": estimated_duration_hours,
            "affected_segments": [segment_id],
        }

        self._road_closures.append(closure)

        for route in self._routes.values():
            for segment in route.road_segments:
                if segment.get("segment_id") == segment_id:
                    segment["status"] = "closed"
                    route.status = RoadStatus.PARTIALLY_BLOCKED

        return closure

    def get_route(self, route_id: str) -> Optional[EvacuationRoute]:
        """Get route by ID."""
        return self._routes.get(route_id)

    def get_routes(self, zone: Optional[EvacuationZone] = None) -> List[EvacuationRoute]:
        """Get all routes, optionally filtered by zone."""
        routes = list(self._routes.values())
        if zone:
            routes = [r for r in routes if r.origin_zone == zone]
        return routes

    def get_road_closures(self) -> List[Dict[str, Any]]:
        """Get all active road closures."""
        return self._road_closures


class PopulationMovementPredictor:
    """
    Predicts population movement during evacuations.
    """

    def __init__(self):
        self._movements: Dict[str, PopulationMovement] = {}
        self._zone_populations: Dict[EvacuationZone, int] = {
            EvacuationZone.ZONE_A: 50000,
            EvacuationZone.ZONE_B: 75000,
            EvacuationZone.ZONE_C: 100000,
            EvacuationZone.ZONE_D: 60000,
            EvacuationZone.ZONE_E: 40000,
        }

    def predict_movement(
        self,
        zone: str,
        evacuation_order_time: datetime,
        compliance_rate: float = 0.85,
    ) -> PopulationMovement:
        """Predict population movement for a zone."""
        movement_id = f"movement-{uuid.uuid4().hex[:8]}"

        zone_enum = EvacuationZone(zone) if zone in [z.value for z in EvacuationZone] else EvacuationZone.ZONE_A
        total_pop = self._zone_populations.get(zone_enum, 50000)

        evacuating_pop = int(total_pop * compliance_rate)
        vehicle_count = int(evacuating_pop / 2.5)
        special_needs = int(total_pop * 0.08)

        evac_rate = self._calculate_evacuation_rate(zone_enum, vehicle_count)
        completion_hours = evacuating_pop / evac_rate if evac_rate > 0 else 24

        movement = PopulationMovement(
            movement_id=movement_id,
            zone=zone_enum,
            total_population=total_pop,
            evacuated_count=0,
            remaining_count=evacuating_pop,
            evacuation_rate_per_hour=evac_rate,
            estimated_completion_hours=completion_hours,
            compliance_rate=compliance_rate,
            vehicle_count=vehicle_count,
            special_needs_count=special_needs,
            shelter_destinations=self._assign_shelter_destinations(evacuating_pop),
        )

        self._movements[movement_id] = movement
        return movement

    def _calculate_evacuation_rate(self, zone: EvacuationZone, vehicles: int) -> int:
        """Calculate evacuation rate based on zone and vehicle count."""
        base_rate = 5000
        zone_factors = {
            EvacuationZone.ZONE_A: 0.8,
            EvacuationZone.ZONE_B: 0.9,
            EvacuationZone.ZONE_C: 1.0,
            EvacuationZone.ZONE_D: 1.1,
            EvacuationZone.ZONE_E: 1.2,
        }
        factor = zone_factors.get(zone, 1.0)
        return int(base_rate * factor)

    def _assign_shelter_destinations(self, population: int) -> Dict[str, int]:
        """Assign population to shelter destinations."""
        shelters = {
            "Shelter A - Convention Center": int(population * 0.3),
            "Shelter B - High School": int(population * 0.25),
            "Shelter C - Community Center": int(population * 0.2),
            "Shelter D - Church": int(population * 0.15),
            "Shelter E - Stadium": int(population * 0.1),
        }
        return shelters

    def update_movement(
        self,
        movement_id: str,
        evacuated_count: int,
    ) -> PopulationMovement:
        """Update movement with current evacuation count."""
        movement = self._movements.get(movement_id)
        if not movement:
            raise ValueError(f"Movement {movement_id} not found")

        movement.evacuated_count = evacuated_count
        movement.remaining_count = int(movement.total_population * movement.compliance_rate) - evacuated_count

        if movement.evacuation_rate_per_hour > 0:
            movement.estimated_completion_hours = movement.remaining_count / movement.evacuation_rate_per_hour

        return movement

    def get_movement(self, movement_id: str) -> Optional[PopulationMovement]:
        """Get movement by ID."""
        return self._movements.get(movement_id)

    def get_movements(self, zone: Optional[EvacuationZone] = None) -> List[PopulationMovement]:
        """Get all movements, optionally filtered by zone."""
        movements = list(self._movements.values())
        if zone:
            movements = [m for m in movements if m.zone == zone]
        return movements

    def get_total_remaining(self) -> int:
        """Get total remaining population to evacuate."""
        return sum(m.remaining_count for m in self._movements.values())


class SpecialNeedsEvacuationPlanner:
    """
    Plans evacuation for special needs populations.
    """

    def __init__(self):
        self._evacuees: Dict[str, SpecialNeedsEvacuee] = {}
        self._transport_assignments: Dict[str, List[str]] = {}

    def register_evacuee(
        self,
        name: str,
        address: Dict[str, Any],
        categories: List[str],
        medical_equipment: Optional[List[str]] = None,
        medications: Optional[List[str]] = None,
        caregiver_contact: Optional[Dict[str, str]] = None,
        notes: str = "",
    ) -> SpecialNeedsEvacuee:
        """Register a special needs evacuee."""
        evacuee_id = f"evacuee-{uuid.uuid4().hex[:8]}"

        category_enums = []
        for cat in categories:
            if cat in [c.value for c in SpecialNeedsCategory]:
                category_enums.append(SpecialNeedsCategory(cat))

        transport_reqs = self._determine_transport_requirements(category_enums)

        evacuee = SpecialNeedsEvacuee(
            evacuee_id=evacuee_id,
            name=name,
            address=address,
            categories=category_enums,
            medical_equipment=medical_equipment or [],
            medications=medications or [],
            caregiver_contact=caregiver_contact,
            transport_requirements=transport_reqs,
            destination_preference=None,
            evacuation_status="registered",
            assigned_transport=None,
            pickup_time=None,
            notes=notes,
        )

        self._evacuees[evacuee_id] = evacuee
        return evacuee

    def _determine_transport_requirements(
        self,
        categories: List[SpecialNeedsCategory],
    ) -> List[TransportMode]:
        """Determine transport requirements based on categories."""
        requirements = []

        if SpecialNeedsCategory.MOBILITY_IMPAIRED in categories:
            requirements.append(TransportMode.PARATRANSIT)
        if SpecialNeedsCategory.MEDICAL_DEPENDENT in categories:
            requirements.append(TransportMode.AMBULANCE)
        if SpecialNeedsCategory.NO_VEHICLE in categories:
            requirements.append(TransportMode.BUS)
        if not requirements:
            requirements.append(TransportMode.BUS)

        return requirements

    def assign_transport(
        self,
        evacuee_id: str,
        transport_id: str,
        pickup_time: datetime,
    ) -> SpecialNeedsEvacuee:
        """Assign transport to an evacuee."""
        evacuee = self._evacuees.get(evacuee_id)
        if not evacuee:
            raise ValueError(f"Evacuee {evacuee_id} not found")

        evacuee.assigned_transport = transport_id
        evacuee.pickup_time = pickup_time
        evacuee.evacuation_status = "transport_assigned"

        if transport_id not in self._transport_assignments:
            self._transport_assignments[transport_id] = []
        self._transport_assignments[transport_id].append(evacuee_id)

        return evacuee

    def update_status(
        self,
        evacuee_id: str,
        status: str,
    ) -> SpecialNeedsEvacuee:
        """Update evacuee status."""
        evacuee = self._evacuees.get(evacuee_id)
        if not evacuee:
            raise ValueError(f"Evacuee {evacuee_id} not found")

        evacuee.evacuation_status = status
        return evacuee

    def get_evacuee(self, evacuee_id: str) -> Optional[SpecialNeedsEvacuee]:
        """Get evacuee by ID."""
        return self._evacuees.get(evacuee_id)

    def get_evacuees(
        self,
        category: Optional[SpecialNeedsCategory] = None,
        status: Optional[str] = None,
    ) -> List[SpecialNeedsEvacuee]:
        """Get evacuees, optionally filtered."""
        evacuees = list(self._evacuees.values())
        if category:
            evacuees = [e for e in evacuees if category in e.categories]
        if status:
            evacuees = [e for e in evacuees if e.evacuation_status == status]
        return evacuees

    def get_unassigned_evacuees(self) -> List[SpecialNeedsEvacuee]:
        """Get evacuees without transport assignment."""
        return [e for e in self._evacuees.values() if e.assigned_transport is None]

    def get_transport_manifest(self, transport_id: str) -> List[SpecialNeedsEvacuee]:
        """Get manifest of evacuees assigned to a transport."""
        evacuee_ids = self._transport_assignments.get(transport_id, [])
        return [self._evacuees[eid] for eid in evacuee_ids if eid in self._evacuees]

    def get_metrics(self) -> Dict[str, Any]:
        """Get special needs evacuation metrics."""
        evacuees = list(self._evacuees.values())
        return {
            "total_registered": len(evacuees),
            "by_status": {
                status: len([e for e in evacuees if e.evacuation_status == status])
                for status in ["registered", "transport_assigned", "in_transit", "evacuated"]
            },
            "by_category": {
                cat.value: len([e for e in evacuees if cat in e.categories])
                for cat in SpecialNeedsCategory
            },
            "unassigned_count": len(self.get_unassigned_evacuees()),
        }


class TrafficSimulationEngine:
    """
    Simulates traffic flow during evacuations (stub implementation).
    """

    def __init__(self, route_optimizer: EvacRouteOptimizer):
        self._route_optimizer = route_optimizer
        self._simulations: Dict[str, TrafficSimulation] = {}

    def run_simulation(
        self,
        scenario_name: str,
        zones: List[str],
        duration_hours: float,
        vehicle_count: int,
        contraflow_enabled: bool = False,
    ) -> TrafficSimulation:
        """Run traffic simulation for evacuation scenario."""
        simulation_id = f"sim-{uuid.uuid4().hex[:8]}"

        zone_enums = []
        for z in zones:
            if z in [zone.value for zone in EvacuationZone]:
                zone_enums.append(EvacuationZone(z))

        bottlenecks = self._identify_bottlenecks(zone_enums, vehicle_count)
        avg_speed = self._calculate_average_speed(vehicle_count, contraflow_enabled)
        clearance_time = self._calculate_clearance_time(vehicle_count, avg_speed, contraflow_enabled)
        contraflow_impact = 0.3 if contraflow_enabled else 0.0

        recommendations = self._generate_recommendations(bottlenecks, clearance_time, contraflow_enabled)

        simulation = TrafficSimulation(
            simulation_id=simulation_id,
            scenario_name=scenario_name,
            start_time=datetime.utcnow(),
            duration_hours=duration_hours,
            zones_included=zone_enums,
            total_vehicles=vehicle_count,
            average_speed_mph=avg_speed,
            bottleneck_locations=bottlenecks,
            clearance_time_hours=clearance_time,
            contraflow_impact=contraflow_impact,
            recommendations=recommendations,
        )

        self._simulations[simulation_id] = simulation
        return simulation

    def _identify_bottlenecks(
        self,
        zones: List[EvacuationZone],
        vehicle_count: int,
    ) -> List[Dict[str, Any]]:
        """Identify potential bottleneck locations."""
        bottlenecks = []

        if vehicle_count > 50000:
            bottlenecks.append({
                "location": "I-95 / I-595 Interchange",
                "severity": "high",
                "expected_delay_minutes": 45,
            })

        if vehicle_count > 30000:
            bottlenecks.append({
                "location": "Florida Turnpike Toll Plaza",
                "severity": "medium",
                "expected_delay_minutes": 30,
            })

        bottlenecks.append({
            "location": "US-1 Bridge",
            "severity": "low",
            "expected_delay_minutes": 15,
        })

        return bottlenecks

    def _calculate_average_speed(self, vehicle_count: int, contraflow: bool) -> float:
        """Calculate average speed based on vehicle count."""
        base_speed = 45.0

        if vehicle_count > 100000:
            base_speed = 15.0
        elif vehicle_count > 50000:
            base_speed = 25.0
        elif vehicle_count > 25000:
            base_speed = 35.0

        if contraflow:
            base_speed *= 1.3

        return base_speed

    def _calculate_clearance_time(
        self,
        vehicle_count: int,
        avg_speed: float,
        contraflow: bool,
    ) -> float:
        """Calculate time to clear all vehicles."""
        base_capacity = 5000
        if contraflow:
            base_capacity *= 2

        return vehicle_count / base_capacity

    def _generate_recommendations(
        self,
        bottlenecks: List[Dict[str, Any]],
        clearance_time: float,
        contraflow: bool,
    ) -> List[str]:
        """Generate recommendations based on simulation results."""
        recommendations = []

        if clearance_time > 12:
            recommendations.append("Consider phased evacuation by zone")
            recommendations.append("Increase public transit capacity")

        if not contraflow and clearance_time > 8:
            recommendations.append("Enable contraflow on major evacuation routes")

        for bottleneck in bottlenecks:
            if bottleneck.get("severity") == "high":
                recommendations.append(f"Deploy traffic control at {bottleneck.get('location')}")

        recommendations.append("Coordinate with neighboring jurisdictions")
        recommendations.append("Pre-position fuel supplies along evacuation routes")

        return recommendations

    def get_simulation(self, simulation_id: str) -> Optional[TrafficSimulation]:
        """Get simulation by ID."""
        return self._simulations.get(simulation_id)

    def get_simulations(self) -> List[TrafficSimulation]:
        """Get all simulations."""
        return list(self._simulations.values())


class EvacuationManager:
    """
    Main evacuation management coordinator.
    """

    def __init__(self):
        self.route_optimizer = EvacRouteOptimizer()
        self.movement_predictor = PopulationMovementPredictor()
        self.special_needs_planner = SpecialNeedsEvacuationPlanner()
        self.traffic_simulator = TrafficSimulationEngine(self.route_optimizer)
        self._orders: Dict[str, EvacuationOrder] = {}

    def issue_evacuation_order(
        self,
        zone: str,
        priority: str,
        reason: str,
        effective_at: Optional[datetime] = None,
    ) -> EvacuationOrder:
        """Issue an evacuation order for a zone."""
        order_id = f"order-{uuid.uuid4().hex[:8]}"

        zone_enum = EvacuationZone(zone) if zone in [z.value for z in EvacuationZone] else EvacuationZone.ZONE_A
        prio_enum = EvacuationPriority(priority) if priority in [p.value for p in EvacuationPriority] else EvacuationPriority.MEDIUM

        routes = self.route_optimizer.get_routes(zone_enum)
        route_ids = [r.route_id for r in routes]

        movement = self.movement_predictor.predict_movement(zone, datetime.utcnow())

        order = EvacuationOrder(
            order_id=order_id,
            zone=zone_enum,
            priority=prio_enum,
            issued_at=datetime.utcnow(),
            effective_at=effective_at or datetime.utcnow(),
            reason=reason,
            affected_population=movement.total_population,
            recommended_routes=route_ids,
            shelter_assignments=movement.shelter_destinations,
            special_instructions=self._generate_special_instructions(prio_enum, reason),
        )

        self._orders[order_id] = order
        return order

    def _generate_special_instructions(
        self,
        priority: EvacuationPriority,
        reason: str,
    ) -> List[str]:
        """Generate special instructions based on priority and reason."""
        instructions = [
            "Take essential documents and medications",
            "Secure your home before leaving",
            "Follow designated evacuation routes",
            "Monitor official emergency channels",
        ]

        if priority == EvacuationPriority.IMMEDIATE:
            instructions.insert(0, "LEAVE IMMEDIATELY - Do not delay")

        if "flood" in reason.lower():
            instructions.append("Do not drive through flooded roads")
        if "fire" in reason.lower():
            instructions.append("Close all windows and doors")
        if "hurricane" in reason.lower():
            instructions.append("Board up windows if time permits")

        return instructions

    def cancel_evacuation_order(self, order_id: str) -> EvacuationOrder:
        """Cancel an evacuation order."""
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.is_active = False
        return order

    def get_order(self, order_id: str) -> Optional[EvacuationOrder]:
        """Get evacuation order by ID."""
        return self._orders.get(order_id)

    def get_active_orders(self) -> List[EvacuationOrder]:
        """Get all active evacuation orders."""
        return [o for o in self._orders.values() if o.is_active]

    def get_metrics(self) -> Dict[str, Any]:
        """Get evacuation metrics."""
        active_orders = self.get_active_orders()
        movements = self.movement_predictor.get_movements()

        return {
            "active_orders": len(active_orders),
            "total_population_affected": sum(o.affected_population for o in active_orders),
            "total_evacuated": sum(m.evacuated_count for m in movements),
            "total_remaining": self.movement_predictor.get_total_remaining(),
            "special_needs_registered": len(self.special_needs_planner.get_evacuees()),
            "special_needs_unassigned": len(self.special_needs_planner.get_unassigned_evacuees()),
            "active_routes": len(self.route_optimizer.get_routes()),
            "road_closures": len(self.route_optimizer.get_road_closures()),
        }
