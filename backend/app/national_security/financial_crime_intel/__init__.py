"""
Financial Crime Intelligence Module

Provides financial crime detection capabilities including:
- Fraud pattern mining
- Crypto wallet risk analysis
- Cross-transaction anomaly detection
- Money-movement network graph building
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import uuid
import statistics
import hashlib


class FraudType(Enum):
    """Types of financial fraud."""
    IDENTITY_THEFT = "identity_theft"
    ACCOUNT_TAKEOVER = "account_takeover"
    PAYMENT_FRAUD = "payment_fraud"
    WIRE_FRAUD = "wire_fraud"
    MONEY_LAUNDERING = "money_laundering"
    EMBEZZLEMENT = "embezzlement"
    PONZI_SCHEME = "ponzi_scheme"
    INSIDER_TRADING = "insider_trading"
    TAX_FRAUD = "tax_fraud"
    INSURANCE_FRAUD = "insurance_fraud"
    MORTGAGE_FRAUD = "mortgage_fraud"
    CREDIT_CARD_FRAUD = "credit_card_fraud"
    CHECK_FRAUD = "check_fraud"
    CRYPTO_FRAUD = "crypto_fraud"
    SANCTIONS_EVASION = "sanctions_evasion"
    TERRORIST_FINANCING = "terrorist_financing"
    OTHER = "other"


class RiskCategory(Enum):
    """Risk categories for financial entities."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


class TransactionFlag(Enum):
    """Flags for suspicious transactions."""
    STRUCTURING = "structuring"
    RAPID_MOVEMENT = "rapid_movement"
    ROUND_AMOUNT = "round_amount"
    HIGH_RISK_COUNTRY = "high_risk_country"
    SHELL_COMPANY = "shell_company"
    PEP_INVOLVED = "politically_exposed_person"
    SANCTIONS_MATCH = "sanctions_match"
    UNUSUAL_PATTERN = "unusual_pattern"
    VELOCITY_SPIKE = "velocity_spike"
    DORMANT_ACCOUNT = "dormant_account"
    LAYERING = "layering"
    INTEGRATION = "integration"
    SMURFING = "smurfing"
    MIXER_USAGE = "mixer_usage"
    DARK_WEB_LINK = "dark_web_link"


class CryptoRiskIndicator(Enum):
    """Risk indicators for crypto wallets."""
    MIXER_INTERACTION = "mixer_interaction"
    DARKNET_MARKET = "darknet_market"
    RANSOMWARE = "ransomware"
    SCAM = "scam"
    STOLEN_FUNDS = "stolen_funds"
    SANCTIONS = "sanctions"
    GAMBLING = "gambling"
    HIGH_RISK_EXCHANGE = "high_risk_exchange"
    UNKNOWN_SOURCE = "unknown_source"
    RAPID_CONSOLIDATION = "rapid_consolidation"


class EntityType(Enum):
    """Types of financial entities."""
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    SHELL_COMPANY = "shell_company"
    TRUST = "trust"
    FOUNDATION = "foundation"
    GOVERNMENT = "government"
    FINANCIAL_INSTITUTION = "financial_institution"
    CRYPTO_EXCHANGE = "crypto_exchange"
    CRYPTO_WALLET = "crypto_wallet"
    UNKNOWN = "unknown"


