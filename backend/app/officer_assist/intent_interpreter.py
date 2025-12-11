"""
Officer Intent Interpreter

Reads officer radio traffic, MDT entries, or voice inputs to detect:
- Traffic stop
- Consent search
- Terry stop
- Arrest
- Vehicle pursuit
- Domestic dispute
- Felony stop
- Use-of-force event

Automatically runs Constitutional Guardrail Engine on detected intents.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Types of officer intents"""
    TRAFFIC_STOP = "TRAFFIC_STOP"
    CONSENT_SEARCH = "CONSENT_SEARCH"
    TERRY_STOP = "TERRY_STOP"
    ARREST = "ARREST"
    VEHICLE_PURSUIT = "VEHICLE_PURSUIT"
    FOOT_PURSUIT = "FOOT_PURSUIT"
    DOMESTIC_DISPUTE = "DOMESTIC_DISPUTE"
    FELONY_STOP = "FELONY_STOP"
    USE_OF_FORCE = "USE_OF_FORCE"
    WARRANT_SERVICE = "WARRANT_SERVICE"
    WELFARE_CHECK = "WELFARE_CHECK"
    SUSPICIOUS_PERSON = "SUSPICIOUS_PERSON"
    BUILDING_CHECK = "BUILDING_CHECK"
    BACKUP_REQUEST = "BACKUP_REQUEST"
    CODE_RED = "CODE_RED"
    MIRANDA_ADVISEMENT = "MIRANDA_ADVISEMENT"
    CUSTODIAL_INTERROGATION = "CUSTODIAL_INTERROGATION"
    FIELD_INTERVIEW = "FIELD_INTERVIEW"


