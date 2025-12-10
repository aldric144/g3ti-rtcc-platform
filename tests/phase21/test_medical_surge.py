"""
Phase 21: Medical Surge AI Tests

Tests for hospital load prediction, EMS demand forecasting,
mass casualty triage, and medical supply tracking.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.medical_surge_ai import (
    HospitalLoadPredictor,
    EMSDemandForecaster,
    MassCasualtyTriageModel,
    MedicalSupplyTracker,
    MedicalSurgeManager,
    HospitalStatus,
    TriageLevel,
    TransportStatus,
)


class TestHospitalLoadPredictor:
    """Tests for HospitalLoadPredictor class."""

    def test_predictor_initialization(self):
        """Test HospitalLoadPredictor initializes correctly."""
        predictor = HospitalLoadPredictor()
        assert predictor is not None
        assert hasattr(predictor, '_hospitals')

    def test_register_hospital(self):
        """Test registering a hospital."""
        predictor = HospitalLoadPredictor()
        hospital = predictor.register_hospital(
            name="Miami General Hospital",
            total_beds=500,
            icu_beds=50,
            er_capacity=100,
            trauma_level=1,
        )
        
        assert hospital is not None
        assert hospital.name == "Miami General Hospital"
        assert hospital.total_beds == 500
        assert hospital.trauma_level == 1

    def test_update_hospital_status(self):
        """Test updating hospital status."""
        predictor = HospitalLoadPredictor()
        hospital = predictor.register_hospital(
            name="County Medical Center",
            total_beds=300,
            icu_beds=30,
            er_capacity=60,
        )
        
        updated = predictor.update_status(
            hospital.hospital_id,
            available_beds=250,
            icu_available=25,
            er_current=40,
        )
        
        assert updated is not None
        assert updated.available_beds == 250

    def test_predict_load(self):
        """Test hospital load prediction."""
        predictor = HospitalLoadPredictor()
        hospital = predictor.register_hospital(
            name="Regional Hospital",
            total_beds=400,
            icu_beds=40,
            er_capacity=80,
        )
        
        prediction = predictor.predict_load(
            hospital.hospital_id,
            incident_type="mass_casualty",
            estimated_casualties=50,
            hours_ahead=6,
        )
        
        assert prediction is not None
        assert hasattr(prediction, 'predicted_bed_usage')
        assert hasattr(prediction, 'predicted_icu_usage')

    def test_set_ambulance_divert(self):
        """Test setting ambulance divert status."""
        predictor = HospitalLoadPredictor()
        hospital = predictor.register_hospital(
            name="City Hospital",
            total_beds=200,
            icu_beds=20,
            er_capacity=40,
        )
        
        updated = predictor.set_ambulance_divert(hospital.hospital_id, True)
        assert updated is not None
        assert updated.ambulance_divert is True

    def test_get_available_hospitals(self):
        """Test getting available hospitals."""
        predictor = HospitalLoadPredictor()
        predictor.register_hospital(
            name="Available Hospital",
            total_beds=300,
            icu_beds=30,
            er_capacity=60,
        )
        
        available = predictor.get_available_hospitals()
        assert len(available) >= 1


class TestEMSDemandForecaster:
    """Tests for EMSDemandForecaster class."""

    def test_forecaster_initialization(self):
        """Test EMSDemandForecaster initializes correctly."""
        forecaster = EMSDemandForecaster()
        assert forecaster is not None
        assert hasattr(forecaster, '_ems_units')

    def test_register_ems_unit(self):
        """Test registering an EMS unit."""
        forecaster = EMSDemandForecaster()
        unit = forecaster.register_unit(
            unit_id="EMS-001",
            unit_type="als",
            station="Station 1",
            crew_size=2,
        )
        
        assert unit is not None
        assert unit.unit_type == "als"

    def test_update_unit_status(self):
        """Test updating EMS unit status."""
        forecaster = EMSDemandForecaster()
        unit = forecaster.register_unit(
            unit_id="EMS-002",
            unit_type="bls",
            station="Station 2",
        )
        
        updated = forecaster.update_unit_status(unit.unit_id, "on_call")
        assert updated is not None

    def test_forecast_demand(self):
        """Test EMS demand forecasting."""
        forecaster = EMSDemandForecaster()
        forecast = forecaster.forecast_demand(
            incident_type="hurricane",
            affected_population=100000,
            hours_ahead=12,
        )
        
        assert forecast is not None
        assert hasattr(forecast, 'predicted_calls')
        assert hasattr(forecast, 'recommended_units')

    def test_get_available_units(self):
        """Test getting available EMS units."""
        forecaster = EMSDemandForecaster()
        forecaster.register_unit(
            unit_id="EMS-003",
            unit_type="als",
            station="Station 3",
        )
        
        available = forecaster.get_available_units()
        assert len(available) >= 1


class TestMassCasualtyTriageModel:
    """Tests for MassCasualtyTriageModel class."""

    def test_model_initialization(self):
        """Test MassCasualtyTriageModel initializes correctly."""
        model = MassCasualtyTriageModel()
        assert model is not None
        assert hasattr(model, '_patients')

    def test_triage_patient(self):
        """Test triaging a patient."""
        model = MassCasualtyTriageModel()
        patient = model.triage_patient(
            injury_type="trauma",
            breathing=True,
            respiratory_rate=25,
            pulse_present=True,
            mental_status="confused",
            location_found={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert patient is not None
        assert patient.triage_level in [
            TriageLevel.IMMEDIATE,
            TriageLevel.DELAYED,
            TriageLevel.MINOR,
            TriageLevel.EXPECTANT,
            TriageLevel.DECEASED,
        ]

    def test_triage_immediate(self):
        """Test immediate triage classification."""
        model = MassCasualtyTriageModel()
        patient = model.triage_patient(
            injury_type="severe_bleeding",
            breathing=True,
            respiratory_rate=35,
            pulse_present=True,
            mental_status="unresponsive",
            location_found={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert patient.triage_level == TriageLevel.IMMEDIATE

    def test_triage_deceased(self):
        """Test deceased triage classification."""
        model = MassCasualtyTriageModel()
        patient = model.triage_patient(
            injury_type="unknown",
            breathing=False,
            respiratory_rate=0,
            pulse_present=False,
            mental_status="unresponsive",
            location_found={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert patient.triage_level == TriageLevel.DECEASED

    def test_update_transport_status(self):
        """Test updating patient transport status."""
        model = MassCasualtyTriageModel()
        patient = model.triage_patient(
            injury_type="fracture",
            breathing=True,
            respiratory_rate=18,
            pulse_present=True,
            mental_status="alert",
            location_found={"lat": 25.7617, "lng": -80.1918},
        )
        
        updated = model.update_transport_status(
            patient.patient_id,
            TransportStatus.EN_ROUTE,
            destination_hospital="hosp-001",
        )
        
        assert updated is not None

    def test_get_patients_by_triage_level(self):
        """Test getting patients by triage level."""
        model = MassCasualtyTriageModel()
        model.triage_patient(
            injury_type="burns",
            breathing=True,
            respiratory_rate=30,
            pulse_present=True,
            mental_status="confused",
            location_found={"lat": 25.7617, "lng": -80.1918},
        )
        
        immediate = model.get_patients_by_level(TriageLevel.IMMEDIATE)
        assert isinstance(immediate, list)


class TestMedicalSupplyTracker:
    """Tests for MedicalSupplyTracker class."""

    def test_tracker_initialization(self):
        """Test MedicalSupplyTracker initializes correctly."""
        tracker = MedicalSupplyTracker()
        assert tracker is not None
        assert hasattr(tracker, '_supplies')

    def test_track_supply(self):
        """Test tracking a medical supply."""
        tracker = MedicalSupplyTracker()
        supply = tracker.track_supply(
            name="Blood Type O-",
            category="blood",
            quantity=100,
            unit="units",
            location="Blood Bank A",
            minimum_stock=50,
            expiration_date=datetime(2025, 12, 31),
        )
        
        assert supply is not None
        assert supply.name == "Blood Type O-"
        assert supply.quantity == 100

    def test_update_quantity(self):
        """Test updating supply quantity."""
        tracker = MedicalSupplyTracker()
        supply = tracker.track_supply(
            name="IV Fluids",
            category="fluids",
            quantity=500,
            unit="bags",
            location="Hospital Storage",
            minimum_stock=200,
        )
        
        updated = tracker.update_quantity(supply.item_id, 450)
        assert updated is not None
        assert updated.quantity == 450

    def test_get_critical_supplies(self):
        """Test getting critical supplies."""
        tracker = MedicalSupplyTracker()
        tracker.track_supply(
            name="Morphine",
            category="medication",
            quantity=10,
            unit="vials",
            location="Pharmacy",
            minimum_stock=50,
        )
        
        critical = tracker.get_critical_supplies()
        assert len(critical) >= 1

    def test_request_resupply(self):
        """Test requesting resupply."""
        tracker = MedicalSupplyTracker()
        supply = tracker.track_supply(
            name="Bandages",
            category="supplies",
            quantity=100,
            unit="boxes",
            location="Supply Room",
            minimum_stock=200,
        )
        
        request = tracker.request_resupply(supply.item_id, quantity=500)
        assert request is not None


class TestMedicalSurgeManager:
    """Tests for MedicalSurgeManager class."""

    def test_manager_initialization(self):
        """Test MedicalSurgeManager initializes correctly."""
        manager = MedicalSurgeManager()
        assert manager is not None
        assert hasattr(manager, 'hospital_predictor')
        assert hasattr(manager, 'ems_forecaster')
        assert hasattr(manager, 'triage_model')
        assert hasattr(manager, 'supply_tracker')

    def test_get_medical_metrics(self):
        """Test getting medical metrics."""
        manager = MedicalSurgeManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert "hospitals" in metrics
        assert "ems" in metrics
        assert "triage" in metrics
        assert "supplies" in metrics

    def test_get_critical_status(self):
        """Test getting critical status."""
        manager = MedicalSurgeManager()
        status = manager.get_critical_status()
        
        assert status is not None
        assert "hospitals_on_divert" in status
        assert "icu_beds_available" in status
        assert "immediate_patients" in status
        assert "critical_supplies" in status

    def test_coordinate_medical_response(self):
        """Test coordinating medical response."""
        manager = MedicalSurgeManager()
        result = manager.coordinate_response(
            incident_id="incident-001",
            estimated_casualties=100,
            incident_location={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert result is not None
