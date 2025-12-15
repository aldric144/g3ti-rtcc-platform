# Phase 37: Master UI Integration & System Orchestration Shell

## Overview

Phase 37 implements the Master UI Integration & System Orchestration Shell for the G3TI RTCC-UIP (Real-Time Crime Center Unified Intelligence Platform). This phase unifies all previous 36 phases into a single cohesive RTCC master interface with global navigation, inter-module synchronization, event aggregation, real-time orchestration, and unified operator workflow.

## Architecture

### Backend Components

#### Master Event Bus (`backend/app/master_orchestration/event_bus.py`)

The Master Event Bus is the central orchestration hub that synchronizes events across all RTCC modules. It supports 25 event types and 30 event sources, providing a unified event stream for the entire platform.

Key features:
- Event publishing with async/sync support
- Subscription management with filtering by event type, source, and priority
- Event acknowledgment tracking
- Event history with configurable retention
- Statistics and monitoring

Event Types:
- ALERT, SYSTEM_MESSAGE, TACTICAL_EVENT
- DRONE_TELEMETRY, ROBOTICS_TELEMETRY
- CAD_UPDATE, INVESTIGATION_LEAD
- GLOBAL_THREAT, CONSTITUTIONAL_ALERT
- HUMAN_STABILITY_ALERT, TRANSPARENCY_FLAG
- OFFICER_SAFETY, MORAL_COMPASS_ALERT
- CITY_BRAIN_UPDATE, GOVERNANCE_UPDATE
- FUSION_CLOUD_UPDATE, AUTONOMOUS_ACTION
- EMERGENCY_MANAGEMENT, CYBER_THREAT
- PREDICTIVE_ALERT, DIGITAL_TWIN_UPDATE
- SENSOR_DATA, MODULE_STATUS
- HEARTBEAT, STATE_SYNC, USER_ACTION

#### Unified Alert Stream (`backend/app/master_orchestration/alert_aggregator.py`)

The Unified Alert Stream aggregates alerts from all 24 RTCC modules into a single, prioritized feed. Each alert includes severity, source, timestamp, geolocation, constitutional compliance tag, moral compass tag, and public safety audit reference.

