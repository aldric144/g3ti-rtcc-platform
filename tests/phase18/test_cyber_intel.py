"""
Tests for Cyber Intelligence Engine

Tests cover:
- Malware signal detection
- Botnet activity prediction
- Ransomware early warning
- Vulnerability scanning
- IOC checking
- Threat feeds
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.cyber_intel import (
    CyberIntelEngine,
    MalwareSignal,
    BotnetActivity,
    RansomwareAlert,
    VulnerabilityReport,
    MalwareType,
    ThreatSeverity,
    AttackVector,
    SectorType,
    BotnetStatus,
)


class TestCyberIntelEngine:
    """Test suite for CyberIntelEngine."""

    @pytest.fixture
    def engine(self):
        """Create a CyberIntelEngine instance."""
        return CyberIntelEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes with empty collections."""
        assert engine.malware_signals == {}
        assert engine.botnet_activities == {}
        assert engine.ransomware_alerts == {}
        assert engine.vulnerability_reports == {}
        assert engine.threat_feeds == []

    def test_detect_malware_signal(self, engine):
        """Test malware signal detection."""
        signal = engine.detect_malware_signal(
            malware_type=MalwareType.TROJAN,
            severity=ThreatSeverity.HIGH,
            name="Test Trojan",
            description="A test trojan for unit testing",
            indicators_of_compromise=["hash123", "domain.evil.com"],
            attack_vectors=[AttackVector.PHISHING],
            affected_sectors=[SectorType.GOVERNMENT],
            source="test_source",
        )

        assert signal is not None
        assert signal.signal_id is not None
        assert signal.malware_type == MalwareType.TROJAN
        assert signal.severity == ThreatSeverity.HIGH
        assert signal.name == "Test Trojan"
        assert signal.is_active is True
        assert signal.confidence_score > 0
        assert signal.threat_score > 0

    def test_get_malware_signals_filtering(self, engine):
        """Test malware signal retrieval with filtering."""
        engine.detect_malware_signal(
            malware_type=MalwareType.RANSOMWARE,
            severity=ThreatSeverity.CRITICAL,
            name="Critical Ransomware",
            description="Critical ransomware threat",
            indicators_of_compromise=["hash456"],
            attack_vectors=[AttackVector.EXPLOIT],
            affected_sectors=[SectorType.HEALTHCARE],
            source="test",
        )

        engine.detect_malware_signal(
            malware_type=MalwareType.WORM,
            severity=ThreatSeverity.LOW,
            name="Low Worm",
            description="Low severity worm",
            indicators_of_compromise=["hash789"],
            attack_vectors=[AttackVector.NETWORK],
            affected_sectors=[SectorType.ENERGY],
            source="test",
        )

        critical_signals = engine.get_malware_signals(severity=ThreatSeverity.CRITICAL)
        assert len(critical_signals) == 1
        assert critical_signals[0].name == "Critical Ransomware"

        ransomware_signals = engine.get_malware_signals(malware_type=MalwareType.RANSOMWARE)
        assert len(ransomware_signals) == 1

    def test_predict_botnet_activity(self, engine):
        """Test botnet activity prediction."""
        activity = engine.predict_botnet_activity(
            botnet_name="TestBotnet",
            estimated_size=10000,
            command_servers=["c2.evil.com", "c2-backup.evil.com"],
            target_sectors=[SectorType.FINANCIAL],
            attack_capabilities=["ddos", "spam"],
            source="test_source",
        )

        assert activity is not None
        assert activity.activity_id is not None
        assert activity.botnet_name == "TestBotnet"
        assert activity.estimated_size == 10000
        assert activity.status == BotnetStatus.ACTIVE
        assert activity.threat_score > 0

    def test_get_botnet_activities_filtering(self, engine):
        """Test botnet activity retrieval with filtering."""
        engine.predict_botnet_activity(
            botnet_name="ActiveBot",
            estimated_size=5000,
            command_servers=["c2.test.com"],
            target_sectors=[SectorType.GOVERNMENT],
            attack_capabilities=["ddos"],
            source="test",
        )

        activities = engine.get_botnet_activities(status=BotnetStatus.ACTIVE)
        assert len(activities) >= 1

    def test_create_ransomware_alert(self, engine):
        """Test ransomware alert creation."""
        alert = engine.create_ransomware_alert(
            ransomware_family="TestLocker",
            severity=ThreatSeverity.CRITICAL,
            encryption_type="AES-256",
            ransom_amount=50000.0,
            ransom_currency="BTC",
            affected_systems=["server1", "server2"],
            indicators_of_compromise=["hash_abc"],
            source="test_source",
        )

        assert alert is not None
        assert alert.alert_id is not None
        assert alert.ransomware_family == "TestLocker"
        assert alert.severity == ThreatSeverity.CRITICAL
        assert alert.ransom_amount == 50000.0
        assert alert.is_active is True
        assert alert.threat_score > 0

    def test_get_ransomware_alerts_filtering(self, engine):
        """Test ransomware alert retrieval with filtering."""
        engine.create_ransomware_alert(
            ransomware_family="CriticalLocker",
            severity=ThreatSeverity.CRITICAL,
            encryption_type="RSA-2048",
            ransom_amount=100000.0,
            ransom_currency="BTC",
            affected_systems=["critical_server"],
            indicators_of_compromise=["hash_xyz"],
            source="test",
        )

        critical_alerts = engine.get_ransomware_alerts(severity=ThreatSeverity.CRITICAL)
        assert len(critical_alerts) >= 1

        active_alerts = engine.get_ransomware_alerts(active_only=True)
        assert all(alert.is_active for alert in active_alerts)

    def test_scan_vulnerability(self, engine):
        """Test vulnerability scanning."""
        report = engine.scan_vulnerability(
            target="192.168.1.100",
            scan_type="full",
            sector=SectorType.GOVERNMENT,
        )

        assert report is not None
        assert report.report_id is not None
        assert report.target == "192.168.1.100"
        assert report.scan_type == "full"
        assert report.sector == SectorType.GOVERNMENT

    def test_check_ioc(self, engine):
        """Test IOC checking."""
        engine.detect_malware_signal(
            malware_type=MalwareType.TROJAN,
            severity=ThreatSeverity.HIGH,
            name="IOC Test Malware",
            description="Malware with known IOC",
            indicators_of_compromise=["known_hash_123", "evil.domain.com"],
            attack_vectors=[AttackVector.PHISHING],
            affected_sectors=[SectorType.GOVERNMENT],
            source="test",
        )

        result = engine.check_ioc("known_hash_123")
        assert result["found"] is True
        assert len(result["matches"]) > 0

        result_not_found = engine.check_ioc("unknown_hash")
        assert result_not_found["found"] is False

    def test_add_threat_feed(self, engine):
        """Test adding threat feeds."""
        feed = engine.add_threat_feed(
            name="Test Feed",
            url="https://threatfeed.example.com/api",
            feed_type="malware",
            update_interval=3600,
        )

        assert feed is not None
        assert feed["name"] == "Test Feed"
        assert feed["is_active"] is True

        feeds = engine.get_threat_feeds()
        assert len(feeds) == 1

    def test_get_metrics(self, engine):
        """Test metrics collection."""
        engine.detect_malware_signal(
            malware_type=MalwareType.TROJAN,
            severity=ThreatSeverity.HIGH,
            name="Metrics Test",
            description="Test for metrics",
            indicators_of_compromise=["hash"],
            attack_vectors=[AttackVector.PHISHING],
            affected_sectors=[SectorType.GOVERNMENT],
            source="test",
        )

        metrics = engine.get_metrics()

        assert "total_malware_signals" in metrics
        assert "active_malware_signals" in metrics
        assert "total_botnet_activities" in metrics
        assert "total_ransomware_alerts" in metrics
        assert "total_vulnerability_reports" in metrics
        assert "threat_feeds_count" in metrics
        assert metrics["total_malware_signals"] >= 1


