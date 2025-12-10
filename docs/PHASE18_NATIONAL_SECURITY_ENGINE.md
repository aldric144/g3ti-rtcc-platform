# Phase 18: Autonomous National Security Engine (AI-NSE)

## Overview

The Autonomous National Security Engine (AI-NSE) is a comprehensive national-level security intelligence platform that monitors, predicts, and correlates threats across multiple domains including cyber threats, insider threats, geopolitical risks, and financial crimes. This phase implements six core subsystems that work together to provide a unified view of national security risks.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS NATIONAL SECURITY ENGINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Cyber Intel │  │   Insider    │  │ Geopolitical │  │  Financial   │    │
│  │    Engine    │  │   Threat     │  │    Risk      │  │    Crime     │    │
│  │              │  │   Engine     │  │   Engine     │  │   Engine     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                   │                                          │
│                    ┌──────────────▼──────────────┐                          │
│                    │   National Risk Fusion      │                          │
│                    │         Engine              │                          │
│                    │  ┌─────────────────────┐   │                          │
│                    │  │ National Stability  │   │                          │
│                    │  │      Score (NSS)    │   │                          │
│                    │  └─────────────────────┘   │                          │
│                    └──────────────┬──────────────┘                          │
│                                   │                                          │
│                    ┌──────────────▼──────────────┐                          │
│                    │  National Security Alerts   │                          │
│                    │    ┌─────────────────┐     │                          │
│                    │    │ REST + WebSocket│     │                          │
│                    │    └─────────────────┘     │                          │
│                    └─────────────────────────────┘                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Cyber Intelligence Engine (`cyber_intel/`)

The Cyber Intelligence Engine monitors and analyzes cyber threats including malware, botnets, ransomware, and vulnerabilities.

#### Components

- **MalwareSignalDetector**: Detects and records malware signals with type classification, severity assessment, and confidence scoring
- **BotnetActivityPredictor**: Predicts botnet activity patterns and tracks known botnets
- **RansomwareEarlyWarning**: Provides early warning alerts for ransomware threats
- **VulnerabilityScanner**: Scans for cross-sector vulnerabilities (API stub for integration)

#### Data Models

```python
@dataclass
class MalwareSignal:
    signal_id: str
    malware_type: MalwareType  # trojan, worm, ransomware, spyware, etc.
    severity: ThreatSeverity   # critical, high, medium, low, informational
    name: str
    description: str
    indicators_of_compromise: List[str]
    attack_vectors: List[AttackVector]
    affected_sectors: List[SectorType]
    confidence_score: float
    threat_score: float
    is_active: bool
```

#### API Endpoints

- `POST /api/national-security/cyber/malware` - Detect malware signal
- `GET /api/national-security/cyber/malware` - Get malware signals with filtering
- `POST /api/national-security/cyber/botnets` - Predict botnet activity
- `GET /api/national-security/cyber/botnets` - Get botnet activities
- `POST /api/national-security/cyber/ransomware` - Create ransomware alert
- `GET /api/national-security/cyber/ransomware` - Get ransomware alerts
- `POST /api/national-security/cyber/vulnerabilities` - Scan vulnerability
- `GET /api/national-security/cyber/vulnerabilities` - Get vulnerability reports
- `GET /api/national-security/cyber/metrics` - Get cyber intel metrics

### 2. Insider Threat Engine (`insider_threat/`)

The Insider Threat Engine profiles employee risk, detects behavior deviations, and identifies access anomalies.

#### Components

- **EmployeeRiskProfiler**: Creates and maintains risk profiles for employees
- **BehaviorDeviationEngine**: Detects deviations from established behavioral baselines
- **AccessAnomalyDetector**: Identifies anomalous access patterns
- **RoleBasedThreatScoring**: Scores threats based on role and clearance level

#### Data Models

```python
@dataclass
class EmployeeRiskProfile:
    profile_id: str
    employee_id: str
    employee_name: str
    department: DepartmentType
    role: str
    clearance_level: ClearanceLevel
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[str]
    is_privileged: bool
    access_patterns: Dict[str, Any]
```

#### API Endpoints

- `POST /api/national-security/insider/profiles` - Create risk profile
- `GET /api/national-security/insider/profiles` - Get risk profiles
- `POST /api/national-security/insider/deviations` - Detect behavior deviation
- `GET /api/national-security/insider/deviations` - Get behavior deviations
- `POST /api/national-security/insider/anomalies` - Detect access anomaly
- `GET /api/national-security/insider/anomalies` - Get access anomalies
- `GET /api/national-security/insider/high-risk` - Get high-risk employees
- `GET /api/national-security/insider/metrics` - Get insider threat metrics

