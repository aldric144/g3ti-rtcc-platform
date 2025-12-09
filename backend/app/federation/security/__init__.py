"""
G3TI RTCC-UIP Zero Trust Security & Data Segregation
Phase 10: Row-level access, query-time masking, audit logging, and CJIS compliance
"""

import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class SecurityLevel(str, Enum):
    """Security classification levels"""
    UNCLASSIFIED = "unclassified"
    LAW_ENFORCEMENT_SENSITIVE = "les"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AccessDecision(str, Enum):
    """Access decision outcomes"""
    ALLOW = "allow"
    DENY = "deny"
    ALLOW_MASKED = "allow_masked"
    ALLOW_PARTIAL = "allow_partial"


class AuditEventType(str, Enum):
    """Types of audit events"""
    DATA_ACCESS = "data_access"
    DATA_QUERY = "data_query"
    DATA_EXPORT = "data_export"
    DATA_SHARE = "data_share"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    POLICY_VIOLATION = "policy_violation"
    ACCESS_DENIED = "access_denied"
    MASKING_APPLIED = "masking_applied"


class RetentionPolicy(str, Enum):
    """Data retention policies"""
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    DAYS_180 = "180_days"
    YEAR_1 = "1_year"
    YEARS_3 = "3_years"
    YEARS_7 = "7_years"
    PERMANENT = "permanent"


class RowLevelAccessRule:
    """Row-level access rule for data segregation"""

    def __init__(
        self,
        rule_id: str,
        agency_id: str,
        resource_type: str,
        conditions: dict[str, Any],
        allowed_fields: list[str] | None = None,
        denied_fields: list[str] | None = None,
        requires_audit: bool = True,
    ):
        self.id = rule_id
        self.agency_id = agency_id
        self.resource_type = resource_type
        self.conditions = conditions
        self.allowed_fields = allowed_fields
        self.denied_fields = denied_fields or []
        self.requires_audit = requires_audit
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True


class MaskingRule:
    """Query-time masking rule for sensitive fields"""

    def __init__(
        self,
        rule_id: str,
        field_name: str,
        resource_type: str,
        masking_type: str,
        applies_to_agencies: list[str] | None = None,
        exceptions: list[str] | None = None,
    ):
        self.id = rule_id
        self.field_name = field_name
        self.resource_type = resource_type
        self.masking_type = masking_type
        self.applies_to_agencies = applies_to_agencies  # None = all agencies
        self.exceptions = exceptions or []
        self.created_at = datetime.utcnow()
        self.is_active = True


