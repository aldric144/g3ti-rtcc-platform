# Phase 16: Multi-City / Multi-Agency Fusion Cloud

## Overview

Phase 16 implements the G3TI Fusion Cloud, a comprehensive multi-tenant infrastructure that enables seamless collaboration between cities, counties, police departments, task forces, and federal agencies. This phase establishes the interoperability backbone for the entire RTCC-UIP platform.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         G3TI FUSION CLOUD                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Multi-Tenant   │  │   Federation    │  │  Shared Intel   │             │
│  │    Manager      │  │     Layer       │  │      Hub        │             │
│  │                 │  │                 │  │                 │             │
│  │ - Tenant Reg.   │  │ - Data Sharing  │  │ - Pursuits      │             │
│  │ - Profiles      │  │ - Permissions   │  │ - BOLOs         │             │
│  │ - Policies      │  │ - Subscriptions │  │ - Patterns      │             │
│  │ - Data Sources  │  │ - Forwarding    │  │ - Alerts        │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Joint Ops     │  │   Federated     │  │  Secure Access  │             │
│  │    Manager      │  │   Analytics     │  │    Gateway      │             │
│  │                 │  │                 │  │                 │             │
│  │ - Op Rooms      │  │ - Heatmaps      │  │ - ABAC          │             │
│  │ - Timelines     │  │ - Clusters      │  │ - Encryption    │             │
│  │ - Whiteboards   │  │ - Trajectories  │  │ - Clearance     │             │
│  │ - Unit Tracking │  │ - Risk Maps     │  │ - Audit         │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Multi-Tenant Model

The Fusion Cloud supports the following tenant types:

| Tenant Type | Description | Example |
|-------------|-------------|---------|
| CITY | Municipal government | City of Metro |
| COUNTY | County government | Metro County |
| STATE | State agency | State Police |
| FEDERAL | Federal agency | FBI, DEA, ATF |
| POLICE_DEPARTMENT | Local police | Metro City PD |
| SHERIFF_OFFICE | County sheriff | County Sheriff |
| TASK_FORCE | Multi-agency task force | Regional Drug TF |
| FUSION_CENTER | Intelligence fusion center | State Fusion Center |
| TRANSIT_AUTHORITY | Transit police | Metro Transit |
| SCHOOL_DISTRICT | School police | Metro Schools |
| UNIVERSITY | Campus police | State University PD |
| PRIVATE_SECURITY | Licensed security | Metro Security Inc |

### Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Tenant A   │     │   Tenant B   │     │   Tenant C   │
│  (Metro PD)  │     │ (County SO)  │     │ (State TF)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│                  FEDERATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Permissions │  │Subscriptions│  │ Forwarding  │     │
│  │   Check     │  │   Match     │  │   Rules     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│                  SHARED INTEL HUB                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Pursuits │ │  BOLOs  │ │Patterns │ │ Alerts  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. MultiTenantManager

Manages tenant lifecycle, profiles, policies, and resource allocation.

**Key Features:**
- Tenant registration and activation
- Profile management (contact info, jurisdiction, ORI numbers)
- Policy enforcement (data retention, user limits, federation rules)
- Data source configuration (CAD, RMS, LPR, ShotSpotter, etc.)
- Integration management (NCIC, N-DEx, eTrace, etc.)
- Federation partnership management
- Resource isolation and allocation

**Tenant Lifecycle:**
```
PENDING → ACTIVE → SUSPENDED → REACTIVATED → ARCHIVED
```

### 2. FederationLayer

Enables secure cross-agency data sharing with classification controls.

**Data Classifications:**
- UNCLASSIFIED
- LAW_ENFORCEMENT_SENSITIVE
- OFFICIAL_USE_ONLY
- CONFIDENTIAL
- SECRET
- TOP_SECRET

**Sensitivity Levels:**
- PUBLIC
- INTERNAL
- RESTRICTED
- HIGHLY_RESTRICTED
- CRITICAL