### 3. Geopolitical Risk Engine (`geopolitical_risk/`)

The Geopolitical Risk Engine monitors global conflicts, nation-state threats, sanctions, and geo-economic instability.

#### Components

- **GlobalConflictIntensityIndex**: Calculates global and regional conflict intensity
- **NationStateThreatModeler**: Models threats from nation-state actors
- **SanctionsEventIngestion**: Ingests sanctions and terrorism events (stub)
- **GeoEconomicInstabilityScoring**: Scores geo-economic instability by country/region

#### Data Models

```python
@dataclass
class ConflictEvent:
    event_id: str
    name: str
    description: str
    intensity: ConflictIntensity  # war, high, medium, low, tension
    region: str
    countries_involved: List[str]
    start_date: str
    is_active: bool
    escalation_risk: float
    casualties_estimate: int
    displacement_estimate: int
```

#### API Endpoints

- `POST /api/national-security/geopolitical/conflicts` - Record conflict event
- `GET /api/national-security/geopolitical/conflicts` - Get conflict events
- `GET /api/national-security/geopolitical/conflict-index` - Get conflict intensity index
- `POST /api/national-security/geopolitical/threats` - Assess nation-state threat
- `GET /api/national-security/geopolitical/threats` - Get nation-state threats
- `POST /api/national-security/geopolitical/geo-economic` - Assess geo-economic risk
- `GET /api/national-security/geopolitical/geo-economic` - Get geo-economic risks
- `GET /api/national-security/geopolitical/summary` - Get global risk summary
- `GET /api/national-security/geopolitical/metrics` - Get geopolitical metrics

### 4. Financial Crime Intelligence Engine (`financial_crime_intel/`)

The Financial Crime Intelligence Engine detects fraud patterns, analyzes crypto wallet risks, and builds money flow networks.

#### Components

- **FraudPatternMiner**: Mines and detects fraud patterns
- **CryptoWalletRiskAnalyzer**: Analyzes cryptocurrency wallet risks
- **TransactionAnomalyDetector**: Detects anomalous transactions
- **MoneyFlowNetworkBuilder**: Builds network graphs of money movements

#### Data Models

```python
@dataclass
class FraudPattern:
    pattern_id: str
    fraud_type: FraudType  # identity_theft, wire_fraud, money_laundering, etc.
    name: str
    description: str
    risk_category: RiskCategory
    risk_score: float
    entities_involved: List[str]
    total_amount: float
    currency: str
    transaction_count: int
    is_confirmed: bool
    investigation_status: str
```

#### API Endpoints

- `POST /api/national-security/financial/fraud-patterns` - Detect fraud pattern
- `GET /api/national-security/financial/fraud-patterns` - Get fraud patterns
- `POST /api/national-security/financial/crypto-wallets` - Assess crypto wallet risk
- `GET /api/national-security/financial/crypto-wallets` - Get crypto wallet risks
- `POST /api/national-security/financial/transaction-anomalies` - Detect transaction anomaly
- `GET /api/national-security/financial/transaction-anomalies` - Get transaction anomalies
- `POST /api/national-security/financial/networks` - Create money flow network
- `GET /api/national-security/financial/networks` - Get money flow networks
- `GET /api/national-security/financial/metrics` - Get financial crime metrics

### 5. National Risk Fusion Engine (`national_risk_fusion/`)

The National Risk Fusion Engine combines signals from all domains to calculate the National Stability Score and generate early warnings.

#### Components

- **DeepFusionEngine**: Fuses cyber, geopolitical, crime, and insider signals
- **NationalStabilityScore**: Calculates the overall national stability score (0-100)
- **EarlyWarningPrediction**: Generates early warning signals with time horizons

#### Fusion Methods

1. **Weighted Average**: Simple weighted combination of domain scores
2. **Max Risk**: Takes the maximum risk across all domains
3. **Ensemble**: Combines multiple fusion methods
4. **Bayesian**: Probabilistic fusion with prior beliefs

#### Data Models

```python
@dataclass
class NationalStabilityScore:
    assessment_id: str
    timestamp: str
    overall_score: float  # 0-100, lower is more stable
    stability_level: StabilityLevel
    domain_scores: Dict[str, DomainRiskScore]
    trend: TrendDirection
    confidence_level: float
    key_drivers: List[str]
    recommendations: List[str]
    forecast_24h: float
    forecast_7d: float
    forecast_30d: float
```

