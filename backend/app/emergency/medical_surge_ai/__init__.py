"""
Phase 21: Medical Surge AI Module

Hospital load prediction, EMS demand forecasting, triage priority modeling,
and medical supply tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import math


class HospitalStatus(Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    SURGE = "surge"
    CRITICAL = "critical"
    DIVERT = "divert"


class TriageLevel(Enum):
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    MINOR = "minor"
    EXPECTANT = "expectant"
    DECEASED = "deceased"


class EMSUnitStatus(Enum):
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    AT_HOSPITAL = "at_hospital"
    OUT_OF_SERVICE = "out_of_service"


class MedicalSupplyCategory(Enum):
    MEDICATIONS = "medications"
    BLOOD_PRODUCTS = "blood_products"
    IV_FLUIDS = "iv_fluids"
    SURGICAL = "surgical"
    RESPIRATORY = "respiratory"
    CARDIAC = "cardiac"
    TRAUMA = "trauma"
    PPE = "ppe"
    DIAGNOSTIC = "diagnostic"


class InjuryType(Enum):
    TRAUMA = "trauma"
    BURN = "burn"
    RESPIRATORY = "respiratory"
    CARDIAC = "cardiac"
    CRUSH = "crush"
    LACERATION = "laceration"
    FRACTURE = "fracture"
    HEAD_INJURY = "head_injury"
    DROWNING = "drowning"
    HYPOTHERMIA = "hypothermia"
    HEAT_STROKE = "heat_stroke"


@dataclass
class Hospital:
    hospital_id: str
    name: str
    address: Dict[str, Any]
    status: HospitalStatus
    total_beds: int
    available_beds: int
    icu_beds: int
    icu_available: int
    er_capacity: int
    er_current: int
    trauma_level: int
    specialties: List[str]
    ambulance_divert: bool
    surge_capacity: int
    staff_on_duty: int
    ventilators_available: int
    blood_supply_status: str
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HospitalLoadPrediction:
    prediction_id: str
    hospital_id: str
    prediction_time: datetime
    predicted_er_arrivals: int
    predicted_admissions: int
    predicted_icu_demand: int
    predicted_surge_level: HospitalStatus
    confidence_score: float
    factors: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EMSUnit:
    unit_id: str
    unit_name: str
    unit_type: str
    status: EMSUnitStatus
    current_location: Dict[str, float]
    assigned_call: Optional[str]
    crew_count: int
    capabilities: List[str]
    equipment: List[str]
    last_dispatch: Optional[datetime]
    shift_end: Optional[datetime]


@dataclass
class EMSDemandForecast:
    forecast_id: str
    forecast_period_start: datetime
    forecast_period_end: datetime
    predicted_calls: int
    predicted_transports: int
    predicted_als_calls: int
    predicted_bls_calls: int
    peak_hours: List[int]
    geographic_hotspots: List[Dict[str, Any]]
    recommended_staging: List[Dict[str, Any]]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TriagePatient:
    patient_id: str
    triage_level: TriageLevel
    injury_type: InjuryType
    injury_description: str
    vital_signs: Dict[str, Any]
    age_group: str
    location_found: Dict[str, Any]
    transport_status: str
    destination_hospital: Optional[str]
    triage_time: datetime
    notes: str


@dataclass
class MassCalsualtySummary:
    incident_id: str
    incident_type: str
    location: Dict[str, Any]
    total_patients: int
    by_triage_level: Dict[str, int]
    by_injury_type: Dict[str, int]
    transported: int
    pending_transport: int
    deceased: int
    hospitals_receiving: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MedicalSupply:
    supply_id: str
    name: str
    category: MedicalSupplyCategory
    quantity: int
    unit: str
    location: str
    expiration_date: Optional[datetime]
    minimum_stock: int
    critical_threshold: int
    supplier: str
    last_restocked: Optional[datetime]


class HospitalLoadPredictor:
    """
    Predicts hospital load during emergencies.
    """

    def __init__(self):
        self._hospitals: Dict[str, Hospital] = {}
        self._predictions: Dict[str, HospitalLoadPrediction] = {}

    def register_hospital(
        self,
        name: str,
        address: Dict[str, Any],
        total_beds: int,
        icu_beds: int,
        er_capacity: int,
        trauma_level: int,
        specialties: Optional[List[str]] = None,
    ) -> Hospital:
        """Register a hospital."""
        hospital_id = f"hosp-{uuid.uuid4().hex[:8]}"

        hospital = Hospital(
            hospital_id=hospital_id,
            name=name,
            address=address,
            status=HospitalStatus.NORMAL,
            total_beds=total_beds,
            available_beds=int(total_beds * 0.3),
            icu_beds=icu_beds,
            icu_available=int(icu_beds * 0.2),
            er_capacity=er_capacity,
            er_current=0,
            trauma_level=trauma_level,
            specialties=specialties or [],
            ambulance_divert=False,
            surge_capacity=int(total_beds * 0.2),
            staff_on_duty=0,
            ventilators_available=int(icu_beds * 0.5),
            blood_supply_status="adequate",
        )

        self._hospitals[hospital_id] = hospital
        return hospital

    def update_hospital_status(
        self,
        hospital_id: str,
        available_beds: Optional[int] = None,
        icu_available: Optional[int] = None,
        er_current: Optional[int] = None,
        ambulance_divert: Optional[bool] = None,
    ) -> Hospital:
        """Update hospital status."""
        hospital = self._hospitals.get(hospital_id)
        if not hospital:
            raise ValueError(f"Hospital {hospital_id} not found")

        if available_beds is not None:
            hospital.available_beds = available_beds
        if icu_available is not None:
            hospital.icu_available = icu_available
        if er_current is not None:
            hospital.er_current = er_current
        if ambulance_divert is not None:
            hospital.ambulance_divert = ambulance_divert

        hospital.status = self._calculate_status(hospital)
        hospital.last_updated = datetime.utcnow()

        return hospital

    def _calculate_status(self, hospital: Hospital) -> HospitalStatus:
        """Calculate hospital status based on capacity."""
        bed_utilization = 1 - (hospital.available_beds / hospital.total_beds)
        er_utilization = hospital.er_current / hospital.er_capacity if hospital.er_capacity > 0 else 0
        icu_utilization = 1 - (hospital.icu_available / hospital.icu_beds) if hospital.icu_beds > 0 else 0

        max_util = max(bed_utilization, er_utilization, icu_utilization)

        if hospital.ambulance_divert:
            return HospitalStatus.DIVERT
        elif max_util >= 0.95:
            return HospitalStatus.CRITICAL
        elif max_util >= 0.85:
            return HospitalStatus.SURGE
        elif max_util >= 0.75:
            return HospitalStatus.ELEVATED
        else:
            return HospitalStatus.NORMAL

    def predict_load(
        self,
        hospital_id: str,
        incident_type: str,
        estimated_casualties: int,
        hours_ahead: int = 24,
    ) -> HospitalLoadPrediction:
        """Predict hospital load for an incident."""
        prediction_id = f"pred-{uuid.uuid4().hex[:8]}"

        hospital = self._hospitals.get(hospital_id)
        if not hospital:
            raise ValueError(f"Hospital {hospital_id} not found")

        er_arrivals = self._estimate_er_arrivals(incident_type, estimated_casualties, hospital)
        admissions = int(er_arrivals * 0.4)
        icu_demand = int(er_arrivals * 0.15)

        predicted_status = self._predict_surge_level(hospital, er_arrivals, admissions, icu_demand)

        factors = self._identify_factors(incident_type, estimated_casualties)
        recommendations = self._generate_recommendations(hospital, predicted_status, er_arrivals)

        prediction = HospitalLoadPrediction(
            prediction_id=prediction_id,
            hospital_id=hospital_id,
            prediction_time=datetime.utcnow() + timedelta(hours=hours_ahead),
            predicted_er_arrivals=er_arrivals,
            predicted_admissions=admissions,
            predicted_icu_demand=icu_demand,
            predicted_surge_level=predicted_status,
            confidence_score=0.75,
            factors=factors,
            recommendations=recommendations,
        )

        self._predictions[prediction_id] = prediction
        return prediction

    def _estimate_er_arrivals(
        self,
        incident_type: str,
        casualties: int,
        hospital: Hospital,
    ) -> int:
        """Estimate ER arrivals based on incident."""
        type_factors = {
            "hurricane": 0.3,
            "flood": 0.25,
            "fire": 0.4,
            "earthquake": 0.5,
            "explosion": 0.6,
            "mass_casualty": 0.8,
        }

        factor = type_factors.get(incident_type.lower(), 0.3)
        trauma_factor = 1.0 + (0.1 * (5 - hospital.trauma_level))

        return int(casualties * factor * trauma_factor)

    def _predict_surge_level(
        self,
        hospital: Hospital,
        er_arrivals: int,
        admissions: int,
        icu_demand: int,
    ) -> HospitalStatus:
        """Predict surge level after incident."""
        projected_er = hospital.er_current + er_arrivals
        projected_beds = hospital.available_beds - admissions
        projected_icu = hospital.icu_available - icu_demand

        er_util = projected_er / hospital.er_capacity if hospital.er_capacity > 0 else 1
        bed_util = 1 - (projected_beds / hospital.total_beds) if projected_beds > 0 else 1
        icu_util = 1 - (projected_icu / hospital.icu_beds) if hospital.icu_beds > 0 and projected_icu > 0 else 1

        max_util = max(er_util, bed_util, icu_util)

        if max_util >= 1.0:
            return HospitalStatus.DIVERT
        elif max_util >= 0.95:
            return HospitalStatus.CRITICAL
        elif max_util >= 0.85:
            return HospitalStatus.SURGE
        elif max_util >= 0.75:
            return HospitalStatus.ELEVATED
        else:
            return HospitalStatus.NORMAL

    def _identify_factors(self, incident_type: str, casualties: int) -> List[str]:
        """Identify factors affecting prediction."""
        factors = [f"Incident type: {incident_type}", f"Estimated casualties: {casualties}"]

        if casualties > 100:
            factors.append("Mass casualty event")
        if incident_type.lower() in ["earthquake", "explosion"]:
            factors.append("High trauma probability")

        return factors

    def _generate_recommendations(
        self,
        hospital: Hospital,
        predicted_status: HospitalStatus,
        er_arrivals: int,
    ) -> List[str]:
        """Generate recommendations based on prediction."""
        recommendations = []

        if predicted_status in [HospitalStatus.CRITICAL, HospitalStatus.DIVERT]:
            recommendations.append("Activate surge capacity protocols")
            recommendations.append("Call in additional staff")
            recommendations.append("Consider diverting ambulances to other facilities")

        if predicted_status == HospitalStatus.SURGE:
            recommendations.append("Prepare surge areas")
            recommendations.append("Notify off-duty staff for potential callback")

        if er_arrivals > hospital.er_capacity:
            recommendations.append("Set up triage area outside ER")
            recommendations.append("Request mutual aid from nearby hospitals")

        return recommendations

    def get_hospital(self, hospital_id: str) -> Optional[Hospital]:
        """Get hospital by ID."""
        return self._hospitals.get(hospital_id)

    def get_hospitals(self, status: Optional[HospitalStatus] = None) -> List[Hospital]:
        """Get hospitals, optionally filtered by status."""
        hospitals = list(self._hospitals.values())
        if status:
            hospitals = [h for h in hospitals if h.status == status]
        return hospitals

    def get_prediction(self, prediction_id: str) -> Optional[HospitalLoadPrediction]:
        """Get prediction by ID."""
        return self._predictions.get(prediction_id)

    def get_regional_capacity(self) -> Dict[str, Any]:
        """Get regional hospital capacity summary."""
        hospitals = list(self._hospitals.values())
        return {
            "total_hospitals": len(hospitals),
            "total_beds": sum(h.total_beds for h in hospitals),
            "available_beds": sum(h.available_beds for h in hospitals),
            "total_icu": sum(h.icu_beds for h in hospitals),
            "available_icu": sum(h.icu_available for h in hospitals),
            "hospitals_on_divert": len([h for h in hospitals if h.ambulance_divert]),
            "by_status": {
                s.value: len([h for h in hospitals if h.status == s])
                for s in HospitalStatus
            },
        }


class EMSDemandForecaster:
    """
    Forecasts EMS demand during emergencies.
    """

    def __init__(self):
        self._units: Dict[str, EMSUnit] = {}
        self._forecasts: Dict[str, EMSDemandForecast] = {}

    def register_unit(
        self,
        unit_name: str,
        unit_type: str,
        current_location: Dict[str, float],
        crew_count: int,
        capabilities: Optional[List[str]] = None,
    ) -> EMSUnit:
        """Register an EMS unit."""
        unit_id = f"ems-{uuid.uuid4().hex[:8]}"

        unit = EMSUnit(
            unit_id=unit_id,
            unit_name=unit_name,
            unit_type=unit_type,
            status=EMSUnitStatus.AVAILABLE,
            current_location=current_location,
            assigned_call=None,
            crew_count=crew_count,
            capabilities=capabilities or [],
            equipment=[],
            last_dispatch=None,
            shift_end=None,
        )

        self._units[unit_id] = unit
        return unit

    def update_unit_status(
        self,
        unit_id: str,
        status: str,
        location: Optional[Dict[str, float]] = None,
    ) -> EMSUnit:
        """Update EMS unit status."""
        unit = self._units.get(unit_id)
        if not unit:
            raise ValueError(f"Unit {unit_id} not found")

        status_enum = EMSUnitStatus(status) if status in [s.value for s in EMSUnitStatus] else EMSUnitStatus.AVAILABLE
        unit.status = status_enum

        if location:
            unit.current_location = location

        return unit

    def forecast_demand(
        self,
        incident_type: str,
        affected_population: int,
        duration_hours: int,
    ) -> EMSDemandForecast:
        """Forecast EMS demand for an incident."""
        forecast_id = f"forecast-{uuid.uuid4().hex[:8]}"

        call_rate = self._calculate_call_rate(incident_type, affected_population)
        total_calls = int(call_rate * duration_hours)
        transports = int(total_calls * 0.7)
        als_calls = int(total_calls * 0.4)
        bls_calls = total_calls - als_calls

        peak_hours = self._identify_peak_hours(incident_type)
        hotspots = self._identify_hotspots(incident_type)
        staging = self._recommend_staging(hotspots)

        forecast = EMSDemandForecast(
            forecast_id=forecast_id,
            forecast_period_start=datetime.utcnow(),
            forecast_period_end=datetime.utcnow() + timedelta(hours=duration_hours),
            predicted_calls=total_calls,
            predicted_transports=transports,
            predicted_als_calls=als_calls,
            predicted_bls_calls=bls_calls,
            peak_hours=peak_hours,
            geographic_hotspots=hotspots,
            recommended_staging=staging,
            confidence_score=0.7,
        )

        self._forecasts[forecast_id] = forecast
        return forecast

    def _calculate_call_rate(self, incident_type: str, population: int) -> float:
        """Calculate expected call rate per hour."""
        base_rate = population / 10000

        type_multipliers = {
            "hurricane": 2.0,
            "flood": 1.5,
            "fire": 3.0,
            "earthquake": 4.0,
            "explosion": 5.0,
        }

        multiplier = type_multipliers.get(incident_type.lower(), 1.5)
        return base_rate * multiplier

    def _identify_peak_hours(self, incident_type: str) -> List[int]:
        """Identify expected peak hours for calls."""
        if incident_type.lower() in ["earthquake", "explosion"]:
            return [0, 1, 2, 3]
        elif incident_type.lower() == "hurricane":
            return [6, 7, 8, 18, 19, 20]
        else:
            return [8, 9, 10, 17, 18, 19]

    def _identify_hotspots(self, incident_type: str) -> List[Dict[str, Any]]:
        """Identify geographic hotspots for EMS demand."""
        return [
            {"location": {"lat": 33.749, "lng": -84.388}, "expected_calls": 50, "priority": "high"},
            {"location": {"lat": 33.755, "lng": -84.390}, "expected_calls": 30, "priority": "medium"},
        ]

    def _recommend_staging(self, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend staging locations based on hotspots."""
        staging = []
        for i, hotspot in enumerate(hotspots):
            staging.append({
                "staging_id": f"stage-{i+1}",
                "location": hotspot.get("location"),
                "recommended_units": 3 if hotspot.get("priority") == "high" else 2,
                "unit_types": ["ALS", "BLS"],
            })
        return staging

    def get_unit(self, unit_id: str) -> Optional[EMSUnit]:
        """Get EMS unit by ID."""
        return self._units.get(unit_id)

    def get_available_units(self) -> List[EMSUnit]:
        """Get available EMS units."""
        return [u for u in self._units.values() if u.status == EMSUnitStatus.AVAILABLE]

    def get_forecast(self, forecast_id: str) -> Optional[EMSDemandForecast]:
        """Get forecast by ID."""
        return self._forecasts.get(forecast_id)

    def get_metrics(self) -> Dict[str, Any]:
        """Get EMS metrics."""
        units = list(self._units.values())
        return {
            "total_units": len(units),
            "available_units": len(self.get_available_units()),
            "by_status": {
                s.value: len([u for u in units if u.status == s])
                for s in EMSUnitStatus
            },
        }


