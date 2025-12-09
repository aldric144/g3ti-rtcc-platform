"""
G3TI RTCC-UIP Multi-Agency Federation Engine
Phase 10: Multi-Agency Intelligence Hub & Interoperability

This module provides multi-agency data federation, cross-jurisdiction
intelligence workflows, and interoperability standards.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class AgencyType(str, Enum):
    """Types of partner agencies"""
    POLICE_DEPARTMENT = "police_department"
    SHERIFF_OFFICE = "sheriff_office"
    STATE_POLICE = "state_police"
    FEDERAL_AGENCY = "federal_agency"
    FUSION_CENTER = "fusion_center"
    TASK_FORCE = "task_force"
    TRANSIT_POLICE = "transit_police"
    UNIVERSITY_POLICE = "university_police"
    COUNTY_INTELLIGENCE = "county_intelligence"
    REGIONAL_CENTER = "regional_center"


class AgencyStatus(str, Enum):
    """Agency registration status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    INACTIVE = "inactive"


class DataSharingLevel(str, Enum):
    """Data sharing permission levels"""
    NONE = "none"
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    FULL = "full"


class DataCategory(str, Enum):
    """Categories of data that can be shared"""
    PERSONS = "persons"
    VEHICLES = "vehicles"
    INCIDENTS = "incidents"
    ADDRESSES = "addresses"
    FIREARMS = "firearms"
    PHONE_NUMBERS = "phone_numbers"
    REPORTS = "reports"
    CAD_EVENTS = "cad_events"
    BOLOS = "bolos"
    INTELLIGENCE = "intelligence"
    OFFICER_SAFETY = "officer_safety"
    TACTICAL = "tactical"
    ANALYTICS = "analytics"


