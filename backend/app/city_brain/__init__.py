"""
Phase 22: AI City Brain Engine

Complete city simulation, prediction, and autonomous governance system
for Riviera Beach, Florida (33404).

This module provides:
- CityBrainCore: Central orchestrator for all city systems
- CityProfileLoader: Loads and manages city profile data
- Real-time data ingestion from federal, state, and local systems
- Digital twin with dynamic object rendering
- City prediction engine for traffic, crime, infrastructure, and disasters
- City input console for manual event management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import json
import os
import uuid


class CityModuleType(Enum):
    """Types of city brain modules."""
    WEATHER = "weather"
    TRAFFIC = "traffic"
    UTILITIES = "utilities"
    INCIDENTS = "incidents"
    DIGITAL_TWIN = "digital_twin"
    PREDICTIONS = "predictions"
    INGESTION = "ingestion"
    ADMIN = "admin"


class EventPriority(Enum):
    """Priority levels for city events."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class CityEventType(Enum):
    """Types of city events."""
    WEATHER_ALERT = "weather_alert"
    TRAFFIC_INCIDENT = "traffic_incident"
    UTILITY_OUTAGE = "utility_outage"
    CRIME_INCIDENT = "crime_incident"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    SCHEDULED_EVENT = "scheduled_event"
    EMERGENCY_DECLARATION = "emergency_declaration"
    PREDICTION_ALERT = "prediction_alert"
    SYSTEM_STATUS = "system_status"


@dataclass
class CityEvent:
    """Represents an event in the city brain system."""
    event_id: str
    event_type: CityEventType
    priority: EventPriority
    title: str
    description: str
    location: Optional[dict] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_module: Optional[CityModuleType] = None
    data: dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    acknowledged: bool = False


@dataclass
class ModuleStatus:
    """Status of a city brain module."""
    module_type: CityModuleType
    name: str
    status: str
    last_update: datetime
    health_score: float
    error_count: int = 0
    warning_count: int = 0
    metrics: dict = field(default_factory=dict)


@dataclass
class CityState:
    """Current state snapshot of the city."""
    timestamp: datetime
    weather: dict
    traffic: dict
    utilities: dict
    incidents: dict
    predictions: dict
    population_estimate: int
    active_events: list
    module_statuses: dict
    overall_health: float