class TriagePriorityModel:
    """
    Models triage priority for mass casualty incidents.
    """

    def __init__(self):
        self._patients: Dict[str, TriagePatient] = {}
        self._incidents: Dict[str, MassCalsualtySummary] = {}

    def triage_patient(
        self,
        injury_type: str,
        injury_description: str,
        vital_signs: Dict[str, Any],
        age_group: str,
        location_found: Dict[str, Any],
    ) -> TriagePatient:
        """Triage a patient."""
        patient_id = f"patient-{uuid.uuid4().hex[:8]}"

        injury_enum = InjuryType(injury_type) if injury_type in [i.value for i in InjuryType] else InjuryType.TRAUMA
        triage_level = self._calculate_triage_level(vital_signs, injury_enum)

        patient = TriagePatient(
            patient_id=patient_id,
            triage_level=triage_level,
            injury_type=injury_enum,
            injury_description=injury_description,
            vital_signs=vital_signs,
            age_group=age_group,
            location_found=location_found,
            transport_status="pending",
            destination_hospital=None,
            triage_time=datetime.utcnow(),
            notes="",
        )

        self._patients[patient_id] = patient
        return patient

    def _calculate_triage_level(
        self,
        vital_signs: Dict[str, Any],
        injury_type: InjuryType,
    ) -> TriageLevel:
        """Calculate triage level using START algorithm."""
        respirations = vital_signs.get("respirations", 15)
        pulse = vital_signs.get("pulse", 80)
        mental_status = vital_signs.get("mental_status", "alert")
        breathing = vital_signs.get("breathing", True)

        if not breathing:
            return TriageLevel.EXPECTANT

        if respirations > 30 or respirations < 10:
            return TriageLevel.IMMEDIATE

        if pulse > 120 or pulse < 60:
            return TriageLevel.IMMEDIATE

        if mental_status.lower() not in ["alert", "responsive"]:
            return TriageLevel.IMMEDIATE

        if injury_type in [InjuryType.HEAD_INJURY, InjuryType.CRUSH, InjuryType.BURN]:
            return TriageLevel.DELAYED

        return TriageLevel.MINOR

    def update_patient_status(
        self,
        patient_id: str,
        transport_status: Optional[str] = None,
        destination_hospital: Optional[str] = None,
        triage_level: Optional[str] = None,
    ) -> TriagePatient:
        """Update patient status."""
        patient = self._patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        if transport_status:
            patient.transport_status = transport_status
        if destination_hospital:
            patient.destination_hospital = destination_hospital
        if triage_level:
            patient.triage_level = TriageLevel(triage_level)

        return patient

    def create_incident_summary(
        self,
        incident_type: str,
        location: Dict[str, Any],
    ) -> MassCalsualtySummary:
        """Create mass casualty incident summary."""
        incident_id = f"mci-{uuid.uuid4().hex[:8]}"

        patients = list(self._patients.values())

        by_triage = {level.value: 0 for level in TriageLevel}
        by_injury = {injury.value: 0 for injury in InjuryType}

        for patient in patients:
            by_triage[patient.triage_level.value] += 1
            by_injury[patient.injury_type.value] += 1

        transported = len([p for p in patients if p.transport_status == "transported"])
        pending = len([p for p in patients if p.transport_status == "pending"])
        deceased = by_triage.get("deceased", 0)

        hospitals = list(set(p.destination_hospital for p in patients if p.destination_hospital))

        summary = MassCalsualtySummary(
            incident_id=incident_id,
            incident_type=incident_type,
            location=location,
            total_patients=len(patients),
            by_triage_level=by_triage,
            by_injury_type=by_injury,
            transported=transported,
            pending_transport=pending,
            deceased=deceased,
            hospitals_receiving=hospitals,
        )

        self._incidents[incident_id] = summary
        return summary

    def get_patient(self, patient_id: str) -> Optional[TriagePatient]:
        """Get patient by ID."""
        return self._patients.get(patient_id)

    def get_patients(
        self,
        triage_level: Optional[TriageLevel] = None,
        transport_status: Optional[str] = None,
    ) -> List[TriagePatient]:
        """Get patients, optionally filtered."""
        patients = list(self._patients.values())
        if triage_level:
            patients = [p for p in patients if p.triage_level == triage_level]
        if transport_status:
            patients = [p for p in patients if p.transport_status == transport_status]
        return patients

    def get_immediate_patients(self) -> List[TriagePatient]:
        """Get patients requiring immediate care."""
        return self.get_patients(triage_level=TriageLevel.IMMEDIATE)

    def get_metrics(self) -> Dict[str, Any]:
        """Get triage metrics."""
        patients = list(self._patients.values())
        return {
            "total_patients": len(patients),
            "by_triage_level": {
                level.value: len([p for p in patients if p.triage_level == level])
                for level in TriageLevel
            },
            "pending_transport": len([p for p in patients if p.transport_status == "pending"]),
            "transported": len([p for p in patients if p.transport_status == "transported"]),
        }


