# Phase 24: AI City Autonomy - Level-2 Autonomous City Operations

## Overview

Phase 24 implements Level-2 Autonomous City Operations for the G3TI RTCC-UIP platform, enabling the AI system to independently detect issues, propose solutions, execute low-risk actions, and prepare high-risk actions for operator approval. This phase builds upon the AI City Brain (Phase 22) and City Governance (Phase 23) to create a comprehensive autonomous operations layer for Riviera Beach, Florida.

## Architecture

### Core Components

The AI City Autonomy system consists of four primary engines:

**AutonomousActionEngine** (`backend/app/city_autonomy/__init__.py`)
- Interprets recommendations from Phases 22 & 23
- Categorizes actions into three levels:
  - Level 0: Read-only observation actions
  - Level 1: Automated low-risk actions (auto-executed)
  - Level 2: Human-confirmed medium/high-risk actions
- Maintains full explainability with decision trees, model weights, and risk scores
- Implements circuit-breaker pattern for failure handling

**PolicyEngine** (`backend/app/city_autonomy/policy_engine.py`)
- Manages city operation rules and emergency thresholds
- Supports policy hierarchy: Global → City → Department → Scenario
- Handles traffic, patrol, EMS, fire, utility, and emergency policies
- Provides policy versioning, testing sandbox, and conflict resolution
- Includes emergency overrides for hurricanes, flooding, mass casualty events, power outages, and city-wide alerts

**AutomatedCityStabilizer** (`backend/app/city_autonomy/stabilizer.py`)
- Monitors 8 domains: grid load, traffic, crime, EMS/Fire demand, weather, flooding, crowd movement
- Detects anomalies with severity classification
- Predicts cascade failures with failure sequence analysis
- Generates domain-specific stabilization actions
- Implements circuit-breaker for system protection

**ActionAuditEngine** (`backend/app/city_autonomy/audit_engine.py`)
- Maintains tamper-proof logs with blockchain-style chaining
- Tracks all autonomous actions, human overrides, denials, and escalations
- Supports CJIS, NIST, and FL State Statute compliance
- Generates PDF reports: incident-level, 24h/7d/30d summaries
- Provides chain of custody management with sealing capability

### Action Categories

| Category | Description | Default Level |
|----------|-------------|---------------|
| Traffic Control | Signal timing, rerouting | Level 1 |
| Patrol Deployment | Unit positioning, rebalancing | Level 2 |
| Resource Allocation | Equipment, personnel assignment | Level 1-2 |
| Notification | Alerts, warnings | Level 1 |
| Emergency Response | Crisis actions | Level 2 |
| Utility Management | Grid, water control | Level 1-2 |
| Crowd Management | Event control | Level 2 |
| Evacuation | Route activation, shelter coordination | Level 2 |
| Infrastructure | Maintenance, repairs | Level 1-2 |
| Observation | Monitoring, data collection | Level 0 |

### Risk Scoring

Actions are scored on a 0-1 scale based on:
- Action type risk weight
- Parameter sensitivity
- Domain criticality
- Time sensitivity
- Reversibility

Risk levels:
- Minimal (0-0.2): Auto-execute eligible
- Low (0.2-0.4): Auto-execute with logging
- Medium (0.4-0.6): Requires approval
- High (0.6-0.8): Requires senior approval
- Critical (0.8-1.0): Requires command approval

## Policy Enforcement

### Policy Hierarchy

Policies are evaluated in order of precedence:
1. **Global Policies**: Apply to all operations
2. **City Policies**: Riviera Beach-specific rules
3. **Department Policies**: Police, Fire, EMS, Public Works
4. **Scenario Policies**: Event-specific overrides

### Emergency Overrides

Pre-configured emergency overrides for Riviera Beach:

| Override | Trigger | Actions |
|----------|---------|---------|
| Hurricane | NWS Hurricane Warning | Activate evacuation routes, suspend non-essential operations |
| Flooding | Water level > 2.0 ft | Close flood zones, reroute traffic, alert residents |
| Mass Casualty | MCI declaration | Surge EMS resources, activate mutual aid |
| Power Outage | Grid failure > 30% | Activate backup systems, prioritize critical facilities |
| City-Wide Alert | Command activation | Full emergency protocols |

### Conflict Resolution

When policies conflict, resolution follows:
1. Higher scope wins (Global > City > Department > Scenario)
2. Higher priority wins within same scope
3. More specific condition wins for equal priority
4. Manual resolution required for unresolvable conflicts

## Safety Mechanisms

### Circuit Breaker Pattern

Both AutonomousActionEngine and AutomatedCityStabilizer implement circuit breakers:
- Opens after 5 consecutive failures
- Auto-switches system to manual mode
- Requires explicit reset to resume autonomous operations
- All actions during open state require manual approval

