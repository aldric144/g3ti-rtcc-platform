"""
Phase 31: Communication Intelligence Engine Tests
"""

import pytest
from datetime import datetime
from backend.app.emergency_ai.communication_intel_engine import (
    CommunicationIntelEngine,
    AlertType,
    AlertPriority,
    Language,
    DistributionChannel,
    SignalType,
    EmergencyAlert,
    MultilingualMessage,
    SocialSignal,
    RumorDebunk,
)


class TestCommunicationIntelEngine:
    """Test suite for CommunicationIntelEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = CommunicationIntelEngine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = CommunicationIntelEngine()
        engine2 = CommunicationIntelEngine()
        assert engine1 is engine2

    def test_agency_config(self):
        """Test agency configuration"""
        assert self.engine.agency_config["ori"] == "FL0500400"
        assert self.engine.agency_config["city"] == "Riviera Beach"

    def test_zone_populations(self):
        """Test zone population data"""
        assert self.engine.zone_populations["Zone_A"] == 3500
        assert self.engine.zone_populations["Zone_E"] == 4500

    def test_alert_templates(self):
        """Test alert templates configuration"""
        assert AlertType.EVACUATION_ORDER in self.engine.alert_templates
        assert Language.ENGLISH in self.engine.alert_templates[AlertType.EVACUATION_ORDER]
        assert Language.SPANISH in self.engine.alert_templates[AlertType.EVACUATION_ORDER]
        assert Language.HAITIAN_CREOLE in self.engine.alert_templates[AlertType.EVACUATION_ORDER]

    def test_crisis_keywords(self):
        """Test crisis keywords configuration"""
        assert Language.ENGLISH in self.engine.crisis_keywords
        assert "help" in self.engine.crisis_keywords[Language.ENGLISH]
        assert "ayuda" in self.engine.crisis_keywords[Language.SPANISH]
        assert "ede" in self.engine.crisis_keywords[Language.HAITIAN_CREOLE]

    def test_create_emergency_alert(self):
        """Test emergency alert creation"""
        alert = self.engine.create_emergency_alert(
            alert_type=AlertType.EVACUATION_ORDER,
            priority=AlertPriority.EMERGENCY,
            affected_zones=["Zone_A", "Zone_B"],
        )
        
        assert alert is not None
        assert alert.alert_id.startswith("EA-")
        assert alert.alert_type == AlertType.EVACUATION_ORDER
        assert alert.priority == AlertPriority.EMERGENCY
        assert len(alert.affected_zones) == 2
        assert len(alert.translations) >= 3
        assert alert.chain_of_custody_hash is not None

    def test_create_alert_with_custom_message(self):
        """Test alert creation with custom message"""
        custom_msg = "This is a custom emergency message"
        alert = self.engine.create_emergency_alert(
            alert_type=AlertType.SHELTER_IN_PLACE,
            priority=AlertPriority.WARNING,
            affected_zones=["Zone_C"],
            custom_message=custom_msg,
        )
        
        assert alert.message == custom_msg

    def test_distribute_alert(self):
        """Test alert distribution"""
        alert = self.engine.create_emergency_alert(
            alert_type=AlertType.WATER_ADVISORY,
            priority=AlertPriority.ADVISORY,
            affected_zones=["Zone_E"],
        )
        
        logs = self.engine.distribute_alert(alert)
        
        assert len(logs) > 0
        assert alert.delivery_status == "distributed"
        for log in logs:
            assert log.recipients_targeted > 0
            assert log.delivery_rate > 0

    def test_detect_social_signals(self):
        """Test social signal detection"""
        public_posts = [
            {
                "content": "Need help! Flooding on my street, car stuck",
                "platform": "twitter",
                "is_public": True,
                "location_mentioned": "Blue Heron Blvd",
            },
            {
                "content": "Where can we get water? Store shelves empty",
                "platform": "facebook",
                "is_public": True,
            },
            {
                "content": "Heard that the bridge collapsed, is it true?",
                "platform": "twitter",
                "is_public": True,
            },
        ]
        
        signals = self.engine.detect_social_signals(public_posts)
        
        assert len(signals) >= 2
        for signal in signals:
            assert signal.signal_id.startswith("SS-")
            assert signal.is_public_post == True
            assert signal.chain_of_custody_hash is not None

    def test_detect_signals_ignores_private(self):
        """Test that private posts are ignored"""
        posts = [
            {
                "content": "Need help!",
                "platform": "twitter",
                "is_public": False,
            },
        ]
        
        signals = self.engine.detect_social_signals(posts)
        assert len(signals) == 0

    def test_debunk_rumor(self):
        """Test rumor debunking"""
        debunk = self.engine.debunk_rumor(
            rumor_summary="Bridge on 13th Street collapsed",
            fact_check_result="FALSE",
            official_statement="The bridge is intact and open. Minor flooding on approach roads.",
            sources=["City Engineering Department", "Police Department"],
        )
        
        assert debunk is not None
        assert debunk.debunk_id.startswith("RD-")
        assert len(debunk.translations) >= 3
        assert len(debunk.sources) == 2

    def test_translate_message(self):
        """Test message translation"""
        message = self.engine.translate_message(
            text="Emergency evacuation in progress",
            source_language=Language.ENGLISH,
            target_languages=[Language.SPANISH, Language.HAITIAN_CREOLE],
        )
        
        assert message is not None
        assert message.message_id.startswith("TM-")
        assert Language.ENGLISH.value in message.translations
        assert Language.SPANISH.value in message.translations
        assert Language.HAITIAN_CREOLE.value in message.translations

    def test_get_alert_templates(self):
        """Test getting alert templates"""
        templates = self.engine.get_alert_templates(AlertType.EVACUATION_ORDER)
        
        assert Language.ENGLISH in templates
        assert Language.SPANISH in templates
        assert Language.HAITIAN_CREOLE in templates

    def test_get_distribution_summary(self):
        """Test distribution summary"""
        alert = self.engine.create_emergency_alert(
            alert_type=AlertType.ALL_CLEAR,
            priority=AlertPriority.INFORMATIONAL,
            affected_zones=["Zone_A"],
        )
        self.engine.distribute_alert(alert)
        
        summary = self.engine.get_distribution_summary()
        
        assert "total_alerts" in summary
        assert "total_targeted" in summary
        assert "total_reached" in summary
        assert "by_channel" in summary

    def test_alert_type_enum(self):
        """Test alert type enumeration"""
        assert AlertType.EVACUATION_ORDER.value == "evacuation_order"
        assert AlertType.SHELTER_IN_PLACE.value == "shelter_in_place"
        assert AlertType.WATER_ADVISORY.value == "water_advisory"
        assert AlertType.ALL_CLEAR.value == "all_clear"

    def test_alert_priority_enum(self):
        """Test alert priority enumeration"""
        assert AlertPriority.INFORMATIONAL.value == 1
        assert AlertPriority.ADVISORY.value == 2
        assert AlertPriority.WATCH.value == 3
        assert AlertPriority.WARNING.value == 4
        assert AlertPriority.EMERGENCY.value == 5

    def test_language_enum(self):
        """Test language enumeration"""
        assert Language.ENGLISH.value == "en"
        assert Language.SPANISH.value == "es"
        assert Language.HAITIAN_CREOLE.value == "ht"

    def test_signal_type_enum(self):
        """Test signal type enumeration"""
        assert SignalType.CRISIS_REPORT.value == "crisis_report"
        assert SignalType.RESOURCE_REQUEST.value == "resource_request"
        assert SignalType.RUMOR.value == "rumor"

    def test_chain_of_custody_hash_format(self):
        """Test chain of custody hash format"""
        alert = self.engine.create_emergency_alert(
            alert_type=AlertType.ROAD_CLOSURE,
            priority=AlertPriority.ADVISORY,
            affected_zones=["Zone_D"],
        )
        assert len(alert.chain_of_custody_hash) == 64
        assert all(c in "0123456789abcdef" for c in alert.chain_of_custody_hash)

    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.engine.get_statistics()
        
        self.engine.create_emergency_alert(
            alert_type=AlertType.BOIL_WATER,
            priority=AlertPriority.WARNING,
            affected_zones=["Zone_F"],
        )
        
        updated_stats = self.engine.get_statistics()
        assert updated_stats["total_alerts_sent"] >= initial_stats["total_alerts_sent"]
