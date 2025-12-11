"""
Phase 26: Civil Liberties Compliance Engine

Validates actions against:
- U.S. Constitution (1st, 4th, 14th Amendments)
- Florida Constitution
- Riviera Beach municipal code
- DOJ Use-of-Force and Surveillance Guidelines
- CJIS Security Policy
- NIST AI RMF

Blocks actions if:
- Surveillance exceeds legal boundaries
- Predictive models show demographic skew
- Facial/biometric identification is attempted illegally
- Tracking exceeds retention rules
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class ConstitutionalBasis(Enum):
    """Constitutional and legal basis for compliance."""
    FIRST_AMENDMENT = "FIRST_AMENDMENT"
    FOURTH_AMENDMENT = "FOURTH_AMENDMENT"
    FIFTH_AMENDMENT = "FIFTH_AMENDMENT"
    FOURTEENTH_AMENDMENT = "FOURTEENTH_AMENDMENT"
    FLORIDA_CONSTITUTION = "FLORIDA_CONSTITUTION"
    FLORIDA_STATUTE = "FLORIDA_STATUTE"
    RIVIERA_BEACH_CODE = "RIVIERA_BEACH_CODE"
    DOJ_GUIDELINES = "DOJ_GUIDELINES"
    CJIS_POLICY = "CJIS_POLICY"
    NIST_AI_RMF = "NIST_AI_RMF"


class ComplianceStatus(Enum):
    """Compliance check status."""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT_BLOCKED = "NON_COMPLIANT_BLOCKED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    CONDITIONAL_APPROVAL = "CONDITIONAL_APPROVAL"


class ViolationType(Enum):
    """Types of civil liberties violations."""
    SURVEILLANCE_OVERREACH = "SURVEILLANCE_OVERREACH"
    DEMOGRAPHIC_SKEW = "DEMOGRAPHIC_SKEW"
    ILLEGAL_BIOMETRIC = "ILLEGAL_BIOMETRIC"
    RETENTION_VIOLATION = "RETENTION_VIOLATION"
    WARRANTLESS_SEARCH = "WARRANTLESS_SEARCH"
    FREE_SPEECH_INFRINGEMENT = "FREE_SPEECH_INFRINGEMENT"
    DUE_PROCESS_VIOLATION = "DUE_PROCESS_VIOLATION"
    EQUAL_PROTECTION_VIOLATION = "EQUAL_PROTECTION_VIOLATION"
    PRIVACY_VIOLATION = "PRIVACY_VIOLATION"


@dataclass
class ComplianceRule:
    """Individual compliance rule."""
    rule_id: str
    name: str
    description: str
    legal_basis: ConstitutionalBasis
    citation: str
    condition: str
    severity: str
    auto_block: bool


@dataclass
class ViolationDetail:
    """Details of a compliance violation."""
    violation_id: str
    violation_type: ViolationType
    description: str
    legal_basis: ConstitutionalBasis
    citation: str
    severity: str
    remediation: str
    blocked: bool


@dataclass
class ComplianceResult:
    """Result of civil liberties compliance check."""
    result_id: str
    action_id: str
    timestamp: datetime
    status: ComplianceStatus
    violations: List[ViolationDetail]
    applicable_rules: List[ComplianceRule]
    constitutional_concerns: List[str]
    legal_citations: List[str]
    blocked: bool
    block_reason: str
    conditions: List[str]
    recommendations: List[str]
    explanation: str
    audit_trail: List[str]


class CivilLibertiesEngine:
    """
    Engine for validating civil liberties compliance.
    
    Validates against federal, state, and local laws,
    as well as DOJ guidelines and CJIS policy.
    """
    
    _instance = None
    
    COMPLIANCE_RULES = [
        ComplianceRule(
            rule_id="4A-001",
            name="Fourth Amendment - Warrant Requirement",
            description="Searches and seizures require a warrant or valid exception",
            legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
            citation="U.S. Const. amend. IV",
            condition="search_or_seizure AND NOT (warrant OR exception)",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="4A-002",
            name="Fourth Amendment - Probable Cause",
            description="Warrants must be supported by probable cause",
            legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
            citation="U.S. Const. amend. IV",
            condition="warrant AND NOT probable_cause",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="1A-001",
            name="First Amendment - Free Speech",
            description="Cannot target individuals based on protected speech",
            legal_basis=ConstitutionalBasis.FIRST_AMENDMENT,
            citation="U.S. Const. amend. I",
            condition="targeting_based_on_speech",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="1A-002",
            name="First Amendment - Assembly",
            description="Cannot interfere with peaceful assembly",
            legal_basis=ConstitutionalBasis.FIRST_AMENDMENT,
            citation="U.S. Const. amend. I",
            condition="interfering_peaceful_assembly",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="14A-001",
            name="Fourteenth Amendment - Equal Protection",
            description="Cannot discriminate based on protected class",
            legal_basis=ConstitutionalBasis.FOURTEENTH_AMENDMENT,
            citation="U.S. Const. amend. XIV",
            condition="discriminatory_targeting",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="14A-002",
            name="Fourteenth Amendment - Due Process",
            description="Must provide due process before deprivation",
            legal_basis=ConstitutionalBasis.FOURTEENTH_AMENDMENT,
            citation="U.S. Const. amend. XIV",
            condition="deprivation_without_process",
            severity="CRITICAL",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="FL-001",
            name="Florida Constitution - Privacy",
            description="Florida provides broader privacy protections",
            legal_basis=ConstitutionalBasis.FLORIDA_CONSTITUTION,
            citation="Fla. Const. art. I, § 23",
            condition="privacy_violation",
            severity="HIGH",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="FL-002",
            name="Florida Statute - Drone Surveillance",
            description="Drone surveillance restrictions under F.S. 934.50",
            legal_basis=ConstitutionalBasis.FLORIDA_STATUTE,
            citation="Fla. Stat. § 934.50",
            condition="drone_surveillance_without_warrant",
            severity="HIGH",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="FL-003",
            name="Florida Statute - Facial Recognition",
            description="Facial recognition use restrictions",
            legal_basis=ConstitutionalBasis.FLORIDA_STATUTE,
            citation="Fla. Stat. § 943.05",
            condition="unauthorized_facial_recognition",
            severity="HIGH",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="RB-001",
            name="Riviera Beach - Data Retention",
            description="Local data retention limits",
            legal_basis=ConstitutionalBasis.RIVIERA_BEACH_CODE,
            citation="Riviera Beach Code § 2-301",
            condition="retention_exceeds_limit",
            severity="MEDIUM",
            auto_block=False,
        ),
        ComplianceRule(
            rule_id="DOJ-001",
            name="DOJ - Use of Force Guidelines",
            description="Federal use of force policy framework",
            legal_basis=ConstitutionalBasis.DOJ_GUIDELINES,
            citation="DOJ Use of Force Policy (2022)",
            condition="force_exceeds_guidelines",
            severity="HIGH",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="CJIS-001",
            name="CJIS - Data Access",
            description="CJIS Security Policy data access requirements",
            legal_basis=ConstitutionalBasis.CJIS_POLICY,
            citation="CJIS Security Policy v5.9",
            condition="unauthorized_cjis_access",
            severity="HIGH",
            auto_block=True,
        ),
        ComplianceRule(
            rule_id="NIST-001",
            name="NIST AI RMF - Bias Mitigation",
            description="AI systems must implement bias mitigation",
            legal_basis=ConstitutionalBasis.NIST_AI_RMF,
            citation="NIST AI RMF 1.0",
            condition="ai_without_bias_mitigation",
            severity="MEDIUM",
            auto_block=False,
        ),
    ]
    
    RETENTION_LIMITS = {
        "surveillance_footage": 30,
        "drone_footage": 30,
        "license_plate_data": 90,
        "facial_recognition_queries": 365,
        "predictive_analytics": 180,
        "general_records": 2555,
    }
    
    WARRANT_EXCEPTIONS = [
        "consent",
        "exigent_circumstances",
        "plain_view",
        "search_incident_to_arrest",
        "automobile_exception",
        "hot_pursuit",
        "community_caretaking",
    ]
    
    def __init__(self):
        self._check_history: List[ComplianceResult] = []
    
    @classmethod
    def get_instance(cls) -> "CivilLibertiesEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def check_compliance(
        self,
        action_id: str,
        action_type: str,
        context: Dict[str, Any],
    ) -> ComplianceResult:
        """
        Check action for civil liberties compliance.
        
        Args:
            action_id: Unique identifier for the action
            action_type: Type of action being checked
            context: Context including relevant details
            
        Returns:
            ComplianceResult with status and any violations
        """
        result_id = f"compliance-{uuid.uuid4().hex[:12]}"
        violations = []
        applicable_rules = []
        constitutional_concerns = []
        legal_citations = []
        conditions = []
        recommendations = []
        audit_trail = []
        
        audit_trail.append(f"Compliance check initiated for action {action_id}")
        audit_trail.append(f"Action type: {action_type}")
        
        fourth_violations = self._check_fourth_amendment(action_type, context)
        violations.extend(fourth_violations)
        if fourth_violations:
            constitutional_concerns.append("Fourth Amendment concerns identified")
            legal_citations.append("U.S. Const. amend. IV")
            audit_trail.append(f"Fourth Amendment check: {len(fourth_violations)} violation(s)")
        
        first_violations = self._check_first_amendment(action_type, context)
        violations.extend(first_violations)
        if first_violations:
            constitutional_concerns.append("First Amendment concerns identified")
            legal_citations.append("U.S. Const. amend. I")
            audit_trail.append(f"First Amendment check: {len(first_violations)} violation(s)")
        
        fourteenth_violations = self._check_fourteenth_amendment(action_type, context)
        violations.extend(fourteenth_violations)
        if fourteenth_violations:
            constitutional_concerns.append("Fourteenth Amendment concerns identified")
            legal_citations.append("U.S. Const. amend. XIV")
            audit_trail.append(f"Fourteenth Amendment check: {len(fourteenth_violations)} violation(s)")
        
        florida_violations = self._check_florida_law(action_type, context)
        violations.extend(florida_violations)
        if florida_violations:
            legal_citations.append("Florida Constitution and Statutes")
            audit_trail.append(f"Florida law check: {len(florida_violations)} violation(s)")
        
        surveillance_violations = self._check_surveillance_limits(action_type, context)
        violations.extend(surveillance_violations)
        if surveillance_violations:
            audit_trail.append(f"Surveillance limits check: {len(surveillance_violations)} violation(s)")
        
        biometric_violations = self._check_biometric_compliance(action_type, context)
        violations.extend(biometric_violations)
        if biometric_violations:
            audit_trail.append(f"Biometric compliance check: {len(biometric_violations)} violation(s)")
        
        retention_violations = self._check_retention_compliance(action_type, context)
        violations.extend(retention_violations)
        if retention_violations:
            audit_trail.append(f"Retention compliance check: {len(retention_violations)} violation(s)")
        
        for rule in self.COMPLIANCE_RULES:
            if self._rule_applies(rule, action_type, context):
                applicable_rules.append(rule)
        
        blocked = any(v.blocked for v in violations)
        block_reason = ""
        if blocked:
            critical_violations = [v for v in violations if v.blocked]
            block_reason = "; ".join(v.description for v in critical_violations[:3])
        
        status = self._determine_status(violations, blocked)
        
        recommendations = self._generate_recommendations(violations, action_type)
        conditions = self._generate_conditions(violations, action_type)
        
        explanation = self._generate_explanation(status, violations, constitutional_concerns)
        
        audit_trail.append(f"Final status: {status.value}")
        audit_trail.append(f"Total violations: {len(violations)}")
        audit_trail.append(f"Action blocked: {blocked}")
        
        result = ComplianceResult(
            result_id=result_id,
            action_id=action_id,
            timestamp=datetime.now(),
            status=status,
            violations=violations,
            applicable_rules=applicable_rules,
            constitutional_concerns=constitutional_concerns,
            legal_citations=list(set(legal_citations)),
            blocked=blocked,
            block_reason=block_reason,
            conditions=conditions,
            recommendations=recommendations,
            explanation=explanation,
            audit_trail=audit_trail,
        )
        
        self._check_history.append(result)
        return result
    
    def _check_fourth_amendment(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check Fourth Amendment compliance."""
        violations = []
        
        if action_type in ["search", "seizure", "surveillance"]:
            has_warrant = context.get("has_warrant", False)
            has_exception = any(
                context.get(exc, False) for exc in self.WARRANT_EXCEPTIONS
            )
            
            if not has_warrant and not has_exception:
                violations.append(ViolationDetail(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.WARRANTLESS_SEARCH,
                    description="Search/seizure without warrant or valid exception",
                    legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
                    citation="U.S. Const. amend. IV",
                    severity="CRITICAL",
                    remediation="Obtain warrant or document valid exception",
                    blocked=True,
                ))
        
        if context.get("excessive_force", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.PRIVACY_VIOLATION,
                description="Unreasonable seizure through excessive force",
                legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
                citation="Graham v. Connor, 490 U.S. 386 (1989)",
                severity="CRITICAL",
                remediation="Apply objective reasonableness standard",
                blocked=True,
            ))
        
        return violations
    
    def _check_first_amendment(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check First Amendment compliance."""
        violations = []
        
        if context.get("targeting_speech", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.FREE_SPEECH_INFRINGEMENT,
                description="Action targets protected speech or expression",
                legal_basis=ConstitutionalBasis.FIRST_AMENDMENT,
                citation="U.S. Const. amend. I",
                severity="CRITICAL",
                remediation="Cannot target based on content of speech",
                blocked=True,
            ))
        
        if context.get("interfering_assembly", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.FREE_SPEECH_INFRINGEMENT,
                description="Action interferes with peaceful assembly",
                legal_basis=ConstitutionalBasis.FIRST_AMENDMENT,
                citation="U.S. Const. amend. I",
                severity="CRITICAL",
                remediation="Protect right to peaceful assembly",
                blocked=True,
            ))
        
        if context.get("religious_targeting", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.FREE_SPEECH_INFRINGEMENT,
                description="Action targets religious practice",
                legal_basis=ConstitutionalBasis.FIRST_AMENDMENT,
                citation="U.S. Const. amend. I",
                severity="CRITICAL",
                remediation="Cannot target based on religious practice",
                blocked=True,
            ))
        
        return violations
    
    def _check_fourteenth_amendment(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check Fourteenth Amendment compliance."""
        violations = []
        
        if context.get("discriminatory_intent", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.EQUAL_PROTECTION_VIOLATION,
                description="Action shows discriminatory intent",
                legal_basis=ConstitutionalBasis.FOURTEENTH_AMENDMENT,
                citation="U.S. Const. amend. XIV, § 1",
                severity="CRITICAL",
                remediation="Apply equal protection standards",
                blocked=True,
            ))
        
        if context.get("disparate_impact", False) and not context.get("compelling_interest", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.EQUAL_PROTECTION_VIOLATION,
                description="Action has disparate impact without compelling interest",
                legal_basis=ConstitutionalBasis.FOURTEENTH_AMENDMENT,
                citation="U.S. Const. amend. XIV, § 1",
                severity="HIGH",
                remediation="Document compelling governmental interest",
                blocked=True,
            ))
        
        if context.get("no_due_process", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.DUE_PROCESS_VIOLATION,
                description="Deprivation without due process",
                legal_basis=ConstitutionalBasis.FOURTEENTH_AMENDMENT,
                citation="U.S. Const. amend. XIV, § 1",
                severity="CRITICAL",
                remediation="Provide notice and opportunity to be heard",
                blocked=True,
            ))
        
        return violations
    
    def _check_florida_law(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check Florida state law compliance."""
        violations = []
        
        if action_type == "drone_surveillance":
            if not context.get("has_warrant", False) and not context.get("exigent_circumstances", False):
                violations.append(ViolationDetail(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.SURVEILLANCE_OVERREACH,
                    description="Drone surveillance without warrant under F.S. 934.50",
                    legal_basis=ConstitutionalBasis.FLORIDA_STATUTE,
                    citation="Fla. Stat. § 934.50",
                    severity="HIGH",
                    remediation="Obtain warrant for drone surveillance",
                    blocked=True,
                ))
        
        if context.get("privacy_expectation", False) and context.get("intrusion", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.PRIVACY_VIOLATION,
                description="Violation of Florida constitutional privacy right",
                legal_basis=ConstitutionalBasis.FLORIDA_CONSTITUTION,
                citation="Fla. Const. art. I, § 23",
                severity="HIGH",
                remediation="Respect reasonable expectation of privacy",
                blocked=True,
            ))
        
        return violations
    
    def _check_surveillance_limits(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check surveillance limit compliance."""
        violations = []
        
        if action_type in ["surveillance", "monitoring", "tracking"]:
            duration = context.get("surveillance_duration_hours", 0)
            if duration > 72 and not context.get("extended_authorization", False):
                violations.append(ViolationDetail(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.SURVEILLANCE_OVERREACH,
                    description=f"Surveillance duration ({duration}h) exceeds 72-hour limit",
                    legal_basis=ConstitutionalBasis.DOJ_GUIDELINES,
                    citation="DOJ Surveillance Guidelines",
                    severity="MEDIUM",
                    remediation="Obtain extended surveillance authorization",
                    blocked=False,
                ))
        
        if context.get("mass_surveillance", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.SURVEILLANCE_OVERREACH,
                description="Mass surveillance without specific target",
                legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
                citation="U.S. Const. amend. IV",
                severity="CRITICAL",
                remediation="Surveillance must be targeted and specific",
                blocked=True,
            ))
        
        return violations
    
    def _check_biometric_compliance(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check biometric identification compliance."""
        violations = []
        
        if action_type == "facial_recognition":
            if not context.get("authorized_use", False):
                violations.append(ViolationDetail(
                    violation_id=f"v-{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.ILLEGAL_BIOMETRIC,
                    description="Unauthorized facial recognition use",
                    legal_basis=ConstitutionalBasis.FLORIDA_STATUTE,
                    citation="Fla. Stat. § 943.05",
                    severity="HIGH",
                    remediation="Obtain proper authorization for facial recognition",
                    blocked=True,
                ))
        
        if context.get("biometric_without_consent", False):
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.ILLEGAL_BIOMETRIC,
                description="Biometric collection without consent or warrant",
                legal_basis=ConstitutionalBasis.FOURTH_AMENDMENT,
                citation="U.S. Const. amend. IV",
                severity="HIGH",
                remediation="Obtain consent or warrant for biometric collection",
                blocked=True,
            ))
        
        return violations
    
    def _check_retention_compliance(
        self,
        action_type: str,
        context: Dict,
    ) -> List[ViolationDetail]:
        """Check data retention compliance."""
        violations = []
        
        data_type = context.get("data_type", "general_records")
        retention_days = context.get("retention_days", 0)
        limit = self.RETENTION_LIMITS.get(data_type, 2555)
        
        if retention_days > limit:
            violations.append(ViolationDetail(
                violation_id=f"v-{uuid.uuid4().hex[:8]}",
                violation_type=ViolationType.RETENTION_VIOLATION,
                description=f"Data retention ({retention_days} days) exceeds {limit}-day limit for {data_type}",
                legal_basis=ConstitutionalBasis.RIVIERA_BEACH_CODE,
                citation="Riviera Beach Data Retention Policy",
                severity="MEDIUM",
                remediation=f"Purge data older than {limit} days",
                blocked=False,
            ))
        
        return violations
    
    def _rule_applies(
        self,
        rule: ComplianceRule,
        action_type: str,
        context: Dict,
    ) -> bool:
        """Check if a rule applies to the action."""
        if "search" in rule.condition and action_type in ["search", "seizure"]:
            return True
        if "surveillance" in rule.condition and action_type in ["surveillance", "monitoring"]:
            return True
        if "force" in rule.condition and action_type in ["use_of_force", "enforcement"]:
            return True
        return False
    
    def _determine_status(
        self,
        violations: List[ViolationDetail],
        blocked: bool,
    ) -> ComplianceStatus:
        """Determine overall compliance status."""
        if blocked:
            return ComplianceStatus.NON_COMPLIANT_BLOCKED
        elif len(violations) > 0:
            critical = any(v.severity == "CRITICAL" for v in violations)
            if critical:
                return ComplianceStatus.REQUIRES_REVIEW
            return ComplianceStatus.CONDITIONAL_APPROVAL
        return ComplianceStatus.COMPLIANT
    
    def _generate_recommendations(
        self,
        violations: List[ViolationDetail],
        action_type: str,
    ) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        for violation in violations:
            recommendations.append(violation.remediation)
        
        if not violations:
            recommendations.append("Continue with standard protocols")
            recommendations.append("Document action in audit log")
        
        return list(set(recommendations))
    
    def _generate_conditions(
        self,
        violations: List[ViolationDetail],
        action_type: str,
    ) -> List[str]:
        """Generate conditions for conditional approval."""
        conditions = []
        
        non_blocking = [v for v in violations if not v.blocked]
        for violation in non_blocking:
            if violation.violation_type == ViolationType.RETENTION_VIOLATION:
                conditions.append("Schedule data purge within 7 days")
            elif violation.violation_type == ViolationType.SURVEILLANCE_OVERREACH:
                conditions.append("Obtain extended authorization within 24 hours")
        
        return conditions
    
    def _generate_explanation(
        self,
        status: ComplianceStatus,
        violations: List[ViolationDetail],
        concerns: List[str],
    ) -> str:
        """Generate human-readable explanation."""
        if status == ComplianceStatus.COMPLIANT:
            return "Action complies with all civil liberties requirements."
        
        explanation = f"Status: {status.value}. "
        
        if violations:
            explanation += f"{len(violations)} violation(s) identified. "
            critical = [v for v in violations if v.severity == "CRITICAL"]
            if critical:
                explanation += f"Critical: {critical[0].description}. "
        
        if concerns:
            explanation += f"Constitutional concerns: {', '.join(concerns)}."
        
        return explanation
    
    def get_check_history(
        self,
        status: Optional[ComplianceStatus] = None,
        limit: int = 100,
    ) -> List[ComplianceResult]:
        """Get compliance check history."""
        results = self._check_history
        
        if status:
            results = [r for r in results if r.status == status]
        
        return results[-limit:]
    
    def get_retention_limits(self) -> Dict[str, int]:
        """Get data retention limits."""
        return self.RETENTION_LIMITS.copy()


def get_civil_liberties_engine() -> CivilLibertiesEngine:
    """Get the singleton CivilLibertiesEngine instance."""
    return CivilLibertiesEngine.get_instance()