### Fail-Safe Design

- All Level 2 actions require human approval
- Emergency overrides can only be activated by authorized personnel
- Audit trail cannot be modified after creation
- Chain of custody can be sealed to prevent tampering
- System defaults to manual mode on any critical failure

### Override Mechanisms

Operators can:
- Pause all autonomous actions
- Emergency stop all operations
- Override any pending action
- Activate/deactivate emergency overrides
- Reset circuit breakers
- Switch between autonomous and manual modes

## Audit & Compliance

### Compliance Standards

The system supports:
- **CJIS**: Criminal Justice Information Services security policy
- **NIST**: National Institute of Standards and Technology guidelines
- **FL State**: Florida State Statutes for public records and emergency management
- **HIPAA**: Health Insurance Portability and Accountability Act (for EMS data)

### Audit Trail

Every action generates audit entries with:
- Unique entry ID
- Event type and severity
- Timestamp with millisecond precision
- Actor identification (human/AI/system)
- Resource affected
- Full description and details
- Previous and new state
- Compliance tags
- Digital signature
- Chain hash for integrity verification

### Chain of Custody

Resources requiring legal chain of custody:
- Investigation evidence
- Arrest records
- Emergency response actions
- Policy changes
- Override activations

Chains can be sealed to prevent further modifications while maintaining full audit history.

## API Endpoints

### Autonomous Actions
- `POST /api/autonomy/action/execute` - Execute an action
- `GET /api/autonomy/action/pending` - Get pending actions
- `POST /api/autonomy/action/approve/{id}` - Approve action
- `POST /api/autonomy/action/deny/{id}` - Deny action
- `POST /api/autonomy/action/escalate/{id}` - Escalate action
- `GET /api/autonomy/action/history` - Get action history
- `GET /api/autonomy/action/{id}` - Get specific action

### Policy Engine
- `GET /api/autonomy/policy` - List policies
- `GET /api/autonomy/policy/{id}` - Get policy
- `POST /api/autonomy/policy` - Create policy
- `PUT /api/autonomy/policy/{id}` - Update policy
- `POST /api/autonomy/policy/simulate` - Simulate policy
- `POST /api/autonomy/policy/{id}/activate` - Activate policy
- `POST /api/autonomy/policy/{id}/deactivate` - Deactivate policy
- `GET /api/autonomy/policy/emergency-overrides` - Get overrides
- `POST /api/autonomy/policy/emergency-override/activate` - Activate override

### Stabilizer
- `GET /api/autonomy/stabilizer/status` - Get status
- `POST /api/autonomy/stabilizer/run` - Run stabilization cycle
- `GET /api/autonomy/stabilizer/anomalies` - Get active anomalies
- `GET /api/autonomy/stabilizer/cascade-predictions` - Get predictions
- `GET /api/autonomy/stabilizer/actions` - Get stabilization actions
- `POST /api/autonomy/stabilizer/sensor-reading` - Ingest sensor data
- `POST /api/autonomy/stabilizer/anomaly/{id}/resolve` - Resolve anomaly
- `POST /api/autonomy/stabilizer/circuit-breaker/reset` - Reset breaker

### Audit
- `GET /api/autonomy/audit` - Query audit entries
- `GET /api/autonomy/audit/{id}` - Get audit entry
- `GET /api/autonomy/audit/action/{id}` - Get entries by action
- `GET /api/autonomy/audit/chain-of-custody/{type}/{id}` - Get chain
- `POST /api/autonomy/audit/chain-of-custody/{type}/{id}/seal` - Seal chain
- `GET /api/autonomy/audit/verify-chain` - Verify integrity
- `POST /api/autonomy/audit/report/compliance` - Generate report
- `GET /api/autonomy/audit/summary/{period}` - Get summary
- `GET /api/autonomy/audit/incident-report/{id}` - Get incident report

### System Control
- `GET /api/autonomy/statistics` - Get all statistics
- `POST /api/autonomy/circuit-breaker/reset` - Reset all breakers
- `POST /api/autonomy/mode/manual` - Switch to manual mode
- `POST /api/autonomy/mode/autonomous` - Switch to autonomous mode

## WebSocket Channels

### /ws/autonomy/actions
Real-time action notifications:
- `action_created` - New action created
- `action_approved` - Action approved
- `action_denied` - Action denied
- `action_executed` - Action executed
- `action_completed` - Action completed
- `action_failed` - Action failed

### /ws/autonomy/approvals
Approval workflow updates:
- `approval_requested` - New approval needed
- `approval_reminder` - Reminder for pending approval
- `approval_timeout_warning` - Timeout approaching
- `approval_expired` - Approval expired

