"""
G3TI RTCC-UIP Notification Rules Engine.

Provides automated alert triggering based on configurable IF/THEN rules:
- Define conditions for automated alerts
- Trigger actions based on events from multiple sources
- Support for complex rule combinations
- Audit logging for all triggered rules

Example rules:
- IF {gunfire cluster} AND {officer within 400m} THEN PUSH ALERT
- IF {high-risk vehicle} enters {tactical zone} THEN SEND BULLETIN
- IF {CAD P1 call} THEN PUSH SCENE INTEL PACKET

All rule triggers are logged for CJIS compliance.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class ConditionType(str, Enum):
    """Types of rule conditions."""
    EVENT_TYPE = "event_type"  # Match specific event type
    ENTITY_TYPE = "entity_type"  # Match entity type
    LOCATION_PROXIMITY = "location_proximity"  # Within distance of location
    ZONE_ENTRY = "zone_entry"  # Entity enters zone
    ZONE_EXIT = "zone_exit"  # Entity exits zone
    THRESHOLD = "threshold"  # Value exceeds threshold
    TIME_WINDOW = "time_window"  # Within time window
    PATTERN_MATCH = "pattern_match"  # Matches pattern
    RISK_LEVEL = "risk_level"  # Risk level condition
    CALL_PRIORITY = "call_priority"  # CAD call priority
    OFFICER_SAFETY = "officer_safety"  # Officer safety condition
    CUSTOM = "custom"  # Custom condition


class ActionType(str, Enum):
    """Types of rule actions."""
    PUSH_ALERT = "push_alert"
    SEND_BULLETIN = "send_bulletin"
    SEND_MESSAGE = "send_message"
    CREATE_SCENE = "create_scene"
    NOTIFY_RTCC = "notify_rtcc"
    NOTIFY_COMMAND = "notify_command"
    LOG_EVENT = "log_event"
    TRIGGER_WEBHOOK = "trigger_webhook"
    UPDATE_ENTITY = "update_entity"
    CUSTOM = "custom"


class RuleOperator(str, Enum):
    """Operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"


class RulePriority(str, Enum):
    """Rule priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RuleCondition(BaseModel):
    """Schema for a rule condition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    condition_type: ConditionType
    field: str | None = None  # Field to evaluate
    operator: str = "equals"  # equals, contains, greater_than, less_than, in, not_in
    value: Any = None  # Value to compare against
    parameters: dict[str, Any] = Field(default_factory=dict)

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate the condition against a context."""
        if self.condition_type == ConditionType.EVENT_TYPE:
            return context.get("event_type") == self.value

        elif self.condition_type == ConditionType.ENTITY_TYPE:
            return context.get("entity_type") == self.value

        elif self.condition_type == ConditionType.LOCATION_PROXIMITY:
            # Check if location is within radius
            lat = context.get("latitude")
            lon = context.get("longitude")
            target_lat = self.parameters.get("latitude")
            target_lon = self.parameters.get("longitude")
            radius = self.parameters.get("radius_meters", 500)

            if all([lat, lon, target_lat, target_lon]):
                distance = self._calculate_distance(lat, lon, target_lat, target_lon)
                return distance <= radius
            return False

        elif self.condition_type == ConditionType.THRESHOLD:
            field_value = context.get(self.field)
            if field_value is None:
                return False

            if self.operator == "greater_than":
                return field_value > self.value
            elif self.operator == "less_than":
                return field_value < self.value
            elif self.operator == "equals":
                return field_value == self.value
            elif self.operator == "greater_than_or_equal":
                return field_value >= self.value
            elif self.operator == "less_than_or_equal":
                return field_value <= self.value

        elif self.condition_type == ConditionType.CALL_PRIORITY:
            return context.get("priority") == self.value

        elif self.condition_type == ConditionType.RISK_LEVEL:
            return context.get("risk_level") == self.value

        elif self.condition_type == ConditionType.OFFICER_SAFETY:
            safety_level = context.get("safety_level")
            if self.operator == "equals":
                return safety_level == self.value
            elif self.operator == "in":
                return safety_level in self.value

        elif self.condition_type == ConditionType.PATTERN_MATCH:
            field_value = context.get(self.field, "")
            import re
            return bool(re.search(self.value, str(field_value)))

        # Default field comparison
        if self.field:
            field_value = context.get(self.field)
            if self.operator == "equals":
                return field_value == self.value
            elif self.operator == "contains":
                return self.value in str(field_value)
            elif self.operator == "in":
                return field_value in self.value
            elif self.operator == "not_in":
                return field_value not in self.value

        return False

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points in meters (Haversine formula)."""
        import math

        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c