@dataclass
class FraudPattern:
    """Represents a detected fraud pattern."""
    pattern_id: str
    fraud_type: FraudType
    name: str
    description: str
    risk_category: RiskCategory
    risk_score: float
    entities_involved: List[str]
    transactions_involved: List[str]
    total_amount: float
    currency: str
    detection_method: str
    indicators: List[TransactionFlag]
    geographic_scope: List[str]
    time_span_days: int
    confidence_score: float
    is_confirmed: bool
    investigation_status: str
    detected_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CryptoWalletRisk:
    """Represents crypto wallet risk assessment."""
    assessment_id: str
    wallet_address: str
    blockchain: str
    risk_category: RiskCategory
    risk_score: float
    risk_indicators: List[CryptoRiskIndicator]
    total_received: float
    total_sent: float
    transaction_count: int
    first_seen: datetime
    last_seen: datetime
    linked_wallets: List[str]
    exchange_interactions: List[str]
    mixer_exposure: float
    darknet_exposure: float
    sanctions_exposure: float
    cluster_id: Optional[str]
    entity_attribution: Optional[str]
    confidence_score: float
    assessment_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionAnomaly:
    """Represents a detected transaction anomaly."""
    anomaly_id: str
    transaction_id: str
    anomaly_type: str
    description: str
    risk_score: float
    flags: List[TransactionFlag]
    source_entity: str
    destination_entity: str
    amount: float
    currency: str
    transaction_time: datetime
    baseline_comparison: Dict[str, Any]
    deviation_metrics: Dict[str, float]
    related_transactions: List[str]
    is_false_positive: bool
    investigation_status: str
    detected_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MoneyFlowNode:
    """Represents a node in the money flow network."""
    node_id: str
    entity_id: str
    entity_type: EntityType
    entity_name: Optional[str]
    risk_score: float
    total_inflow: float
    total_outflow: float
    transaction_count: int
    connected_nodes: List[str]
    flags: List[TransactionFlag]
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MoneyFlowEdge:
    """Represents an edge in the money flow network."""
    edge_id: str
    source_node: str
    target_node: str
    total_amount: float
    transaction_count: int
    average_amount: float
    currency: str
    flags: List[TransactionFlag]
    first_transaction: datetime
    last_transaction: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MoneyFlowNetwork:
    """Represents a money flow network graph."""
    network_id: str
    name: str
    description: str
    nodes: Dict[str, MoneyFlowNode]
    edges: Dict[str, MoneyFlowEdge]
    total_value: float
    risk_score: float
    fraud_types_detected: List[FraudType]
    geographic_scope: List[str]
    time_span_days: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class FinancialCrimeEngine:
    """
    Financial Crime Intelligence Engine.
    
    Provides capabilities for:
    - Fraud pattern mining
    - Crypto wallet risk analysis
    - Cross-transaction anomaly detection
    - Money-movement network graph building
    """

    def __init__(self):
        self.fraud_patterns: Dict[str, FraudPattern] = {}
        self.crypto_wallet_risks: Dict[str, CryptoWalletRisk] = {}
        self.transaction_anomalies: Dict[str, TransactionAnomaly] = {}
        self.money_flow_networks: Dict[str, MoneyFlowNetwork] = {}
        self.entity_risk_cache: Dict[str, float] = {}
        self.transaction_baselines: Dict[str, Dict[str, Any]] = {}
        self.high_risk_countries: Set[str] = {
            "KP", "IR", "SY", "CU", "VE", "MM", "BY", "RU"
        }

    def detect_fraud_pattern(
        self,
        fraud_type: FraudType,
        name: str,
        description: str,
        entities_involved: List[str],
        transactions_involved: List[str],
        total_amount: float,
        currency: str = "USD",
        detection_method: str = "rule_based",
        indicators: Optional[List[TransactionFlag]] = None,
        geographic_scope: Optional[List[str]] = None,
        time_span_days: int = 30,
        confidence_score: float = 0.7,
    ) -> FraudPattern:
        """Detect and record a fraud pattern."""
        pattern_id = f"fp-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        risk_score = self._calculate_fraud_risk_score(
            fraud_type, total_amount, len(entities_involved), indicators or []
        )
        risk_category = self._score_to_risk_category(risk_score)
        
        pattern = FraudPattern(
            pattern_id=pattern_id,
            fraud_type=fraud_type,
            name=name,
            description=description,
            risk_category=risk_category,
            risk_score=risk_score,
            entities_involved=entities_involved,
            transactions_involved=transactions_involved,
            total_amount=total_amount,
            currency=currency,
            detection_method=detection_method,
            indicators=indicators or [],
            geographic_scope=geographic_scope or [],
            time_span_days=time_span_days,
            confidence_score=confidence_score,
            is_confirmed=False,
            investigation_status="open",
            detected_at=now,
            last_activity=now,
        )
        
        self.fraud_patterns[pattern_id] = pattern
        
        for entity in entities_involved:
            self._update_entity_risk(entity, risk_score)
        
        return pattern

    def _calculate_fraud_risk_score(
        self,
        fraud_type: FraudType,
        amount: float,
        entity_count: int,
        indicators: List[TransactionFlag],
    ) -> float:
        """Calculate risk score for a fraud pattern."""
        type_scores = {
            FraudType.TERRORIST_FINANCING: 95,
            FraudType.SANCTIONS_EVASION: 90,
            FraudType.MONEY_LAUNDERING: 85,
            FraudType.WIRE_FRAUD: 75,
            FraudType.EMBEZZLEMENT: 70,
            FraudType.PONZI_SCHEME: 70,
            FraudType.INSIDER_TRADING: 65,
            FraudType.IDENTITY_THEFT: 60,
            FraudType.ACCOUNT_TAKEOVER: 60,
            FraudType.CRYPTO_FRAUD: 65,
            FraudType.PAYMENT_FRAUD: 55,
            FraudType.TAX_FRAUD: 50,
            FraudType.INSURANCE_FRAUD: 50,
            FraudType.MORTGAGE_FRAUD: 50,
            FraudType.CREDIT_CARD_FRAUD: 45,
            FraudType.CHECK_FRAUD: 40,
            FraudType.OTHER: 30,
        }
        
        base_score = type_scores.get(fraud_type, 50)
        
        if amount > 10000000:
            base_score += 15
        elif amount > 1000000:
            base_score += 10
        elif amount > 100000:
            base_score += 5
        
        base_score += min(10, entity_count)
        
        high_risk_indicators = [
            TransactionFlag.SANCTIONS_MATCH,
            TransactionFlag.DARK_WEB_LINK,
            TransactionFlag.MIXER_USAGE,
            TransactionFlag.TERRORIST_FINANCING if hasattr(TransactionFlag, 'TERRORIST_FINANCING') else None,
        ]
        for indicator in indicators:
            if indicator in high_risk_indicators:
                base_score += 5
            else:
                base_score += 2
        
        return min(100, base_score)

    def _score_to_risk_category(self, score: float) -> RiskCategory:
        """Convert numeric score to risk category."""
        if score < 15:
            return RiskCategory.MINIMAL
        elif score < 30:
            return RiskCategory.LOW
        elif score < 45:
            return RiskCategory.MODERATE
        elif score < 60:
            return RiskCategory.ELEVATED
        elif score < 75:
            return RiskCategory.HIGH
        elif score < 90:
            return RiskCategory.SEVERE
        else:
            return RiskCategory.CRITICAL

    def _update_entity_risk(self, entity_id: str, risk_score: float) -> None:
        """Update cached risk score for an entity."""
        current = self.entity_risk_cache.get(entity_id, 0)
        self.entity_risk_cache[entity_id] = max(current, risk_score * 0.8)

    def get_fraud_patterns(
        self,
        fraud_type: Optional[FraudType] = None,
        risk_category: Optional[RiskCategory] = None,
        min_amount: float = 0,
        investigation_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[FraudPattern]:
        """Retrieve fraud patterns with optional filtering."""
        patterns = list(self.fraud_patterns.values())
        
        if fraud_type:
            patterns = [p for p in patterns if p.fraud_type == fraud_type]
        
        if risk_category:
            risk_order = list(RiskCategory)
            min_index = risk_order.index(risk_category)
            patterns = [p for p in patterns if risk_order.index(p.risk_category) >= min_index]
        
        patterns = [p for p in patterns if p.total_amount >= min_amount]
        
        if investigation_status:
            patterns = [p for p in patterns if p.investigation_status == investigation_status]
        
        patterns.sort(key=lambda x: x.risk_score, reverse=True)
        return patterns[:limit]

    def assess_crypto_wallet_risk(
        self,
        wallet_address: str,
        blockchain: str = "bitcoin",
        total_received: float = 0,
        total_sent: float = 0,
        transaction_count: int = 0,
        first_seen: Optional[datetime] = None,
        last_seen: Optional[datetime] = None,
        linked_wallets: Optional[List[str]] = None,
        exchange_interactions: Optional[List[str]] = None,
        mixer_exposure: float = 0,
        darknet_exposure: float = 0,
        sanctions_exposure: float = 0,
        cluster_id: Optional[str] = None,
        entity_attribution: Optional[str] = None,
    ) -> CryptoWalletRisk:
        """Assess risk for a crypto wallet."""
        assessment_id = f"cw-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        risk_indicators = self._identify_crypto_risk_indicators(
            mixer_exposure, darknet_exposure, sanctions_exposure
        )
        
        risk_score = self._calculate_crypto_risk_score(
            mixer_exposure, darknet_exposure, sanctions_exposure,
            total_received, transaction_count
        )
        risk_category = self._score_to_risk_category(risk_score)
        
        confidence_score = min(0.95, 0.5 + (transaction_count * 0.01))
        
        assessment = CryptoWalletRisk(
            assessment_id=assessment_id,
            wallet_address=wallet_address,
            blockchain=blockchain,
            risk_category=risk_category,
            risk_score=risk_score,
            risk_indicators=risk_indicators,
            total_received=total_received,
            total_sent=total_sent,
            transaction_count=transaction_count,
            first_seen=first_seen or now,
            last_seen=last_seen or now,
            linked_wallets=linked_wallets or [],
            exchange_interactions=exchange_interactions or [],
            mixer_exposure=mixer_exposure,
            darknet_exposure=darknet_exposure,
            sanctions_exposure=sanctions_exposure,
            cluster_id=cluster_id,
            entity_attribution=entity_attribution,
            confidence_score=confidence_score,
            assessment_date=now,
        )
        
        self.crypto_wallet_risks[wallet_address] = assessment
        return assessment

    def _identify_crypto_risk_indicators(
        self,
        mixer_exposure: float,
        darknet_exposure: float,
        sanctions_exposure: float,
    ) -> List[CryptoRiskIndicator]:
        """Identify risk indicators for a crypto wallet."""
        indicators = []
        
        if mixer_exposure > 0.1:
            indicators.append(CryptoRiskIndicator.MIXER_INTERACTION)
        
        if darknet_exposure > 0.1:
            indicators.append(CryptoRiskIndicator.DARKNET_MARKET)
        
        if sanctions_exposure > 0:
            indicators.append(CryptoRiskIndicator.SANCTIONS)
        
        return indicators

    def _calculate_crypto_risk_score(
        self,
        mixer_exposure: float,
        darknet_exposure: float,
        sanctions_exposure: float,
        total_received: float,
        transaction_count: int,
    ) -> float:
        """Calculate risk score for a crypto wallet."""
        score = 10.0
        
        score += min(30, mixer_exposure * 100)
        
        score += min(40, darknet_exposure * 100)
        
        score += min(50, sanctions_exposure * 100)
        
        if total_received > 1000000:
            score += 10
        elif total_received > 100000:
            score += 5
        
        return min(100, score)

    def get_crypto_wallet_risks(
        self,
        blockchain: Optional[str] = None,
        risk_category: Optional[RiskCategory] = None,
        min_risk_score: float = 0,
        has_indicator: Optional[CryptoRiskIndicator] = None,
        limit: int = 100,
    ) -> List[CryptoWalletRisk]:
        """Retrieve crypto wallet risks with optional filtering."""
        assessments = list(self.crypto_wallet_risks.values())
        
        if blockchain:
            assessments = [a for a in assessments if a.blockchain == blockchain]
        
        if risk_category:
            risk_order = list(RiskCategory)
            min_index = risk_order.index(risk_category)
            assessments = [a for a in assessments if risk_order.index(a.risk_category) >= min_index]
        
        assessments = [a for a in assessments if a.risk_score >= min_risk_score]
        
        if has_indicator:
            assessments = [a for a in assessments if has_indicator in a.risk_indicators]
        
        assessments.sort(key=lambda x: x.risk_score, reverse=True)
        return assessments[:limit]

    def detect_transaction_anomaly(
        self,
        transaction_id: str,
        anomaly_type: str,
        description: str,
        source_entity: str,
        destination_entity: str,
        amount: float,
        currency: str = "USD",
        flags: Optional[List[TransactionFlag]] = None,
        baseline_comparison: Optional[Dict[str, Any]] = None,
        deviation_metrics: Optional[Dict[str, float]] = None,
        related_transactions: Optional[List[str]] = None,
    ) -> TransactionAnomaly:
        """Detect and record a transaction anomaly."""
        anomaly_id = f"ta-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        risk_score = self._calculate_anomaly_risk_score(
            amount, flags or [], deviation_metrics or {}
        )
        
        anomaly = TransactionAnomaly(
            anomaly_id=anomaly_id,
            transaction_id=transaction_id,
            anomaly_type=anomaly_type,
            description=description,
            risk_score=risk_score,
            flags=flags or [],
            source_entity=source_entity,
            destination_entity=destination_entity,
            amount=amount,
            currency=currency,
            transaction_time=now,
            baseline_comparison=baseline_comparison or {},
            deviation_metrics=deviation_metrics or {},
            related_transactions=related_transactions or [],
            is_false_positive=False,
            investigation_status="open",
            detected_at=now,
        )
        
        self.transaction_anomalies[anomaly_id] = anomaly
        return anomaly

    def _calculate_anomaly_risk_score(
        self,
        amount: float,
        flags: List[TransactionFlag],
        deviation_metrics: Dict[str, float],
    ) -> float:
        """Calculate risk score for a transaction anomaly."""
        score = 20.0
        
        if amount > 1000000:
            score += 25
        elif amount > 100000:
            score += 15
        elif amount > 10000:
            score += 10
        
        high_risk_flags = [
            TransactionFlag.SANCTIONS_MATCH,
            TransactionFlag.DARK_WEB_LINK,
            TransactionFlag.MIXER_USAGE,
            TransactionFlag.LAYERING,
            TransactionFlag.SMURFING,
        ]
        for flag in flags:
            if flag in high_risk_flags:
                score += 10
            else:
                score += 5
        
        for metric, value in deviation_metrics.items():
            if value > 3:
                score += 10
            elif value > 2:
                score += 5
        
        return min(100, score)

    def get_transaction_anomalies(
        self,
        anomaly_type: Optional[str] = None,
        min_risk_score: float = 0,
        has_flag: Optional[TransactionFlag] = None,
        investigation_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[TransactionAnomaly]:
        """Retrieve transaction anomalies with optional filtering."""
        anomalies = list(self.transaction_anomalies.values())
        
        if anomaly_type:
            anomalies = [a for a in anomalies if a.anomaly_type == anomaly_type]
        
        anomalies = [a for a in anomalies if a.risk_score >= min_risk_score]
        
        if has_flag:
            anomalies = [a for a in anomalies if has_flag in a.flags]
        
        if investigation_status:
            anomalies = [a for a in anomalies if a.investigation_status == investigation_status]
        
        anomalies.sort(key=lambda x: x.risk_score, reverse=True)
        return anomalies[:limit]

    def create_money_flow_network(
        self,
        name: str,
        description: str = "",
    ) -> MoneyFlowNetwork:
        """Create a new money flow network graph."""
        network_id = f"mfn-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        network = MoneyFlowNetwork(
            network_id=network_id,
            name=name,
            description=description,
            nodes={},
            edges={},
            total_value=0,
            risk_score=0,
            fraud_types_detected=[],
            geographic_scope=[],
            time_span_days=0,
            created_at=now,
            updated_at=now,
        )
        
        self.money_flow_networks[network_id] = network
        return network

    def add_network_node(
        self,
        network_id: str,
        entity_id: str,
        entity_type: EntityType,
        entity_name: Optional[str] = None,
        risk_score: float = 0,
        total_inflow: float = 0,
        total_outflow: float = 0,
        transaction_count: int = 0,
        flags: Optional[List[TransactionFlag]] = None,
    ) -> Optional[MoneyFlowNode]:
        """Add a node to a money flow network."""
        network = self.money_flow_networks.get(network_id)
        if not network:
            return None
        
        node_id = f"node-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        node = MoneyFlowNode(
            node_id=node_id,
            entity_id=entity_id,
            entity_type=entity_type,
            entity_name=entity_name,
            risk_score=risk_score,
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            transaction_count=transaction_count,
            connected_nodes=[],
            flags=flags or [],
            first_seen=now,
            last_seen=now,
        )
        
        network.nodes[node_id] = node
        network.updated_at = now
        
        return node

    def add_network_edge(
        self,
        network_id: str,
        source_node: str,
        target_node: str,
        total_amount: float,
        transaction_count: int = 1,
        currency: str = "USD",
        flags: Optional[List[TransactionFlag]] = None,
    ) -> Optional[MoneyFlowEdge]:
        """Add an edge to a money flow network."""
        network = self.money_flow_networks.get(network_id)
        if not network:
            return None
        
        if source_node not in network.nodes or target_node not in network.nodes:
            return None
        
        edge_id = f"edge-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        edge = MoneyFlowEdge(
            edge_id=edge_id,
            source_node=source_node,
            target_node=target_node,
            total_amount=total_amount,
            transaction_count=transaction_count,
            average_amount=total_amount / transaction_count if transaction_count > 0 else 0,
            currency=currency,
            flags=flags or [],
            first_transaction=now,
            last_transaction=now,
        )
        
        network.edges[edge_id] = edge
        network.total_value += total_amount
        network.updated_at = now
        
        network.nodes[source_node].connected_nodes.append(target_node)
        network.nodes[target_node].connected_nodes.append(source_node)
        
        return edge

    def analyze_network(self, network_id: str) -> Optional[Dict[str, Any]]:
        """Analyze a money flow network for patterns."""
        network = self.money_flow_networks.get(network_id)
        if not network:
            return None
        
        node_count = len(network.nodes)
        edge_count = len(network.edges)
        
        if node_count == 0:
            return {
                "network_id": network_id,
                "status": "empty",
                "analysis": {},
            }
        
        avg_connections = sum(len(n.connected_nodes) for n in network.nodes.values()) / node_count
        
        high_risk_nodes = [n for n in network.nodes.values() if n.risk_score >= 65]
        
        hub_nodes = [n for n in network.nodes.values() if len(n.connected_nodes) > avg_connections * 2]
        
        flagged_edges = [e for e in network.edges.values() if e.flags]
        
        network_risk = self._calculate_network_risk(network)
        network.risk_score = network_risk
        
        return {
            "network_id": network_id,
            "status": "analyzed",
            "analysis": {
                "node_count": node_count,
                "edge_count": edge_count,
                "total_value": network.total_value,
                "average_connections": round(avg_connections, 2),
                "high_risk_nodes": len(high_risk_nodes),
                "hub_nodes": len(hub_nodes),
                "flagged_edges": len(flagged_edges),
                "network_risk_score": network_risk,
                "density": edge_count / (node_count * (node_count - 1)) if node_count > 1 else 0,
            },
        }

    def _calculate_network_risk(self, network: MoneyFlowNetwork) -> float:
        """Calculate overall risk score for a network."""
        if not network.nodes:
            return 0
        
        avg_node_risk = statistics.mean([n.risk_score for n in network.nodes.values()])
        
        flagged_ratio = len([e for e in network.edges.values() if e.flags]) / max(1, len(network.edges))
        
        risk = avg_node_risk * 0.6 + flagged_ratio * 40
        
        if network.total_value > 10000000:
            risk += 15
        elif network.total_value > 1000000:
            risk += 10
        
        return min(100, risk)

    def get_money_flow_networks(
        self,
        min_risk_score: float = 0,
        min_nodes: int = 0,
        limit: int = 100,
    ) -> List[MoneyFlowNetwork]:
        """Retrieve money flow networks with optional filtering."""
        networks = list(self.money_flow_networks.values())
        
        networks = [n for n in networks if n.risk_score >= min_risk_score]
        networks = [n for n in networks if len(n.nodes) >= min_nodes]
        
        networks.sort(key=lambda x: x.risk_score, reverse=True)
        return networks[:limit]

    def get_entity_risk(self, entity_id: str) -> float:
        """Get cached risk score for an entity."""
        return self.entity_risk_cache.get(entity_id, 0)

    def set_transaction_baseline(
        self,
        entity_id: str,
        baseline_data: Dict[str, Any],
    ) -> None:
        """Set transaction baseline for an entity."""
        self.transaction_baselines[entity_id] = {
            "data": baseline_data,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get financial crime intelligence metrics."""
        patterns = list(self.fraud_patterns.values())
        wallets = list(self.crypto_wallet_risks.values())
        anomalies = list(self.transaction_anomalies.values())
        
        fraud_type_distribution = {}
        for fraud_type in FraudType:
            fraud_type_distribution[fraud_type.value] = len([p for p in patterns if p.fraud_type == fraud_type])
        
        risk_distribution = {}
        for category in RiskCategory:
            risk_distribution[category.value] = len([p for p in patterns if p.risk_category == category])
        
        return {
            "total_fraud_patterns": len(patterns),
            "open_investigations": len([p for p in patterns if p.investigation_status == "open"]),
            "confirmed_fraud": len([p for p in patterns if p.is_confirmed]),
            "total_fraud_amount": sum(p.total_amount for p in patterns),
            "total_crypto_wallets_assessed": len(wallets),
            "high_risk_wallets": len([w for w in wallets if w.risk_category in [RiskCategory.HIGH, RiskCategory.SEVERE, RiskCategory.CRITICAL]]),
            "total_transaction_anomalies": len(anomalies),
            "open_anomaly_investigations": len([a for a in anomalies if a.investigation_status == "open"]),
            "total_money_flow_networks": len(self.money_flow_networks),
            "fraud_type_distribution": fraud_type_distribution,
            "risk_distribution": risk_distribution,
            "entities_tracked": len(self.entity_risk_cache),
        }