class TestMalwareSignalDataclass:
    """Test MalwareSignal dataclass."""

    def test_malware_signal_creation(self):
        """Test MalwareSignal dataclass creation."""
        signal = MalwareSignal(
            signal_id="test-123",
            malware_type=MalwareType.RANSOMWARE,
            severity=ThreatSeverity.CRITICAL,
            name="Test Ransomware",
            description="Test description",
            indicators_of_compromise=["hash1", "hash2"],
            attack_vectors=[AttackVector.PHISHING, AttackVector.EXPLOIT],
            affected_sectors=[SectorType.HEALTHCARE],
            first_seen="2025-12-10T00:00:00Z",
            last_seen="2025-12-10T12:00:00Z",
            source="test",
            confidence_score=0.95,
            threat_score=85.0,
            is_active=True,
            mitigations=["Block hash1", "Update AV signatures"],
            related_campaigns=["Campaign1"],
            metadata={},
        )

        assert signal.signal_id == "test-123"
        assert signal.malware_type == MalwareType.RANSOMWARE
        assert signal.severity == ThreatSeverity.CRITICAL
        assert signal.confidence_score == 0.95
        assert signal.threat_score == 85.0


class TestBotnetActivityDataclass:
    """Test BotnetActivity dataclass."""

    def test_botnet_activity_creation(self):
        """Test BotnetActivity dataclass creation."""
        activity = BotnetActivity(
            activity_id="bot-123",
            botnet_name="TestBot",
            status=BotnetStatus.ACTIVE,
            estimated_size=50000,
            command_servers=["c2.test.com"],
            target_sectors=[SectorType.FINANCIAL],
            attack_capabilities=["ddos", "spam", "credential_theft"],
            detected_at="2025-12-10T00:00:00Z",
            last_activity="2025-12-10T12:00:00Z",
            source="test",
            threat_score=75.0,
            geographic_distribution={"US": 30, "EU": 40, "ASIA": 30},
            metadata={},
        )

        assert activity.activity_id == "bot-123"
        assert activity.botnet_name == "TestBot"
        assert activity.status == BotnetStatus.ACTIVE
        assert activity.estimated_size == 50000