class EventBus:
    """Internal event bus for cross-module communication."""
    
    def __init__(self):
        self._subscribers: dict[CityEventType, list[Callable]] = {}
        self._event_history: list[CityEvent] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: CityEventType, callback: Callable) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: CityEventType, callback: Callable) -> None:
        """Unsubscribe from events."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]
    
    def publish(self, event: CityEvent) -> None:
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    pass
    
    def get_recent_events(self, count: int = 100) -> list[CityEvent]:
        """Get recent events from history."""
        return self._event_history[-count:]
    
    def get_events_by_type(self, event_type: CityEventType) -> list[CityEvent]:
        """Get events of a specific type."""
        return [e for e in self._event_history if e.event_type == event_type]


class CityProfileLoader:
    """Loads and manages city profile data for Riviera Beach."""
    
    def __init__(self, profile_path: Optional[str] = None):
        self._profile_path = profile_path or os.path.join(
            os.path.dirname(__file__),
            "data",
            "riviera_beach_profile.json"
        )
        self._profile: Optional[dict] = None
        self._loaded_at: Optional[datetime] = None
    
    def load(self) -> dict:
        """Load the city profile from JSON file."""
        with open(self._profile_path, 'r') as f:
            self._profile = json.load(f)
        self._loaded_at = datetime.utcnow()
        return self._profile
    
    def get_profile(self) -> dict:
        """Get the loaded city profile."""
        if self._profile is None:
            self.load()
        return self._profile
    
    def get_city_info(self) -> dict:
        """Get basic city information."""
        profile = self.get_profile()
        return profile.get("city", {})
    
    def get_bounding_box(self) -> dict:
        """Get city bounding box coordinates."""
        profile = self.get_profile()
        return profile.get("bounding_box", {})
    
    def get_districts(self) -> list[dict]:
        """Get city districts."""
        profile = self.get_profile()
        return profile.get("districts", [])
    
    def get_flood_zones(self) -> list[dict]:
        """Get flood zone information."""
        profile = self.get_profile()
        return profile.get("flood_zones", [])
    
    def get_schools(self) -> list[dict]:
        """Get school locations."""
        profile = self.get_profile()
        return profile.get("schools", [])
    
    def get_police_stations(self) -> list[dict]:
        """Get police station locations."""
        profile = self.get_profile()
        return profile.get("police_stations", [])
    
    def get_fire_stations(self) -> list[dict]:
        """Get fire station locations."""
        profile = self.get_profile()
        return profile.get("fire_stations", [])
    
    def get_marina(self) -> dict:
        """Get marina information."""
        profile = self.get_profile()
        return profile.get("marina", {})
    
    def get_major_roads(self) -> list[dict]:
        """Get major road information."""
        profile = self.get_profile()
        return profile.get("major_roads", [])
    
    def get_utility_zones(self) -> list[dict]:
        """Get utility zone information."""
        profile = self.get_profile()
        return profile.get("utility_zones", [])
    
    def get_critical_infrastructure(self) -> list[dict]:
        """Get critical infrastructure locations."""
        profile = self.get_profile()
        return profile.get("critical_infrastructure", [])
    
    def get_hurricane_zones(self) -> dict:
        """Get hurricane evacuation zone information."""
        profile = self.get_profile()
        return profile.get("hurricane_zones", {})
    
    def get_population_density(self) -> dict:
        """Get population density information."""
        profile = self.get_profile()
        return profile.get("population_density", {})
    
    def get_elevation_data(self) -> dict:
        """Get elevation data."""
        profile = self.get_profile()
        return profile.get("elevation_data", {})
    
    def get_points_of_interest(self) -> list[dict]:
        """Get points of interest."""
        profile = self.get_profile()
        return profile.get("points_of_interest", [])
    
    def get_churches(self) -> list[dict]:
        """Get church locations."""
        profile = self.get_profile()
        return profile.get("churches", [])
    
    def get_nearby_hospitals(self) -> list[dict]:
        """Get nearby hospital information."""
        profile = self.get_profile()
        return profile.get("hospitals_nearby", [])


class CityBrainCore:
    """
    Central orchestrator for the AI City Brain Engine.
    
    Manages all city brain modules and coordinates cross-module communication
    for Riviera Beach, Florida (33404).
    """
    
    def __init__(self):
        self._profile_loader = CityProfileLoader()
        self._event_bus = EventBus()
        self._modules: dict[CityModuleType, ModuleStatus] = {}
        self._active_events: list[CityEvent] = []
        self._city_state: Optional[CityState] = None
        self._started_at: Optional[datetime] = None
        self._health_check_interval = 30
        
        self._weather_data: dict = {}
        self._traffic_data: dict = {}
        self._utility_data: dict = {}
        self._incident_data: dict = {}
        self._prediction_data: dict = {}
        
        self._initialize_modules()
    
    def _initialize_modules(self) -> None:
        """Initialize all city brain modules."""
        module_configs = [
            (CityModuleType.WEATHER, "Weather Module"),
            (CityModuleType.TRAFFIC, "Traffic Module"),
            (CityModuleType.UTILITIES, "Utilities Module"),
            (CityModuleType.INCIDENTS, "Incidents Module"),
            (CityModuleType.DIGITAL_TWIN, "Digital Twin Module"),
            (CityModuleType.PREDICTIONS, "Predictions Module"),
            (CityModuleType.INGESTION, "Data Ingestion Module"),
            (CityModuleType.ADMIN, "Admin Console Module"),
        ]
        
        for module_type, name in module_configs:
            self._modules[module_type] = ModuleStatus(
                module_type=module_type,
                name=name,
                status="initialized",
                last_update=datetime.utcnow(),
                health_score=1.0,
            )
    
    def start(self) -> None:
        """Start the city brain engine."""
        self._started_at = datetime.utcnow()
        self._profile_loader.load()
        
        for module_type in self._modules:
            self._modules[module_type].status = "running"
            self._modules[module_type].last_update = datetime.utcnow()
        
        self._publish_event(
            CityEventType.SYSTEM_STATUS,
            EventPriority.LOW,
            "City Brain Started",
            "AI City Brain Engine has been initialized for Riviera Beach, FL 33404",
            source_module=CityModuleType.ADMIN,
        )
    
    def stop(self) -> None:
        """Stop the city brain engine."""
        for module_type in self._modules:
            self._modules[module_type].status = "stopped"
            self._modules[module_type].last_update = datetime.utcnow()
        
        self._publish_event(
            CityEventType.SYSTEM_STATUS,
            EventPriority.LOW,
            "City Brain Stopped",
            "AI City Brain Engine has been stopped",
            source_module=CityModuleType.ADMIN,
        )
    
    def get_profile_loader(self) -> CityProfileLoader:
        """Get the city profile loader."""
        return self._profile_loader
    
    def get_event_bus(self) -> EventBus:
        """Get the event bus for cross-module communication."""
        return self._event_bus
    
    def get_module_status(self, module_type: CityModuleType) -> ModuleStatus:
        """Get status of a specific module."""
        return self._modules.get(module_type)
    
    def get_all_module_statuses(self) -> dict[CityModuleType, ModuleStatus]:
        """Get status of all modules."""
        return self._modules.copy()
    
    def update_module_status(
        self,
        module_type: CityModuleType,
        status: str,
        health_score: float,
        metrics: Optional[dict] = None,
    ) -> None:
        """Update the status of a module."""
        if module_type in self._modules:
            self._modules[module_type].status = status
            self._modules[module_type].health_score = health_score
            self._modules[module_type].last_update = datetime.utcnow()
            if metrics:
                self._modules[module_type].metrics = metrics
    
    def update_weather_data(self, data: dict) -> None:
        """Update weather data from ingestion."""
        self._weather_data = data
        self._weather_data["updated_at"] = datetime.utcnow().isoformat()
        self.update_module_status(CityModuleType.WEATHER, "running", 1.0)
    
    def update_traffic_data(self, data: dict) -> None:
        """Update traffic data from ingestion."""
        self._traffic_data = data
        self._traffic_data["updated_at"] = datetime.utcnow().isoformat()
        self.update_module_status(CityModuleType.TRAFFIC, "running", 1.0)
    
    def update_utility_data(self, data: dict) -> None:
        """Update utility data from ingestion."""
        self._utility_data = data
        self._utility_data["updated_at"] = datetime.utcnow().isoformat()
        self.update_module_status(CityModuleType.UTILITIES, "running", 1.0)
    
    def update_incident_data(self, data: dict) -> None:
        """Update incident data from ingestion."""
        self._incident_data = data
        self._incident_data["updated_at"] = datetime.utcnow().isoformat()
        self.update_module_status(CityModuleType.INCIDENTS, "running", 1.0)
    
    def update_prediction_data(self, data: dict) -> None:
        """Update prediction data."""
        self._prediction_data = data
        self._prediction_data["updated_at"] = datetime.utcnow().isoformat()
        self.update_module_status(CityModuleType.PREDICTIONS, "running", 1.0)
    
    def get_weather_data(self) -> dict:
        """Get current weather data."""
        return self._weather_data
    
    def get_traffic_data(self) -> dict:
        """Get current traffic data."""
        return self._traffic_data
    
    def get_utility_data(self) -> dict:
        """Get current utility data."""
        return self._utility_data
    
    def get_incident_data(self) -> dict:
        """Get current incident data."""
        return self._incident_data
    
    def get_prediction_data(self) -> dict:
        """Get current prediction data."""
        return self._prediction_data
    
    def add_event(self, event: CityEvent) -> None:
        """Add an event to the active events list."""
        self._active_events.append(event)
        self._event_bus.publish(event)
    
    def get_active_events(self) -> list[CityEvent]:
        """Get all active events."""
        now = datetime.utcnow()
        self._active_events = [
            e for e in self._active_events
            if e.expires_at is None or e.expires_at > now
        ]
        return self._active_events
    
    def acknowledge_event(self, event_id: str) -> bool:
        """Acknowledge an event."""
        for event in self._active_events:
            if event.event_id == event_id:
                event.acknowledged = True
                return True
        return False
    
    def _publish_event(
        self,
        event_type: CityEventType,
        priority: EventPriority,
        title: str,
        description: str,
        location: Optional[dict] = None,
        source_module: Optional[CityModuleType] = None,
        data: Optional[dict] = None,
    ) -> CityEvent:
        """Create and publish an event."""
        event = CityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            priority=priority,
            title=title,
            description=description,
            location=location,
            source_module=source_module,
            data=data or {},
        )
        self.add_event(event)
        return event
    
    def get_city_state(self) -> CityState:
        """Get current city state snapshot."""
        profile = self._profile_loader.get_profile()
        city_info = profile.get("city", {})
        
        module_statuses = {
            mt.value: {
                "status": ms.status,
                "health_score": ms.health_score,
                "last_update": ms.last_update.isoformat(),
            }
            for mt, ms in self._modules.items()
        }
        
        overall_health = sum(
            ms.health_score for ms in self._modules.values()
        ) / len(self._modules)
        
        self._city_state = CityState(
            timestamp=datetime.utcnow(),
            weather=self._weather_data,
            traffic=self._traffic_data,
            utilities=self._utility_data,
            incidents=self._incident_data,
            predictions=self._prediction_data,
            population_estimate=city_info.get("population", 0),
            active_events=[
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "priority": e.priority.value,
                    "title": e.title,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.get_active_events()
            ],
            module_statuses=module_statuses,
            overall_health=overall_health,
        )
        
        return self._city_state
    
    def get_health_status(self) -> dict:
        """Get health status for system diagnostics (Phase 14 integration)."""
        return {
            "service": "city_brain",
            "status": "healthy" if all(
                ms.health_score > 0.5 for ms in self._modules.values()
            ) else "degraded",
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "modules": {
                mt.value: {
                    "status": ms.status,
                    "health_score": ms.health_score,
                    "error_count": ms.error_count,
                    "warning_count": ms.warning_count,
                }
                for mt, ms in self._modules.items()
            },
            "active_events_count": len(self._active_events),
            "city": self._profile_loader.get_city_info().get("name", "Unknown"),
        }
    
    def register_with_diagnostics(self) -> dict:
        """Register city brain with Phase 14 diagnostics system."""
        return {
            "service_name": "city_brain",
            "service_type": "city_simulation",
            "health_endpoint": "/api/citybrain/health",
            "check_interval_seconds": self._health_check_interval,
            "dependencies": [
                "weather_ingestion",
                "traffic_ingestion",
                "utility_ingestion",
                "incident_ingestion",
            ],
        }


_city_brain_instance: Optional[CityBrainCore] = None


def get_city_brain() -> CityBrainCore:
    """Get the singleton city brain instance."""
    global _city_brain_instance
    if _city_brain_instance is None:
        _city_brain_instance = CityBrainCore()
    return _city_brain_instance


__all__ = [
    "CityBrainCore",
    "CityProfileLoader",
    "EventBus",
    "CityEvent",
    "CityState",
    "ModuleStatus",
    "CityModuleType",
    "CityEventType",
    "EventPriority",
    "get_city_brain",
]
