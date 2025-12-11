# Phase 23: AI City Governance & Resource Optimization Engine

## Overview

Phase 23 implements the AI City Governance & Resource Optimization Engine for the G3TI RTCC-UIP platform. This module transforms Riviera Beach's Real-Time Crime Center into a full city operations co-pilot, capable of providing predictive recommendations, resource optimization, and operational decision-support for all city departments.

## Architecture

### Core Components

The City Governance Engine consists of four primary subsystems:

1. **GovernanceDecisionEngine** - Decision recommendation system with weighted rules and ML policy models
2. **ResourceOptimizer** - Multi-algorithm resource allocation and optimization
3. **CityScenarioSimulator** - What-if scenario modeling and outcome prediction
4. **GovernanceKPIEngine** - Performance metrics and reporting system

### Data Flow

```
City Brain (Phase 22) → Data Ingestion → Decision Engine → Recommendations
                                              ↓
                                    Resource Optimizer → Allocations
                                              ↓
                                    Scenario Simulator → Predictions
                                              ↓
                                       KPI Engine → Reports
```

## Module Details

### 1. GovernanceDecisionEngine

The decision engine processes real-time city data and generates actionable recommendations across multiple domains.

**Decision Domains:**
- Public Safety - Crime prevention, patrol deployment, incident response
- Traffic & Mobility - Congestion management, signal timing, rerouting
- Utilities - Power grid, water system, infrastructure management
- Public Works - Maintenance scheduling, road repairs, facility management
- Storm/Hurricane Response - Emergency preparation, evacuation, resource staging
- City Events & Crowd Management - Event planning, crowd control, traffic management

**Features:**
- Weighted rules engine with 8 default decision rules
- ML policy models for patrol, traffic, resource allocation, and emergency response
- Confidence scoring (high, medium, low, uncertain)
- Explainability layer with detailed reasoning for each recommendation
- Decision lifecycle management (pending → approved/rejected → implemented)
- CJIS-aligned audit logging

**Default Rules:**
- `high_crime_patrol` - Increase patrol in high-crime areas
- `traffic_congestion_reroute` - Activate traffic rerouting during congestion
- `storm_preparation` - Pre-position resources before storms
- `utility_failure_response` - Rapid response to utility outages
- `crowd_surge_management` - Manage crowd density at events
- `ems_coverage_gap` - Address EMS coverage gaps
- `fire_risk_prevention` - Respond to elevated fire risk
- `public_works_maintenance` - Schedule preventive maintenance

### 2. ResourceOptimizer

The resource optimizer uses multiple algorithms to optimize resource allocation across the city.

**Optimization Algorithms:**
- Linear Programming - Constraint-based optimization
- Multi-Objective Optimization - Pareto frontier analysis
- Route Optimization - Nearest neighbor with priority weighting
- Load Balancing - Workload distribution across zones
- Cost-Reward Scoring - Economic impact analysis

**Resource Types:**
- Police Units
- Fire Units
- EMS Units
- Traffic Control
- Public Works Crews
- Utility Crews

**Optimization Objectives:**
- Maximize Coverage - Ensure all zones have adequate coverage
- Minimize Response Time - Reduce average response times
- Balance Workload - Distribute work evenly across units
- Minimize Cost - Optimize resource utilization costs

**Default Zones (Riviera Beach):**
- Downtown/Marina District
- Singer Island
- Westside
- Marina
- Industrial/Port
- North Riviera Beach

### 3. CityScenarioSimulator

The scenario simulator models "what-if" scenarios and predicts potential outcomes.

**Scenario Types:**
- Road Closure - Traffic impact analysis
- Weather Event - Storm, rain, wind effects
- Major Incident - Crime, accident, emergency response
- Multi-Day Operation - Extended operations planning
- Infrastructure Outage - Power, water, communications failures
- Crowd Surge - Event crowd management
- Crime Displacement - Crime pattern shifts
- Hurricane - Category 1-5 hurricane impact
- Flooding - Flood zone impact analysis
- Heatwave - Extreme heat response
- Mass Casualty - Multi-casualty incident response
- Civil Unrest - Public safety response
- Special Event - Planned event management

