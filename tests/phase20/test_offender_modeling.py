"""
Phase 20: Offender Modeling Tests

Tests for BehavioralSignatureEngine, OffenderPredictionModel,
ModusOperandiClusterer, and UnknownSuspectProfiler.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.offender_modeling import (
    BehavioralSignatureEngine,
    OffenderPredictionModel,
    ModusOperandiClusterer,
    UnknownSuspectProfiler,
    SignatureCategory,
    OffenseType,
    RiskLevel,
    ProfileConfidence,
)


class TestBehavioralSignatureEngine:
    def setup_method(self):
        self.engine = BehavioralSignatureEngine()

    def test_analyze_case(self):
        case_data = {
            "offense_type": "burglary",
            "entry_method": "forced_rear",
            "weapon_used": "knife",
            "time_of_day": "night",
            "target_type": "residential",
            "items_taken": ["jewelry", "electronics"],
            "forensic_awareness": True,
        }
        signatures = self.engine.analyze_case(
            case_id="case-001",
            case_data=case_data,
        )
        assert len(signatures) > 0
        assert all(s.case_id == "case-001" for s in signatures)

    def test_get_signature(self):
        case_data = {"offense_type": "robbery"}
        signatures = self.engine.analyze_case(
            case_id="case-002",
            case_data=case_data,
        )
        if signatures:
            retrieved = self.engine.get_signature(signatures[0].signature_id)
            assert retrieved is not None

    def test_find_similar_signatures(self):
        case_data = {"offense_type": "assault", "weapon_used": "blunt_object"}
        signatures = self.engine.analyze_case(
            case_id="case-003",
            case_data=case_data,
        )
        if signatures:
            similar = self.engine.find_similar_signatures(
                signatures[0].signature_id,
                threshold=0.3,
            )
            assert isinstance(similar, list)

    def test_link_cases_by_signature(self):
        case_data = {"offense_type": "burglary"}
        signatures = self.engine.analyze_case(
            case_id="case-004",
            case_data=case_data,
        )
        if signatures:
            linked = self.engine.link_cases_by_signature(
                signatures[0].signature_id,
                threshold=0.5,
            )
            assert isinstance(linked, list)

    def test_get_metrics(self):
        metrics = self.engine.get_metrics()
        assert "total_signatures" in metrics
        assert "by_category" in metrics


class TestOffenderPredictionModel:
    def setup_method(self):
        self.signature_engine = BehavioralSignatureEngine()
        self.model = OffenderPredictionModel(self.signature_engine)

    def test_predict_next_offense_by_offender(self):
        prediction = self.model.predict_next_offense(offender_id="offender-001")
        assert prediction is not None
        assert prediction.offender_id == "offender-001"

    def test_predict_next_offense_by_signature(self):
        case_data = {"offense_type": "burglary", "repeat_offender": True}
        signatures = self.signature_engine.analyze_case(
            case_id="case-001",
            case_data=case_data,
        )
        if signatures:
            prediction = self.model.predict_next_offense(
                signature_id=signatures[0].signature_id
            )
            assert prediction is not None

    def test_get_prediction(self):
        prediction = self.model.predict_next_offense(offender_id="offender-002")
        retrieved = self.model.get_prediction(prediction.prediction_id)
        assert retrieved is not None
        assert retrieved.prediction_id == prediction.prediction_id

    def test_get_high_risk_predictions(self):
        self.model.predict_next_offense(offender_id="offender-003")
        high_risk = self.model.get_high_risk_predictions()
        assert isinstance(high_risk, list)

    def test_prediction_has_required_fields(self):
        prediction = self.model.predict_next_offense(offender_id="offender-004")
        assert hasattr(prediction, "predicted_offense_type")
        assert hasattr(prediction, "predicted_location")
        assert hasattr(prediction, "predicted_timeframe")
        assert hasattr(prediction, "risk_level")
        assert hasattr(prediction, "confidence_score")


class TestModusOperandiClusterer:
    def setup_method(self):
        self.signature_engine = BehavioralSignatureEngine()
        self.clusterer = ModusOperandiClusterer(self.signature_engine)

    def test_cluster_cases(self):
        case_ids = ["case-001", "case-002", "case-003"]
        clusters = self.clusterer.cluster_cases(
            case_ids=case_ids,
            offense_type=OffenseType.BURGLARY,
            similarity_threshold=0.5,
        )
        assert isinstance(clusters, list)

    def test_get_cluster(self):
        case_ids = ["case-004", "case-005"]
        clusters = self.clusterer.cluster_cases(
            case_ids=case_ids,
            offense_type=OffenseType.ROBBERY,
        )
        if clusters:
            retrieved = self.clusterer.get_cluster(clusters[0].cluster_id)
            assert retrieved is not None

    def test_get_clusters_by_offense_type(self):
        self.clusterer.cluster_cases(
            case_ids=["case-006"],
            offense_type=OffenseType.ASSAULT,
        )
        clusters = self.clusterer.get_clusters(offense_type=OffenseType.ASSAULT)
        assert isinstance(clusters, list)

    def test_cluster_has_common_behaviors(self):
        clusters = self.clusterer.cluster_cases(
            case_ids=["case-007", "case-008"],
            offense_type=OffenseType.BURGLARY,
        )
        if clusters:
            assert hasattr(clusters[0], "common_behaviors")


class TestUnknownSuspectProfiler:
    def setup_method(self):
        self.signature_engine = BehavioralSignatureEngine()
        self.profiler = UnknownSuspectProfiler(self.signature_engine)

    def test_generate_profile(self):
        case_data = [
            {"offense_type": "burglary", "time_of_day": "night"},
            {"offense_type": "burglary", "time_of_day": "night"},
        ]
        profile = self.profiler.generate_profile(
            case_ids=["case-001", "case-002"],
            case_data=case_data,
        )
        assert profile is not None
        assert len(profile.case_ids) == 2

    def test_get_profile(self):
        case_data = [{"offense_type": "robbery"}]
        profile = self.profiler.generate_profile(
            case_ids=["case-003"],
            case_data=case_data,
        )
        retrieved = self.profiler.get_profile(profile.profile_id)
        assert retrieved is not None
        assert retrieved.profile_id == profile.profile_id

    def test_profile_has_demographics(self):
        case_data = [{"offense_type": "assault"}]
        profile = self.profiler.generate_profile(
            case_ids=["case-004"],
            case_data=case_data,
        )
        assert hasattr(profile, "demographics")
        assert "age_range" in profile.demographics

    def test_profile_has_psychological_traits(self):
        case_data = [{"offense_type": "homicide"}]
        profile = self.profiler.generate_profile(
            case_ids=["case-005"],
            case_data=case_data,
        )
        assert hasattr(profile, "psychological_traits")
        assert isinstance(profile.psychological_traits, list)

    def test_profile_has_behavioral_indicators(self):
        case_data = [{"offense_type": "sexual_assault"}]
        profile = self.profiler.generate_profile(
            case_ids=["case-006"],
            case_data=case_data,
        )
        assert hasattr(profile, "behavioral_indicators")
        assert isinstance(profile.behavioral_indicators, list)

    def test_profile_has_geographic_profile(self):
        case_data = [{"offense_type": "burglary", "location": {"lat": 33.749, "lng": -84.388}}]
        profile = self.profiler.generate_profile(
            case_ids=["case-007"],
            case_data=case_data,
        )
        assert hasattr(profile, "geographic_profile")

    def test_get_profiles_by_confidence(self):
        case_data = [{"offense_type": "robbery"}]
        self.profiler.generate_profile(
            case_ids=["case-008"],
            case_data=case_data,
        )
        profiles = self.profiler.get_profiles(confidence=ProfileConfidence.MODERATE)
        assert isinstance(profiles, list)
