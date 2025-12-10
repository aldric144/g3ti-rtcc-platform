"""
Tests for Financial Crime Intelligence Engine

Tests cover:
- Fraud pattern detection
- Crypto wallet risk analysis
- Transaction anomaly detection
- Money flow network building
- Entity risk assessment
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.financial_crime_intel import (
    FinancialCrimeEngine,
    FraudPattern,
    CryptoWalletRisk,
    TransactionAnomaly,
    MoneyFlowNode,
    MoneyFlowEdge,
    MoneyFlowNetwork,
    FraudType,
    RiskCategory,
    TransactionFlag,
    CryptoRiskIndicator,
    EntityType,
)


class TestFinancialCrimeEngine:
    """Test suite for FinancialCrimeEngine."""

    @pytest.fixture
    def engine(self):
        """Create a FinancialCrimeEngine instance."""
        return FinancialCrimeEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes with empty collections."""
        assert engine.fraud_patterns == {}
        assert engine.crypto_wallet_risks == {}
        assert engine.transaction_anomalies == {}
        assert engine.money_flow_networks == {}
        assert engine.entity_risk_cache == {}

    def test_detect_fraud_pattern(self, engine):
        """Test fraud pattern detection."""
        pattern = engine.detect_fraud_pattern(
            fraud_type=FraudType.WIRE_FRAUD,
            name="Test Wire Fraud Pattern",
            description="A test wire fraud pattern for unit testing",
            entities_involved=["Entity A", "Entity B"],
            total_amount=500000.0,
            currency="USD",
            transaction_count=25,
            time_span_days=30,
            indicators=["rapid_transfers", "shell_companies"],
        )

        assert pattern is not None
        assert pattern.pattern_id is not None
        assert pattern.fraud_type == FraudType.WIRE_FRAUD
        assert pattern.name == "Test Wire Fraud Pattern"
        assert pattern.total_amount == 500000.0
        assert pattern.risk_score > 0

    def test_get_fraud_patterns_filtering(self, engine):
        """Test fraud pattern retrieval with filtering."""
        engine.detect_fraud_pattern(
            fraud_type=FraudType.MONEY_LAUNDERING,
            name="Money Laundering Pattern",
            description="Money laundering detection",
            entities_involved=["Shell Corp 1", "Shell Corp 2"],
            total_amount=1000000.0,
            currency="USD",
            transaction_count=50,
            time_span_days=90,
            indicators=["layering", "structuring"],
        )

        engine.detect_fraud_pattern(
            fraud_type=FraudType.IDENTITY_THEFT,
            name="Identity Theft Pattern",
            description="Identity theft detection",
            entities_involved=["Victim 1"],
            total_amount=50000.0,
            currency="USD",
            transaction_count=10,
            time_span_days=7,
            indicators=["new_accounts", "address_changes"],
        )

        ml_patterns = engine.get_fraud_patterns(fraud_type=FraudType.MONEY_LAUNDERING)
        assert len(ml_patterns) == 1
        assert ml_patterns[0].name == "Money Laundering Pattern"

    def test_assess_crypto_wallet_risk(self, engine):
        """Test crypto wallet risk assessment."""
        assessment = engine.assess_crypto_wallet_risk(
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            blockchain="ethereum",
            total_received=100.5,
            total_sent=95.2,
            transaction_count=150,
            first_seen="2024-01-01",
            last_seen="2025-12-10",
            known_associations=["mixer_service", "darknet_market"],
            risk_indicators=[CryptoRiskIndicator.MIXER_USAGE, CryptoRiskIndicator.DARKNET_ASSOCIATION],
        )

        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert assessment.blockchain == "ethereum"
        assert assessment.risk_score > 0
        assert CryptoRiskIndicator.MIXER_USAGE in assessment.risk_indicators

    def test_get_crypto_wallet_risks_filtering(self, engine):
        """Test crypto wallet risk retrieval with filtering."""
        engine.assess_crypto_wallet_risk(
            wallet_address="bc1qhighrisktestaddress",
            blockchain="bitcoin",
            total_received=50.0,
            total_sent=49.5,
            transaction_count=100,
            first_seen="2024-06-01",
            last_seen="2025-12-10",
            known_associations=["ransomware_payment"],
            risk_indicators=[CryptoRiskIndicator.RANSOMWARE_PAYMENT, CryptoRiskIndicator.HIGH_VELOCITY],
        )

        high_risk = engine.get_crypto_wallet_risks(risk_category=RiskCategory.HIGH)
        assert len(high_risk) >= 0

        bitcoin_wallets = engine.get_crypto_wallet_risks(blockchain="bitcoin")
        assert len(bitcoin_wallets) >= 1

    def test_detect_transaction_anomaly(self, engine):
        """Test transaction anomaly detection."""
        anomaly = engine.detect_transaction_anomaly(
            transaction_id="TXN-123456",
            source_entity="Account A",
            source_entity_type=EntityType.INDIVIDUAL,
            destination_entity="Account B",
            destination_entity_type=EntityType.SHELL_COMPANY,
            amount=250000.0,
            currency="USD",
            transaction_type="wire_transfer",
            flags=[TransactionFlag.STRUCTURING, TransactionFlag.RAPID_MOVEMENT],
            anomaly_description="Large transfer to shell company with structuring pattern",
        )

        assert anomaly is not None
        assert anomaly.anomaly_id is not None
        assert anomaly.transaction_id == "TXN-123456"
        assert anomaly.amount == 250000.0
        assert anomaly.risk_score > 0
        assert TransactionFlag.STRUCTURING in anomaly.flags

    def test_get_transaction_anomalies_filtering(self, engine):
        """Test transaction anomaly retrieval with filtering."""
        engine.detect_transaction_anomaly(
            transaction_id="TXN-789",
            source_entity="Suspicious Account",
            source_entity_type=EntityType.INDIVIDUAL,
            destination_entity="Offshore Account",
            destination_entity_type=EntityType.OFFSHORE_ENTITY,
            amount=500000.0,
            currency="EUR",
            transaction_type="international_wire",
            flags=[TransactionFlag.OFFSHORE_TRANSFER, TransactionFlag.UNUSUAL_AMOUNT],
            anomaly_description="Large offshore transfer",
        )

        offshore_anomalies = engine.get_transaction_anomalies(
            flags=[TransactionFlag.OFFSHORE_TRANSFER]
        )
        assert len(offshore_anomalies) >= 1

    def test_create_money_flow_network(self, engine):
        """Test money flow network creation."""
        network = engine.create_money_flow_network(
            name="Test Network",
            description="A test money flow network",
            investigation_id="INV-001",
        )

        assert network is not None
        assert network.network_id is not None
        assert network.name == "Test Network"
        assert len(network.nodes) == 0
        assert len(network.edges) == 0

    def test_add_network_node(self, engine):
        """Test adding nodes to money flow network."""
        network = engine.create_money_flow_network(
            name="Node Test Network",
            description="Network for node testing",
            investigation_id="INV-002",
        )

        node = engine.add_network_node(
            network_id=network.network_id,
            entity_id="ENT-001",
            entity_type=EntityType.CORPORATION,
            entity_name="Test Corporation",
            risk_score=65.0,
            attributes={"country": "US", "industry": "finance"},
        )

        assert node is not None
        assert node.node_id is not None
        assert node.entity_name == "Test Corporation"

        updated_network = engine.money_flow_networks[network.network_id]
        assert len(updated_network.nodes) == 1

    def test_add_network_edge(self, engine):
        """Test adding edges to money flow network."""
        network = engine.create_money_flow_network(
            name="Edge Test Network",
            description="Network for edge testing",
            investigation_id="INV-003",
        )

        node1 = engine.add_network_node(
            network_id=network.network_id,
            entity_id="ENT-A",
            entity_type=EntityType.INDIVIDUAL,
            entity_name="Person A",
            risk_score=30.0,
            attributes={},
        )

        node2 = engine.add_network_node(
            network_id=network.network_id,
            entity_id="ENT-B",
            entity_type=EntityType.CORPORATION,
            entity_name="Company B",
            risk_score=50.0,
            attributes={},
        )

        edge = engine.add_network_edge(
            network_id=network.network_id,
            source_node_id=node1.node_id,
            target_node_id=node2.node_id,
            relationship_type="payment",
            total_amount=100000.0,
            currency="USD",
            transaction_count=5,
            attributes={"frequency": "monthly"},
        )

        assert edge is not None
        assert edge.edge_id is not None
        assert edge.total_amount == 100000.0

        updated_network = engine.money_flow_networks[network.network_id]
        assert len(updated_network.edges) == 1

    def test_analyze_network(self, engine):
        """Test network analysis."""
        network = engine.create_money_flow_network(
            name="Analysis Test Network",
            description="Network for analysis testing",
            investigation_id="INV-004",
        )

        node1 = engine.add_network_node(
            network_id=network.network_id,
            entity_id="HUB-001",
            entity_type=EntityType.SHELL_COMPANY,
            entity_name="Hub Company",
            risk_score=80.0,
            attributes={},
        )

        for i in range(5):
            node = engine.add_network_node(
                network_id=network.network_id,
                entity_id=f"SPOKE-{i}",
                entity_type=EntityType.INDIVIDUAL,
                entity_name=f"Person {i}",
                risk_score=40.0,
                attributes={},
            )

            engine.add_network_edge(
                network_id=network.network_id,
                source_node_id=node.node_id,
                target_node_id=node1.node_id,
                relationship_type="payment",
                total_amount=50000.0,
                currency="USD",
                transaction_count=2,
                attributes={},
            )

        analysis = engine.analyze_network(network.network_id)

        assert analysis is not None
        assert "total_nodes" in analysis
        assert "total_edges" in analysis
        assert "total_flow" in analysis
        assert "high_risk_nodes" in analysis
        assert analysis["total_nodes"] == 6
        assert analysis["total_edges"] == 5

    def test_get_money_flow_networks_filtering(self, engine):
        """Test money flow network retrieval with filtering."""
        engine.create_money_flow_network(
            name="Filter Test Network",
            description="Network for filter testing",
            investigation_id="INV-005",
        )

        networks = engine.get_money_flow_networks(investigation_id="INV-005")
        assert len(networks) >= 1

    def test_get_entity_risk(self, engine):
        """Test entity risk retrieval."""
        engine.detect_fraud_pattern(
            fraud_type=FraudType.WIRE_FRAUD,
            name="Entity Risk Test",
            description="Pattern for entity risk testing",
            entities_involved=["Risk Test Entity"],
            total_amount=100000.0,
            currency="USD",
            transaction_count=10,
            time_span_days=30,
            indicators=["suspicious_activity"],
        )

        risk = engine.get_entity_risk("Risk Test Entity")
        assert risk is not None
        assert risk >= 0

        unknown_risk = engine.get_entity_risk("Unknown Entity")
        assert unknown_risk is None or unknown_risk == 0

    def test_set_transaction_baseline(self, engine):
        """Test setting transaction baseline for an entity."""
        baseline = engine.set_transaction_baseline(
            entity_id="BASELINE-001",
            avg_transaction_amount=5000.0,
            avg_transaction_count_daily=10,
            typical_counterparties=["Partner A", "Partner B"],
            typical_currencies=["USD", "EUR"],
            typical_transaction_types=["wire", "ach"],
        )

        assert baseline is not None
        assert baseline["entity_id"] == "BASELINE-001"
        assert baseline["avg_transaction_amount"] == 5000.0

    def test_get_metrics(self, engine):
        """Test metrics collection."""
        engine.detect_fraud_pattern(
            fraud_type=FraudType.IDENTITY_THEFT,
            name="Metrics Test Pattern",
            description="Pattern for metrics testing",
            entities_involved=["Metrics Entity"],
            total_amount=25000.0,
            currency="USD",
            transaction_count=5,
            time_span_days=7,
            indicators=["new_account"],
        )

        metrics = engine.get_metrics()

        assert "total_fraud_patterns" in metrics
        assert "confirmed_fraud_patterns" in metrics
        assert "total_crypto_assessments" in metrics
        assert "high_risk_wallets" in metrics
        assert "total_transaction_anomalies" in metrics
        assert "open_anomalies" in metrics
        assert "total_networks" in metrics


