"""
National Security API Router

Comprehensive REST API endpoints for the Autonomous National Security Engine (AI-NSE).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.national_security import (
    CyberIntelEngine,
    MalwareType,
    ThreatSeverity,
    AttackVector,
    InsiderThreatEngine,
    RiskLevel,
    BehaviorType,
    AnomalyType,
    DepartmentType,
    ClearanceLevel,
    GeopoliticalRiskEngine,
    ConflictIntensity,
    ThreatActorType,
    RegionStability,
    ThreatDomain,
    SanctionType,
    EventCategory,
    FinancialCrimeEngine,
    FraudType,
    RiskCategory,
    TransactionFlag,
    CryptoRiskIndicator,
    EntityType,
    NationalRiskFusionEngine,
    StabilityLevel,
    RiskDomain,
    FusionMethod,
    AlertUrgency,
    NationalSecurityAlertManager,
    AlertPriority,
    AlertCategory,
    AlertDestination,
)

router = APIRouter(prefix="/api/national-security", tags=["National Security"])

cyber_engine = CyberIntelEngine()
insider_engine = InsiderThreatEngine()
geopolitical_engine = GeopoliticalRiskEngine()
financial_engine = FinancialCrimeEngine()
fusion_engine = NationalRiskFusionEngine()
alert_manager = NationalSecurityAlertManager()


class MalwareSignalRequest(BaseModel):
    malware_type: str
    name: str
    description: str
    severity: str = "medium"
    attack_vector: str = "other"
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    file_name: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    affected_sectors: List[str] = []
    indicators_of_compromise: List[str] = []
    detection_method: str = "signature_based"
    confidence_score: float = 0.8


class BotnetActivityRequest(BaseModel):
    botnet_name: str
    command_control_ips: List[str]
    estimated_size: int = 0
    target_sectors: List[str] = []
    attack_type: str = "ddos"
    communication_protocol: str = "http"
    encryption_used: bool = True
    geographic_distribution: Dict[str, int] = {}


class RansomwareAlertRequest(BaseModel):
    ransomware_family: str
    severity: str
    attack_vector: str
    target_sectors: List[str] = []
    ransom_demand: Optional[float] = None
    ransom_currency: str = "BTC"
    decryption_available: bool = False
    known_victims: List[str] = []
    geographic_targets: List[str] = []
    indicators_of_compromise: List[str] = []
    mitigation_steps: List[str] = []


class VulnerabilityReportRequest(BaseModel):
    vulnerability_name: str
    description: str
    severity: str
    cvss_score: float
    cve_id: Optional[str] = None
    affected_systems: List[str] = []
    affected_sectors: List[str] = []
    exploit_available: bool = False
    patch_available: bool = False
    patch_url: Optional[str] = None
    affected_vendors: List[str] = []
    affected_products: List[str] = []


class EmployeeRiskProfileRequest(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    role: str
    clearance_level: str = "unclassified"
    access_level: int = 1
    is_privileged: bool = False
    is_contractor: bool = False
    manager_id: Optional[str] = None


class BehaviorDeviationRequest(BaseModel):
    employee_id: str
    behavior_type: str
    observed_value: Any
    description: str
    context: Dict[str, Any] = {}


class AccessAnomalyRequest(BaseModel):
    employee_id: str
    anomaly_type: str
    resource_accessed: str
    description: str
    source_ip: Optional[str] = None
    source_device: Optional[str] = None
    source_location: Optional[str] = None
    expected_pattern: Dict[str, Any] = {}
    observed_pattern: Dict[str, Any] = {}


class ConflictEventRequest(BaseModel):
    name: str
    description: str
    intensity: str
    region: str
    countries_involved: List[str]
    casualties_estimate: int = 0
    displaced_estimate: int = 0
    threat_domains: List[str] = []
    escalation_risk: float = 0.5
    international_response: str = "monitoring"
    sources: List[str] = []


class NationStateThreatRequest(BaseModel):
    actor_name: str
    actor_type: str
    country_of_origin: str
    target_countries: List[str]
    threat_domains: List[str]
    capability_score: float
    intent_score: float
    known_operations: List[str] = []
    attributed_attacks: List[str] = []
    sanctions_status: bool = False
    alliance_affiliations: List[str] = []
    resources_estimate: str = "unknown"
    confidence_level: float = 0.7


class SanctionsEventRequest(BaseModel):
    sanction_type: str
    issuing_authority: str
    reason: str
    target_country: Optional[str] = None
    target_entities: List[str] = []
    target_individuals: List[str] = []
    economic_impact_estimate: float = 0
    compliance_requirements: List[str] = []
    sources: List[str] = []


class GeoEconomicRiskRequest(BaseModel):
    country: str
    region: str
    economic_risk_score: float
    political_risk_score: float
    security_risk_score: float
    gdp_growth_forecast: float = 0
    inflation_rate: float = 0
    currency_stability: float = 50
    trade_dependency_score: float = 50
    debt_to_gdp_ratio: float = 0
    foreign_investment_risk: float = 50
    supply_chain_vulnerability: float = 50
    key_risk_factors: List[str] = []
    opportunities: List[str] = []
    forecast_horizon_months: int = 12
    confidence_level: float = 0.7


class FraudPatternRequest(BaseModel):
    fraud_type: str
    name: str
    description: str
    entities_involved: List[str]
    transactions_involved: List[str]
    total_amount: float
    currency: str = "USD"
    detection_method: str = "rule_based"
    indicators: List[str] = []
    geographic_scope: List[str] = []
    time_span_days: int = 30
    confidence_score: float = 0.7


class CryptoWalletRiskRequest(BaseModel):
    wallet_address: str
    blockchain: str = "bitcoin"
    total_received: float = 0
    total_sent: float = 0
    transaction_count: int = 0
    linked_wallets: List[str] = []
    exchange_interactions: List[str] = []
    mixer_exposure: float = 0
    darknet_exposure: float = 0
    sanctions_exposure: float = 0
    cluster_id: Optional[str] = None
    entity_attribution: Optional[str] = None


class TransactionAnomalyRequest(BaseModel):
    transaction_id: str
    anomaly_type: str
    description: str
    source_entity: str
    destination_entity: str
    amount: float
    currency: str = "USD"
    flags: List[str] = []
    baseline_comparison: Dict[str, Any] = {}
    deviation_metrics: Dict[str, float] = {}
    related_transactions: List[str] = []


class MoneyFlowNetworkRequest(BaseModel):
    name: str
    description: str = ""


class NetworkNodeRequest(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: Optional[str] = None
    risk_score: float = 0
    total_inflow: float = 0
    total_outflow: float = 0
    transaction_count: int = 0
    flags: List[str] = []


class NetworkEdgeRequest(BaseModel):
    source_node: str
    target_node: str
    total_amount: float
    transaction_count: int = 1
    currency: str = "USD"
    flags: List[str] = []


class NationalStabilityScoreRequest(BaseModel):
    domain_scores: Dict[str, Dict[str, float]]
    fusion_method: str = "weighted_average"


class RiskFusionRequest(BaseModel):
    domain_scores: Dict[str, float]
    fusion_method: str = "weighted_average"


class EarlyWarningRequest(BaseModel):
    title: str
    description: str
    urgency: str
    domains_affected: List[str]
    risk_score: float
    probability: float
    time_horizon_hours: int
    indicators: List[str]
    potential_impacts: List[str]
    recommended_actions: List[str]
    source_signals: List[str] = []
    confidence_level: float = 0.7


class TrendPredictionRequest(BaseModel):
    domain: str
    current_score: float
    prediction_horizon_hours: int = 24
    key_factors: List[str] = []


class SecurityAlertRequest(BaseModel):
    title: str
    description: str
    priority: str
    category: str
    risk_score: float
    source_module: str
    source_signal_id: Optional[str] = None
    affected_domains: List[str] = []
    expires_in_hours: Optional[int] = None
    related_alerts: List[str] = []
    attachments: List[str] = []
    metadata: Dict[str, Any] = {}


class AlertSubscriptionRequest(BaseModel):
    subscriber_id: str
    subscriber_name: str
    subscriber_role: str
    categories: List[str]
    min_priority: str = "routine"
    destinations: List[str] = []
    notification_methods: List[str] = ["websocket"]


class RoutingRuleRequest(BaseModel):
    name: str
    description: str
    conditions: Dict[str, Any]
    destinations: List[str]
    priority_override: Optional[str] = None
    auto_escalate: bool = False
    escalation_delay_minutes: int = 30


@router.get("/cyber/malware")
async def get_malware_signals(
    malware_type: Optional[str] = None,
    severity: Optional[str] = None,
    sector: Optional[str] = None,
    active_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get malware signals with optional filtering."""
    mt = MalwareType(malware_type) if malware_type else None
    sev = ThreatSeverity(severity) if severity else None
    
    signals = cyber_engine.get_malware_signals(
        malware_type=mt,
        severity=sev,
        active_only=active_only,
        limit=limit,
    )
    
    return {
        "signals": [
            {
                "signal_id": s.signal_id,
                "malware_type": s.malware_type.value,
                "severity": s.severity.value,
                "name": s.name,
                "description": s.description,
                "attack_vector": s.attack_vector.value,
                "confidence_score": s.confidence_score,
                "is_active": s.is_active,
                "first_seen": s.first_seen.isoformat(),
                "last_seen": s.last_seen.isoformat(),
            }
            for s in signals
        ],
        "count": len(signals),
    }


