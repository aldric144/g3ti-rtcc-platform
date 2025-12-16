"""
G3TI RTCC Admin Suite - Backend Admin Modules
Phase: RTCC-ADMIN-SUITE-X

This module provides comprehensive admin functionality for the RTCC platform including:
- 15 admin modules for data management
- CRUD operations for all entities
- Validation engine
- Audit logging
- Role-based access control
"""

from .cameras_admin import CameraAdmin, CameraModel, CameraCreate, CameraUpdate
from .drones_admin import DroneAdmin, DroneModel, DroneCreate, DroneUpdate
from .robots_admin import RobotAdmin, RobotModel, RobotCreate, RobotUpdate
from .lpr_zones_admin import LPRZoneAdmin, LPRZoneModel, LPRZoneCreate, LPRZoneUpdate
from .sectors_admin import SectorAdmin, SectorModel, SectorCreate, SectorUpdate
from .fire_preplans_admin import FirePreplanAdmin, FirePreplanModel, FirePreplanCreate, FirePreplanUpdate
from .infrastructure_admin import InfrastructureAdmin, InfrastructureModel, InfrastructureCreate, InfrastructureUpdate
from .schools_admin import SchoolAdmin, SchoolModel, SchoolCreate, SchoolUpdate
from .dv_risk_homes_admin import DVRiskHomeAdmin, DVRiskHomeModel, DVRiskHomeCreate, DVRiskHomeUpdate
from .incidents_admin import IncidentAdmin, IncidentModel, IncidentCreate, IncidentUpdate
from .api_connections_admin import APIConnectionAdmin, APIConnectionModel, APIConnectionCreate, APIConnectionUpdate
from .events_admin import EventAdmin, EventModel, EventCreate, EventUpdate
from .hydrants_admin import HydrantAdmin, HydrantModel, HydrantCreate, HydrantUpdate
from .users_admin import UserAdmin, UserModel, UserCreate, UserUpdate
from .system_settings_admin import SystemSettingsAdmin, SystemSettingsModel, SystemSettingsCreate, SystemSettingsUpdate
from .validation import ValidationEngine
from .audit_log import AuditLogger

__all__ = [
    # Cameras
    "CameraAdmin", "CameraModel", "CameraCreate", "CameraUpdate",
    # Drones
    "DroneAdmin", "DroneModel", "DroneCreate", "DroneUpdate",
    # Robots
    "RobotAdmin", "RobotModel", "RobotCreate", "RobotUpdate",
    # LPR Zones
    "LPRZoneAdmin", "LPRZoneModel", "LPRZoneCreate", "LPRZoneUpdate",
    # Sectors
    "SectorAdmin", "SectorModel", "SectorCreate", "SectorUpdate",
    # Fire Preplans
    "FirePreplanAdmin", "FirePreplanModel", "FirePreplanCreate", "FirePreplanUpdate",
    # Infrastructure
    "InfrastructureAdmin", "InfrastructureModel", "InfrastructureCreate", "InfrastructureUpdate",
    # Schools
    "SchoolAdmin", "SchoolModel", "SchoolCreate", "SchoolUpdate",
    # DV Risk Homes
    "DVRiskHomeAdmin", "DVRiskHomeModel", "DVRiskHomeCreate", "DVRiskHomeUpdate",
    # Incidents
    "IncidentAdmin", "IncidentModel", "IncidentCreate", "IncidentUpdate",
    # API Connections
    "APIConnectionAdmin", "APIConnectionModel", "APIConnectionCreate", "APIConnectionUpdate",
    # Events
    "EventAdmin", "EventModel", "EventCreate", "EventUpdate",
    # Hydrants
    "HydrantAdmin", "HydrantModel", "HydrantCreate", "HydrantUpdate",
    # Users
    "UserAdmin", "UserModel", "UserCreate", "UserUpdate",
    # System Settings
    "SystemSettingsAdmin", "SystemSettingsModel", "SystemSettingsCreate", "SystemSettingsUpdate",
    # Utilities
    "ValidationEngine", "AuditLogger",
]