class MedicalSupplyTracker:
    """
    Tracks medical supplies during emergencies.
    """

    def __init__(self):
        self._supplies: Dict[str, MedicalSupply] = {}

    def add_supply(
        self,
        name: str,
        category: str,
        quantity: int,
        unit: str,
        location: str,
        minimum_stock: int = 0,
        critical_threshold: int = 0,
    ) -> MedicalSupply:
        """Add medical supply to inventory."""
        supply_id = f"supply-{uuid.uuid4().hex[:8]}"

        cat_enum = MedicalSupplyCategory(category) if category in [c.value for c in MedicalSupplyCategory] else MedicalSupplyCategory.MEDICATIONS

        supply = MedicalSupply(
            supply_id=supply_id,
            name=name,
            category=cat_enum,
            quantity=quantity,
            unit=unit,
            location=location,
            expiration_date=None,
            minimum_stock=minimum_stock,
            critical_threshold=critical_threshold or int(minimum_stock * 0.5),
            supplier="",
            last_restocked=datetime.utcnow(),
        )

        self._supplies[supply_id] = supply
        return supply

    def update_quantity(self, supply_id: str, quantity: int) -> MedicalSupply:
        """Update supply quantity."""
        supply = self._supplies.get(supply_id)
        if not supply:
            raise ValueError(f"Supply {supply_id} not found")

        supply.quantity = quantity
        return supply

    def consume_supply(self, supply_id: str, amount: int) -> MedicalSupply:
        """Consume supply (reduce quantity)."""
        supply = self._supplies.get(supply_id)
        if not supply:
            raise ValueError(f"Supply {supply_id} not found")

        supply.quantity = max(0, supply.quantity - amount)
        return supply

    def get_supply(self, supply_id: str) -> Optional[MedicalSupply]:
        """Get supply by ID."""
        return self._supplies.get(supply_id)

    def get_supplies(self, category: Optional[MedicalSupplyCategory] = None) -> List[MedicalSupply]:
        """Get supplies, optionally filtered by category."""
        supplies = list(self._supplies.values())
        if category:
            supplies = [s for s in supplies if s.category == category]
        return supplies

    def get_critical_supplies(self) -> List[MedicalSupply]:
        """Get supplies below critical threshold."""
        return [s for s in self._supplies.values() if s.quantity <= s.critical_threshold]

    def get_low_stock_supplies(self) -> List[MedicalSupply]:
        """Get supplies below minimum stock."""
        return [s for s in self._supplies.values() if s.quantity <= s.minimum_stock]

    def get_metrics(self) -> Dict[str, Any]:
        """Get supply metrics."""
        supplies = list(self._supplies.values())
        return {
            "total_items": len(supplies),
            "critical_count": len(self.get_critical_supplies()),
            "low_stock_count": len(self.get_low_stock_supplies()),
            "by_category": {
                cat.value: len([s for s in supplies if s.category == cat])
                for cat in MedicalSupplyCategory
            },
        }


class MedicalSurgeManager:
    """
    Main medical surge coordinator.
    """

    def __init__(self):
        self.hospital_predictor = HospitalLoadPredictor()
        self.ems_forecaster = EMSDemandForecaster()
        self.triage_model = TriagePriorityModel()
        self.supply_tracker = MedicalSupplyTracker()

    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall medical surge metrics."""
        return {
            "hospitals": self.hospital_predictor.get_regional_capacity(),
            "ems": self.ems_forecaster.get_metrics(),
            "triage": self.triage_model.get_metrics(),
            "supplies": self.supply_tracker.get_metrics(),
        }

    def get_critical_status(self) -> Dict[str, Any]:
        """Get critical status summary."""
        return {
            "hospitals_on_divert": len([
                h for h in self.hospital_predictor.get_hospitals()
                if h.ambulance_divert
            ]),
            "immediate_patients": len(self.triage_model.get_immediate_patients()),
            "critical_supplies": len(self.supply_tracker.get_critical_supplies()),
            "available_ems_units": len(self.ems_forecaster.get_available_units()),
        }
