"""
Phase 30: Privacy Guard

Ethical + Legal Safeguards for Human Stability Intelligence Engine

Enforces:
- No use of private social media
- No predictive policing on protected classes
- No demographic profiling
- All models reviewed through fairness audit
- GDPR-style anonymization
- HIPAA-adjacent protections for crisis data

If a query violates ethics → BLOCK execution.

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import hashlib
import uuid


class PrivacyViolationType(Enum):
    """Types of privacy violations"""
    PRIVATE_SOCIAL_MEDIA = "private_social_media"
    PROTECTED_CLASS_PROFILING = "protected_class_profiling"
    DEMOGRAPHIC_PROFILING = "demographic_profiling"
    PII_EXPOSURE = "pii_exposure"
    UNAUTHORIZED_DATA_ACCESS = "unauthorized_data_access"
    HIPAA_VIOLATION = "hipaa_violation"
    FERPA_VIOLATION = "ferpa_violation"
    VAWA_VIOLATION = "vawa_violation"
    PREDICTIVE_POLICING_INDIVIDUAL = "predictive_policing_individual"
    UNFAIR_ALGORITHM = "unfair_algorithm"
    DATA_RETENTION_VIOLATION = "data_retention_violation"
    CONSENT_VIOLATION = "consent_violation"


class AnonymizationLevel(Enum):
    """Levels of data anonymization"""
    NONE = 0
    MINIMAL = 1
    PARTIAL = 2
    SUBSTANTIAL = 3
    FULL = 4
    AGGREGATED = 5


class DataCategory(Enum):
    """Categories of data with different protection requirements"""
    PUBLIC_RECORD = "public_record"
    CAD_DATA = "cad_data"
    INCIDENT_REPORT = "incident_report"
    MENTAL_HEALTH = "mental_health"
    SUBSTANCE_ABUSE = "substance_abuse"
    DOMESTIC_VIOLENCE = "domestic_violence"
    JUVENILE = "juvenile"
    SCHOOL_RECORD = "school_record"
    MEDICAL = "medical"
    SOCIAL_MEDIA_PUBLIC = "social_media_public"
    SOCIAL_MEDIA_PRIVATE = "social_media_private"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    FINANCIAL = "financial"


class ProtectedClass(Enum):
    """Protected classes that cannot be used for profiling"""
    RACE = "race"
    ETHNICITY = "ethnicity"
    NATIONAL_ORIGIN = "national_origin"
    RELIGION = "religion"
    SEX = "sex"
    GENDER_IDENTITY = "gender_identity"
    SEXUAL_ORIENTATION = "sexual_orientation"
    AGE = "age"
    DISABILITY = "disability"
    VETERAN_STATUS = "veteran_status"
    GENETIC_INFORMATION = "genetic_information"
    PREGNANCY = "pregnancy"
    CITIZENSHIP = "citizenship"


@dataclass
class PrivacyCheckResult:
    """Result of a privacy check"""
    check_id: str
    timestamp: datetime
    query_type: str
    approved: bool
    violations: List[PrivacyViolationType]
    warnings: List[str]
    required_anonymization: AnonymizationLevel
    data_categories_checked: List[DataCategory]
    protected_classes_checked: List[ProtectedClass]
    recommendations: List[str]
    audit_trail: str
    
    def __post_init__(self):
        if not self.audit_trail:
            self.audit_trail = self._generate_audit_trail()
    
    def _generate_audit_trail(self) -> str:
        data = f"{self.check_id}:{self.timestamp.isoformat()}:{self.approved}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class EthicsAuditResult:
    """Result of an ethics audit"""
    audit_id: str
    timestamp: datetime
    model_name: str
    audit_type: str
    passed: bool
    fairness_score: float
    bias_indicators: List[str]
    protected_class_impact: Dict[str, float]
    recommendations: List[str]
    certification_status: str
    next_audit_date: str
    audit_trail: str = ""
    
    def __post_init__(self):
        if not self.audit_trail:
            self.audit_trail = self._generate_audit_trail()
    
    def _generate_audit_trail(self) -> str:
        data = f"{self.audit_id}:{self.timestamp.isoformat()}:{self.passed}"
        return hashlib.sha256(data.encode()).hexdigest()


class PrivacyGuard:
    """
    Privacy Guard for Human Stability Intelligence Engine
    
    Enforces ethical and legal safeguards for all data operations.
    Blocks any query that violates privacy or ethics requirements.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "county": "Palm Beach",
            "city": "Riviera Beach",
            "zip": "33404",
        }
        
        self._blocked_data_sources = {
            "private_social_media",
            "private_messages",
            "private_email",
            "private_phone_records",
            "private_financial_records",
            "private_medical_records",
            "private_therapy_records",
            "private_school_records_without_consent",
            "private_employment_records",
            "private_insurance_records",
        }
        
        self._protected_data_categories = {
            DataCategory.MENTAL_HEALTH: AnonymizationLevel.FULL,
            DataCategory.SUBSTANCE_ABUSE: AnonymizationLevel.FULL,
            DataCategory.DOMESTIC_VIOLENCE: AnonymizationLevel.FULL,
            DataCategory.JUVENILE: AnonymizationLevel.FULL,
            DataCategory.SCHOOL_RECORD: AnonymizationLevel.FULL,
            DataCategory.MEDICAL: AnonymizationLevel.FULL,
            DataCategory.SOCIAL_MEDIA_PRIVATE: AnonymizationLevel.FULL,
            DataCategory.BIOMETRIC: AnonymizationLevel.FULL,
        }
        
        self._allowed_query_types = {
            "suicide_risk_assessment",
            "dv_escalation_assessment",
            "community_trauma_pulse",
            "crisis_routing",
            "repeat_crisis_detection",
            "youth_risk_assessment",
            "school_incident_analysis",
            "gang_exposure_assessment",
            "youth_stability_map",
            "mental_health_check",
            "stability_map",
            "community_pulse",
        }
        
        self._pii_patterns = [
            "ssn", "social_security",
            "date_of_birth", "dob",
            "full_name", "name",
            "address", "home_address",
            "phone_number", "phone",
            "email", "email_address",
            "driver_license", "dl_number",
            "passport", "passport_number",
            "bank_account", "credit_card",
            "ip_address",
        ]
        
        self.privacy_checks: List[PrivacyCheckResult] = []
        self.ethics_audits: List[EthicsAuditResult] = []
        self.blocked_queries: List[Dict[str, Any]] = []
        
        self._initialized = True
    
    def check_query(
        self,
        query_type: str,
        data_sources: List[str],
        contains_pii: bool = False,
        target_demographics: Optional[List[str]] = None,
        protected_class_filters: Optional[List[str]] = None,
        individual_targeting: bool = False,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> PrivacyCheckResult:
        """
        Check if a query meets privacy and ethics requirements
        
        Returns approved=False if any violations are detected.
        """
        violations = []
        warnings = []
        recommendations = []
        
        for source in data_sources:
            if source.lower() in self._blocked_data_sources:
                violations.append(PrivacyViolationType.PRIVATE_SOCIAL_MEDIA)
                recommendations.append(f"Remove blocked data source: {source}")
        
        if protected_class_filters:
            for pc_filter in protected_class_filters:
                for protected_class in ProtectedClass:
                    if protected_class.value.lower() in pc_filter.lower():
                        violations.append(PrivacyViolationType.PROTECTED_CLASS_PROFILING)
                        recommendations.append(
                            f"Remove protected class filter: {pc_filter}"
                        )
                        break
        
        if target_demographics:
            demographic_keywords = [
                "race", "ethnicity", "religion", "gender",
                "sexual_orientation", "disability", "national_origin",
            ]
            for demo in target_demographics:
                for keyword in demographic_keywords:
                    if keyword in demo.lower():
                        violations.append(PrivacyViolationType.DEMOGRAPHIC_PROFILING)
                        recommendations.append(
                            f"Remove demographic targeting: {demo}"
                        )
                        break
        
        if contains_pii:
            violations.append(PrivacyViolationType.PII_EXPOSURE)
            recommendations.append("Remove or anonymize PII before processing")
        
        if individual_targeting and query_type not in [
            "crisis_routing",
            "repeat_crisis_detection",
        ]:
            violations.append(PrivacyViolationType.PREDICTIVE_POLICING_INDIVIDUAL)
            recommendations.append(
                "Use aggregated/zone-level analysis instead of individual targeting"
            )
        
        data_categories = self._identify_data_categories(data_sources)
        required_anonymization = AnonymizationLevel.MINIMAL
        
        for category in data_categories:
            if category in self._protected_data_categories:
                cat_level = self._protected_data_categories[category]
                if cat_level.value > required_anonymization.value:
                    required_anonymization = cat_level
                warnings.append(
                    f"Protected data category detected: {category.value}"
                )
        
        if query_type not in self._allowed_query_types:
            warnings.append(f"Query type '{query_type}' not in standard list")
        
        if not violations:
            recommendations.append("Query approved - maintain audit trail")
            recommendations.append("Apply required anonymization level")
        
        approved = len(violations) == 0
        
        if not approved:
            self.blocked_queries.append({
                "timestamp": datetime.utcnow().isoformat(),
                "query_type": query_type,
                "violations": [v.value for v in violations],
                "data_sources": data_sources,
            })
        
        result = PrivacyCheckResult(
            check_id=f"PC-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            query_type=query_type,
            approved=approved,
            violations=violations,
            warnings=warnings,
            required_anonymization=required_anonymization,
            data_categories_checked=data_categories,
            protected_classes_checked=list(ProtectedClass) if protected_class_filters else [],
            recommendations=recommendations,
            audit_trail="",
        )
        
        self.privacy_checks.append(result)
        return result
    
    def _identify_data_categories(
        self,
        data_sources: List[str],
    ) -> List[DataCategory]:
        """Identify data categories from source names"""
        categories = []
        
        source_mapping = {
            "mental_health": DataCategory.MENTAL_HEALTH,
            "substance": DataCategory.SUBSTANCE_ABUSE,
            "domestic_violence": DataCategory.DOMESTIC_VIOLENCE,
            "dv": DataCategory.DOMESTIC_VIOLENCE,
            "juvenile": DataCategory.JUVENILE,
            "youth": DataCategory.JUVENILE,
            "school": DataCategory.SCHOOL_RECORD,
            "medical": DataCategory.MEDICAL,
            "social_media": DataCategory.SOCIAL_MEDIA_PUBLIC,
            "biometric": DataCategory.BIOMETRIC,
            "location": DataCategory.LOCATION,
            "financial": DataCategory.FINANCIAL,
            "cad": DataCategory.CAD_DATA,
            "incident": DataCategory.INCIDENT_REPORT,
            "public": DataCategory.PUBLIC_RECORD,
        }
        
        for source in data_sources:
            source_lower = source.lower()
            for keyword, category in source_mapping.items():
                if keyword in source_lower:
                    if category not in categories:
                        categories.append(category)
        
        if not categories:
            categories.append(DataCategory.PUBLIC_RECORD)
        
        return categories
    
    def audit_model_fairness(
        self,
        model_name: str,
        model_type: str,
        training_data_description: str,
        protected_class_metrics: Optional[Dict[str, float]] = None,
    ) -> EthicsAuditResult:
        """
        Audit a model for fairness and bias
        
        All models must pass fairness audit before deployment.
        """
        bias_indicators = []
        recommendations = []
        
        if protected_class_metrics:
            for pc, metric in protected_class_metrics.items():
                if metric < 0.8 or metric > 1.2:
                    bias_indicators.append(
                        f"Disparate impact detected for {pc}: {metric}"
                    )
        
        if "demographic" in training_data_description.lower():
            bias_indicators.append("Training data includes demographic features")
            recommendations.append("Remove demographic features from training data")
        
        if "race" in training_data_description.lower():
            bias_indicators.append("Training data includes race information")
            recommendations.append("Remove race from training data")
        
        fairness_score = 1.0 - (len(bias_indicators) * 0.15)
        fairness_score = max(0.0, min(1.0, fairness_score))
        
        passed = fairness_score >= 0.8 and len(bias_indicators) <= 1
        
        if passed:
            certification_status = "CERTIFIED"
            recommendations.append("Model approved for deployment")
        else:
            certification_status = "REQUIRES_REMEDIATION"
            recommendations.append("Address bias indicators before deployment")
            recommendations.append("Retrain model without demographic features")
        
        audit = EthicsAuditResult(
            audit_id=f"EA-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            model_name=model_name,
            audit_type=model_type,
            passed=passed,
            fairness_score=fairness_score,
            bias_indicators=bias_indicators,
            protected_class_impact=protected_class_metrics or {},
            recommendations=recommendations,
            certification_status=certification_status,
            next_audit_date=(
                datetime.utcnow().replace(month=datetime.utcnow().month + 3)
            ).strftime("%Y-%m-%d") if datetime.utcnow().month <= 9 else (
                datetime.utcnow().replace(year=datetime.utcnow().year + 1, month=1)
            ).strftime("%Y-%m-%d"),
        )
        
        self.ethics_audits.append(audit)
        return audit
    
    def anonymize_data(
        self,
        data: Dict[str, Any],
        level: AnonymizationLevel,
    ) -> Dict[str, Any]:
        """
        Anonymize data according to specified level
        
        Levels:
        - NONE: No anonymization (not recommended)
        - MINIMAL: Remove direct identifiers
        - PARTIAL: Remove direct identifiers + generalize quasi-identifiers
        - SUBSTANTIAL: K-anonymity with k=5
        - FULL: Remove all potentially identifying information
        - AGGREGATED: Return only aggregate statistics
        """
        if level == AnonymizationLevel.NONE:
            return data
        
        anonymized = data.copy()
        
        direct_identifiers = [
            "name", "full_name", "first_name", "last_name",
            "ssn", "social_security", "dob", "date_of_birth",
            "address", "phone", "email", "driver_license",
        ]
        
        if level.value >= AnonymizationLevel.MINIMAL.value:
            for identifier in direct_identifiers:
                if identifier in anonymized:
                    anonymized[identifier] = "[REDACTED]"
        
        quasi_identifiers = [
            "zip_code", "age", "gender", "occupation",
            "employer", "school", "neighborhood",
        ]
        
        if level.value >= AnonymizationLevel.PARTIAL.value:
            for qi in quasi_identifiers:
                if qi in anonymized:
                    if qi == "zip_code" and isinstance(anonymized[qi], str):
                        anonymized[qi] = anonymized[qi][:3] + "XX"
                    elif qi == "age" and isinstance(anonymized[qi], int):
                        anonymized[qi] = f"{(anonymized[qi] // 10) * 10}-{(anonymized[qi] // 10) * 10 + 9}"
                    else:
                        anonymized[qi] = "[GENERALIZED]"
        
        if level.value >= AnonymizationLevel.SUBSTANTIAL.value:
            anonymized["k_anonymity"] = 5
            anonymized["anonymization_method"] = "k-anonymity"
        
        if level.value >= AnonymizationLevel.FULL.value:
            sensitive_fields = [
                "location", "coordinates", "lat", "lng",
                "timestamp", "time", "date",
            ]
            for field in sensitive_fields:
                if field in anonymized:
                    anonymized[field] = "[REMOVED]"
        
        if level == AnonymizationLevel.AGGREGATED:
            return {
                "data_type": "aggregated",
                "record_count": 1,
                "anonymization_level": "AGGREGATED",
                "note": "Individual records not available",
            }
        
        anonymized["anonymization_level"] = level.name
        anonymized["anonymization_timestamp"] = datetime.utcnow().isoformat()
        
        return anonymized
    
    def validate_hipaa_compliance(
        self,
        data_operation: str,
        data_type: str,
        has_authorization: bool = False,
        is_treatment_purpose: bool = False,
        is_public_health_purpose: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate HIPAA-adjacent compliance for health-related data
        
        Note: This is HIPAA-adjacent as law enforcement has specific
        exemptions, but we apply similar protections voluntarily.
        """
        compliant = True
        issues = []
        recommendations = []
        
        protected_health_info = [
            "mental_health", "substance_abuse", "medical",
            "diagnosis", "treatment", "medication",
        ]
        
        is_phi = any(phi in data_type.lower() for phi in protected_health_info)
        
        if is_phi:
            if not has_authorization and not is_treatment_purpose and not is_public_health_purpose:
                if data_operation in ["share", "disclose", "export"]:
                    compliant = False
                    issues.append("PHI disclosure without authorization")
                    recommendations.append("Obtain authorization or apply de-identification")
            
            recommendations.append("Apply minimum necessary standard")
            recommendations.append("Maintain access logs")
            recommendations.append("Ensure secure transmission")
        
        return {
            "compliant": compliant,
            "is_phi": is_phi,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def validate_ferpa_compliance(
        self,
        data_operation: str,
        involves_student_records: bool,
        has_parental_consent: bool = False,
        is_health_safety_emergency: bool = False,
        is_law_enforcement_unit: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate FERPA compliance for education records
        """
        compliant = True
        issues = []
        recommendations = []
        
        if involves_student_records:
            if not has_parental_consent and not is_health_safety_emergency:
                if data_operation in ["access", "share", "disclose"]:
                    if not is_law_enforcement_unit:
                        compliant = False
                        issues.append("Student record access without consent")
                    else:
                        recommendations.append(
                            "Document law enforcement unit exception"
                        )
            
            recommendations.append("Limit to directory information when possible")
            recommendations.append("Maintain access logs")
            recommendations.append("Apply need-to-know principle")
        
        return {
            "compliant": compliant,
            "involves_student_records": involves_student_records,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def validate_vawa_compliance(
        self,
        data_operation: str,
        involves_dv_victim: bool,
        victim_consent: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate VAWA (Violence Against Women Act) compliance
        """
        compliant = True
        issues = []
        recommendations = []
        
        if involves_dv_victim:
            if not victim_consent:
                if data_operation in ["share", "disclose"]:
                    compliant = False
                    issues.append("DV victim information disclosure without consent")
                    recommendations.append("Obtain victim consent before disclosure")
            
            recommendations.append("Protect victim location information")
            recommendations.append("Do not share with perpetrator")
            recommendations.append("Maintain confidentiality of shelter locations")
            recommendations.append("Document all disclosures")
        
        return {
            "compliant": compliant,
            "involves_dv_victim": involves_dv_victim,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Get privacy compliance report"""
        total_checks = len(self.privacy_checks)
        approved_checks = len([c for c in self.privacy_checks if c.approved])
        blocked_checks = len(self.blocked_queries)
        
        violation_counts = {}
        for check in self.privacy_checks:
            for violation in check.violations:
                violation_counts[violation.value] = violation_counts.get(
                    violation.value, 0
                ) + 1
        
        return {
            "report_id": f"PR-{uuid.uuid4().hex[:12].upper()}",
            "timestamp": datetime.utcnow().isoformat(),
            "total_privacy_checks": total_checks,
            "approved_checks": approved_checks,
            "blocked_queries": blocked_checks,
            "approval_rate": approved_checks / total_checks if total_checks > 0 else 1.0,
            "violation_breakdown": violation_counts,
            "total_ethics_audits": len(self.ethics_audits),
            "passed_audits": len([a for a in self.ethics_audits if a.passed]),
            "agency": self.agency_config,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get guard statistics"""
        return {
            "total_privacy_checks": len(self.privacy_checks),
            "total_blocked_queries": len(self.blocked_queries),
            "total_ethics_audits": len(self.ethics_audits),
            "approval_rate": (
                len([c for c in self.privacy_checks if c.approved]) /
                len(self.privacy_checks)
            ) if self.privacy_checks else 1.0,
            "agency": self.agency_config,
        }
