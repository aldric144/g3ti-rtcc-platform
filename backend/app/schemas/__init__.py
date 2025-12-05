"""
Pydantic schemas for the G3TI RTCC-UIP Backend.

This module contains all request/response schemas organized by domain:
- auth: Authentication and user schemas
- entities: Graph entity schemas (Person, Vehicle, Incident, etc.)
- investigations: Investigation and case schemas
- events: Real-time event schemas
- common: Shared base schemas and utilities
"""

from app.schemas.auth import (
    LoginRequest,
    PasswordChange,
    Role,
    Token,
    TokenPayload,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)
from app.schemas.common import (
    ErrorResponse,
    HealthCheck,
    PaginatedResponse,
)
from app.schemas.entities import (
    AddressCreate,
    AddressResponse,
    AssociationCreate,
    AssociationResponse,
    CameraCreate,
    CameraResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    LicensePlateCreate,
    LicensePlateResponse,
    PersonCreate,
    PersonResponse,
    PersonUpdate,
    ShellCasingCreate,
    ShellCasingResponse,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
    WeaponCreate,
    WeaponResponse,
)
from app.schemas.events import (
    EventBase,
    EventCreate,
    EventResponse,
    EventSubscription,
    WebSocketMessage,
)
from app.schemas.investigations import (
    InvestigationCreate,
    InvestigationResponse,
    InvestigationUpdate,
    SearchQuery,
    SearchResult,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "Token",
    "TokenPayload",
    "LoginRequest",
    "PasswordChange",
    "Role",
    # Entities
    "PersonCreate",
    "PersonUpdate",
    "PersonResponse",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentResponse",
    "WeaponCreate",
    "WeaponResponse",
    "ShellCasingCreate",
    "ShellCasingResponse",
    "AddressCreate",
    "AddressResponse",
    "CameraCreate",
    "CameraResponse",
    "LicensePlateCreate",
    "LicensePlateResponse",
    "AssociationCreate",
    "AssociationResponse",
    # Events
    "EventBase",
    "EventCreate",
    "EventResponse",
    "WebSocketMessage",
    "EventSubscription",
    # Investigations
    "InvestigationCreate",
    "InvestigationUpdate",
    "InvestigationResponse",
    "SearchQuery",
    "SearchResult",
    # Common
    "PaginatedResponse",
    "HealthCheck",
    "ErrorResponse",
]
