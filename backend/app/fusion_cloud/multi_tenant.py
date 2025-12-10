"""
MultiTenantManager - Multi-tenant architecture for G3TI Fusion Cloud

Manages:
- Tenant registry (cities, counties, police departments, task forces)
- Tenant profiles (data sources, policies, integrations)
- Resource isolation between tenants
"""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid
import hashlib


class TenantType(str, Enum):
    """Types of tenants in the fusion cloud"""
    CITY = "city"
    COUNTY = "county"
    STATE = "state"
    FEDERAL = "federal"
    POLICE_DEPARTMENT = "police_department"
    SHERIFF_OFFICE = "sheriff_office"
    TASK_FORCE = "task_force"
    FUSION_CENTER = "fusion_center"
    TRANSIT_AUTHORITY = "transit_authority"
    SCHOOL_DISTRICT = "school_district"
    UNIVERSITY = "university"
    PRIVATE_SECURITY = "private_security"


class TenantStatus(str, Enum):
    """Status of a tenant"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class DataSourceType(str, Enum):
    """Types of data sources a tenant can have"""
    CAD = "cad"
    RMS = "rms"
    LPR = "lpr"
    SHOTSPOTTER = "shotspotter"
    BODY_CAMERA = "body_camera"
    CCTV = "cctv"
    DRONE = "drone"
    SENSOR_GRID = "sensor_grid"
    NCIC = "ncic"
    NDEX = "ndex"
    ETRACE = "etrace"
    DHS_SAR = "dhs_sar"
    CUSTOM = "custom"


class IntegrationStatus(str, Enum):
    """Status of an integration"""
    CONFIGURED = "configured"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DataSource:
    """A data source for a tenant"""
    source_id: str
    source_type: DataSourceType
    name: str
    description: str = ""
    endpoint_url: str = ""
    api_version: str = ""
    credentials_ref: str = ""
    enabled: bool = True
    last_sync: Optional[datetime] = None
    sync_interval_seconds: int = 300
    record_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationConfig:
    """Configuration for a tenant integration"""
    integration_id: str
    name: str
    integration_type: str
    status: IntegrationStatus = IntegrationStatus.CONFIGURED
    endpoint_url: str = ""
    auth_type: str = "api_key"
    credentials_ref: str = ""
    enabled: bool = True
    inbound_enabled: bool = True
    outbound_enabled: bool = True
    data_filters: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: Dict[str, Any] = field(default_factory=dict)
    last_activity: Optional[datetime] = None
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantPolicy:
    """Policies governing tenant behavior"""
    policy_id: str
    name: str
    data_retention_days: int = 365
    max_users: int = 100
    max_concurrent_sessions: int = 50
    max_api_calls_per_minute: int = 1000
    allowed_data_classifications: List[str] = field(default_factory=lambda: ["unclassified", "law_enforcement_sensitive"])
    federation_enabled: bool = True
    cross_agency_sharing_enabled: bool = True
    audit_logging_required: bool = True
    mfa_required: bool = True
    ip_whitelist: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantProfile:
    """Profile information for a tenant"""
    profile_id: str
    display_name: str
    description: str = ""
    logo_url: str = ""
    primary_contact_name: str = ""
    primary_contact_email: str = ""
    primary_contact_phone: str = ""
    technical_contact_name: str = ""
    technical_contact_email: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "USA"
    timezone: str = "America/New_York"
    jurisdiction_codes: List[str] = field(default_factory=list)
    ori_number: str = ""
    ncic_agency_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantResource:
    """Resource allocation for a tenant"""
    resource_id: str
    tenant_id: str
    resource_type: str
    allocated_units: int
    used_units: int = 0
    max_units: int = 0
    unit_type: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tenant:
    """A tenant in the fusion cloud"""
    tenant_id: str
    name: str
    tenant_type: TenantType
    status: TenantStatus = TenantStatus.PENDING
    profile: Optional[TenantProfile] = None
    policy: Optional[TenantPolicy] = None
    data_sources: List[DataSource] = field(default_factory=list)
    integrations: List[IntegrationConfig] = field(default_factory=list)
    parent_tenant_id: Optional[str] = None
    child_tenant_ids: List[str] = field(default_factory=list)
    federation_partners: List[str] = field(default_factory=list)
    encryption_key_ref: str = ""
    database_schema: str = ""
    storage_bucket: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantMetrics:
    """Metrics for the multi-tenant system"""
    total_tenants: int = 0
    active_tenants: int = 0
    tenants_by_type: Dict[TenantType, int] = field(default_factory=dict)
    tenants_by_status: Dict[TenantStatus, int] = field(default_factory=dict)
    total_data_sources: int = 0
    total_integrations: int = 0
    total_users: int = 0
    total_api_calls_24h: int = 0


class MultiTenantManager:
    """
    Manages multi-tenant architecture for the G3TI Fusion Cloud.
    
    Provides:
    - Tenant registration and lifecycle management
    - Data source and integration management
    - Resource isolation between tenants
    - Policy enforcement
    """
    
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._tenants_by_name: Dict[str, str] = {}
        self._resources: Dict[str, List[TenantResource]] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
    
    def register_tenant(
        self,
        name: str,
        tenant_type: TenantType,
        profile: Optional[TenantProfile] = None,
        policy: Optional[TenantPolicy] = None,
        parent_tenant_id: Optional[str] = None,
    ) -> Optional[Tenant]:
        """Register a new tenant"""
        if name.lower() in self._tenants_by_name:
            return None
        
        tenant_id = f"tenant-{uuid.uuid4().hex[:12]}"
        
        if profile is None:
            profile = TenantProfile(
                profile_id=f"profile-{uuid.uuid4().hex[:8]}",
                display_name=name,
            )
        
        if policy is None:
            policy = TenantPolicy(
                policy_id=f"policy-{uuid.uuid4().hex[:8]}",
                name=f"{name} Default Policy",
            )
        
        database_schema = f"tenant_{tenant_id.replace('-', '_')}"
        storage_bucket = f"g3ti-fusion-{tenant_id}"
        encryption_key_ref = f"keys/{tenant_id}/master"
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            tenant_type=tenant_type,
            status=TenantStatus.PENDING,
            profile=profile,
            policy=policy,
            parent_tenant_id=parent_tenant_id,
            database_schema=database_schema,
            storage_bucket=storage_bucket,
            encryption_key_ref=encryption_key_ref,
        )
        
        if parent_tenant_id and parent_tenant_id in self._tenants:
            self._tenants[parent_tenant_id].child_tenant_ids.append(tenant_id)
        
        self._tenants[tenant_id] = tenant
        self._tenants_by_name[name.lower()] = tenant_id
        self._resources[tenant_id] = []
        
        self._record_event("tenant_registered", {
            "tenant_id": tenant_id,
            "name": name,
            "tenant_type": tenant_type.value,
        })
        self._notify_callbacks("tenant_registered", tenant)
        
        return tenant
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        if tenant.status != TenantStatus.PENDING:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.activated_at = datetime.utcnow()
        tenant.updated_at = datetime.utcnow()
        
        self._record_event("tenant_activated", {"tenant_id": tenant_id})
        self._notify_callbacks("tenant_activated", tenant)
        
        return True
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        tenant.status = TenantStatus.SUSPENDED
        tenant.updated_at = datetime.utcnow()
        tenant.metadata["suspension_reason"] = reason
        tenant.metadata["suspended_at"] = datetime.utcnow().isoformat()
        
        self._record_event("tenant_suspended", {
            "tenant_id": tenant_id,
            "reason": reason,
        })
        self._notify_callbacks("tenant_suspended", tenant)
        
        return True
    
    def reactivate_tenant(self, tenant_id: str) -> bool:
        """Reactivate a suspended tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        if tenant.status != TenantStatus.SUSPENDED:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.updated_at = datetime.utcnow()
        tenant.metadata.pop("suspension_reason", None)
        tenant.metadata.pop("suspended_at", None)
        
        self._record_event("tenant_reactivated", {"tenant_id": tenant_id})
        self._notify_callbacks("tenant_reactivated", tenant)
        
        return True
    
    def archive_tenant(self, tenant_id: str) -> bool:
        """Archive a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        tenant.status = TenantStatus.ARCHIVED
        tenant.updated_at = datetime.utcnow()
        tenant.metadata["archived_at"] = datetime.utcnow().isoformat()
        
        self._record_event("tenant_archived", {"tenant_id": tenant_id})
        self._notify_callbacks("tenant_archived", tenant)
        
        return True
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID"""
        return self._tenants.get(tenant_id)
    
    def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        """Get a tenant by name"""
        tenant_id = self._tenants_by_name.get(name.lower())
        if tenant_id:
            return self._tenants.get(tenant_id)
        return None
    
    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants"""
        return list(self._tenants.values())
    
    def get_tenants_by_type(self, tenant_type: TenantType) -> List[Tenant]:
        """Get tenants by type"""
        return [t for t in self._tenants.values() if t.tenant_type == tenant_type]
    
    def get_tenants_by_status(self, status: TenantStatus) -> List[Tenant]:
        """Get tenants by status"""
        return [t for t in self._tenants.values() if t.status == status]
    
    def get_active_tenants(self) -> List[Tenant]:
        """Get all active tenants"""
        return self.get_tenants_by_status(TenantStatus.ACTIVE)
    
    def get_child_tenants(self, parent_tenant_id: str) -> List[Tenant]:
        """Get child tenants of a parent"""
        if parent_tenant_id not in self._tenants:
            return []
        
        parent = self._tenants[parent_tenant_id]
        return [self._tenants[tid] for tid in parent.child_tenant_ids if tid in self._tenants]
    
    def update_tenant_profile(
        self,
        tenant_id: str,
        profile: TenantProfile,
    ) -> bool:
        """Update tenant profile"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        tenant.profile = profile
        tenant.updated_at = datetime.utcnow()
        
        self._record_event("tenant_profile_updated", {"tenant_id": tenant_id})
        self._notify_callbacks("tenant_profile_updated", tenant)
        
        return True
    
    def update_tenant_policy(
        self,
        tenant_id: str,
        policy: TenantPolicy,
    ) -> bool:
        """Update tenant policy"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        tenant.policy = policy
        tenant.updated_at = datetime.utcnow()
        
        self._record_event("tenant_policy_updated", {"tenant_id": tenant_id})
        self._notify_callbacks("tenant_policy_updated", tenant)
        
        return True
    
    def add_data_source(
        self,
        tenant_id: str,
        data_source: DataSource,
    ) -> bool:
        """Add a data source to a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        
        existing_ids = {ds.source_id for ds in tenant.data_sources}
        if data_source.source_id in existing_ids:
            return False
        
        tenant.data_sources.append(data_source)
        tenant.updated_at = datetime.utcnow()
        
        self._record_event("data_source_added", {
            "tenant_id": tenant_id,
            "source_id": data_source.source_id,
            "source_type": data_source.source_type.value,
        })
        self._notify_callbacks("data_source_added", {"tenant": tenant, "data_source": data_source})
        
        return True
    
    def remove_data_source(
        self,
        tenant_id: str,
        source_id: str,
    ) -> bool:
        """Remove a data source from a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        original_count = len(tenant.data_sources)
        tenant.data_sources = [ds for ds in tenant.data_sources if ds.source_id != source_id]
        
        if len(tenant.data_sources) < original_count:
            tenant.updated_at = datetime.utcnow()
            self._record_event("data_source_removed", {
                "tenant_id": tenant_id,
                "source_id": source_id,
            })
            return True
        
        return False
    
    def get_data_sources(self, tenant_id: str) -> List[DataSource]:
        """Get all data sources for a tenant"""
        if tenant_id not in self._tenants:
            return []
        return self._tenants[tenant_id].data_sources
    
    def add_integration(
        self,
        tenant_id: str,
        integration: IntegrationConfig,
    ) -> bool:
        """Add an integration to a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        
        existing_ids = {i.integration_id for i in tenant.integrations}
        if integration.integration_id in existing_ids:
            return False
        
        tenant.integrations.append(integration)
        tenant.updated_at = datetime.utcnow()
        
        self._record_event("integration_added", {
            "tenant_id": tenant_id,
            "integration_id": integration.integration_id,
            "integration_type": integration.integration_type,
        })
        self._notify_callbacks("integration_added", {"tenant": tenant, "integration": integration})
        
        return True
    
    def remove_integration(
        self,
        tenant_id: str,
        integration_id: str,
    ) -> bool:
        """Remove an integration from a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        original_count = len(tenant.integrations)
        tenant.integrations = [i for i in tenant.integrations if i.integration_id != integration_id]
        
        if len(tenant.integrations) < original_count:
            tenant.updated_at = datetime.utcnow()
            self._record_event("integration_removed", {
                "tenant_id": tenant_id,
                "integration_id": integration_id,
            })
            return True
        
        return False
    
    def update_integration_status(
        self,
        tenant_id: str,
        integration_id: str,
        status: IntegrationStatus,
    ) -> bool:
        """Update integration status"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        for integration in tenant.integrations:
            if integration.integration_id == integration_id:
                integration.status = status
                integration.last_activity = datetime.utcnow()
                tenant.updated_at = datetime.utcnow()
                
                self._record_event("integration_status_updated", {
                    "tenant_id": tenant_id,
                    "integration_id": integration_id,
                    "status": status.value,
                })
                return True
        
        return False
    
    def get_integrations(self, tenant_id: str) -> List[IntegrationConfig]:
        """Get all integrations for a tenant"""
        if tenant_id not in self._tenants:
            return []
        return self._tenants[tenant_id].integrations
    
    def add_federation_partner(
        self,
        tenant_id: str,
        partner_tenant_id: str,
    ) -> bool:
        """Add a federation partner to a tenant"""
        if tenant_id not in self._tenants or partner_tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        partner = self._tenants[partner_tenant_id]
        
        if partner_tenant_id not in tenant.federation_partners:
            tenant.federation_partners.append(partner_tenant_id)
            tenant.updated_at = datetime.utcnow()
        
        if tenant_id not in partner.federation_partners:
            partner.federation_partners.append(tenant_id)
            partner.updated_at = datetime.utcnow()
        
        self._record_event("federation_partner_added", {
            "tenant_id": tenant_id,
            "partner_tenant_id": partner_tenant_id,
        })
        self._notify_callbacks("federation_partner_added", {
            "tenant": tenant,
            "partner": partner,
        })
        
        return True
    
    def remove_federation_partner(
        self,
        tenant_id: str,
        partner_tenant_id: str,
    ) -> bool:
        """Remove a federation partner from a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        
        if partner_tenant_id in tenant.federation_partners:
            tenant.federation_partners.remove(partner_tenant_id)
            tenant.updated_at = datetime.utcnow()
            
            if partner_tenant_id in self._tenants:
                partner = self._tenants[partner_tenant_id]
                if tenant_id in partner.federation_partners:
                    partner.federation_partners.remove(tenant_id)
                    partner.updated_at = datetime.utcnow()
            
            self._record_event("federation_partner_removed", {
                "tenant_id": tenant_id,
                "partner_tenant_id": partner_tenant_id,
            })
            return True
        
        return False
    
    def get_federation_partners(self, tenant_id: str) -> List[Tenant]:
        """Get all federation partners for a tenant"""
        if tenant_id not in self._tenants:
            return []
        
        tenant = self._tenants[tenant_id]
        return [self._tenants[pid] for pid in tenant.federation_partners if pid in self._tenants]
    
    def allocate_resource(
        self,
        tenant_id: str,
        resource_type: str,
        allocated_units: int,
        max_units: int,
        unit_type: str = "",
    ) -> Optional[TenantResource]:
        """Allocate a resource to a tenant"""
        if tenant_id not in self._tenants:
            return None
        
        resource = TenantResource(
            resource_id=f"resource-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            resource_type=resource_type,
            allocated_units=allocated_units,
            max_units=max_units,
            unit_type=unit_type,
        )
        
        self._resources[tenant_id].append(resource)
        
        self._record_event("resource_allocated", {
            "tenant_id": tenant_id,
            "resource_id": resource.resource_id,
            "resource_type": resource_type,
        })
        
        return resource
    
    def get_tenant_resources(self, tenant_id: str) -> List[TenantResource]:
        """Get all resources for a tenant"""
        return self._resources.get(tenant_id, [])
    
    def validate_tenant_access(
        self,
        tenant_id: str,
        user_id: str,
        resource_type: str,
        action: str,
    ) -> bool:
        """Validate if a user has access to a resource in a tenant"""
        if tenant_id not in self._tenants:
            return False
        
        tenant = self._tenants[tenant_id]
        
        if tenant.status != TenantStatus.ACTIVE:
            return False
        
        return True
    
    def get_metrics(self) -> TenantMetrics:
        """Get metrics for the multi-tenant system"""
        metrics = TenantMetrics()
        metrics.total_tenants = len(self._tenants)
        
        for tenant in self._tenants.values():
            if tenant.status == TenantStatus.ACTIVE:
                metrics.active_tenants += 1
            
            metrics.tenants_by_type[tenant.tenant_type] = \
                metrics.tenants_by_type.get(tenant.tenant_type, 0) + 1
            metrics.tenants_by_status[tenant.status] = \
                metrics.tenants_by_status.get(tenant.status, 0) + 1
            
            metrics.total_data_sources += len(tenant.data_sources)
            metrics.total_integrations += len(tenant.integrations)
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str, callback: Callable) -> bool:
        """Unregister a callback"""
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
            return True
        return False
    
    def _record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record an event"""
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def _notify_callbacks(self, event_type: str, data: Any) -> None:
        """Notify registered callbacks"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