class TestRansomwareAlertDataclass:
    """Test RansomwareAlert dataclass."""

    def test_ransomware_alert_creation(self):
        """Test RansomwareAlert dataclass creation."""
        alert = RansomwareAlert(
            alert_id="ransom-123",
            ransomware_family="LockBit",
            severity=ThreatSeverity.CRITICAL,
            encryption_type="AES-256-CBC",
            ransom_amount=100000.0,
            ransom_currency="BTC",
            payment_deadline="2025-12-15T00:00:00Z",
            affected_systems=["server1", "server2", "workstation1"],
            indicators_of_compromise=["hash1", "hash2"],
            first_detected="2025-12-10T00:00:00Z",
            source="test",
            threat_score=95.0,
            is_active=True,
            decryption_available=False,
            metadata={},
        )

        assert alert.alert_id == "ransom-123"
        assert alert.ransomware_family == "LockBit"
        assert alert.ransom_amount == 100000.0
        assert alert.is_active is True


class TestVulnerabilityReportDataclass:
    """Test VulnerabilityReport dataclass."""

    def test_vulnerability_report_creation(self):
        """Test VulnerabilityReport dataclass creation."""
        report = VulnerabilityReport(
            report_id="vuln-123",
            target="192.168.1.100",
            scan_type="full",
            sector=SectorType.GOVERNMENT,
            vulnerabilities_found=[
                {"cve": "CVE-2025-1234", "severity": "critical"},
                {"cve": "CVE-2025-5678", "severity": "high"},
            ],
            critical_count=1,
            high_count=1,
            medium_count=0,
            low_count=0,
            scan_started="2025-12-10T00:00:00Z",
            scan_completed="2025-12-10T01:00:00Z",
            overall_risk_score=85.0,
            recommendations=["Patch CVE-2025-1234 immediately"],
            metadata={},
        )

        assert report.report_id == "vuln-123"
        assert report.critical_count == 1
        assert report.overall_risk_score == 85.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
