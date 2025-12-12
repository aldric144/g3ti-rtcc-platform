"""
Phase 31: Autonomous Recovery & Logistics Engine

Implements:
- Damage Assessment AI
- Humanitarian Supply Optimizer
- Cost & Recovery Timeline Estimation

City: Riviera Beach, Florida 33404
Agency ORI: FL0500400
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
import uuid
import math


class DamageTier(Enum):
    """Structure damage tiers"""
    NONE = 0
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    DESTROYED = 4


class RecoveryPhase(Enum):
    """Recovery phases"""
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    INTERMEDIATE = "intermediate"
    LONG_TERM = "long_term"


class FEMACategory(Enum):
    """FEMA disaster categories"""
    CATEGORY_A = "debris_removal"
    CATEGORY_B = "emergency_protective_measures"
    CATEGORY_C = "roads_bridges"
    CATEGORY_D = "water_control"
    CATEGORY_E = "public_buildings"
    CATEGORY_F = "public_utilities"
    CATEGORY_G = "parks_recreation"


class SupplyType(Enum):
    """Humanitarian supply types"""
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    GENERATOR = "generator"
    FUEL = "fuel"
    SHELTER_KIT = "shelter_kit"
    HYGIENE_KIT = "hygiene_kit"
    BLANKETS = "blankets"
    TARPS = "tarps"
    TOOLS = "tools"


class InfrastructureType(Enum):
    """Infrastructure types"""
    ROAD = "road"
    BRIDGE = "bridge"
    POWER_LINE = "power_line"
    WATER_MAIN = "water_main"
    SEWER = "sewer"
    BUILDING = "building"
    SEAWALL = "seawall"
    DRAINAGE = "drainage"


@dataclass
class StructureDamage:
    """Individual structure damage assessment"""
    assessment_id: str
    timestamp: datetime
    structure_id: str
    structure_type: str
    address: str
    zone: str
    damage_tier: DamageTier
    damage_percent: float
    structural_integrity: str
    habitability: str
    utility_status: Dict[str, str] = field(default_factory=dict)
    hazards_present: List[str] = field(default_factory=list)
    estimated_repair_cost: float = 0.0
    estimated_repair_days: int = 0
    insurance_category: str = ""
    photos_available: bool = False
    inspector_notes: str = ""
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.assessment_id}:{self.timestamp.isoformat()}:{self.structure_id}:{self.damage_tier.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class DamageAssessment:
    """Zone-level damage assessment"""
    assessment_id: str
    timestamp: datetime
    zone: str
    incident_type: str
    total_structures_assessed: int
    structures_by_tier: Dict[str, int]
    total_damage_estimate: float
    utility_outages: Dict[str, int]
    road_closures: int
    bridge_closures: int
    displaced_residents: int
    injuries_reported: int
    fatalities_reported: int
    disaster_impact_index: float
    priority_repairs: List[str] = field(default_factory=list)
    fema_categories_affected: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.assessment_id}:{self.timestamp.isoformat()}:{self.zone}:{self.disaster_impact_index}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class SupplyAllocation:
    """Supply allocation record"""
    allocation_id: str
    timestamp: datetime
    supply_type: SupplyType
    quantity: int
    unit: str
    source_location: str
    destination_zone: str
    destination_facility: str
    priority: int
    estimated_arrival: datetime
    status: str
    beneficiaries_served: int = 0
    days_of_supply: float = 0.0
    cost: float = 0.0
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.allocation_id}:{self.timestamp.isoformat()}:{self.supply_type.value}:{self.quantity}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class InfrastructureRepair:
    """Infrastructure repair record"""
    repair_id: str
    timestamp: datetime
    infrastructure_type: InfrastructureType
    infrastructure_name: str
    zone: str
    damage_description: str
    repair_priority: int
    estimated_cost: float
    estimated_days: int
    contractor_assigned: Optional[str] = None
    fema_category: Optional[FEMACategory] = None
    federal_share_percent: float = 75.0
    state_share_percent: float = 12.5
    local_share_percent: float = 12.5
    status: str = "pending"
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.repair_id}:{self.timestamp.isoformat()}:{self.infrastructure_type.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RecoveryTimeline:
    """Recovery timeline estimation"""
    timeline_id: str
    timestamp: datetime
    zone: str
    incident_type: str
    immediate_phase_days: int
    short_term_phase_days: int
    intermediate_phase_days: int
    long_term_phase_days: int
    total_recovery_days: int
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    critical_path_items: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class RecoveryPlan:
    """Comprehensive recovery plan"""
    plan_id: str
    timestamp: datetime
    incident_type: str
    affected_zones: List[str]
    damage_assessments: List[DamageAssessment]
    supply_allocations: List[SupplyAllocation]
    infrastructure_repairs: List[InfrastructureRepair]
    recovery_timeline: RecoveryTimeline
    total_estimated_cost: float
    federal_assistance_estimate: float
    state_assistance_estimate: float
    local_cost_share: float
    insurance_claims_estimate: float
    unmet_needs_estimate: float
    population_affected: int
    housing_units_damaged: int
    businesses_affected: int
    jobs_impacted: int
    economic_impact_estimate: float
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.plan_id}:{self.timestamp.isoformat()}:{self.incident_type}:{self.total_estimated_cost}"
        return hashlib.sha256(data.encode()).hexdigest()


class RecoveryPlanner:
    """
    Autonomous Recovery & Logistics Engine
    
    Provides damage assessment, supply optimization,
    and recovery timeline estimation.
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
            "city": "Riviera Beach",
            "state": "FL",
            "zip": "33404",
            "county": "Palm Beach",
        }
        
        self.city_zones = [
            "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
            "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
        ]
        
        self.zone_populations = {
            "Zone_A": 3500, "Zone_B": 4200, "Zone_C": 3800,
            "Zone_D": 2900, "Zone_E": 4500, "Zone_F": 3200,
            "Zone_G": 2800, "Zone_H": 3600, "Zone_I": 4100,
            "Zone_J": 3400,
        }
        
        self.zone_structures = {
            "Zone_A": 1200, "Zone_B": 1500, "Zone_C": 1300,
            "Zone_D": 1000, "Zone_E": 1600, "Zone_F": 1100,
            "Zone_G": 950, "Zone_H": 1250, "Zone_I": 1400,
            "Zone_J": 1150,
        }
        
        self.supply_sources = [
            {"name": "Palm Beach County EOC", "distance_miles": 15},
            {"name": "FEMA Distribution Center", "distance_miles": 50},
            {"name": "Red Cross Regional Warehouse", "distance_miles": 25},
            {"name": "Local Emergency Stockpile", "distance_miles": 5},
        ]
        
        self.repair_cost_estimates = {
            InfrastructureType.ROAD: 50000,
            InfrastructureType.BRIDGE: 500000,
            InfrastructureType.POWER_LINE: 25000,
            InfrastructureType.WATER_MAIN: 75000,
            InfrastructureType.SEWER: 100000,
            InfrastructureType.BUILDING: 150000,
            InfrastructureType.SEAWALL: 250000,
            InfrastructureType.DRAINAGE: 40000,
        }
        
        self.statistics = {
            "total_assessments": 0,
            "total_supply_allocations": 0,
            "total_repair_plans": 0,
            "total_recovery_plans": 0,
        }
    
    def assess_structure_damage(
        self,
        structure_id: str,
        structure_type: str,
        address: str,
        zone: str,
        damage_indicators: Dict[str, Any],
    ) -> StructureDamage:
        """
        Assess damage to an individual structure.
        """
        assessment_id = f"SD-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        damage_percent = 0.0
        damage_tier = DamageTier.NONE
        
        if damage_indicators.get("roof_damage"):
            damage_percent += damage_indicators.get("roof_damage_percent", 20)
        if damage_indicators.get("wall_damage"):
            damage_percent += damage_indicators.get("wall_damage_percent", 25)
        if damage_indicators.get("foundation_damage"):
            damage_percent += damage_indicators.get("foundation_damage_percent", 30)
        if damage_indicators.get("flooding"):
            damage_percent += damage_indicators.get("flood_damage_percent", 15)
        if damage_indicators.get("fire_damage"):
            damage_percent += damage_indicators.get("fire_damage_percent", 40)
        
        damage_percent = min(damage_percent, 100)
        
        if damage_percent >= 80:
            damage_tier = DamageTier.DESTROYED
        elif damage_percent >= 50:
            damage_tier = DamageTier.MAJOR
        elif damage_percent >= 25:
            damage_tier = DamageTier.MODERATE
        elif damage_percent > 0:
            damage_tier = DamageTier.MINOR
        
        structural_integrity = "safe"
        if damage_tier == DamageTier.DESTROYED:
            structural_integrity = "unsafe_condemned"
        elif damage_tier == DamageTier.MAJOR:
            structural_integrity = "unsafe_restricted"
        elif damage_tier == DamageTier.MODERATE:
            structural_integrity = "limited_entry"
        
        habitability = "habitable"
        if damage_tier.value >= DamageTier.MAJOR.value:
            habitability = "uninhabitable"
        elif damage_tier == DamageTier.MODERATE:
            habitability = "limited"
        
        utility_status = {
            "electricity": "on" if not damage_indicators.get("power_out") else "off",
            "water": "on" if not damage_indicators.get("water_out") else "off",
            "gas": "on" if not damage_indicators.get("gas_out") else "off",
            "sewer": "functional" if not damage_indicators.get("sewer_damage") else "damaged",
        }
        
        hazards = []
        if damage_indicators.get("gas_leak"):
            hazards.append("gas_leak")
        if damage_indicators.get("electrical_hazard"):
            hazards.append("electrical_hazard")
        if damage_indicators.get("structural_collapse_risk"):
            hazards.append("collapse_risk")
        if damage_indicators.get("mold_risk"):
            hazards.append("mold_risk")
        if damage_indicators.get("contamination"):
            hazards.append("contamination")
        
        base_value = 200000
        repair_cost = base_value * (damage_percent / 100)
        
        repair_days = int(damage_percent / 5) + 1
        if damage_tier == DamageTier.DESTROYED:
            repair_days = 180
        
        return StructureDamage(
            assessment_id=assessment_id,
            timestamp=timestamp,
            structure_id=structure_id,
            structure_type=structure_type,
            address=address,
            zone=zone,
            damage_tier=damage_tier,
            damage_percent=damage_percent,
            structural_integrity=structural_integrity,
            habitability=habitability,
            utility_status=utility_status,
            hazards_present=hazards,
            estimated_repair_cost=repair_cost,
            estimated_repair_days=repair_days,
            insurance_category=self._determine_insurance_category(damage_tier),
        )
    
    def assess_zone_damage(
        self,
        zone: str,
        incident_type: str,
        data_sources: Optional[List[str]] = None,
        severity_factor: float = 0.5,
    ) -> DamageAssessment:
        """
        Assess damage at zone level using AI analysis.
        """
        assessment_id = f"DA-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        total_structures = self.zone_structures.get(zone, 1000)
        population = self.zone_populations.get(zone, 3000)
        
        destroyed = int(total_structures * severity_factor * 0.1)
        major = int(total_structures * severity_factor * 0.15)
        moderate = int(total_structures * severity_factor * 0.25)
        minor = int(total_structures * severity_factor * 0.30)
        none = total_structures - destroyed - major - moderate - minor
        
        structures_by_tier = {
            "destroyed": destroyed,
            "major": major,
            "moderate": moderate,
            "minor": minor,
            "none": none,
        }
        
        avg_structure_value = 200000
        total_damage = (
            destroyed * avg_structure_value +
            major * avg_structure_value * 0.6 +
            moderate * avg_structure_value * 0.35 +
            minor * avg_structure_value * 0.1
        )
        
        utility_outages = {
            "electricity": int(total_structures * severity_factor * 0.6),
            "water": int(total_structures * severity_factor * 0.4),
            "gas": int(total_structures * severity_factor * 0.2),
            "internet": int(total_structures * severity_factor * 0.7),
        }
        
        road_closures = int(10 * severity_factor)
        bridge_closures = 1 if severity_factor > 0.5 else 0
        
        displaced = int((destroyed + major) * 2.5)
        injuries = int(population * severity_factor * 0.01)
        fatalities = int(population * severity_factor * 0.001) if severity_factor > 0.7 else 0
        
        impact_index = (
            (destroyed / total_structures) * 40 +
            (major / total_structures) * 30 +
            (moderate / total_structures) * 20 +
            (displaced / population) * 10
        )
        impact_index = min(impact_index, 100)
        
        priority_repairs = []
        if bridge_closures > 0:
            priority_repairs.append("Bridge restoration")
        if utility_outages["electricity"] > total_structures * 0.3:
            priority_repairs.append("Power grid restoration")
        if utility_outages["water"] > total_structures * 0.2:
            priority_repairs.append("Water system restoration")
        if road_closures > 5:
            priority_repairs.append("Road clearing and repair")
        
        fema_categories = [FEMACategory.CATEGORY_A.value, FEMACategory.CATEGORY_B.value]
        if road_closures > 0 or bridge_closures > 0:
            fema_categories.append(FEMACategory.CATEGORY_C.value)
        if utility_outages["water"] > 0:
            fema_categories.append(FEMACategory.CATEGORY_D.value)
        if destroyed + major > 0:
            fema_categories.append(FEMACategory.CATEGORY_E.value)
        if utility_outages["electricity"] > 0:
            fema_categories.append(FEMACategory.CATEGORY_F.value)
        
        confidence = 0.6
        if data_sources:
            confidence = min(0.5 + len(data_sources) * 0.1, 0.95)
        
        self.statistics["total_assessments"] += 1
        
        return DamageAssessment(
            assessment_id=assessment_id,
            timestamp=timestamp,
            zone=zone,
            incident_type=incident_type,
            total_structures_assessed=total_structures,
            structures_by_tier=structures_by_tier,
            total_damage_estimate=total_damage,
            utility_outages=utility_outages,
            road_closures=road_closures,
            bridge_closures=bridge_closures,
            displaced_residents=displaced,
            injuries_reported=injuries,
            fatalities_reported=fatalities,
            disaster_impact_index=impact_index,
            priority_repairs=priority_repairs,
            fema_categories_affected=fema_categories,
            data_sources=data_sources or ["drone_imagery", "sensor_grid"],
            confidence_score=confidence,
        )
    
    def optimize_supply_allocation(
        self,
        zone: str,
        supply_type: SupplyType,
        population_served: int,
        days_needed: float = 3.0,
        priority: int = 3,
    ) -> SupplyAllocation:
        """
        Optimize supply allocation for a zone.
        """
        allocation_id = f"SA-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        quantity = self._calculate_supply_quantity(supply_type, population_served, days_needed)
        unit = self._get_supply_unit(supply_type)
        
        best_source = min(self.supply_sources, key=lambda s: s["distance_miles"])
        
        travel_hours = best_source["distance_miles"] / 30
        estimated_arrival = timestamp + timedelta(hours=travel_hours + 2)
        
        cost = self._calculate_supply_cost(supply_type, quantity)
        
        self.statistics["total_supply_allocations"] += 1
        
        return SupplyAllocation(
            allocation_id=allocation_id,
            timestamp=timestamp,
            supply_type=supply_type,
            quantity=quantity,
            unit=unit,
            source_location=best_source["name"],
            destination_zone=zone,
            destination_facility=f"{zone} Distribution Point",
            priority=priority,
            estimated_arrival=estimated_arrival,
            status="dispatched",
            beneficiaries_served=population_served,
            days_of_supply=days_needed,
            cost=cost,
        )
    
    def plan_infrastructure_repair(
        self,
        infrastructure_type: InfrastructureType,
        infrastructure_name: str,
        zone: str,
        damage_description: str,
        priority: int = 3,
    ) -> InfrastructureRepair:
        """
        Plan infrastructure repair.
        """
        repair_id = f"IR-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        base_cost = self.repair_cost_estimates.get(infrastructure_type, 100000)
        
        if "major" in damage_description.lower() or "severe" in damage_description.lower():
            estimated_cost = base_cost * 1.5
            estimated_days = 30
        elif "moderate" in damage_description.lower():
            estimated_cost = base_cost
            estimated_days = 14
        else:
            estimated_cost = base_cost * 0.5
            estimated_days = 7
        
        fema_category = self._determine_fema_category(infrastructure_type)
        
        self.statistics["total_repair_plans"] += 1
        
        return InfrastructureRepair(
            repair_id=repair_id,
            timestamp=timestamp,
            infrastructure_type=infrastructure_type,
            infrastructure_name=infrastructure_name,
            zone=zone,
            damage_description=damage_description,
            repair_priority=priority,
            estimated_cost=estimated_cost,
            estimated_days=estimated_days,
            fema_category=fema_category,
        )
    
    def estimate_recovery_timeline(
        self,
        zone: str,
        incident_type: str,
        damage_assessment: DamageAssessment,
    ) -> RecoveryTimeline:
        """
        Estimate recovery timeline for a zone.
        """
        timeline_id = f"RT-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        impact_index = damage_assessment.disaster_impact_index
        
        immediate_days = 3 + int(impact_index / 20)
        short_term_days = 14 + int(impact_index / 10)
        intermediate_days = 30 + int(impact_index / 5)
        long_term_days = 90 + int(impact_index * 2)
        
        total_days = immediate_days + short_term_days + intermediate_days + long_term_days
        
        milestones = [
            {
                "phase": "immediate",
                "day": 1,
                "milestone": "Emergency operations center activated",
            },
            {
                "phase": "immediate",
                "day": 3,
                "milestone": "Search and rescue complete",
            },
            {
                "phase": "short_term",
                "day": immediate_days + 7,
                "milestone": "Power restored to 80% of structures",
            },
            {
                "phase": "short_term",
                "day": immediate_days + 14,
                "milestone": "Water service restored",
            },
            {
                "phase": "intermediate",
                "day": immediate_days + short_term_days + 14,
                "milestone": "Major roads reopened",
            },
            {
                "phase": "intermediate",
                "day": immediate_days + short_term_days + 30,
                "milestone": "Temporary housing established",
            },
            {
                "phase": "long_term",
                "day": total_days - 30,
                "milestone": "Permanent repairs 75% complete",
            },
            {
                "phase": "long_term",
                "day": total_days,
                "milestone": "Full recovery achieved",
            },
        ]
        
        critical_path = []
        if damage_assessment.bridge_closures > 0:
            critical_path.append("Bridge repair")
        if damage_assessment.utility_outages.get("electricity", 0) > 500:
            critical_path.append("Power grid restoration")
        if damage_assessment.structures_by_tier.get("destroyed", 0) > 50:
            critical_path.append("Debris removal")
        
        risk_factors = []
        if incident_type == "hurricane":
            risk_factors.append("Secondary storm risk")
        if damage_assessment.displaced_residents > 1000:
            risk_factors.append("Housing shortage")
        if damage_assessment.total_damage_estimate > 50000000:
            risk_factors.append("Funding delays")
        
        return RecoveryTimeline(
            timeline_id=timeline_id,
            timestamp=timestamp,
            zone=zone,
            incident_type=incident_type,
            immediate_phase_days=immediate_days,
            short_term_phase_days=short_term_days,
            intermediate_phase_days=intermediate_days,
            long_term_phase_days=long_term_days,
            total_recovery_days=total_days,
            milestones=milestones,
            critical_path_items=critical_path,
            risk_factors=risk_factors,
            confidence_score=0.75,
        )
    
    def create_recovery_plan(
        self,
        incident_type: str,
        affected_zones: List[str],
        severity_factor: float = 0.5,
    ) -> RecoveryPlan:
        """
        Create comprehensive recovery plan.
        """
        plan_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        damage_assessments = []
        for zone in affected_zones:
            assessment = self.assess_zone_damage(
                zone=zone,
                incident_type=incident_type,
                severity_factor=severity_factor,
            )
            damage_assessments.append(assessment)
        
        supply_allocations = []
        for zone in affected_zones:
            population = self.zone_populations.get(zone, 3000)
            displaced = int(population * severity_factor * 0.2)
            
            if displaced > 0:
                for supply_type in [SupplyType.FOOD, SupplyType.WATER, SupplyType.MEDICAL]:
                    allocation = self.optimize_supply_allocation(
                        zone=zone,
                        supply_type=supply_type,
                        population_served=displaced,
                        days_needed=7.0,
                    )
                    supply_allocations.append(allocation)
        
        infrastructure_repairs = []
        for assessment in damage_assessments:
            if assessment.road_closures > 0:
                repair = self.plan_infrastructure_repair(
                    infrastructure_type=InfrastructureType.ROAD,
                    infrastructure_name=f"{assessment.zone} Main Road",
                    zone=assessment.zone,
                    damage_description="Moderate damage from flooding",
                    priority=2,
                )
                infrastructure_repairs.append(repair)
            
            if assessment.bridge_closures > 0:
                repair = self.plan_infrastructure_repair(
                    infrastructure_type=InfrastructureType.BRIDGE,
                    infrastructure_name=f"{assessment.zone} Bridge",
                    zone=assessment.zone,
                    damage_description="Major structural damage",
                    priority=1,
                )
                infrastructure_repairs.append(repair)
            
            if assessment.utility_outages.get("electricity", 0) > 100:
                repair = self.plan_infrastructure_repair(
                    infrastructure_type=InfrastructureType.POWER_LINE,
                    infrastructure_name=f"{assessment.zone} Power Grid",
                    zone=assessment.zone,
                    damage_description="Multiple line failures",
                    priority=1,
                )
                infrastructure_repairs.append(repair)
        
        combined_assessment = damage_assessments[0] if damage_assessments else None
        if combined_assessment:
            recovery_timeline = self.estimate_recovery_timeline(
                zone=affected_zones[0],
                incident_type=incident_type,
                damage_assessment=combined_assessment,
            )
        else:
            recovery_timeline = RecoveryTimeline(
                timeline_id=f"RT-{uuid.uuid4().hex[:8].upper()}",
                timestamp=timestamp,
                zone=affected_zones[0] if affected_zones else "Zone_A",
                incident_type=incident_type,
                immediate_phase_days=7,
                short_term_phase_days=30,
                intermediate_phase_days=60,
                long_term_phase_days=180,
                total_recovery_days=277,
            )
        
        total_damage = sum(a.total_damage_estimate for a in damage_assessments)
        total_repair_cost = sum(r.estimated_cost for r in infrastructure_repairs)
        total_supply_cost = sum(s.cost for s in supply_allocations)
        
        total_cost = total_damage + total_repair_cost + total_supply_cost
        
        federal_assistance = total_cost * 0.75
        state_assistance = total_cost * 0.125
        local_share = total_cost * 0.125
        
        insurance_estimate = total_damage * 0.4
        unmet_needs = total_cost - federal_assistance - state_assistance - insurance_estimate
        
        population_affected = sum(
            self.zone_populations.get(z, 0) for z in affected_zones
        )
        housing_damaged = sum(
            a.structures_by_tier.get("destroyed", 0) +
            a.structures_by_tier.get("major", 0) +
            a.structures_by_tier.get("moderate", 0)
            for a in damage_assessments
        )
        businesses_affected = int(housing_damaged * 0.1)
        jobs_impacted = businesses_affected * 5
        
        economic_impact = total_damage * 1.5
        
        self.statistics["total_recovery_plans"] += 1
        
        return RecoveryPlan(
            plan_id=plan_id,
            timestamp=timestamp,
            incident_type=incident_type,
            affected_zones=affected_zones,
            damage_assessments=damage_assessments,
            supply_allocations=supply_allocations,
            infrastructure_repairs=infrastructure_repairs,
            recovery_timeline=recovery_timeline,
            total_estimated_cost=total_cost,
            federal_assistance_estimate=federal_assistance,
            state_assistance_estimate=state_assistance,
            local_cost_share=local_share,
            insurance_claims_estimate=insurance_estimate,
            unmet_needs_estimate=max(0, unmet_needs),
            population_affected=population_affected,
            housing_units_damaged=housing_damaged,
            businesses_affected=businesses_affected,
            jobs_impacted=jobs_impacted,
            economic_impact_estimate=economic_impact,
        )
    
    def _determine_insurance_category(self, damage_tier: DamageTier) -> str:
        """Determine insurance category based on damage tier."""
        categories = {
            DamageTier.NONE: "no_claim",
            DamageTier.MINOR: "minor_claim",
            DamageTier.MODERATE: "standard_claim",
            DamageTier.MAJOR: "major_claim",
            DamageTier.DESTROYED: "total_loss",
        }
        return categories.get(damage_tier, "unknown")
    
    def _determine_fema_category(self, infrastructure_type: InfrastructureType) -> FEMACategory:
        """Determine FEMA category for infrastructure type."""
        mapping = {
            InfrastructureType.ROAD: FEMACategory.CATEGORY_C,
            InfrastructureType.BRIDGE: FEMACategory.CATEGORY_C,
            InfrastructureType.POWER_LINE: FEMACategory.CATEGORY_F,
            InfrastructureType.WATER_MAIN: FEMACategory.CATEGORY_F,
            InfrastructureType.SEWER: FEMACategory.CATEGORY_F,
            InfrastructureType.BUILDING: FEMACategory.CATEGORY_E,
            InfrastructureType.SEAWALL: FEMACategory.CATEGORY_D,
            InfrastructureType.DRAINAGE: FEMACategory.CATEGORY_D,
        }
        return mapping.get(infrastructure_type, FEMACategory.CATEGORY_A)
    
    def _calculate_supply_quantity(
        self,
        supply_type: SupplyType,
        population: int,
        days: float,
    ) -> int:
        """Calculate supply quantity needed."""
        daily_needs = {
            SupplyType.FOOD: 3,
            SupplyType.WATER: 1,
            SupplyType.MEDICAL: 0.1,
            SupplyType.GENERATOR: 0.01,
            SupplyType.FUEL: 2,
            SupplyType.SHELTER_KIT: 0.25,
            SupplyType.HYGIENE_KIT: 0.5,
            SupplyType.BLANKETS: 1,
            SupplyType.TARPS: 0.1,
            SupplyType.TOOLS: 0.05,
        }
        daily_per_person = daily_needs.get(supply_type, 1)
        return int(population * daily_per_person * days)
    
    def _get_supply_unit(self, supply_type: SupplyType) -> str:
        """Get unit of measure for supply type."""
        units = {
            SupplyType.FOOD: "meals",
            SupplyType.WATER: "gallons",
            SupplyType.MEDICAL: "kits",
            SupplyType.GENERATOR: "units",
            SupplyType.FUEL: "gallons",
            SupplyType.SHELTER_KIT: "kits",
            SupplyType.HYGIENE_KIT: "kits",
            SupplyType.BLANKETS: "units",
            SupplyType.TARPS: "units",
            SupplyType.TOOLS: "kits",
        }
        return units.get(supply_type, "units")
    
    def _calculate_supply_cost(self, supply_type: SupplyType, quantity: int) -> float:
        """Calculate supply cost."""
        unit_costs = {
            SupplyType.FOOD: 5,
            SupplyType.WATER: 0.5,
            SupplyType.MEDICAL: 50,
            SupplyType.GENERATOR: 500,
            SupplyType.FUEL: 4,
            SupplyType.SHELTER_KIT: 200,
            SupplyType.HYGIENE_KIT: 25,
            SupplyType.BLANKETS: 15,
            SupplyType.TARPS: 30,
            SupplyType.TOOLS: 100,
        }
        unit_cost = unit_costs.get(supply_type, 10)
        return quantity * unit_cost
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.statistics,
            "agency": self.agency_config,
            "zones_covered": len(self.city_zones),
            "supply_sources": len(self.supply_sources),
        }