**Federated Data Types:**
- LPR_HIT
- SHOTSPOTTER_ALERT
- INVESTIGATION
- BOLO
- SUSPECT_PROFILE
- VEHICLE_PROFILE
- INCIDENT
- HEATMAP
- OFFENDER_PROFILE
- PATTERN
- ALERT
- CASE
- INTELLIGENCE

### 3. SharedIntelHub

Real-time intelligence sharing through topic-based channels.

**Channel Types:**
- PURSUITS - Active pursuit coordination
- BOLOS - Be On the Lookout alerts
- PATTERNS - Emerging crime patterns
- HIGH_RISK_SUSPECTS - High-risk individual tracking
- REGIONAL_ALERTS - Multi-jurisdiction alerts
- OFFICER_SAFETY - Officer safety bulletins
- MISSING_PERSONS - Missing person alerts
- AMBER_ALERTS - Child abduction alerts
- SILVER_ALERTS - Missing elderly alerts
- CRITICAL_INCIDENTS - Critical incident notifications
- GANG_ACTIVITY - Gang intelligence
- NARCOTICS - Drug-related intelligence
- HUMAN_TRAFFICKING - Trafficking intelligence
- TERRORISM - Terrorism-related alerts
- CYBER_THREATS - Cyber threat intelligence

**Message Priorities:**
- LOW
- NORMAL
- HIGH
- URGENT
- CRITICAL
- FLASH

### 4. JointOpsManager

Coordinates multi-agency operations with shared resources.

**Operation Types:**
- PURSUIT
- INVESTIGATION
- SURVEILLANCE
- RAID
- SEARCH
- RESCUE
- DISASTER_RESPONSE
- CROWD_CONTROL
- VIP_PROTECTION
- TASK_FORCE
- TRAINING
- SPECIAL_EVENT
- FUGITIVE_APPREHENSION
- NARCOTICS
- HUMAN_TRAFFICKING
- CYBER
- TERRORISM

**Operation Roles:**
- COMMANDER
- DEPUTY_COMMANDER
- OPERATIONS_CHIEF
- PLANNING_CHIEF
- LOGISTICS_CHIEF
- INTELLIGENCE_OFFICER
- COMMUNICATIONS_OFFICER
- SAFETY_OFFICER
- PUBLIC_INFORMATION
- LIAISON_OFFICER
- TEAM_LEADER
- UNIT_MEMBER
- OBSERVER
- ANALYST
- DISPATCHER

**Features:**
- Operation rooms with real-time collaboration
- Shared timelines with event tracking
- Interactive whiteboards
- Unit deployment and tracking
- Objective management
- Role-based access per jurisdiction

### 5. FederatedAnalyticsEngine

Multi-city crime analysis and predictive modeling.

**Heatmap Types:**
- CRIME - General crime distribution
- VIOLENCE - Violent crime hotspots
- PROPERTY_CRIME - Property crime patterns
- DRUG_ACTIVITY - Drug-related activity
- GANG_ACTIVITY - Gang territory mapping
- TRAFFIC_INCIDENTS - Traffic-related incidents
- CALLS_FOR_SERVICE - CFS density
- ARRESTS - Arrest locations
- SHOTS_FIRED - Gunfire detection
- DOMESTIC_VIOLENCE - DV incident patterns

**Cluster Types:**
- EMERGING - New/growing clusters
- ACTIVE - Currently active clusters
- DECLINING - Decreasing activity
- DORMANT - Inactive clusters
- SEASONAL - Time-based patterns
- PERSISTENT - Long-term hotspots

**Risk Levels:**
- MINIMAL
- LOW
- MODERATE
- HIGH
- CRITICAL

**Features:**
- Regional heatmaps with H3 hexagonal indexing
- Cross-city offender trajectory tracking
- Crime cluster identification and monitoring
- Real-time risk overlay maps
- Federated analytics queries

### 6. SecureAccessGateway

CJIS-compliant security with attribute-based access control.

**Access Control Features:**
- Attribute-Based Access Control (ABAC)
- Role-based permissions
- Jurisdiction-based filtering
- Clearance level enforcement
- Per-tenant encryption
- Domain separation
- Data redaction for unauthorized users
- Comprehensive audit logging

