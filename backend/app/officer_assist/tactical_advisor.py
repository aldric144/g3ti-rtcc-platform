"""
Tactical Advisor Engine

Provides live tactical guidance for officers including:
- Best cover positions
- Suspect escape routes
- Backup ETA
- Building entry recommendations
- Scene-specific tactical advice

Supports: Traffic stops, foot pursuits, domestic calls, high-risk vehicle
encounters, burglary in progress, shots fired response
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TacticalScenario(str, Enum):
    """Types of tactical scenarios"""
    TRAFFIC_STOP = "TRAFFIC_STOP"
    FOOT_PURSUIT = "FOOT_PURSUIT"
    DOMESTIC_CALL = "DOMESTIC_CALL"
    HIGH_RISK_VEHICLE = "HIGH_RISK_VEHICLE"
    BURGLARY_IN_PROGRESS = "BURGLARY_IN_PROGRESS"
    SHOTS_FIRED = "SHOTS_FIRED"
    ARMED_ROBBERY = "ARMED_ROBBERY"
    HOSTAGE_SITUATION = "HOSTAGE_SITUATION"
    BARRICADED_SUBJECT = "BARRICADED_SUBJECT"
    ACTIVE_SHOOTER = "ACTIVE_SHOOTER"
    FELONY_STOP = "FELONY_STOP"
    WARRANT_SERVICE = "WARRANT_SERVICE"
    CROWD_CONTROL = "CROWD_CONTROL"
    BUILDING_SEARCH = "BUILDING_SEARCH"


class CoverType(str, Enum):
    """Types of cover"""
    HARD_COVER = "HARD_COVER"
    SOFT_COVER = "SOFT_COVER"
    CONCEALMENT = "CONCEALMENT"
    NONE = "NONE"


class ThreatLevel(str, Enum):
    """Threat levels"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CoverPosition(BaseModel):
    """Cover position recommendation"""
    position_id: str
    description: str
    cover_type: CoverType
    distance_feet: float
    direction: str
    effectiveness_score: float
    notes: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None


class EscapeRoute(BaseModel):
    """Suspect escape route"""
    route_id: str
    description: str
    probability: float
    direction: str
    vehicle_accessible: bool = False
    foot_accessible: bool = True
    intercept_points: List[str] = []
    recommended_units: int = 1


class BackupUnit(BaseModel):
    """Backup unit information"""
    unit_id: str
    unit_type: str
    eta_minutes: float
    distance_miles: float
    current_status: str
    capabilities: List[str] = []


class BuildingEntry(BaseModel):
    """Building entry recommendation"""
    entry_id: str
    entry_point: str
    direction: str
    risk_level: str
    recommended: bool
    notes: str
    requires_breach: bool = False
    cover_available: bool = True


class TacticalAdvice(BaseModel):
    """Complete tactical advice package"""
    advice_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    incident_id: str
    officer_id: str
    scenario: TacticalScenario
    threat_level: ThreatLevel
    primary_recommendation: str
    cover_positions: List[CoverPosition] = []
    escape_routes: List[EscapeRoute] = []
    backup_units: List[BackupUnit] = []
    building_entries: List[BuildingEntry] = []
    tactical_notes: List[str] = []
    warnings: List[str] = []
    communication_plan: Optional[str] = None
    containment_strategy: Optional[str] = None
    de_escalation_options: List[str] = []
    lethal_cover_required: bool = False
    less_lethal_recommended: bool = False
    k9_recommended: bool = False
    air_support_recommended: bool = False


class SceneLocation(BaseModel):
    """Scene location details"""
    address: str
    latitude: float
    longitude: float
    location_type: str
    building_type: Optional[str] = None
    floors: int = 1
    known_exits: int = 0
    parking_areas: List[str] = []
    nearby_landmarks: List[str] = []


