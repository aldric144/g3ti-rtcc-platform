"""
FederationLayer - Cross-agency data federation for G3TI Fusion Cloud

Manages:
- Cross-agency data sharing
- Metadata tagging (jurisdiction, clearance, sensitivity, retention)
- Secure forwarding of intelligence data
- Federation subscriptions and permissions
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid


class DataClassification(str, Enum):
    """Data classification levels"""
    UNCLASSIFIED = "unclassified"
    LAW_ENFORCEMENT_SENSITIVE = "law_enforcement_sensitive"
    OFFICIAL_USE_ONLY = "official_use_only"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class ClearanceLevel(str, Enum):
    """User clearance levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ELEVATED = "elevated"
    HIGH = "high"
    TOP = "top"


class SensitivityLevel(str, Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    HIGHLY_RESTRICTED = "highly_restricted"
    CRITICAL = "critical"


class FederatedDataType(str, Enum):
    """Types of federated data"""
    LPR_HIT = "lpr_hit"
    SHOTSPOTTER_ALERT = "shotspotter_alert"
    INVESTIGATION = "investigation"
    BOLO = "bolo"
    SUSPECT_PROFILE = "suspect_profile"
    VEHICLE_PROFILE = "vehicle_profile"
    INCIDENT = "incident"
    HEATMAP = "heatmap"
    OFFENDER_PROFILE = "offender_profile"
    PATTERN = "pattern"
    ALERT = "alert"
    CASE = "case"
    INTELLIGENCE = "intelligence"


class SubscriptionStatus(str, Enum):
    """Status of a federation subscription"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class JurisdictionTag:
    """Jurisdiction metadata tag"""
    tag_id: str
    jurisdiction_code: str
    jurisdiction_name: str
    jurisdiction_type: str
    state: str = ""
    county: str = ""
    city: str = ""
    federal_district: str = ""
    tribal_area: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetentionPolicy:
    """Data retention policy"""
    policy_id: str
    name: str
    retention_days: int = 365
    auto_archive: bool = True
    auto_delete: bool = False
    archive_after_days: int = 180
    delete_after_days: int = 730
    legal_hold_enabled: bool = False
    audit_required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederatedData:
    """A piece of federated data shared across agencies"""
    data_id: str
    data_type: FederatedDataType
    source_tenant_id: str
    source_agency_name: str
    classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE
    sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED
    required_clearance: ClearanceLevel = ClearanceLevel.STANDARD
    jurisdiction_tags: List[JurisdictionTag] = field(default_factory=list)
    retention_policy: Optional[RetentionPolicy] = None
    title: str = ""
    description: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    related_data_ids: List[str] = field(default_factory=list)
    shared_with_tenants: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederationPermission:
    """Permission for federation data sharing"""
    permission_id: str
    source_tenant_id: str
    target_tenant_id: str
    data_types: List[FederatedDataType] = field(default_factory=list)
    max_classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE
    max_sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED
    inbound_enabled: bool = True
    outbound_enabled: bool = True
    auto_share: bool = False
    require_approval: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederationSubscription:
    """Subscription to federated data channels"""
    subscription_id: str
    subscriber_tenant_id: str
    publisher_tenant_id: str
    data_types: List[FederatedDataType] = field(default_factory=list)
    jurisdiction_filters: List[str] = field(default_factory=list)
    classification_filter: Optional[DataClassification] = None
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    webhook_url: str = ""
    notification_enabled: bool = True
    batch_delivery: bool = False
    batch_interval_minutes: int = 15
    last_delivery: Optional[datetime] = None
    delivery_count: int = 0
    error_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForwardingRule:
    """Rule for automatic data forwarding"""
    rule_id: str
    name: str
    source_tenant_id: str
    target_tenant_ids: List[str] = field(default_factory=list)
    data_types: List[FederatedDataType] = field(default_factory=list)
    jurisdiction_match: List[str] = field(default_factory=list)
    classification_match: List[DataClassification] = field(default_factory=list)
    keyword_match: List[str] = field(default_factory=list)
    enabled: bool = True
    require_approval: bool = False
    transform_rules: Dict[str, Any] = field(default_factory=dict)
    redaction_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FederationMetrics:
    """Metrics for the federation layer"""
    total_federated_data: int = 0
    data_by_type: Dict[FederatedDataType, int] = field(default_factory=dict)
    data_by_classification: Dict[DataClassification, int] = field(default_factory=dict)
    total_subscriptions: int = 0
    active_subscriptions: int = 0
    total_permissions: int = 0
    total_forwarding_rules: int = 0
    data_shared_24h: int = 0
    data_received_24h: int = 0


class FederationLayer:
    """
    Manages cross-agency data federation for the G3TI Fusion Cloud.
    
    Provides:
    - Cross-agency data sharing with classification controls
    - Metadata tagging for jurisdiction, clearance, sensitivity
    - Secure forwarding of LPR hits, ShotSpotter, investigations, etc.
    - Federation subscriptions and permissions management
    """
    
    def __init__(self):
        self._federated_data: Dict[str, FederatedData] = {}
        self._permissions: Dict[str, FederationPermission] = {}
        self._subscriptions: Dict[str, FederationSubscription] = {}
        self._forwarding_rules: Dict[str, ForwardingRule] = {}
        self._jurisdiction_tags: Dict[str, JurisdictionTag] = {}
        self._retention_policies: Dict[str, RetentionPolicy] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
        
        self._init_default_retention_policies()
    
    def _init_default_retention_policies(self) -> None:
        """Initialize default retention policies"""
        default_policies = [
            RetentionPolicy(
                policy_id="policy-standard",
                name="Standard Retention",
                retention_days=365,
                archive_after_days=180,
                delete_after_days=730,
            ),
            RetentionPolicy(
                policy_id="policy-investigation",
                name="Investigation Retention",
                retention_days=2555,
                archive_after_days=365,
                delete_after_days=3650,
                legal_hold_enabled=True,
            ),
            RetentionPolicy(
                policy_id="policy-short-term",
                name="Short-Term Retention",
                retention_days=90,
                archive_after_days=60,
                delete_after_days=180,
            ),
        ]
        
        for policy in default_policies:
            self._retention_policies[policy.policy_id] = policy
    
    def publish_data(
        self,
        source_tenant_id: str,
        source_agency_name: str,
        data_type: FederatedDataType,
        title: str,
        payload: Dict[str, Any],
        classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED,
        required_clearance: ClearanceLevel = ClearanceLevel.STANDARD,
        jurisdiction_codes: List[str] = None,
        retention_policy_id: str = "policy-standard",
        share_with_tenants: List[str] = None,
        description: str = "",
        expires_in_days: int = None,
    ) -> Optional[FederatedData]:
        """Publish federated data"""
        data_id = f"fed-{uuid.uuid4().hex[:12]}"
        
        jurisdiction_tags = []
        if jurisdiction_codes:
            for code in jurisdiction_codes:
                if code in self._jurisdiction_tags:
                    jurisdiction_tags.append(self._jurisdiction_tags[code])
                else:
                    tag = JurisdictionTag(
                        tag_id=f"jur-{uuid.uuid4().hex[:8]}",
                        jurisdiction_code=code,
                        jurisdiction_name=code,
                        jurisdiction_type="unknown",
                    )
                    self._jurisdiction_tags[code] = tag
                    jurisdiction_tags.append(tag)
        
        retention_policy = self._retention_policies.get(retention_policy_id)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        federated_data = FederatedData(
            data_id=data_id,
            data_type=data_type,
            source_tenant_id=source_tenant_id,
            source_agency_name=source_agency_name,
            classification=classification,
            sensitivity=sensitivity,
            required_clearance=required_clearance,
            jurisdiction_tags=jurisdiction_tags,
            retention_policy=retention_policy,
            title=title,
            description=description,
            payload=payload,
            shared_with_tenants=share_with_tenants or [],
            expires_at=expires_at,
        )
        
        self._federated_data[data_id] = federated_data
        
        self._process_forwarding_rules(federated_data)
        self._notify_subscribers(federated_data)
        
        self._record_event("data_published", {
            "data_id": data_id,
            "data_type": data_type.value,
            "source_tenant_id": source_tenant_id,
            "classification": classification.value,
        })
        self._notify_callbacks("data_published", federated_data)
        
        return federated_data
    
    def get_data(self, data_id: str) -> Optional[FederatedData]:
        """Get federated data by ID"""
        data = self._federated_data.get(data_id)
        if data:
            data.access_count += 1
            data.last_accessed = datetime.utcnow()
        return data
    
    def get_data_for_tenant(
        self,
        tenant_id: str,
        data_types: List[FederatedDataType] = None,
        classification_max: DataClassification = None,
        jurisdiction_codes: List[str] = None,
        limit: int = 100,
    ) -> List[FederatedData]:
        """Get federated data accessible to a tenant"""
        results = []
        
        for data in self._federated_data.values():
            if data.source_tenant_id == tenant_id:
                results.append(data)
                continue
            
            if tenant_id in data.shared_with_tenants:
                if data_types and data.data_type not in data_types:
                    continue
                
                if classification_max:
                    if self._classification_level(data.classification) > self._classification_level(classification_max):
                        continue
                
                if jurisdiction_codes:
                    data_jurisdictions = {t.jurisdiction_code for t in data.jurisdiction_tags}
                    if not any(jc in data_jurisdictions for jc in jurisdiction_codes):
                        continue
                
                results.append(data)
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    def share_data_with_tenant(
        self,
        data_id: str,
        target_tenant_id: str,
        shared_by: str = "",
    ) -> bool:
        """Share federated data with a specific tenant"""
        if data_id not in self._federated_data:
            return False
        
        data = self._federated_data[data_id]
        
        if target_tenant_id not in data.shared_with_tenants:
            data.shared_with_tenants.append(target_tenant_id)
            data.updated_at = datetime.utcnow()
            
            self._record_event("data_shared", {
                "data_id": data_id,
                "target_tenant_id": target_tenant_id,
                "shared_by": shared_by,
            })
            self._notify_callbacks("data_shared", {
                "data": data,
                "target_tenant_id": target_tenant_id,
            })
            
            return True
        
        return False
    
    def revoke_data_sharing(
        self,
        data_id: str,
        target_tenant_id: str,
        revoked_by: str = "",
    ) -> bool:
        """Revoke data sharing with a tenant"""
        if data_id not in self._federated_data:
            return False
        
        data = self._federated_data[data_id]
        
        if target_tenant_id in data.shared_with_tenants:
            data.shared_with_tenants.remove(target_tenant_id)
            data.updated_at = datetime.utcnow()
            
            self._record_event("data_sharing_revoked", {
                "data_id": data_id,
                "target_tenant_id": target_tenant_id,
                "revoked_by": revoked_by,
            })
            
            return True
        
        return False
    
    def create_permission(
        self,
        source_tenant_id: str,
        target_tenant_id: str,
        data_types: List[FederatedDataType],
        max_classification: DataClassification = DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        max_sensitivity: SensitivityLevel = SensitivityLevel.RESTRICTED,
        inbound_enabled: bool = True,
        outbound_enabled: bool = True,
        auto_share: bool = False,
        require_approval: bool = True,
        expires_in_days: int = None,
        created_by: str = "",
    ) -> Optional[FederationPermission]:
        """Create a federation permission between tenants"""
        permission_id = f"perm-{uuid.uuid4().hex[:12]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        permission = FederationPermission(
            permission_id=permission_id,
            source_tenant_id=source_tenant_id,
            target_tenant_id=target_tenant_id,
            data_types=data_types,
            max_classification=max_classification,
            max_sensitivity=max_sensitivity,
            inbound_enabled=inbound_enabled,
            outbound_enabled=outbound_enabled,
            auto_share=auto_share,
            require_approval=require_approval,
            expires_at=expires_at,
            created_by=created_by,
        )
        
        self._permissions[permission_id] = permission
        
        self._record_event("permission_created", {
            "permission_id": permission_id,
            "source_tenant_id": source_tenant_id,
            "target_tenant_id": target_tenant_id,
        })
        self._notify_callbacks("permission_created", permission)
        
        return permission
    
    def revoke_permission(self, permission_id: str, revoked_by: str = "") -> bool:
        """Revoke a federation permission"""
        if permission_id not in self._permissions:
            return False
        
        del self._permissions[permission_id]
        
        self._record_event("permission_revoked", {
            "permission_id": permission_id,
            "revoked_by": revoked_by,
        })
        
        return True
    
    def get_permissions_for_tenant(self, tenant_id: str) -> List[FederationPermission]:
        """Get all permissions for a tenant"""
        return [
            p for p in self._permissions.values()
            if p.source_tenant_id == tenant_id or p.target_tenant_id == tenant_id
        ]
    
    def check_permission(
        self,
        source_tenant_id: str,
        target_tenant_id: str,
        data_type: FederatedDataType,
        classification: DataClassification,
    ) -> bool:
        """Check if a permission exists for data sharing"""
        for permission in self._permissions.values():
            if permission.source_tenant_id != source_tenant_id:
                continue
            if permission.target_tenant_id != target_tenant_id:
                continue
            if data_type not in permission.data_types:
                continue
            if self._classification_level(classification) > self._classification_level(permission.max_classification):
                continue
            if permission.expires_at and permission.expires_at < datetime.utcnow():
                continue
            return True
        return False
    
    def create_subscription(
        self,
        subscriber_tenant_id: str,
        publisher_tenant_id: str,
        data_types: List[FederatedDataType],
        jurisdiction_filters: List[str] = None,
        classification_filter: DataClassification = None,
        webhook_url: str = "",
        notification_enabled: bool = True,
        batch_delivery: bool = False,
        batch_interval_minutes: int = 15,
        expires_in_days: int = None,
    ) -> Optional[FederationSubscription]:
        """Create a subscription to federated data"""
        subscription_id = f"sub-{uuid.uuid4().hex[:12]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        subscription = FederationSubscription(
            subscription_id=subscription_id,
            subscriber_tenant_id=subscriber_tenant_id,
            publisher_tenant_id=publisher_tenant_id,
            data_types=data_types,
            jurisdiction_filters=jurisdiction_filters or [],
            classification_filter=classification_filter,
            status=SubscriptionStatus.PENDING,
            webhook_url=webhook_url,
            notification_enabled=notification_enabled,
            batch_delivery=batch_delivery,
            batch_interval_minutes=batch_interval_minutes,
            expires_at=expires_at,
        )
        
        self._subscriptions[subscription_id] = subscription
        
        self._record_event("subscription_created", {
            "subscription_id": subscription_id,
            "subscriber_tenant_id": subscriber_tenant_id,
            "publisher_tenant_id": publisher_tenant_id,
        })
        self._notify_callbacks("subscription_created", subscription)
        
        return subscription
    
    def activate_subscription(self, subscription_id: str) -> bool:
        """Activate a subscription"""
        if subscription_id not in self._subscriptions:
            return False
        
        subscription = self._subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.ACTIVE
        
        self._record_event("subscription_activated", {"subscription_id": subscription_id})
        
        return True
    
    def pause_subscription(self, subscription_id: str) -> bool:
        """Pause a subscription"""
        if subscription_id not in self._subscriptions:
            return False
        
        subscription = self._subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.PAUSED
        
        self._record_event("subscription_paused", {"subscription_id": subscription_id})
        
        return True
    
    def revoke_subscription(self, subscription_id: str) -> bool:
        """Revoke a subscription"""
        if subscription_id not in self._subscriptions:
            return False
        
        subscription = self._subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.REVOKED
        
        self._record_event("subscription_revoked", {"subscription_id": subscription_id})
        
        return True
    
    def get_subscriptions_for_tenant(self, tenant_id: str) -> List[FederationSubscription]:
        """Get all subscriptions for a tenant"""
        return [
            s for s in self._subscriptions.values()
            if s.subscriber_tenant_id == tenant_id or s.publisher_tenant_id == tenant_id
        ]
    
    def get_active_subscriptions(self, publisher_tenant_id: str) -> List[FederationSubscription]:
        """Get active subscriptions for a publisher"""
        return [
            s for s in self._subscriptions.values()
            if s.publisher_tenant_id == publisher_tenant_id and s.status == SubscriptionStatus.ACTIVE
        ]
    
    def create_forwarding_rule(
        self,
        name: str,
        source_tenant_id: str,
        target_tenant_ids: List[str],
        data_types: List[FederatedDataType],
        jurisdiction_match: List[str] = None,
        classification_match: List[DataClassification] = None,
        keyword_match: List[str] = None,
        require_approval: bool = False,
        transform_rules: Dict[str, Any] = None,
        redaction_rules: Dict[str, Any] = None,
    ) -> Optional[ForwardingRule]:
        """Create a forwarding rule for automatic data sharing"""
        rule_id = f"fwd-{uuid.uuid4().hex[:12]}"
        
        rule = ForwardingRule(
            rule_id=rule_id,
            name=name,
            source_tenant_id=source_tenant_id,
            target_tenant_ids=target_tenant_ids,
            data_types=data_types,
            jurisdiction_match=jurisdiction_match or [],
            classification_match=classification_match or [],
            keyword_match=keyword_match or [],
            require_approval=require_approval,
            transform_rules=transform_rules or {},
            redaction_rules=redaction_rules or {},
        )
        
        self._forwarding_rules[rule_id] = rule
        
        self._record_event("forwarding_rule_created", {
            "rule_id": rule_id,
            "name": name,
            "source_tenant_id": source_tenant_id,
        })
        
        return rule
    
    def delete_forwarding_rule(self, rule_id: str) -> bool:
        """Delete a forwarding rule"""
        if rule_id not in self._forwarding_rules:
            return False
        
        del self._forwarding_rules[rule_id]
        
        self._record_event("forwarding_rule_deleted", {"rule_id": rule_id})
        
        return True
    
    def get_forwarding_rules(self, tenant_id: str) -> List[ForwardingRule]:
        """Get forwarding rules for a tenant"""
        return [
            r for r in self._forwarding_rules.values()
            if r.source_tenant_id == tenant_id
        ]
    
    def register_jurisdiction(
        self,
        jurisdiction_code: str,
        jurisdiction_name: str,
        jurisdiction_type: str,
        state: str = "",
        county: str = "",
        city: str = "",
    ) -> JurisdictionTag:
        """Register a jurisdiction tag"""
        tag = JurisdictionTag(
            tag_id=f"jur-{uuid.uuid4().hex[:8]}",
            jurisdiction_code=jurisdiction_code,
            jurisdiction_name=jurisdiction_name,
            jurisdiction_type=jurisdiction_type,
            state=state,
            county=county,
            city=city,
        )
        
        self._jurisdiction_tags[jurisdiction_code] = tag
        
        return tag
    
    def get_jurisdiction(self, jurisdiction_code: str) -> Optional[JurisdictionTag]:
        """Get a jurisdiction tag"""
        return self._jurisdiction_tags.get(jurisdiction_code)
    
    def get_all_jurisdictions(self) -> List[JurisdictionTag]:
        """Get all jurisdiction tags"""
        return list(self._jurisdiction_tags.values())
    
    def create_retention_policy(
        self,
        name: str,
        retention_days: int,
        archive_after_days: int = None,
        delete_after_days: int = None,
        legal_hold_enabled: bool = False,
    ) -> RetentionPolicy:
        """Create a retention policy"""
        policy_id = f"policy-{uuid.uuid4().hex[:8]}"
        
        policy = RetentionPolicy(
            policy_id=policy_id,
            name=name,
            retention_days=retention_days,
            archive_after_days=archive_after_days or retention_days // 2,
            delete_after_days=delete_after_days or retention_days * 2,
            legal_hold_enabled=legal_hold_enabled,
        )
        
        self._retention_policies[policy_id] = policy
        
        return policy
    
    def get_retention_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get a retention policy"""
        return self._retention_policies.get(policy_id)
    
    def get_metrics(self) -> FederationMetrics:
        """Get federation metrics"""
        metrics = FederationMetrics()
        metrics.total_federated_data = len(self._federated_data)
        metrics.total_subscriptions = len(self._subscriptions)
        metrics.total_permissions = len(self._permissions)
        metrics.total_forwarding_rules = len(self._forwarding_rules)
        
        for data in self._federated_data.values():
            metrics.data_by_type[data.data_type] = \
                metrics.data_by_type.get(data.data_type, 0) + 1
            metrics.data_by_classification[data.classification] = \
                metrics.data_by_classification.get(data.classification, 0) + 1
        
        for sub in self._subscriptions.values():
            if sub.status == SubscriptionStatus.ACTIVE:
                metrics.active_subscriptions += 1
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def _process_forwarding_rules(self, data: FederatedData) -> None:
        """Process forwarding rules for new data"""
        for rule in self._forwarding_rules.values():
            if not rule.enabled:
                continue
            if rule.source_tenant_id != data.source_tenant_id:
                continue
            if data.data_type not in rule.data_types:
                continue
            
            if rule.classification_match:
                if data.classification not in rule.classification_match:
                    continue
            
            if rule.jurisdiction_match:
                data_jurisdictions = {t.jurisdiction_code for t in data.jurisdiction_tags}
                if not any(jc in data_jurisdictions for jc in rule.jurisdiction_match):
                    continue
            
            for target_tenant_id in rule.target_tenant_ids:
                if target_tenant_id not in data.shared_with_tenants:
                    data.shared_with_tenants.append(target_tenant_id)
                    
                    self._record_event("data_auto_forwarded", {
                        "data_id": data.data_id,
                        "rule_id": rule.rule_id,
                        "target_tenant_id": target_tenant_id,
                    })
    
    def _notify_subscribers(self, data: FederatedData) -> None:
        """Notify subscribers of new data"""
        for subscription in self._subscriptions.values():
            if subscription.status != SubscriptionStatus.ACTIVE:
                continue
            if subscription.publisher_tenant_id != data.source_tenant_id:
                continue
            if data.data_type not in subscription.data_types:
                continue
            
            if subscription.classification_filter:
                if self._classification_level(data.classification) > \
                   self._classification_level(subscription.classification_filter):
                    continue
            
            if subscription.jurisdiction_filters:
                data_jurisdictions = {t.jurisdiction_code for t in data.jurisdiction_tags}
                if not any(jc in data_jurisdictions for jc in subscription.jurisdiction_filters):
                    continue
            
            subscription.delivery_count += 1
            subscription.last_delivery = datetime.utcnow()
            
            if subscription.subscriber_tenant_id not in data.shared_with_tenants:
                data.shared_with_tenants.append(subscription.subscriber_tenant_id)
            
            self._notify_callbacks("subscription_delivery", {
                "subscription": subscription,
                "data": data,
            })
    
    def _classification_level(self, classification: DataClassification) -> int:
        """Get numeric level for classification"""
        levels = {
            DataClassification.UNCLASSIFIED: 0,
            DataClassification.LAW_ENFORCEMENT_SENSITIVE: 1,
            DataClassification.OFFICIAL_USE_ONLY: 2,
            DataClassification.CONFIDENTIAL: 3,
            DataClassification.SECRET: 4,
            DataClassification.TOP_SECRET: 5,
        }
        return levels.get(classification, 0)
    
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
