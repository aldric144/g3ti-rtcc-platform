"""
Persona Interaction Engine

Handles natural language interaction with AI Personas including:
- Natural language to operational intent pipeline
- Domain routing (intel, patrol, robotics, crisis, etc.)
- Multi-turn conversation memory
- Emotion and urgency detection
- Role-appropriate responses
- Full explainability trace

Supports 4 interaction interfaces:
- RTCC console chat
- Mobile MDT chat
- Voice-to-text radio assist
- WebSocket interactive channels
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
    EmotionalState,
    Persona,
)


class InteractionType(Enum):
    """Types of interaction interfaces."""
    RTCC_CONSOLE = "rtcc_console"
    MOBILE_MDT = "mobile_mdt"
    VOICE_RADIO = "voice_radio"
    WEBSOCKET = "websocket"
    API = "api"


class IntentCategory(Enum):
    """Categories of operational intent."""
    QUERY = "query"
    COMMAND = "command"
    REPORT = "report"
    REQUEST = "request"
    ALERT = "alert"
    ANALYSIS = "analysis"
    COORDINATION = "coordination"
    DEESCALATION = "deescalation"
    INVESTIGATION = "investigation"
    TACTICAL = "tactical"
    ADMINISTRATIVE = "administrative"
    UNKNOWN = "unknown"


class UrgencyLevel(Enum):
    """Urgency levels for interactions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


class EmotionDetected(Enum):
    """Detected emotions in user input."""
    NEUTRAL = "neutral"
    STRESSED = "stressed"
    URGENT = "urgent"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    CONFUSED = "confused"


class DomainType(Enum):
    """Operational domains for routing."""
    PATROL = "patrol"
    COMMAND = "command"
    INTELLIGENCE = "intelligence"
    CRISIS = "crisis"
    ROBOTICS = "robotics"
    INVESTIGATIONS = "investigations"
    GENERAL = "general"


@dataclass
class IntentAnalysis:
    """Analysis of user intent from natural language."""
    intent_id: str
    raw_input: str
    intent_category: IntentCategory
    domain: DomainType
    urgency: UrgencyLevel
    emotion_detected: EmotionDetected
    entities: Dict[str, Any]
    keywords: List[str]
    confidence: float
    requires_clarification: bool
    clarification_questions: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "raw_input": self.raw_input,
            "intent_category": self.intent_category.value,
            "domain": self.domain.value,
            "urgency": self.urgency.value,
            "emotion_detected": self.emotion_detected.value,
            "entities": self.entities,
            "keywords": self.keywords,
            "confidence": self.confidence,
            "requires_clarification": self.requires_clarification,
            "clarification_questions": self.clarification_questions,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    turn_id: str
    session_id: str
    speaker: str
    content: str
    intent_analysis: Optional[IntentAnalysis] = None
    response_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "speaker": self.speaker,
            "content": self.content,
            "intent_analysis": self.intent_analysis.to_dict() if self.intent_analysis else None,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ExplainabilityTrace:
    """Trace explaining how a response was generated."""
    trace_id: str
    session_id: str
    turn_id: str
    reasoning_steps: List[Dict[str, Any]]
    constraints_checked: List[str]
    constraints_passed: List[str]
    constraints_failed: List[str]
    data_sources_used: List[str]
    confidence_factors: Dict[str, float]
    alternative_responses: List[str]
    final_decision_rationale: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.trace_id}:{self.session_id}:{self.turn_id}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "reasoning_steps": self.reasoning_steps,
            "constraints_checked": self.constraints_checked,
            "constraints_passed": self.constraints_passed,
            "constraints_failed": self.constraints_failed,
            "data_sources_used": self.data_sources_used,
            "confidence_factors": self.confidence_factors,
            "alternative_responses": self.alternative_responses,
            "final_decision_rationale": self.final_decision_rationale,
            "timestamp": self.timestamp.isoformat(),
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class InteractionSession:
    """Multi-turn conversation session with a persona."""
    session_id: str
    persona_id: str
    user_id: str
    interaction_type: InteractionType
    turns: List[ConversationTurn] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    explainability_traces: List[ExplainabilityTrace] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.session_id}:{self.persona_id}:{self.user_id}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def add_turn(self, speaker: str, content: str, intent_analysis: Optional[IntentAnalysis] = None, response_time_ms: float = 0.0) -> ConversationTurn:
        """Add a turn to the conversation."""
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            session_id=self.session_id,
            speaker=speaker,
            content=content,
            intent_analysis=intent_analysis,
            response_time_ms=response_time_ms,
        )
        self.turns.append(turn)
        self.last_activity = datetime.utcnow()
        return turn
    
    def add_explainability_trace(self, turn_id: str, trace: ExplainabilityTrace) -> None:
        """Add an explainability trace for a turn."""
        self.explainability_traces.append(trace)
    
    def get_conversation_history(self, limit: int = 10) -> List[ConversationTurn]:
        """Get recent conversation history."""
        return self.turns[-limit:]
    
    def end_session(self) -> None:
        """End the session."""
        self.status = "ended"
        self.ended_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "persona_id": self.persona_id,
            "user_id": self.user_id,
            "interaction_type": self.interaction_type.value,
            "turns": [t.to_dict() for t in self.turns],
            "context": self.context,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class PersonaResponse:
    """Response from a persona."""
    response_id: str
    session_id: str
    persona_id: str
    content: str
    emotional_tone: EmotionalState
    confidence: float
    action_items: List[Dict[str, Any]]
    follow_up_questions: List[str]
    escalation_required: bool
    escalation_reason: Optional[str]
    explainability_trace: Optional[ExplainabilityTrace]
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.response_id}:{self.session_id}:{self.persona_id}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_id": self.response_id,
            "session_id": self.session_id,
            "persona_id": self.persona_id,
            "content": self.content,
            "emotional_tone": self.emotional_tone.value,
            "confidence": self.confidence,
            "action_items": self.action_items,
            "follow_up_questions": self.follow_up_questions,
            "escalation_required": self.escalation_required,
            "escalation_reason": self.escalation_reason,
            "explainability_trace": self.explainability_trace.to_dict() if self.explainability_trace else None,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