class AccessLevel(str, Enum):
    """Access levels for federated data"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"
    ADMIN = "admin"


class SyncDirection(str, Enum):
    """Data synchronization direction"""
    PULL = "pull"
    PUSH = "push"
    BIDIRECTIONAL = "bidirectional"


class PartnerAgency:
    """Represents a registered partner agency"""

    def __init__(
        self,
        agency_id: str,
        name: str,
        agency_type: AgencyType,
        ori_number: str,
        jurisdiction: str,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
        api_endpoint: str | None = None,
        status: AgencyStatus = AgencyStatus.PENDING,
    ):
        self.id = agency_id
        self.name = name
        self.agency_type = agency_type
        self.ori_number = ori_number
        self.jurisdiction = jurisdiction
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.api_endpoint = api_endpoint
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.last_sync_at: datetime | None = None
        self.access_tokens: list[AgencyAccessToken] = []
        self.data_sharing_agreement: DataSharingAgreement | None = None


class AgencyAccessToken:
    """Access token for partner agency API access"""

    def __init__(
        self,
        agency_id: str,
        token: str,
        scope: list[str],
        expires_at: datetime,
        created_by: str,
    ):
        self.id = str(uuid4())
        self.agency_id = agency_id
        self.token = token
        self.scope = scope
        self.expires_at = expires_at
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.last_used_at: datetime | None = None
        self.is_revoked = False
        self.revoked_at: datetime | None = None


class DataSharingAgreement:
    """CJIS-compliant data sharing agreement between agencies"""

    def __init__(
        self,
        agency_id: str,
        agreement_number: str,
        effective_date: datetime,
        expiration_date: datetime,
        sharing_level: DataSharingLevel,
        allowed_categories: list[DataCategory],
        restricted_fields: list[str],
        sync_direction: SyncDirection,
        requires_audit: bool = True,
        requires_encryption: bool = True,
    ):
        self.id = str(uuid4())
        self.agency_id = agency_id
        self.agreement_number = agreement_number
        self.effective_date = effective_date
        self.expiration_date = expiration_date
        self.sharing_level = sharing_level
        self.allowed_categories = allowed_categories
        self.restricted_fields = restricted_fields
        self.sync_direction = sync_direction
        self.requires_audit = requires_audit
        self.requires_encryption = requires_encryption
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        self.signed_by_local: str | None = None
        self.signed_by_partner: str | None = None
        self.signed_at: datetime | None = None


class AccessPolicy:
    """Access policy for data sharing"""

    def __init__(
        self,
        agency_id: str,
        category: DataCategory,
        access_level: AccessLevel,
        field_restrictions: list[str] | None = None,
        time_restrictions: dict[str, Any] | None = None,
        geo_restrictions: dict[str, Any] | None = None,
    ):
        self.id = str(uuid4())
        self.agency_id = agency_id
        self.category = category
        self.access_level = access_level
        self.field_restrictions = field_restrictions or []
        self.time_restrictions = time_restrictions or {}
        self.geo_restrictions = geo_restrictions or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True


class FederatedQuery:
    """Represents a federated query across agencies"""

    def __init__(
        self,
        query_id: str,
        requesting_agency: str,
        requesting_user: str,
        query_type: str,
        query_params: dict[str, Any],
        target_agencies: list[str],
    ):
        self.id = query_id
        self.requesting_agency = requesting_agency
        self.requesting_user = requesting_user
        self.query_type = query_type
        self.query_params = query_params
        self.target_agencies = target_agencies
        self.created_at = datetime.utcnow()
        self.completed_at: datetime | None = None
        self.results: list[FederatedQueryResult] = []
        self.status = "pending"
        self.error_message: str | None = None


class FederatedQueryResult:
    """Result from a single agency in a federated query"""

    def __init__(
        self,
        query_id: str,
        source_agency: str,
        result_count: int,
        results: list[dict[str, Any]],
        confidence_score: float,
        response_time_ms: int,
    ):
        self.id = str(uuid4())
        self.query_id = query_id
        self.source_agency = source_agency
        self.result_count = result_count
        self.results = results
        self.confidence_score = confidence_score
        self.response_time_ms = response_time_ms
        self.created_at = datetime.utcnow()
        self.masked_fields: list[str] = []


class SyncOperation:
    """Data synchronization operation between agencies"""

    def __init__(
        self,
        agency_id: str,
        direction: SyncDirection,
        categories: list[DataCategory],
        initiated_by: str,
    ):
        self.id = str(uuid4())
        self.agency_id = agency_id
        self.direction = direction
        self.categories = categories
        self.initiated_by = initiated_by
        self.started_at = datetime.utcnow()
        self.completed_at: datetime | None = None
        self.status = "in_progress"
        self.records_processed = 0
        self.records_synced = 0
        self.records_failed = 0
        self.error_message: str | None = None


class AuditLogEntry:
    """Audit log entry for federated operations"""

    def __init__(
        self,
        operation_type: str,
        agency_id: str,
        user_id: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
    ):
        self.id = str(uuid4())
        self.operation_type = operation_type
        self.agency_id = agency_id
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.details = details
        self.ip_address = ip_address
        self.timestamp = datetime.utcnow()


class FederationRegistry:
    """Registry for managing partner agencies"""

    def __init__(self):
        self.agencies: dict[str, PartnerAgency] = {}
        self.agreements: dict[str, DataSharingAgreement] = {}
        self.tokens: dict[str, AgencyAccessToken] = {}

    def register_agency(
        self,
        name: str,
        agency_type: AgencyType,
        ori_number: str,
        jurisdiction: str,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
        api_endpoint: str | None = None,
    ) -> PartnerAgency:
        """Register a new partner agency"""
        agency_id = str(uuid4())
        agency = PartnerAgency(
            agency_id=agency_id,
            name=name,
            agency_type=agency_type,
            ori_number=ori_number,
            jurisdiction=jurisdiction,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            api_endpoint=api_endpoint,
        )
        self.agencies[agency_id] = agency
        return agency

    def get_agency(self, agency_id: str) -> PartnerAgency | None:
        """Get agency by ID"""
        return self.agencies.get(agency_id)

    def get_agency_by_ori(self, ori_number: str) -> PartnerAgency | None:
        """Get agency by ORI number"""
        for agency in self.agencies.values():
            if agency.ori_number == ori_number:
                return agency
        return None

    def list_agencies(
        self,
        status: AgencyStatus | None = None,
        agency_type: AgencyType | None = None,
    ) -> list[PartnerAgency]:
        """List all registered agencies with optional filtering"""
        agencies = list(self.agencies.values())
        if status:
            agencies = [a for a in agencies if a.status == status]
        if agency_type:
            agencies = [a for a in agencies if a.agency_type == agency_type]
        return agencies

    def update_agency_status(
        self,
        agency_id: str,
        status: AgencyStatus,
    ) -> PartnerAgency | None:
        """Update agency status"""
        agency = self.agencies.get(agency_id)
        if agency:
            agency.status = status
            agency.updated_at = datetime.utcnow()
        return agency

    def create_agreement(
        self,
        agency_id: str,
        agreement_number: str,
        effective_date: datetime,
        expiration_date: datetime,
        sharing_level: DataSharingLevel,
        allowed_categories: list[DataCategory],
        restricted_fields: list[str],
        sync_direction: SyncDirection,
    ) -> DataSharingAgreement | None:
        """Create a data sharing agreement for an agency"""
        agency = self.agencies.get(agency_id)
        if not agency:
            return None

        agreement = DataSharingAgreement(
            agency_id=agency_id,
            agreement_number=agreement_number,
            effective_date=effective_date,
            expiration_date=expiration_date,
            sharing_level=sharing_level,
            allowed_categories=allowed_categories,
            restricted_fields=restricted_fields,
            sync_direction=sync_direction,
        )
        self.agreements[agreement.id] = agreement
        agency.data_sharing_agreement = agreement
        return agreement

    def get_agreement(self, agreement_id: str) -> DataSharingAgreement | None:
        """Get agreement by ID"""
        return self.agreements.get(agreement_id)

    def sign_agreement(
        self,
        agreement_id: str,
        local_signer: str,
        partner_signer: str,
    ) -> DataSharingAgreement | None:
        """Sign a data sharing agreement"""
        agreement = self.agreements.get(agreement_id)
        if agreement:
            agreement.signed_by_local = local_signer
            agreement.signed_by_partner = partner_signer
            agreement.signed_at = datetime.utcnow()
            agreement.is_active = True
            # Activate the agency
            agency = self.agencies.get(agreement.agency_id)
            if agency:
                agency.status = AgencyStatus.ACTIVE
        return agreement


class AccessPolicyManager:
    """Manages access policies for data sharing"""

    def __init__(self):
        self.policies: dict[str, AccessPolicy] = {}
        self.agency_policies: dict[str, list[str]] = {}

    def create_policy(
        self,
        agency_id: str,
        category: DataCategory,
        access_level: AccessLevel,
        field_restrictions: list[str] | None = None,
        time_restrictions: dict[str, Any] | None = None,
        geo_restrictions: dict[str, Any] | None = None,
    ) -> AccessPolicy:
        """Create an access policy for an agency"""
        policy = AccessPolicy(
            agency_id=agency_id,
            category=category,
            access_level=access_level,
            field_restrictions=field_restrictions,
            time_restrictions=time_restrictions,
            geo_restrictions=geo_restrictions,
        )
        self.policies[policy.id] = policy
        if agency_id not in self.agency_policies:
            self.agency_policies[agency_id] = []
        self.agency_policies[agency_id].append(policy.id)
        return policy

    def get_policies_for_agency(self, agency_id: str) -> list[AccessPolicy]:
        """Get all policies for an agency"""
        policy_ids = self.agency_policies.get(agency_id, [])
        return [self.policies[pid] for pid in policy_ids if pid in self.policies]

    def get_policy_for_category(
        self,
        agency_id: str,
        category: DataCategory,
    ) -> AccessPolicy | None:
        """Get policy for a specific category"""
        policies = self.get_policies_for_agency(agency_id)
        for policy in policies:
            if policy.category == category and policy.is_active:
                return policy
        return None

    def check_access(
        self,
        agency_id: str,
        category: DataCategory,
        required_level: AccessLevel,
    ) -> bool:
        """Check if agency has required access level for category"""
        policy = self.get_policy_for_category(agency_id, category)
        if not policy:
            return False

        access_hierarchy = [
            AccessLevel.READ_ONLY,
            AccessLevel.READ_WRITE,
            AccessLevel.FULL_ACCESS,
            AccessLevel.ADMIN,
        ]

        policy_level = access_hierarchy.index(policy.access_level)
        required_idx = access_hierarchy.index(required_level)
        return policy_level >= required_idx

    def get_restricted_fields(
        self,
        agency_id: str,
        category: DataCategory,
    ) -> list[str]:
        """Get list of restricted fields for an agency and category"""
        policy = self.get_policy_for_category(agency_id, category)
        if policy:
            return policy.field_restrictions
        return []

    def deactivate_policy(self, policy_id: str) -> bool:
        """Deactivate a policy"""
        policy = self.policies.get(policy_id)
        if policy:
            policy.is_active = False
            policy.updated_at = datetime.utcnow()
            return True
        return False


class RemoteConnector:
    """Connector for remote agency API communication"""

    def __init__(self, agency: PartnerAgency, token: AgencyAccessToken):
        self.agency = agency
        self.token = token
        self.base_url = agency.api_endpoint
        self.timeout = 30

    async def query(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a query against the remote agency API"""
        # In production, this would make actual HTTP requests
        # For now, return a simulated response
        return {
            "status": "success",
            "agency": self.agency.name,
            "endpoint": endpoint,
            "params": params,
            "results": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def push_data(
        self,
        endpoint: str,
        data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Push data to the remote agency"""
        return {
            "status": "success",
            "agency": self.agency.name,
            "endpoint": endpoint,
            "records_sent": len(data),
            "records_accepted": len(data),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def pull_data(
        self,
        endpoint: str,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """Pull data from the remote agency"""
        return {
            "status": "success",
            "agency": self.agency.name,
            "endpoint": endpoint,
            "since": since.isoformat() if since else None,
            "records": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def test_connection(self) -> bool:
        """Test connection to remote agency"""
        # In production, this would ping the remote API
        return self.base_url is not None


class PartnerAgencyDataMapper:
    """Maps data between local and partner agency formats"""

    def __init__(self):
        self.field_mappings: dict[str, dict[str, str]] = {}
        self.value_mappings: dict[str, dict[str, dict[str, str]]] = {}

    def register_field_mapping(
        self,
        agency_id: str,
        local_field: str,
        remote_field: str,
    ) -> None:
        """Register a field mapping for an agency"""
        if agency_id not in self.field_mappings:
            self.field_mappings[agency_id] = {}
        self.field_mappings[agency_id][local_field] = remote_field

    def register_value_mapping(
        self,
        agency_id: str,
        field: str,
        local_value: str,
        remote_value: str,
    ) -> None:
        """Register a value mapping for an agency"""
        if agency_id not in self.value_mappings:
            self.value_mappings[agency_id] = {}
        if field not in self.value_mappings[agency_id]:
            self.value_mappings[agency_id][field] = {}
        self.value_mappings[agency_id][field][local_value] = remote_value

    def map_to_remote(
        self,
        agency_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Map local data to remote agency format"""
        mappings = self.field_mappings.get(agency_id, {})
        value_maps = self.value_mappings.get(agency_id, {})

        result = {}
        for local_field, value in data.items():
            remote_field = mappings.get(local_field, local_field)
            if local_field in value_maps and value in value_maps[local_field]:
                value = value_maps[local_field][value]
            result[remote_field] = value
        return result

    def map_from_remote(
        self,
        agency_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Map remote agency data to local format"""
        mappings = self.field_mappings.get(agency_id, {})
        reverse_mappings = {v: k for k, v in mappings.items()}

        value_maps = self.value_mappings.get(agency_id, {})
        reverse_value_maps: dict[str, dict[str, str]] = {}
        for field, vmap in value_maps.items():
            reverse_value_maps[field] = {v: k for k, v in vmap.items()}

        result = {}
        for remote_field, value in data.items():
            local_field = reverse_mappings.get(remote_field, remote_field)
            if local_field in reverse_value_maps and value in reverse_value_maps[local_field]:
                value = reverse_value_maps[local_field][value]
            result[local_field] = value
        return result


class FederationManager:
    """Main manager for multi-agency federation operations"""

    def __init__(self):
        self.registry = FederationRegistry()
        self.policy_manager = AccessPolicyManager()
        self.data_mapper = PartnerAgencyDataMapper()
        self.queries: dict[str, FederatedQuery] = {}
        self.sync_operations: dict[str, SyncOperation] = {}
        self.audit_log: list[AuditLogEntry] = []
        self.connectors: dict[str, RemoteConnector] = {}

    def register_agency(
        self,
        name: str,
        agency_type: AgencyType,
        ori_number: str,
        jurisdiction: str,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
        api_endpoint: str | None = None,
        registered_by: str = "system",
    ) -> PartnerAgency:
        """Register a new partner agency"""
        agency = self.registry.register_agency(
            name=name,
            agency_type=agency_type,
            ori_number=ori_number,
            jurisdiction=jurisdiction,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            api_endpoint=api_endpoint,
        )

        # Log the registration
        self._log_audit(
            operation_type="agency_registration",
            agency_id=agency.id,
            user_id=registered_by,
            resource_type="agency",
            resource_id=agency.id,
            action="register",
            details={"name": name, "ori_number": ori_number},
        )

        return agency

    def configure_agency(
        self,
        agency_id: str,
        agreement_number: str,
        effective_date: datetime,
        expiration_date: datetime,
        sharing_level: DataSharingLevel,
        allowed_categories: list[DataCategory],
        restricted_fields: list[str],
        sync_direction: SyncDirection,
        configured_by: str = "system",
    ) -> DataSharingAgreement | None:
        """Configure data sharing agreement for an agency"""
        agreement = self.registry.create_agreement(
            agency_id=agency_id,
            agreement_number=agreement_number,
            effective_date=effective_date,
            expiration_date=expiration_date,
            sharing_level=sharing_level,
            allowed_categories=allowed_categories,
            restricted_fields=restricted_fields,
            sync_direction=sync_direction,
        )

        if agreement:
            # Create default policies for allowed categories
            for category in allowed_categories:
                access_level = self._get_access_level_for_sharing(sharing_level)
                self.policy_manager.create_policy(
                    agency_id=agency_id,
                    category=category,
                    access_level=access_level,
                    field_restrictions=restricted_fields,
                )

            # Log the configuration
            self._log_audit(
                operation_type="agency_configuration",
                agency_id=agency_id,
                user_id=configured_by,
                resource_type="agreement",
                resource_id=agreement.id,
                action="configure",
                details={
                    "agreement_number": agreement_number,
                    "sharing_level": sharing_level.value,
                    "categories": [c.value for c in allowed_categories],
                },
            )

        return agreement

    def _get_access_level_for_sharing(
        self,
        sharing_level: DataSharingLevel,
    ) -> AccessLevel:
        """Map sharing level to access level"""
        mapping = {
            DataSharingLevel.NONE: AccessLevel.READ_ONLY,
            DataSharingLevel.MINIMAL: AccessLevel.READ_ONLY,
            DataSharingLevel.STANDARD: AccessLevel.READ_ONLY,
            DataSharingLevel.ENHANCED: AccessLevel.READ_WRITE,
            DataSharingLevel.FULL: AccessLevel.FULL_ACCESS,
        }
        return mapping.get(sharing_level, AccessLevel.READ_ONLY)

    def list_agencies(
        self,
        status: AgencyStatus | None = None,
        agency_type: AgencyType | None = None,
    ) -> list[PartnerAgency]:
        """List all registered agencies"""
        return self.registry.list_agencies(status=status, agency_type=agency_type)

    def get_agency(self, agency_id: str) -> PartnerAgency | None:
        """Get agency by ID"""
        return self.registry.get_agency(agency_id)

    def generate_access_token(
        self,
        agency_id: str,
        scope: list[str],
        expires_in_days: int = 365,
        created_by: str = "system",
    ) -> AgencyAccessToken | None:
        """Generate an access token for a partner agency"""
        agency = self.registry.get_agency(agency_id)
        if not agency or agency.status != AgencyStatus.ACTIVE:
            return None

        token = AgencyAccessToken(
            agency_id=agency_id,
            token=str(uuid4()),
            scope=scope,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            created_by=created_by,
        )
        self.registry.tokens[token.id] = token
        agency.access_tokens.append(token)

        # Log token generation
        self._log_audit(
            operation_type="token_generation",
            agency_id=agency_id,
            user_id=created_by,
            resource_type="token",
            resource_id=token.id,
            action="generate",
            details={"scope": scope, "expires_in_days": expires_in_days},
        )

        return token

    def validate_token(self, token_value: str) -> AgencyAccessToken | None:
        """Validate an access token"""
        for token in self.registry.tokens.values():
            if token.token == token_value:
                if token.is_revoked:
                    return None
                if token.expires_at < datetime.utcnow():
                    return None
                token.last_used_at = datetime.utcnow()
                return token
        return None

    def revoke_token(self, token_id: str, revoked_by: str = "system") -> bool:
        """Revoke an access token"""
        token = self.registry.tokens.get(token_id)
        if token:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()

            self._log_audit(
                operation_type="token_revocation",
                agency_id=token.agency_id,
                user_id=revoked_by,
                resource_type="token",
                resource_id=token_id,
                action="revoke",
                details={},
            )
            return True
        return False

    async def execute_federated_query(
        self,
        requesting_agency: str,
        requesting_user: str,
        query_type: str,
        query_params: dict[str, Any],
        target_agencies: list[str] | None = None,
    ) -> FederatedQuery:
        """Execute a federated query across agencies"""
        query_id = str(uuid4())

        # If no target agencies specified, query all active agencies
        if not target_agencies:
            active_agencies = self.registry.list_agencies(status=AgencyStatus.ACTIVE)
            target_agencies = [a.id for a in active_agencies]

        query = FederatedQuery(
            query_id=query_id,
            requesting_agency=requesting_agency,
            requesting_user=requesting_user,
            query_type=query_type,
            query_params=query_params,
            target_agencies=target_agencies,
        )
        self.queries[query_id] = query

        # Log the query
        self._log_audit(
            operation_type="federated_query",
            agency_id=requesting_agency,
            user_id=requesting_user,
            resource_type="query",
            resource_id=query_id,
            action="execute",
            details={
                "query_type": query_type,
                "target_agencies": target_agencies,
            },
        )

        # Execute queries against each target agency
        for agency_id in target_agencies:
            agency = self.registry.get_agency(agency_id)
            if not agency or agency.status != AgencyStatus.ACTIVE:
                continue

            # Check access policy
            category = self._get_category_for_query_type(query_type)
            if not self.policy_manager.check_access(
                agency_id, category, AccessLevel.READ_ONLY
            ):
                continue

            # Execute query (simulated for now)
            start_time = datetime.utcnow()
            result = FederatedQueryResult(
                query_id=query_id,
                source_agency=agency_id,
                result_count=0,
                results=[],
                confidence_score=1.0,
                response_time_ms=int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                ),
            )

            # Apply field masking
            restricted_fields = self.policy_manager.get_restricted_fields(
                agency_id, category
            )
            result.masked_fields = restricted_fields

            query.results.append(result)

        query.status = "completed"
        query.completed_at = datetime.utcnow()
        return query

    def _get_category_for_query_type(self, query_type: str) -> DataCategory:
        """Map query type to data category"""
        mapping = {
            "person": DataCategory.PERSONS,
            "vehicle": DataCategory.VEHICLES,
            "incident": DataCategory.INCIDENTS,
            "address": DataCategory.ADDRESSES,
            "firearm": DataCategory.FIREARMS,
            "phone": DataCategory.PHONE_NUMBERS,
            "report": DataCategory.REPORTS,
            "cad": DataCategory.CAD_EVENTS,
            "bolo": DataCategory.BOLOS,
        }
        return mapping.get(query_type, DataCategory.INTELLIGENCE)

    async def sync_pull(
        self,
        agency_id: str,
        categories: list[DataCategory],
        initiated_by: str = "system",
    ) -> SyncOperation:
        """Pull data from a partner agency"""
        operation = SyncOperation(
            agency_id=agency_id,
            direction=SyncDirection.PULL,
            categories=categories,
            initiated_by=initiated_by,
        )
        self.sync_operations[operation.id] = operation

        # Log the sync operation
        self._log_audit(
            operation_type="sync_pull",
            agency_id=agency_id,
            user_id=initiated_by,
            resource_type="sync",
            resource_id=operation.id,
            action="pull",
            details={"categories": [c.value for c in categories]},
        )

        # Simulate sync completion
        operation.status = "completed"
        operation.completed_at = datetime.utcnow()

        # Update agency last sync time
        agency = self.registry.get_agency(agency_id)
        if agency:
            agency.last_sync_at = datetime.utcnow()

        return operation

    async def sync_push(
        self,
        agency_id: str,
        categories: list[DataCategory],
        data: list[dict[str, Any]],
        initiated_by: str = "system",
    ) -> SyncOperation:
        """Push data to a partner agency"""
        operation = SyncOperation(
            agency_id=agency_id,
            direction=SyncDirection.PUSH,
            categories=categories,
            initiated_by=initiated_by,
        )
        self.sync_operations[operation.id] = operation

        # Log the sync operation
        self._log_audit(
            operation_type="sync_push",
            agency_id=agency_id,
            user_id=initiated_by,
            resource_type="sync",
            resource_id=operation.id,
            action="push",
            details={
                "categories": [c.value for c in categories],
                "record_count": len(data),
            },
        )

        # Simulate sync completion
        operation.records_processed = len(data)
        operation.records_synced = len(data)
        operation.status = "completed"
        operation.completed_at = datetime.utcnow()

        return operation

    def _log_audit(
        self,
        operation_type: str,
        agency_id: str,
        user_id: str,
        resource_type: str,
        resource_id: str | None,
        action: str,
        details: dict[str, Any],
        ip_address: str | None = None,
    ) -> AuditLogEntry:
        """Log an audit entry"""
        entry = AuditLogEntry(
            operation_type=operation_type,
            agency_id=agency_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
        )
        self.audit_log.append(entry)
        return entry

    def get_audit_log(
        self,
        agency_id: str | None = None,
        operation_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """Get audit log entries with optional filtering"""
        entries = self.audit_log.copy()

        if agency_id:
            entries = [e for e in entries if e.agency_id == agency_id]
        if operation_type:
            entries = [e for e in entries if e.operation_type == operation_type]
        if since:
            entries = [e for e in entries if e.timestamp >= since]

        # Sort by timestamp descending
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]


# Create singleton instance
federation_manager = FederationManager()