class RuleAction(BaseModel):
    """Schema for a rule action."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType
    parameters: dict[str, Any] = Field(default_factory=dict)

    # For alerts
    alert_type: str | None = None
    alert_priority: str | None = None
    alert_title_template: str | None = None
    alert_body_template: str | None = None

    # For bulletins
    bulletin_type: str | None = None
    bulletin_template_id: str | None = None

    # For messages
    channel_id: str | None = None
    message_template: str | None = None

    # Targeting
    target_badges: list[str] = Field(default_factory=list)
    target_shifts: list[str] = Field(default_factory=list)
    target_districts: list[str] = Field(default_factory=list)
    broadcast_all: bool = False


class NotificationRule(BaseModel):
    """Schema for a notification rule."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str | None = None
    priority: RulePriority = RulePriority.NORMAL

    # Conditions
    conditions: list[RuleCondition] = Field(default_factory=list)
    condition_operator: RuleOperator = RuleOperator.AND  # How to combine conditions

    # Actions
    actions: list[RuleAction] = Field(default_factory=list)

    # Event sources this rule applies to
    event_sources: list[str] = Field(default_factory=list)  # shotspotter, lpr, cad, etc.

    # Status
    is_active: bool = True
    is_system: bool = False  # System rules cannot be deleted

    # Rate limiting
    cooldown_seconds: int = 0  # Minimum time between triggers
    max_triggers_per_hour: int | None = None

    # Metadata
    created_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    last_triggered_at: datetime | None = None
    trigger_count: int = 0

    # CJIS compliance
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class RuleTriggerEvent(BaseModel):
    """Schema for a rule trigger event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    rule_name: str
    event_source: str
    event_type: str
    context: dict[str, Any] = Field(default_factory=dict)
    actions_executed: list[str] = Field(default_factory=list)
    success: bool = True
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class NotificationRulesEngine:
    """
    Notification Rules Engine for automated alert triggering.

    Evaluates events against configured rules and executes
    corresponding actions when conditions are met.
    """

    def __init__(
        self,
        alerts_manager: Any | None = None,
        bulletin_manager: Any | None = None,
        messaging_manager: Any | None = None,
        redis_manager: Any | None = None,
    ):
        """
        Initialize the rules engine.

        Args:
            alerts_manager: Alerts manager for push notifications
            bulletin_manager: Bulletin manager for bulletins
            messaging_manager: Messaging manager for messages
            redis_manager: Redis manager for caching
        """
        self.alerts = alerts_manager
        self.bulletins = bulletin_manager
        self.messaging = messaging_manager
        self.redis = redis_manager

        # In-memory stores
        self._rules: dict[str, NotificationRule] = {}
        self._trigger_history: list[RuleTriggerEvent] = []
        self._last_trigger_times: dict[str, datetime] = {}
        self._trigger_counts: dict[str, list[datetime]] = {}

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("notification_rules_engine_initialized")

    def _initialize_default_rules(self) -> None:
        """Initialize default system rules."""
        default_rules = [
            NotificationRule(
                id="gunfire_officer_proximity",
                name="Gunfire Near Officer",
                description="Alert officers within 400m of detected gunfire",
                priority=RulePriority.CRITICAL,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.EVENT_TYPE,
                        value="gunfire_detected",
                    ),
                    RuleCondition(
                        condition_type=ConditionType.THRESHOLD,
                        field="rounds",
                        operator="greater_than",
                        value=0,
                    ),
                ],
                condition_operator=RuleOperator.AND,
                actions=[
                    RuleAction(
                        action_type=ActionType.PUSH_ALERT,
                        alert_type="gunfire",
                        alert_priority="urgent",
                        alert_title_template="GUNFIRE DETECTED",
                        alert_body_template="{rounds} rounds at {address}. {distance}m from your position.",
                        parameters={"radius_meters": 400},
                    ),
                ],
                event_sources=["shotspotter"],
                is_system=True,
            ),
            NotificationRule(
                id="high_risk_vehicle_zone_entry",
                name="High-Risk Vehicle Zone Entry",
                description="Send bulletin when high-risk vehicle enters tactical zone",
                priority=RulePriority.HIGH,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.EVENT_TYPE,
                        value="lpr_hit",
                    ),
                    RuleCondition(
                        condition_type=ConditionType.RISK_LEVEL,
                        operator="in",
                        value=["high", "critical"],
                    ),
                ],
                condition_operator=RuleOperator.AND,
                actions=[
                    RuleAction(
                        action_type=ActionType.SEND_BULLETIN,
                        bulletin_type="high_risk_vehicle",
                        bulletin_template_id="high_risk_vehicle",
                    ),
                ],
                event_sources=["lpr", "flock"],
                is_system=True,
            ),
            NotificationRule(
                id="cad_p1_scene_intel",
                name="Priority 1 Call Scene Intel",
                description="Push scene intel packet for P1 calls",
                priority=RulePriority.CRITICAL,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.EVENT_TYPE,
                        value="cad_call_created",
                    ),
                    RuleCondition(
                        condition_type=ConditionType.CALL_PRIORITY,
                        value="P1",
                    ),
                ],
                condition_operator=RuleOperator.AND,
                actions=[
                    RuleAction(
                        action_type=ActionType.PUSH_ALERT,
                        alert_type="cad_priority",
                        alert_priority="urgent",
                        alert_title_template="P1 - {call_type}",
                        alert_body_template="{description} at {address}",
                    ),
                    RuleAction(
                        action_type=ActionType.NOTIFY_RTCC,
                        parameters={"create_scene_intel": True},
                    ),
                ],
                event_sources=["cad"],
                is_system=True,
            ),
            NotificationRule(
                id="officer_safety_critical",
                name="Officer Safety Critical",
                description="Alert command when officer safety level is critical",
                priority=RulePriority.CRITICAL,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.OFFICER_SAFETY,
                        operator="in",
                        value=["red", "black"],
                    ),
                ],
                condition_operator=RuleOperator.AND,
                actions=[
                    RuleAction(
                        action_type=ActionType.PUSH_ALERT,
                        alert_type="officer_safety",
                        alert_priority="critical",
                        alert_title_template="OFFICER SAFETY ALERT",
                        alert_body_template="Officer {badge} safety level: {safety_level}. Location: {address}",
                        broadcast_all=True,
                    ),
                    RuleAction(
                        action_type=ActionType.NOTIFY_COMMAND,
                    ),
                ],
                event_sources=["officer_safety"],
                is_system=True,
            ),
            NotificationRule(
                id="ambush_detection",
                name="Ambush Detection Alert",
                description="Alert all units when ambush indicators detected",
                priority=RulePriority.CRITICAL,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.EVENT_TYPE,
                        value="ambush_warning",
                    ),
                    RuleCondition(
                        condition_type=ConditionType.THRESHOLD,
                        field="confidence",
                        operator="greater_than",
                        value=0.7,
                    ),
                ],
                condition_operator=RuleOperator.AND,
                actions=[
                    RuleAction(
                        action_type=ActionType.PUSH_ALERT,
                        alert_type="ambush_warning",
                        alert_priority="critical",
                        alert_title_template="AMBUSH WARNING",
                        alert_body_template="Potential ambush at {address}. Indicators: {indicators}",
                        broadcast_all=True,
                    ),
                ],
                event_sources=["officer_safety"],
                is_system=True,
                cooldown_seconds=300,  # 5 minute cooldown
            ),
            NotificationRule(
                id="bolo_match",
                name="BOLO Match Alert",
                description="Alert when BOLO subject/vehicle is spotted",
                priority=RulePriority.HIGH,
                conditions=[
                    RuleCondition(
                        condition_type=ConditionType.EVENT_TYPE,
                        value="bolo_match",
                    ),
                ],
                actions=[
                    RuleAction(
                        action_type=ActionType.PUSH_ALERT,
                        alert_type="bolo",
                        alert_priority="high",
                        alert_title_template="BOLO MATCH: {subject_type}",
                        alert_body_template="{description}. Spotted at {address}.",
                    ),
                ],
                event_sources=["lpr", "camera", "manual"],
                is_system=True,
            ),
        ]

        for rule in default_rules:
            self._rules[rule.id] = rule

        logger.info("default_rules_initialized", count=len(default_rules))

    async def evaluate_event(
        self,
        event_source: str,
        event_type: str,
        context: dict[str, Any],
    ) -> list[RuleTriggerEvent]:
        """
        Evaluate an event against all active rules.

        Args:
            event_source: Source of the event (shotspotter, lpr, cad, etc.)
            event_type: Type of event
            context: Event context data

        Returns:
            List of triggered rule events
        """
        triggered_events = []

        # Add event info to context
        context["event_source"] = event_source
        context["event_type"] = event_type

        # Find applicable rules
        applicable_rules = [
            r for r in self._rules.values()
            if r.is_active and (not r.event_sources or event_source in r.event_sources)
        ]

        for rule in applicable_rules:
            # Check rate limiting
            if not self._check_rate_limit(rule):
                continue

            # Evaluate conditions
            if self._evaluate_conditions(rule, context):
                # Execute actions
                trigger_event = await self._execute_rule(rule, event_source, event_type, context)
                triggered_events.append(trigger_event)

                # Update trigger tracking
                self._update_trigger_tracking(rule)

        return triggered_events

    def _evaluate_conditions(
        self,
        rule: NotificationRule,
        context: dict[str, Any],
    ) -> bool:
        """Evaluate rule conditions against context."""
        if not rule.conditions:
            return True

        results = [c.evaluate(context) for c in rule.conditions]

        if rule.condition_operator == RuleOperator.AND:
            return all(results)
        elif rule.condition_operator == RuleOperator.OR:
            return any(results)
        elif rule.condition_operator == RuleOperator.NOT:
            return not any(results)

        return False

    def _check_rate_limit(self, rule: NotificationRule) -> bool:
        """Check if rule is within rate limits."""
        now = datetime.now(UTC)

        # Check cooldown
        if rule.cooldown_seconds > 0:
            last_trigger = self._last_trigger_times.get(rule.id)
            if last_trigger:
                elapsed = (now - last_trigger).total_seconds()
                if elapsed < rule.cooldown_seconds:
                    return False

        # Check max triggers per hour
        if rule.max_triggers_per_hour:
            triggers = self._trigger_counts.get(rule.id, [])
            hour_ago = now.replace(hour=now.hour - 1) if now.hour > 0 else now
            recent_triggers = [t for t in triggers if t > hour_ago]
            if len(recent_triggers) >= rule.max_triggers_per_hour:
                return False

        return True

    def _update_trigger_tracking(self, rule: NotificationRule) -> None:
        """Update trigger tracking for rate limiting."""
        now = datetime.now(UTC)

        self._last_trigger_times[rule.id] = now

        if rule.id not in self._trigger_counts:
            self._trigger_counts[rule.id] = []
        self._trigger_counts[rule.id].append(now)

        # Clean old entries
        hour_ago = now.replace(hour=now.hour - 1) if now.hour > 0 else now
        self._trigger_counts[rule.id] = [
            t for t in self._trigger_counts[rule.id] if t > hour_ago
        ]

        # Update rule stats
        rule.last_triggered_at = now
        rule.trigger_count += 1

    async def _execute_rule(
        self,
        rule: NotificationRule,
        event_source: str,
        event_type: str,
        context: dict[str, Any],
    ) -> RuleTriggerEvent:
        """Execute a rule's actions."""
        actions_executed = []
        success = True
        error_message = None

        for action in rule.actions:
            try:
                await self._execute_action(action, context)
                actions_executed.append(action.action_type.value)
            except Exception as e:
                logger.error(
                    "rule_action_failed",
                    rule_id=rule.id,
                    action_type=action.action_type.value,
                    error=str(e),
                )
                success = False
                error_message = str(e)

        # Create trigger event
        trigger_event = RuleTriggerEvent(
            rule_id=rule.id,
            rule_name=rule.name,
            event_source=event_source,
            event_type=event_type,
            context=context,
            actions_executed=actions_executed,
            success=success,
            error_message=error_message,
        )

        self._trigger_history.append(trigger_event)

        # Log for CJIS compliance
        logger.info(
            "rule_triggered",
            rule_id=rule.id,
            rule_name=rule.name,
            event_source=event_source,
            event_type=event_type,
            actions=actions_executed,
            success=success,
            audit_id=trigger_event.audit_id,
        )

        return trigger_event

    async def _execute_action(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute a single action."""
        if action.action_type == ActionType.PUSH_ALERT:
            await self._execute_push_alert(action, context)
        elif action.action_type == ActionType.SEND_BULLETIN:
            await self._execute_send_bulletin(action, context)
        elif action.action_type == ActionType.SEND_MESSAGE:
            await self._execute_send_message(action, context)
        elif action.action_type == ActionType.NOTIFY_RTCC:
            await self._execute_notify_rtcc(action, context)
        elif action.action_type == ActionType.NOTIFY_COMMAND:
            await self._execute_notify_command(action, context)
        elif action.action_type == ActionType.LOG_EVENT:
            await self._execute_log_event(action, context)
        else:
            logger.warning("unsupported_action_type", action_type=action.action_type.value)

    async def _execute_push_alert(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute push alert action."""
        if not self.alerts:
            logger.warning("alerts_manager_not_configured")
            return

        # Substitute template variables
        title = self._substitute_template(action.alert_title_template or "", context)
        body = self._substitute_template(action.alert_body_template or "", context)

        from .alerts import AlertPriority, AlertType

        await self.alerts.create_alert(
            alert_type=AlertType(action.alert_type or "system"),
            title=title,
            body=body,
            priority=AlertPriority(action.alert_priority or "normal"),
            target_badges=action.target_badges,
            target_shifts=action.target_shifts,
            target_districts=action.target_districts,
            broadcast_all=action.broadcast_all,
            latitude=context.get("latitude"),
            longitude=context.get("longitude"),
            address=context.get("address"),
            metadata={"triggered_by_rule": True, "context": context},
        )

    async def _execute_send_bulletin(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute send bulletin action."""
        if not self.bulletins:
            logger.warning("bulletin_manager_not_configured")
            return

        if action.bulletin_template_id:
            await self.bulletins.create_bulletin_from_template(
                template_id=action.bulletin_template_id,
                variables=context,
                target_shifts=action.target_shifts,
                target_districts=action.target_districts,
                auto_publish=True,
            )

    async def _execute_send_message(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute send message action."""
        if not self.messaging:
            logger.warning("messaging_manager_not_configured")
            return

        content = self._substitute_template(action.message_template or "", context)

        from .messaging import MessageType

        await self.messaging.send_message(
            sender_id="system",
            sender_name="RTCC System",
            sender_type="system",
            channel_id=action.channel_id or "broadcast",
            content=content,
            message_type=MessageType.ALERT,
        )

    async def _execute_notify_rtcc(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute notify RTCC action."""
        # Would integrate with RTCC notification system
        logger.info("rtcc_notified", context=context)

    async def _execute_notify_command(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute notify command staff action."""
        # Would integrate with command notification system
        logger.info("command_notified", context=context)

    async def _execute_log_event(
        self,
        action: RuleAction,
        context: dict[str, Any],
    ) -> None:
        """Execute log event action."""
        logger.info("rule_event_logged", context=context)

    def _substitute_template(
        self,
        template: str,
        context: dict[str, Any],
    ) -> str:
        """Substitute template variables with context values."""
        try:
            return template.format(**context)
        except KeyError:
            # Return template with missing keys as-is
            result = template
            for key, value in context.items():
                result = result.replace(f"{{{key}}}", str(value))
            return result

    async def create_rule(
        self,
        name: str,
        conditions: list[RuleCondition],
        actions: list[RuleAction],
        description: str | None = None,
        priority: RulePriority = RulePriority.NORMAL,
        condition_operator: RuleOperator = RuleOperator.AND,
        event_sources: list[str] | None = None,
        cooldown_seconds: int = 0,
        max_triggers_per_hour: int | None = None,
        created_by: str | None = None,
    ) -> NotificationRule:
        """
        Create a new notification rule.

        Args:
            name: Rule name
            conditions: List of conditions
            actions: List of actions
            description: Rule description
            priority: Rule priority
            condition_operator: How to combine conditions
            event_sources: Event sources to apply to
            cooldown_seconds: Cooldown between triggers
            max_triggers_per_hour: Max triggers per hour
            created_by: User who created

        Returns:
            The created rule
        """
        rule = NotificationRule(
            name=name,
            description=description,
            priority=priority,
            conditions=conditions,
            condition_operator=condition_operator,
            actions=actions,
            event_sources=event_sources or [],
            cooldown_seconds=cooldown_seconds,
            max_triggers_per_hour=max_triggers_per_hour,
            created_by=created_by,
        )

        self._rules[rule.id] = rule

        logger.info(
            "rule_created",
            rule_id=rule.id,
            rule_name=name,
            audit_id=rule.audit_id,
        )

        return rule

    async def update_rule(
        self,
        rule_id: str,
        **updates: Any,
    ) -> NotificationRule:
        """Update an existing rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        if rule.is_system:
            raise ValueError("Cannot modify system rules")

        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        rule.updated_at = datetime.now(UTC)

        logger.info("rule_updated", rule_id=rule_id)

        return rule

    async def delete_rule(self, rule_id: str) -> None:
        """Delete a rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        if rule.is_system:
            raise ValueError("Cannot delete system rules")

        del self._rules[rule_id]

        logger.info("rule_deleted", rule_id=rule_id)

    async def toggle_rule(self, rule_id: str, is_active: bool) -> NotificationRule:
        """Toggle rule active status."""
        rule = self._rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        rule.is_active = is_active
        rule.updated_at = datetime.now(UTC)

        logger.info("rule_toggled", rule_id=rule_id, is_active=is_active)

        return rule

    async def test_rule(
        self,
        rule_id: str,
        test_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Test a rule against a context without executing actions.

        Args:
            rule_id: Rule ID to test
            test_context: Test context data

        Returns:
            Test results
        """
        rule = self._rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        # Evaluate conditions
        condition_results = []
        for condition in rule.conditions:
            result = condition.evaluate(test_context)
            condition_results.append({
                "condition_type": condition.condition_type.value,
                "field": condition.field,
                "operator": condition.operator,
                "value": condition.value,
                "result": result,
            })

        # Overall result
        would_trigger = self._evaluate_conditions(rule, test_context)

        return {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "would_trigger": would_trigger,
            "condition_results": condition_results,
            "actions_that_would_execute": [a.action_type.value for a in rule.actions],
        }

    def get_rule(self, rule_id: str) -> NotificationRule | None:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self, include_system: bool = True) -> list[NotificationRule]:
        """Get all rules."""
        rules = list(self._rules.values())
        if not include_system:
            rules = [r for r in rules if not r.is_system]
        return rules

    def get_trigger_history(
        self,
        rule_id: str | None = None,
        limit: int = 100,
    ) -> list[RuleTriggerEvent]:
        """Get rule trigger history."""
        events = self._trigger_history
        if rule_id:
            events = [e for e in events if e.rule_id == rule_id]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]


# Export classes
__all__ = [
    "NotificationRulesEngine",
    "NotificationRule",
    "RuleCondition",
    "RuleAction",
    "RuleTriggerEvent",
    "ConditionType",
    "ActionType",
    "RuleOperator",
    "RulePriority",
]
