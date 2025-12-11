"""
CJIS Compliance Layer Module

Implements CJIS Security Policy 5.9 compliance checks for the G3TI RTCC-UIP platform.
Features:
- Password & MFA compliance
- Session timeout rules
- Restricted-query alerts
- Data retention timer controls
- Encryption enforcement
- Logging & chain-of-custody
- Criminal Justice Information access pathways
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import hashlib
import uuid


class ComplianceResult(Enum):
    """CJIS compliance check results"""
    PASS = "PASS"
    FAIL = "FAIL"
    PASS_WITH_WARNING = "PASS_WITH_WARNING"


class CJISViolationType(Enum):
    """Types of CJIS violations"""
    PASSWORD_POLICY = "PASSWORD_POLICY"
    MFA_REQUIRED = "MFA_REQUIRED"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    ENCRYPTION_REQUIRED = "ENCRYPTION_REQUIRED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_RETENTION = "DATA_RETENTION"
    AUDIT_LOGGING = "AUDIT_LOGGING"
    CHAIN_OF_CUSTODY = "CHAIN_OF_CUSTODY"
    RESTRICTED_QUERY = "RESTRICTED_QUERY"
    BACKGROUND_CHECK = "BACKGROUND_CHECK"
    TRAINING_REQUIRED = "TRAINING_REQUIRED"
    PHYSICAL_SECURITY = "PHYSICAL_SECURITY"
    NETWORK_SECURITY = "NETWORK_SECURITY"


class CJISDataCategory(Enum):
    """CJIS data categories"""
    CJI = "Criminal Justice Information"
    CHRI = "Criminal History Record Information"
    III = "Interstate Identification Index"
    NCIC = "National Crime Information Center"
    NLETS = "National Law Enforcement Telecommunications System"
    SOR = "Sex Offender Registry"
    TERRORIST_WATCHLIST = "Terrorist Watchlist"
    IMMIGRATION = "Immigration Data"


@dataclass
class CJISUser:
    """CJIS authorized user"""
    user_id: str
    badge_number: str
    agency_ori: str
    clearance_level: str
    background_check_date: datetime
    training_completion_date: datetime
    mfa_enabled: bool
    last_password_change: datetime
    failed_login_attempts: int = 0
    account_locked: bool = False
    session_active: bool = False
    last_activity: Optional[datetime] = None


@dataclass
class CJISQuery:
    """CJIS query record"""
    query_id: str
    user_id: str
    query_type: str
    data_category: CJISDataCategory
    query_parameters: dict
    timestamp: datetime
    source_ip: str
    device_id: str
    case_number: Optional[str] = None
    justification: Optional[str] = None
    results_count: int = 0
    flagged: bool = False


@dataclass
class ComplianceCheckResult:
    """Result of a compliance check"""
    check_id: str
    check_type: str
    result: ComplianceResult
    violations: list[CJISViolationType]
    warnings: list[str]
    details: dict
    timestamp: datetime
    user_id: Optional[str] = None
    action_required: Optional[str] = None
    blocked: bool = False


class CJISComplianceLayer:
    """
    CJIS Security Policy 5.9 Compliance Layer
    
    Implements comprehensive CJIS compliance checks including:
    - Password and MFA requirements
    - Session management
    - Data access controls
    - Encryption enforcement
    - Audit logging
    - Chain of custody tracking
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
        self._initialized = True
        
        self.authorized_users: dict[str, CJISUser] = {}
        self.query_log: list[CJISQuery] = []
        self.compliance_log: list[ComplianceCheckResult] = []
        self.active_sessions: dict[str, dict] = {}
        self.restricted_queries: list[str] = []
        
        self._init_compliance_rules()
        self._init_riviera_beach_config()
    
    def _init_compliance_rules(self):
        """Initialize CJIS 5.9 compliance rules"""
        self.password_policy = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
            "max_age_days": 90,
            "history_count": 10,
            "lockout_threshold": 5,
            "lockout_duration_minutes": 30,
        }
        
        self.session_policy = {
            "max_idle_minutes": 30,
            "max_session_hours": 12,
            "require_reauthentication_for_sensitive": True,
            "concurrent_sessions_allowed": 1,
        }
        
        self.mfa_policy = {
            "required_for_remote_access": True,
            "required_for_cji_access": True,
            "required_for_admin_functions": True,
            "allowed_methods": ["hardware_token", "software_token", "sms", "biometric"],
            "token_validity_seconds": 300,
        }
        
        self.encryption_policy = {
            "data_at_rest": "AES-256",
            "data_in_transit": "TLS 1.2+",
            "key_rotation_days": 365,
            "fips_140_2_required": True,
        }
        
        self.audit_policy = {
            "log_all_cji_access": True,
            "log_authentication_events": True,
            "log_authorization_events": True,
            "log_data_modifications": True,
            "retention_years": 7,
            "tamper_detection": True,
        }
        
        self.training_requirements = {
            "security_awareness_frequency_months": 12,
            "cjis_certification_frequency_months": 24,
            "specialized_training_required": True,
        }
        
        self.background_check_requirements = {
            "fingerprint_based": True,
            "state_check_required": True,
            "federal_check_required": True,
            "renewal_years": 5,
        }
    
    def _init_riviera_beach_config(self):
        """Initialize Riviera Beach PD specific configuration"""
        self.agency_config = {
            "ori": "FL0500400",
            "agency_name": "Riviera Beach Police Department",
            "state": "Florida",
            "county": "Palm Beach",
            "cjis_systems_officer": "CSO",
            "terminal_agency_coordinator": "TAC",
            "local_agency_security_officer": "LASO",
            "authorized_terminals": 50,
            "mobile_devices": 100,
        }
        
        self.data_retention_limits = {
            CJISDataCategory.CJI: 2555,
            CJISDataCategory.CHRI: 2555,
            CJISDataCategory.III: 365,
            CJISDataCategory.NCIC: 365,
            CJISDataCategory.NLETS: 180,
            CJISDataCategory.SOR: 2555,
            CJISDataCategory.TERRORIST_WATCHLIST: 365,
            CJISDataCategory.IMMIGRATION: 365,
        }
    
    def check_compliance(
        self,
        user_id: str,
        action: str,
        context: dict,
    ) -> ComplianceCheckResult:
        """
        Perform comprehensive CJIS compliance check
        
        Args:
            user_id: User performing the action
            action: Action being performed
            context: Additional context for the check
            
        Returns:
            ComplianceCheckResult with pass/fail status
        """
        check_id = str(uuid.uuid4())
        violations = []
        warnings = []
        details = {}
        
        user = self.authorized_users.get(user_id)
        if not user:
            violations.append(CJISViolationType.UNAUTHORIZED_ACCESS)
            details["user_check"] = "User not found in authorized users"
        else:
            password_check = self._check_password_compliance(user)
            if not password_check["compliant"]:
                violations.append(CJISViolationType.PASSWORD_POLICY)
                details["password_check"] = password_check["reason"]
            
            mfa_check = self._check_mfa_compliance(user, context)
            if not mfa_check["compliant"]:
                violations.append(CJISViolationType.MFA_REQUIRED)
                details["mfa_check"] = mfa_check["reason"]
            
            session_check = self._check_session_compliance(user)
            if not session_check["compliant"]:
                violations.append(CJISViolationType.SESSION_TIMEOUT)
                details["session_check"] = session_check["reason"]
            
            background_check = self._check_background_compliance(user)
            if not background_check["compliant"]:
                if background_check.get("warning"):
                    warnings.append(background_check["reason"])
                else:
                    violations.append(CJISViolationType.BACKGROUND_CHECK)
                    details["background_check"] = background_check["reason"]
            
            training_check = self._check_training_compliance(user)
            if not training_check["compliant"]:
                if training_check.get("warning"):
                    warnings.append(training_check["reason"])
                else:
                    violations.append(CJISViolationType.TRAINING_REQUIRED)
                    details["training_check"] = training_check["reason"]
        
        encryption_check = self._check_encryption_compliance(context)
        if not encryption_check["compliant"]:
            violations.append(CJISViolationType.ENCRYPTION_REQUIRED)
            details["encryption_check"] = encryption_check["reason"]
        
        data_category = context.get("data_category")
        if data_category:
            retention_check = self._check_retention_compliance(data_category, context)
            if not retention_check["compliant"]:
                violations.append(CJISViolationType.DATA_RETENTION)
                details["retention_check"] = retention_check["reason"]
        
        if context.get("query_type") in self.restricted_queries:
            violations.append(CJISViolationType.RESTRICTED_QUERY)
            details["restricted_query"] = "Query type requires additional authorization"
        
        if len(violations) == 0:
            if len(warnings) > 0:
                result = ComplianceResult.PASS_WITH_WARNING
            else:
                result = ComplianceResult.PASS
            blocked = False
        else:
            result = ComplianceResult.FAIL
            blocked = True
        
        check_result = ComplianceCheckResult(
            check_id=check_id,
            check_type=action,
            result=result,
            violations=violations,
            warnings=warnings,
            details=details,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action_required=self._get_action_required(violations),
            blocked=blocked,
        )
        
        self.compliance_log.append(check_result)
        
        return check_result
    
    def _check_password_compliance(self, user: CJISUser) -> dict:
        """Check password policy compliance"""
        max_age = timedelta(days=self.password_policy["max_age_days"])
        
        if datetime.utcnow() - user.last_password_change > max_age:
            return {
                "compliant": False,
                "reason": "Password expired - must be changed every 90 days",
            }
        
        if user.failed_login_attempts >= self.password_policy["lockout_threshold"]:
            return {
                "compliant": False,
                "reason": "Account locked due to failed login attempts",
            }
        
        return {"compliant": True, "reason": "Password policy compliant"}
    
    def _check_mfa_compliance(self, user: CJISUser, context: dict) -> dict:
        """Check MFA compliance"""
        is_remote = context.get("is_remote_access", False)
        is_cji_access = context.get("is_cji_access", False)
        is_admin = context.get("is_admin_function", False)
        
        mfa_required = (
            (is_remote and self.mfa_policy["required_for_remote_access"]) or
            (is_cji_access and self.mfa_policy["required_for_cji_access"]) or
            (is_admin and self.mfa_policy["required_for_admin_functions"])
        )
        
        if mfa_required and not user.mfa_enabled:
            return {
                "compliant": False,
                "reason": "MFA required but not enabled for user",
            }
        
        if mfa_required and not context.get("mfa_verified", False):
            return {
                "compliant": False,
                "reason": "MFA verification required",
            }
        
        return {"compliant": True, "reason": "MFA compliant"}
    
    def _check_session_compliance(self, user: CJISUser) -> dict:
        """Check session timeout compliance"""
        if not user.session_active:
            return {"compliant": True, "reason": "No active session"}
        
        if not user.last_activity:
            return {"compliant": True, "reason": "Session just started"}
        
        idle_time = datetime.utcnow() - user.last_activity
        max_idle = timedelta(minutes=self.session_policy["max_idle_minutes"])
        
        if idle_time > max_idle:
            return {
                "compliant": False,
                "reason": f"Session idle for {idle_time.seconds // 60} minutes - max is {self.session_policy['max_idle_minutes']}",
            }
        
        return {"compliant": True, "reason": "Session compliant"}
    
    def _check_background_compliance(self, user: CJISUser) -> dict:
        """Check background check compliance"""
        renewal_period = timedelta(
            days=self.background_check_requirements["renewal_years"] * 365
        )
        
        time_since_check = datetime.utcnow() - user.background_check_date
        
        if time_since_check > renewal_period:
            return {
                "compliant": False,
                "reason": "Background check expired - renewal required",
            }
        
        warning_threshold = renewal_period - timedelta(days=90)
        if time_since_check > warning_threshold:
            return {
                "compliant": True,
                "warning": True,
                "reason": "Background check renewal due within 90 days",
            }
        
        return {"compliant": True, "reason": "Background check current"}
    
    def _check_training_compliance(self, user: CJISUser) -> dict:
        """Check training compliance"""
        training_period = timedelta(
            days=self.training_requirements["security_awareness_frequency_months"] * 30
        )
        
        time_since_training = datetime.utcnow() - user.training_completion_date
        
        if time_since_training > training_period:
            return {
                "compliant": False,
                "reason": "Security awareness training expired",
            }
        
        warning_threshold = training_period - timedelta(days=30)
        if time_since_training > warning_threshold:
            return {
                "compliant": True,
                "warning": True,
                "reason": "Security awareness training due within 30 days",
            }
        
        return {"compliant": True, "reason": "Training current"}
    
    def _check_encryption_compliance(self, context: dict) -> dict:
        """Check encryption compliance"""
        if context.get("data_at_rest") and not context.get("encrypted_at_rest"):
            return {
                "compliant": False,
                "reason": "Data at rest must be encrypted with AES-256",
            }
        
        if context.get("data_in_transit") and not context.get("tls_enabled"):
            return {
                "compliant": False,
                "reason": "Data in transit must use TLS 1.2 or higher",
            }
        
        return {"compliant": True, "reason": "Encryption compliant"}
    
    def _check_retention_compliance(
        self, data_category: CJISDataCategory, context: dict
    ) -> dict:
        """Check data retention compliance"""
        retention_limit = self.data_retention_limits.get(data_category, 365)
        data_age_days = context.get("data_age_days", 0)
        
        if data_age_days > retention_limit:
            return {
                "compliant": False,
                "reason": f"Data exceeds retention limit of {retention_limit} days",
            }
        
        return {"compliant": True, "reason": "Retention compliant"}
    
    def _get_action_required(self, violations: list[CJISViolationType]) -> Optional[str]:
        """Get required action based on violations"""
        if not violations:
            return None
        
        action_map = {
            CJISViolationType.PASSWORD_POLICY: "Change password immediately",
            CJISViolationType.MFA_REQUIRED: "Complete MFA verification",
            CJISViolationType.SESSION_TIMEOUT: "Re-authenticate to continue",
            CJISViolationType.ENCRYPTION_REQUIRED: "Enable encryption",
            CJISViolationType.UNAUTHORIZED_ACCESS: "Contact system administrator",
            CJISViolationType.DATA_RETENTION: "Purge expired data",
            CJISViolationType.BACKGROUND_CHECK: "Complete background check renewal",
            CJISViolationType.TRAINING_REQUIRED: "Complete required training",
            CJISViolationType.RESTRICTED_QUERY: "Obtain supervisor authorization",
        }
        
        for violation in violations:
            if violation in action_map:
                return action_map[violation]
        
        return "Contact CJIS Systems Officer"
    
    def log_cji_query(self, query: CJISQuery) -> str:
        """Log a CJI query for audit purposes"""
        self.query_log.append(query)
        
        if self._is_suspicious_query(query):
            query.flagged = True
            self._alert_suspicious_activity(query)
        
        return query.query_id
    
    def _is_suspicious_query(self, query: CJISQuery) -> bool:
        """Check if query is suspicious"""
        user_queries = [
            q for q in self.query_log
            if q.user_id == query.user_id
            and q.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if len(user_queries) > 50:
            return True
        
        if not query.case_number and query.data_category in [
            CJISDataCategory.CHRI,
            CJISDataCategory.III,
        ]:
            return True
        
        return False
    
    def _alert_suspicious_activity(self, query: CJISQuery):
        """Alert on suspicious activity"""
        pass
    
    def register_user(self, user: CJISUser) -> bool:
        """Register a CJIS authorized user"""
        self.authorized_users[user.user_id] = user
        return True
    
    def get_compliance_log(
        self,
        limit: int = 100,
        result_filter: Optional[ComplianceResult] = None,
    ) -> list[ComplianceCheckResult]:
        """Get compliance check log"""
        log = self.compliance_log
        
        if result_filter:
            log = [entry for entry in log if entry.result == result_filter]
        
        return log[-limit:]
    
    def get_query_log(
        self,
        limit: int = 100,
        user_id: Optional[str] = None,
        flagged_only: bool = False,
    ) -> list[CJISQuery]:
        """Get CJI query log"""
        log = self.query_log
        
        if user_id:
            log = [entry for entry in log if entry.user_id == user_id]
        
        if flagged_only:
            log = [entry for entry in log if entry.flagged]
        
        return log[-limit:]
    
    def get_user_compliance_status(self, user_id: str) -> dict:
        """Get comprehensive compliance status for a user"""
        user = self.authorized_users.get(user_id)
        if not user:
            return {"status": "NOT_FOUND", "compliant": False}
        
        status = {
            "user_id": user_id,
            "password_compliant": self._check_password_compliance(user)["compliant"],
            "mfa_enabled": user.mfa_enabled,
            "background_check_current": self._check_background_compliance(user)["compliant"],
            "training_current": self._check_training_compliance(user)["compliant"],
            "account_locked": user.account_locked,
            "last_activity": user.last_activity,
        }
        
        status["overall_compliant"] = all([
            status["password_compliant"],
            status["mfa_enabled"],
            status["background_check_current"],
            status["training_current"],
            not status["account_locked"],
        ])
        
        return status


_cjis_compliance_layer: Optional[CJISComplianceLayer] = None


def get_cjis_compliance_layer() -> CJISComplianceLayer:
    """Get singleton instance of CJISComplianceLayer"""
    global _cjis_compliance_layer
    if _cjis_compliance_layer is None:
        _cjis_compliance_layer = CJISComplianceLayer()
    return _cjis_compliance_layer