**Features:**
- Three outcome paths: Best Case, Most Likely, Worst Case
- Timeline event generation with impact scoring
- Impact assessment across 8 categories
- Pre-built scenario templates
- Variable adjustment for scenario customization
- Resource requirement estimation
- Cost calculation

**Pre-built Templates:**
- Category 3 Hurricane
- Major Public Event (15,000+ attendees)
- Major Power Outage (5,000+ customers)
- Major Road Closure

### 4. GovernanceKPIEngine

The KPI engine generates performance dashboards and reports for city operations.

**KPI Categories:**
- Response Time - Police, Fire, EMS response metrics
- Patrol Efficiency - Zone coverage, calls per unit, proactive time
- Traffic - Congestion score, incidents, signal efficiency
- Utility Uptime - Power, water, communications availability
- Fire/EMS Readiness - Unit availability, equipment, training
- Budget - Spending, variance, overtime
- City Health - Overall city performance index

**Report Types:**
- Daily Reports
- Weekly Reports
- Monthly Reports
- Quarterly Reports
- Yearly Reports

**Key Metrics:**
- City Health Index (0-100 with letter grade)
- Department Scores (Police, Fire, EMS, Public Works)
- Budget Utilization and Variance
- Overtime Hours and Cost
- Response Time Trends
- Coverage Metrics

## API Endpoints

### Decision Endpoints
- `POST /api/governance/decisions` - Process city data and generate decisions
- `GET /api/governance/recommendations` - Get pending recommendations
- `GET /api/governance/decisions/{id}` - Get specific decision
- `POST /api/governance/decisions/{id}/approve` - Approve a decision
- `POST /api/governance/decisions/{id}/reject` - Reject a decision
- `POST /api/governance/decisions/{id}/implement` - Mark as implemented

### Resource Optimization Endpoints
- `GET /api/governance/resource-optimization` - Get optimization status
- `POST /api/governance/resource-optimization/run` - Run optimization
- `POST /api/governance/resource-optimization/patrol` - Optimize patrol coverage
- `POST /api/governance/resource-optimization/fire-ems` - Optimize fire/EMS
- `POST /api/governance/resource-optimization/traffic` - Optimize traffic
- `POST /api/governance/resource-optimization/route` - Get optimized route
- `GET /api/governance/resource-optimization/vehicles` - Vehicle allocation
- `POST /api/governance/resource-optimization/maintenance` - Schedule maintenance

### Scenario Endpoints
- `GET /api/governance/scenario/templates` - Get scenario templates
- `POST /api/governance/scenario/create` - Create new scenario
- `POST /api/governance/scenario/from-template` - Create from template
- `POST /api/governance/scenario/run` - Run simulation
- `GET /api/governance/scenario/{id}` - Get scenario details
- `GET /api/governance/scenario/result/{id}` - Get simulation result
- `PUT /api/governance/scenario/{id}/variable` - Update variable
- `DELETE /api/governance/scenario/{id}` - Delete scenario
- `GET /api/governance/scenario` - List all scenarios

### KPI Endpoints
- `GET /api/governance/kpi` - Get all KPIs
- `GET /api/governance/kpi/city-health` - Get city health index
- `GET /api/governance/kpi/departments` - Get department scores
- `GET /api/governance/kpi/budget` - Get budget metrics
- `GET /api/governance/kpi/overtime-forecast` - Get overtime forecast
- `GET /api/governance/kpi/time-series` - Get KPI time series
- `POST /api/governance/kpi/report` - Generate report
- `GET /api/governance/kpi/report/{id}` - Get specific report
- `GET /api/governance/kpi/reports` - List all reports