Key features:
- Alert creation with full metadata
- Severity-based filtering (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Source-based filtering (24 sources)
- Action tracking and resolution
- Alert escalation with level tracking
- Related alert linking
- Automatic expiration cleanup

#### Module Heartbeat Checker (`backend/app/master_orchestration/module_heartbeat.py`)

The Module Heartbeat Checker monitors the health status of all 33 RTCC modules with green/yellow/red indicators. It provides real-time health monitoring, dependency tracking, and system-wide health reporting.

Key features:
- Module registration and health tracking
- Status indicators: HEALTHY, DEGRADED, UNHEALTHY, OFFLINE, UNKNOWN
- Response time monitoring
- CPU and memory usage tracking
- Error and warning counts
- Dependency management
- Heartbeat history

Pre-registered modules include all RTCC systems from Phases 1-36.

#### Cross-Module State Synchronizer (`backend/app/master_orchestration/state_synchronizer.py`)

The Cross-Module State Synchronizer ensures that when one module updates, all related UI components update accordingly. It supports 20 state change types and 22 sync targets.

Key features:
- State change publishing with async/sync support
- Subscription management with target filtering
- Sync rules for automatic propagation
- Acknowledgment tracking
- State change history

State Change Types:
- MAP_UPDATE, ALERT_UPDATE, INVESTIGATION_UPDATE
- TACTICAL_HEATMAP_UPDATE, PREDICTIVE_MODEL_REFRESH
- OPERATOR_HUD_UPDATE, PUBLIC_SAFETY_LOG
- OFFICER_STATUS_UPDATE, DRONE_TELEMETRY_UPDATE
- ROBOT_TELEMETRY_UPDATE, INCIDENT_UPDATE
- RESOURCE_UPDATE, THREAT_UPDATE
- COMPLIANCE_UPDATE, TRUST_SCORE_UPDATE
- CITY_BRAIN_UPDATE, GOVERNANCE_UPDATE
- EMERGENCY_UPDATE, SENSOR_UPDATE
- DIGITAL_TWIN_UPDATE, MODULE_STATUS_UPDATE

#### Global Permissions Manager (`backend/app/master_orchestration/permissions_manager.py`)

The Global Permissions Manager implements RBAC (Role-Based Access Control) for 2,000+ actions across all RTCC modules. It supports 11 roles with granular permission control.

Roles (by access level):
1. super_admin (100) - Full system access
2. admin (90) - Administrative access
3. commander (80) - Command-level access
4. supervisor (70) - Supervisory access
5. analyst (60) - Analysis access
6. investigator (55) - Investigation access
7. officer (50) - Officer-level access
8. dispatcher (45) - Dispatch access
9. operator (40) - Operator access
10. viewer (10) - View-only access
11. public (5) - Public access

Permission Actions:
- VIEW, CREATE, UPDATE, DELETE
- EXECUTE, APPROVE, EXPORT, IMPORT
- CONFIGURE, ADMIN

### REST API Layer (`backend/app/api/master/master_router.py`)

The Master Orchestration REST API provides endpoints for all orchestration operations:

Event Bus Endpoints:
- `GET /api/master/events` - Get recent events with filtering
- `POST /api/master/events` - Create and publish new event
- `GET /api/master/events/{event_id}` - Get specific event
- `POST /api/master/events/{event_id}/acknowledge` - Acknowledge event
- `GET /api/master/events/unacknowledged` - Get unacknowledged events

Alert Stream Endpoints:
- `GET /api/master/alerts` - Get active alerts with filtering
- `POST /api/master/alerts` - Create new alert
- `GET /api/master/alerts/{alert_id}` - Get specific alert
- `POST /api/master/alerts/{alert_id}/action` - Take action on alert
- `POST /api/master/alerts/{alert_id}/resolve` - Resolve alert
- `POST /api/master/alerts/{alert_id}/escalate` - Escalate alert
- `GET /api/master/alerts/unified-feed` - Get unified alert feed

Module Health Endpoints:
- `GET /api/master/modules/health` - Get all module health
- `GET /api/master/modules/{module_id}/health` - Get specific module health
- `POST /api/master/modules/heartbeat` - Update module heartbeat
- `GET /api/master/modules/overview` - Get system overview
- `GET /api/master/modules/unhealthy` - Get unhealthy modules

State Sync Endpoints:
- `GET /api/master/state/changes` - Get recent state changes
- `POST /api/master/state/publish` - Publish state change
- `GET /api/master/state/summary` - Get state summary
- `GET /api/master/state/sync-rules` - Get sync rules

Permissions Endpoints:
- `POST /api/master/permissions/check` - Check permission
- `GET /api/master/permissions/roles` - Get all roles
- `GET /api/master/permissions/user/{user_id}` - Get user permissions
- `POST /api/master/permissions/user/{user_id}/role` - Assign role
- `GET /api/master/permissions/map` - Get permissions map

Dashboard Endpoints:
- `GET /api/master/statistics` - Get master statistics
- `GET /api/master/health` - Health check
- `GET /api/master/dashboard-data` - Get dashboard data

### WebSocket Manager (`backend/app/websockets/master_orchestration_ws.py`)

The Master Orchestration WebSocket Manager provides real-time event streaming across all RTCC modules with 14 channels.

Channels:
- EVENTS - System-wide events from all modules
- ALERTS - Unified alert stream from all sources
- MODULE_STATUS - Module health and status updates
- STATE_SYNC - Cross-module state synchronization
- NOTIFICATIONS - User notifications and messages
- TACTICAL - Tactical analytics updates
- OFFICER_SAFETY - Officer safety alerts and status
- DRONE_TELEMETRY - Drone position and status updates
- ROBOT_TELEMETRY - Robot position and status updates
- INVESTIGATIONS - Investigation case updates
- THREATS - Threat intelligence updates
- EMERGENCY - Emergency management alerts
- COMPLIANCE - Compliance and audit updates
- ALL - All channels combined

Key features:
- Connection management with user tracking
- Channel subscription/unsubscription
- Message broadcasting by channel
- Specialized broadcast methods for each data type
- Message history with channel filtering
- Connection statistics

### Frontend Components

#### Global Navigation Shell

TopNavBar (`frontend/components/navigation/TopNavBar.tsx`):
- Agency logo (RBPD)
- System clock (UTC and Local EST)
- Operator status indicator
- Global alerts bell with count
- AI-powered quick-search bar

LeftSidebar (`frontend/components/navigation/LeftSidebar.tsx`):
- Collapsible sections for all operational modules
- Three sections: Operational Modules, Advanced Systems, Developer/Admin Tools
- Active state highlighting
- Badge support for notifications

MasterLayout (`frontend/components/navigation/MasterLayout.tsx`):
- Unified layout wrapper
- Sidebar toggle functionality
- Responsive design

#### Master Dashboard (`frontend/app/master-dashboard/page.tsx`)

The Master Dashboard provides a unified view of all RTCC operations with 9 core panels:

1. Real-Time Incident Map - Interactive map showing incidents, officers, and drones
2. Unified Alerts Feed - Aggregated alerts from all modules with filtering
3. Officer Safety Status Grid - Officer status overview with visual indicators
4. Tactical Heatmap Overview - Crime density visualization
5. Drone & Robot Activity Snapshot - Fleet status with battery levels
6. Investigations Queue - Active investigations with priority indicators
7. Global Threat Indicators - Threat intelligence summary
8. Human Stability Pulse - Community wellness metrics
9. AI Moral Compass Compliance Score - Ethics and compliance metrics

#### State Management (`frontend/stores/masterStore.ts`)

Zustand store for centralized state management:
- Alerts state with CRUD operations
- Events state with history
- Module health tracking
- Officer status management
- Drone and robot tracking
- Investigation queue
- Threat indicators
- Human stability metrics
- Moral compass scores
- WebSocket connection status

## Integration with Previous Phases

Phase 37 integrates with all previous phases (1-36) through:

1. Event Bus Integration - All modules can publish events to the master event bus
2. Alert Aggregation - Alerts from all modules flow into the unified alert stream
3. Health Monitoring - All modules report health status to the heartbeat checker
4. State Synchronization - State changes propagate across all relevant UI components
5. Permission Enforcement - RBAC applies to all module operations

## Visual Theme

The UI follows the established G3TI RTCC theme:
- Primary: Gold (#c9a227)
- Background: Navy (#0a1628, #0d1f3c)
- Borders: Dark blue (#1e3a5f)
- Text: White (#ffffff), Gray (#94a3b8)
- Status colors: Green (#22c55e), Yellow (#eab308), Orange (#f97316), Red (#ef4444)

## Security Considerations

1. All API endpoints require authentication
2. RBAC enforces permission checks on all operations
3. Sensitive data is filtered based on user role
4. Constitutional compliance is tracked on all alerts
5. Audit trails are maintained for all actions

## Testing

Phase 37 includes 12 test suites:
1. test_event_bus.py - Event bus functionality
2. test_alert_stream.py - Alert aggregation and management
3. test_module_heartbeat.py - Health monitoring
4. test_state_synchronizer.py - State synchronization
5. test_permissions_manager.py - RBAC enforcement
6. test_master_api.py - REST API endpoints
7. test_master_ws.py - WebSocket functionality
8. test_navigation_shell.py - Navigation components
9. test_master_dashboard.py - Dashboard rendering
10. test_ui_sync.py - UI synchronization
11. test_orchestration_integration.py - End-to-end integration
12. test_safety_compliance.py - Safety and compliance checks

## Deployment

The Master UI is accessible at `/master-dashboard` and serves as the primary entry point for RTCC operators. The navigation shell provides access to all 36 previous phase modules through the left sidebar.

## Next Steps (Phase 38)

Phase 38 will implement Total System Synchronization:
- Real-time data synchronization across all modules
- Conflict resolution for concurrent updates
- Offline support with sync-on-reconnect
- Performance optimization for large-scale deployments
