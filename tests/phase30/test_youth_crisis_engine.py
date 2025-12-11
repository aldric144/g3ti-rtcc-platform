"""
Phase 30: Youth Crisis Intelligence Engine Tests

Tests for:
- Youth risk assessment
- School incident clustering
- Gang exposure assessment
- Intervention planning
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestYouthCrisisEngine:
    """Tests for YouthCrisisEngine"""
    
    def test_engine_singleton(self):
        """Test that engine is a singleton"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine1 = YouthCrisisEngine()
        engine2 = YouthCrisisEngine()
        
        assert engine1 is engine2
    
    def test_engine_initialization(self):
        """Test engine initializes with correct agency config"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["city"] == "Riviera Beach"
    
    def test_youth_risk_level_enum(self):
        """Test YouthRiskLevel enum values"""
        from backend.app.human_intel.youth_crisis_engine import YouthRiskLevel
        
        assert YouthRiskLevel.MINIMAL.value == 1
        assert YouthRiskLevel.LOW.value == 2
        assert YouthRiskLevel.MODERATE.value == 3
        assert YouthRiskLevel.ELEVATED.value == 4
        assert YouthRiskLevel.HIGH.value == 5
        assert YouthRiskLevel.CRITICAL.value == 6
    
    def test_youth_risk_type_enum(self):
        """Test YouthRiskType enum values"""
        from backend.app.human_intel.youth_crisis_engine import YouthRiskType
        
        assert YouthRiskType.VIOLENCE_EXPOSURE.value == "violence_exposure"
        assert YouthRiskType.TRUANCY.value == "truancy"
        assert YouthRiskType.GANG_EXPOSURE.value == "gang_exposure"
    
    def test_school_incident_type_enum(self):
        """Test SchoolIncidentType enum values"""
        from backend.app.human_intel.youth_crisis_engine import SchoolIncidentType
        
        assert SchoolIncidentType.FIGHT.value == "fight"
        assert SchoolIncidentType.BULLYING.value == "bullying"
        assert SchoolIncidentType.WEAPON.value == "weapon"
    
    def test_intervention_type_enum(self):
        """Test InterventionType enum values"""
        from backend.app.human_intel.youth_crisis_engine import InterventionType
        
        assert InterventionType.SCHOOL_COUNSELOR.value == "school_counselor"
        assert InterventionType.YOUTH_MENTOR.value == "youth_mentor"
        assert InterventionType.GANG_INTERVENTION.value == "gang_intervention"
    
    def test_youth_risk_assessment_dataclass(self):
        """Test YouthRiskAssessment dataclass"""
        from backend.app.human_intel.youth_crisis_engine import (
            YouthRiskAssessment, YouthRiskLevel, YouthRiskType, InterventionType
        )
        
        assessment = YouthRiskAssessment(
            assessment_id="YRA-TEST001",
            timestamp=datetime.utcnow(),
            risk_level=YouthRiskLevel.ELEVATED,
            risk_types=[YouthRiskType.TRUANCY],
            confidence_score=0.75,
            risk_factors=["chronic_absences"],
            protective_factors=["engaged_parent_guardian"],
            school_zone="Zone_A",
            age_group="middle_school",
            recommended_interventions=[InterventionType.SCHOOL_COUNSELOR],
            urgency="URGENT",
            anonymization_level="FULL",
            privacy_protections=["No individual identification"],
            data_sources_used=["aggregated_school_data"],
        )
        
        assert assessment.assessment_id == "YRA-TEST001"
        assert assessment.risk_level == YouthRiskLevel.ELEVATED
    
    def test_school_incident_cluster_dataclass(self):
        """Test SchoolIncidentCluster dataclass"""
        from backend.app.human_intel.youth_crisis_engine import (
            SchoolIncidentCluster, SchoolIncidentType
        )
        
        cluster = SchoolIncidentCluster(
            cluster_id="SIC-TEST001",
            timestamp=datetime.utcnow(),
            school_zone="Zone_A",
            incident_types=[SchoolIncidentType.FIGHT],
            incident_count=5,
            time_span_days=30,
            severity_trend="increasing",
            affected_grade_levels=["middle_school"],
            peer_group_involvement=True,
            recommended_actions=["Coordinate with school"],
            school_notification_required=True,
            anonymization_level="AGGREGATED",
            privacy_protections=["No student identification"],
        )
        
        assert cluster.cluster_id == "SIC-TEST001"
        assert cluster.incident_count == 5
    
    def test_gang_exposure_risk_dataclass(self):
        """Test GangExposureRisk dataclass"""
        from backend.app.human_intel.youth_crisis_engine import (
            GangExposureRisk, YouthRiskLevel, InterventionType
        )
        
        risk = GangExposureRisk(
            risk_id="GER-TEST001",
            timestamp=datetime.utcnow(),
            zone="Zone_C",
            exposure_level=YouthRiskLevel.HIGH,
            risk_indicators=["gang_activity_in_area"],
            protective_factors=["community_program_participation"],
            gang_activity_proximity="within_zone",
            recruitment_risk="HIGH",
            recommended_interventions=[InterventionType.GANG_INTERVENTION],
            community_resources=["Youth mentorship programs"],
            anonymization_level="ZONE_LEVEL",
            privacy_protections=["No individual identification"],
        )
        
        assert risk.risk_id == "GER-TEST001"
        assert risk.exposure_level == YouthRiskLevel.HIGH


class TestYouthRiskAssessment:
    """Tests for youth risk assessment functionality"""
    
    def test_assess_youth_risk_minimal(self):
        """Test minimal risk assessment"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine, YouthRiskLevel
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_B",
            age_group="elementary",
            protective_factors=["engaged_parent_guardian", "positive_school_connection"],
        )
        
        assert assessment is not None
        assert assessment.risk_level in [YouthRiskLevel.MINIMAL, YouthRiskLevel.LOW]
    
    def test_assess_youth_risk_elevated(self):
        """Test elevated risk assessment"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine, YouthRiskLevel
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
            incident_history=["prior_violent_incident"],
            truancy_indicators=["chronic_absences", "declining_grades"],
        )
        
        assert assessment is not None
        assert assessment.risk_level.value >= YouthRiskLevel.MODERATE.value
    
    def test_assess_youth_risk_high(self):
        """Test high risk assessment"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine, YouthRiskLevel
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_C",
            age_group="high_school",
            incident_history=["prior_violent_incident", "weapon_access"],
            truancy_indicators=["chronic_absences"],
            family_factors=["instability"],
            peer_factors=["gang_involvement"],
        )
        
        assert assessment is not None
        assert assessment.risk_level.value >= YouthRiskLevel.ELEVATED.value
    
    def test_assess_youth_risk_ferpa_protections(self):
        """Test that FERPA protections are applied"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
        )
        
        assert assessment is not None
        assert "FERPA protections applied" in assessment.privacy_protections
        assert "No individual identification" in assessment.privacy_protections


class TestSchoolIncidentAnalysis:
    """Tests for school incident analysis"""
    
    def test_analyze_school_incidents(self):
        """Test school incident analysis"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        cluster = engine.analyze_school_incidents(
            school_zone="Zone_A",
            time_window_days=30,
        )
        
        assert cluster is not None
        assert cluster.school_zone == "Zone_A"
        assert cluster.incident_count >= 0
    
    def test_school_incident_notification(self):
        """Test school notification requirement"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        cluster = engine.analyze_school_incidents(
            school_zone="Zone_A",
            time_window_days=30,
        )
        
        assert cluster is not None
        if cluster.incident_count >= 3:
            assert cluster.school_notification_required == True


class TestGangExposureAssessment:
    """Tests for gang exposure assessment"""
    
    def test_assess_gang_exposure_low(self):
        """Test low gang exposure assessment"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine, YouthRiskLevel
        
        engine = YouthCrisisEngine()
        
        risk = engine.assess_gang_exposure(
            zone="Zone_B",
            gang_activity_level="low",
        )
        
        assert risk is not None
        assert risk.exposure_level == YouthRiskLevel.LOW
    
    def test_assess_gang_exposure_high(self):
        """Test high gang exposure assessment"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine, YouthRiskLevel
        
        engine = YouthCrisisEngine()
        
        risk = engine.assess_gang_exposure(
            zone="Zone_C",
            gang_activity_level="high",
            community_factors=["gang_activity_in_area", "peer_gang_involvement"],
        )
        
        assert risk is not None
        assert risk.exposure_level == YouthRiskLevel.HIGH
        assert risk.recruitment_risk in ["HIGH", "MODERATE"]
    
    def test_gang_exposure_no_individual_profiling(self):
        """Test that no individual profiling is done"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        risk = engine.assess_gang_exposure(
            zone="Zone_C",
            gang_activity_level="high",
        )
        
        assert risk is not None
        assert "No individual identification" in risk.privacy_protections
        assert "No predictive policing on individuals" in risk.privacy_protections


class TestInterventionPlanning:
    """Tests for intervention planning"""
    
    def test_create_intervention_plan(self):
        """Test intervention plan creation"""
        from backend.app.human_intel.youth_crisis_engine import (
            YouthCrisisEngine, YouthRiskLevel, YouthRiskType, InterventionType
        )
        from backend.app.human_intel.youth_crisis_engine import YouthRiskAssessment
        
        engine = YouthCrisisEngine()
        
        assessment = engine.assess_youth_risk(
            school_zone="Zone_A",
            age_group="middle_school",
            truancy_indicators=["chronic_absences"],
        )
        
        plan = engine.create_intervention_plan(assessment)
        
        assert plan is not None
        assert plan.primary_intervention is not None
    
    def test_get_youth_stability_map(self):
        """Test youth stability map"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        
        stability_map = engine.get_youth_stability_map()
        
        assert stability_map is not None
        assert "zones" in stability_map
        assert "overall_stability" in stability_map
    
    def test_get_statistics(self):
        """Test get_statistics method"""
        from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
        
        engine = YouthCrisisEngine()
        stats = engine.get_statistics()
        
        assert "total_risk_assessments" in stats
        assert "total_incident_clusters" in stats
        assert "agency" in stats
