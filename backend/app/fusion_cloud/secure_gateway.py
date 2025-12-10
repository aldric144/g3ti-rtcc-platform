"""
SecureAccessGateway - CJIS-compliant security for G3TI Fusion Cloud

Manages:
- Per-tenant encryption
- Domain separation
- Attribute-based access control (ABAC)
- Clearance-based filtering
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid
import hashlib
import secrets


class AccessDecision(str, Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    AUDIT = "audit"


class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class ClearanceLevel(str, Enum):
    """Security clearance levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ELEVATED = "elevated"
    HIGH = "high"
    TOP = "top"
    COMPARTMENTED = "compartmented"


class DataSensitivity(str, Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AttributeType(str, Enum):
    """Types of attributes for ABAC"""
    USER = "user"
    RESOURCE = "resource"
    ACTION = "action"
    ENVIRONMENT = "environment"
    TENANT = "tenant"
    JURISDICTION = "jurisdiction"
    ROLE = "role"
    CLEARANCE = "clearance"
    TIME = "time"
    LOCATION = "location"


@dataclass
class TenantEncryption:
    """Encryption configuration for a tenant"""
    encryption_id: str
    tenant_id: str
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_id: str = ""
    key_version: int = 1
    key_rotation_days: int = 90
    last_rotation: datetime = field(default_factory=datetime.utcnow)
    next_rotation: Optional[datetime] = None
    kms_provider: str = "internal"
    kms_key_arn: str = ""
    data_at_rest_enabled: bool = True
    data_in_transit_enabled: bool = True
    field_level_encryption: bool = False
    encrypted_fields: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainSeparation:
    """Domain separation configuration for a tenant"""
    domain_id: str
    tenant_id: str
    domain_name: str
    network_segment: str = ""
    vlan_id: int = 0
    subnet_cidr: str = ""
    firewall_rules: List[Dict[str, Any]] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    data_isolation_level: str = "strict"
    cross_domain_allowed: bool = False
    cross_domain_audit: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Attribute:
    """An attribute for ABAC"""
    attribute_id: str
    attribute_type: AttributeType
    name: str
    value: Any
    operator: str = "equals"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyCondition:
    """A condition in an access policy"""
    condition_id: str
    attribute_type: AttributeType
    attribute_name: str
    operator: str
    value: Any
    negate: bool = False


@dataclass
class AccessPolicy:
    """An access control policy"""
    policy_id: str
    name: str
    description: str = ""
    tenant_id: str = ""
    priority: int = 100
    effect: AccessDecision = AccessDecision.DENY
    conditions: List[PolicyCondition] = field(default_factory=list)
    required_clearance: ClearanceLevel = ClearanceLevel.NONE
    required_roles: List[str] = field(default_factory=list)
    required_jurisdictions: List[str] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    denied_actions: List[str] = field(default_factory=list)
    resource_patterns: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    ip_restrictions: List[str] = field(default_factory=list)
    enabled: bool = True
    audit_on_match: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttributeBasedAccess:
    """Attribute-based access control configuration"""
    abac_id: str
    tenant_id: str
    user_id: str
    user_attributes: Dict[str, Any] = field(default_factory=dict)
    clearance_level: ClearanceLevel = ClearanceLevel.STANDARD
    roles: List[str] = field(default_factory=list)
    jurisdictions: List[str] = field(default_factory=list)
    allowed_data_classifications: List[DataSensitivity] = field(default_factory=list)
    allowed_resource_types: List[str] = field(default_factory=list)
    denied_resource_types: List[str] = field(default_factory=list)
    time_based_restrictions: Dict[str, Any] = field(default_factory=dict)
    location_restrictions: List[str] = field(default_factory=list)
    session_timeout_minutes: int = 480
    mfa_required: bool = True
    last_access: Optional[datetime] = None
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClearanceFilter:
    """Clearance-based data filter"""
    filter_id: str
    name: str
    min_clearance: ClearanceLevel = ClearanceLevel.NONE
    max_sensitivity: DataSensitivity = DataSensitivity.RESTRICTED
    redaction_rules: Dict[str, Any] = field(default_factory=dict)
    field_masks: Dict[str, str] = field(default_factory=dict)
    excluded_fields: List[str] = field(default_factory=list)
    jurisdiction_filter: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """An access request for evaluation"""
    request_id: str
    tenant_id: str
    user_id: str
    resource_type: str
    resource_id: str
    action: str
    user_clearance: ClearanceLevel = ClearanceLevel.NONE
    user_roles: List[str] = field(default_factory=list)
    user_jurisdictions: List[str] = field(default_factory=list)
    user_attributes: Dict[str, Any] = field(default_factory=dict)
    resource_sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    resource_jurisdiction: str = ""
    source_ip: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessResult:
    """Result of an access control decision"""
    result_id: str
    request_id: str
    decision: AccessDecision
    matched_policy_id: str = ""
    matched_policy_name: str = ""
    reason: str = ""
    conditions_evaluated: int = 0
    conditions_matched: int = 0
    redaction_applied: bool = False
    redacted_fields: List[str] = field(default_factory=list)
    audit_logged: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    """An audit log entry"""
    audit_id: str
    tenant_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    decision: AccessDecision
    policy_id: str = ""
    source_ip: str = ""
    user_agent: str = ""
    session_id: str = ""
    request_details: Dict[str, Any] = field(default_factory=dict)
    response_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    chain_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayMetrics:
    """Metrics for the secure gateway"""
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    conditional_requests: int = 0
    total_policies: int = 0
    active_policies: int = 0
    total_tenants_encrypted: int = 0
    total_audit_entries: int = 0
    requests_24h: int = 0
    denials_24h: int = 0


class SecureAccessGateway:
    """
    Manages CJIS-compliant security for the G3TI Fusion Cloud.
    
    Provides:
    - Per-tenant encryption
    - Domain separation
    - Attribute-based access control (ABAC)
    - Clearance-based filtering
    - Zero-trust tenant gateway
    """
    
    def __init__(self):
        self._tenant_encryption: Dict[str, TenantEncryption] = {}
        self._domain_separation: Dict[str, DomainSeparation] = {}
        self._policies: Dict[str, AccessPolicy] = {}
        self._abac_configs: Dict[str, AttributeBasedAccess] = {}
        self._clearance_filters: Dict[str, ClearanceFilter] = {}
        self._audit_log: List[AuditEntry] = []
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
        self._max_audit_entries = 100000
        self._last_chain_hash = ""
        
        self._init_default_policies()
        self._init_default_filters()
    
    def _init_default_policies(self) -> None:
        """Initialize default access policies"""
        default_policies = [
            AccessPolicy(
                policy_id="policy-deny-all",
                name="Default Deny All",
                description="Default policy to deny all access",
                priority=1000,
                effect=AccessDecision.DENY,
            ),
            AccessPolicy(
                policy_id="policy-allow-read-basic",
                name="Allow Basic Read Access",
                description="Allow read access for basic clearance",
                priority=100,
                effect=AccessDecision.ALLOW,
                required_clearance=ClearanceLevel.BASIC,
                allowed_actions=["read", "list", "view"],
            ),
            AccessPolicy(
                policy_id="policy-allow-write-standard",
                name="Allow Standard Write Access",
                description="Allow write access for standard clearance",
                priority=90,
                effect=AccessDecision.ALLOW,
                required_clearance=ClearanceLevel.STANDARD,
                allowed_actions=["read", "list", "view", "create", "update"],
            ),
            AccessPolicy(
                policy_id="policy-allow-admin-elevated",
                name="Allow Admin Access",
                description="Allow admin access for elevated clearance",
                priority=80,
                effect=AccessDecision.ALLOW,
                required_clearance=ClearanceLevel.ELEVATED,
                allowed_actions=["read", "list", "view", "create", "update", "delete", "admin"],
            ),
        ]
        
        for policy in default_policies:
            self._policies[policy.policy_id] = policy
    
    def _init_default_filters(self) -> None:
        """Initialize default clearance filters"""
        default_filters = [
            ClearanceFilter(
                filter_id="filter-basic",
                name="Basic Clearance Filter",
                min_clearance=ClearanceLevel.BASIC,
                max_sensitivity=DataSensitivity.INTERNAL,
                field_masks={
                    "ssn": "***-**-****",
                    "dob": "**/**/****",
                    "phone": "***-***-****",
                },
                excluded_fields=["ssn", "financial_data", "medical_records"],
            ),
            ClearanceFilter(
                filter_id="filter-standard",
                name="Standard Clearance Filter",
                min_clearance=ClearanceLevel.STANDARD,
                max_sensitivity=DataSensitivity.RESTRICTED,
                field_masks={
                    "ssn": "***-**-****",
                },
                excluded_fields=["financial_data", "medical_records"],
            ),
            ClearanceFilter(
                filter_id="filter-elevated",
                name="Elevated Clearance Filter",
                min_clearance=ClearanceLevel.ELEVATED,
                max_sensitivity=DataSensitivity.CONFIDENTIAL,
            ),
            ClearanceFilter(
                filter_id="filter-high",
                name="High Clearance Filter",
                min_clearance=ClearanceLevel.HIGH,
                max_sensitivity=DataSensitivity.SECRET,
            ),
        ]
        
        for filter_config in default_filters:
            self._clearance_filters[filter_config.filter_id] = filter_config
    
    def configure_tenant_encryption(
        self,
        tenant_id: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_rotation_days: int = 90,
        kms_provider: str = "internal",
        data_at_rest_enabled: bool = True,
        data_in_transit_enabled: bool = True,
        field_level_encryption: bool = False,
        encrypted_fields: List[str] = None,
    ) -> Optional[TenantEncryption]:
        """Configure encryption for a tenant"""
        encryption_id = f"enc-{uuid.uuid4().hex[:12]}"
        key_id = f"key-{secrets.token_hex(16)}"
        
        encryption = TenantEncryption(
            encryption_id=encryption_id,
            tenant_id=tenant_id,
            algorithm=algorithm,
            key_id=key_id,
            key_rotation_days=key_rotation_days,
            next_rotation=datetime.utcnow() + timedelta(days=key_rotation_days),
            kms_provider=kms_provider,
            data_at_rest_enabled=data_at_rest_enabled,
            data_in_transit_enabled=data_in_transit_enabled,
            field_level_encryption=field_level_encryption,
            encrypted_fields=encrypted_fields or [],
        )
        
        self._tenant_encryption[tenant_id] = encryption
        
        self._record_event("encryption_configured", {
            "tenant_id": tenant_id,
            "encryption_id": encryption_id,
            "algorithm": algorithm.value,
        })
        self._notify_callbacks("encryption_configured", encryption)
        
        return encryption
    
    def rotate_encryption_key(self, tenant_id: str) -> bool:
        """Rotate encryption key for a tenant"""
        if tenant_id not in self._tenant_encryption:
            return False
        
        encryption = self._tenant_encryption[tenant_id]
        encryption.key_version += 1
        encryption.key_id = f"key-{secrets.token_hex(16)}"
        encryption.last_rotation = datetime.utcnow()
        encryption.next_rotation = datetime.utcnow() + timedelta(days=encryption.key_rotation_days)
        
        self._record_event("encryption_key_rotated", {
            "tenant_id": tenant_id,
            "key_version": encryption.key_version,
        })
        
        return True
    
    def get_tenant_encryption(self, tenant_id: str) -> Optional[TenantEncryption]:
        """Get encryption configuration for a tenant"""
        return self._tenant_encryption.get(tenant_id)
    
    def configure_domain_separation(
        self,
        tenant_id: str,
        domain_name: str,
        network_segment: str = "",
        vlan_id: int = 0,
        subnet_cidr: str = "",
        allowed_domains: List[str] = None,
        blocked_domains: List[str] = None,
        data_isolation_level: str = "strict",
        cross_domain_allowed: bool = False,
    ) -> Optional[DomainSeparation]:
        """Configure domain separation for a tenant"""
        domain_id = f"domain-{uuid.uuid4().hex[:12]}"
        
        domain = DomainSeparation(
            domain_id=domain_id,
            tenant_id=tenant_id,
            domain_name=domain_name,
            network_segment=network_segment,
            vlan_id=vlan_id,
            subnet_cidr=subnet_cidr,
            allowed_domains=allowed_domains or [],
            blocked_domains=blocked_domains or [],
            data_isolation_level=data_isolation_level,
            cross_domain_allowed=cross_domain_allowed,
        )
        
        self._domain_separation[tenant_id] = domain
        
        self._record_event("domain_configured", {
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "domain_name": domain_name,
        })
        self._notify_callbacks("domain_configured", domain)
        
        return domain
    
    def get_domain_separation(self, tenant_id: str) -> Optional[DomainSeparation]:
        """Get domain separation configuration for a tenant"""
        return self._domain_separation.get(tenant_id)
    
    def check_cross_domain_access(
        self,
        source_tenant_id: str,
        target_tenant_id: str,
    ) -> bool:
        """Check if cross-domain access is allowed"""
        source_domain = self._domain_separation.get(source_tenant_id)
        target_domain = self._domain_separation.get(target_tenant_id)
        
        if not source_domain or not target_domain:
            return True
        
        if not source_domain.cross_domain_allowed:
            return False
        
        if target_domain.domain_name in source_domain.blocked_domains:
            return False
        
        if source_domain.allowed_domains:
            if target_domain.domain_name not in source_domain.allowed_domains:
                return False
        
        return True
    
    def create_policy(
        self,
        name: str,
        effect: AccessDecision,
        tenant_id: str = "",
        priority: int = 100,
        required_clearance: ClearanceLevel = ClearanceLevel.NONE,
        required_roles: List[str] = None,
        required_jurisdictions: List[str] = None,
        allowed_actions: List[str] = None,
        denied_actions: List[str] = None,
        resource_patterns: List[str] = None,
        conditions: List[PolicyCondition] = None,
        description: str = "",
        created_by: str = "",
    ) -> Optional[AccessPolicy]:
        """Create an access policy"""
        policy_id = f"policy-{uuid.uuid4().hex[:12]}"
        
        policy = AccessPolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            tenant_id=tenant_id,
            priority=priority,
            effect=effect,
            conditions=conditions or [],
            required_clearance=required_clearance,
            required_roles=required_roles or [],
            required_jurisdictions=required_jurisdictions or [],
            allowed_actions=allowed_actions or [],
            denied_actions=denied_actions or [],
            resource_patterns=resource_patterns or [],
            created_by=created_by,
        )
        
        self._policies[policy_id] = policy
        
        self._record_event("policy_created", {
            "policy_id": policy_id,
            "name": name,
            "effect": effect.value,
        })
        self._notify_callbacks("policy_created", policy)
        
        return policy
    
    def update_policy(
        self,
        policy_id: str,
        enabled: bool = None,
        priority: int = None,
        required_clearance: ClearanceLevel = None,
        allowed_actions: List[str] = None,
        denied_actions: List[str] = None,
    ) -> bool:
        """Update an access policy"""
        if policy_id not in self._policies:
            return False
        
        policy = self._policies[policy_id]
        
        if enabled is not None:
            policy.enabled = enabled
        if priority is not None:
            policy.priority = priority
        if required_clearance is not None:
            policy.required_clearance = required_clearance
        if allowed_actions is not None:
            policy.allowed_actions = allowed_actions
        if denied_actions is not None:
            policy.denied_actions = denied_actions
        
        policy.updated_at = datetime.utcnow()
        
        self._record_event("policy_updated", {"policy_id": policy_id})
        
        return True
    
    def delete_policy(self, policy_id: str) -> bool:
        """Delete an access policy"""
        if policy_id not in self._policies:
            return False
        
        if policy_id.startswith("policy-deny-all") or policy_id.startswith("policy-allow"):
            return False
        
        del self._policies[policy_id]
        
        self._record_event("policy_deleted", {"policy_id": policy_id})
        
        return True
    
    def get_policy(self, policy_id: str) -> Optional[AccessPolicy]:
        """Get a policy by ID"""
        return self._policies.get(policy_id)
    
    def get_policies_for_tenant(self, tenant_id: str) -> List[AccessPolicy]:
        """Get policies for a tenant"""
        return [
            p for p in self._policies.values()
            if p.tenant_id == tenant_id or p.tenant_id == ""
        ]
    
    def configure_abac(
        self,
        tenant_id: str,
        user_id: str,
        clearance_level: ClearanceLevel = ClearanceLevel.STANDARD,
        roles: List[str] = None,
        jurisdictions: List[str] = None,
        allowed_data_classifications: List[DataSensitivity] = None,
        user_attributes: Dict[str, Any] = None,
        session_timeout_minutes: int = 480,
        mfa_required: bool = True,
    ) -> Optional[AttributeBasedAccess]:
        """Configure ABAC for a user"""
        abac_id = f"abac-{uuid.uuid4().hex[:12]}"
        
        if allowed_data_classifications is None:
            allowed_data_classifications = [
                DataSensitivity.PUBLIC,
                DataSensitivity.INTERNAL,
            ]
            if clearance_level in [ClearanceLevel.STANDARD, ClearanceLevel.ELEVATED, ClearanceLevel.HIGH, ClearanceLevel.TOP]:
                allowed_data_classifications.append(DataSensitivity.RESTRICTED)
            if clearance_level in [ClearanceLevel.ELEVATED, ClearanceLevel.HIGH, ClearanceLevel.TOP]:
                allowed_data_classifications.append(DataSensitivity.CONFIDENTIAL)
            if clearance_level in [ClearanceLevel.HIGH, ClearanceLevel.TOP]:
                allowed_data_classifications.append(DataSensitivity.SECRET)
            if clearance_level == ClearanceLevel.TOP:
                allowed_data_classifications.append(DataSensitivity.TOP_SECRET)
        
        abac = AttributeBasedAccess(
            abac_id=abac_id,
            tenant_id=tenant_id,
            user_id=user_id,
            user_attributes=user_attributes or {},
            clearance_level=clearance_level,
            roles=roles or [],
            jurisdictions=jurisdictions or [],
            allowed_data_classifications=allowed_data_classifications,
            session_timeout_minutes=session_timeout_minutes,
            mfa_required=mfa_required,
        )
        
        key = f"{tenant_id}:{user_id}"
        self._abac_configs[key] = abac
        
        self._record_event("abac_configured", {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "clearance_level": clearance_level.value,
        })
        self._notify_callbacks("abac_configured", abac)
        
        return abac
    
    def get_abac(self, tenant_id: str, user_id: str) -> Optional[AttributeBasedAccess]:
        """Get ABAC configuration for a user"""
        key = f"{tenant_id}:{user_id}"
        return self._abac_configs.get(key)
    
    def evaluate_access(self, request: AccessRequest) -> AccessResult:
        """Evaluate an access request"""
        result_id = f"result-{uuid.uuid4().hex[:8]}"
        
        abac_key = f"{request.tenant_id}:{request.user_id}"
        abac = self._abac_configs.get(abac_key)
        
        if not abac:
            result = AccessResult(
                result_id=result_id,
                request_id=request.request_id,
                decision=AccessDecision.DENY,
                reason="No ABAC configuration found for user",
            )
            self._log_access(request, result)
            return result
        
        clearance_ok = self._check_clearance(
            abac.clearance_level,
            request.resource_sensitivity,
        )
        
        if not clearance_ok:
            result = AccessResult(
                result_id=result_id,
                request_id=request.request_id,
                decision=AccessDecision.DENY,
                reason=f"Insufficient clearance level for {request.resource_sensitivity.value} data",
            )
            self._log_access(request, result)
            return result
        
        applicable_policies = self._get_applicable_policies(request, abac)
        applicable_policies.sort(key=lambda p: p.priority)
        
        for policy in applicable_policies:
            if not policy.enabled:
                continue
            
            match, conditions_evaluated, conditions_matched = self._evaluate_policy(
                policy, request, abac
            )
            
            if match:
                redaction_applied = False
                redacted_fields: List[str] = []
                
                if policy.effect == AccessDecision.ALLOW:
                    clearance_filter = self._get_clearance_filter(abac.clearance_level)
                    if clearance_filter:
                        redaction_applied = True
                        redacted_fields = clearance_filter.excluded_fields
                
                result = AccessResult(
                    result_id=result_id,
                    request_id=request.request_id,
                    decision=policy.effect,
                    matched_policy_id=policy.policy_id,
                    matched_policy_name=policy.name,
                    reason=f"Matched policy: {policy.name}",
                    conditions_evaluated=conditions_evaluated,
                    conditions_matched=conditions_matched,
                    redaction_applied=redaction_applied,
                    redacted_fields=redacted_fields,
                    audit_logged=policy.audit_on_match,
                )
                
                self._log_access(request, result)
                self._notify_callbacks("access_evaluated", {
                    "request": request,
                    "result": result,
                })
                
                return result
        
        result = AccessResult(
            result_id=result_id,
            request_id=request.request_id,
            decision=AccessDecision.DENY,
            matched_policy_id="policy-deny-all",
            matched_policy_name="Default Deny All",
            reason="No matching allow policy found",
        )
        
        self._log_access(request, result)
        
        return result
    
    def create_clearance_filter(
        self,
        name: str,
        min_clearance: ClearanceLevel,
        max_sensitivity: DataSensitivity,
        redaction_rules: Dict[str, Any] = None,
        field_masks: Dict[str, str] = None,
        excluded_fields: List[str] = None,
        jurisdiction_filter: List[str] = None,
    ) -> Optional[ClearanceFilter]:
        """Create a clearance filter"""
        filter_id = f"filter-{uuid.uuid4().hex[:8]}"
        
        clearance_filter = ClearanceFilter(
            filter_id=filter_id,
            name=name,
            min_clearance=min_clearance,
            max_sensitivity=max_sensitivity,
            redaction_rules=redaction_rules or {},
            field_masks=field_masks or {},
            excluded_fields=excluded_fields or [],
            jurisdiction_filter=jurisdiction_filter or [],
        )
        
        self._clearance_filters[filter_id] = clearance_filter
        
        self._record_event("clearance_filter_created", {
            "filter_id": filter_id,
            "name": name,
        })
        
        return clearance_filter
    
    def get_clearance_filter(self, filter_id: str) -> Optional[ClearanceFilter]:
        """Get a clearance filter by ID"""
        return self._clearance_filters.get(filter_id)
    
    def apply_data_redaction(
        self,
        data: Dict[str, Any],
        clearance_level: ClearanceLevel,
    ) -> Dict[str, Any]:
        """Apply data redaction based on clearance level"""
        clearance_filter = self._get_clearance_filter(clearance_level)
        
        if not clearance_filter:
            return data
        
        redacted_data = data.copy()
        
        for field in clearance_filter.excluded_fields:
            if field in redacted_data:
                del redacted_data[field]
        
        for field, mask in clearance_filter.field_masks.items():
            if field in redacted_data:
                redacted_data[field] = mask
        
        return redacted_data
    
    def get_audit_log(
        self,
        tenant_id: str = None,
        user_id: str = None,
        action: str = None,
        decision: AccessDecision = None,
        since: datetime = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Get audit log entries"""
        entries = self._audit_log
        
        if tenant_id:
            entries = [e for e in entries if e.tenant_id == tenant_id]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if decision:
            entries = [e for e in entries if e.decision == decision]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        return entries[-limit:]
    
    def verify_audit_chain(self) -> bool:
        """Verify the integrity of the audit chain"""
        if not self._audit_log:
            return True
        
        prev_hash = ""
        for entry in self._audit_log:
            expected_hash = self._compute_chain_hash(entry, prev_hash)
            if entry.chain_hash != expected_hash:
                return False
            prev_hash = entry.chain_hash
        
        return True
    
    def get_metrics(self) -> GatewayMetrics:
        """Get gateway metrics"""
        metrics = GatewayMetrics()
        metrics.total_policies = len(self._policies)
        metrics.active_policies = len([p for p in self._policies.values() if p.enabled])
        metrics.total_tenants_encrypted = len(self._tenant_encryption)
        metrics.total_audit_entries = len(self._audit_log)
        
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        for entry in self._audit_log:
            metrics.total_requests += 1
            
            if entry.decision == AccessDecision.ALLOW:
                metrics.allowed_requests += 1
            elif entry.decision == AccessDecision.DENY:
                metrics.denied_requests += 1
            elif entry.decision == AccessDecision.CONDITIONAL:
                metrics.conditional_requests += 1
            
            if entry.timestamp >= day_ago:
                metrics.requests_24h += 1
                if entry.decision == AccessDecision.DENY:
                    metrics.denials_24h += 1
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def _check_clearance(
        self,
        user_clearance: ClearanceLevel,
        data_sensitivity: DataSensitivity,
    ) -> bool:
        """Check if user clearance is sufficient for data sensitivity"""
        clearance_levels = {
            ClearanceLevel.NONE: 0,
            ClearanceLevel.BASIC: 1,
            ClearanceLevel.STANDARD: 2,
            ClearanceLevel.ELEVATED: 3,
            ClearanceLevel.HIGH: 4,
            ClearanceLevel.TOP: 5,
            ClearanceLevel.COMPARTMENTED: 6,
        }
        
        sensitivity_requirements = {
            DataSensitivity.PUBLIC: 0,
            DataSensitivity.INTERNAL: 1,
            DataSensitivity.RESTRICTED: 2,
            DataSensitivity.CONFIDENTIAL: 3,
            DataSensitivity.SECRET: 4,
            DataSensitivity.TOP_SECRET: 5,
        }
        
        user_level = clearance_levels.get(user_clearance, 0)
        required_level = sensitivity_requirements.get(data_sensitivity, 0)
        
        return user_level >= required_level
    
    def _get_applicable_policies(
        self,
        request: AccessRequest,
        abac: AttributeBasedAccess,
    ) -> List[AccessPolicy]:
        """Get policies applicable to a request"""
        applicable = []
        
        for policy in self._policies.values():
            if policy.tenant_id and policy.tenant_id != request.tenant_id:
                continue
            
            if policy.resource_patterns:
                pattern_match = False
                for pattern in policy.resource_patterns:
                    if pattern == "*" or pattern == request.resource_type:
                        pattern_match = True
                        break
                if not pattern_match:
                    continue
            
            applicable.append(policy)
        
        return applicable
    
    def _evaluate_policy(
        self,
        policy: AccessPolicy,
        request: AccessRequest,
        abac: AttributeBasedAccess,
    ) -> tuple:
        """Evaluate a policy against a request"""
        conditions_evaluated = 0
        conditions_matched = 0
        
        if policy.required_clearance != ClearanceLevel.NONE:
            conditions_evaluated += 1
            if self._clearance_level_value(abac.clearance_level) >= \
               self._clearance_level_value(policy.required_clearance):
                conditions_matched += 1
            else:
                return False, conditions_evaluated, conditions_matched
        
        if policy.required_roles:
            conditions_evaluated += 1
            if any(role in abac.roles for role in policy.required_roles):
                conditions_matched += 1
            else:
                return False, conditions_evaluated, conditions_matched
        
        if policy.required_jurisdictions:
            conditions_evaluated += 1
            if any(jur in abac.jurisdictions for jur in policy.required_jurisdictions):
                conditions_matched += 1
            else:
                return False, conditions_evaluated, conditions_matched
        
        if policy.allowed_actions:
            conditions_evaluated += 1
            if request.action in policy.allowed_actions:
                conditions_matched += 1
            else:
                return False, conditions_evaluated, conditions_matched
        
        if policy.denied_actions:
            conditions_evaluated += 1
            if request.action in policy.denied_actions:
                return False, conditions_evaluated, conditions_matched
            conditions_matched += 1
        
        for condition in policy.conditions:
            conditions_evaluated += 1
            if self._evaluate_condition(condition, request, abac):
                conditions_matched += 1
            else:
                return False, conditions_evaluated, conditions_matched
        
        return True, conditions_evaluated, conditions_matched
    
    def _evaluate_condition(
        self,
        condition: PolicyCondition,
        request: AccessRequest,
        abac: AttributeBasedAccess,
    ) -> bool:
        """Evaluate a single policy condition"""
        if condition.attribute_type == AttributeType.USER:
            actual_value = abac.user_attributes.get(condition.attribute_name)
        elif condition.attribute_type == AttributeType.CLEARANCE:
            actual_value = abac.clearance_level.value
        elif condition.attribute_type == AttributeType.ROLE:
            actual_value = abac.roles
        elif condition.attribute_type == AttributeType.JURISDICTION:
            actual_value = abac.jurisdictions
        elif condition.attribute_type == AttributeType.RESOURCE:
            actual_value = request.metadata.get(condition.attribute_name)
        elif condition.attribute_type == AttributeType.ACTION:
            actual_value = request.action
        elif condition.attribute_type == AttributeType.TENANT:
            actual_value = request.tenant_id
        else:
            actual_value = None
        
        result = self._compare_values(actual_value, condition.operator, condition.value)
        
        if condition.negate:
            result = not result
        
        return result
    
    def _compare_values(self, actual: Any, operator: str, expected: Any) -> bool:
        """Compare values using an operator"""
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "contains":
            if isinstance(actual, list):
                return expected in actual
            return expected in str(actual)
        elif operator == "not_contains":
            if isinstance(actual, list):
                return expected not in actual
            return expected not in str(actual)
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        elif operator == "greater_than":
            return actual > expected
        elif operator == "less_than":
            return actual < expected
        elif operator == "starts_with":
            return str(actual).startswith(str(expected))
        elif operator == "ends_with":
            return str(actual).endswith(str(expected))
        else:
            return False
    
    def _clearance_level_value(self, level: ClearanceLevel) -> int:
        """Get numeric value for clearance level"""
        levels = {
            ClearanceLevel.NONE: 0,
            ClearanceLevel.BASIC: 1,
            ClearanceLevel.STANDARD: 2,
            ClearanceLevel.ELEVATED: 3,
            ClearanceLevel.HIGH: 4,
            ClearanceLevel.TOP: 5,
            ClearanceLevel.COMPARTMENTED: 6,
        }
        return levels.get(level, 0)
    
    def _get_clearance_filter(self, clearance_level: ClearanceLevel) -> Optional[ClearanceFilter]:
        """Get the appropriate clearance filter for a level"""
        filter_map = {
            ClearanceLevel.BASIC: "filter-basic",
            ClearanceLevel.STANDARD: "filter-standard",
            ClearanceLevel.ELEVATED: "filter-elevated",
            ClearanceLevel.HIGH: "filter-high",
        }
        
        filter_id = filter_map.get(clearance_level)
        if filter_id:
            return self._clearance_filters.get(filter_id)
        return None
    
    def _log_access(self, request: AccessRequest, result: AccessResult) -> None:
        """Log an access decision"""
        audit_entry = AuditEntry(
            audit_id=f"audit-{uuid.uuid4().hex[:12]}",
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            decision=result.decision,
            policy_id=result.matched_policy_id,
            source_ip=request.source_ip,
            request_details={
                "clearance": request.user_clearance.value,
                "roles": request.user_roles,
                "jurisdictions": request.user_jurisdictions,
            },
            response_details={
                "reason": result.reason,
                "redaction_applied": result.redaction_applied,
            },
        )
        
        audit_entry.chain_hash = self._compute_chain_hash(audit_entry, self._last_chain_hash)
        self._last_chain_hash = audit_entry.chain_hash
        
        self._audit_log.append(audit_entry)
        
        if len(self._audit_log) > self._max_audit_entries:
            self._audit_log = self._audit_log[-self._max_audit_entries:]
        
        result.audit_logged = True
    
    def _compute_chain_hash(self, entry: AuditEntry, prev_hash: str) -> str:
        """Compute chain hash for audit entry"""
        data = f"{entry.audit_id}:{entry.tenant_id}:{entry.user_id}:{entry.action}:" \
               f"{entry.resource_type}:{entry.resource_id}:{entry.decision.value}:" \
               f"{entry.timestamp.isoformat()}:{prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record an event"""
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def _notify_callbacks(self, event_type: str, data: Any) -> None:
        """Notify registered callbacks"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