class FederatedAuditEntry:
    """Audit log entry for federated operations"""

    def __init__(
        self,
        event_type: AuditEventType,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
        user_agent: str | None = None,
        session_id: str | None = None,
        query_text: str | None = None,
        result_count: int | None = None,
        access_decision: AccessDecision | None = None,
        masked_fields: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.event_type = event_type
        self.agency_id = agency_id
        self.user_id = user_id
        self.user_name = user_name
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.session_id = session_id
        self.query_text = query_text
        self.result_count = result_count
        self.access_decision = access_decision
        self.masked_fields = masked_fields or []
        self.timestamp = datetime.utcnow()
        self.retention_until = self._calculate_retention()

    def _calculate_retention(self) -> datetime:
        """Calculate retention date based on event type"""
        # CJIS requires minimum 1 year retention for access logs
        if self.event_type in [
            AuditEventType.DATA_ACCESS,
            AuditEventType.DATA_QUERY,
            AuditEventType.DATA_EXPORT,
        ]:
            return self.timestamp + timedelta(days=365 * 3)  # 3 years
        elif self.event_type == AuditEventType.POLICY_VIOLATION:
            return self.timestamp + timedelta(days=365 * 7)  # 7 years
        return self.timestamp + timedelta(days=365)  # 1 year default


class AgencyDataDomain:
    """Separate data domain for an agency"""

    def __init__(
        self,
        agency_id: str,
        domain_name: str,
        security_level: SecurityLevel,
        allowed_data_types: list[str],
        encryption_required: bool = True,
        audit_all_access: bool = True,
    ):
        self.id = str(uuid4())
        self.agency_id = agency_id
        self.domain_name = domain_name
        self.security_level = security_level
        self.allowed_data_types = allowed_data_types
        self.encryption_required = encryption_required
        self.audit_all_access = audit_all_access
        self.created_at = datetime.utcnow()
        self.search_index_prefix = f"agency_{agency_id}_"


class AccessRequest:
    """Request for data access evaluation"""

    def __init__(
        self,
        requesting_agency: str,
        requesting_user: str,
        target_agency: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        fields_requested: list[str] | None = None,
        query_params: dict[str, Any] | None = None,
    ):
        self.id = str(uuid4())
        self.requesting_agency = requesting_agency
        self.requesting_user = requesting_user
        self.target_agency = target_agency
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.fields_requested = fields_requested
        self.query_params = query_params or {}
        self.timestamp = datetime.utcnow()


class AccessResponse:
    """Response from access evaluation"""

    def __init__(
        self,
        request_id: str,
        decision: AccessDecision,
        allowed_fields: list[str] | None = None,
        masked_fields: list[str] | None = None,
        denied_fields: list[str] | None = None,
        reason: str | None = None,
        conditions: dict[str, Any] | None = None,
    ):
        self.request_id = request_id
        self.decision = decision
        self.allowed_fields = allowed_fields or []
        self.masked_fields = masked_fields or []
        self.denied_fields = denied_fields or []
        self.reason = reason
        self.conditions = conditions or {}
        self.evaluated_at = datetime.utcnow()


class ZeroTrustSecurityManager:
    """Manager for zero trust security and data segregation"""

    def __init__(self):
        self.row_level_rules: dict[str, RowLevelAccessRule] = {}
        self.masking_rules: dict[str, MaskingRule] = {}
        self.audit_log: list[FederatedAuditEntry] = []
        self.data_domains: dict[str, AgencyDataDomain] = {}
        self.agency_permissions: dict[str, dict[str, list[str]]] = {}
        self.revoked_access: dict[str, list[str]] = {}  # agency -> revoked user IDs

    def create_data_domain(
        self,
        agency_id: str,
        domain_name: str,
        security_level: SecurityLevel,
        allowed_data_types: list[str],
        encryption_required: bool = True,
        audit_all_access: bool = True,
    ) -> AgencyDataDomain:
        """Create a separate data domain for an agency"""
        domain = AgencyDataDomain(
            agency_id=agency_id,
            domain_name=domain_name,
            security_level=security_level,
            allowed_data_types=allowed_data_types,
            encryption_required=encryption_required,
            audit_all_access=audit_all_access,
        )
        self.data_domains[agency_id] = domain
        return domain

    def get_data_domain(self, agency_id: str) -> AgencyDataDomain | None:
        """Get data domain for an agency"""
        return self.data_domains.get(agency_id)

    def create_row_level_rule(
        self,
        agency_id: str,
        resource_type: str,
        conditions: dict[str, Any],
        allowed_fields: list[str] | None = None,
        denied_fields: list[str] | None = None,
    ) -> RowLevelAccessRule:
        """Create a row-level access rule"""
        rule = RowLevelAccessRule(
            rule_id=str(uuid4()),
            agency_id=agency_id,
            resource_type=resource_type,
            conditions=conditions,
            allowed_fields=allowed_fields,
            denied_fields=denied_fields,
        )
        self.row_level_rules[rule.id] = rule
        return rule

    def create_masking_rule(
        self,
        field_name: str,
        resource_type: str,
        masking_type: str,
        applies_to_agencies: list[str] | None = None,
        exceptions: list[str] | None = None,
    ) -> MaskingRule:
        """Create a query-time masking rule"""
        rule = MaskingRule(
            rule_id=str(uuid4()),
            field_name=field_name,
            resource_type=resource_type,
            masking_type=masking_type,
            applies_to_agencies=applies_to_agencies,
            exceptions=exceptions,
        )
        self.masking_rules[rule.id] = rule
        return rule

    def evaluate_access(
        self,
        request: AccessRequest,
    ) -> AccessResponse:
        """Evaluate an access request using zero trust principles"""
        # Check if access has been revoked
        if request.requesting_user in self.revoked_access.get(
            request.requesting_agency, []
        ):
            self._log_access_denied(request, "Access revoked")
            return AccessResponse(
                request_id=request.id,
                decision=AccessDecision.DENY,
                reason="Access has been revoked",
            )

        # Check agency permissions
        if not self._check_agency_permission(
            request.requesting_agency,
            request.target_agency,
            request.resource_type,
        ):
            self._log_access_denied(request, "No permission for resource type")
            return AccessResponse(
                request_id=request.id,
                decision=AccessDecision.DENY,
                reason="Agency does not have permission for this resource type",
            )

        # Get applicable row-level rules
        applicable_rules = self._get_applicable_rules(
            request.requesting_agency,
            request.resource_type,
        )

        # Evaluate rules
        allowed_fields = request.fields_requested or []
        denied_fields = []
        masked_fields = []

        for rule in applicable_rules:
            if rule.denied_fields:
                denied_fields.extend(rule.denied_fields)
            if rule.allowed_fields:
                allowed_fields = [
                    f for f in allowed_fields
                    if f in rule.allowed_fields
                ]

        # Apply masking rules
        masking_rules = self._get_masking_rules(
            request.requesting_agency,
            request.resource_type,
        )
        for rule in masking_rules:
            if rule.field_name in allowed_fields:
                masked_fields.append(rule.field_name)

        # Remove denied fields from allowed
        allowed_fields = [f for f in allowed_fields if f not in denied_fields]

        # Determine decision
        if not allowed_fields and request.fields_requested:
            decision = AccessDecision.DENY
            reason = "No fields allowed for access"
        elif masked_fields:
            decision = AccessDecision.ALLOW_MASKED
            reason = "Access granted with masking applied"
        elif denied_fields:
            decision = AccessDecision.ALLOW_PARTIAL
            reason = "Partial access granted"
        else:
            decision = AccessDecision.ALLOW
            reason = "Full access granted"

        response = AccessResponse(
            request_id=request.id,
            decision=decision,
            allowed_fields=allowed_fields,
            masked_fields=masked_fields,
            denied_fields=denied_fields,
            reason=reason,
        )

        # Log the access
        self._log_access(request, response)

        return response

    def _check_agency_permission(
        self,
        requesting_agency: str,
        target_agency: str,
        resource_type: str,
    ) -> bool:
        """Check if agency has permission for resource type"""
        permissions = self.agency_permissions.get(requesting_agency, {})
        allowed_types = permissions.get(target_agency, [])
        return resource_type in allowed_types or "*" in allowed_types

    def _get_applicable_rules(
        self,
        agency_id: str,
        resource_type: str,
    ) -> list[RowLevelAccessRule]:
        """Get applicable row-level rules for an agency and resource"""
        return [
            rule for rule in self.row_level_rules.values()
            if rule.agency_id == agency_id
            and rule.resource_type == resource_type
            and rule.is_active
        ]

    def _get_masking_rules(
        self,
        agency_id: str,
        resource_type: str,
    ) -> list[MaskingRule]:
        """Get applicable masking rules"""
        rules = []
        for rule in self.masking_rules.values():
            if not rule.is_active:
                continue
            if rule.resource_type != resource_type:
                continue
            if agency_id in (rule.exceptions or []):
                continue
            if rule.applies_to_agencies is None or agency_id in rule.applies_to_agencies:
                rules.append(rule)
        return rules

    def apply_masking(
        self,
        data: dict[str, Any],
        masked_fields: list[str],
    ) -> dict[str, Any]:
        """Apply masking to data fields"""
        result = data.copy()
        for field in masked_fields:
            if field in result:
                result[field] = self._mask_value(result[field], field)
        return result

    def _mask_value(self, value: Any, field_name: str) -> str:
        """Mask a value based on field type"""
        if value is None:
            return "[MASKED]"

        str_value = str(value)

        # SSN masking
        if "ssn" in field_name.lower():
            if len(str_value) >= 4:
                return "***-**-" + str_value[-4:]
            return "[MASKED]"

        # Date masking
        if "date" in field_name.lower() or "dob" in field_name.lower():
            return "[DATE MASKED]"

        # Phone masking
        if "phone" in field_name.lower():
            if len(str_value) >= 4:
                return "***-***-" + str_value[-4:]
            return "[MASKED]"

        # Address masking
        if "address" in field_name.lower():
            return "[ADDRESS MASKED]"

        # Default masking
        if len(str_value) <= 4:
            return "****"
        return str_value[:2] + "*" * (len(str_value) - 4) + str_value[-2:]

    def grant_agency_permission(
        self,
        requesting_agency: str,
        target_agency: str,
        resource_types: list[str],
        granted_by: str,
    ) -> None:
        """Grant permission for an agency to access another agency's data"""
        if requesting_agency not in self.agency_permissions:
            self.agency_permissions[requesting_agency] = {}
        self.agency_permissions[requesting_agency][target_agency] = resource_types

        self._log_audit(
            event_type=AuditEventType.PERMISSION_CHANGE,
            agency_id=requesting_agency,
            user_id=granted_by,
            user_name=granted_by,
            resource_type="permission",
            resource_id=None,
            action="grant",
            details={
                "target_agency": target_agency,
                "resource_types": resource_types,
            },
        )

    def revoke_agency_permission(
        self,
        requesting_agency: str,
        target_agency: str,
        revoked_by: str,
    ) -> None:
        """Revoke permission for an agency"""
        if requesting_agency in self.agency_permissions:
            self.agency_permissions[requesting_agency].pop(target_agency, None)

        self._log_audit(
            event_type=AuditEventType.PERMISSION_CHANGE,
            agency_id=requesting_agency,
            user_id=revoked_by,
            user_name=revoked_by,
            resource_type="permission",
            resource_id=None,
            action="revoke",
            details={"target_agency": target_agency},
        )

    def revoke_user_access(
        self,
        agency_id: str,
        user_id: str,
        revoked_by: str,
        reason: str,
    ) -> None:
        """Revoke access for a specific user"""
        if agency_id not in self.revoked_access:
            self.revoked_access[agency_id] = []
        if user_id not in self.revoked_access[agency_id]:
            self.revoked_access[agency_id].append(user_id)

        self._log_audit(
            event_type=AuditEventType.PERMISSION_CHANGE,
            agency_id=agency_id,
            user_id=revoked_by,
            user_name=revoked_by,
            resource_type="user_access",
            resource_id=user_id,
            action="revoke",
            details={"reason": reason},
        )

    def restore_user_access(
        self,
        agency_id: str,
        user_id: str,
        restored_by: str,
    ) -> None:
        """Restore access for a previously revoked user"""
        if agency_id in self.revoked_access:
            if user_id in self.revoked_access[agency_id]:
                self.revoked_access[agency_id].remove(user_id)

        self._log_audit(
            event_type=AuditEventType.PERMISSION_CHANGE,
            agency_id=agency_id,
            user_id=restored_by,
            user_name=restored_by,
            resource_type="user_access",
            resource_id=user_id,
            action="restore",
            details={},
        )

    def _log_access(
        self,
        request: AccessRequest,
        response: AccessResponse,
    ) -> None:
        """Log an access evaluation"""
        self._log_audit(
            event_type=AuditEventType.DATA_ACCESS,
            agency_id=request.requesting_agency,
            user_id=request.requesting_user,
            user_name=request.requesting_user,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            action=request.action,
            details={
                "target_agency": request.target_agency,
                "fields_requested": request.fields_requested,
            },
            access_decision=response.decision,
            masked_fields=response.masked_fields,
        )

    def _log_access_denied(
        self,
        request: AccessRequest,
        reason: str,
    ) -> None:
        """Log an access denial"""
        self._log_audit(
            event_type=AuditEventType.ACCESS_DENIED,
            agency_id=request.requesting_agency,
            user_id=request.requesting_user,
            user_name=request.requesting_user,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            action=request.action,
            details={
                "target_agency": request.target_agency,
                "reason": reason,
            },
            access_decision=AccessDecision.DENY,
        )

    def _log_audit(
        self,
        event_type: AuditEventType,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
        access_decision: AccessDecision | None = None,
        masked_fields: list[str] | None = None,
    ) -> FederatedAuditEntry:
        """Log an audit entry"""
        entry = FederatedAuditEntry(
            event_type=event_type,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            access_decision=access_decision,
            masked_fields=masked_fields,
        )
        self.audit_log.append(entry)
        return entry

    def log_data_query(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        query_text: str,
        resource_type: str,
        result_count: int,
        ip_address: str | None = None,
    ) -> FederatedAuditEntry:
        """Log a data query for CJIS compliance"""
        return self._log_audit(
            event_type=AuditEventType.DATA_QUERY,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=None,
            action="query",
            details={"query_text": self._hash_query(query_text)},
            ip_address=ip_address,
        )

    def log_data_export(
        self,
        agency_id: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        record_count: int,
        export_format: str,
        ip_address: str | None = None,
    ) -> FederatedAuditEntry:
        """Log a data export for CJIS compliance"""
        return self._log_audit(
            event_type=AuditEventType.DATA_EXPORT,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=None,
            action="export",
            details={
                "record_count": record_count,
                "export_format": export_format,
            },
            ip_address=ip_address,
        )

    def log_data_share(
        self,
        from_agency: str,
        to_agency: str,
        user_id: str,
        user_name: str,
        resource_type: str,
        record_count: int,
        ip_address: str | None = None,
    ) -> FederatedAuditEntry:
        """Log data sharing between agencies"""
        return self._log_audit(
            event_type=AuditEventType.DATA_SHARE,
            agency_id=from_agency,
            user_id=user_id,
            user_name=user_name,
            resource_type=resource_type,
            resource_id=None,
            action="share",
            details={
                "to_agency": to_agency,
                "record_count": record_count,
            },
            ip_address=ip_address,
        )

    def _hash_query(self, query_text: str) -> str:
        """Hash query text for audit logging (privacy)"""
        return hashlib.sha256(query_text.encode()).hexdigest()[:16]

    def get_audit_log(
        self,
        agency_id: str | None = None,
        event_type: AuditEventType | None = None,
        user_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 1000,
    ) -> list[FederatedAuditEntry]:
        """Get audit log entries with filtering"""
        entries = self.audit_log.copy()

        if agency_id:
            entries = [e for e in entries if e.agency_id == agency_id]
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        if until:
            entries = [e for e in entries if e.timestamp <= until]

        # Sort by timestamp descending
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_compliance_report(
        self,
        agency_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """Generate CJIS compliance report for an agency"""
        entries = self.get_audit_log(
            agency_id=agency_id,
            since=start_date,
            until=end_date,
            limit=10000,
        )

        # Aggregate statistics
        stats = {
            "total_events": len(entries),
            "by_event_type": {},
            "by_access_decision": {},
            "unique_users": set(),
            "policy_violations": 0,
            "access_denials": 0,
            "data_exports": 0,
            "data_shares": 0,
        }

        for entry in entries:
            # Count by event type
            event_type = entry.event_type.value
            stats["by_event_type"][event_type] = (
                stats["by_event_type"].get(event_type, 0) + 1
            )

            # Count by access decision
            if entry.access_decision:
                decision = entry.access_decision.value
                stats["by_access_decision"][decision] = (
                    stats["by_access_decision"].get(decision, 0) + 1
                )

            # Track unique users
            stats["unique_users"].add(entry.user_id)

            # Count specific events
            if entry.event_type == AuditEventType.POLICY_VIOLATION:
                stats["policy_violations"] += 1
            elif entry.event_type == AuditEventType.ACCESS_DENIED:
                stats["access_denials"] += 1
            elif entry.event_type == AuditEventType.DATA_EXPORT:
                stats["data_exports"] += 1
            elif entry.event_type == AuditEventType.DATA_SHARE:
                stats["data_shares"] += 1

        stats["unique_users"] = len(stats["unique_users"])

        return {
            "agency_id": agency_id,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "statistics": stats,
            "compliance_status": "compliant" if stats["policy_violations"] == 0 else "review_required",
            "generated_at": datetime.utcnow().isoformat(),
        }

    def cleanup_expired_logs(self) -> int:
        """Remove expired audit log entries based on retention policy"""
        now = datetime.utcnow()
        original_count = len(self.audit_log)
        self.audit_log = [
            entry for entry in self.audit_log
            if entry.retention_until > now
        ]
        return original_count - len(self.audit_log)


# Create singleton instance
security_manager = ZeroTrustSecurityManager()