#### Stability Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 0-20 | Optimal | Minimal risk, stable conditions |
| 20-35 | Stable | Low risk, normal operations |
| 35-50 | Elevated Concern | Moderate risk, increased monitoring |
| 50-70 | Unstable | High risk, active response needed |
| 70-85 | Critical | Severe risk, emergency protocols |
| 85-100 | Emergency | Extreme risk, immediate action required |

#### API Endpoints

- `POST /api/national-security/fusion/stability-score` - Calculate stability score
- `GET /api/national-security/fusion/stability-score` - Get latest stability score
- `POST /api/national-security/fusion/risk-fusion` - Perform risk fusion
- `POST /api/national-security/fusion/early-warnings` - Generate early warning
- `GET /api/national-security/fusion/early-warnings` - Get early warnings
- `POST /api/national-security/fusion/trend-predictions` - Create trend prediction
- `GET /api/national-security/fusion/timeline` - Get fusion timeline
- `GET /api/national-security/fusion/metrics` - Get fusion metrics

### 6. National Security Alerts (`national_security_alerts/`)

The National Security Alerts module manages alert creation, routing, escalation, and delivery.

#### Components

- **AlertManager**: Creates and manages security alerts
- **RoutingEngine**: Routes alerts to appropriate destinations
- **EscalationManager**: Handles alert escalation
- **WebSocketBroadcaster**: Broadcasts alerts via WebSocket

#### Alert Priorities

| Priority | Response Time | Escalation |
|----------|---------------|------------|
| Critical | Immediate | Auto-escalate to Chief |
| Flash | < 5 minutes | Auto-escalate to Director |
| Immediate | < 15 minutes | Notify Homeland Security Liaison |
| Priority | < 1 hour | Standard routing |
| Routine | < 4 hours | Normal processing |

#### Default Routing Rules

1. **Critical Alerts**: Chief, RTCC Director, Homeland Security Liaison
2. **Cyber Threats**: Cyber Security Team, IT Director
3. **Financial Crimes**: Financial Crimes Unit, FBI Liaison
4. **Terrorism**: Homeland Security Liaison, FBI Liaison, Chief
5. **National Stability**: RTCC Director, Chief, Command Center

#### API Endpoints

- `POST /api/national-security/alerts` - Create alert
- `GET /api/national-security/alerts` - Get alerts with filtering
- `GET /api/national-security/alerts/{alert_id}` - Get specific alert
- `POST /api/national-security/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/national-security/alerts/{alert_id}/escalate` - Escalate alert
- `POST /api/national-security/alerts/{alert_id}/resolve` - Resolve alert
- `POST /api/national-security/alerts/{alert_id}/close` - Close alert
- `GET /api/national-security/alerts/statistics` - Get alert statistics
- `GET /api/national-security/alerts/subscriptions` - Get subscriptions
- `GET /api/national-security/alerts/routing-rules` - Get routing rules
- `GET /api/national-security/alerts/audit-log` - Get audit log
- `GET /api/national-security/alerts/metrics` - Get alert metrics

## WebSocket Channels

### Main Channel

`/ws/national-security`

Broadcasts all national security events including alerts, stability score updates, and early warnings.

### Sub-Channels

| Channel | Description |
|---------|-------------|
| `/ws/national-security/cyber` | Cyber threat intelligence updates |
| `/ws/national-security/insider` | Insider threat notifications |
| `/ws/national-security/geopolitical` | Geopolitical risk updates |
| `/ws/national-security/financial` | Financial crime alerts |
| `/ws/national-security/fusion` | Risk fusion and stability updates |
| `/ws/national-security/alerts` | Security alert broadcasts |
| `/ws/national-security/stability` | Stability score changes |

### Message Types

```json
{
  "type": "security_alert",
  "alert_id": "alert-123",
  "title": "Critical Cyber Threat Detected",
  "priority": "critical",
  "category": "cyber_threat",
  "risk_score": 85.5,
  "destinations": ["chief", "rtcc_director"],
  "escalation_level": "executive",
  "timestamp": "2025-12-10T19:30:00Z"
}
```

```json
{
  "type": "stability_score_update",
  "assessment_id": "nss-456",
  "overall_score": 42.5,
  "stability_level": "elevated_concern",
  "trend": "degrading",
  "key_drivers": ["cyber_threat_increase", "geopolitical_tension"],
  "forecasts": {
    "24h": 45.2,
    "7d": 48.1,
    "30d": 44.8
  },
  "timestamp": "2025-12-10T19:30:00Z"
}
```

