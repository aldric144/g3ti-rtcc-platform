"""
Phase 38: Cross-Module Resource Manager
Manages shared assets across RTCC subsystems including drones, robots,
dispatch units, sensor grid, AI compute resources, and global intel feeds.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid


class ResourceType(Enum):
    DRONE = "drone"
    ROBOT = "robot"
    DISPATCH_UNIT = "dispatch_unit"
    SENSOR = "sensor"
    AI_COMPUTE = "ai_compute"
    INTEL_FEED = "intel_feed"
    COMMUNICATION_CHANNEL = "communication_channel"
    CAMERA = "camera"
    LPR_READER = "lpr_reader"
    GUNSHOT_DETECTOR = "gunshot_detector"
    WEATHER_STATION = "weather_station"
    TRAFFIC_SENSOR = "traffic_sensor"
    OFFICER = "officer"
    VEHICLE = "vehicle"
    HELICOPTER = "helicopter"
    BOAT = "boat"


class ResourceStatus(Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    RESERVED = "reserved"
    RETURNING = "returning"
    CHARGING = "charging"
    DEPLOYING = "deploying"


class AllocationPriority(Enum):
    EMERGENCY = 1
    CRITICAL = 2
    HIGH = 3
    MEDIUM = 4
    LOW = 5


@dataclass
class Resource:
    resource_id: str = field(default_factory=lambda: f"res-{uuid.uuid4().hex[:12]}")
    resource_type: ResourceType = ResourceType.SENSOR
    name: str = ""
    description: str = ""
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: Optional[Dict[str, float]] = None
    capabilities: List[str] = field(default_factory=list)
    capacity: float = 100.0
    current_load: float = 0.0
    battery_level: Optional[float] = None
    fuel_level: Optional[float] = None
    health_score: float = 100.0
    assigned_to: Optional[str] = None
    assigned_workflow: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if resource is available for allocation."""
        return self.status == ResourceStatus.AVAILABLE and self.health_score > 50.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "location": self.location,
            "capabilities": self.capabilities,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "battery_level": self.battery_level,
            "fuel_level": self.fuel_level,
            "health_score": self.health_score,
            "assigned_to": self.assigned_to,
            "assigned_workflow": self.assigned_workflow,
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ResourceAllocation:
    allocation_id: str = field(default_factory=lambda: f"alloc-{uuid.uuid4().hex[:8]}")
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.SENSOR
    workflow_id: str = ""
    requester_id: str = ""
    priority: AllocationPriority = AllocationPriority.MEDIUM
    purpose: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: int = 60
    location: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    released_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocation_id": self.allocation_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "workflow_id": self.workflow_id,
            "requester_id": self.requester_id,
            "priority": self.priority.value,
            "purpose": self.purpose,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "parameters": self.parameters,
            "status": self.status,
            "released_at": self.released_at.isoformat() if self.released_at else None,
        }


