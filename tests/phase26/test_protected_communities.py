"""
Test Suite 3: Protected Community Safeguards Tests
Tests for protected class safeguards
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.protected_communities import (
    get_protected_community_safeguards,
    ProtectedCommunitySafeguards,
    CommunityType,
    SafeguardLevel,
)


class TestProtectedCommunitySafeguards:
    """Tests for ProtectedCommunitySafeguards"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_singleton_pattern(self):
        """Test that safeguards follows singleton pattern"""
        safeguards1 = get_protected_community_safeguards()
        safeguards2 = get_protected_community_safeguards()
        assert safeguards1 is safeguards2

    def test_community_types_defined(self):
        """Test that all community types are defined"""
        expected_types = [
            CommunityType.BLACK_COMMUNITY,
            CommunityType.HISPANIC_COMMUNITY,
            CommunityType.LGBTQ_YOUTH,
            CommunityType.PEOPLE_WITH_DISABILITIES,
            CommunityType.VETERANS,
            CommunityType.FAITH_COMMUNITIES,
            CommunityType.AGING_POPULATION,
        ]
        for community_type in expected_types:
            assert community_type in self.safeguards.community_profiles


class TestRivieraBeachCommunityProfiles:
    """Tests for Riviera Beach community profiles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_black_community_profile(self):
        """Test Black community profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.BLACK_COMMUNITY]
        assert profile["population_estimate"] == 25056
        assert profile["population_percentage"] == 66.0
        assert profile["safeguard_level"] == SafeguardLevel.HIGH
        assert profile["bias_sensitivity_multiplier"] == 1.5

    def test_hispanic_community_profile(self):
        """Test Hispanic community profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.HISPANIC_COMMUNITY]
        assert profile["population_estimate"] == 3037
        assert profile["population_percentage"] == 8.0
        assert profile["safeguard_level"] == SafeguardLevel.ELEVATED
        assert profile["bias_sensitivity_multiplier"] == 1.3

    def test_lgbtq_youth_profile(self):
        """Test LGBTQ+ Youth profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.LGBTQ_YOUTH]
        assert profile["safeguard_level"] == SafeguardLevel.HIGH
        assert profile["bias_sensitivity_multiplier"] == 1.5

    def test_disabilities_profile(self):
        """Test People with Disabilities profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.PEOPLE_WITH_DISABILITIES]
        assert profile["population_estimate"] == 4556
        assert profile["population_percentage"] == 12.0
        assert profile["safeguard_level"] == SafeguardLevel.HIGH

    def test_veterans_profile(self):
        """Test Veterans profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.VETERANS]
        assert profile["population_estimate"] == 2278
        assert profile["population_percentage"] == 6.0
        assert profile["safeguard_level"] == SafeguardLevel.ELEVATED

    def test_faith_communities_profile(self):
        """Test Faith Communities profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.FAITH_COMMUNITIES]
        assert profile["population_estimate"] == 20000
        assert profile["safeguard_level"] == SafeguardLevel.ELEVATED

    def test_aging_population_profile(self):
        """Test Aging Population profile is correctly configured"""
        profile = self.safeguards.community_profiles[CommunityType.AGING_POPULATION]
        assert profile["population_estimate"] == 5695
        assert profile["population_percentage"] == 15.0
        assert profile["safeguard_level"] == SafeguardLevel.ELEVATED


class TestSafeguardRules:
    """Tests for safeguard rules"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_safeguard_rules_defined(self):
        """Test that safeguard rules are defined"""
        assert len(self.safeguards.safeguard_rules) >= 8

    def test_disparate_impact_rule(self):
        """Test disparate impact review rule exists"""
        rule_names = [r.name for r in self.safeguards.safeguard_rules]
        assert any("disparate" in name.lower() for name in rule_names)

    def test_over_surveillance_rule(self):
        """Test over-surveillance prevention rule exists"""
        rule_names = [r.name for r in self.safeguards.safeguard_rules]
        assert any("surveillance" in name.lower() for name in rule_names)


class TestSafeguardChecks:
    """Tests for safeguard check functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_check_safeguards_black_community(self):
        """Test safeguard check for Black community"""
        context = {
            "affected_communities": [CommunityType.BLACK_COMMUNITY],
            "disparate_impact_ratio": 0.75,
        }
        result = self.safeguards.check_safeguards("test-001", "enforcement", context)
        assert result is not None
        assert len(result.triggered_rules) > 0

    def test_check_safeguards_lgbtq_youth(self):
        """Test safeguard check for LGBTQ+ Youth"""
        context = {
            "affected_communities": [CommunityType.LGBTQ_YOUTH],
            "involves_minor": True,
        }
        result = self.safeguards.check_safeguards("test-002", "enforcement", context)
        assert result is not None

    def test_check_safeguards_disabilities(self):
        """Test safeguard check for People with Disabilities"""
        context = {
            "affected_communities": [CommunityType.PEOPLE_WITH_DISABILITIES],
            "ada_accommodation_needed": True,
        }
        result = self.safeguards.check_safeguards("test-003", "enforcement", context)
        assert result is not None

    def test_check_safeguards_no_trigger(self):
        """Test safeguard check with no triggers"""
        context = {
            "affected_communities": [],
            "disparate_impact_ratio": 0.95,
        }
        result = self.safeguards.check_safeguards("test-004", "patrol", context)
        assert result is not None
        assert len(result.triggered_rules) == 0


class TestCommunityImpactAssessment:
    """Tests for community impact assessment"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_assess_community_impact(self):
        """Test community impact assessment"""
        context = {
            "location": "Downtown",
            "action_scope": "area_wide",
        }
        result = self.safeguards.assess_community_impact("enforcement", context)
        assert result is not None
        assert hasattr(result, "impact_score")
        assert hasattr(result, "affected_communities")

    def test_impact_score_range(self):
        """Test impact score is within valid range"""
        context = {
            "location": "Singer Island",
            "action_scope": "targeted",
        }
        result = self.safeguards.assess_community_impact("surveillance", context)
        assert 0.0 <= result.impact_score <= 1.0


class TestBiasSensitivityMultipliers:
    """Tests for bias sensitivity multipliers"""

    def setup_method(self):
        """Setup test fixtures"""
        self.safeguards = get_protected_community_safeguards()

    def test_high_safeguard_multiplier(self):
        """Test HIGH safeguard level has 1.5x multiplier"""
        profile = self.safeguards.community_profiles[CommunityType.BLACK_COMMUNITY]
        assert profile["bias_sensitivity_multiplier"] == 1.5

    def test_elevated_safeguard_multiplier(self):
        """Test ELEVATED safeguard level has 1.2-1.3x multiplier"""
        profile = self.safeguards.community_profiles[CommunityType.VETERANS]
        assert 1.2 <= profile["bias_sensitivity_multiplier"] <= 1.3

    def test_surveillance_limit_factors(self):
        """Test surveillance limit factors are defined"""
        for community_type, profile in self.safeguards.community_profiles.items():
            assert "surveillance_limit_factor" in profile
            assert 0.0 < profile["surveillance_limit_factor"] <= 1.0