@router.post("/cyber/malware")
async def create_malware_signal(request: MalwareSignalRequest) -> Dict[str, Any]:
    """Create a new malware signal."""
    signal = cyber_engine.detect_malware_signal(
        malware_type=MalwareType(request.malware_type),
        name=request.name,
        description=request.description,
        severity=ThreatSeverity(request.severity),
        attack_vector=AttackVector(request.attack_vector),
        hash_md5=request.hash_md5,
        hash_sha256=request.hash_sha256,
        file_name=request.file_name,
        source_ip=request.source_ip,
        destination_ip=request.destination_ip,
        indicators_of_compromise=request.indicators_of_compromise,
        detection_method=request.detection_method,
        confidence_score=request.confidence_score,
    )
    
    return {
        "signal_id": signal.signal_id,
        "malware_type": signal.malware_type.value,
        "severity": signal.severity.value,
        "name": signal.name,
        "created": True,
    }


@router.get("/cyber/botnets")
async def get_botnet_activities(
    status: Optional[str] = None,
    sector: Optional[str] = None,
    min_threat_score: float = 0,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get botnet activities with optional filtering."""
    activities = cyber_engine.get_botnet_activities(
        min_threat_score=min_threat_score,
        limit=limit,
    )
    
    return {
        "activities": [
            {
                "activity_id": a.activity_id,
                "botnet_name": a.botnet_name,
                "status": a.status.value,
                "estimated_size": a.estimated_size,
                "threat_score": a.threat_score,
                "confidence_score": a.confidence_score,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in activities
        ],
        "count": len(activities),
    }


@router.post("/cyber/botnets")
async def create_botnet_activity(request: BotnetActivityRequest) -> Dict[str, Any]:
    """Create a new botnet activity prediction."""
    activity = cyber_engine.predict_botnet_activity(
        botnet_name=request.botnet_name,
        command_control_ips=request.command_control_ips,
        estimated_size=request.estimated_size,
        attack_type=request.attack_type,
        communication_protocol=request.communication_protocol,
        encryption_used=request.encryption_used,
        geographic_distribution=request.geographic_distribution,
    )
    
    return {
        "activity_id": activity.activity_id,
        "botnet_name": activity.botnet_name,
        "status": activity.status.value,
        "threat_score": activity.threat_score,
        "created": True,
    }


@router.get("/cyber/ransomware")
async def get_ransomware_alerts(
    severity: Optional[str] = None,
    sector: Optional[str] = None,
    active_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get ransomware alerts with optional filtering."""
    sev = ThreatSeverity(severity) if severity else None
    
    alerts = cyber_engine.get_ransomware_alerts(
        severity=sev,
        active_only=active_only,
        limit=limit,
    )
    
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "ransomware_family": a.ransomware_family,
                "severity": a.severity.value,
                "attack_vector": a.attack_vector.value,
                "threat_score": a.threat_score,
                "is_active": a.is_active,
                "first_detected": a.first_detected.isoformat(),
            }
            for a in alerts
        ],
        "count": len(alerts),
    }


@router.post("/cyber/ransomware")
async def create_ransomware_alert(request: RansomwareAlertRequest) -> Dict[str, Any]:
    """Create a new ransomware alert."""
    alert = cyber_engine.create_ransomware_alert(
        ransomware_family=request.ransomware_family,
        severity=ThreatSeverity(request.severity),
        attack_vector=AttackVector(request.attack_vector),
        ransom_demand=request.ransom_demand,
        ransom_currency=request.ransom_currency,
        decryption_available=request.decryption_available,
        known_victims=request.known_victims,
        geographic_targets=request.geographic_targets,
        indicators_of_compromise=request.indicators_of_compromise,
        mitigation_steps=request.mitigation_steps,
    )
    
    return {
        "alert_id": alert.alert_id,
        "ransomware_family": alert.ransomware_family,
        "severity": alert.severity.value,
        "threat_score": alert.threat_score,
        "created": True,
    }