class TacticalAdvisorEngine:
    """
    Tactical Advisor Engine
    
    Provides real-time tactical guidance and recommendations
    for various law enforcement scenarios.
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
            "county": "Palm Beach",
        }
        
        self.scenario_protocols = {
            TacticalScenario.TRAFFIC_STOP: {
                "approach": "driver_side_rear",
                "positioning": "offset_behind",
                "lighting": "high_beam_spotlight",
                "communication": "pa_system_first",
                "backup_threshold": "felony_or_multiple_occupants",
            },
            TacticalScenario.FELONY_STOP: {
                "approach": "no_approach",
                "positioning": "cover_behind_engine_block",
                "minimum_units": 2,
                "pa_commands": True,
                "weapons_drawn": True,
                "backup_required": True,
            },
            TacticalScenario.FOOT_PURSUIT: {
                "communication": "continuous_updates",
                "containment": "perimeter_priority",
                "air_support_threshold": "armed_or_violent_felony",
                "k9_threshold": "lost_visual",
                "termination_factors": ["officer_safety", "public_safety", "crime_severity"],
            },
            TacticalScenario.DOMESTIC_CALL: {
                "approach": "two_officer_minimum",
                "positioning": "offset_from_door",
                "weapons_check": "all_parties",
                "separation": "interview_separately",
                "children_check": "mandatory",
            },
            TacticalScenario.SHOTS_FIRED: {
                "approach": "staged_response",
                "minimum_units": 4,
                "cover_priority": "hard_cover_only",
                "medical_staging": True,
                "perimeter": "immediate",
                "air_support": "requested",
            },
            TacticalScenario.BURGLARY_IN_PROGRESS: {
                "approach": "silent",
                "perimeter_first": True,
                "minimum_units": 2,
                "k9_recommended": True,
                "entry_delay": "perimeter_set",
            },
            TacticalScenario.ACTIVE_SHOOTER: {
                "response": "immediate_action",
                "formation": "contact_team",
                "minimum_team": 2,
                "objective": "stop_threat",
                "medical_integration": "rescue_task_force",
            },
        }
        
        self.cover_effectiveness = {
            "engine_block": {"type": CoverType.HARD_COVER, "effectiveness": 0.95},
            "brick_wall": {"type": CoverType.HARD_COVER, "effectiveness": 0.90},
            "concrete_barrier": {"type": CoverType.HARD_COVER, "effectiveness": 0.95},
            "vehicle_door": {"type": CoverType.SOFT_COVER, "effectiveness": 0.30},
            "dumpster": {"type": CoverType.HARD_COVER, "effectiveness": 0.85},
            "tree_large": {"type": CoverType.SOFT_COVER, "effectiveness": 0.50},
            "wooden_fence": {"type": CoverType.CONCEALMENT, "effectiveness": 0.20},
            "bushes": {"type": CoverType.CONCEALMENT, "effectiveness": 0.10},
        }
        
        self.riviera_beach_zones = {
            "downtown": {"risk_modifier": 1.1, "backup_availability": "high"},
            "marina": {"risk_modifier": 1.0, "backup_availability": "medium"},
            "residential_north": {"risk_modifier": 0.9, "backup_availability": "medium"},
            "residential_south": {"risk_modifier": 1.0, "backup_availability": "medium"},
            "industrial": {"risk_modifier": 1.2, "backup_availability": "low"},
            "commercial": {"risk_modifier": 1.1, "backup_availability": "high"},
        }
        
        self.active_advisories: Dict[str, TacticalAdvice] = {}
        self.advisory_history: List[TacticalAdvice] = []
    
    def get_tactical_advice(
        self,
        incident_id: str,
        officer_id: str,
        scenario: TacticalScenario,
        location: Optional[SceneLocation] = None,
        threat_level: ThreatLevel = ThreatLevel.MODERATE,
        suspect_armed: bool = False,
        suspect_count: int = 1,
        officer_count: int = 1,
        available_backup: Optional[List[BackupUnit]] = None,
    ) -> TacticalAdvice:
        """
        Get tactical advice for a scenario
        
        Args:
            incident_id: Incident identifier
            officer_id: Requesting officer
            scenario: Type of tactical scenario
            location: Scene location details
            threat_level: Current threat level
            suspect_armed: Whether suspect is known to be armed
            suspect_count: Number of suspects
            officer_count: Number of officers on scene
            available_backup: Available backup units
            
        Returns:
            TacticalAdvice with recommendations
        """
        if suspect_armed:
            threat_level = ThreatLevel.HIGH if threat_level.value < ThreatLevel.HIGH.value else threat_level
        
        cover_positions = self._identify_cover_positions(location, scenario)
        escape_routes = self._identify_escape_routes(location, scenario)
        building_entries = self._identify_building_entries(location, scenario) if location else []
        
        if available_backup is None:
            available_backup = self._get_simulated_backup()
        
        tactical_notes = []
        warnings = []
        de_escalation_options = []
        
        protocol = self.scenario_protocols.get(scenario, {})
        
        primary_recommendation = self._generate_primary_recommendation(
            scenario, threat_level, suspect_armed, suspect_count, officer_count, protocol
        )
        
        if scenario == TacticalScenario.TRAFFIC_STOP:
            tactical_notes.extend([
                "Position patrol vehicle offset to driver's side rear",
                "Use high beams and spotlight to illuminate vehicle interior",
                "Approach from driver's side rear quarter panel",
                "Maintain awareness of passenger compartment",
            ])
            if suspect_count > 1:
                warnings.append("Multiple occupants - consider backup before approach")
            de_escalation_options.extend([
                "Use calm, clear verbal commands",
                "Explain reason for stop",
                "Allow subject to ask questions",
            ])
        
        elif scenario == TacticalScenario.FELONY_STOP:
            tactical_notes.extend([
                "Do NOT approach vehicle",
                "Position behind engine block for cover",
                "Use PA system for all commands",
                "Have subjects exit one at a time",
                "Prone subjects at gunpoint",
                "Wait for backup before approach",
            ])
            warnings.extend([
                "HIGH RISK - Maintain lethal cover",
                "Do not break cover until scene secured",
            ])
        
        elif scenario == TacticalScenario.FOOT_PURSUIT:
            tactical_notes.extend([
                "Broadcast direction of travel continuously",
                "Request perimeter units",
                "Maintain visual if safe",
                "Consider termination if losing ground",
            ])
            warnings.extend([
                "Watch for ambush points",
                "Do not enter confined spaces alone",
            ])
            if suspect_armed:
                warnings.append("ARMED SUSPECT - Do not close distance")
        
        elif scenario == TacticalScenario.DOMESTIC_CALL:
            tactical_notes.extend([
                "Two-officer response minimum",
                "Stand offset from door when knocking",
                "Separate parties for interviews",
                "Check on all children in residence",
                "Look for signs of injury on all parties",
            ])
            de_escalation_options.extend([
                "Speak calmly and separately to each party",
                "Allow venting without interruption",
                "Offer resources and alternatives",
            ])
            warnings.append("Domestic calls are high-risk - maintain awareness")
        
        elif scenario == TacticalScenario.SHOTS_FIRED:
            tactical_notes.extend([
                "Stage and await additional units",
                "Establish hard cover immediately",
                "Request medical staging",
                "Set perimeter before approach",
                "Request air support if available",
            ])
            warnings.extend([
                "ACTIVE THREAT - Hard cover only",
                "Do not approach without adequate backup",
                "Watch for secondary shooters",
            ])
        
        elif scenario == TacticalScenario.BURGLARY_IN_PROGRESS:
            tactical_notes.extend([
                "Silent approach - no sirens",
                "Establish perimeter before entry",
                "Request K9 if available",
                "Clear systematically room by room",
            ])
            if location and location.floors > 1:
                tactical_notes.append(f"Multi-story building ({location.floors} floors) - clear floor by floor")
        
        elif scenario == TacticalScenario.ACTIVE_SHOOTER:
            tactical_notes.extend([
                "IMMEDIATE ACTION REQUIRED",
                "Form contact team with available officers",
                "Move toward sound of gunfire",
                "Neutralize threat - do not stop for wounded",
                "Rescue Task Force for medical",
            ])
            warnings.extend([
                "ACTIVE THREAT - Immediate response required",
                "Do not wait for SWAT",
                "Priority is stopping the killing",
            ])
        
        lethal_cover_required = threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] or suspect_armed
        less_lethal_recommended = threat_level == ThreatLevel.MODERATE and not suspect_armed
        k9_recommended = scenario in [TacticalScenario.FOOT_PURSUIT, TacticalScenario.BURGLARY_IN_PROGRESS, TacticalScenario.BUILDING_SEARCH]
        air_support_recommended = scenario in [TacticalScenario.FOOT_PURSUIT, TacticalScenario.SHOTS_FIRED, TacticalScenario.ACTIVE_SHOOTER]
        
        containment_strategy = self._generate_containment_strategy(scenario, location, officer_count)
        communication_plan = self._generate_communication_plan(scenario, threat_level)
        
        advice = TacticalAdvice(
            advice_id=f"ta-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{incident_id}",
            incident_id=incident_id,
            officer_id=officer_id,
            scenario=scenario,
            threat_level=threat_level,
            primary_recommendation=primary_recommendation,
            cover_positions=cover_positions,
            escape_routes=escape_routes,
            backup_units=available_backup,
            building_entries=building_entries,
            tactical_notes=tactical_notes,
            warnings=warnings,
            communication_plan=communication_plan,
            containment_strategy=containment_strategy,
            de_escalation_options=de_escalation_options,
            lethal_cover_required=lethal_cover_required,
            less_lethal_recommended=less_lethal_recommended,
            k9_recommended=k9_recommended,
            air_support_recommended=air_support_recommended,
        )
        
        self.active_advisories[incident_id] = advice
        self.advisory_history.append(advice)
        
        return advice
    
    def _generate_primary_recommendation(
        self,
        scenario: TacticalScenario,
        threat_level: ThreatLevel,
        suspect_armed: bool,
        suspect_count: int,
        officer_count: int,
        protocol: Dict[str, Any],
    ) -> str:
        """Generate primary tactical recommendation"""
        if scenario == TacticalScenario.ACTIVE_SHOOTER:
            return "IMMEDIATE ACTION: Form contact team and move to neutralize threat"
        
        if threat_level == ThreatLevel.CRITICAL:
            return "CRITICAL THREAT: Seek hard cover immediately and await tactical support"
        
        if suspect_armed and officer_count < 2:
            return "ARMED SUSPECT: Stage and await backup before engagement"
        
        if suspect_count > officer_count * 2:
            return "OUTNUMBERED: Request additional units before contact"
        
        recommendations = {
            TacticalScenario.TRAFFIC_STOP: "Standard traffic stop approach - maintain tactical positioning",
            TacticalScenario.FELONY_STOP: "High-risk stop protocol - PA commands, do not approach",
            TacticalScenario.FOOT_PURSUIT: "Maintain visual, broadcast continuously, request perimeter",
            TacticalScenario.DOMESTIC_CALL: "Two-officer approach, separate parties, check for weapons",
            TacticalScenario.SHOTS_FIRED: "Stage for backup, establish hard cover, set perimeter",
            TacticalScenario.BURGLARY_IN_PROGRESS: "Silent approach, perimeter first, K9 if available",
            TacticalScenario.HOSTAGE_SITUATION: "Contain and isolate, request negotiator and SWAT",
            TacticalScenario.BARRICADED_SUBJECT: "Establish perimeter, request SWAT, begin negotiations",
        }
        
        return recommendations.get(scenario, "Assess scene and maintain tactical awareness")
    
    def _identify_cover_positions(
        self,
        location: Optional[SceneLocation],
        scenario: TacticalScenario,
    ) -> List[CoverPosition]:
        """Identify available cover positions"""
        positions = []
        
        positions.append(CoverPosition(
            position_id="cp-001",
            description="Engine block of patrol vehicle",
            cover_type=CoverType.HARD_COVER,
            distance_feet=15.0,
            direction="rear",
            effectiveness_score=0.95,
            notes="Best ballistic protection available",
        ))
        
        if scenario in [TacticalScenario.SHOTS_FIRED, TacticalScenario.ACTIVE_SHOOTER]:
            positions.append(CoverPosition(
                position_id="cp-002",
                description="Concrete barrier or wall corner",
                cover_type=CoverType.HARD_COVER,
                distance_feet=25.0,
                direction="lateral",
                effectiveness_score=0.90,
                notes="Provides hard cover with observation angle",
            ))
        
        positions.append(CoverPosition(
            position_id="cp-003",
            description="Building corner",
            cover_type=CoverType.HARD_COVER,
            distance_feet=30.0,
            direction="west",
            effectiveness_score=0.85,
            notes="Allows observation while maintaining cover",
        ))
        
        return positions
    
    def _identify_escape_routes(
        self,
        location: Optional[SceneLocation],
        scenario: TacticalScenario,
    ) -> List[EscapeRoute]:
        """Identify potential suspect escape routes"""
        routes = []
        
        routes.append(EscapeRoute(
            route_id="er-001",
            description="Primary street - northbound",
            probability=0.4,
            direction="north",
            vehicle_accessible=True,
            foot_accessible=True,
            intercept_points=["Main St intersection", "Highway on-ramp"],
            recommended_units=2,
        ))
        
        routes.append(EscapeRoute(
            route_id="er-002",
            description="Alley - eastbound",
            probability=0.3,
            direction="east",
            vehicle_accessible=False,
            foot_accessible=True,
            intercept_points=["Alley exit at 2nd Ave"],
            recommended_units=1,
        ))
        
        routes.append(EscapeRoute(
            route_id="er-003",
            description="Secondary street - southbound",
            probability=0.3,
            direction="south",
            vehicle_accessible=True,
            foot_accessible=True,
            intercept_points=["Traffic light at Oak St"],
            recommended_units=1,
        ))
        
        return routes
    
    def _identify_building_entries(
        self,
        location: Optional[SceneLocation],
        scenario: TacticalScenario,
    ) -> List[BuildingEntry]:
        """Identify building entry points"""
        entries = []
        
        entries.append(BuildingEntry(
            entry_id="be-001",
            entry_point="Front door",
            direction="south",
            risk_level="HIGH",
            recommended=False,
            notes="Expected entry point - likely monitored",
            requires_breach=False,
            cover_available=False,
        ))
        
        entries.append(BuildingEntry(
            entry_id="be-002",
            entry_point="Side door - west",
            direction="west",
            risk_level="MEDIUM",
            recommended=True,
            notes="Less visible approach, cover available from corner",
            requires_breach=False,
            cover_available=True,
        ))
        
        entries.append(BuildingEntry(
            entry_id="be-003",
            entry_point="Rear door",
            direction="north",
            risk_level="MEDIUM",
            recommended=True,
            notes="Good for secondary entry team",
            requires_breach=False,
            cover_available=True,
        ))
        
        return entries
    
    def _get_simulated_backup(self) -> List[BackupUnit]:
        """Get simulated backup unit information"""
        return [
            BackupUnit(
                unit_id="RBPD-201",
                unit_type="Patrol",
                eta_minutes=2.3,
                distance_miles=1.2,
                current_status="Responding",
                capabilities=["patrol", "traffic"],
            ),
            BackupUnit(
                unit_id="RBPD-205",
                unit_type="Patrol",
                eta_minutes=4.1,
                distance_miles=2.5,
                current_status="Responding",
                capabilities=["patrol", "traffic"],
            ),
            BackupUnit(
                unit_id="RBPD-K9",
                unit_type="K9",
                eta_minutes=8.5,
                distance_miles=5.0,
                current_status="Available",
                capabilities=["k9", "tracking", "apprehension"],
            ),
        ]
    
    def _generate_containment_strategy(
        self,
        scenario: TacticalScenario,
        location: Optional[SceneLocation],
        officer_count: int,
    ) -> str:
        """Generate containment strategy"""
        if scenario in [TacticalScenario.FOOT_PURSUIT, TacticalScenario.BURGLARY_IN_PROGRESS]:
            return f"Establish {min(4, officer_count + 2)}-point perimeter. Primary units cover likely escape routes. K9 for tracking if visual lost."
        elif scenario in [TacticalScenario.HOSTAGE_SITUATION, TacticalScenario.BARRICADED_SUBJECT]:
            return "Inner perimeter at 50 yards, outer perimeter at 100 yards. Evacuate adjacent structures. Establish command post."
        elif scenario == TacticalScenario.ACTIVE_SHOOTER:
            return "Dynamic containment - contact team moves to threat. Perimeter units prevent escape and direct evacuees."
        else:
            return "Standard scene containment. Control access points and maintain situational awareness."
    
    def _generate_communication_plan(
        self,
        scenario: TacticalScenario,
        threat_level: ThreatLevel,
    ) -> str:
        """Generate communication plan"""
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            return "TAC channel for all units. Dispatch monitors main. Updates every 60 seconds minimum."
        elif scenario in [TacticalScenario.FOOT_PURSUIT]:
            return "Continuous updates on main channel. Direction, speed, description. Request TAC if extended."
        else:
            return "Standard radio protocol. Request TAC channel if situation escalates."
    
    def update_advice(
        self,
        incident_id: str,
        **kwargs,
    ) -> Optional[TacticalAdvice]:
        """Update tactical advice with new information"""
        if incident_id not in self.active_advisories:
            return None
        
        current = self.active_advisories[incident_id]
        
        return self.get_tactical_advice(
            incident_id=incident_id,
            officer_id=current.officer_id,
            scenario=kwargs.get("scenario", current.scenario),
            threat_level=kwargs.get("threat_level", current.threat_level),
            suspect_armed=kwargs.get("suspect_armed", current.lethal_cover_required),
        )
    
    def get_active_advisory(self, incident_id: str) -> Optional[TacticalAdvice]:
        """Get active advisory for incident"""
        return self.active_advisories.get(incident_id)
    
    def get_advisory_history(self, limit: int = 100) -> List[TacticalAdvice]:
        """Get advisory history"""
        return self.advisory_history[-limit:]
    
    def close_incident(self, incident_id: str) -> bool:
        """Close incident and remove from active advisories"""
        if incident_id in self.active_advisories:
            del self.active_advisories[incident_id]
            return True
        return False
    
    def get_scenario_protocol(self, scenario: TacticalScenario) -> Dict[str, Any]:
        """Get protocol for a specific scenario"""
        return self.scenario_protocols.get(scenario, {})
