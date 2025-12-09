"""Tests for the Notification Rules Engine module."""


import pytest

from app.comms.rules_engine import (
    ActionType,
    ConditionType,
    NotificationRule,
    NotificationRulesEngine,
    RuleAction,
    RuleCondition,
    RuleOperator,
    RulePriority,
    RuleTriggerEvent,
)


@pytest.fixture
def rules_engine():
    """Create a rules engine instance."""
    return NotificationRulesEngine()


class TestNotificationRulesEngine:
    """Tests for NotificationRulesEngine."""

    @pytest.mark.asyncio
    async def test_default_rules_initialized(self, rules_engine):
        """Test that default rules are initialized."""
        rules = rules_engine.get_all_rules()

        assert len(rules) > 0
        assert any(r.id == "gunfire_officer_proximity" for r in rules)
        assert any(r.id == "cad_p1_scene_intel" for r in rules)

    @pytest.mark.asyncio
    async def test_evaluate_event_gunfire(self, rules_engine):
        """Test evaluating a gunfire event."""
        context = {
            "event_type": "gunfire_detected",
            "rounds": 5,
            "latitude": 33.7490,
            "longitude": -84.3880,
            "address": "123 Main St",
        }

        triggered = await rules_engine.evaluate_event(
            event_source="shotspotter",
            event_type="gunfire_detected",
            context=context,
        )

        # Should trigger the gunfire_officer_proximity rule
        assert any(t.rule_id == "gunfire_officer_proximity" for t in triggered)

    @pytest.mark.asyncio
    async def test_evaluate_event_cad_p1(self, rules_engine):
        """Test evaluating a P1 CAD call event."""
        context = {
            "event_type": "cad_call_created",
            "priority": "P1",
            "call_type": "Shots Fired",
            "address": "456 Oak Ave",
            "description": "Multiple shots heard",
        }

        triggered = await rules_engine.evaluate_event(
            event_source="cad",
            event_type="cad_call_created",
            context=context,
        )

        assert any(t.rule_id == "cad_p1_scene_intel" for t in triggered)

    @pytest.mark.asyncio
    async def test_evaluate_event_no_match(self, rules_engine):
        """Test evaluating an event that doesn't match any rules."""
        context = {
            "event_type": "routine_patrol",
            "unit_id": "Alpha-11",
        }

        triggered = await rules_engine.evaluate_event(
            event_source="patrol",
            event_type="routine_patrol",
            context=context,
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_create_rule(self, rules_engine):
        """Test creating a custom rule."""
        conditions = [
            RuleCondition(
                condition_type=ConditionType.EVENT_TYPE,
                value="custom_event",
            ),
        ]
        actions = [
            RuleAction(
                action_type=ActionType.LOG_EVENT,
            ),
        ]

        rule = await rules_engine.create_rule(
            name="Custom Test Rule",
            conditions=conditions,
            actions=actions,
            description="A test rule",
            priority=RulePriority.NORMAL,
        )

        assert rule is not None
        assert rule.name == "Custom Test Rule"
        assert rule.is_system is False

    @pytest.mark.asyncio
    async def test_toggle_rule(self, rules_engine):
        """Test toggling a rule's active status."""
        # Create a custom rule
        rule = await rules_engine.create_rule(
            name="Toggle Test Rule",
            conditions=[],
            actions=[],
        )

        # Toggle off
        updated = await rules_engine.toggle_rule(rule.id, False)
        assert updated.is_active is False

        # Toggle on
        updated = await rules_engine.toggle_rule(rule.id, True)
        assert updated.is_active is True

    @pytest.mark.asyncio
    async def test_delete_rule(self, rules_engine):
        """Test deleting a custom rule."""
        rule = await rules_engine.create_rule(
            name="Delete Test Rule",
            conditions=[],
            actions=[],
        )

        await rules_engine.delete_rule(rule.id)

        assert rules_engine.get_rule(rule.id) is None

    @pytest.mark.asyncio
    async def test_cannot_delete_system_rule(self, rules_engine):
        """Test that system rules cannot be deleted."""
        with pytest.raises(ValueError, match="Cannot delete system rules"):
            await rules_engine.delete_rule("gunfire_officer_proximity")

    @pytest.mark.asyncio
    async def test_test_rule(self, rules_engine):
        """Test testing a rule against a context."""
        result = await rules_engine.test_rule(
            rule_id="gunfire_officer_proximity",
            test_context={
                "event_type": "gunfire_detected",
                "rounds": 3,
            },
        )

        assert "would_trigger" in result
        assert "condition_results" in result
        assert result["would_trigger"] is True

    @pytest.mark.asyncio
    async def test_test_rule_no_trigger(self, rules_engine):
        """Test testing a rule that wouldn't trigger."""
        result = await rules_engine.test_rule(
            rule_id="gunfire_officer_proximity",
            test_context={
                "event_type": "other_event",
                "rounds": 0,
            },
        )

        assert result["would_trigger"] is False

    @pytest.mark.asyncio
    async def test_get_trigger_history(self, rules_engine):
        """Test getting trigger history."""
        # Trigger some rules
        await rules_engine.evaluate_event(
            event_source="shotspotter",
            event_type="gunfire_detected",
            context={"event_type": "gunfire_detected", "rounds": 5},
        )

        history = rules_engine.get_trigger_history()

        assert len(history) >= 1

    @pytest.mark.asyncio
    async def test_rule_cooldown(self, rules_engine):
        """Test rule cooldown."""
        # Create a rule with cooldown
        rule = await rules_engine.create_rule(
            name="Cooldown Test Rule",
            conditions=[
                RuleCondition(
                    condition_type=ConditionType.EVENT_TYPE,
                    value="cooldown_test",
                ),
            ],
            actions=[
                RuleAction(action_type=ActionType.LOG_EVENT),
            ],
            cooldown_seconds=60,
        )

        # First trigger should work
        triggered1 = await rules_engine.evaluate_event(
            event_source="test",
            event_type="cooldown_test",
            context={"event_type": "cooldown_test"},
        )

        assert any(t.rule_id == rule.id for t in triggered1)

        # Second trigger should be blocked by cooldown
        triggered2 = await rules_engine.evaluate_event(
            event_source="test",
            event_type="cooldown_test",
            context={"event_type": "cooldown_test"},
        )

        assert not any(t.rule_id == rule.id for t in triggered2)


class TestRuleCondition:
    """Tests for RuleCondition."""

    def test_evaluate_event_type(self):
        """Test evaluating event type condition."""
        condition = RuleCondition(
            condition_type=ConditionType.EVENT_TYPE,
            value="gunfire_detected",
        )

        assert condition.evaluate({"event_type": "gunfire_detected"}) is True
        assert condition.evaluate({"event_type": "other_event"}) is False

    def test_evaluate_threshold_greater_than(self):
        """Test evaluating threshold condition."""
        condition = RuleCondition(
            condition_type=ConditionType.THRESHOLD,
            field="rounds",
            operator="greater_than",
            value=3,
        )

        assert condition.evaluate({"rounds": 5}) is True
        assert condition.evaluate({"rounds": 2}) is False

    def test_evaluate_threshold_less_than(self):
        """Test evaluating less than threshold."""
        condition = RuleCondition(
            condition_type=ConditionType.THRESHOLD,
            field="score",
            operator="less_than",
            value=50,
        )

        assert condition.evaluate({"score": 30}) is True
        assert condition.evaluate({"score": 60}) is False

    def test_evaluate_call_priority(self):
        """Test evaluating call priority condition."""
        condition = RuleCondition(
            condition_type=ConditionType.CALL_PRIORITY,
            value="P1",
        )

        assert condition.evaluate({"priority": "P1"}) is True
        assert condition.evaluate({"priority": "P3"}) is False

    def test_evaluate_risk_level(self):
        """Test evaluating risk level condition."""
        condition = RuleCondition(
            condition_type=ConditionType.RISK_LEVEL,
            value="high",
        )

        assert condition.evaluate({"risk_level": "high"}) is True
        assert condition.evaluate({"risk_level": "low"}) is False

    def test_evaluate_officer_safety_in(self):
        """Test evaluating officer safety with 'in' operator."""
        condition = RuleCondition(
            condition_type=ConditionType.OFFICER_SAFETY,
            operator="in",
            value=["red", "black"],
        )

        assert condition.evaluate({"safety_level": "red"}) is True
        assert condition.evaluate({"safety_level": "green"}) is False

    def test_evaluate_pattern_match(self):
        """Test evaluating pattern match condition."""
        condition = RuleCondition(
            condition_type=ConditionType.PATTERN_MATCH,
            field="description",
            value=r"armed.*suspect",
        )

        assert condition.evaluate({"description": "Armed robbery suspect"}) is True
        assert condition.evaluate({"description": "Traffic violation"}) is False


class TestNotificationRuleModel:
    """Tests for NotificationRule model."""

    def test_rule_creation(self):
        """Test creating a notification rule."""
        rule = NotificationRule(
            name="Test Rule",
            conditions=[],
            actions=[],
        )

        assert rule.id is not None
        assert rule.is_active is True
        assert rule.is_system is False
        assert rule.audit_id is not None

    def test_rule_with_conditions_and_actions(self):
        """Test rule with conditions and actions."""
        rule = NotificationRule(
            name="Complex Rule",
            conditions=[
                RuleCondition(
                    condition_type=ConditionType.EVENT_TYPE,
                    value="test",
                ),
            ],
            actions=[
                RuleAction(
                    action_type=ActionType.PUSH_ALERT,
                    alert_type="test",
                    alert_title_template="Test Alert",
                ),
            ],
            condition_operator=RuleOperator.AND,
        )

        assert len(rule.conditions) == 1
        assert len(rule.actions) == 1


class TestRuleTriggerEventModel:
    """Tests for RuleTriggerEvent model."""

    def test_trigger_event_creation(self):
        """Test creating a trigger event."""
        event = RuleTriggerEvent(
            rule_id="rule-001",
            rule_name="Test Rule",
            event_source="shotspotter",
            event_type="gunfire_detected",
            context={"rounds": 5},
            actions_executed=["push_alert"],
        )

        assert event.id is not None
        assert event.success is True
        assert event.audit_id is not None
