"""
Fusion Cloud API Router

Provides REST API endpoints for:
- /api/fusion/tenants - Tenant management
- /api/fusion/federation - Cross-agency data federation
- /api/fusion/jointops - Joint operations management
- /api/fusion/analytics - Federated analytics
- /api/fusion/intel - Shared intelligence hub
- /api/fusion/security - Security gateway
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.fusion_cloud import (
    MultiTenantManager,
    TenantType,
    TenantStatus,
    TenantProfile,
    TenantPolicy,
    DataSource,
    DataSourceType,
    IntegrationConfig,
    IntegrationStatus,
    FederationLayer,
    FederatedDataType,
    DataClassification,
    SensitivityLevel,
    ClearanceLevel,
    SharedIntelHub,
    ChannelType,
    MessagePriority,
    JointOpsManager,
    OperationType,
    OperationStatus,
    OperationRole,
    TimelineEventType,
    WhiteboardItemType,
    FederatedAnalyticsEngine,
    HeatmapType,
    ClusterType,
    SecureAccessGateway,
    AccessDecision,
)

router = APIRouter(prefix="/api/fusion", tags=["fusion-cloud"])

tenant_manager = MultiTenantManager()
federation_layer = FederationLayer()
intel_hub = SharedIntelHub()
joint_ops_manager = JointOpsManager()
analytics_engine = FederatedAnalyticsEngine()
security_gateway = SecureAccessGateway()


class TenantProfileCreate(BaseModel):
    display_name: str
    description: str = ""
    primary_contact_name: str = ""
    primary_contact_email: str = ""
    primary_contact_phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    timezone: str = "America/New_York"
    ori_number: str = ""


class TenantPolicyCreate(BaseModel):
    name: str
    data_retention_days: int = 365
    max_users: int = 100
    federation_enabled: bool = True
    cross_agency_sharing_enabled: bool = True
    mfa_required: bool = True


class TenantCreate(BaseModel):
    name: str
    tenant_type: TenantType
    profile: Optional[TenantProfileCreate] = None
    policy: Optional[TenantPolicyCreate] = None
    parent_tenant_id: Optional[str] = None


class DataSourceCreate(BaseModel):
    source_type: DataSourceType
    name: str
    description: str = ""
    endpoint_url: str = ""
    api_version: str = ""
    enabled: bool = True
    sync_interval_seconds: int = 300


class IntegrationCreate(BaseModel):
    name: str
    integration_type: str
    endpoint_url: str = ""
    auth_type: str = "api_key"
    enabled: bool = True
    inbound_enabled: bool = True
    outbound_enabled: bool = True


class FederatedDataPublish(BaseModel):
    data_type: FederatedDataType
    title: str
    payload: Dict[str, Any]
    classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE
    sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED
    jurisdiction_codes: List[str] = []
    share_with_tenants: List[str] = []
    description: str = ""
    expires_in_days: Optional[int] = None


class PermissionCreate(BaseModel):
    target_tenant_id: str
    data_types: List[FederatedDataType]
    max_classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE
    auto_share: bool = False
    require_approval: bool = True
    expires_in_days: Optional[int] = None


class SubscriptionCreate(BaseModel):
    publisher_tenant_id: str
    data_types: List[FederatedDataType]
    jurisdiction_filters: List[str] = []
    webhook_url: str = ""
    notification_enabled: bool = True


class IntelMessagePublish(BaseModel):
    channel_type: ChannelType
    title: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    summary: str = ""
    jurisdiction_codes: List[str] = []
    tags: List[str] = []
    expires_in_hours: Optional[int] = None


class JointOperationCreate(BaseModel):
    name: str
    operation_type: OperationType
    description: str = ""
    commander_name: str = ""
    commander_contact: str = ""
    jurisdiction_codes: List[str] = []
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None


class AgencyAdd(BaseModel):
    agency_name: str
    role: OperationRole = OperationRole.UNIT_MEMBER
    lead_contact_name: str = ""
    lead_contact_phone: str = ""
    jurisdiction_codes: List[str] = []


class UnitDeploy(BaseModel):
    agency_name: str
    call_sign: str
    unit_type: str = ""
    personnel_count: int = 1
    role: OperationRole = OperationRole.UNIT_MEMBER
    latitude: float = 0.0
    longitude: float = 0.0
    capabilities: List[str] = []


class ObjectiveCreate(BaseModel):
    name: str
    description: str = ""
    priority: int = 1
    assigned_agencies: List[str] = []
    due_at: Optional[datetime] = None


class TimelineEventCreate(BaseModel):
    event_type: TimelineEventType
    title: str
    description: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    is_critical: bool = False


class HeatmapCreate(BaseModel):
    heatmap_type: HeatmapType
    name: str
    region_codes: List[str]
    tenant_ids: List[str]
    resolution: int = 8
    description: str = ""
    time_range_days: int = 30


class ClusterCreate(BaseModel):
    cluster_type: ClusterType
    name: str
    center_lat: float
    center_lon: float
    radius_km: float = 1.0
    jurisdictions: List[str] = []
    tenants: List[str] = []
    crime_types: List[str] = []
    description: str = ""


class RiskMapCreate(BaseModel):
    name: str
    region_codes: List[str]
    tenant_ids: List[str]
    resolution: int = 8
    description: str = ""
    valid_hours: int = 24


@router.post("/tenants")
async def register_tenant(tenant_data: TenantCreate):
    """Register a new tenant"""
    profile = None
    if tenant_data.profile:
        profile = TenantProfile(
            profile_id=f"profile-temp",
            display_name=tenant_data.profile.display_name,
            description=tenant_data.profile.description,
            primary_contact_name=tenant_data.profile.primary_contact_name,
            primary_contact_email=tenant_data.profile.primary_contact_email,
            primary_contact_phone=tenant_data.profile.primary_contact_phone,
            address=tenant_data.profile.address,
            city=tenant_data.profile.city,
            state=tenant_data.profile.state,
            zip_code=tenant_data.profile.zip_code,
            timezone=tenant_data.profile.timezone,
            ori_number=tenant_data.profile.ori_number,
        )
    
    policy = None
    if tenant_data.policy:
        policy = TenantPolicy(
            policy_id=f"policy-temp",
            name=tenant_data.policy.name,
            data_retention_days=tenant_data.policy.data_retention_days,
            max_users=tenant_data.policy.max_users,
            federation_enabled=tenant_data.policy.federation_enabled,
            cross_agency_sharing_enabled=tenant_data.policy.cross_agency_sharing_enabled,
            mfa_required=tenant_data.policy.mfa_required,
        )
    
    tenant = tenant_manager.register_tenant(
        name=tenant_data.name,
        tenant_type=tenant_data.tenant_type,
        profile=profile,
        policy=policy,
        parent_tenant_id=tenant_data.parent_tenant_id,
    )
    
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant with this name already exists")
    
    return {"status": "success", "tenant_id": tenant.tenant_id, "tenant": tenant}


@router.get("/tenants")
async def list_tenants(
    tenant_type: Optional[TenantType] = None,
    status: Optional[TenantStatus] = None,
):
    """List all tenants"""
    if tenant_type:
        tenants = tenant_manager.get_tenants_by_type(tenant_type)
    elif status:
        tenants = tenant_manager.get_tenants_by_status(status)
    else:
        tenants = tenant_manager.get_all_tenants()
    
    return {"status": "success", "count": len(tenants), "tenants": tenants}


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get a tenant by ID"""
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"status": "success", "tenant": tenant}