### /ws/autonomy/stabilizer
Anomaly and stabilization updates:
- `anomaly_detected` - New anomaly detected
- `anomaly_resolved` - Anomaly resolved
- `cascade_prediction` - Cascade failure predicted
- `stabilization_started` - Stabilization action started
- `stabilization_progress` - Progress update
- `stabilization_completed` - Stabilization completed
- `circuit_breaker_triggered` - Circuit breaker opened
- `circuit_breaker_reset` - Circuit breaker reset

### /ws/autonomy/audit
Audit trail updates:
- `audit_entry_created` - New audit entry
- `chain_sealed` - Chain of custody sealed
- `compliance_alert` - Compliance issue detected
- `integrity_warning` - Chain integrity warning

## Frontend Pages

### Autonomy Command Console (`/ai-city-autonomy`)
- Pending Actions Queue with approve/deny buttons
- Action Explainability Drawer showing decision tree and model weights
- Risk Score Indicator with visual representation
- Recent Actions feed
- Audit Trail pane
- Action Statistics summary

### Policy Engine Manager
- Policy List with status and scope indicators
- Policy Editor with rule and threshold configuration
- Simulation Sandbox for testing policies
- Conflict Detector with resolution suggestions
- Emergency Override controls
- Policy Hierarchy visualization

### City Stabilization Dashboard
- Active Anomalies map with severity indicators
- Cascade Failure Predictions with recommended actions
- Stabilization Actions feed with approval controls
- Domain Status overview
- Manual Override Control panel
- Circuit Breaker status and reset

### Autonomy Audit Center
- Full Audit Trail with filtering
- Chain of Custody records
- Compliance Reports generation
- Decision Distribution statistics
- Override Statistics
- Downloadable reports (PDF/CSV)

## Riviera Beach Configuration

### City Profile
- Population: 37,964
- Area: 9.76 square miles
- Coordinates: 26.7753°N, 80.0583°W
- ZIP Code: 33404

### Districts
- Downtown
- Marina District
- Singer Island
- Riviera Beach Heights
- Industrial Area

### Critical Infrastructure
- Port of Palm Beach
- FPL Riviera Beach Plant
- Riviera Beach Marina
- Blue Heron Bridge
- City Hall Complex

### Flood Zones
- Coastal Zone A (Singer Island)
- Flood Zone AE (Marina District)
- Flood Zone X (Downtown)

### Hurricane Zones
- Evacuation Zone A (Singer Island, Marina)
- Evacuation Zone B (Coastal areas)
- Evacuation Zone C (Inland areas)

## Integration with Previous Phases

### Phase 22 (AI City Brain)
- Receives city state updates and predictions
- Processes recommendations from CityPredictionEngine
- Coordinates with CityBrainCore for event handling

### Phase 23 (City Governance)
- Receives governance decisions and resource optimization recommendations
- Integrates with GovernanceDecisionEngine for policy-based actions
- Coordinates with ResourceOptimizer for allocation actions

## Testing

Phase 24 includes 10 test suites:
1. `test_autonomous_action_engine.py` - Action interpretation and execution
2. `test_policy_engine.py` - Policy management and enforcement
3. `test_stabilizer.py` - Anomaly detection and stabilization
4. `test_risk_scoring.py` - Risk calculation accuracy
5. `test_explainability.py` - Decision explainability validation
6. `test_approval_workflow.py` - Approval process testing
7. `test_autonomy_override.py` - Override mechanism testing
8. `test_audit_chain.py` - Audit integrity verification
9. `test_autonomy_api.py` - API endpoint testing
10. `test_autonomy_ui.py` - UI integration testing

## Deployment

### Docker Services
- `autonomy-engine`: Main autonomy processing service
- Healthcheck endpoint: `/health/autonomy`
- Circuit breaker monitoring

### Environment Variables
- `AUTONOMY_AUTO_EXECUTE`: Enable/disable auto-execution (default: true)
- `AUTONOMY_CIRCUIT_BREAKER_THRESHOLD`: Failure threshold (default: 5)
- `AUTONOMY_APPROVAL_TIMEOUT_MINUTES`: Approval timeout (default: 30)
- `AUTONOMY_AUDIT_SIGNING_KEY`: Key for audit signatures

### Monitoring
- Autonomy logs route to RTCC audit log aggregator
- Circuit breaker status exposed via metrics endpoint
- Action execution latency tracking
- Approval queue depth monitoring

## Security Considerations

- All API endpoints require authentication
- Role-based access control (RBAC) for actions
- Audit logging for all operations
- Encrypted communication for WebSocket channels
- Tamper-proof audit chain with digital signatures
- Emergency override requires elevated privileges

## Future Enhancements

- Machine learning model for risk scoring optimization
- Predictive action recommendation
- Multi-city federation support
- Advanced cascade failure modeling
- Natural language policy definition
- Mobile app for operator approvals