**Access Decisions:**
- ALLOW
- DENY
- ALLOW_PARTIAL (with redaction)
- REQUIRE_APPROVAL
- ESCALATE

## API Endpoints

### Tenant Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/fusion/tenants | Register new tenant |
| GET | /api/fusion/tenants | List all tenants |
| GET | /api/fusion/tenants/{id} | Get tenant details |
| PUT | /api/fusion/tenants/{id}/activate | Activate tenant |
| PUT | /api/fusion/tenants/{id}/suspend | Suspend tenant |
| POST | /api/fusion/tenants/{id}/data-sources | Add data source |
| GET | /api/fusion/tenants/{id}/data-sources | List data sources |
| POST | /api/fusion/tenants/{id}/integrations | Add integration |
| GET | /api/fusion/tenants/{id}/integrations | List integrations |
| POST | /api/fusion/tenants/{id}/federation-partners/{partner_id} | Add federation partner |
| GET | /api/fusion/tenants/metrics | Get tenant metrics |

### Federation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/fusion/federation/publish | Publish federated data |
| GET | /api/fusion/federation/data/{id} | Get federated data |
| GET | /api/fusion/federation/data | Get data for tenant |
| POST | /api/fusion/federation/share/{id} | Share data with tenant |
| POST | /api/fusion/federation/permissions | Create permission |
| GET | /api/fusion/federation/permissions/{tenant_id} | Get permissions |
| POST | /api/fusion/federation/subscriptions | Create subscription |
| PUT | /api/fusion/federation/subscriptions/{id}/activate | Activate subscription |
| GET | /api/fusion/federation/subscriptions/{tenant_id} | Get subscriptions |
| GET | /api/fusion/federation/metrics | Get federation metrics |

### Intelligence Hub

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/fusion/intel/channels | List channels |
| GET | /api/fusion/intel/channels/{id} | Get channel |
| POST | /api/fusion/intel/channels/{id}/subscribe | Subscribe to channel |
| POST | /api/fusion/intel/messages | Publish message |
| GET | /api/fusion/intel/messages/{channel_id} | Get channel messages |
| PUT | /api/fusion/intel/messages/{id}/acknowledge | Acknowledge message |
| GET | /api/fusion/intel/metrics | Get hub metrics |

### Joint Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/fusion/jointops | Create operation |
| GET | /api/fusion/jointops | List operations |
| GET | /api/fusion/jointops/{id} | Get operation |
| PUT | /api/fusion/jointops/{id}/start | Start operation |
| PUT | /api/fusion/jointops/{id}/pause | Pause operation |
| PUT | /api/fusion/jointops/{id}/resume | Resume operation |
| PUT | /api/fusion/jointops/{id}/complete | Complete operation |
| POST | /api/fusion/jointops/{id}/agencies | Add agency |
| DELETE | /api/fusion/jointops/{id}/agencies/{tenant_id} | Remove agency |
| PUT | /api/fusion/jointops/{id}/agencies/{tenant_id}/role | Assign role |
| POST | /api/fusion/jointops/{id}/units | Deploy unit |
| PUT | /api/fusion/jointops/{id}/units/{unit_id}/position | Update position |
| POST | /api/fusion/jointops/{id}/objectives | Add objective |
| PUT | /api/fusion/jointops/{id}/objectives/{obj_id}/complete | Complete objective |
| GET | /api/fusion/jointops/{id}/timeline | Get timeline |
| POST | /api/fusion/jointops/{id}/timeline | Add timeline event |
| GET | /api/fusion/jointops/metrics | Get metrics |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/fusion/analytics/heatmaps | Create heatmap |
| GET | /api/fusion/analytics/heatmaps/{id} | Get heatmap |
| GET | /api/fusion/analytics/heatmaps | List heatmaps |
| POST | /api/fusion/analytics/clusters | Create cluster |
| GET | /api/fusion/analytics/clusters/{id} | Get cluster |
| GET | /api/fusion/analytics/clusters | List clusters |
| POST | /api/fusion/analytics/riskmaps | Create risk map |
| GET | /api/fusion/analytics/riskmaps/{id} | Get risk map |
| GET | /api/fusion/analytics/risk | Get risk at location |
| GET | /api/fusion/analytics/trajectories | List trajectories |
| GET | /api/fusion/analytics/metrics | Get analytics metrics |

