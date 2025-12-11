"""
Phase 25: Policy Translator Engine

Transforms natural-language policies into structured machine-readable rules.
Handles ambiguities, conflicts, precedence, and overrides.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import re
import json


class RuleOperator(Enum):
    """Operators for rule conditions."""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    AND = "and"
    OR = "or"
    NOT = "not"


class RuleAction(Enum):
    """Actions that rules can trigger."""
    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_APPROVAL = "require_approval"
    ALERT = "alert"
    LOG = "log"
    ESCALATE = "escalate"
    MODIFY = "modify"


class ConflictType(Enum):
    """Types of policy conflicts."""
    DIRECT_CONTRADICTION = "direct_contradiction"
    PARTIAL_OVERLAP = "partial_overlap"
    PRECEDENCE_AMBIGUITY = "precedence_ambiguity"
    SCOPE_CONFLICT = "scope_conflict"


class AmbiguityType(Enum):
    """Types of ambiguities in natural language policies."""
    UNDEFINED_TERM = "undefined_term"
    VAGUE_CONDITION = "vague_condition"
    MISSING_SCOPE = "missing_scope"
    UNCLEAR_ACTION = "unclear_action"
    TEMPORAL_AMBIGUITY = "temporal_ambiguity"


@dataclass
class RuleCondition:
    """A single condition in a machine rule."""
    variable: str
    operator: RuleOperator
    value: Any
    
    def to_expression(self) -> str:
        """Convert to expression string."""
        if self.operator == RuleOperator.IS_TRUE:
            return f"{self.variable}"
        elif self.operator == RuleOperator.IS_FALSE:
            return f"NOT {self.variable}"
        elif self.operator == RuleOperator.CONTAINS:
            return f"{self.variable} CONTAINS '{self.value}'"
        elif self.operator == RuleOperator.IN:
            return f"{self.variable} IN {self.value}"
        else:
            return f"{self.variable} {self.operator.value} {repr(self.value)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variable": self.variable,
            "operator": self.operator.value,
            "value": self.value,
        }


@dataclass
class CompositeCondition:
    """A composite condition combining multiple conditions."""
    operator: RuleOperator  # AND, OR, NOT
    conditions: List['RuleCondition | CompositeCondition']
    
    def to_expression(self) -> str:
        """Convert to expression string."""
        if self.operator == RuleOperator.NOT:
            return f"NOT ({self.conditions[0].to_expression()})"
        
        op_str = " AND " if self.operator == RuleOperator.AND else " OR "
        parts = [c.to_expression() for c in self.conditions]
        return f"({op_str.join(parts)})"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator.value,
            "conditions": [c.to_dict() for c in self.conditions],
        }


@dataclass
class RuleActionSpec:
    """Specification for a rule action."""
    action: RuleAction
    parameters: Dict[str, Any]
    
    def to_expression(self) -> str:
        """Convert to expression string."""
        if self.parameters:
            params = ", ".join(f"{k}={repr(v)}" for k, v in self.parameters.items())
            return f"{self.action.value}({params})"
        return self.action.value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "parameters": self.parameters,
        }


@dataclass
class PolicyAmbiguity:
    """Represents an ambiguity found in a policy."""
    ambiguity_id: str
    ambiguity_type: AmbiguityType
    location: str
    description: str
    suggestions: List[str]
    severity: str  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ambiguity_id": self.ambiguity_id,
            "ambiguity_type": self.ambiguity_type.value,
            "location": self.location,
            "description": self.description,
            "suggestions": self.suggestions,
            "severity": self.severity,
        }


@dataclass
class PolicyConflict:
    """Represents a conflict between policies."""
    conflict_id: str
    conflict_type: ConflictType
    policy_a_id: str
    policy_b_id: str
    description: str
    resolution_options: List[str]
    recommended_resolution: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "policy_a_id": self.policy_a_id,
            "policy_b_id": self.policy_b_id,
            "description": self.description,
            "resolution_options": self.resolution_options,
            "recommended_resolution": self.recommended_resolution,
        }


@dataclass
class MachineRule:
    """A machine-readable rule translated from natural language."""
    rule_id: str
    original_text: str
    name: str
    description: str
    condition: CompositeCondition | RuleCondition
    action: RuleActionSpec
    variables: Dict[str, str]
    confidence: float
    ambiguities: List[PolicyAmbiguity]
    precedence: int
    overrides: List[str]
    scope: Dict[str, Any]
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "original_text": self.original_text,
            "name": self.name,
            "description": self.description,
            "condition_expression": self.condition.to_expression(),
            "condition": self.condition.to_dict(),
            "action_expression": self.action.to_expression(),
            "action": self.action.to_dict(),
            "variables": self.variables,
            "confidence": self.confidence,
            "ambiguities": [a.to_dict() for a in self.ambiguities],
            "precedence": self.precedence,
            "overrides": self.overrides,
            "scope": self.scope,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "created_at": self.created_at.isoformat(),
        }
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the rule against a context."""
        return self._evaluate_condition(self.condition, context)
    
    def _evaluate_condition(
        self,
        condition: CompositeCondition | RuleCondition,
        context: Dict[str, Any],
    ) -> bool:
        """Recursively evaluate a condition."""
        if isinstance(condition, RuleCondition):
            return self._evaluate_simple_condition(condition, context)
        
        # Composite condition
        if condition.operator == RuleOperator.AND:
            return all(self._evaluate_condition(c, context) for c in condition.conditions)
        elif condition.operator == RuleOperator.OR:
            return any(self._evaluate_condition(c, context) for c in condition.conditions)
        elif condition.operator == RuleOperator.NOT:
            return not self._evaluate_condition(condition.conditions[0], context)
        
        return False
    
    def _evaluate_simple_condition(
        self,
        condition: RuleCondition,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a simple condition."""
        # Get value from context using dot notation
        value = self._get_nested_value(context, condition.variable)
        
        if condition.operator == RuleOperator.IS_TRUE:
            return bool(value)
        elif condition.operator == RuleOperator.IS_FALSE:
            return not bool(value)
        elif condition.operator == RuleOperator.EQUALS:
            return value == condition.value
        elif condition.operator == RuleOperator.NOT_EQUALS:
            return value != condition.value
        elif condition.operator == RuleOperator.GREATER_THAN:
            return value > condition.value
        elif condition.operator == RuleOperator.LESS_THAN:
            return value < condition.value
        elif condition.operator == RuleOperator.GREATER_THAN_OR_EQUAL:
            return value >= condition.value
        elif condition.operator == RuleOperator.LESS_THAN_OR_EQUAL:
            return value <= condition.value
        elif condition.operator == RuleOperator.CONTAINS:
            return condition.value in str(value)
        elif condition.operator == RuleOperator.NOT_CONTAINS:
            return condition.value not in str(value)
        elif condition.operator == RuleOperator.IN:
            return value in condition.value
        elif condition.operator == RuleOperator.NOT_IN:
            return value not in condition.value
        
        return False
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get a nested value using dot notation."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current


@dataclass
class TranslationResult:
    """Result of translating a natural language policy."""
    success: bool
    rule: Optional[MachineRule]
    ambiguities: List[PolicyAmbiguity]
    confidence: float
    warnings: List[str]
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "rule": self.rule.to_dict() if self.rule else None,
            "ambiguities": [a.to_dict() for a in self.ambiguities],
            "confidence": self.confidence,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }


class PolicyTranslatorEngine:
    """
    Policy Translator Engine
    
    Transforms natural-language policies into structured machine-readable rules.
    Handles ambiguities, conflicts, precedence, and overrides.
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
        
        self._rules: Dict[str, MachineRule] = {}
        self._conflicts: Dict[str, PolicyConflict] = {}
        self._translation_history: List[TranslationResult] = []
        
        # Pattern matching for natural language parsing
        self._condition_patterns = self._initialize_condition_patterns()
        self._action_patterns = self._initialize_action_patterns()
        self._variable_mappings = self._initialize_variable_mappings()
        
        self._initialized = True
    
    def _initialize_condition_patterns(self) -> List[Dict[str, Any]]:
        """Initialize patterns for parsing conditions from natural language."""
        return [
            # Property/location patterns
            {
                "pattern": r"(?:cannot|must not|shall not|may not)\s+(?:enter|access)\s+(?:private\s+)?property",
                "variable": "enters_private_property",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
                "action": RuleAction.BLOCK,
            },
            {
                "pattern": r"(?:on|in|within)\s+private\s+property",
                "variable": "location.is_private_property",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            # Exigent circumstances
            {
                "pattern": r"(?:without|unless)\s+(?:exigent\s+)?circumstances",
                "variable": "exigent_circumstances",
                "operator": RuleOperator.IS_FALSE,
                "value": False,
                "negate": True,
            },
            {
                "pattern": r"(?:with|if|when)\s+exigent\s+circumstances",
                "variable": "exigent_circumstances",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            # Warrant patterns
            {
                "pattern": r"(?:without|unless)\s+(?:a\s+)?warrant",
                "variable": "has_warrant",
                "operator": RuleOperator.IS_FALSE,
                "value": False,
                "negate": True,
            },
            {
                "pattern": r"(?:with|if|when)\s+(?:a\s+)?warrant",
                "variable": "has_warrant",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            # Consent patterns
            {
                "pattern": r"(?:without|unless)\s+consent",
                "variable": "consent_given",
                "operator": RuleOperator.IS_FALSE,
                "value": False,
                "negate": True,
            },
            {
                "pattern": r"(?:with|if|when)\s+consent",
                "variable": "consent_given",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            # Emergency patterns
            {
                "pattern": r"(?:during|in)\s+(?:an?\s+)?emergency",
                "variable": "emergency_declared",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            {
                "pattern": r"(?:not\s+)?(?:during|in)\s+(?:an?\s+)?emergency",
                "variable": "emergency_declared",
                "operator": RuleOperator.IS_FALSE,
                "value": False,
            },
            # Time-based patterns
            {
                "pattern": r"(?:after|past)\s+(\d{1,2})\s*(?:pm|PM)",
                "variable": "time_of_day",
                "operator": RuleOperator.GREATER_THAN,
                "value_extract": lambda m: int(m.group(1)) + 12,
            },
            {
                "pattern": r"(?:before)\s+(\d{1,2})\s*(?:am|AM)",
                "variable": "time_of_day",
                "operator": RuleOperator.LESS_THAN,
                "value_extract": lambda m: int(m.group(1)),
            },
            # Risk/severity patterns
            {
                "pattern": r"(?:high|elevated)\s+risk",
                "variable": "risk_score",
                "operator": RuleOperator.GREATER_THAN_OR_EQUAL,
                "value": 0.7,
            },
            {
                "pattern": r"(?:low)\s+risk",
                "variable": "risk_score",
                "operator": RuleOperator.LESS_THAN,
                "value": 0.3,
            },
            # Subject patterns
            {
                "pattern": r"drones?\s+(?:cannot|must not|shall not)",
                "variable": "is_drone_operation",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            {
                "pattern": r"robot(?:ic)?s?\s+(?:cannot|must not|shall not)",
                "variable": "is_robotics_operation",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
            },
            # Approval patterns
            {
                "pattern": r"(?:requires?|needs?)\s+(?:supervisor\s+)?approval",
                "variable": "requires_approval",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
                "action": RuleAction.REQUIRE_APPROVAL,
            },
            {
                "pattern": r"(?:requires?|needs?)\s+human\s+(?:review|approval|confirmation)",
                "variable": "requires_human_review",
                "operator": RuleOperator.IS_TRUE,
                "value": True,
                "action": RuleAction.REQUIRE_APPROVAL,
            },
        ]
    
    def _initialize_action_patterns(self) -> List[Dict[str, Any]]:
        """Initialize patterns for parsing actions from natural language."""
        return [
            {
                "pattern": r"(?:block|deny|prohibit|prevent|cannot|must not|shall not|may not)",
                "action": RuleAction.BLOCK,
            },
            {
                "pattern": r"(?:allow|permit|authorize|may|can)",
                "action": RuleAction.ALLOW,
            },
            {
                "pattern": r"(?:require|need)\s+(?:approval|authorization|review)",
                "action": RuleAction.REQUIRE_APPROVAL,
            },
            {
                "pattern": r"(?:alert|notify|warn)",
                "action": RuleAction.ALERT,
            },
            {
                "pattern": r"(?:log|record|document)",
                "action": RuleAction.LOG,
            },
            {
                "pattern": r"(?:escalate|elevate)",
                "action": RuleAction.ESCALATE,
            },
        ]
    
    def _initialize_variable_mappings(self) -> Dict[str, str]:
        """Initialize mappings from natural language terms to variables."""
        return {
            "private property": "location.is_private_property",
            "public property": "location.is_public_property",
            "drone": "is_drone_operation",
            "drones": "is_drone_operation",
            "robot": "is_robotics_operation",
            "robots": "is_robotics_operation",
            "robotics": "is_robotics_operation",
            "surveillance": "is_surveillance",
            "exigent circumstances": "exigent_circumstances",
            "exigent": "exigent_circumstances",
            "warrant": "has_warrant",
            "consent": "consent_given",
            "emergency": "emergency_declared",
            "force": "involves_force",
            "use of force": "involves_force",
            "deadly force": "involves_deadly_force",
            "pursuit": "is_pursuit",
            "chase": "is_pursuit",
            "evacuation": "is_evacuation",
            "curfew": "is_curfew",
            "mass alert": "is_mass_alert",
            "predictive": "uses_predictive_model",
            "predictive policing": "uses_predictive_model",
        }
    
    def translate_policy(
        self,
        policy_text: str,
        name: Optional[str] = None,
        precedence: int = 50,
        scope: Optional[Dict[str, Any]] = None,
    ) -> TranslationResult:
        """
        Translate a natural language policy into a machine rule.
        
        Args:
            policy_text: The natural language policy text
            name: Optional name for the rule
            precedence: Rule precedence (higher = more important)
            scope: Optional scope restrictions
        
        Returns:
            TranslationResult with the translated rule and any issues
        """
        ambiguities: List[PolicyAmbiguity] = []
        warnings: List[str] = []
        suggestions: List[str] = []
        confidence = 1.0
        
        # Normalize text
        normalized_text = policy_text.lower().strip()
        
        # Extract conditions
        conditions, cond_ambiguities = self._extract_conditions(normalized_text)
        ambiguities.extend(cond_ambiguities)
        
        # Extract action
        action, action_confidence = self._extract_action(normalized_text)
        confidence *= action_confidence
        
        # Extract variables
        variables = self._extract_variables(normalized_text)
        
        # Check for ambiguities
        text_ambiguities = self._detect_ambiguities(normalized_text, conditions)
        ambiguities.extend(text_ambiguities)
        
        # Adjust confidence based on ambiguities
        for amb in ambiguities:
            if amb.severity == "high":
                confidence *= 0.5
            elif amb.severity == "medium":
                confidence *= 0.7
            elif amb.severity == "low":
                confidence *= 0.9
        
        # Generate warnings
        if not conditions:
            warnings.append("No conditions could be extracted from the policy text")
            confidence *= 0.3
        
        if action.action == RuleAction.BLOCK and not conditions:
            warnings.append("Blocking action without conditions may block all actions")
        
        # Generate suggestions
        if confidence < 0.7:
            suggestions.append("Consider rephrasing the policy with more specific conditions")
        
        if ambiguities:
            suggestions.append("Review and resolve the identified ambiguities")
        
        # Build the rule
        if conditions:
            if len(conditions) == 1:
                final_condition = conditions[0]
            else:
                final_condition = CompositeCondition(
                    operator=RuleOperator.AND,
                    conditions=conditions,
                )
        else:
            # Default condition that always matches
            final_condition = RuleCondition(
                variable="always",
                operator=RuleOperator.IS_TRUE,
                value=True,
            )
        
        rule = MachineRule(
            rule_id=f"rule-{uuid4().hex[:12]}",
            original_text=policy_text,
            name=name or f"Policy Rule {datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=f"Translated from: {policy_text[:100]}...",
            condition=final_condition,
            action=action,
            variables=variables,
            confidence=confidence,
            ambiguities=ambiguities,
            precedence=precedence,
            overrides=[],
            scope=scope or {},
        )
        
        result = TranslationResult(
            success=confidence >= 0.3,
            rule=rule if confidence >= 0.3 else None,
            ambiguities=ambiguities,
            confidence=confidence,
            warnings=warnings,
            suggestions=suggestions,
        )
        
        self._translation_history.append(result)
        
        if result.success and rule:
            self._rules[rule.rule_id] = rule
        
        return result
    
    def _extract_conditions(
        self,
        text: str,
    ) -> Tuple[List[RuleCondition], List[PolicyAmbiguity]]:
        """Extract conditions from natural language text."""
        conditions: List[RuleCondition] = []
        ambiguities: List[PolicyAmbiguity] = []
        
        for pattern_info in self._condition_patterns:
            pattern = pattern_info["pattern"]
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                variable = pattern_info["variable"]
                operator = pattern_info["operator"]
                
                # Get value
                if "value_extract" in pattern_info:
                    value = pattern_info["value_extract"](match)
                else:
                    value = pattern_info.get("value", True)
                
                # Handle negation
                if pattern_info.get("negate", False):
                    if operator == RuleOperator.IS_TRUE:
                        operator = RuleOperator.IS_FALSE
                    elif operator == RuleOperator.IS_FALSE:
                        operator = RuleOperator.IS_TRUE
                
                condition = RuleCondition(
                    variable=variable,
                    operator=operator,
                    value=value,
                )
                conditions.append(condition)
        
        return conditions, ambiguities
    
    def _extract_action(self, text: str) -> Tuple[RuleActionSpec, float]:
        """Extract the action from natural language text."""
        confidence = 1.0
        
        for pattern_info in self._action_patterns:
            pattern = pattern_info["pattern"]
            if re.search(pattern, text, re.IGNORECASE):
                return RuleActionSpec(
                    action=pattern_info["action"],
                    parameters={},
                ), confidence
        
        # Default action with lower confidence
        return RuleActionSpec(
            action=RuleAction.LOG,
            parameters={},
        ), 0.5
    
    def _extract_variables(self, text: str) -> Dict[str, str]:
        """Extract variable mappings from the text."""
        variables = {}
        
        for term, variable in self._variable_mappings.items():
            if term in text:
                variables[term] = variable
        
        return variables
    
    def _detect_ambiguities(
        self,
        text: str,
        conditions: List[RuleCondition],
    ) -> List[PolicyAmbiguity]:
        """Detect ambiguities in the policy text."""
        ambiguities = []
        
        # Check for vague terms
        vague_terms = ["sometimes", "usually", "often", "rarely", "may", "might", "could"]
        for term in vague_terms:
            if term in text:
                ambiguities.append(PolicyAmbiguity(
                    ambiguity_id=f"amb-{uuid4().hex[:8]}",
                    ambiguity_type=AmbiguityType.VAGUE_CONDITION,
                    location=term,
                    description=f"Vague term '{term}' found - unclear when condition applies",
                    suggestions=[
                        f"Replace '{term}' with specific conditions",
                        "Define exact thresholds or criteria",
                    ],
                    severity="medium",
                ))
        
        # Check for undefined terms
        undefined_patterns = [
            (r"appropriate", "What constitutes 'appropriate'?"),
            (r"reasonable", "What constitutes 'reasonable'?"),
            (r"necessary", "What constitutes 'necessary'?"),
            (r"sufficient", "What constitutes 'sufficient'?"),
        ]
        
        for pattern, question in undefined_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                ambiguities.append(PolicyAmbiguity(
                    ambiguity_id=f"amb-{uuid4().hex[:8]}",
                    ambiguity_type=AmbiguityType.UNDEFINED_TERM,
                    location=pattern,
                    description=question,
                    suggestions=[
                        "Define specific criteria",
                        "Provide measurable thresholds",
                    ],
                    severity="medium",
                ))
        
        # Check for missing scope
        if not any(term in text for term in ["drone", "robot", "surveillance", "patrol", "force"]):
            ambiguities.append(PolicyAmbiguity(
                ambiguity_id=f"amb-{uuid4().hex[:8]}",
                ambiguity_type=AmbiguityType.MISSING_SCOPE,
                location="entire policy",
                description="No specific action type or subject identified",
                suggestions=[
                    "Specify what type of action this policy applies to",
                    "Add subject (e.g., 'drones', 'officers', 'AI system')",
                ],
                severity="high",
            ))
        
        # Check for temporal ambiguity
        temporal_terms = ["before", "after", "during", "when", "while"]
        temporal_found = [t for t in temporal_terms if t in text]
        if temporal_found and not re.search(r"\d", text):
            ambiguities.append(PolicyAmbiguity(
                ambiguity_id=f"amb-{uuid4().hex[:8]}",
                ambiguity_type=AmbiguityType.TEMPORAL_AMBIGUITY,
                location=", ".join(temporal_found),
                description="Temporal reference without specific time",
                suggestions=[
                    "Add specific time constraints",
                    "Define duration or deadline",
                ],
                severity="low",
            ))
        
        return ambiguities
    
    def detect_conflicts(
        self,
        rule_a: MachineRule,
        rule_b: MachineRule,
    ) -> Optional[PolicyConflict]:
        """Detect conflicts between two rules."""
        
        # Check for direct contradiction
        if (rule_a.action.action == RuleAction.ALLOW and 
            rule_b.action.action == RuleAction.BLOCK):
            # Check if conditions overlap
            if self._conditions_overlap(rule_a.condition, rule_b.condition):
                return PolicyConflict(
                    conflict_id=f"conflict-{uuid4().hex[:8]}",
                    conflict_type=ConflictType.DIRECT_CONTRADICTION,
                    policy_a_id=rule_a.rule_id,
                    policy_b_id=rule_b.rule_id,
                    description=f"Rule '{rule_a.name}' allows what rule '{rule_b.name}' blocks",
                    resolution_options=[
                        "Assign different precedence levels",
                        "Add distinguishing conditions",
                        "Remove one of the conflicting rules",
                    ],
                    recommended_resolution="Assign different precedence levels",
                )
        
        # Check for precedence ambiguity
        if rule_a.precedence == rule_b.precedence:
            if self._conditions_overlap(rule_a.condition, rule_b.condition):
                return PolicyConflict(
                    conflict_id=f"conflict-{uuid4().hex[:8]}",
                    conflict_type=ConflictType.PRECEDENCE_AMBIGUITY,
                    policy_a_id=rule_a.rule_id,
                    policy_b_id=rule_b.rule_id,
                    description=f"Rules '{rule_a.name}' and '{rule_b.name}' have same precedence with overlapping conditions",
                    resolution_options=[
                        "Assign different precedence levels",
                        "Merge rules into one",
                    ],
                    recommended_resolution="Assign different precedence levels",
                )
        
        return None
    
    def _conditions_overlap(
        self,
        cond_a: CompositeCondition | RuleCondition,
        cond_b: CompositeCondition | RuleCondition,
    ) -> bool:
        """Check if two conditions could potentially overlap."""
        # Simplified overlap detection
        vars_a = self._get_condition_variables(cond_a)
        vars_b = self._get_condition_variables(cond_b)
        
        # If they share variables, they might overlap
        return bool(vars_a & vars_b)
    
    def _get_condition_variables(
        self,
        condition: CompositeCondition | RuleCondition,
    ) -> set:
        """Get all variables referenced in a condition."""
        if isinstance(condition, RuleCondition):
            return {condition.variable}
        
        variables = set()
        for sub_cond in condition.conditions:
            variables.update(self._get_condition_variables(sub_cond))
        return variables
    
    def detect_all_conflicts(self) -> List[PolicyConflict]:
        """Detect all conflicts among stored rules."""
        conflicts = []
        rules = list(self._rules.values())
        
        for i, rule_a in enumerate(rules):
            for rule_b in rules[i + 1:]:
                conflict = self.detect_conflicts(rule_a, rule_b)
                if conflict:
                    conflicts.append(conflict)
                    self._conflicts[conflict.conflict_id] = conflict
        
        return conflicts
    
    def get_rule(self, rule_id: str) -> Optional[MachineRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def get_all_rules(self) -> List[MachineRule]:
        """Get all translated rules."""
        return list(self._rules.values())
    
    def get_conflicts(self) -> List[PolicyConflict]:
        """Get all detected conflicts."""
        return list(self._conflicts.values())
    
    def validate_policy(self, policy_text: str) -> Dict[str, Any]:
        """Validate a policy without storing it."""
        result = self.translate_policy(policy_text)
        
        # Remove from storage if it was added
        if result.rule and result.rule.rule_id in self._rules:
            del self._rules[result.rule.rule_id]
        
        return {
            "valid": result.success,
            "confidence": result.confidence,
            "ambiguities": [a.to_dict() for a in result.ambiguities],
            "warnings": result.warnings,
            "suggestions": result.suggestions,
            "preview": result.rule.to_dict() if result.rule else None,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translator statistics."""
        return {
            "total_rules": len(self._rules),
            "total_conflicts": len(self._conflicts),
            "total_translations": len(self._translation_history),
            "successful_translations": len([t for t in self._translation_history if t.success]),
            "average_confidence": (
                sum(t.confidence for t in self._translation_history) / len(self._translation_history)
                if self._translation_history else 0
            ),
        }


# Singleton accessor
_policy_translator_instance: Optional[PolicyTranslatorEngine] = None


def get_policy_translator() -> PolicyTranslatorEngine:
    """Get the singleton PolicyTranslatorEngine instance."""
    global _policy_translator_instance
    if _policy_translator_instance is None:
        _policy_translator_instance = PolicyTranslatorEngine()
    return _policy_translator_instance