@router.get("/cyber/vulnerabilities")
async def get_vulnerability_reports(
    severity: Optional[str] = None,
    sector: Optional[str] = None,
    exploit_available: Optional[bool] = None,
    patch_available: Optional[bool] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get vulnerability reports with optional filtering."""
    sev = ThreatSeverity(severity) if severity else None
    
    reports = cyber_engine.get_vulnerability_reports(
        severity=sev,
        exploit_available=exploit_available,
        patch_available=patch_available,
        limit=limit,
    )
    
    return {
        "reports": [
            {
                "report_id": r.report_id,
                "cve_id": r.cve_id,
                "vulnerability_name": r.vulnerability_name,
                "severity": r.severity.value,
                "cvss_score": r.cvss_score,
                "exploit_available": r.exploit_available,
                "patch_available": r.patch_available,
                "discovered_at": r.discovered_at.isoformat(),
            }
            for r in reports
        ],
        "count": len(reports),
    }


@router.post("/cyber/vulnerabilities")
async def create_vulnerability_report(request: VulnerabilityReportRequest) -> Dict[str, Any]:
    """Create a new vulnerability report."""
    report = cyber_engine.scan_vulnerability(
        vulnerability_name=request.vulnerability_name,
        description=request.description,
        severity=ThreatSeverity(request.severity),
        cvss_score=request.cvss_score,
        cve_id=request.cve_id,
        affected_systems=request.affected_systems,
        exploit_available=request.exploit_available,
        patch_available=request.patch_available,
        patch_url=request.patch_url,
        affected_vendors=request.affected_vendors,
        affected_products=request.affected_products,
    )
    
    return {
        "report_id": report.report_id,
        "vulnerability_name": report.vulnerability_name,
        "severity": report.severity.value,
        "cvss_score": report.cvss_score,
        "created": True,
    }


@router.get("/cyber/metrics")
async def get_cyber_metrics() -> Dict[str, Any]:
    """Get cyber intelligence metrics."""
    return cyber_engine.get_metrics()


@router.get("/insider/profiles")
async def get_risk_profiles(
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    min_risk_score: float = 0,
    privileged_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get employee risk profiles with optional filtering."""
    dept = DepartmentType(department) if department else None
    rl = RiskLevel(risk_level) if risk_level else None
    
    profiles = insider_engine.get_risk_profiles(
        department=dept,
        risk_level=rl,
        min_risk_score=min_risk_score,
        privileged_only=privileged_only,
        limit=limit,
    )
    
    return {
        "profiles": [
            {
                "profile_id": p.profile_id,
                "employee_id": p.employee_id,
                "employee_name": p.employee_name,
                "department": p.department.value,
                "role": p.role,
                "risk_level": p.risk_level.value,
                "risk_score": p.risk_score,
                "is_privileged": p.is_privileged,
                "last_assessment": p.last_assessment.isoformat(),
            }
            for p in profiles
        ],
        "count": len(profiles),
    }


@router.post("/insider/profiles")
async def create_risk_profile(request: EmployeeRiskProfileRequest) -> Dict[str, Any]:
    """Create a new employee risk profile."""
    profile = insider_engine.create_risk_profile(
        employee_id=request.employee_id,
        employee_name=request.employee_name,
        department=DepartmentType(request.department),
        role=request.role,
        clearance_level=ClearanceLevel(request.clearance_level),
        access_level=request.access_level,
        is_privileged=request.is_privileged,
        is_contractor=request.is_contractor,
        manager_id=request.manager_id,
    )
    
    return {
        "profile_id": profile.profile_id,
        "employee_id": profile.employee_id,
        "risk_level": profile.risk_level.value,
        "risk_score": profile.risk_score,
        "created": True,
    }


@router.get("/insider/profiles/{employee_id}")
async def get_risk_profile(employee_id: str) -> Dict[str, Any]:
    """Get risk profile for a specific employee."""
    profile = insider_engine.get_risk_profile(employee_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "profile_id": profile.profile_id,
        "employee_id": profile.employee_id,
        "employee_name": profile.employee_name,
        "department": profile.department.value,
        "clearance_level": profile.clearance_level.value,
        "role": profile.role,
        "risk_level": profile.risk_level.value,
        "risk_score": profile.risk_score,
        "risk_factors": profile.risk_factors,
        "is_privileged": profile.is_privileged,
        "is_contractor": profile.is_contractor,
        "last_assessment": profile.last_assessment.isoformat(),
        "next_assessment": profile.next_assessment.isoformat(),
    }


@router.get("/insider/deviations")
async def get_behavior_deviations(
    employee_id: Optional[str] = None,
    behavior_type: Optional[str] = None,
    severity: Optional[str] = None,
    unacknowledged_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get behavior deviations with optional filtering."""
    bt = BehaviorType(behavior_type) if behavior_type else None
    sev = RiskLevel(severity) if severity else None
    
    deviations = insider_engine.get_behavior_deviations(
        employee_id=employee_id,
        behavior_type=bt,
        severity=sev,
        unacknowledged_only=unacknowledged_only,
        limit=limit,
    )
    
    return {
        "deviations": [
            {
                "deviation_id": d.deviation_id,
                "employee_id": d.employee_id,
                "behavior_type": d.behavior_type.value,
                "description": d.description,
                "deviation_score": d.deviation_score,
                "severity": d.severity.value,
                "is_acknowledged": d.is_acknowledged,
                "detected_at": d.detected_at.isoformat(),
            }
            for d in deviations
        ],
        "count": len(deviations),
    }


@router.post("/insider/deviations")
async def create_behavior_deviation(request: BehaviorDeviationRequest) -> Dict[str, Any]:
    """Detect and record a behavior deviation."""
    deviation = insider_engine.detect_behavior_deviation(
        employee_id=request.employee_id,
        behavior_type=BehaviorType(request.behavior_type),
        observed_value=request.observed_value,
        description=request.description,
        context=request.context,
    )
    
    if not deviation:
        raise HTTPException(status_code=400, detail="Deviation not significant or employee not found")
    
    return {
        "deviation_id": deviation.deviation_id,
        "employee_id": deviation.employee_id,
        "behavior_type": deviation.behavior_type.value,
        "deviation_score": deviation.deviation_score,
        "severity": deviation.severity.value,
        "created": True,
    }


@router.get("/insider/anomalies")
async def get_access_anomalies(
    employee_id: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    severity: Optional[str] = None,
    investigation_status: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get access anomalies with optional filtering."""
    at = AnomalyType(anomaly_type) if anomaly_type else None
    sev = RiskLevel(severity) if severity else None
    
    anomalies = insider_engine.get_access_anomalies(
        employee_id=employee_id,
        anomaly_type=at,
        severity=sev,
        investigation_status=investigation_status,
        limit=limit,
    )
    
    return {
        "anomalies": [
            {
                "anomaly_id": a.anomaly_id,
                "employee_id": a.employee_id,
                "anomaly_type": a.anomaly_type.value,
                "description": a.description,
                "resource_accessed": a.resource_accessed,
                "risk_score": a.risk_score,
                "severity": a.severity.value,
                "investigation_status": a.investigation_status,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in anomalies
        ],
        "count": len(anomalies),
    }


@router.post("/insider/anomalies")
async def create_access_anomaly(request: AccessAnomalyRequest) -> Dict[str, Any]:
    """Detect and record an access anomaly."""
    anomaly = insider_engine.detect_access_anomaly(
        employee_id=request.employee_id,
        anomaly_type=AnomalyType(request.anomaly_type),
        resource_accessed=request.resource_accessed,
        description=request.description,
        source_ip=request.source_ip,
        source_device=request.source_device,
        source_location=request.source_location,
        expected_pattern=request.expected_pattern,
        observed_pattern=request.observed_pattern,
    )
    
    if not anomaly:
        raise HTTPException(status_code=400, detail="Employee not found")
    
    return {
        "anomaly_id": anomaly.anomaly_id,
        "employee_id": anomaly.employee_id,
        "anomaly_type": anomaly.anomaly_type.value,
        "risk_score": anomaly.risk_score,
        "severity": anomaly.severity.value,
        "created": True,
    }


@router.post("/insider/assessments/{employee_id}")
async def create_threat_assessment(
    employee_id: str,
    assessor_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a comprehensive threat assessment for an employee."""
    assessment = insider_engine.create_threat_assessment(
        employee_id=employee_id,
        assessor_id=assessor_id,
    )
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "assessment_id": assessment.assessment_id,
        "employee_id": assessment.employee_id,
        "overall_risk_level": assessment.overall_risk_level.value,
        "overall_risk_score": assessment.overall_risk_score,
        "behavior_score": assessment.behavior_score,
        "access_score": assessment.access_score,
        "role_score": assessment.role_score,
        "trend": assessment.trend,
        "recommendations": assessment.recommendations,
        "next_review": assessment.next_review.isoformat(),
    }


@router.get("/insider/high-risk")
async def get_high_risk_employees(
    min_risk_score: float = 65,
    limit: int = Query(50, le=200),
) -> Dict[str, Any]:
    """Get employees with high risk scores."""
    profiles = insider_engine.get_high_risk_employees(
        min_risk_score=min_risk_score,
        limit=limit,
    )
    
    return {
        "profiles": [
            {
                "employee_id": p.employee_id,
                "employee_name": p.employee_name,
                "department": p.department.value,
                "risk_level": p.risk_level.value,
                "risk_score": p.risk_score,
                "risk_factors": p.risk_factors,
            }
            for p in profiles
        ],
        "count": len(profiles),
    }


@router.get("/insider/metrics")
async def get_insider_metrics() -> Dict[str, Any]:
    """Get insider threat metrics."""
    return insider_engine.get_metrics()


@router.get("/geopolitical/conflicts")
async def get_conflict_events(
    region: Optional[str] = None,
    intensity: Optional[str] = None,
    active_only: bool = False,
    country: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get conflict events with optional filtering."""
    ci = ConflictIntensity(intensity) if intensity else None
    
    events = geopolitical_engine.get_conflict_events(
        region=region,
        intensity=ci,
        active_only=active_only,
        country=country,
        limit=limit,
    )
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "name": e.name,
                "description": e.description,
                "intensity": e.intensity.value,
                "region": e.region,
                "countries_involved": e.countries_involved,
                "is_active": e.is_active,
                "escalation_risk": e.escalation_risk,
                "last_updated": e.last_updated.isoformat(),
            }
            for e in events
        ],
        "count": len(events),
    }


@router.post("/geopolitical/conflicts")
async def create_conflict_event(request: ConflictEventRequest) -> Dict[str, Any]:
    """Record a conflict event."""
    event = geopolitical_engine.record_conflict_event(
        name=request.name,
        description=request.description,
        intensity=ConflictIntensity(request.intensity),
        region=request.region,
        countries_involved=request.countries_involved,
        casualties_estimate=request.casualties_estimate,
        displaced_estimate=request.displaced_estimate,
        escalation_risk=request.escalation_risk,
        international_response=request.international_response,
        sources=request.sources,
    )
    
    return {
        "event_id": event.event_id,
        "name": event.name,
        "intensity": event.intensity.value,
        "created": True,
    }


@router.get("/geopolitical/conflict-index")
async def get_conflict_intensity_index(
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Calculate global or regional conflict intensity index."""
    return geopolitical_engine.calculate_conflict_intensity_index(region=region)


@router.get("/geopolitical/threats")
async def get_nation_state_threats(
    actor_type: Optional[str] = None,
    target_country: Optional[str] = None,
    threat_domain: Optional[str] = None,
    min_threat_score: float = 0,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get nation-state threats with optional filtering."""
    at = ThreatActorType(actor_type) if actor_type else None
    td = ThreatDomain(threat_domain) if threat_domain else None
    
    threats = geopolitical_engine.get_nation_state_threats(
        actor_type=at,
        target_country=target_country,
        threat_domain=td,
        min_threat_score=min_threat_score,
        limit=limit,
    )
    
    return {
        "threats": [
            {
                "threat_id": t.threat_id,
                "actor_name": t.actor_name,
                "actor_type": t.actor_type.value,
                "country_of_origin": t.country_of_origin,
                "target_countries": t.target_countries,
                "overall_threat_score": t.overall_threat_score,
                "capability_score": t.capability_score,
                "intent_score": t.intent_score,
                "confidence_level": t.confidence_level,
                "assessment_date": t.assessment_date.isoformat(),
            }
            for t in threats
        ],
        "count": len(threats),
    }


@router.post("/geopolitical/threats")
async def create_nation_state_threat(request: NationStateThreatRequest) -> Dict[str, Any]:
    """Create a nation-state threat assessment."""
    threat = geopolitical_engine.assess_nation_state_threat(
        actor_name=request.actor_name,
        actor_type=ThreatActorType(request.actor_type),
        country_of_origin=request.country_of_origin,
        target_countries=request.target_countries,
        threat_domains=[ThreatDomain(d) for d in request.threat_domains],
        capability_score=request.capability_score,
        intent_score=request.intent_score,
        known_operations=request.known_operations,
        attributed_attacks=request.attributed_attacks,
        sanctions_status=request.sanctions_status,
        alliance_affiliations=request.alliance_affiliations,
        resources_estimate=request.resources_estimate,
        confidence_level=request.confidence_level,
    )
    
    return {
        "threat_id": threat.threat_id,
        "actor_name": threat.actor_name,
        "overall_threat_score": threat.overall_threat_score,
        "created": True,
    }


@router.get("/geopolitical/sanctions")
async def get_sanctions_events(
    sanction_type: Optional[str] = None,
    target_country: Optional[str] = None,
    issuing_authority: Optional[str] = None,
    active_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get sanctions events with optional filtering."""
    st = SanctionType(sanction_type) if sanction_type else None
    
    events = geopolitical_engine.get_sanctions_events(
        sanction_type=st,
        target_country=target_country,
        issuing_authority=issuing_authority,
        active_only=active_only,
        limit=limit,
    )
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "sanction_type": e.sanction_type.value,
                "issuing_authority": e.issuing_authority,
                "target_country": e.target_country,
                "reason": e.reason,
                "is_active": e.is_active,
                "effective_date": e.effective_date.isoformat(),
            }
            for e in events
        ],
        "count": len(events),
    }


@router.post("/geopolitical/sanctions")
async def create_sanctions_event(request: SanctionsEventRequest) -> Dict[str, Any]:
    """Record a sanctions event."""
    event = geopolitical_engine.record_sanctions_event(
        sanction_type=SanctionType(request.sanction_type),
        issuing_authority=request.issuing_authority,
        reason=request.reason,
        target_country=request.target_country,
        target_entities=request.target_entities,
        target_individuals=request.target_individuals,
        economic_impact_estimate=request.economic_impact_estimate,
        compliance_requirements=request.compliance_requirements,
        sources=request.sources,
    )
    
    return {
        "event_id": event.event_id,
        "sanction_type": event.sanction_type.value,
        "target_country": event.target_country,
        "created": True,
    }


@router.get("/geopolitical/geo-economic")
async def get_geo_economic_risks(
    country: Optional[str] = None,
    region: Optional[str] = None,
    stability_level: Optional[str] = None,
    min_risk_score: float = 0,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get geo-economic risks with optional filtering."""
    sl = RegionStability(stability_level) if stability_level else None
    
    risks = geopolitical_engine.get_geo_economic_risks(
        country=country,
        region=region,
        stability_level=sl,
        min_risk_score=min_risk_score,
        limit=limit,
    )
    
    return {
        "risks": [
            {
                "risk_id": r.risk_id,
                "country": r.country,
                "region": r.region,
                "stability_level": r.stability_level.value,
                "overall_risk_score": r.overall_risk_score,
                "economic_risk_score": r.economic_risk_score,
                "political_risk_score": r.political_risk_score,
                "security_risk_score": r.security_risk_score,
                "assessment_date": r.assessment_date.isoformat(),
            }
            for r in risks
        ],
        "count": len(risks),
    }


@router.post("/geopolitical/geo-economic")
async def create_geo_economic_risk(request: GeoEconomicRiskRequest) -> Dict[str, Any]:
    """Create a geo-economic risk assessment."""
    risk = geopolitical_engine.assess_geo_economic_risk(
        country=request.country,
        region=request.region,
        economic_risk_score=request.economic_risk_score,
        political_risk_score=request.political_risk_score,
        security_risk_score=request.security_risk_score,
        gdp_growth_forecast=request.gdp_growth_forecast,
        inflation_rate=request.inflation_rate,
        currency_stability=request.currency_stability,
        trade_dependency_score=request.trade_dependency_score,
        debt_to_gdp_ratio=request.debt_to_gdp_ratio,
        foreign_investment_risk=request.foreign_investment_risk,
        supply_chain_vulnerability=request.supply_chain_vulnerability,
        key_risk_factors=request.key_risk_factors,
        opportunities=request.opportunities,
        forecast_horizon_months=request.forecast_horizon_months,
        confidence_level=request.confidence_level,
    )
    
    return {
        "risk_id": risk.risk_id,
        "country": risk.country,
        "stability_level": risk.stability_level.value,
        "overall_risk_score": risk.overall_risk_score,
        "created": True,
    }


@router.get("/geopolitical/summary")
async def get_global_risk_summary() -> Dict[str, Any]:
    """Get a summary of global geopolitical risks."""
    return geopolitical_engine.get_global_risk_summary()


@router.get("/geopolitical/metrics")
async def get_geopolitical_metrics() -> Dict[str, Any]:
    """Get geopolitical risk metrics."""
    return geopolitical_engine.get_metrics()


@router.get("/financial/fraud-patterns")
async def get_fraud_patterns(
    fraud_type: Optional[str] = None,
    risk_category: Optional[str] = None,
    min_amount: float = 0,
    investigation_status: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get fraud patterns with optional filtering."""
    ft = FraudType(fraud_type) if fraud_type else None
    rc = RiskCategory(risk_category) if risk_category else None
    
    patterns = financial_engine.get_fraud_patterns(
        fraud_type=ft,
        risk_category=rc,
        min_amount=min_amount,
        investigation_status=investigation_status,
        limit=limit,
    )
    
    return {
        "patterns": [
            {
                "pattern_id": p.pattern_id,
                "fraud_type": p.fraud_type.value,
                "name": p.name,
                "risk_category": p.risk_category.value,
                "risk_score": p.risk_score,
                "total_amount": p.total_amount,
                "currency": p.currency,
                "is_confirmed": p.is_confirmed,
                "investigation_status": p.investigation_status,
                "detected_at": p.detected_at.isoformat(),
            }
            for p in patterns
        ],
        "count": len(patterns),
    }


@router.post("/financial/fraud-patterns")
async def create_fraud_pattern(request: FraudPatternRequest) -> Dict[str, Any]:
    """Detect and record a fraud pattern."""
    pattern = financial_engine.detect_fraud_pattern(
        fraud_type=FraudType(request.fraud_type),
        name=request.name,
        description=request.description,
        entities_involved=request.entities_involved,
        transactions_involved=request.transactions_involved,
        total_amount=request.total_amount,
        currency=request.currency,
        detection_method=request.detection_method,
        indicators=[TransactionFlag(i) for i in request.indicators] if request.indicators else None,
        geographic_scope=request.geographic_scope,
        time_span_days=request.time_span_days,
        confidence_score=request.confidence_score,
    )
    
    return {
        "pattern_id": pattern.pattern_id,
        "fraud_type": pattern.fraud_type.value,
        "risk_category": pattern.risk_category.value,
        "risk_score": pattern.risk_score,
        "created": True,
    }


@router.get("/financial/crypto-wallets")
async def get_crypto_wallet_risks(
    blockchain: Optional[str] = None,
    risk_category: Optional[str] = None,
    min_risk_score: float = 0,
    has_indicator: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get crypto wallet risks with optional filtering."""
    rc = RiskCategory(risk_category) if risk_category else None
    hi = CryptoRiskIndicator(has_indicator) if has_indicator else None
    
    assessments = financial_engine.get_crypto_wallet_risks(
        blockchain=blockchain,
        risk_category=rc,
        min_risk_score=min_risk_score,
        has_indicator=hi,
        limit=limit,
    )
    
    return {
        "assessments": [
            {
                "assessment_id": a.assessment_id,
                "wallet_address": a.wallet_address,
                "blockchain": a.blockchain,
                "risk_category": a.risk_category.value,
                "risk_score": a.risk_score,
                "risk_indicators": [i.value for i in a.risk_indicators],
                "total_received": a.total_received,
                "total_sent": a.total_sent,
                "transaction_count": a.transaction_count,
                "assessment_date": a.assessment_date.isoformat(),
            }
            for a in assessments
        ],
        "count": len(assessments),
    }


@router.post("/financial/crypto-wallets")
async def create_crypto_wallet_risk(request: CryptoWalletRiskRequest) -> Dict[str, Any]:
    """Assess risk for a crypto wallet."""
    assessment = financial_engine.assess_crypto_wallet_risk(
        wallet_address=request.wallet_address,
        blockchain=request.blockchain,
        total_received=request.total_received,
        total_sent=request.total_sent,
        transaction_count=request.transaction_count,
        linked_wallets=request.linked_wallets,
        exchange_interactions=request.exchange_interactions,
        mixer_exposure=request.mixer_exposure,
        darknet_exposure=request.darknet_exposure,
        sanctions_exposure=request.sanctions_exposure,
        cluster_id=request.cluster_id,
        entity_attribution=request.entity_attribution,
    )
    
    return {
        "assessment_id": assessment.assessment_id,
        "wallet_address": assessment.wallet_address,
        "risk_category": assessment.risk_category.value,
        "risk_score": assessment.risk_score,
        "created": True,
    }


@router.get("/financial/transaction-anomalies")
async def get_transaction_anomalies(
    anomaly_type: Optional[str] = None,
    min_risk_score: float = 0,
    has_flag: Optional[str] = None,
    investigation_status: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get transaction anomalies with optional filtering."""
    hf = TransactionFlag(has_flag) if has_flag else None
    
    anomalies = financial_engine.get_transaction_anomalies(
        anomaly_type=anomaly_type,
        min_risk_score=min_risk_score,
        has_flag=hf,
        investigation_status=investigation_status,
        limit=limit,
    )
    
    return {
        "anomalies": [
            {
                "anomaly_id": a.anomaly_id,
                "transaction_id": a.transaction_id,
                "anomaly_type": a.anomaly_type,
                "risk_score": a.risk_score,
                "flags": [f.value for f in a.flags],
                "source_entity": a.source_entity,
                "destination_entity": a.destination_entity,
                "amount": a.amount,
                "currency": a.currency,
                "investigation_status": a.investigation_status,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in anomalies
        ],
        "count": len(anomalies),
    }


@router.post("/financial/transaction-anomalies")
async def create_transaction_anomaly(request: TransactionAnomalyRequest) -> Dict[str, Any]:
    """Detect and record a transaction anomaly."""
    anomaly = financial_engine.detect_transaction_anomaly(
        transaction_id=request.transaction_id,
        anomaly_type=request.anomaly_type,
        description=request.description,
        source_entity=request.source_entity,
        destination_entity=request.destination_entity,
        amount=request.amount,
        currency=request.currency,
        flags=[TransactionFlag(f) for f in request.flags] if request.flags else None,
        baseline_comparison=request.baseline_comparison,
        deviation_metrics=request.deviation_metrics,
        related_transactions=request.related_transactions,
    )
    
    return {
        "anomaly_id": anomaly.anomaly_id,
        "transaction_id": anomaly.transaction_id,
        "risk_score": anomaly.risk_score,
        "created": True,
    }


@router.get("/financial/networks")
async def get_money_flow_networks(
    min_risk_score: float = 0,
    min_nodes: int = 0,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get money flow networks with optional filtering."""
    networks = financial_engine.get_money_flow_networks(
        min_risk_score=min_risk_score,
        min_nodes=min_nodes,
        limit=limit,
    )
    
    return {
        "networks": [
            {
                "network_id": n.network_id,
                "name": n.name,
                "description": n.description,
                "node_count": len(n.nodes),
                "edge_count": len(n.edges),
                "total_value": n.total_value,
                "risk_score": n.risk_score,
                "created_at": n.created_at.isoformat(),
            }
            for n in networks
        ],
        "count": len(networks),
    }


@router.post("/financial/networks")
async def create_money_flow_network(request: MoneyFlowNetworkRequest) -> Dict[str, Any]:
    """Create a new money flow network."""
    network = financial_engine.create_money_flow_network(
        name=request.name,
        description=request.description,
    )
    
    return {
        "network_id": network.network_id,
        "name": network.name,
        "created": True,
    }


@router.post("/financial/networks/{network_id}/nodes")
async def add_network_node(network_id: str, request: NetworkNodeRequest) -> Dict[str, Any]:
    """Add a node to a money flow network."""
    node = financial_engine.add_network_node(
        network_id=network_id,
        entity_id=request.entity_id,
        entity_type=EntityType(request.entity_type),
        entity_name=request.entity_name,
        risk_score=request.risk_score,
        total_inflow=request.total_inflow,
        total_outflow=request.total_outflow,
        transaction_count=request.transaction_count,
        flags=[TransactionFlag(f) for f in request.flags] if request.flags else None,
    )
    
    if not node:
        raise HTTPException(status_code=404, detail="Network not found")
    
    return {
        "node_id": node.node_id,
        "entity_id": node.entity_id,
        "created": True,
    }


@router.post("/financial/networks/{network_id}/edges")
async def add_network_edge(network_id: str, request: NetworkEdgeRequest) -> Dict[str, Any]:
    """Add an edge to a money flow network."""
    edge = financial_engine.add_network_edge(
        network_id=network_id,
        source_node=request.source_node,
        target_node=request.target_node,
        total_amount=request.total_amount,
        transaction_count=request.transaction_count,
        currency=request.currency,
        flags=[TransactionFlag(f) for f in request.flags] if request.flags else None,
    )
    
    if not edge:
        raise HTTPException(status_code=404, detail="Network or nodes not found")
    
    return {
        "edge_id": edge.edge_id,
        "source_node": edge.source_node,
        "target_node": edge.target_node,
        "created": True,
    }


@router.get("/financial/networks/{network_id}/analysis")
async def analyze_network(network_id: str) -> Dict[str, Any]:
    """Analyze a money flow network for patterns."""
    analysis = financial_engine.analyze_network(network_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Network not found")
    
    return analysis


@router.get("/financial/metrics")
async def get_financial_metrics() -> Dict[str, Any]:
    """Get financial crime intelligence metrics."""
    return financial_engine.get_metrics()


@router.get("/fusion/stability-score")
async def get_latest_stability_score() -> Dict[str, Any]:
    """Get the most recent National Stability Score."""
    nss = fusion_engine.get_latest_stability_score()
    
    if not nss:
        return {"message": "No stability score calculated yet"}
    
    return {
        "assessment_id": nss.assessment_id,
        "timestamp": nss.timestamp.isoformat(),
        "overall_score": nss.overall_score,
        "stability_level": nss.stability_level.value,
        "trend": nss.trend.value,
        "confidence_level": nss.confidence_level,
        "key_drivers": nss.key_drivers,
        "recommendations": nss.recommendations,
        "forecast_24h": nss.forecast_24h,
        "forecast_7d": nss.forecast_7d,
        "forecast_30d": nss.forecast_30d,
    }


@router.post("/fusion/stability-score")
async def calculate_stability_score(request: NationalStabilityScoreRequest) -> Dict[str, Any]:
    """Calculate a new National Stability Score."""
    domain_scores = {}
    for domain_str, scores in request.domain_scores.items():
        domain = RiskDomain(domain_str)
        domain_scores[domain] = (scores.get("score", 50), scores.get("confidence", 0.8))
    
    nss = fusion_engine.calculate_national_stability_score(
        domain_scores=domain_scores,
        fusion_method=FusionMethod(request.fusion_method),
    )
    
    return {
        "assessment_id": nss.assessment_id,
        "overall_score": nss.overall_score,
        "stability_level": nss.stability_level.value,
        "trend": nss.trend.value,
        "key_drivers": nss.key_drivers,
        "recommendations": nss.recommendations,
        "created": True,
    }


@router.post("/fusion/risk-fusion")
async def perform_risk_fusion(request: RiskFusionRequest) -> Dict[str, Any]:
    """Perform multi-domain risk fusion analysis."""
    domain_scores = {RiskDomain(k): v for k, v in request.domain_scores.items()}
    
    result = fusion_engine.perform_risk_fusion(
        domain_scores=domain_scores,
        fusion_method=FusionMethod(request.fusion_method),
    )
    
    return {
        "fusion_id": result.fusion_id,
        "fused_score": result.fused_score,
        "confidence": result.confidence,
        "correlations": result.correlations,
        "amplification_factors": result.amplification_factors,
        "mitigation_factors": result.mitigation_factors,
        "cross_domain_patterns": result.cross_domain_patterns,
        "anomalies_detected": result.anomalies_detected,
    }


@router.get("/fusion/early-warnings")
async def get_early_warnings(
    urgency: Optional[str] = None,
    domain: Optional[str] = None,
    active_only: bool = False,
    min_risk_score: float = 0,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get early warning signals with optional filtering."""
    urg = AlertUrgency(urgency) if urgency else None
    dom = RiskDomain(domain) if domain else None
    
    warnings = fusion_engine.get_early_warnings(
        urgency=urg,
        domain=dom,
        active_only=active_only,
        min_risk_score=min_risk_score,
        limit=limit,
    )
    
    return {
        "warnings": [
            {
                "signal_id": w.signal_id,
                "title": w.title,
                "description": w.description,
                "urgency": w.urgency.value,
                "domains_affected": [d.value for d in w.domains_affected],
                "risk_score": w.risk_score,
                "probability": w.probability,
                "time_horizon_hours": w.time_horizon_hours,
                "is_active": w.is_active,
                "acknowledged": w.acknowledged,
                "created_at": w.created_at.isoformat(),
                "expires_at": w.expires_at.isoformat(),
            }
            for w in warnings
        ],
        "count": len(warnings),
    }


@router.post("/fusion/early-warnings")
async def create_early_warning(request: EarlyWarningRequest) -> Dict[str, Any]:
    """Generate an early warning signal."""
    warning = fusion_engine.generate_early_warning(
        title=request.title,
        description=request.description,
        urgency=AlertUrgency(request.urgency),
        domains_affected=[RiskDomain(d) for d in request.domains_affected],
        risk_score=request.risk_score,
        probability=request.probability,
        time_horizon_hours=request.time_horizon_hours,
        indicators=request.indicators,
        potential_impacts=request.potential_impacts,
        recommended_actions=request.recommended_actions,
        source_signals=request.source_signals,
        confidence_level=request.confidence_level,
    )
    
    return {
        "signal_id": warning.signal_id,
        "title": warning.title,
        "urgency": warning.urgency.value,
        "risk_score": warning.risk_score,
        "created": True,
    }


@router.post("/fusion/early-warnings/{signal_id}/acknowledge")
async def acknowledge_early_warning(
    signal_id: str,
    acknowledged_by: str,
) -> Dict[str, Any]:
    """Acknowledge an early warning signal."""
    success = fusion_engine.acknowledge_warning(signal_id, acknowledged_by)
    
    if not success:
        raise HTTPException(status_code=404, detail="Warning not found")
    
    return {"acknowledged": True}


@router.post("/fusion/trend-predictions")
async def create_trend_prediction(request: TrendPredictionRequest) -> Dict[str, Any]:
    """Create a trend prediction for a domain."""
    prediction = fusion_engine.create_trend_prediction(
        domain=RiskDomain(request.domain),
        current_score=request.current_score,
        prediction_horizon_hours=request.prediction_horizon_hours,
        key_factors=request.key_factors,
    )
    
    return {
        "prediction_id": prediction.prediction_id,
        "domain": prediction.domain.value,
        "current_score": prediction.current_score,
        "predicted_score": prediction.predicted_score,
        "trend_direction": prediction.trend_direction.value,
        "confidence": prediction.confidence,
        "scenarios": prediction.scenarios,
    }


@router.get("/fusion/timeline")
async def get_fusion_timeline(
    domain: Optional[str] = None,
    min_severity: float = 0,
    hours: int = 24,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get fusion events timeline."""
    dom = RiskDomain(domain) if domain else None
    
    events = fusion_engine.get_fusion_timeline(
        domain=dom,
        min_severity=min_severity,
        hours=hours,
        limit=limit,
    )
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "domain": e.domain.value,
                "severity": e.severity,
                "description": e.description,
                "impact_assessment": e.impact_assessment,
            }
            for e in events
        ],
        "count": len(events),
    }


@router.get("/fusion/metrics")
async def get_fusion_metrics() -> Dict[str, Any]:
    """Get national risk fusion metrics."""
    return fusion_engine.get_metrics()


@router.get("/alerts")
async def get_security_alerts(
    priority: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    destination: Optional[str] = None,
    min_risk_score: float = 0,
    active_only: bool = False,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get security alerts with optional filtering."""
    from app.national_security.national_security_alerts import AlertStatus
    
    pri = AlertPriority(priority) if priority else None
    cat = AlertCategory(category) if category else None
    stat = AlertStatus(status) if status else None
    dest = AlertDestination(destination) if destination else None
    
    alerts = alert_manager.get_alerts(
        priority=pri,
        category=cat,
        status=stat,
        destination=dest,
        min_risk_score=min_risk_score,
        active_only=active_only,
        limit=limit,
    )
    
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "title": a.title,
                "description": a.description,
                "priority": a.priority.value,
                "category": a.category.value,
                "status": a.status.value,
                "risk_score": a.risk_score,
                "escalation_level": a.escalation_level.value,
                "destinations": [d.value for d in a.destinations],
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
            }
            for a in alerts
        ],
        "count": len(alerts),
    }


@router.post("/alerts")
async def create_security_alert(request: SecurityAlertRequest) -> Dict[str, Any]:
    """Create a new security alert."""
    alert = alert_manager.create_alert(
        title=request.title,
        description=request.description,
        priority=AlertPriority(request.priority),
        category=AlertCategory(request.category),
        risk_score=request.risk_score,
        source_module=request.source_module,
        source_signal_id=request.source_signal_id,
        affected_domains=request.affected_domains,
        expires_in_hours=request.expires_in_hours,
        related_alerts=request.related_alerts,
        attachments=request.attachments,
        metadata=request.metadata,
    )
    
    return {
        "alert_id": alert.alert_id,
        "title": alert.title,
        "priority": alert.priority.value,
        "status": alert.status.value,
        "destinations": [d.value for d in alert.destinations],
        "created": True,
    }


@router.get("/alerts/{alert_id}")
async def get_security_alert(alert_id: str) -> Dict[str, Any]:
    """Get a specific security alert."""
    alert = alert_manager.get_alert(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "alert_id": alert.alert_id,
        "title": alert.title,
        "description": alert.description,
        "priority": alert.priority.value,
        "category": alert.category.value,
        "status": alert.status.value,
        "risk_score": alert.risk_score,
        "source_module": alert.source_module,
        "affected_domains": alert.affected_domains,
        "destinations": [d.value for d in alert.destinations],
        "escalation_level": alert.escalation_level.value,
        "actions_taken": alert.actions_taken,
        "created_at": alert.created_at.isoformat(),
        "updated_at": alert.updated_at.isoformat(),
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolved_by": alert.resolved_by,
        "resolution_notes": alert.resolution_notes,
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_security_alert(
    alert_id: str,
    acknowledged_by: str,
    actor_name: str = "",
) -> Dict[str, Any]:
    """Acknowledge a security alert."""
    success = alert_manager.acknowledge_alert(alert_id, acknowledged_by, actor_name)
    
    if not success:
        raise HTTPException(status_code=400, detail="Alert not found or already acknowledged")
    
    return {"acknowledged": True}


@router.post("/alerts/{alert_id}/escalate")
async def escalate_security_alert(
    alert_id: str,
    escalated_by: str,
    actor_name: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    """Escalate a security alert."""
    success = alert_manager.escalate_alert(alert_id, escalated_by, actor_name, reason)
    
    if not success:
        raise HTTPException(status_code=400, detail="Alert not found or cannot be escalated further")
    
    return {"escalated": True}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    resolved_by: str,
    actor_name: str = "",
    resolution_notes: str = "",
) -> Dict[str, Any]:
    """Resolve a security alert."""
    success = alert_manager.resolve_alert(alert_id, resolved_by, actor_name, resolution_notes)
    
    if not success:
        raise HTTPException(status_code=400, detail="Alert not found or already resolved")
    
    return {"resolved": True}


@router.post("/alerts/{alert_id}/close")
async def close_security_alert(
    alert_id: str,
    closed_by: str,
    actor_name: str = "",
    close_reason: str = "",
) -> Dict[str, Any]:
    """Close a security alert."""
    success = alert_manager.close_alert(alert_id, closed_by, actor_name, close_reason)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"closed": True}


@router.get("/alerts/statistics")
async def get_alert_statistics() -> Dict[str, Any]:
    """Get alert statistics."""
    return alert_manager.get_alert_statistics()


@router.get("/alerts/subscriptions")
async def get_alert_subscriptions(
    subscriber_id: Optional[str] = None,
    active_only: bool = False,
) -> Dict[str, Any]:
    """Get alert subscriptions."""
    subscriptions = alert_manager.get_subscriptions(
        subscriber_id=subscriber_id,
        active_only=active_only,
    )
    
    return {
        "subscriptions": [
            {
                "subscription_id": s.subscription_id,
                "subscriber_id": s.subscriber_id,
                "subscriber_name": s.subscriber_name,
                "subscriber_role": s.subscriber_role,
                "categories": [c.value for c in s.categories],
                "min_priority": s.min_priority.value,
                "is_active": s.is_active,
            }
            for s in subscriptions
        ],
        "count": len(subscriptions),
    }


@router.post("/alerts/subscriptions")
async def create_alert_subscription(request: AlertSubscriptionRequest) -> Dict[str, Any]:
    """Create an alert subscription."""
    subscription = alert_manager.create_subscription(
        subscriber_id=request.subscriber_id,
        subscriber_name=request.subscriber_name,
        subscriber_role=request.subscriber_role,
        categories=[AlertCategory(c) for c in request.categories],
        min_priority=AlertPriority(request.min_priority),
        destinations=[AlertDestination(d) for d in request.destinations] if request.destinations else None,
        notification_methods=request.notification_methods,
    )
    
    return {
        "subscription_id": subscription.subscription_id,
        "subscriber_id": subscription.subscriber_id,
        "created": True,
    }


@router.get("/alerts/routing-rules")
async def get_routing_rules(active_only: bool = False) -> Dict[str, Any]:
    """Get alert routing rules."""
    rules = alert_manager.get_routing_rules(active_only=active_only)
    
    return {
        "rules": [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "conditions": r.conditions,
                "destinations": [d.value for d in r.destinations],
                "auto_escalate": r.auto_escalate,
                "is_active": r.is_active,
            }
            for r in rules
        ],
        "count": len(rules),
    }


@router.post("/alerts/routing-rules")
async def create_routing_rule(request: RoutingRuleRequest) -> Dict[str, Any]:
    """Create an alert routing rule."""
    rule = alert_manager.create_routing_rule(
        name=request.name,
        description=request.description,
        conditions=request.conditions,
        destinations=[AlertDestination(d) for d in request.destinations],
        priority_override=AlertPriority(request.priority_override) if request.priority_override else None,
        auto_escalate=request.auto_escalate,
        escalation_delay_minutes=request.escalation_delay_minutes,
    )
    
    return {
        "rule_id": rule.rule_id,
        "name": rule.name,
        "created": True,
    }


@router.get("/alerts/audit-log")
async def get_alert_audit_log(
    alert_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(100, le=500),
) -> Dict[str, Any]:
    """Get alert audit log entries."""
    entries = alert_manager.get_audit_log(
        alert_id=alert_id,
        actor_id=actor_id,
        action=action,
        limit=limit,
    )
    
    return {
        "entries": [
            {
                "entry_id": e.entry_id,
                "alert_id": e.alert_id,
                "action": e.action,
                "actor_id": e.actor_id,
                "actor_name": e.actor_name,
                "timestamp": e.timestamp.isoformat(),
                "details": e.details,
            }
            for e in entries
        ],
        "count": len(entries),
    }


@router.get("/alerts/metrics")
async def get_alert_metrics() -> Dict[str, Any]:
    """Get alert manager metrics."""
    return alert_manager.get_metrics()


@router.get("/metrics")
async def get_all_metrics() -> Dict[str, Any]:
    """Get combined metrics from all AI-NSE modules."""
    return {
        "cyber_intel": cyber_engine.get_metrics(),
        "insider_threat": insider_engine.get_metrics(),
        "geopolitical_risk": geopolitical_engine.get_metrics(),
        "financial_crime": financial_engine.get_metrics(),
        "national_risk_fusion": fusion_engine.get_metrics(),
        "security_alerts": alert_manager.get_metrics(),
    }