### Security

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/fusion/security/audit | Get audit log |
| GET | /api/fusion/security/audit/verify | Verify audit chain |
| GET | /api/fusion/security/metrics | Get security metrics |

## WebSocket Channels

| Channel | Description |
|---------|-------------|
| /ws/fusion/tenants | Tenant lifecycle events |
| /ws/fusion/intel/{channel_id} | Intelligence channel messages |
| /ws/fusion/jointops/{room_id} | Joint operations room updates |
| /ws/fusion/analytics | Analytics updates and alerts |

### WebSocket Event Types

**Tenant Events:**
- tenant_registered
- tenant_activated
- tenant_suspended
- tenant_updated
- federation_partner_added

**Intel Events:**
- new_message
- message_updated
- message_acknowledged
- message_cancelled
- message_resolved

**Joint Ops Events:**
- operation_created
- operation_started
- operation_paused
- operation_completed
- agency_joined
- agency_left
- unit_deployed
- unit_position_update
- objective_completed
- timeline_event
- whiteboard_update
- chat_message

**Analytics Events:**
- heatmap_updated
- cluster_detected
- cluster_updated
- trajectory_updated
- risk_level_changed

## Security Model

### CJIS Compliance

The Fusion Cloud implements CJIS Security Policy requirements:

1. **Access Control** - Role and attribute-based access
2. **Identification & Authentication** - Multi-factor authentication support
3. **Audit & Accountability** - Comprehensive audit logging with chain verification
4. **Configuration Management** - Tenant-isolated configurations
5. **Media Protection** - Encrypted data at rest and in transit
6. **Physical Protection** - Tenant resource isolation
7. **System & Communications Protection** - Domain separation
8. **System & Information Integrity** - Data classification enforcement

### Access Control Rules

```python
# Example ABAC Policy
{
    "effect": "allow",
    "resource": "federated_data",
    "action": "read",
    "conditions": {
        "user.clearance_level": {"gte": "data.required_clearance"},
        "user.jurisdiction": {"in": "data.jurisdiction_codes"},
        "user.tenant_id": {"in": "data.shared_with_tenants"}
    }
}
```

### Audit Logging

All access requests are logged with:
- Timestamp
- User ID
- Tenant ID
- Resource accessed
- Action performed
- Access decision
- IP address
- User agent
- Chain hash for integrity verification

## Deployment

### Docker Services