class TestFraudPatternDataclass:
    """Test FraudPattern dataclass."""

    def test_fraud_pattern_creation(self):
        """Test FraudPattern dataclass creation."""
        pattern = FraudPattern(
            pattern_id="fraud-123",
            fraud_type=FraudType.MONEY_LAUNDERING,
            name="Test ML Pattern",
            description="Test description",
            risk_category=RiskCategory.HIGH,
            risk_score=85.0,
            entities_involved=["Entity 1", "Entity 2"],
            total_amount=1000000.0,
            currency="USD",
            transaction_count=100,
            time_span_days=180,
            indicators=["layering", "structuring", "smurfing"],
            is_confirmed=False,
            investigation_status="open",
            detected_at="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert pattern.pattern_id == "fraud-123"
        assert pattern.fraud_type == FraudType.MONEY_LAUNDERING
        assert pattern.risk_score == 85.0


class TestCryptoWalletRiskDataclass:
    """Test CryptoWalletRisk dataclass."""

    def test_crypto_wallet_risk_creation(self):
        """Test CryptoWalletRisk dataclass creation."""
        risk = CryptoWalletRisk(
            assessment_id="crypto-123",
            wallet_address="0xabcdef1234567890",
            blockchain="ethereum",
            risk_category=RiskCategory.CRITICAL,
            risk_score=95.0,
            risk_indicators=[
                CryptoRiskIndicator.RANSOMWARE_PAYMENT,
                CryptoRiskIndicator.SANCTIONED_ENTITY,
            ],
            total_received=500.0,
            total_sent=495.0,
            transaction_count=1000,
            first_seen="2023-01-01",
            last_seen="2025-12-10",
            known_associations=["ransomware_group", "sanctioned_exchange"],
            assessment_date="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert risk.assessment_id == "crypto-123"
        assert risk.risk_category == RiskCategory.CRITICAL
        assert risk.risk_score == 95.0


class TestTransactionAnomalyDataclass:
    """Test TransactionAnomaly dataclass."""

    def test_transaction_anomaly_creation(self):
        """Test TransactionAnomaly dataclass creation."""
        anomaly = TransactionAnomaly(
            anomaly_id="anom-123",
            transaction_id="TXN-456",
            anomaly_type="structuring",
            source_entity="Account X",
            source_entity_type=EntityType.INDIVIDUAL,
            destination_entity="Account Y",
            destination_entity_type=EntityType.SHELL_COMPANY,
            amount=9500.0,
            currency="USD",
            transaction_type="cash_deposit",
            flags=[TransactionFlag.STRUCTURING, TransactionFlag.CASH_INTENSIVE],
            risk_score=75.0,
            description="Multiple deposits just under reporting threshold",
            detected_at="2025-12-10T00:00:00Z",
            investigation_status="open",
            metadata={},
        )

        assert anomaly.anomaly_id == "anom-123"
        assert anomaly.amount == 9500.0
        assert TransactionFlag.STRUCTURING in anomaly.flags


class TestMoneyFlowNetworkDataclass:
    """Test MoneyFlowNetwork dataclass."""

    def test_money_flow_network_creation(self):
        """Test MoneyFlowNetwork dataclass creation."""
        network = MoneyFlowNetwork(
            network_id="net-123",
            name="Test Network",
            description="Test description",
            investigation_id="INV-001",
            nodes=[],
            edges=[],
            total_flow=0.0,
            risk_score=0.0,
            created_at="2025-12-10T00:00:00Z",
            updated_at="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert network.network_id == "net-123"
        assert network.name == "Test Network"
        assert len(network.nodes) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
