"""
Phase 23: City Governance API Router

REST API endpoints for the AI City Governance & Resource Optimization Engine.
Includes CJIS-aligned audit logging and RTCC Administrator permissions.
"""

from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import uuid

from ...city_governance import (
    get_governance_engine,
    GovernanceDecisionEngine,
    DecisionDomain,
    DecisionStatus,
    RecommendationType,
)
from ...city_governance.resource_optimizer import (
    get_resource_optimizer,
    ResourceOptimizer,
    AlgorithmType,
    OptimizationObjective,
    ResourceType,
    MaintenanceTask,
)
from ...city_governance.scenario_simulator import (
    get_scenario_simulator,
    CityScenarioSimulator,
    ScenarioType,
)
from ...city_governance.kpi_engine import (
    get_kpi_engine,
    GovernanceKPIEngine,
    KPICategory,
    ReportPeriod,
)


router = APIRouter(prefix="/governance", tags=["City Governance"])


class AuditLogger:
    """CJIS-aligned audit logger for governance operations."""

    _logs: list[dict[str, Any]] = []

    @classmethod
    def log(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str = "system",
        details: Optional[dict[str, Any]] = None,
    ):
        """Log an audit entry."""
        entry = {
            "audit_id": f"audit-{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "details": details or {},
            "ip_address": "internal",
            "session_id": "api-session",
        }
        cls._logs.append(entry)
        if len(cls._logs) > 10000:
            cls._logs = cls._logs[-5000:]

    @classmethod
    def get_logs(cls, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit logs."""
        return cls._logs[-limit:]


class DecisionRequest(BaseModel):
    """Request model for creating a governance decision."""
    city_state: dict[str, Any] = Field(..., description="Current city state data")


class DecisionApprovalRequest(BaseModel):
    """Request model for approving a decision."""
    approved_by: str = Field(..., description="User approving the decision")
    notes: Optional[str] = Field(None, description="Approval notes")


class DecisionRejectionRequest(BaseModel):
    """Request model for rejecting a decision."""
    rejected_by: str = Field(..., description="User rejecting the decision")
    reason: str = Field(..., description="Rejection reason")


class OptimizationRequest(BaseModel):
    """Request model for running optimization."""
    algorithm: str = Field("linear_programming", description="Optimization algorithm")
    objectives: list[str] = Field(
        ["maximize_coverage"],
        description="Optimization objectives",
    )
    resource_types: Optional[list[str]] = Field(
        None,
        description="Resource types to optimize",
    )


class RouteOptimizationRequest(BaseModel):
    """Request model for route optimization."""
    unit_id: str = Field(..., description="Unit ID")
    waypoints: list[tuple[float, float]] = Field(..., description="Waypoints to visit")
    priorities: list[int] = Field(..., description="Priority for each waypoint")


class MaintenanceScheduleRequest(BaseModel):
    """Request model for maintenance scheduling."""
    tasks: list[dict[str, Any]] = Field(..., description="Maintenance tasks to schedule")


class ScenarioCreateRequest(BaseModel):
    """Request model for creating a scenario."""
    scenario_type: str = Field(..., description="Type of scenario")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    variables: list[dict[str, Any]] = Field(..., description="Scenario variables")
    duration_hours: int = Field(24, description="Simulation duration in hours")
    affected_zones: list[str] = Field(..., description="Affected zones")
    created_by: str = Field("user", description="Creator")


class ScenarioFromTemplateRequest(BaseModel):
    """Request model for creating scenario from template."""
    template_id: str = Field(..., description="Template ID")
    variable_overrides: Optional[dict[str, float]] = Field(
        None,
        description="Variable overrides",
    )
    created_by: str = Field("user", description="Creator")


class VariableUpdateRequest(BaseModel):
    """Request model for updating a scenario variable."""
    variable_name: str = Field(..., description="Variable name")
    new_value: float = Field(..., description="New value")


class ReportGenerateRequest(BaseModel):
    """Request model for generating a report."""
    period: str = Field("daily", description="Report period")


@router.post("/decisions")
async def create_decisions(request: DecisionRequest):
    """
    Process city data and generate governance decisions.
    
    Parses real-time city data and computes decision recommendations
    using the weighted rules engine and ML policy engine.
    """
    engine = get_governance_engine()
    decisions = engine.process_city_data(request.city_state)

    AuditLogger.log(
        action="create_decisions",
        resource_type="governance_decision",
        resource_id="batch",
        details={"count": len(decisions)},
    )

    return {
        "success": True,
        "decisions": [d.to_dict() for d in decisions],
        "count": len(decisions),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/recommendations")
async def get_recommendations(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Get governance recommendations.
    
    Returns pending and recent recommendations with optional filtering.
    """
    engine = get_governance_engine()

    if domain:
        try:
            domain_enum = DecisionDomain(domain)
            decisions = engine.get_decisions_by_domain(domain_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
    else:
        decisions = list(engine._decisions.values())

    if status:
        try:
            status_enum = DecisionStatus(status)
            decisions = [d for d in decisions if d.status == status_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    decisions = sorted(decisions, key=lambda d: d.created_at, reverse=True)
    total = len(decisions)
    decisions = decisions[offset : offset + limit]

    AuditLogger.log(
        action="get_recommendations",
        resource_type="governance_decision",
        resource_id="query",
        details={"domain": domain, "status": status, "count": len(decisions)},
    )

    return {
        "success": True,
        "recommendations": [d.to_dict() for d in decisions],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific governance decision by ID."""
    engine = get_governance_engine()
    decision = engine.get_decision(decision_id)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    AuditLogger.log(
        action="get_decision",
        resource_type="governance_decision",
        resource_id=decision_id,
    )

    return {
        "success": True,
        "decision": decision.to_dict(),
    }


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, request: DecisionApprovalRequest):
    """Approve a pending governance decision."""
    engine = get_governance_engine()

    success = engine.approve_decision(
        decision_id,
        request.approved_by,
        request.notes,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Decision not found or not in pending status",
        )

    AuditLogger.log(
        action="approve_decision",
        resource_type="governance_decision",
        resource_id=decision_id,
        user_id=request.approved_by,
        details={"notes": request.notes},
    )

    return {
        "success": True,
        "message": "Decision approved",
        "decision_id": decision_id,
    }


@router.post("/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, request: DecisionRejectionRequest):
    """Reject a pending governance decision."""
    engine = get_governance_engine()

    success = engine.reject_decision(
        decision_id,
        request.rejected_by,
        request.reason,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Decision not found or not in pending status",
        )

    AuditLogger.log(
        action="reject_decision",
        resource_type="governance_decision",
        resource_id=decision_id,
        user_id=request.rejected_by,
        details={"reason": request.reason},
    )

    return {
        "success": True,
        "message": "Decision rejected",
        "decision_id": decision_id,
    }


@router.post("/decisions/{decision_id}/implement")
async def implement_decision(decision_id: str):
    """Mark an approved decision as implemented."""
    engine = get_governance_engine()

    success = engine.implement_decision(decision_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Decision not found or not in approved status",
        )

    AuditLogger.log(
        action="implement_decision",
        resource_type="governance_decision",
        resource_id=decision_id,
    )

    return {
        "success": True,
        "message": "Decision implemented",
        "decision_id": decision_id,
    }


@router.get("/resource-optimization")
async def get_resource_optimization_status():
    """Get current resource optimization status and statistics."""
    optimizer = get_resource_optimizer()

    resources = optimizer.get_resources()
    zones = optimizer.get_zones()
    history = optimizer.get_optimization_history(5)
    stats = optimizer.get_statistics()

    AuditLogger.log(
        action="get_optimization_status",
        resource_type="resource_optimization",
        resource_id="status",
    )

    return {
        "success": True,
        "resources": [r.to_dict() for r in resources],
        "zones": [z.to_dict() for z in zones],
        "recent_optimizations": [h.to_dict() for h in history],
        "statistics": stats,
    }


@router.post("/resource-optimization/run")
async def run_resource_optimization(request: OptimizationRequest):
    """
    Run resource optimization with specified algorithm and objectives.
    
    Supports linear programming, multi-objective optimization,
    route optimization, load balancing, and cost-reward scoring.
    """
    optimizer = get_resource_optimizer()

    try:
        algorithm = AlgorithmType(request.algorithm)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid algorithm: {request.algorithm}",
        )

    objectives = []
    for obj in request.objectives:
        try:
            objectives.append(OptimizationObjective(obj))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid objective: {obj}",
            )

    resource_types = None
    if request.resource_types:
        resource_types = []
        for rt in request.resource_types:
            try:
                resource_types.append(ResourceType(rt))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid resource type: {rt}",
                )

    result = optimizer.run_optimization(algorithm, objectives, resource_types)

    AuditLogger.log(
        action="run_optimization",
        resource_type="resource_optimization",
        resource_id=result.optimization_id,
        details={
            "algorithm": request.algorithm,
            "objectives": request.objectives,
            "allocations": len(result.allocations),
        },
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.post("/resource-optimization/patrol")
async def optimize_patrol_coverage():
    """Optimize patrol unit coverage across zones."""
    optimizer = get_resource_optimizer()
    result = optimizer.optimize_patrol_coverage()

    AuditLogger.log(
        action="optimize_patrol",
        resource_type="resource_optimization",
        resource_id=result.optimization_id,
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.post("/resource-optimization/fire-ems")
async def optimize_fire_ems_coverage():
    """Optimize fire and EMS coverage."""
    optimizer = get_resource_optimizer()
    result = optimizer.optimize_fire_ems_coverage()

    AuditLogger.log(
        action="optimize_fire_ems",
        resource_type="resource_optimization",
        resource_id=result.optimization_id,
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.post("/resource-optimization/traffic")
async def optimize_traffic_flow():
    """Optimize traffic unit deployment."""
    optimizer = get_resource_optimizer()
    result = optimizer.optimize_traffic_flow()

    AuditLogger.log(
        action="optimize_traffic",
        resource_type="resource_optimization",
        resource_id=result.optimization_id,
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.post("/resource-optimization/route")
async def optimize_route(request: RouteOptimizationRequest):
    """Get optimized route for a unit."""
    optimizer = get_resource_optimizer()

    result = optimizer.get_route_optimization(
        request.unit_id,
        request.waypoints,
        request.priorities,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    AuditLogger.log(
        action="optimize_route",
        resource_type="resource_optimization",
        resource_id=request.unit_id,
    )

    return {
        "success": True,
        "result": result,
    }


@router.get("/resource-optimization/vehicles")
async def get_vehicle_allocation():
    """Get vehicle allocation and fuel efficiency analysis."""
    optimizer = get_resource_optimizer()
    result = optimizer.optimize_vehicle_allocation()

    AuditLogger.log(
        action="get_vehicle_allocation",
        resource_type="resource_optimization",
        resource_id="vehicles",
    )

    return {
        "success": True,
        "result": result,
    }


@router.post("/resource-optimization/maintenance")
async def schedule_maintenance(request: MaintenanceScheduleRequest):
    """Schedule preventive maintenance tasks."""
    optimizer = get_resource_optimizer()

    tasks = []
    for task_data in request.tasks:
        task = MaintenanceTask(
            task_id=task_data.get("task_id", f"task-{uuid.uuid4().hex[:8]}"),
            asset_id=task_data.get("asset_id", ""),
            asset_name=task_data.get("asset_name", ""),
            task_type=task_data.get("task_type", "general"),
            priority=task_data.get("priority", 1),
            estimated_duration_hours=task_data.get("estimated_duration_hours", 2),
            required_skills=task_data.get("required_skills", []),
            required_equipment=task_data.get("required_equipment", []),
            due_date=datetime.fromisoformat(task_data["due_date"])
            if "due_date" in task_data
            else datetime.utcnow(),
        )
        tasks.append(task)

    scheduled = optimizer.schedule_preventive_maintenance(tasks)

    AuditLogger.log(
        action="schedule_maintenance",
        resource_type="resource_optimization",
        resource_id="maintenance",
        details={"tasks_scheduled": len(scheduled)},
    )

    return {
        "success": True,
        "scheduled_tasks": [t.to_dict() for t in scheduled],
        "total_scheduled": len(scheduled),
    }


@router.get("/scenario/templates")
async def get_scenario_templates():
    """Get available scenario templates."""
    simulator = get_scenario_simulator()
    templates = simulator.get_templates()

    return {
        "success": True,
        "templates": [t.to_dict() for t in templates],
        "count": len(templates),
    }


@router.post("/scenario/create")
async def create_scenario(request: ScenarioCreateRequest):
    """Create a new scenario configuration."""
    simulator = get_scenario_simulator()

    try:
        scenario_type = ScenarioType(request.scenario_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario type: {request.scenario_type}",
        )

    config = simulator.create_scenario(
        scenario_type=scenario_type,
        name=request.name,
        description=request.description,
        variables=request.variables,
        duration_hours=request.duration_hours,
        affected_zones=request.affected_zones,
        created_by=request.created_by,
    )

    AuditLogger.log(
        action="create_scenario",
        resource_type="scenario",
        resource_id=config.scenario_id,
        user_id=request.created_by,
    )

    return {
        "success": True,
        "scenario": config.to_dict(),
    }


@router.post("/scenario/from-template")
async def create_scenario_from_template(request: ScenarioFromTemplateRequest):
    """Create a scenario from a template."""
    simulator = get_scenario_simulator()

    config = simulator.create_from_template(
        template_id=request.template_id,
        variable_overrides=request.variable_overrides,
        created_by=request.created_by,
    )

    if not config:
        raise HTTPException(status_code=404, detail="Template not found")

    AuditLogger.log(
        action="create_scenario_from_template",
        resource_type="scenario",
        resource_id=config.scenario_id,
        user_id=request.created_by,
        details={"template_id": request.template_id},
    )

    return {
        "success": True,
        "scenario": config.to_dict(),
    }


@router.post("/scenario/run")
async def run_scenario(scenario_id: str = Query(..., description="Scenario ID to run")):
    """Run a scenario simulation."""
    simulator = get_scenario_simulator()

    result = simulator.run_scenario(scenario_id)

    if not result:
        raise HTTPException(status_code=404, detail="Scenario not found")

    AuditLogger.log(
        action="run_scenario",
        resource_type="scenario",
        resource_id=scenario_id,
        details={"result_id": result.result_id},
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.get("/scenario/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get a specific scenario configuration."""
    simulator = get_scenario_simulator()
    config = simulator.get_scenario(scenario_id)

    if not config:
        raise HTTPException(status_code=404, detail="Scenario not found")

    AuditLogger.log(
        action="get_scenario",
        resource_type="scenario",
        resource_id=scenario_id,
    )

    return {
        "success": True,
        "scenario": config.to_dict(),
    }


@router.get("/scenario/result/{result_id}")
async def get_scenario_result(result_id: str):
    """Get a scenario simulation result."""
    simulator = get_scenario_simulator()
    result = simulator.get_result(result_id)

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    AuditLogger.log(
        action="get_scenario_result",
        resource_type="scenario_result",
        resource_id=result_id,
    )

    return {
        "success": True,
        "result": result.to_dict(),
    }


@router.put("/scenario/{scenario_id}/variable")
async def update_scenario_variable(scenario_id: str, request: VariableUpdateRequest):
    """Update a variable in a scenario."""
    simulator = get_scenario_simulator()

    success = simulator.update_variable(
        scenario_id,
        request.variable_name,
        request.new_value,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Scenario not found or invalid variable",
        )

    AuditLogger.log(
        action="update_scenario_variable",
        resource_type="scenario",
        resource_id=scenario_id,
        details={
            "variable": request.variable_name,
            "new_value": request.new_value,
        },
    )

    return {
        "success": True,
        "message": "Variable updated",
    }


@router.delete("/scenario/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete a scenario."""
    simulator = get_scenario_simulator()

    success = simulator.delete_scenario(scenario_id)

    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")

    AuditLogger.log(
        action="delete_scenario",
        resource_type="scenario",
        resource_id=scenario_id,
    )

    return {
        "success": True,
        "message": "Scenario deleted",
    }


@router.get("/scenario")
async def list_scenarios(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all scenarios."""
    simulator = get_scenario_simulator()
    scenarios = simulator.get_scenarios()

    total = len(scenarios)
    scenarios = scenarios[offset : offset + limit]

    return {
        "success": True,
        "scenarios": [s.to_dict() for s in scenarios],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/kpi")
async def get_kpis(
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Get all KPI metrics."""
    engine = get_kpi_engine()

    if category:
        try:
            category_enum = KPICategory(category)
            metrics = engine.get_kpis_by_category(category_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}",
            )
    else:
        metrics = engine.get_all_kpis()

    AuditLogger.log(
        action="get_kpis",
        resource_type="kpi",
        resource_id="query",
        details={"category": category, "count": len(metrics)},
    )

    return {
        "success": True,
        "kpis": [m.to_dict() for m in metrics],
        "count": len(metrics),
    }


@router.get("/kpi/city-health")
async def get_city_health_index():
    """Get the city health index."""
    engine = get_kpi_engine()
    index = engine.get_city_health_index()

    AuditLogger.log(
        action="get_city_health",
        resource_type="kpi",
        resource_id=index.index_id,
    )

    return {
        "success": True,
        "city_health_index": index.to_dict(),
    }


@router.get("/kpi/departments")
async def get_department_scores():
    """Get performance scores for all departments."""
    engine = get_kpi_engine()
    scores = engine.get_department_scores()

    AuditLogger.log(
        action="get_department_scores",
        resource_type="kpi",
        resource_id="departments",
    )

    return {
        "success": True,
        "department_scores": [s.to_dict() for s in scores],
    }


@router.get("/kpi/budget")
async def get_budget_metrics():
    """Get budget and overtime metrics."""
    engine = get_kpi_engine()
    metrics = engine.get_budget_metrics()

    AuditLogger.log(
        action="get_budget_metrics",
        resource_type="kpi",
        resource_id="budget",
    )

    return {
        "success": True,
        "budget_metrics": metrics.to_dict(),
    }


@router.get("/kpi/overtime-forecast")
async def get_overtime_forecast(
    months: int = Query(3, ge=1, le=12, description="Months to forecast"),
):
    """Get overtime forecast."""
    engine = get_kpi_engine()
    forecast = engine.get_overtime_forecast(months)

    AuditLogger.log(
        action="get_overtime_forecast",
        resource_type="kpi",
        resource_id="overtime",
        details={"months": months},
    )

    return {
        "success": True,
        "forecast": forecast,
    }


@router.get("/kpi/time-series")
async def get_kpi_time_series(
    category: str = Query(..., description="KPI category"),
    period: str = Query("daily", description="Time period"),
):
    """Get time series data for KPIs."""
    engine = get_kpi_engine()

    try:
        category_enum = KPICategory(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}",
        )

    try:
        period_enum = ReportPeriod(period)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {period}",
        )

    series = engine.get_time_series(category_enum, period_enum)

    AuditLogger.log(
        action="get_kpi_time_series",
        resource_type="kpi",
        resource_id="time_series",
        details={"category": category, "period": period},
    )

    return {
        "success": True,
        "time_series": [s.to_dict() for s in series],
    }


@router.post("/kpi/report")
async def generate_report(request: ReportGenerateRequest):
    """Generate a comprehensive performance report."""
    engine = get_kpi_engine()

    try:
        period = ReportPeriod(request.period)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {request.period}",
        )

    report = engine.generate_report(period)

    AuditLogger.log(
        action="generate_report",
        resource_type="kpi_report",
        resource_id=report.report_id,
        details={"period": request.period},
    )

    return {
        "success": True,
        "report": report.to_dict(),
    }


@router.get("/kpi/report/{report_id}")
async def get_report(report_id: str):
    """Get a specific report."""
    engine = get_kpi_engine()
    report = engine.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    AuditLogger.log(
        action="get_report",
        resource_type="kpi_report",
        resource_id=report_id,
    )

    return {
        "success": True,
        "report": report.to_dict(),
    }


@router.get("/kpi/reports")
async def list_reports(
    period: Optional[str] = Query(None, description="Filter by period"),
    limit: int = Query(20, ge=1, le=100),
):
    """List all reports."""
    engine = get_kpi_engine()

    period_enum = None
    if period:
        try:
            period_enum = ReportPeriod(period)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period: {period}",
            )

    reports = engine.get_reports(period_enum)[:limit]

    return {
        "success": True,
        "reports": [r.to_dict() for r in reports],
        "count": len(reports),
    }


@router.get("/audit-log")
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000, description="Maximum entries"),
):
    """Get governance audit log entries."""
    logs = AuditLogger.get_logs(limit)

    return {
        "success": True,
        "audit_log": logs,
        "count": len(logs),
    }


@router.get("/statistics")
async def get_governance_statistics():
    """Get overall governance engine statistics."""
    governance_engine = get_governance_engine()
    optimizer = get_resource_optimizer()
    simulator = get_scenario_simulator()
    kpi_engine = get_kpi_engine()

    return {
        "success": True,
        "statistics": {
            "governance": governance_engine.get_statistics(),
            "optimization": optimizer.get_statistics(),
            "simulation": simulator.get_statistics(),
            "kpi": kpi_engine.get_statistics(),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for the governance API."""
    return {
        "status": "healthy",
        "service": "city-governance",
        "timestamp": datetime.utcnow().isoformat(),
    }