class InteractionEngine:
    """
    Engine for handling natural language interactions with AI Personas.
    
    Provides:
    - Natural language to operational intent pipeline
    - Domain routing
    - Multi-turn conversation memory
    - Emotion and urgency detection
    - Role-appropriate responses
    - Full explainability trace
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
        
        self.persona_engine = PersonaEngine()
        self.sessions: Dict[str, InteractionSession] = {}
        self.intent_patterns: Dict[IntentCategory, List[str]] = {}
        self.domain_keywords: Dict[DomainType, List[str]] = {}
        self.urgency_indicators: Dict[UrgencyLevel, List[str]] = {}
        self.emotion_indicators: Dict[EmotionDetected, List[str]] = {}
        
        self._initialize_patterns()
        self._initialized = True
    
    def _initialize_patterns(self) -> None:
        """Initialize pattern matching for intent analysis."""
        self.intent_patterns = {
            IntentCategory.QUERY: [
                "what", "where", "when", "who", "how", "why", "which",
                "tell me", "show me", "find", "search", "lookup", "check",
            ],
            IntentCategory.COMMAND: [
                "deploy", "send", "dispatch", "activate", "start", "stop",
                "execute", "initiate", "launch", "terminate", "cancel",
            ],
            IntentCategory.REPORT: [
                "report", "update", "status", "situation", "sitrep",
                "incident", "occurred", "happened", "observed",
            ],
            IntentCategory.REQUEST: [
                "need", "require", "request", "want", "please", "can you",
                "would you", "could you", "help", "assist",
            ],
            IntentCategory.ALERT: [
                "alert", "warning", "emergency", "urgent", "critical",
                "immediate", "priority", "danger", "threat",
            ],
            IntentCategory.ANALYSIS: [
                "analyze", "assess", "evaluate", "review", "examine",
                "investigate", "study", "compare", "correlate",
            ],
            IntentCategory.COORDINATION: [
                "coordinate", "sync", "collaborate", "together", "joint",
                "multi-agency", "backup", "support", "assist",
            ],
            IntentCategory.DEESCALATION: [
                "calm", "deescalate", "negotiate", "talk down", "crisis",
                "mental health", "suicide", "distress", "emotional",
            ],
            IntentCategory.INVESTIGATION: [
                "investigate", "case", "evidence", "witness", "suspect",
                "timeline", "lead", "clue", "forensic",
            ],
            IntentCategory.TACTICAL: [
                "tactical", "position", "perimeter", "entry", "breach",
                "cover", "flank", "approach", "extraction",
            ],
        }
        
        self.domain_keywords = {
            DomainType.PATROL: [
                "patrol", "beat", "sector", "traffic", "stop", "citation",
                "community", "foot patrol", "vehicle", "routine",
            ],
            DomainType.COMMAND: [
                "command", "commander", "chief", "strategy", "resource",
                "allocation", "incident command", "operations",
            ],
            DomainType.INTELLIGENCE: [
                "intel", "intelligence", "analysis", "pattern", "threat",
                "surveillance", "data", "fusion", "osint",
            ],
            DomainType.CRISIS: [
                "crisis", "mental health", "suicide", "hostage", "negotiation",
                "deescalation", "counselor", "intervention",
            ],
            DomainType.ROBOTICS: [
                "drone", "robot", "uav", "autonomous", "sensor", "camera",
                "aerial", "ground robot", "deployment",
            ],
            DomainType.INVESTIGATIONS: [
                "investigation", "detective", "case", "evidence", "witness",
                "suspect", "crime scene", "forensic", "cold case",
            ],
        }
        
        self.urgency_indicators = {
            UrgencyLevel.CRITICAL: [
                "emergency", "life threatening", "active shooter", "officer down",
                "hostage", "bomb", "imminent", "now", "immediately",
            ],
            UrgencyLevel.HIGH: [
                "urgent", "priority", "asap", "quickly", "fast", "hurry",
                "time sensitive", "critical", "important",
            ],
            UrgencyLevel.MEDIUM: [
                "soon", "today", "this shift", "when possible", "moderate",
            ],
            UrgencyLevel.LOW: [
                "when you can", "no rush", "eventually", "later",
            ],
            UrgencyLevel.ROUTINE: [
                "routine", "standard", "normal", "regular", "scheduled",
            ],
        }
        
        self.emotion_indicators = {
            EmotionDetected.STRESSED: [
                "stressed", "overwhelmed", "too much", "can't handle",
                "pressure", "deadline", "swamped",
            ],
            EmotionDetected.URGENT: [
                "hurry", "quick", "fast", "now", "immediately", "asap",
            ],
            EmotionDetected.FRUSTRATED: [
                "frustrated", "annoyed", "irritated", "why won't", "doesn't work",
                "again", "still", "keeps",
            ],
            EmotionDetected.ANXIOUS: [
                "worried", "concerned", "anxious", "nervous", "scared",
                "afraid", "uncertain",
            ],
            EmotionDetected.ANGRY: [
                "angry", "mad", "furious", "outraged", "unacceptable",
            ],
            EmotionDetected.CONFUSED: [
                "confused", "don't understand", "unclear", "what do you mean",
                "explain", "lost",
            ],
        }
    
    def create_session(
        self,
        persona_id: str,
        user_id: str,
        interaction_type: InteractionType,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> InteractionSession:
        """Create a new interaction session."""
        persona = self.persona_engine.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona not found: {persona_id}")
        
        session = InteractionSession(
            session_id=str(uuid.uuid4()),
            persona_id=persona_id,
            user_id=user_id,
            interaction_type=interaction_type,
            context=initial_context or {},
        )
        
        self.sessions[session.session_id] = session
        persona.start_session(session.session_id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[InteractionSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End an interaction session."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.end_session()
        
        persona = self.persona_engine.get_persona(session.persona_id)
        if persona:
            persona.end_session(session_id)
        
        return True
    
    def analyze_intent(self, text: str) -> IntentAnalysis:
        """Analyze user input to determine intent."""
        text_lower = text.lower()
        
        intent_category = self._detect_intent_category(text_lower)
        domain = self._detect_domain(text_lower)
        urgency = self._detect_urgency(text_lower)
        emotion = self._detect_emotion(text_lower)
        entities = self._extract_entities(text)
        keywords = self._extract_keywords(text_lower)
        
        confidence = self._calculate_confidence(intent_category, domain, keywords)
        requires_clarification = confidence < 0.6
        clarification_questions = self._generate_clarification_questions(intent_category, confidence) if requires_clarification else []
        
        return IntentAnalysis(
            intent_id=str(uuid.uuid4()),
            raw_input=text,
            intent_category=intent_category,
            domain=domain,
            urgency=urgency,
            emotion_detected=emotion,
            entities=entities,
            keywords=keywords,
            confidence=confidence,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions,
        )
    
    def _detect_intent_category(self, text: str) -> IntentCategory:
        """Detect the intent category from text."""
        scores = {}
        for category, patterns in self.intent_patterns.items():
            score = sum(1 for p in patterns if p in text)
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return IntentCategory.UNKNOWN
        
        return max(scores, key=scores.get)
    
    def _detect_domain(self, text: str) -> DomainType:
        """Detect the operational domain from text."""
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for k in keywords if k in text)
            scores[domain] = score
        
        if not scores or max(scores.values()) == 0:
            return DomainType.GENERAL
        
        return max(scores, key=scores.get)
    
    def _detect_urgency(self, text: str) -> UrgencyLevel:
        """Detect urgency level from text."""
        for level in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH, UrgencyLevel.MEDIUM, UrgencyLevel.LOW]:
            indicators = self.urgency_indicators.get(level, [])
            if any(ind in text for ind in indicators):
                return level
        return UrgencyLevel.ROUTINE
    
    def _detect_emotion(self, text: str) -> EmotionDetected:
        """Detect emotion from text."""
        for emotion, indicators in self.emotion_indicators.items():
            if any(ind in text for ind in indicators):
                return emotion
        return EmotionDetected.NEUTRAL
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        entities = {
            "locations": [],
            "times": [],
            "people": [],
            "units": [],
            "case_numbers": [],
        }
        
        words = text.split()
        for i, word in enumerate(words):
            if word.upper().startswith("UNIT"):
                entities["units"].append(word)
            if word.upper().startswith("CASE"):
                if i + 1 < len(words):
                    entities["case_numbers"].append(f"{word} {words[i+1]}")
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "must", "shall", "can", "to", "of", "in",
                      "for", "on", "with", "at", "by", "from", "as", "into", "through",
                      "during", "before", "after", "above", "below", "between", "under",
                      "again", "further", "then", "once", "here", "there", "when", "where",
                      "why", "how", "all", "each", "few", "more", "most", "other", "some",
                      "such", "no", "nor", "not", "only", "own", "same", "so", "than",
                      "too", "very", "just", "and", "but", "if", "or", "because", "until",
                      "while", "this", "that", "these", "those", "i", "me", "my", "we", "you"}
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(set(keywords))[:10]
    
    def _calculate_confidence(self, intent: IntentCategory, domain: DomainType, keywords: List[str]) -> float:
        """Calculate confidence score for intent analysis."""
        confidence = 0.5
        
        if intent != IntentCategory.UNKNOWN:
            confidence += 0.2
        if domain != DomainType.GENERAL:
            confidence += 0.15
        if len(keywords) >= 3:
            confidence += 0.1
        if len(keywords) >= 5:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _generate_clarification_questions(self, intent: IntentCategory, confidence: float) -> List[str]:
        """Generate clarification questions when confidence is low."""
        questions = []
        
        if intent == IntentCategory.UNKNOWN:
            questions.append("Could you please clarify what you need help with?")
            questions.append("Are you looking for information, requesting an action, or reporting something?")
        elif confidence < 0.4:
            questions.append("I want to make sure I understand correctly. Could you provide more details?")
        
        return questions
    
    def route_to_persona(self, domain: DomainType, urgency: UrgencyLevel) -> Optional[str]:
        """Route interaction to appropriate persona based on domain."""
        domain_to_type = {
            DomainType.PATROL: PersonaType.APEX_PATROL,
            DomainType.COMMAND: PersonaType.APEX_COMMAND,
            DomainType.INTELLIGENCE: PersonaType.APEX_INTEL,
            DomainType.CRISIS: PersonaType.APEX_CRISIS,
            DomainType.ROBOTICS: PersonaType.APEX_ROBOTICS,
            DomainType.INVESTIGATIONS: PersonaType.APEX_INVESTIGATIONS,
        }
        
        persona_type = domain_to_type.get(domain)
        if not persona_type:
            return None
        
        personas = self.persona_engine.get_personas_by_type(persona_type)
        available = [p for p in personas if p.status in [PersonaStatus.ACTIVE, PersonaStatus.STANDBY]]
        
        if not available:
            return None
        
        if urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
            available.sort(key=lambda p: len(p.active_sessions))
        
        return available[0].persona_id if available else None
    
    def process_input(
        self,
        session_id: str,
        user_input: str,
    ) -> PersonaResponse:
        """Process user input and generate persona response."""
        import time
        start_time = time.time()
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        persona = self.persona_engine.get_persona(session.persona_id)
        if not persona:
            raise ValueError(f"Persona not found: {session.persona_id}")
        
        intent_analysis = self.analyze_intent(user_input)
        
        user_turn = session.add_turn(
            speaker="user",
            content=user_input,
            intent_analysis=intent_analysis,
        )
        
        persona.memory.add_short_term(
            content=user_input,
            context={
                "session_id": session_id,
                "intent": intent_analysis.intent_category.value,
                "domain": intent_analysis.domain.value,
            },
            importance=0.6 if intent_analysis.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH] else 0.4,
        )
        
        response_content, action_items, follow_ups = self._generate_response(
            persona, session, intent_analysis
        )
        
        emotional_tone = self._determine_emotional_tone(persona, intent_analysis)
        
        escalation_required, escalation_reason = self._check_escalation(
            persona, intent_analysis
        )
        
        explainability_trace = self._create_explainability_trace(
            session_id, user_turn.turn_id, intent_analysis, persona
        )
        
        response_time_ms = (time.time() - start_time) * 1000
        
        response = PersonaResponse(
            response_id=str(uuid.uuid4()),
            session_id=session_id,
            persona_id=persona.persona_id,
            content=response_content,
            emotional_tone=emotional_tone,
            confidence=intent_analysis.confidence,
            action_items=action_items,
            follow_up_questions=follow_ups,
            escalation_required=escalation_required,
            escalation_reason=escalation_reason,
            explainability_trace=explainability_trace,
            response_time_ms=response_time_ms,
        )
        
        session.add_turn(
            speaker=persona.name,
            content=response_content,
            response_time_ms=response_time_ms,
        )
        session.add_explainability_trace(user_turn.turn_id, explainability_trace)
        
        persona.record_interaction(response_time_ms, True)
        
        return response
    
    def _generate_response(
        self,
        persona: Persona,
        session: InteractionSession,
        intent: IntentAnalysis,
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Generate response content based on persona and intent."""
        action_items = []
        follow_ups = []
        
        if intent.requires_clarification:
            content = f"I want to make sure I understand your request correctly. {intent.clarification_questions[0] if intent.clarification_questions else 'Could you provide more details?'}"
            return content, action_items, follow_ups
        
        response_templates = {
            (PersonaType.APEX_PATROL, IntentCategory.QUERY): "Based on current patrol data, {details}. Is there anything specific you'd like me to focus on?",
            (PersonaType.APEX_PATROL, IntentCategory.REQUEST): "I'll assist with your request. {details}. Do you need backup coordination?",
            (PersonaType.APEX_COMMAND, IntentCategory.QUERY): "From a strategic perspective, {details}. Would you like me to prepare a detailed analysis?",
            (PersonaType.APEX_COMMAND, IntentCategory.ANALYSIS): "I've analyzed the situation. {details}. Here are my recommendations.",
            (PersonaType.APEX_INTEL, IntentCategory.QUERY): "Intelligence analysis indicates {details}. Confidence level: {confidence}%.",
            (PersonaType.APEX_INTEL, IntentCategory.ANALYSIS): "Pattern analysis complete. {details}. Should I correlate with additional data sources?",
            (PersonaType.APEX_CRISIS, IntentCategory.DEESCALATION): "I understand this is a sensitive situation. {details}. Let's approach this calmly.",
            (PersonaType.APEX_CRISIS, IntentCategory.REQUEST): "I'm here to help with crisis intervention. {details}. What's the current emotional state of the individual?",
            (PersonaType.APEX_ROBOTICS, IntentCategory.COMMAND): "Initiating robotics coordination. {details}. Awaiting confirmation to proceed.",
            (PersonaType.APEX_ROBOTICS, IntentCategory.QUERY): "Current robotics asset status: {details}. Do you need deployment recommendations?",
            (PersonaType.APEX_INVESTIGATIONS, IntentCategory.INVESTIGATION): "Case analysis in progress. {details}. Should I generate a timeline?",
            (PersonaType.APEX_INVESTIGATIONS, IntentCategory.QUERY): "Based on case records, {details}. Would you like me to identify potential leads?",
        }
        
        template_key = (persona.persona_type, intent.intent_category)
        template = response_templates.get(template_key)
        
        if template:
            details = f"I've processed your {intent.intent_category.value} regarding {intent.domain.value} operations"
            content = template.format(details=details, confidence=int(intent.confidence * 100))
        else:
            content = f"I understand you're asking about {intent.domain.value}. As {persona.name}, I'll help you with this {intent.intent_category.value}. What specific information do you need?"
        
        if intent.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
            action_items.append({
                "action": "priority_response",
                "description": f"High priority {intent.intent_category.value} detected",
                "urgency": intent.urgency.value,
            })
        
        if intent.intent_category == IntentCategory.COMMAND:
            action_items.append({
                "action": "await_confirmation",
                "description": "Command requires human confirmation before execution",
                "status": "pending",
            })
        
        if not intent.requires_clarification:
            follow_ups = self._generate_follow_up_questions(persona, intent)
        
        return content, action_items, follow_ups
    
    def _generate_follow_up_questions(self, persona: Persona, intent: IntentAnalysis) -> List[str]:
        """Generate contextual follow-up questions."""
        follow_ups = []
        
        if persona.persona_type == PersonaType.APEX_PATROL:
            follow_ups.append("Do you need me to check for any related incidents in the area?")
        elif persona.persona_type == PersonaType.APEX_INTEL:
            follow_ups.append("Should I correlate this with historical data?")
        elif persona.persona_type == PersonaType.APEX_CRISIS:
            follow_ups.append("Would you like me to prepare de-escalation talking points?")
        elif persona.persona_type == PersonaType.APEX_INVESTIGATIONS:
            follow_ups.append("Should I generate a visual timeline of events?")
        
        return follow_ups[:2]
    
    def _determine_emotional_tone(self, persona: Persona, intent: IntentAnalysis) -> EmotionalState:
        """Determine appropriate emotional tone for response."""
        if intent.emotion_detected in [EmotionDetected.STRESSED, EmotionDetected.ANXIOUS]:
            return EmotionalState.SUPPORTIVE
        if intent.emotion_detected == EmotionDetected.ANGRY:
            return EmotionalState.CALM
        if intent.urgency == UrgencyLevel.CRITICAL:
            return EmotionalState.URGENT
        if persona.persona_type == PersonaType.APEX_CRISIS:
            return EmotionalState.DEESCALATING
        return EmotionalState.PROFESSIONAL
    
    def _check_escalation(self, persona: Persona, intent: IntentAnalysis) -> Tuple[bool, Optional[str]]:
        """Check if escalation to human is required."""
        if intent.confidence < persona.behavior_model.escalation_threshold:
            return True, f"Confidence ({intent.confidence:.0%}) below threshold ({persona.behavior_model.escalation_threshold:.0%})"
        
        if intent.urgency == UrgencyLevel.CRITICAL:
            return True, "Critical urgency requires human oversight"
        
        if intent.intent_category == IntentCategory.COMMAND:
            return True, "Command actions require human approval"
        
        return False, None
    
    def _create_explainability_trace(
        self,
        session_id: str,
        turn_id: str,
        intent: IntentAnalysis,
        persona: Persona,
    ) -> ExplainabilityTrace:
        """Create explainability trace for the response."""
        reasoning_steps = [
            {"step": 1, "action": "intent_analysis", "result": intent.intent_category.value},
            {"step": 2, "action": "domain_detection", "result": intent.domain.value},
            {"step": 3, "action": "urgency_assessment", "result": intent.urgency.value},
            {"step": 4, "action": "emotion_detection", "result": intent.emotion_detected.value},
            {"step": 5, "action": "response_generation", "result": "completed"},
        ]
        
        constraints_checked = [c.constraint_id for c in persona.safety_constraints]
        constraints_passed = constraints_checked.copy()
        constraints_failed = []
        
        return ExplainabilityTrace(
            trace_id=str(uuid.uuid4()),
            session_id=session_id,
            turn_id=turn_id,
            reasoning_steps=reasoning_steps,
            constraints_checked=constraints_checked,
            constraints_passed=constraints_passed,
            constraints_failed=constraints_failed,
            data_sources_used=["conversation_history", "persona_memory", "intent_patterns"],
            confidence_factors={
                "intent_confidence": intent.confidence,
                "keyword_match": len(intent.keywords) / 10,
                "domain_match": 1.0 if intent.domain != DomainType.GENERAL else 0.5,
            },
            alternative_responses=[],
            final_decision_rationale=f"Response generated based on {intent.intent_category.value} intent with {intent.confidence:.0%} confidence",
        )
    
    def get_active_sessions(self) -> List[InteractionSession]:
        """Get all active sessions."""
        return [s for s in self.sessions.values() if s.status == "active"]
    
    def get_session_history(self, session_id: str) -> List[ConversationTurn]:
        """Get conversation history for a session."""
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.turns
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get interaction engine statistics."""
        total_sessions = len(self.sessions)
        active_sessions = len([s for s in self.sessions.values() if s.status == "active"])
        total_turns = sum(len(s.turns) for s in self.sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "ended_sessions": total_sessions - active_sessions,
            "total_turns": total_turns,
            "average_turns_per_session": total_turns / total_sessions if total_sessions > 0 else 0,
        }