## Frontend Dashboard

### Page: `/national-security`

The National Security dashboard provides a comprehensive view of all AI-NSE modules.

### Components

1. **CyberIntelPanel**: Displays malware signals, botnet activities, and ransomware alerts
2. **InsiderThreatPanel**: Shows employee risk profiles, behavior deviations, and access anomalies
3. **GeoRiskMap**: Visualizes global conflicts, nation-state threats, and geo-economic risks
4. **FinancialCrimeGraph**: Displays fraud patterns, crypto wallet risks, and transaction anomalies
5. **NationalStabilityScore**: Shows the current NSS with forecasts and key drivers
6. **EarlyWarningTimeline**: Displays active early warnings and fusion event timeline

### Tab Navigation

| Tab | Description |
|-----|-------------|
| Overview | Combined view of all modules with NSS prominently displayed |
| Cyber Intel | Detailed cyber threat intelligence |
| Insider Threat | Employee risk and behavior analysis |
| Geo Risk | Geopolitical risk assessment |
| Financial Crime | Financial crime intelligence |
| Risk Fusion | National stability and early warnings |

## DevOps Configuration

### Docker Services

```yaml
services:
  nse-cyber-intel:
    # Cyber Intelligence background worker
    profiles: [national-security]
    
  nse-financial-crime:
    # Financial Crime Intelligence background worker
    profiles: [national-security]
    
  nse-risk-fusion:
    # GPU-accelerated Risk Fusion Engine
    profiles: [national-security, gpu]
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CYBER_MALWARE_DETECTION_ENABLED` | Enable malware detection | `true` |
| `CYBER_BOTNET_PREDICTION_ENABLED` | Enable botnet prediction | `true` |
| `CYBER_RANSOMWARE_ALERT_ENABLED` | Enable ransomware alerts | `true` |
| `FINANCIAL_FRAUD_DETECTION_ENABLED` | Enable fraud detection | `true` |
| `FINANCIAL_CRYPTO_ANALYSIS_ENABLED` | Enable crypto analysis | `true` |
| `FUSION_STABILITY_SCORE_ENABLED` | Enable stability scoring | `true` |
| `FUSION_EARLY_WARNING_ENABLED` | Enable early warnings | `true` |
| `FUSION_METHOD` | Fusion method (weighted_average, max_risk, ensemble, bayesian) | `ensemble` |

### GitHub Actions

The `nse-selftest.yml` workflow runs:

1. **Unit Tests**: Tests for all 6 AI-NSE modules
2. **Integration Tests**: End-to-end tests with Redis
3. **Security Scan**: Bandit security analysis
4. **Code Quality**: Ruff, Black, and isort checks

## Security Considerations

### Access Control

- All endpoints require authentication
- Clearance-level filtering for sensitive data
- Role-based access control (RBAC) for alert routing
- Audit logging for all operations

### Data Protection

- Encryption at rest for sensitive data
- TLS for all WebSocket connections
- PII redaction in logs
- Secure credential storage

### Compliance

- CJIS-aligned security controls
- Audit trail for all security events
- Data retention policies
- Incident response procedures

## Testing

### Test Suites

1. `test_cyber_intel.py` - Cyber Intelligence Engine tests
2. `test_insider_threat.py` - Insider Threat Engine tests
3. `test_geopolitical_risk.py` - Geopolitical Risk Engine tests
4. `test_financial_crime_intel.py` - Financial Crime Intelligence tests
5. `test_national_risk_fusion.py` - National Risk Fusion Engine tests
6. `test_national_security_alerts.py` - Security Alerts tests

### Running Tests

```bash
# Run all Phase 18 tests
pytest tests/phase18/ -v

# Run specific module tests
pytest tests/phase18/test_cyber_intel.py -v
pytest tests/phase18/test_national_risk_fusion.py -v
```

## Integration with Previous Phases

The AI-NSE integrates with:

- **Phase 17 (GTIE)**: Receives threat intelligence feeds
- **Phase 16 (Fusion Cloud)**: Multi-agency alert sharing
- **Phase 15 (Autonomous Ops)**: Predictive AI integration
- **Phase 14 (Ops Continuity)**: Health monitoring and failover
- **Phase 13 (Intel Orchestration)**: Signal correlation and routing

## Future Enhancements

1. Machine learning models for threat prediction
2. Natural language processing for threat reports
3. Automated response playbooks
4. Integration with external threat feeds
5. Advanced visualization and analytics
6. Mobile push notifications for critical alerts