```yaml
# Fusion Cloud Gateway
fusion-cloud:
  profiles:
    - fusion
  environment:
    - FUSION_TENANT_ISOLATION=true
    - FUSION_FEDERATION_ENABLED=true
    - FUSION_CROSS_AGENCY_SHARING=true
    - FUSION_CJIS_COMPLIANCE=true
    - FUSION_ENCRYPTION_ENABLED=true
    - FUSION_ABAC_ENABLED=true

# Fusion Analytics Processor
fusion-analytics:
  profiles:
    - fusion
  environment:
    - FUSION_HEATMAP_RESOLUTION=8
    - FUSION_CLUSTER_UPDATE_INTERVAL=300
    - FUSION_TRAJECTORY_ANALYSIS=true
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FUSION_TENANT_ISOLATION | Enable tenant isolation | true |
| FUSION_FEDERATION_ENABLED | Enable federation layer | true |
| FUSION_CROSS_AGENCY_SHARING | Enable cross-agency sharing | true |
| FUSION_CJIS_COMPLIANCE | Enable CJIS compliance mode | true |
| FUSION_ENCRYPTION_ENABLED | Enable per-tenant encryption | true |
| FUSION_ABAC_ENABLED | Enable ABAC | true |
| FUSION_HEATMAP_RESOLUTION | H3 resolution for heatmaps | 8 |
| FUSION_CLUSTER_UPDATE_INTERVAL | Cluster update interval (seconds) | 300 |
| FUSION_TRAJECTORY_ANALYSIS | Enable trajectory analysis | true |

## Frontend Pages

### /fusion-cloud

Main Fusion Cloud dashboard with tabs:

1. **Tenant Manager** - Manage tenants, data sources, integrations
2. **Shared Intelligence Hub** - Real-time intelligence channels
3. **Joint Operations Room** - Multi-agency operation coordination
4. **Regional Analytics** - Heatmaps, clusters, trajectories
5. **Inter-Agency Alerts** - Cross-jurisdiction alert management

### Components

- TenantCard - Tenant information display
- IntelChannelFeed - Intelligence message feed
- CrossAgencyBoloBoard - BOLO management
- JointOpsTimeline - Operation timeline view
- TrajectoryMap - Offender trajectory visualization
- RegionalHeatmap - Multi-city heatmap display
- ClearanceFilterBar - Access level filtering

## Examples

### Register a Tenant

```python
tenant = tenant_manager.register_tenant(
    name="Metro City Police Department",
    tenant_type=TenantType.POLICE_DEPARTMENT,
    profile=TenantProfile(
        display_name="Metro City PD",
        city="Metro City",
        state="CA",
        ori_number="CA0123456"
    ),
    policy=TenantPolicy(
        name="Standard PD Policy",
        data_retention_days=365,
        federation_enabled=True,
        mfa_required=True
    )
)
```

### Publish Federated Data

```python
data = federation_layer.publish_data(
    source_tenant_id="tenant-001",
    source_agency_name="Metro City PD",
    data_type=FederatedDataType.LPR_HIT,
    title="Hot Vehicle Hit - Armed Robbery Suspect",
    payload={
        "plate": "ABC123",
        "vehicle": "Black BMW X5",
        "alert_type": "armed_robbery"
    },
    classification=DataClassification.LAW_ENFORCEMENT_SENSITIVE,
    share_with_tenants=["tenant-002", "tenant-003"]
)
```

### Create Joint Operation

```python
operation = joint_ops_manager.create_operation(
    name="Operation Thunder Strike",
    operation_type=OperationType.RAID,
    lead_tenant_id="tenant-001",
    lead_agency_name="Metro City PD",
    commander_name="Captain Johnson",
    jurisdiction_codes=["CA-METRO", "CA-COUNTY"]
)

# Add participating agency
joint_ops_manager.add_agency(
    operation_id=operation.operation_id,
    tenant_id="tenant-002",
    agency_name="County Sheriff",
    role=OperationRole.TEAM_LEADER
)

# Deploy unit
joint_ops_manager.deploy_unit(
    operation_id=operation.operation_id,
    tenant_id="tenant-001",
    agency_name="Metro City PD",
    call_sign="SWAT-1",
    unit_type="swat",
    latitude=34.0522,
    longitude=-118.2437
)
```

### Create Regional Heatmap

```python
heatmap = analytics_engine.create_regional_heatmap(
    heatmap_type=HeatmapType.CRIME,
    name="Regional Crime Heatmap",
    region_codes=["CA-METRO", "CA-COUNTY", "CA-EAST"],
    tenant_ids=["tenant-001", "tenant-002", "tenant-003"],
    time_range_start=datetime.utcnow() - timedelta(days=30),
    time_range_end=datetime.utcnow(),
    resolution=8
)
```

## Backward Compatibility

Phase 16 is fully backward compatible with Phases 1-15:

- All existing APIs remain unchanged
- New fusion cloud endpoints are additive
- Existing data models are preserved
- No breaking changes to WebSocket channels
- Frontend routes are new additions

## Testing

Test suites cover:

1. Tenant creation and lifecycle
2. Federation layer permissions
3. Intel hub publishing and subscriptions
4. Joint ops room management
5. Federated heatmap generation
6. Access control enforcement
7. WebSocket event isolation
8. Audit log integrity

Run tests with:
```bash
pytest tests/phase16/ -v
```
