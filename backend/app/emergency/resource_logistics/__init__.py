"""
Phase 21: Resource Logistics Module

Shelter registry, supply chain optimization, deployment allocation,
and critical infrastructure monitoring.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ShelterStatus(Enum):
    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"
    PREPARING = "preparing"
    EVACUATING = "evacuating"


class ShelterType(Enum):
    GENERAL = "general"
    SPECIAL_NEEDS = "special_needs"
    PET_FRIENDLY = "pet_friendly"
    MEDICAL = "medical"
    OVERFLOW = "overflow"


class SupplyCategory(Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    BEDDING = "bedding"
    HYGIENE = "hygiene"
    GENERATORS = "generators"
    FUEL = "fuel"
    COMMUNICATIONS = "communications"
    TOOLS = "tools"
    CLOTHING = "clothing"


class ResourceStatus(Enum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    IN_TRANSIT = "in_transit"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class InfrastructureType(Enum):
    POWER = "power"
    WATER = "water"
    GAS = "gas"
    COMMUNICATIONS = "communications"
    TRANSPORTATION = "transportation"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"


class InfrastructureStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    FULL_OUTAGE = "full_outage"
    UNKNOWN = "unknown"


class DeploymentType(Enum):
    POLICE = "police"
    FIRE = "fire"
    EMS = "ems"
    NATIONAL_GUARD = "national_guard"
    UTILITIES = "utilities"
    PUBLIC_WORKS = "public_works"
    SEARCH_RESCUE = "search_rescue"
    MEDICAL_TEAM = "medical_team"


@dataclass
class Shelter:
    shelter_id: str
    name: str
    address: Dict[str, Any]
    shelter_type: ShelterType
    status: ShelterStatus
    capacity: int
    current_occupancy: int
    staff_count: int
    supplies: Dict[str, int]
    amenities: List[str]
    contact_info: Dict[str, str]
    pet_capacity: int
    medical_capability: bool
    generator_available: bool
    last_inspection: Optional[datetime]
    notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SupplyItem:
    item_id: str
    name: str
    category: SupplyCategory
    quantity: int
    unit: str
    location: str
    status: ResourceStatus
    expiration_date: Optional[datetime]
    minimum_stock: int
    reorder_point: int
    supplier: str
    cost_per_unit: float
    last_restocked: Optional[datetime]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SupplyRequest:
    request_id: str
    shelter_id: str
    items: List[Dict[str, Any]]
    priority: str
    status: str
    requested_by: str
    requested_at: datetime
    fulfilled_at: Optional[datetime]
    notes: str


@dataclass
class DeploymentUnit:
    unit_id: str
    name: str
    deployment_type: DeploymentType
    personnel_count: int
    equipment: List[str]
    current_location: Dict[str, Any]
    assigned_location: Optional[Dict[str, Any]]
    status: ResourceStatus
    shift_start: Optional[datetime]
    shift_end: Optional[datetime]
    contact_info: Dict[str, str]
    capabilities: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InfrastructureAsset:
    asset_id: str
    name: str
    infrastructure_type: InfrastructureType
    location: Dict[str, Any]
    status: InfrastructureStatus
    capacity: float
    current_load: float
    backup_available: bool
    estimated_restoration: Optional[datetime]
    affected_population: int
    priority: int
    last_inspection: Optional[datetime]
    notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ShelterRegistry:
    """
    Manages shelter capacity, supplies, and staff.
    """

    def __init__(self):
        self._shelters: Dict[str, Shelter] = {}
        self._supply_requests: Dict[str, SupplyRequest] = {}

    def register_shelter(
        self,
        name: str,
        address: Dict[str, Any],
        shelter_type: str,
        capacity: int,
        amenities: Optional[List[str]] = None,
        pet_capacity: int = 0,
        medical_capability: bool = False,
    ) -> Shelter:
        """Register a new shelter."""
        shelter_id = f"shelter-{uuid.uuid4().hex[:8]}"

        type_enum = ShelterType(shelter_type) if shelter_type in [t.value for t in ShelterType] else ShelterType.GENERAL

        shelter = Shelter(
            shelter_id=shelter_id,
            name=name,
            address=address,
            shelter_type=type_enum,
            status=ShelterStatus.PREPARING,
            capacity=capacity,
            current_occupancy=0,
            staff_count=0,
            supplies={
                "water_gallons": 0,
                "meals": 0,
                "cots": 0,
                "blankets": 0,
                "first_aid_kits": 0,
            },
            amenities=amenities or [],
            contact_info={},
            pet_capacity=pet_capacity,
            medical_capability=medical_capability,
            generator_available=False,
            last_inspection=None,
            notes="",
        )

        self._shelters[shelter_id] = shelter
        return shelter

    def open_shelter(self, shelter_id: str, staff_count: int) -> Shelter:
        """Open a shelter for occupancy."""
        shelter = self._shelters.get(shelter_id)
        if not shelter:
            raise ValueError(f"Shelter {shelter_id} not found")

        shelter.status = ShelterStatus.OPEN
        shelter.staff_count = staff_count
        shelter.updated_at = datetime.utcnow()

        return shelter

    def close_shelter(self, shelter_id: str) -> Shelter:
        """Close a shelter."""
        shelter = self._shelters.get(shelter_id)
        if not shelter:
            raise ValueError(f"Shelter {shelter_id} not found")

        shelter.status = ShelterStatus.CLOSED
        shelter.updated_at = datetime.utcnow()

        return shelter

    def update_occupancy(self, shelter_id: str, occupancy: int) -> Shelter:
        """Update shelter occupancy."""
        shelter = self._shelters.get(shelter_id)
        if not shelter:
            raise ValueError(f"Shelter {shelter_id} not found")

        shelter.current_occupancy = occupancy
        if occupancy >= shelter.capacity:
            shelter.status = ShelterStatus.FULL
        elif shelter.status == ShelterStatus.FULL and occupancy < shelter.capacity:
            shelter.status = ShelterStatus.OPEN
        shelter.updated_at = datetime.utcnow()

        return shelter

    def update_supplies(self, shelter_id: str, supplies: Dict[str, int]) -> Shelter:
        """Update shelter supplies."""
        shelter = self._shelters.get(shelter_id)
        if not shelter:
            raise ValueError(f"Shelter {shelter_id} not found")

        shelter.supplies.update(supplies)
        shelter.updated_at = datetime.utcnow()

        return shelter

    def request_supplies(
        self,
        shelter_id: str,
        items: List[Dict[str, Any]],
        priority: str,
        requested_by: str,
    ) -> SupplyRequest:
        """Request supplies for a shelter."""
        request_id = f"req-{uuid.uuid4().hex[:8]}"

        request = SupplyRequest(
            request_id=request_id,
            shelter_id=shelter_id,
            items=items,
            priority=priority,
            status="pending",
            requested_by=requested_by,
            requested_at=datetime.utcnow(),
            fulfilled_at=None,
            notes="",
        )

        self._supply_requests[request_id] = request
        return request

    def get_shelter(self, shelter_id: str) -> Optional[Shelter]:
        """Get shelter by ID."""
        return self._shelters.get(shelter_id)

    def get_shelters(
        self,
        status: Optional[ShelterStatus] = None,
        shelter_type: Optional[ShelterType] = None,
    ) -> List[Shelter]:
        """Get shelters, optionally filtered."""
        shelters = list(self._shelters.values())
        if status:
            shelters = [s for s in shelters if s.status == status]
        if shelter_type:
            shelters = [s for s in shelters if s.shelter_type == shelter_type]
        return shelters

    def get_available_capacity(self) -> int:
        """Get total available capacity across all open shelters."""
        open_shelters = self.get_shelters(status=ShelterStatus.OPEN)
        return sum(s.capacity - s.current_occupancy for s in open_shelters)

    def get_metrics(self) -> Dict[str, Any]:
        """Get shelter metrics."""
        shelters = list(self._shelters.values())
        open_shelters = [s for s in shelters if s.status == ShelterStatus.OPEN]

        return {
            "total_shelters": len(shelters),
            "open_shelters": len(open_shelters),
            "total_capacity": sum(s.capacity for s in shelters),
            "current_occupancy": sum(s.current_occupancy for s in shelters),
            "available_capacity": self.get_available_capacity(),
            "by_type": {
                t.value: len([s for s in shelters if s.shelter_type == t])
                for t in ShelterType
            },
            "pending_requests": len([r for r in self._supply_requests.values() if r.status == "pending"]),
        }


class SupplyChainOptimizer:
    """
    Optimizes supply chain for emergency resources.
    """

    def __init__(self):
        self._inventory: Dict[str, SupplyItem] = {}
        self._warehouses: Dict[str, Dict[str, Any]] = {}

    def add_inventory(
        self,
        name: str,
        category: str,
        quantity: int,
        unit: str,
        location: str,
        minimum_stock: int = 0,
        supplier: str = "",
        cost_per_unit: float = 0.0,
    ) -> SupplyItem:
        """Add item to inventory."""
        item_id = f"item-{uuid.uuid4().hex[:8]}"

        cat_enum = SupplyCategory(category) if category in [c.value for c in SupplyCategory] else SupplyCategory.FOOD

        item = SupplyItem(
            item_id=item_id,
            name=name,
            category=cat_enum,
            quantity=quantity,
            unit=unit,
            location=location,
            status=ResourceStatus.AVAILABLE,
            expiration_date=None,
            minimum_stock=minimum_stock,
            reorder_point=int(minimum_stock * 1.5),
            supplier=supplier,
            cost_per_unit=cost_per_unit,
            last_restocked=datetime.utcnow(),
        )

        self._inventory[item_id] = item
        return item

    def update_quantity(self, item_id: str, quantity: int) -> SupplyItem:
        """Update item quantity."""
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        item.quantity = quantity
        return item

    def allocate_supplies(
        self,
        destination: str,
        items: List[Dict[str, int]],
    ) -> Dict[str, Any]:
        """Allocate supplies to a destination."""
        allocation_id = f"alloc-{uuid.uuid4().hex[:8]}"
        allocated_items = []

        for item_request in items:
            item_id = item_request.get("item_id")
            quantity = item_request.get("quantity", 0)

            item = self._inventory.get(item_id)
            if item and item.quantity >= quantity:
                item.quantity -= quantity
                allocated_items.append({
                    "item_id": item_id,
                    "name": item.name,
                    "quantity": quantity,
                    "status": "allocated",
                })
            else:
                allocated_items.append({
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "insufficient_stock",
                })

        return {
            "allocation_id": allocation_id,
            "destination": destination,
            "items": allocated_items,
            "created_at": datetime.utcnow().isoformat(),
        }

    def get_low_stock_items(self) -> List[SupplyItem]:
        """Get items below reorder point."""
        return [
            item for item in self._inventory.values()
            if item.quantity <= item.reorder_point
        ]

    def optimize_distribution(
        self,
        shelters: List[Dict[str, Any]],
        available_supplies: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Optimize supply distribution across shelters."""
        distribution_plan = []

        for shelter in shelters:
            shelter_id = shelter.get("shelter_id")
            occupancy = shelter.get("current_occupancy", 0)
            current_supplies = shelter.get("supplies", {})

            needed_water = max(0, (occupancy * 3) - current_supplies.get("water_gallons", 0))
            needed_meals = max(0, (occupancy * 3) - current_supplies.get("meals", 0))
            needed_cots = max(0, occupancy - current_supplies.get("cots", 0))

            if needed_water > 0 or needed_meals > 0 or needed_cots > 0:
                distribution_plan.append({
                    "shelter_id": shelter_id,
                    "supplies_needed": {
                        "water_gallons": needed_water,
                        "meals": needed_meals,
                        "cots": needed_cots,
                    },
                    "priority": "high" if occupancy > 100 else "medium",
                })

        return distribution_plan

    def get_inventory(self, category: Optional[SupplyCategory] = None) -> List[SupplyItem]:
        """Get inventory items, optionally filtered by category."""
        items = list(self._inventory.values())
        if category:
            items = [i for i in items if i.category == category]
        return items

    def get_metrics(self) -> Dict[str, Any]:
        """Get supply chain metrics."""
        items = list(self._inventory.values())
        return {
            "total_items": len(items),
            "total_value": sum(i.quantity * i.cost_per_unit for i in items),
            "low_stock_count": len(self.get_low_stock_items()),
            "by_category": {
                cat.value: sum(i.quantity for i in items if i.category == cat)
                for cat in SupplyCategory
            },
        }