@router.put("/tenants/{tenant_id}/activate")
async def activate_tenant(tenant_id: str):
    """Activate a tenant"""
    success = tenant_manager.activate_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to activate tenant")
    return {"status": "success", "message": "Tenant activated"}


@router.put("/tenants/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str, reason: str = ""):
    """Suspend a tenant"""
    success = tenant_manager.suspend_tenant(tenant_id, reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to suspend tenant")
    return {"status": "success", "message": "Tenant suspended"}


@router.post("/tenants/{tenant_id}/data-sources")
async def add_data_source(tenant_id: str, data_source: DataSourceCreate):
    """Add a data source to a tenant"""
    import uuid
    ds = DataSource(
        source_id=f"ds-{uuid.uuid4().hex[:8]}",
        source_type=data_source.source_type,
        name=data_source.name,
        description=data_source.description,
        endpoint_url=data_source.endpoint_url,
        api_version=data_source.api_version,
        enabled=data_source.enabled,
        sync_interval_seconds=data_source.sync_interval_seconds,
    )
    
    success = tenant_manager.add_data_source(tenant_id, ds)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add data source")
    
    return {"status": "success", "source_id": ds.source_id}


@router.get("/tenants/{tenant_id}/data-sources")
async def get_data_sources(tenant_id: str):
    """Get data sources for a tenant"""
    sources = tenant_manager.get_data_sources(tenant_id)
    return {"status": "success", "count": len(sources), "data_sources": sources}


@router.post("/tenants/{tenant_id}/integrations")
async def add_integration(tenant_id: str, integration: IntegrationCreate):
    """Add an integration to a tenant"""
    import uuid
    integ = IntegrationConfig(
        integration_id=f"int-{uuid.uuid4().hex[:8]}",
        name=integration.name,
        integration_type=integration.integration_type,
        endpoint_url=integration.endpoint_url,
        auth_type=integration.auth_type,
        enabled=integration.enabled,
        inbound_enabled=integration.inbound_enabled,
        outbound_enabled=integration.outbound_enabled,
    )
    
    success = tenant_manager.add_integration(tenant_id, integ)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add integration")
    
    return {"status": "success", "integration_id": integ.integration_id}


@router.get("/tenants/{tenant_id}/integrations")
async def get_integrations(tenant_id: str):
    """Get integrations for a tenant"""
    integrations = tenant_manager.get_integrations(tenant_id)
    return {"status": "success", "count": len(integrations), "integrations": integrations}


@router.post("/tenants/{tenant_id}/federation-partners/{partner_id}")
async def add_federation_partner(tenant_id: str, partner_id: str):
    """Add a federation partner"""
    success = tenant_manager.add_federation_partner(tenant_id, partner_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add federation partner")
    return {"status": "success", "message": "Federation partner added"}


@router.get("/tenants/metrics")
async def get_tenant_metrics():
    """Get tenant metrics"""
    metrics = tenant_manager.get_metrics()
    return {"status": "success", "metrics": metrics}


@router.post("/federation/publish")
async def publish_federated_data(
    source_tenant_id: str,
    source_agency_name: str,
    data: FederatedDataPublish,
):
    """Publish federated data"""
    federated_data = federation_layer.publish_data(
        source_tenant_id=source_tenant_id,
        source_agency_name=source_agency_name,
        data_type=data.data_type,
        title=data.title,
        payload=data.payload,
        classification=data.classification,
        sensitivity=data.sensitivity,
        jurisdiction_codes=data.jurisdiction_codes,
        share_with_tenants=data.share_with_tenants,
        description=data.description,
        expires_in_days=data.expires_in_days,
    )
    
    if not federated_data:
        raise HTTPException(status_code=400, detail="Failed to publish data")
    
    return {"status": "success", "data_id": federated_data.data_id}


@router.get("/federation/data/{data_id}")
async def get_federated_data(data_id: str):
    """Get federated data by ID"""
    data = federation_layer.get_data(data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return {"status": "success", "data": data}


@router.get("/federation/data")
async def get_federated_data_for_tenant(
    tenant_id: str,
    data_types: Optional[List[FederatedDataType]] = Query(None),
    limit: int = 100,
):
    """Get federated data for a tenant"""
    data = federation_layer.get_data_for_tenant(
        tenant_id=tenant_id,
        data_types=data_types,
        limit=limit,
    )
    return {"status": "success", "count": len(data), "data": data}


@router.post("/federation/share/{data_id}")
async def share_data_with_tenant(data_id: str, target_tenant_id: str):
    """Share data with a tenant"""
    success = federation_layer.share_data_with_tenant(data_id, target_tenant_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to share data")
    return {"status": "success", "message": "Data shared"}


@router.post("/federation/permissions")
async def create_permission(source_tenant_id: str, permission: PermissionCreate):
    """Create a federation permission"""
    perm = federation_layer.create_permission(
        source_tenant_id=source_tenant_id,
        target_tenant_id=permission.target_tenant_id,
        data_types=permission.data_types,
        max_classification=permission.max_classification,
        auto_share=permission.auto_share,
        require_approval=permission.require_approval,
        expires_in_days=permission.expires_in_days,
    )
    
    if not perm:
        raise HTTPException(status_code=400, detail="Failed to create permission")
    
    return {"status": "success", "permission_id": perm.permission_id}


@router.get("/federation/permissions/{tenant_id}")
async def get_permissions(tenant_id: str):
    """Get permissions for a tenant"""
    permissions = federation_layer.get_permissions_for_tenant(tenant_id)
    return {"status": "success", "count": len(permissions), "permissions": permissions}


@router.post("/federation/subscriptions")
async def create_subscription(subscriber_tenant_id: str, subscription: SubscriptionCreate):
    """Create a federation subscription"""
    sub = federation_layer.create_subscription(
        subscriber_tenant_id=subscriber_tenant_id,
        publisher_tenant_id=subscription.publisher_tenant_id,
        data_types=subscription.data_types,
        jurisdiction_filters=subscription.jurisdiction_filters,
        webhook_url=subscription.webhook_url,
        notification_enabled=subscription.notification_enabled,
    )
    
    if not sub:
        raise HTTPException(status_code=400, detail="Failed to create subscription")
    
    return {"status": "success", "subscription_id": sub.subscription_id}


@router.put("/federation/subscriptions/{subscription_id}/activate")
async def activate_subscription(subscription_id: str):
    """Activate a subscription"""
    success = federation_layer.activate_subscription(subscription_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to activate subscription")
    return {"status": "success", "message": "Subscription activated"}


@router.get("/federation/subscriptions/{tenant_id}")
async def get_subscriptions(tenant_id: str):
    """Get subscriptions for a tenant"""
    subscriptions = federation_layer.get_subscriptions_for_tenant(tenant_id)
    return {"status": "success", "count": len(subscriptions), "subscriptions": subscriptions}


@router.get("/federation/metrics")
async def get_federation_metrics():
    """Get federation metrics"""
    metrics = federation_layer.get_metrics()
    return {"status": "success", "metrics": metrics}


@router.get("/intel/channels")
async def list_channels(tenant_id: Optional[str] = None):
    """List intelligence channels"""
    if tenant_id:
        channels = intel_hub.get_channels_for_tenant(tenant_id)
    else:
        channels = intel_hub.get_all_channels()
    return {"status": "success", "count": len(channels), "channels": channels}


@router.get("/intel/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get a channel by ID"""
    channel = intel_hub.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"status": "success", "channel": channel}


@router.post("/intel/channels/{channel_id}/subscribe")
async def subscribe_to_channel(
    channel_id: str,
    tenant_id: str,
    priority_filter: Optional[List[MessagePriority]] = Query(None),
    webhook_url: str = "",
):
    """Subscribe to a channel"""
    subscription = intel_hub.subscribe_to_channel(
        channel_id=channel_id,
        tenant_id=tenant_id,
        priority_filter=priority_filter,
        webhook_url=webhook_url,
    )
    
    if not subscription:
        raise HTTPException(status_code=400, detail="Failed to subscribe")
    
    return {"status": "success", "subscription_id": subscription.subscription_id}


@router.post("/intel/messages")
async def publish_intel_message(
    source_tenant_id: str,
    source_agency_name: str,
    message: IntelMessagePublish,
):
    """Publish an intelligence message"""
    channel = intel_hub.get_channel_by_type(message.channel_type)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    msg = intel_hub.publish_message(
        channel_id=channel.channel_id,
        source_tenant_id=source_tenant_id,
        source_agency_name=source_agency_name,
        title=message.title,
        content=message.content,
        priority=message.priority,
        summary=message.summary,
        jurisdiction_codes=message.jurisdiction_codes,
        tags=message.tags,
        expires_in_hours=message.expires_in_hours,
    )
    
    if not msg:
        raise HTTPException(status_code=400, detail="Failed to publish message")
    
    return {"status": "success", "message_id": msg.message_id}


@router.get("/intel/messages/{channel_id}")
async def get_channel_messages(
    channel_id: str,
    limit: int = 100,
    priority_filter: Optional[List[MessagePriority]] = Query(None),
):
    """Get messages from a channel"""
    messages = intel_hub.get_channel_messages(
        channel_id=channel_id,
        limit=limit,
        priority_filter=priority_filter,
    )
    return {"status": "success", "count": len(messages), "messages": messages}


@router.put("/intel/messages/{message_id}/acknowledge")
async def acknowledge_message(message_id: str, tenant_id: str):
    """Acknowledge a message"""
    success = intel_hub.acknowledge_message(message_id, tenant_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to acknowledge message")
    return {"status": "success", "message": "Message acknowledged"}


@router.get("/intel/metrics")
async def get_intel_metrics():
    """Get intel hub metrics"""
    metrics = intel_hub.get_hub_metrics()
    return {"status": "success", "metrics": metrics}


@router.post("/jointops")
async def create_joint_operation(
    lead_tenant_id: str,
    lead_agency_name: str,
    operation: JointOperationCreate,
):
    """Create a joint operation"""
    op = joint_ops_manager.create_operation(
        name=operation.name,
        operation_type=operation.operation_type,
        lead_tenant_id=lead_tenant_id,
        lead_agency_name=lead_agency_name,
        description=operation.description,
        commander_name=operation.commander_name,
        commander_contact=operation.commander_contact,
        jurisdiction_codes=operation.jurisdiction_codes,
        planned_start=operation.planned_start,
        planned_end=operation.planned_end,
    )
    
    if not op:
        raise HTTPException(status_code=400, detail="Failed to create operation")
    
    return {"status": "success", "operation_id": op.operation_id, "room_id": op.room.room_id if op.room else None}


@router.get("/jointops")
async def list_operations(
    tenant_id: Optional[str] = None,
    status: Optional[OperationStatus] = None,
):
    """List joint operations"""
    if tenant_id:
        operations = joint_ops_manager.get_operations_for_tenant(tenant_id)
    elif status:
        operations = joint_ops_manager.get_operations_by_status(status)
    else:
        operations = joint_ops_manager.get_all_operations()
    
    return {"status": "success", "count": len(operations), "operations": operations}


@router.get("/jointops/{operation_id}")
async def get_operation(operation_id: str):
    """Get an operation by ID"""
    operation = joint_ops_manager.get_operation(operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return {"status": "success", "operation": operation}


@router.put("/jointops/{operation_id}/start")
async def start_operation(operation_id: str):
    """Start an operation"""
    success = joint_ops_manager.start_operation(operation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start operation")
    return {"status": "success", "message": "Operation started"}


@router.put("/jointops/{operation_id}/pause")
async def pause_operation(operation_id: str, reason: str = ""):
    """Pause an operation"""
    success = joint_ops_manager.pause_operation(operation_id, reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause operation")
    return {"status": "success", "message": "Operation paused"}


@router.put("/jointops/{operation_id}/resume")
async def resume_operation(operation_id: str):
    """Resume an operation"""
    success = joint_ops_manager.resume_operation(operation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resume operation")
    return {"status": "success", "message": "Operation resumed"}


@router.put("/jointops/{operation_id}/complete")
async def complete_operation(operation_id: str, summary: str = ""):
    """Complete an operation"""
    success = joint_ops_manager.complete_operation(operation_id, summary)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to complete operation")
    return {"status": "success", "message": "Operation completed"}


@router.post("/jointops/{operation_id}/agencies")
async def add_agency_to_operation(operation_id: str, tenant_id: str, agency: AgencyAdd):
    """Add an agency to an operation"""
    participation = joint_ops_manager.add_agency(
        operation_id=operation_id,
        tenant_id=tenant_id,
        agency_name=agency.agency_name,
        role=agency.role,
        lead_contact_name=agency.lead_contact_name,
        lead_contact_phone=agency.lead_contact_phone,
        jurisdiction_codes=agency.jurisdiction_codes,
    )
    
    if not participation:
        raise HTTPException(status_code=400, detail="Failed to add agency")
    
    return {"status": "success", "participation_id": participation.participation_id}


@router.delete("/jointops/{operation_id}/agencies/{tenant_id}")
async def remove_agency_from_operation(operation_id: str, tenant_id: str, reason: str = ""):
    """Remove an agency from an operation"""
    success = joint_ops_manager.remove_agency(operation_id, tenant_id, reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove agency")
    return {"status": "success", "message": "Agency removed"}


@router.put("/jointops/{operation_id}/agencies/{tenant_id}/role")
async def assign_agency_role(operation_id: str, tenant_id: str, role: OperationRole):
    """Assign a role to an agency"""
    success = joint_ops_manager.assign_role(operation_id, tenant_id, role)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign role")
    return {"status": "success", "message": "Role assigned"}


@router.post("/jointops/{operation_id}/units")
async def deploy_unit(operation_id: str, tenant_id: str, unit: UnitDeploy):
    """Deploy a unit to an operation"""
    deployed_unit = joint_ops_manager.deploy_unit(
        operation_id=operation_id,
        tenant_id=tenant_id,
        agency_name=unit.agency_name,
        call_sign=unit.call_sign,
        unit_type=unit.unit_type,
        personnel_count=unit.personnel_count,
        role=unit.role,
        latitude=unit.latitude,
        longitude=unit.longitude,
        capabilities=unit.capabilities,
    )
    
    if not deployed_unit:
        raise HTTPException(status_code=400, detail="Failed to deploy unit")
    
    return {"status": "success", "unit_id": deployed_unit.unit_id}


@router.put("/jointops/{operation_id}/units/{unit_id}/position")
async def update_unit_position(operation_id: str, unit_id: str, latitude: float, longitude: float):
    """Update unit position"""
    success = joint_ops_manager.update_unit_position(operation_id, unit_id, latitude, longitude)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update position")
    return {"status": "success", "message": "Position updated"}


@router.post("/jointops/{operation_id}/objectives")
async def add_objective(operation_id: str, objective: ObjectiveCreate):
    """Add an objective to an operation"""
    obj = joint_ops_manager.add_objective(
        operation_id=operation_id,
        name=objective.name,
        description=objective.description,
        priority=objective.priority,
        assigned_agencies=objective.assigned_agencies,
        due_at=objective.due_at,
    )
    
    if not obj:
        raise HTTPException(status_code=400, detail="Failed to add objective")
    
    return {"status": "success", "objective_id": obj.objective_id}


@router.put("/jointops/{operation_id}/objectives/{objective_id}/complete")
async def complete_objective(operation_id: str, objective_id: str, notes: str = ""):
    """Complete an objective"""
    success = joint_ops_manager.complete_objective(operation_id, objective_id, notes=notes)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to complete objective")
    return {"status": "success", "message": "Objective completed"}


@router.get("/jointops/{operation_id}/timeline")
async def get_operation_timeline(
    operation_id: str,
    tenant_id: Optional[str] = None,
    limit: int = 100,
):
    """Get operation timeline"""
    events = joint_ops_manager.get_timeline(operation_id, tenant_id, limit)
    return {"status": "success", "count": len(events), "events": events}


@router.post("/jointops/{operation_id}/timeline")
async def add_timeline_event(
    operation_id: str,
    source_tenant_id: str,
    source_agency_name: str,
    event: TimelineEventCreate,
):
    """Add a timeline event"""
    evt = joint_ops_manager.add_timeline_event(
        operation_id=operation_id,
        event_type=event.event_type,
        source_tenant_id=source_tenant_id,
        source_agency_name=source_agency_name,
        title=event.title,
        description=event.description,
        latitude=event.latitude,
        longitude=event.longitude,
        is_critical=event.is_critical,
    )
    
    if not evt:
        raise HTTPException(status_code=400, detail="Failed to add event")
    
    return {"status": "success", "event_id": evt.event_id}


@router.get("/jointops/metrics")
async def get_jointops_metrics():
    """Get joint operations metrics"""
    metrics = joint_ops_manager.get_metrics()
    return {"status": "success", "metrics": metrics}


@router.post("/analytics/heatmaps")
async def create_heatmap(heatmap: HeatmapCreate):
    """Create a regional heatmap"""
    from datetime import timedelta
    time_range_end = datetime.utcnow()
    time_range_start = time_range_end - timedelta(days=heatmap.time_range_days)
    
    hm = analytics_engine.create_regional_heatmap(
        heatmap_type=heatmap.heatmap_type,
        name=heatmap.name,
        region_codes=heatmap.region_codes,
        tenant_ids=heatmap.tenant_ids,
        time_range_start=time_range_start,
        time_range_end=time_range_end,
        resolution=heatmap.resolution,
        description=heatmap.description,
    )
    
    if not hm:
        raise HTTPException(status_code=400, detail="Failed to create heatmap")
    
    return {"status": "success", "heatmap_id": hm.heatmap_id}


@router.get("/analytics/heatmaps/{heatmap_id}")
async def get_heatmap(heatmap_id: str):
    """Get a heatmap by ID"""
    heatmap = analytics_engine.get_heatmap(heatmap_id)
    if not heatmap:
        raise HTTPException(status_code=404, detail="Heatmap not found")
    return {"status": "success", "heatmap": heatmap}


@router.get("/analytics/heatmaps")
async def list_heatmaps(tenant_id: Optional[str] = None, region_code: Optional[str] = None):
    """List heatmaps"""
    if tenant_id:
        heatmaps = analytics_engine.get_heatmaps_for_tenant(tenant_id)
    elif region_code:
        heatmaps = analytics_engine.get_heatmaps_for_region(region_code)
    else:
        heatmaps = list(analytics_engine._heatmaps.values())
    
    return {"status": "success", "count": len(heatmaps), "heatmaps": heatmaps}


@router.post("/analytics/clusters")
async def create_cluster(cluster: ClusterCreate):
    """Create a regional cluster"""
    cl = analytics_engine.create_cluster(
        cluster_type=cluster.cluster_type,
        name=cluster.name,
        center_lat=cluster.center_lat,
        center_lon=cluster.center_lon,
        radius_km=cluster.radius_km,
        jurisdictions=cluster.jurisdictions,
        tenants=cluster.tenants,
        crime_types=cluster.crime_types,
        description=cluster.description,
    )
    
    if not cl:
        raise HTTPException(status_code=400, detail="Failed to create cluster")
    
    return {"status": "success", "cluster_id": cl.cluster_id}


@router.get("/analytics/clusters/{cluster_id}")
async def get_cluster(cluster_id: str):
    """Get a cluster by ID"""
    cluster = analytics_engine.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"status": "success", "cluster": cluster}


@router.get("/analytics/clusters")
async def list_clusters(
    region_code: Optional[str] = None,
    active_only: bool = False,
    high_risk_only: bool = False,
):
    """List clusters"""
    if active_only:
        clusters = analytics_engine.get_active_clusters()
    elif high_risk_only:
        clusters = analytics_engine.get_high_risk_clusters()
    elif region_code:
        clusters = analytics_engine.get_clusters_for_region(region_code)
    else:
        clusters = list(analytics_engine._clusters.values())
    
    return {"status": "success", "count": len(clusters), "clusters": clusters}


@router.post("/analytics/riskmaps")
async def create_risk_map(riskmap: RiskMapCreate):
    """Create a federated risk map"""
    rm = analytics_engine.create_risk_map(
        name=riskmap.name,
        region_codes=riskmap.region_codes,
        tenant_ids=riskmap.tenant_ids,
        resolution=riskmap.resolution,
        description=riskmap.description,
        valid_hours=riskmap.valid_hours,
    )
    
    if not rm:
        raise HTTPException(status_code=400, detail="Failed to create risk map")
    
    return {"status": "success", "riskmap_id": rm.riskmap_id}


@router.get("/analytics/riskmaps/{riskmap_id}")
async def get_risk_map(riskmap_id: str):
    """Get a risk map by ID"""
    riskmap = analytics_engine.get_risk_map(riskmap_id)
    if not riskmap:
        raise HTTPException(status_code=404, detail="Risk map not found")
    return {"status": "success", "riskmap": riskmap}


@router.get("/analytics/risk")
async def get_risk_at_location(latitude: float, longitude: float, riskmap_id: Optional[str] = None):
    """Get risk level at a location"""
    risk = analytics_engine.get_risk_at_location(latitude, longitude, riskmap_id)
    if not risk:
        return {"status": "success", "risk": None, "message": "No risk data for location"}
    return {"status": "success", "risk": risk}


@router.get("/analytics/trajectories")
async def list_trajectories(min_jurisdictions: int = 2):
    """List cross-jurisdiction trajectories"""
    trajectories = analytics_engine.get_cross_jurisdiction_trajectories(min_jurisdictions)
    return {"status": "success", "count": len(trajectories), "trajectories": trajectories}


@router.get("/analytics/metrics")
async def get_analytics_metrics():
    """Get analytics metrics"""
    metrics = analytics_engine.get_metrics()
    return {"status": "success", "metrics": metrics}


@router.get("/security/audit")
async def get_audit_log(
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    decision: Optional[AccessDecision] = None,
    limit: int = 100,
):
    """Get audit log entries"""
    entries = security_gateway.get_audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        decision=decision,
        limit=limit,
    )
    return {"status": "success", "count": len(entries), "entries": entries}


@router.get("/security/audit/verify")
async def verify_audit_chain():
    """Verify audit chain integrity"""
    valid = security_gateway.verify_audit_chain()
    return {"status": "success", "chain_valid": valid}


@router.get("/security/metrics")
async def get_security_metrics():
    """Get security gateway metrics"""
    metrics = security_gateway.get_metrics()
    return {"status": "success", "metrics": metrics}
