"""
Test Suite 9: Cyber Ingestion Tests

Tests for cyber threat signal ingestion functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestCyberThreatTypes:
    """Tests for cyber threat type handling."""

    def test_ransomware_threat_ingestion(self):
        """Test ingesting ransomware threats."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="ransomware",
            threat_actor="LockBit 3.0",
            target_sector="Healthcare",
            target_country="USA",
            attack_vector="Phishing Email",
            iocs=["192.168.1.100", "malware.exe"],
            severity=5,
            cve_ids=["CVE-2024-1234"],
            ttps=["T1566", "T1486"],
            source="threat_intel",
            confidence=0.92,
        )

        assert signal is not None
        assert signal.raw_data.get("threat_type") == "ransomware"

    def test_apt_threat_ingestion(self):
        """Test ingesting APT threats."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="apt",
            threat_actor="APT29",
            target_sector="Government",
            target_country="Germany",
            attack_vector="Supply Chain Compromise",
            iocs=["apt29-c2.example.com"],
            severity=5,
            cve_ids=["CVE-2024-5678"],
            ttps=["T1195", "T1071"],
            source="threat_intel",
            confidence=0.88,
        )

        assert signal is not None

    def test_ddos_threat_ingestion(self):
        """Test ingesting DDoS threats."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="ddos",
            threat_actor=None,
            target_sector="Finance",
            target_country="UK",
            attack_vector="Botnet",
            iocs=["botnet-c2.example.net"],
            severity=4,
            cve_ids=[],
            ttps=["T1498", "T1499"],
            source="threat_intel",
            confidence=0.85,
        )

        assert signal is not None

    def test_zero_day_threat_ingestion(self):
        """Test ingesting zero-day threats."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="zero_day",
            threat_actor="Unknown",
            target_sector="Technology",
            target_country="Japan",
            attack_vector="Browser Exploit",
            iocs=["exploit-kit.example.org"],
            severity=5,
            cve_ids=["CVE-2024-0DAY"],
            ttps=["T1189", "T1203"],
            source="cve_feed",
            confidence=0.75,
        )

        assert signal is not None

    def test_supply_chain_threat_ingestion(self):
        """Test ingesting supply chain threats."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="supply_chain",
            threat_actor="Lazarus Group",
            target_sector="Defense",
            target_country="South Korea",
            attack_vector="Compromised Software Update",
            iocs=["lazarus-c2.example.com", "trojan.exe"],
            severity=5,
            cve_ids=["CVE-2024-3456"],
            ttps=["T1195.002", "T1071"],
            source="threat_intel",
            confidence=0.90,
        )

        assert signal is not None


class TestCyberThreatActors:
    """Tests for cyber threat actor handling."""

    def test_known_threat_actor_ingestion(self):
        """Test ingesting threats with known actors."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="apt",
            threat_actor="APT41",
            target_sector="Technology",
            target_country="USA",
            attack_vector="Spear Phishing",
            iocs=["apt41-c2.example.com"],
            severity=5,
            cve_ids=[],
            ttps=["T1566.001"],
            source="threat_intel",
            confidence=0.85,
        )

        assert signal is not None
        assert signal.raw_data.get("threat_actor") == "APT41"

    def test_unknown_threat_actor_ingestion(self):
        """Test ingesting threats with unknown actors."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="malware",
            threat_actor=None,
            target_sector="Manufacturing",
            target_country="Germany",
            attack_vector="USB Drive",
            iocs=["malware.dll"],
            severity=3,
            cve_ids=[],
            ttps=["T1091"],
            source="threat_intel",
            confidence=0.70,
        )

        assert signal is not None


class TestCyberIOCs:
    """Tests for cyber IOC handling."""

    def test_ip_ioc_ingestion(self):
        """Test ingesting IP address IOCs."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="malware",
            threat_actor=None,
            target_sector="Finance",
            target_country="USA",
            attack_vector="Network",
            iocs=["192.168.1.100", "10.0.0.50"],
            severity=4,
            cve_ids=[],
            ttps=[],
            source="threat_intel",
            confidence=0.80,
        )

        assert signal is not None
        assert len(signal.raw_data.get("iocs", [])) == 2

    def test_domain_ioc_ingestion(self):
        """Test ingesting domain IOCs."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="phishing",
            threat_actor=None,
            target_sector="Healthcare",
            target_country="UK",
            attack_vector="Email",
            iocs=["malicious-domain.com", "phishing-site.net"],
            severity=3,
            cve_ids=[],
            ttps=["T1566"],
            source="threat_intel",
            confidence=0.75,
        )

        assert signal is not None

    def test_file_hash_ioc_ingestion(self):
        """Test ingesting file hash IOCs."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="malware",
            threat_actor=None,
            target_sector="Government",
            target_country="France",
            attack_vector="Email Attachment",
            iocs=["a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"],
            severity=4,
            cve_ids=[],
            ttps=["T1566.001"],
            source="threat_intel",
            confidence=0.85,
        )

        assert signal is not None


class TestCyberTTPs:
    """Tests for cyber TTP handling."""

    def test_mitre_ttp_ingestion(self):
        """Test ingesting MITRE ATT&CK TTPs."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="apt",
            threat_actor="APT29",
            target_sector="Defense",
            target_country="USA",
            attack_vector="Spear Phishing",
            iocs=[],
            severity=5,
            cve_ids=[],
            ttps=["T1566.001", "T1059.001", "T1071.001", "T1027"],
            source="threat_intel",
            confidence=0.90,
        )

        assert signal is not None
        assert len(signal.raw_data.get("ttps", [])) == 4


class TestCyberCVEs:
    """Tests for cyber CVE handling."""

    def test_cve_ingestion(self):
        """Test ingesting CVE references."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="exploit",
            threat_actor=None,
            target_sector="Technology",
            target_country="Global",
            attack_vector="Remote Code Execution",
            iocs=[],
            severity=5,
            cve_ids=["CVE-2024-1234", "CVE-2024-5678"],
            ttps=["T1203"],
            source="cve_feed",
            confidence=0.95,
        )

        assert signal is not None
        assert len(signal.raw_data.get("cve_ids", [])) == 2


class TestCyberChainOfCustody:
    """Tests for cyber chain of custody."""

    def test_cyber_signal_has_hash(self):
        """Test that cyber signal has chain of custody hash."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="ransomware",
            threat_actor="LockBit",
            target_sector="Healthcare",
            target_country="USA",
            attack_vector="Phishing",
            iocs=["test.exe"],
            severity=5,
            cve_ids=[],
            ttps=[],
            source="threat_intel",
            confidence=0.90,
        )

        assert signal.chain_of_custody_hash is not None
        assert len(signal.chain_of_custody_hash) == 64


class TestCyberSignalID:
    """Tests for cyber signal ID generation."""

    def test_cyber_signal_id_format(self):
        """Test that cyber signal ID has correct format."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_cyber_signal(
            threat_type="malware",
            threat_actor=None,
            target_sector="Finance",
            target_country="USA",
            attack_vector="Email",
            iocs=[],
            severity=3,
            cve_ids=[],
            ttps=[],
            source="threat_intel",
            confidence=0.70,
        )

        assert signal.signal_id.startswith("CYB-")