class DeploymentAllocator:
    """
    Allocates emergency response units (police, fire, EMS, utilities).
    """

    def __init__(self):
        self._units: Dict[str, DeploymentUnit] = {}
        self._assignments: Dict[str, Dict[str, Any]] = {}

    def register_unit(
        self,
        name: str,
        deployment_type: str,
        personnel_count: int,
        equipment: List[str],
        current_location: Dict[str, Any],
        capabilities: Optional[List[str]] = None,
    ) -> DeploymentUnit:
        """Register a deployment unit."""
        unit_id = f"unit-{uuid.uuid4().hex[:8]}"

        type_enum = DeploymentType(deployment_type) if deployment_type in [t.value for t in DeploymentType] else DeploymentType.POLICE

        unit = DeploymentUnit(
            unit_id=unit_id,
            name=name,
            deployment_type=type_enum,
            personnel_count=personnel_count,
            equipment=equipment,
            current_location=current_location,
            assigned_location=None,
            status=ResourceStatus.AVAILABLE,
            shift_start=None,
            shift_end=None,
            contact_info={},
            capabilities=capabilities or [],
        )

        self._units[unit_id] = unit
        return unit

    def deploy_unit(
        self,
        unit_id: str,
        location: Dict[str, Any],
        mission: str,
        duration_hours: float,
    ) -> DeploymentUnit:
        """Deploy a unit to a location."""
        unit = self._units.get(unit_id)
        if not unit:
            raise ValueError(f"Unit {unit_id} not found")

        unit.assigned_location = location
        unit.status = ResourceStatus.DEPLOYED
        unit.shift_start = datetime.utcnow()

        assignment_id = f"assign-{uuid.uuid4().hex[:8]}"
        self._assignments[assignment_id] = {
            "assignment_id": assignment_id,
            "unit_id": unit_id,
            "location": location,
            "mission": mission,
            "duration_hours": duration_hours,
            "start_time": datetime.utcnow(),
            "status": "active",
        }

        return unit

    def recall_unit(self, unit_id: str) -> DeploymentUnit:
        """Recall a deployed unit."""
        unit = self._units.get(unit_id)
        if not unit:
            raise ValueError(f"Unit {unit_id} not found")

        unit.assigned_location = None
        unit.status = ResourceStatus.AVAILABLE
        unit.shift_end = datetime.utcnow()

        for assignment in self._assignments.values():
            if assignment.get("unit_id") == unit_id and assignment.get("status") == "active":
                assignment["status"] = "completed"
                assignment["end_time"] = datetime.utcnow()

        return unit

    def get_available_units(
        self,
        deployment_type: Optional[DeploymentType] = None,
    ) -> List[DeploymentUnit]:
        """Get available units, optionally filtered by type."""
        units = [u for u in self._units.values() if u.status == ResourceStatus.AVAILABLE]
        if deployment_type:
            units = [u for u in units if u.deployment_type == deployment_type]
        return units

    def get_deployed_units(self) -> List[DeploymentUnit]:
        """Get all deployed units."""
        return [u for u in self._units.values() if u.status == ResourceStatus.DEPLOYED]

    def optimize_deployment(
        self,
        incidents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Optimize unit deployment based on incidents."""
        recommendations = []
        available_units = self.get_available_units()

        for incident in incidents:
            incident_type = incident.get("type", "")
            location = incident.get("location", {})
            priority = incident.get("priority", "medium")

            recommended_type = self._get_recommended_unit_type(incident_type)
            matching_units = [
                u for u in available_units
                if u.deployment_type == recommended_type
            ]

            if matching_units:
                recommendations.append({
                    "incident": incident,
                    "recommended_unit": matching_units[0].unit_id,
                    "unit_type": recommended_type.value,
                    "priority": priority,
                })

        return recommendations

    def _get_recommended_unit_type(self, incident_type: str) -> DeploymentType:
        """Get recommended unit type for incident."""
        type_map = {
            "fire": DeploymentType.FIRE,
            "medical": DeploymentType.EMS,
            "rescue": DeploymentType.SEARCH_RESCUE,
            "security": DeploymentType.POLICE,
            "utility": DeploymentType.UTILITIES,
        }
        return type_map.get(incident_type.lower(), DeploymentType.POLICE)

    def get_unit(self, unit_id: str) -> Optional[DeploymentUnit]:
        """Get unit by ID."""
        return self._units.get(unit_id)

    def get_units(self, deployment_type: Optional[DeploymentType] = None) -> List[DeploymentUnit]:
        """Get all units, optionally filtered by type."""
        units = list(self._units.values())
        if deployment_type:
            units = [u for u in units if u.deployment_type == deployment_type]
        return units

    def get_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics."""
        units = list(self._units.values())
        return {
            "total_units": len(units),
            "available_units": len(self.get_available_units()),
            "deployed_units": len(self.get_deployed_units()),
            "total_personnel": sum(u.personnel_count for u in units),
            "by_type": {
                t.value: len([u for u in units if u.deployment_type == t])
                for t in DeploymentType
            },
            "active_assignments": len([a for a in self._assignments.values() if a.get("status") == "active"]),
        }


class CriticalInfrastructureMonitor:
    """
    Monitors critical infrastructure (power, water, communications).
    """

    def __init__(self):
        self._assets: Dict[str, InfrastructureAsset] = {}
        self._outages: Dict[str, Dict[str, Any]] = {}

    def register_asset(
        self,
        name: str,
        infrastructure_type: str,
        location: Dict[str, Any],
        capacity: float,
        backup_available: bool = False,
    ) -> InfrastructureAsset:
        """Register an infrastructure asset."""
        asset_id = f"asset-{uuid.uuid4().hex[:8]}"

        type_enum = InfrastructureType(infrastructure_type) if infrastructure_type in [t.value for t in InfrastructureType] else InfrastructureType.POWER

        asset = InfrastructureAsset(
            asset_id=asset_id,
            name=name,
            infrastructure_type=type_enum,
            location=location,
            status=InfrastructureStatus.OPERATIONAL,
            capacity=capacity,
            current_load=0,
            backup_available=backup_available,
            estimated_restoration=None,
            affected_population=0,
            priority=1,
            last_inspection=None,
            notes="",
        )

        self._assets[asset_id] = asset
        return asset

    def update_status(
        self,
        asset_id: str,
        status: str,
        affected_population: int = 0,
        estimated_restoration: Optional[datetime] = None,
    ) -> InfrastructureAsset:
        """Update asset status."""
        asset = self._assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        status_enum = InfrastructureStatus(status) if status in [s.value for s in InfrastructureStatus] else InfrastructureStatus.UNKNOWN

        asset.status = status_enum
        asset.affected_population = affected_population
        asset.estimated_restoration = estimated_restoration
        asset.updated_at = datetime.utcnow()

        if status_enum in [InfrastructureStatus.PARTIAL_OUTAGE, InfrastructureStatus.FULL_OUTAGE]:
            self._record_outage(asset)

        return asset

    def _record_outage(self, asset: InfrastructureAsset) -> None:
        """Record an outage event."""
        outage_id = f"outage-{uuid.uuid4().hex[:8]}"
        self._outages[outage_id] = {
            "outage_id": outage_id,
            "asset_id": asset.asset_id,
            "asset_name": asset.name,
            "infrastructure_type": asset.infrastructure_type.value,
            "status": asset.status.value,
            "affected_population": asset.affected_population,
            "start_time": datetime.utcnow(),
            "estimated_restoration": asset.estimated_restoration,
        }

    def get_asset(self, asset_id: str) -> Optional[InfrastructureAsset]:
        """Get asset by ID."""
        return self._assets.get(asset_id)

    def get_assets(
        self,
        infrastructure_type: Optional[InfrastructureType] = None,
        status: Optional[InfrastructureStatus] = None,
    ) -> List[InfrastructureAsset]:
        """Get assets, optionally filtered."""
        assets = list(self._assets.values())
        if infrastructure_type:
            assets = [a for a in assets if a.infrastructure_type == infrastructure_type]
        if status:
            assets = [a for a in assets if a.status == status]
        return assets

    def get_outages(self) -> List[Dict[str, Any]]:
        """Get all active outages."""
        return list(self._outages.values())

    def get_affected_population(self) -> int:
        """Get total affected population from all outages."""
        return sum(
            a.affected_population for a in self._assets.values()
            if a.status in [InfrastructureStatus.PARTIAL_OUTAGE, InfrastructureStatus.FULL_OUTAGE]
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get infrastructure metrics."""
        assets = list(self._assets.values())
        return {
            "total_assets": len(assets),
            "operational": len([a for a in assets if a.status == InfrastructureStatus.OPERATIONAL]),
            "degraded": len([a for a in assets if a.status == InfrastructureStatus.DEGRADED]),
            "outages": len([a for a in assets if a.status in [InfrastructureStatus.PARTIAL_OUTAGE, InfrastructureStatus.FULL_OUTAGE]]),
            "affected_population": self.get_affected_population(),
            "by_type": {
                t.value: len([a for a in assets if a.infrastructure_type == t])
                for t in InfrastructureType
            },
        }


class ResourceLogisticsManager:
    """
    Main resource logistics coordinator.
    """

    def __init__(self):
        self.shelter_registry = ShelterRegistry()
        self.supply_chain = SupplyChainOptimizer()
        self.deployment_allocator = DeploymentAllocator()
        self.infrastructure_monitor = CriticalInfrastructureMonitor()

    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall resource logistics metrics."""
        return {
            "shelters": self.shelter_registry.get_metrics(),
            "supplies": self.supply_chain.get_metrics(),
            "deployments": self.deployment_allocator.get_metrics(),
            "infrastructure": self.infrastructure_monitor.get_metrics(),
        }

    def get_resource_status_summary(self) -> Dict[str, Any]:
        """Get summary of all resource statuses."""
        return {
            "shelter_capacity_available": self.shelter_registry.get_available_capacity(),
            "low_stock_items": len(self.supply_chain.get_low_stock_items()),
            "available_units": len(self.deployment_allocator.get_available_units()),
            "infrastructure_outages": len([
                a for a in self.infrastructure_monitor.get_assets()
                if a.status in [InfrastructureStatus.PARTIAL_OUTAGE, InfrastructureStatus.FULL_OUTAGE]
            ]),
            "affected_population": self.infrastructure_monitor.get_affected_population(),
        }