### Utility Endpoints
- `GET /api/governance/audit-log` - Get audit log entries
- `GET /api/governance/statistics` - Get engine statistics
- `GET /api/governance/health` - Health check

## WebSocket Channels

### /ws/governance/decisions
Real-time decision updates and status changes.

**Message Types:**
- `decision_update` - New decision created
- `decision_status_change` - Decision status changed

### /ws/governance/optimizations
Real-time optimization results and progress.

**Message Types:**
- `optimization_result` - Optimization completed
- `optimization_progress` - Optimization in progress
- `resource_update` - Resource status changed

### /ws/governance/kpi
Real-time KPI metric updates.

**Message Types:**
- `kpi_update` - Individual KPI updated
- `city_health_update` - City health index changed
- `department_score_update` - Department score changed
- `budget_alert` - Budget threshold alert

### /ws/governance/scenario/{scenario_id}
Scenario playback and simulation updates.

**Message Types:**
- `scenario_event` - Timeline event occurred
- `scenario_progress` - Simulation progress
- `scenario_metrics` - Metrics snapshot
- `scenario_complete` - Simulation completed

## Frontend Pages

### City Operations Dashboard (`/city-governance`)
Main dashboard showing:
- City Health Score
- Resource Efficiency Score
- Recommended Deployments
- City Alerts Feed
- Rolling 24-hour Forecast

### Resource Optimization Panel
Interactive resource management:
- Drag-and-drop unit allocation
- Zone coverage map
- Optimization metrics
- "Run Optimization" modal
- Explainability drawer

### Scenario Simulator
What-if modeling interface:
- Scenario template selection
- Variable sliders
- Run simulation button
- Result timeline
- Risk outcome visualization
- Downloadable reports

### Governance KPI Dashboard
Performance metrics display:
- Response time trendline
- Patrol efficiency graph
- Fire/EMS coverage map
- Utility uptime bar chart
- Crowd density forecast
- Traffic congestion score
- Budget and overtime metrics

## Security & Permissions

### CJIS Compliance
- All governance operations are logged with CJIS-aligned audit entries
- Audit logs include: timestamp, action, resource type, resource ID, user ID, details
- Logs are retained and can be queried via API

### Permission Model
- RTCC Administrator - Full access to all governance functions
- Department Supervisor - Access to department-specific decisions and KPIs
- Operator - View-only access to dashboards and recommendations

## Integration with Phase 22

The City Governance Engine integrates with the Phase 22 AI City Brain:

1. **Data Ingestion** - Receives real-time city state from City Brain
2. **Digital Twin** - Uses city model for scenario simulation
3. **Predictions** - Incorporates City Brain predictions into decisions
4. **Events** - Subscribes to City Brain event bus for real-time updates

## Configuration

### Environment Variables
```
GOVERNANCE_ENGINE_ENABLED=true
GOVERNANCE_DECISION_THRESHOLD=0.7
GOVERNANCE_OPTIMIZATION_INTERVAL=300
GOVERNANCE_KPI_REFRESH_INTERVAL=300
```

### Docker Service
The governance engine runs as part of the main backend service with optional autoscaling based on CPU utilization.

## Testing

Phase 23 includes 8 test suites:
1. GovernanceDecisionEngine tests
2. ResourceOptimizer tests
3. ScenarioSimulator tests
4. KPIEngine tests
5. Governance API endpoint tests
6. Governance WebSocket tests
7. Frontend governance UI tests
8. Integration tests with Phase 22

## Performance Considerations

- Decision engine processes city data in < 100ms
- Optimization algorithms complete in < 5 seconds
- Scenario simulations complete in < 10 seconds
- KPI calculations refresh every 5 minutes
- WebSocket broadcasts are batched for efficiency

## Future Enhancements

- Machine learning model training from historical decisions
- Advanced multi-objective optimization algorithms
- Real-time scenario playback with live data
- Predictive maintenance scheduling
- Cross-city federation for regional coordination