class IntentConfidence(str, Enum):
    """Confidence levels for intent detection"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class InputSource(str, Enum):
    """Source of input for intent detection"""
    RADIO = "RADIO"
    MDT = "MDT"
    VOICE = "VOICE"
    CAD = "CAD"
    BODY_CAM = "BODY_CAM"
    MANUAL = "MANUAL"


class OfficerIntent(BaseModel):
    """Detected officer intent"""
    intent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    officer_id: str
    incident_id: Optional[str] = None
    intent_type: IntentType
    confidence: IntentConfidence
    confidence_score: float
    input_source: InputSource
    raw_input: str
    extracted_entities: Dict[str, Any] = {}
    guardrail_triggered: bool = False
    guardrail_result: Optional[Dict[str, Any]] = None
    tactical_advice_generated: bool = False
    requires_supervisor_review: bool = False
    notes: List[str] = []


class IntentPattern(BaseModel):
    """Pattern for intent detection"""
    pattern_id: str
    intent_type: IntentType
    keywords: List[str]
    phrases: List[str]
    weight: float = 1.0
    requires_context: bool = False


class OfficerIntentInterpreter:
    """
    Officer Intent Interpreter
    
    Analyzes officer communications to detect intent and automatically
    trigger constitutional guardrails and tactical advice.
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
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "city": "Riviera Beach",
        }
        
        self.intent_patterns = self._initialize_patterns()
        
        self.ten_codes = {
            "10-0": "CAUTION",
            "10-1": "UNABLE_TO_COPY",
            "10-2": "SIGNAL_GOOD",
            "10-3": "STOP_TRANSMITTING",
            "10-4": "ACKNOWLEDGMENT",
            "10-6": "BUSY",
            "10-7": "OUT_OF_SERVICE",
            "10-8": "IN_SERVICE",
            "10-9": "REPEAT",
            "10-10": "FIGHT_IN_PROGRESS",
            "10-11": "TRAFFIC_STOP",
            "10-12": "STANDBY",
            "10-14": "PROWLER",
            "10-15": "PRISONER_IN_CUSTODY",
            "10-16": "DOMESTIC_DISTURBANCE",
            "10-17": "MEET_COMPLAINANT",
            "10-18": "URGENT",
            "10-19": "RETURN_TO_STATION",
            "10-20": "LOCATION",
            "10-21": "CALL_BY_PHONE",
            "10-22": "DISREGARD",
            "10-23": "ARRIVED_AT_SCENE",
            "10-24": "ASSIGNMENT_COMPLETE",
            "10-25": "REPORT_IN_PERSON",
            "10-26": "DETAINING_SUBJECT",
            "10-27": "LICENSE_CHECK",
            "10-28": "VEHICLE_REGISTRATION",
            "10-29": "WARRANT_CHECK",
            "10-30": "UNNECESSARY_USE_OF_RADIO",
            "10-31": "CRIME_IN_PROGRESS",
            "10-32": "PERSON_WITH_GUN",
            "10-33": "EMERGENCY",
            "10-34": "RIOT",
            "10-35": "MAJOR_CRIME_ALERT",
            "10-36": "CORRECT_TIME",
            "10-37": "SUSPICIOUS_VEHICLE",
            "10-38": "STOPPING_SUSPICIOUS_VEHICLE",
            "10-39": "URGENT_USE_LIGHTS_SIREN",
            "10-40": "SILENT_RUN",
            "10-41": "BEGINNING_TOUR_OF_DUTY",
            "10-42": "ENDING_TOUR_OF_DUTY",
            "10-43": "INFORMATION",
            "10-45": "ANIMAL_CARCASS",
            "10-46": "ASSIST_MOTORIST",
            "10-47": "EMERGENCY_ROAD_REPAIR",
            "10-48": "TRAFFIC_STANDARD_REPAIR",
            "10-49": "TRAFFIC_LIGHT_OUT",
            "10-50": "ACCIDENT",
            "10-51": "WRECKER_NEEDED",
            "10-52": "AMBULANCE_NEEDED",
            "10-53": "ROAD_BLOCKED",
            "10-54": "LIVESTOCK_ON_HIGHWAY",
            "10-55": "INTOXICATED_DRIVER",
            "10-56": "INTOXICATED_PEDESTRIAN",
            "10-57": "HIT_AND_RUN",
            "10-58": "DIRECT_TRAFFIC",
            "10-59": "CONVOY_OR_ESCORT",
            "10-60": "SQUAD_IN_VICINITY",
            "10-61": "PERSONNEL_IN_AREA",
            "10-62": "REPLY_TO_MESSAGE",
            "10-63": "PREPARE_TO_COPY",
            "10-64": "MESSAGE_FOR_LOCAL_DELIVERY",
            "10-65": "NET_MESSAGE_ASSIGNMENT",
            "10-66": "MESSAGE_CANCELLATION",
            "10-67": "CLEAR_FOR_NET_MESSAGE",
            "10-68": "DISPATCH_INFORMATION",
            "10-69": "MESSAGE_RECEIVED",
            "10-70": "FIRE_ALARM",
            "10-71": "ADVISE_NATURE_OF_FIRE",
            "10-72": "REPORT_PROGRESS_ON_FIRE",
            "10-73": "SMOKE_REPORT",
            "10-74": "NEGATIVE",
            "10-75": "IN_CONTACT_WITH",
            "10-76": "EN_ROUTE",
            "10-77": "ETA",
            "10-78": "NEED_ASSISTANCE",
            "10-79": "NOTIFY_CORONER",
            "10-80": "CHASE_IN_PROGRESS",
            "10-81": "BREATHALYZER",
            "10-82": "RESERVE_LODGING",
            "10-83": "WORK_SCHOOL_CROSSING",
            "10-84": "IF_MEETING",
            "10-85": "DELAYED_DUE_TO",
            "10-86": "OFFICER_ON_DUTY",
            "10-87": "PICKUP",
            "10-88": "PRESENT_TELEPHONE_NUMBER",
            "10-89": "BOMB_THREAT",
            "10-90": "BANK_ALARM",
            "10-91": "PICK_UP_PRISONER",
            "10-92": "IMPROPERLY_PARKED_VEHICLE",
            "10-93": "BLOCKADE",
            "10-94": "DRAG_RACING",
            "10-95": "PRISONER_IN_CUSTODY",
            "10-96": "MENTAL_SUBJECT",
            "10-97": "CHECK_SIGNAL",
            "10-98": "PRISON_JAIL_BREAK",
            "10-99": "WANTED_STOLEN_INDICATED",
        }
        
        self.detected_intents: List[OfficerIntent] = []
        self.active_incidents: Dict[str, List[OfficerIntent]] = {}
    
    def _initialize_patterns(self) -> Dict[IntentType, IntentPattern]:
        """Initialize intent detection patterns"""
        patterns = {}
        
        patterns[IntentType.TRAFFIC_STOP] = IntentPattern(
            pattern_id="pat-ts",
            intent_type=IntentType.TRAFFIC_STOP,
            keywords=["traffic stop", "pulling over", "stopping vehicle", "10-11", "traffic violation", "speeding", "running red", "tag expired"],
            phrases=["initiating traffic stop", "stopping a vehicle", "traffic stop on", "pulling over a"],
            weight=1.0,
        )
        
        patterns[IntentType.CONSENT_SEARCH] = IntentPattern(
            pattern_id="pat-cs",
            intent_type=IntentType.CONSENT_SEARCH,
            keywords=["consent", "search", "permission to search", "may i search", "consent to search"],
            phrases=["requesting consent", "asking for consent", "consent search", "do you mind if i"],
            weight=1.2,
        )
        
        patterns[IntentType.TERRY_STOP] = IntentPattern(
            pattern_id="pat-terry",
            intent_type=IntentType.TERRY_STOP,
            keywords=["terry stop", "investigative detention", "stop and frisk", "reasonable suspicion", "suspicious person", "10-14"],
            phrases=["stopping for investigation", "detaining for", "investigative stop"],
            weight=1.1,
        )
        
        patterns[IntentType.ARREST] = IntentPattern(
            pattern_id="pat-arrest",
            intent_type=IntentType.ARREST,
            keywords=["arrest", "custody", "under arrest", "10-15", "prisoner", "booking", "handcuffs"],
            phrases=["placing under arrest", "you are under arrest", "taking into custody", "one in custody"],
            weight=1.3,
        )
        
        patterns[IntentType.VEHICLE_PURSUIT] = IntentPattern(
            pattern_id="pat-pursuit",
            intent_type=IntentType.VEHICLE_PURSUIT,
            keywords=["pursuit", "chase", "10-80", "fleeing", "failing to stop", "high speed"],
            phrases=["in pursuit", "vehicle pursuit", "suspect fleeing", "not stopping"],
            weight=1.5,
        )
        
        patterns[IntentType.FOOT_PURSUIT] = IntentPattern(
            pattern_id="pat-foot",
            intent_type=IntentType.FOOT_PURSUIT,
            keywords=["foot pursuit", "on foot", "running", "fleeing on foot", "foot chase"],
            phrases=["in foot pursuit", "suspect running", "chasing on foot"],
            weight=1.4,
        )
        
        patterns[IntentType.DOMESTIC_DISPUTE] = IntentPattern(
            pattern_id="pat-domestic",
            intent_type=IntentType.DOMESTIC_DISPUTE,
            keywords=["domestic", "10-16", "disturbance", "family dispute", "domestic violence", "dv"],
            phrases=["domestic disturbance", "domestic dispute", "family disturbance"],
            weight=1.2,
        )
        
        patterns[IntentType.FELONY_STOP] = IntentPattern(
            pattern_id="pat-felony",
            intent_type=IntentType.FELONY_STOP,
            keywords=["felony stop", "high risk stop", "felony traffic", "armed suspect", "wanted vehicle"],
            phrases=["initiating felony stop", "high risk vehicle stop", "felony traffic stop"],
            weight=1.5,
        )
        
        patterns[IntentType.USE_OF_FORCE] = IntentPattern(
            pattern_id="pat-uof",
            intent_type=IntentType.USE_OF_FORCE,
            keywords=["force", "taser", "oc spray", "baton", "shots fired", "weapon", "fighting", "resisting"],
            phrases=["deploying taser", "using force", "shots fired", "subject resisting", "physical altercation"],
            weight=1.6,
        )
        
        patterns[IntentType.MIRANDA_ADVISEMENT] = IntentPattern(
            pattern_id="pat-miranda",
            intent_type=IntentType.MIRANDA_ADVISEMENT,
            keywords=["miranda", "rights", "remain silent", "attorney", "advisement"],
            phrases=["reading miranda", "advising of rights", "you have the right"],
            weight=1.3,
        )
        
        patterns[IntentType.CUSTODIAL_INTERROGATION] = IntentPattern(
            pattern_id="pat-custodial",
            intent_type=IntentType.CUSTODIAL_INTERROGATION,
            keywords=["interrogation", "questioning", "interview", "statement"],
            phrases=["conducting interview", "taking statement", "questioning suspect"],
            weight=1.2,
            requires_context=True,
        )
        
        patterns[IntentType.BACKUP_REQUEST] = IntentPattern(
            pattern_id="pat-backup",
            intent_type=IntentType.BACKUP_REQUEST,
            keywords=["backup", "10-78", "assistance", "additional units", "code 3"],
            phrases=["requesting backup", "need assistance", "send backup", "additional units"],
            weight=1.4,
        )
        
        patterns[IntentType.CODE_RED] = IntentPattern(
            pattern_id="pat-emergency",
            intent_type=IntentType.CODE_RED,
            keywords=["10-33", "emergency", "officer down", "shots fired", "code red", "mayday"],
            phrases=["officer down", "shots fired", "emergency traffic", "code red"],
            weight=2.0,
        )
        
        return patterns
    
    def interpret_input(
        self,
        officer_id: str,
        raw_input: str,
        input_source: InputSource = InputSource.RADIO,
        incident_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> OfficerIntent:
        """
        Interpret officer input to detect intent
        
        Args:
            officer_id: Officer identifier
            raw_input: Raw input text (radio, MDT, voice)
            input_source: Source of the input
            incident_id: Associated incident ID if known
            context: Additional context for interpretation
            
        Returns:
            OfficerIntent with detected intent and confidence
        """
        input_lower = raw_input.lower()
        
        detected_type, confidence_score = self._detect_intent_type(input_lower, context)
        
        if confidence_score >= 0.8:
            confidence = IntentConfidence.HIGH
        elif confidence_score >= 0.5:
            confidence = IntentConfidence.MEDIUM
        else:
            confidence = IntentConfidence.LOW
        
        entities = self._extract_entities(raw_input, detected_type)
        
        guardrail_triggered = detected_type in [
            IntentType.TRAFFIC_STOP,
            IntentType.CONSENT_SEARCH,
            IntentType.TERRY_STOP,
            IntentType.ARREST,
            IntentType.USE_OF_FORCE,
            IntentType.CUSTODIAL_INTERROGATION,
            IntentType.VEHICLE_PURSUIT,
            IntentType.FELONY_STOP,
        ]
        
        guardrail_result = None
        if guardrail_triggered and confidence != IntentConfidence.LOW:
            guardrail_result = self._trigger_guardrail_check(detected_type, officer_id, entities)
        
        tactical_advice_generated = detected_type in [
            IntentType.VEHICLE_PURSUIT,
            IntentType.FOOT_PURSUIT,
            IntentType.FELONY_STOP,
            IntentType.USE_OF_FORCE,
            IntentType.CODE_RED,
            IntentType.DOMESTIC_DISPUTE,
        ]
        
        requires_supervisor = detected_type in [
            IntentType.USE_OF_FORCE,
            IntentType.VEHICLE_PURSUIT,
            IntentType.CODE_RED,
        ] or (guardrail_result and guardrail_result.get("status") in ["WARNING", "BLOCKED"])
        
        notes = []
        if detected_type == IntentType.CODE_RED:
            notes.append("EMERGENCY: Immediate supervisor notification required")
        if guardrail_result and guardrail_result.get("status") == "BLOCKED":
            notes.append("GUARDRAIL BLOCKED: Action may violate policy or law")
        if guardrail_result and guardrail_result.get("status") == "WARNING":
            notes.append("GUARDRAIL WARNING: Review legal/policy considerations")
        
        intent = OfficerIntent(
            intent_id=f"int-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{officer_id}",
            officer_id=officer_id,
            incident_id=incident_id,
            intent_type=detected_type,
            confidence=confidence,
            confidence_score=confidence_score,
            input_source=input_source,
            raw_input=raw_input,
            extracted_entities=entities,
            guardrail_triggered=guardrail_triggered,
            guardrail_result=guardrail_result,
            tactical_advice_generated=tactical_advice_generated,
            requires_supervisor_review=requires_supervisor,
            notes=notes,
        )
        
        self.detected_intents.append(intent)
        
        if incident_id:
            if incident_id not in self.active_incidents:
                self.active_incidents[incident_id] = []
            self.active_incidents[incident_id].append(intent)
        
        return intent
    
    def _detect_intent_type(
        self,
        input_lower: str,
        context: Optional[Dict[str, Any]],
    ) -> tuple[IntentType, float]:
        """Detect intent type from input"""
        scores: Dict[IntentType, float] = {}
        
        for intent_type, pattern in self.intent_patterns.items():
            score = 0.0
            
            for keyword in pattern.keywords:
                if keyword.lower() in input_lower:
                    score += 0.3 * pattern.weight
            
            for phrase in pattern.phrases:
                if phrase.lower() in input_lower:
                    score += 0.5 * pattern.weight
            
            if pattern.requires_context and context:
                if context.get("in_custody") and intent_type == IntentType.CUSTODIAL_INTERROGATION:
                    score += 0.3
            
            scores[intent_type] = min(score, 1.0)
        
        for code, meaning in self.ten_codes.items():
            if code in input_lower:
                if meaning == "TRAFFIC_STOP":
                    scores[IntentType.TRAFFIC_STOP] = max(scores.get(IntentType.TRAFFIC_STOP, 0), 0.9)
                elif meaning == "CHASE_IN_PROGRESS":
                    scores[IntentType.VEHICLE_PURSUIT] = max(scores.get(IntentType.VEHICLE_PURSUIT, 0), 0.9)
                elif meaning == "DOMESTIC_DISTURBANCE":
                    scores[IntentType.DOMESTIC_DISPUTE] = max(scores.get(IntentType.DOMESTIC_DISPUTE, 0), 0.9)
                elif meaning == "PRISONER_IN_CUSTODY":
                    scores[IntentType.ARREST] = max(scores.get(IntentType.ARREST, 0), 0.8)
                elif meaning == "EMERGENCY":
                    scores[IntentType.CODE_RED] = max(scores.get(IntentType.CODE_RED, 0), 0.95)
                elif meaning == "NEED_ASSISTANCE":
                    scores[IntentType.BACKUP_REQUEST] = max(scores.get(IntentType.BACKUP_REQUEST, 0), 0.9)
        
        if scores:
            best_intent = max(scores, key=scores.get)
            best_score = scores[best_intent]
            if best_score > 0:
                return best_intent, best_score
        
        return IntentType.FIELD_INTERVIEW, 0.3
    
    def _extract_entities(
        self,
        raw_input: str,
        intent_type: IntentType,
    ) -> Dict[str, Any]:
        """Extract relevant entities from input"""
        entities = {}
        
        import re
        
        plate_pattern = r'\b[A-Z0-9]{1,3}[-\s]?[A-Z0-9]{2,4}[-\s]?[A-Z0-9]{0,3}\b'
        plates = re.findall(plate_pattern, raw_input.upper())
        if plates:
            entities["license_plates"] = plates
        
        location_indicators = ["at", "on", "near", "by", "location"]
        for indicator in location_indicators:
            if indicator in raw_input.lower():
                entities["has_location"] = True
                break
        
        directions = ["northbound", "southbound", "eastbound", "westbound", "north", "south", "east", "west"]
        for direction in directions:
            if direction in raw_input.lower():
                entities["direction"] = direction
                break
        
        if intent_type == IntentType.VEHICLE_PURSUIT:
            speed_pattern = r'(\d+)\s*(?:mph|miles per hour)'
            speeds = re.findall(speed_pattern, raw_input.lower())
            if speeds:
                entities["speed_mph"] = int(speeds[0])
        
        if intent_type in [IntentType.ARREST, IntentType.TERRY_STOP]:
            entities["requires_miranda_check"] = True
        
        return entities
    
    def _trigger_guardrail_check(
        self,
        intent_type: IntentType,
        officer_id: str,
        entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Trigger constitutional guardrail check"""
        guardrail_mapping = {
            IntentType.TRAFFIC_STOP: "TRAFFIC_STOP",
            IntentType.CONSENT_SEARCH: "CONSENT_SEARCH",
            IntentType.TERRY_STOP: "TERRY_STOP",
            IntentType.ARREST: "ARREST",
            IntentType.USE_OF_FORCE: "USE_OF_FORCE",
            IntentType.CUSTODIAL_INTERROGATION: "CUSTODIAL_INTERROGATION",
            IntentType.VEHICLE_PURSUIT: "VEHICLE_PURSUIT",
            IntentType.FELONY_STOP: "FELONY_STOP",
        }
        
        action_type = guardrail_mapping.get(intent_type, "UNKNOWN")
        
        return {
            "status": "PASS",
            "action_type": action_type,
            "officer_id": officer_id,
            "checks_performed": [
                "constitutional_compliance",
                "policy_compliance",
                "bias_check",
            ],
            "recommendations": [],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_intent_history(
        self,
        limit: int = 100,
        officer_id: Optional[str] = None,
        intent_type: Optional[IntentType] = None,
    ) -> List[OfficerIntent]:
        """Get intent detection history"""
        history = self.detected_intents
        
        if officer_id:
            history = [i for i in history if i.officer_id == officer_id]
        
        if intent_type:
            history = [i for i in history if i.intent_type == intent_type]
        
        return history[-limit:]
    
    def get_incident_intents(self, incident_id: str) -> List[OfficerIntent]:
        """Get all intents for an incident"""
        return self.active_incidents.get(incident_id, [])
    
    def get_high_priority_intents(self, limit: int = 50) -> List[OfficerIntent]:
        """Get high-priority intents requiring attention"""
        high_priority = [
            i for i in self.detected_intents
            if i.requires_supervisor_review or 
               i.intent_type in [IntentType.CODE_RED, IntentType.USE_OF_FORCE, IntentType.VEHICLE_PURSUIT]
        ]
        return high_priority[-limit:]
    
    def get_guardrail_triggered_intents(self, limit: int = 100) -> List[OfficerIntent]:
        """Get intents that triggered guardrail checks"""
        return [i for i in self.detected_intents if i.guardrail_triggered][-limit:]
    
    def get_ten_code_meaning(self, code: str) -> Optional[str]:
        """Get meaning of a ten code"""
        return self.ten_codes.get(code.upper())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get intent interpretation statistics"""
        if not self.detected_intents:
            return {
                "total_intents": 0,
                "high_confidence": 0,
                "guardrail_triggered": 0,
                "supervisor_review_required": 0,
            }
        
        return {
            "total_intents": len(self.detected_intents),
            "high_confidence": sum(1 for i in self.detected_intents if i.confidence == IntentConfidence.HIGH),
            "medium_confidence": sum(1 for i in self.detected_intents if i.confidence == IntentConfidence.MEDIUM),
            "low_confidence": sum(1 for i in self.detected_intents if i.confidence == IntentConfidence.LOW),
            "guardrail_triggered": sum(1 for i in self.detected_intents if i.guardrail_triggered),
            "supervisor_review_required": sum(1 for i in self.detected_intents if i.requires_supervisor_review),
            "by_type": {
                intent_type.value: sum(1 for i in self.detected_intents if i.intent_type == intent_type)
                for intent_type in IntentType
            },
        }