class ResourceManager:
    """
    Manages shared resources across all RTCC subsystems.
    Handles allocation, scheduling, and optimization of assets.
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

        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.reservation_queue: List[ResourceAllocation] = []
        self.statistics: Dict[str, Any] = {
            "total_allocations": 0,
            "active_allocations": 0,
            "completed_allocations": 0,
            "failed_allocations": 0,
            "average_allocation_duration_minutes": 0.0,
        }
        self._register_default_resources()

    def _register_default_resources(self):
        """Register default RTCC resources."""
        default_resources = [
            Resource(
                resource_type=ResourceType.DRONE,
                name="Sentinel-1",
                capabilities=["surveillance", "thermal", "spotlight", "speaker"],
                battery_level=100.0,
                location={"lat": 26.7753, "lng": -80.0589},
            ),
            Resource(
                resource_type=ResourceType.DRONE,
                name="Sentinel-2",
                capabilities=["surveillance", "thermal", "spotlight"],
                battery_level=85.0,
                location={"lat": 26.7800, "lng": -80.0550},
            ),
            Resource(
                resource_type=ResourceType.DRONE,
                name="Sentinel-3",
                capabilities=["surveillance", "zoom", "night_vision"],
                battery_level=92.0,
                location={"lat": 26.7700, "lng": -80.0620},
            ),
            Resource(
                resource_type=ResourceType.ROBOT,
                name="Guardian-1",
                capabilities=["patrol", "communication", "sensor_array"],
                battery_level=100.0,
                location={"lat": 26.7753, "lng": -80.0589},
            ),
            Resource(
                resource_type=ResourceType.ROBOT,
                name="Guardian-2",
                capabilities=["patrol", "communication", "hazmat_detection"],
                battery_level=78.0,
                location={"lat": 26.7780, "lng": -80.0560},
            ),
            Resource(
                resource_type=ResourceType.DISPATCH_UNIT,
                name="Unit-101",
                capabilities=["patrol", "response", "traffic"],
                fuel_level=85.0,
                location={"lat": 26.7760, "lng": -80.0580},
            ),
            Resource(
                resource_type=ResourceType.DISPATCH_UNIT,
                name="Unit-102",
                capabilities=["patrol", "response", "k9"],
                fuel_level=92.0,
                location={"lat": 26.7740, "lng": -80.0600},
            ),
            Resource(
                resource_type=ResourceType.DISPATCH_UNIT,
                name="Unit-103",
                capabilities=["patrol", "response", "tactical"],
                fuel_level=78.0,
                location={"lat": 26.7720, "lng": -80.0570},
            ),
            Resource(
                resource_type=ResourceType.AI_COMPUTE,
                name="AI-Cluster-Primary",
                capabilities=["inference", "training", "analytics"],
                capacity=1000.0,
                current_load=350.0,
            ),
            Resource(
                resource_type=ResourceType.AI_COMPUTE,
                name="AI-Cluster-Secondary",
                capabilities=["inference", "analytics"],
                capacity=500.0,
                current_load=120.0,
            ),
            Resource(
                resource_type=ResourceType.INTEL_FEED,
                name="FBI-NICS",
                capabilities=["background_check", "criminal_history"],
            ),
            Resource(
                resource_type=ResourceType.INTEL_FEED,
                name="NCIC",
                capabilities=["wanted_persons", "stolen_vehicles", "missing_persons"],
            ),
            Resource(
                resource_type=ResourceType.INTEL_FEED,
                name="Fusion-Center",
                capabilities=["threat_intel", "terrorism", "organized_crime"],
            ),
            Resource(
                resource_type=ResourceType.SENSOR,
                name="Gunshot-Detector-Grid",
                capabilities=["gunshot_detection", "triangulation"],
                location={"lat": 26.7753, "lng": -80.0589},
            ),
            Resource(
                resource_type=ResourceType.LPR_READER,
                name="LPR-Network",
                capabilities=["plate_recognition", "hot_list_alert"],
            ),
            Resource(
                resource_type=ResourceType.CAMERA,
                name="CCTV-Network",
                capabilities=["video_surveillance", "facial_recognition", "analytics"],
            ),
        ]
        for resource in default_resources:
            self.resources[resource.resource_id] = resource

    def register_resource(self, resource: Resource) -> bool:
        """Register a new resource."""
        self.resources[resource.resource_id] = resource
        return True

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            return True
        return False

    def update_resource_status(
        self, resource_id: str, status: ResourceStatus
    ) -> bool:
        """Update resource status."""
        if resource_id in self.resources:
            self.resources[resource_id].status = status
            self.resources[resource_id].last_activity = datetime.utcnow()
            return True
        return False

    def update_resource_location(
        self, resource_id: str, location: Dict[str, float]
    ) -> bool:
        """Update resource location."""
        if resource_id in self.resources:
            self.resources[resource_id].location = location
            self.resources[resource_id].last_activity = datetime.utcnow()
            return True
        return False

    def allocate_resource(
        self,
        resource_id: str,
        workflow_id: str,
        requester_id: str,
        purpose: str,
        priority: AllocationPriority = AllocationPriority.MEDIUM,
        duration_minutes: int = 60,
        location: Dict[str, float] = None,
        parameters: Dict[str, Any] = None,
    ) -> Optional[ResourceAllocation]:
        """Allocate a resource to a workflow."""
        resource = self.resources.get(resource_id)
        if not resource:
            return None

        if not resource.is_available():
            if priority.value < AllocationPriority.HIGH.value:
                current_alloc = self.get_resource_allocation(resource_id)
                if current_alloc and current_alloc.priority.value > priority.value:
                    self.release_resource(resource_id)
                else:
                    return None
            else:
                return None

        allocation = ResourceAllocation(
            resource_id=resource_id,
            resource_type=resource.resource_type,
            workflow_id=workflow_id,
            requester_id=requester_id,
            priority=priority,
            purpose=purpose,
            duration_minutes=duration_minutes,
            location=location,
            parameters=parameters or {},
        )

        resource.status = ResourceStatus.ALLOCATED
        resource.assigned_to = requester_id
        resource.assigned_workflow = workflow_id
        resource.last_activity = datetime.utcnow()

        self.allocations[allocation.allocation_id] = allocation
        self.statistics["total_allocations"] += 1
        self.statistics["active_allocations"] += 1

        return allocation

    def release_resource(self, resource_id: str) -> bool:
        """Release a resource from its current allocation."""
        resource = self.resources.get(resource_id)
        if not resource:
            return False

        for alloc_id, allocation in list(self.allocations.items()):
            if allocation.resource_id == resource_id and allocation.status == "active":
                allocation.status = "completed"
                allocation.released_at = datetime.utcnow()
                allocation.end_time = datetime.utcnow()
                self.allocation_history.append(allocation)
                del self.allocations[alloc_id]
                self.statistics["active_allocations"] -= 1
                self.statistics["completed_allocations"] += 1

        resource.status = ResourceStatus.AVAILABLE
        resource.assigned_to = None
        resource.assigned_workflow = None
        resource.last_activity = datetime.utcnow()

        return True

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)

    def get_resource_allocation(self, resource_id: str) -> Optional[ResourceAllocation]:
        """Get current allocation for a resource."""
        for allocation in self.allocations.values():
            if allocation.resource_id == resource_id and allocation.status == "active":
                return allocation
        return None

    def get_available_resources(
        self, resource_type: ResourceType = None, capabilities: List[str] = None
    ) -> List[Resource]:
        """Get available resources optionally filtered by type and capabilities."""
        available = [r for r in self.resources.values() if r.is_available()]
        if resource_type:
            available = [r for r in available if r.resource_type == resource_type]
        if capabilities:
            available = [
                r for r in available
                if all(cap in r.capabilities for cap in capabilities)
            ]
        return available

    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """Get all resources of a specific type."""
        return [r for r in self.resources.values() if r.resource_type == resource_type]

    def get_nearest_resource(
        self,
        location: Dict[str, float],
        resource_type: ResourceType,
        capabilities: List[str] = None,
    ) -> Optional[Resource]:
        """Get nearest available resource to a location."""
        available = self.get_available_resources(resource_type, capabilities)
        if not available:
            return None

        def distance(r: Resource) -> float:
            if not r.location:
                return float("inf")
            return (
                (r.location["lat"] - location["lat"]) ** 2 +
                (r.location["lng"] - location["lng"]) ** 2
            ) ** 0.5

        return min(available, key=distance)

    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get all resources."""
        return [r.to_dict() for r in self.resources.values()]

    def get_active_allocations(self) -> List[Dict[str, Any]]:
        """Get all active allocations."""
        return [a.to_dict() for a in self.allocations.values() if a.status == "active"]

    def get_allocation_history(
        self, limit: int = 100, resource_type: ResourceType = None
    ) -> List[Dict[str, Any]]:
        """Get allocation history."""
        history = self.allocation_history[-limit:]
        if resource_type:
            history = [a for a in history if a.resource_type == resource_type]
        return [a.to_dict() for a in history]

    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization statistics."""
        utilization = {}
        for resource_type in ResourceType:
            resources = self.get_resources_by_type(resource_type)
            if resources:
                total = len(resources)
                available = len([r for r in resources if r.is_available()])
                in_use = len([r for r in resources if r.status == ResourceStatus.IN_USE])
                allocated = len([r for r in resources if r.status == ResourceStatus.ALLOCATED])
                utilization[resource_type.value] = {
                    "total": total,
                    "available": available,
                    "in_use": in_use,
                    "allocated": allocated,
                    "utilization_rate": ((total - available) / total) * 100 if total > 0 else 0,
                }
        return utilization

    def get_statistics(self) -> Dict[str, Any]:
        """Get resource manager statistics."""
        return {
            **self.statistics,
            "total_resources": len(self.resources),
            "available_resources": len([r for r in self.resources.values() if r.is_available()]),
            "resources_by_type": {
                rt.value: len(self.get_resources_by_type(rt)) for rt in ResourceType
            },
            "utilization": self.get_resource_utilization(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def optimize_allocations(self) -> Dict[str, Any]:
        """Optimize current resource allocations."""
        optimizations = []
        for allocation in self.allocations.values():
            resource = self.resources.get(allocation.resource_id)
            if resource and resource.battery_level and resource.battery_level < 20:
                optimizations.append({
                    "type": "low_battery_warning",
                    "resource_id": allocation.resource_id,
                    "recommendation": "Consider releasing or replacing resource",
                })
        return {
            "optimizations": optimizations,
            "timestamp": datetime.utcnow().isoformat(),
        }
