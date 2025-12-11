# Phase 26: AI Ethics, Bias Safeguards & Civil Rights Protection Layer

## Overview

Phase 26 implements the full civil rights protection stack for the G3TI RTCC-UIP platform, ensuring compliance with:
- **Riviera Beach, Florida 33404** municipal requirements
- **Florida state law** (Constitution, Statutes)
- **Federal constitutional requirements** (1st, 4th, 14th Amendments)
- **DOJ Guidelines** and **CJIS Security Policy**
- **NIST AI Risk Management Framework**

This phase provides comprehensive bias detection, use-of-force risk assessment, civil liberties compliance validation, protected community safeguards, ethics scoring, and transparency/explainability for all AI-driven decisions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Ethics Guardian Layer                             │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Bias Detection  │  │ Force Risk      │  │ Civil Liberties │         │
│  │ Engine          │  │ Engine          │  │ Engine          │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐         │
│  │ Protected       │  │ Ethics Score    │  │ Transparency    │         │
│  │ Communities     │  │ Engine          │  │ Engine          │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
├─────────────────────────────────────────────────────────────────────────┤
│                           API Layer                                      │
│  POST /api/ethics/check-bias    POST /api/ethics/force-risk             │
│  POST /api/ethics/civil-rights  POST /api/ethics/ethics-score           │
│  GET  /api/ethics/explain/{id}  GET  /api/ethics/audit                  │
│  POST /api/ethics/protected-community                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                        WebSocket Channels                                │
│  /ws/ethics/alerts    /ws/ethics/review    /ws/ethics/audit             │
├─────────────────────────────────────────────────────────────────────────┤
│                        Frontend UI                                       │
│  Bias Monitor | Civil Rights | Ethics Score | Communities | Audit       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Bias Detection Engine

**Location:** `backend/app/ethics_guardian/bias_detection.py`

Detects bias in AI outputs using five fairness metrics:

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Disparate Impact Ratio | Ratio of positive outcomes between groups | ≥ 0.80 (80% rule) |
| Demographic Parity | Difference in positive outcome rates | ≤ 0.10 |
| Equal Opportunity Difference | Difference in true positive rates | ≤ 0.10 |
| Predictive Equality | Difference in false positive rates | ≤ 0.10 |
| Calibration Fairness | Difference in positive predictive values | ≤ 0.10 |

**Analysis Types:**
- PREDICTIVE_AI
- RISK_SCORE
- PATROL_ROUTING
- ENTITY_CORRELATION
- SURVEILLANCE_TRIGGER
- ENFORCEMENT_RECOMMENDATION

**Riviera Beach Demographics (Baseline):**
- Black: 66%
- White: 22%
- Hispanic: 8%
- Asian: 2%
- Other: 2%

**Bias Status Outcomes:**
- `NO_BIAS_DETECTED` - All metrics pass
- `POSSIBLE_BIAS_FLAG_REVIEW` - Some metrics fail, requires review
- `BIAS_DETECTED_BLOCKED` - Critical bias detected, action blocked

### 2. Use-of-Force Risk Engine

**Location:** `backend/app/ethics_guardian/force_risk.py`

Evaluates use-of-force risk using 10 weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Civil Rights Exposure | 20% | Risk of civil rights violation |
| Force Escalation Probability | 15% | Likelihood of force escalation |
| Mental Health Indicators | 15% | Mental health crisis indicators |
| Juvenile Involvement | 15% | Presence of minors |
| Sensitive Location | 10% | Schools, churches, hospitals |
| Protected Class | 10% | Protected community involvement |
| Crowd Presence | 5% | Bystander risk |
| Media Presence | 5% | Public accountability |
| Prior Incidents | 3% | Location history |
| Officer History | 2% | Officer use-of-force history |

**Risk Levels:**
- LOW (0-25): Standard protocols
- MODERATE (26-50): Enhanced caution
- HIGH (51-75): Supervisor notification required
- CRITICAL (76-100): Command staff approval required

**De-escalation Techniques:**
1. Verbal Communication (85% effectiveness)
2. Time and Distance (80% effectiveness)
3. Active Listening (75% effectiveness)
4. Crisis Intervention (70% effectiveness)
5. Tactical Repositioning (65% effectiveness)

**Riviera Beach Sensitive Locations:**
- Riviera Beach High School
- First Baptist Church
- Barracuda Bay Playground
- Riviera Beach Marina
- Palm Beach County Health Department

### 3. Civil Liberties Engine

**Location:** `backend/app/ethics_guardian/civil_liberties.py`

Validates actions against 13 compliance rules:

**Constitutional Framework:**
- **Fourth Amendment:** Warrant requirement, probable cause
- **First Amendment:** Free speech, assembly, religion
- **Fourteenth Amendment:** Equal protection, due process

**State & Local Law:**
- Florida Constitution Art. I, § 23 (Privacy)
- Florida Statute § 934.50 (Drone Surveillance)
- Riviera Beach Municipal Code (Data Retention)

**Federal Guidelines:**
- DOJ Use of Force Policy Framework
- CJIS Security Policy v5.9
- NIST AI Risk Management Framework 1.0

**Warrant Exceptions:**
- Consent
- Exigent circumstances
- Plain view
- Search incident to arrest
- Automobile exception
- Hot pursuit
- Community caretaking

**Data Retention Limits:**
| Data Type | Retention Period |
|-----------|------------------|
| Surveillance Footage | 30 days |
| Drone Footage | 30 days |
| License Plate Data | 90 days |
| Facial Recognition Queries | 365 days |
| Predictive Analytics | 180 days |
| General Records | 2555 days (7 years) |

### 4. Protected Community Safeguards

**Location:** `backend/app/ethics_guardian/protected_communities.py`

Implements safeguards for 7 protected communities in Riviera Beach:

| Community | Population | % | Safeguard Level | Bias Sensitivity |
|-----------|------------|---|-----------------|------------------|
| Black Community | 25,056 | 66% | HIGH | 1.5x |
| Hispanic Community | 3,037 | 8% | ELEVATED | 1.3x |
| LGBTQ+ Youth | 500 | 1.3% | HIGH | 1.5x |
| People with Disabilities | 4,556 | 12% | HIGH | 1.4x |
| Veterans | 2,278 | 6% | ELEVATED | 1.2x |
| Faith Communities | 20,000 | 52.7% | ELEVATED | 1.2x |
| Aging Population (65+) | 5,695 | 15% | ELEVATED | 1.2x |

**Safeguard Rules:**
- Disparate Impact Review (automatic for Black community)
- Over-Surveillance Prevention
- Immigration Enforcement Separation
- Youth Protection Protocol
- ADA Compliance Check
- PTSD-Aware Response
- Religious Freedom Protection
- Elder Protection Protocol

### 5. Ethics Score Engine

**Location:** `backend/app/ethics_guardian/ethics_score.py`

Computes combined ethics score (0-100) based on 8 components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Fairness | 20% | Bias metrics compliance |
| Civil Rights | 20% | Constitutional compliance |
| Use of Force | 15% | Force risk assessment |
| Historical Disparity | 15% | Pattern analysis |
| Policy Compliance | 10% | SOP adherence |
| Transparency | 10% | Explainability |
| Community Impact | 5% | Community effects |
| Accountability | 5% | Documentation |

**Ethics Levels:**
| Level | Score Range | Color | Action |
|-------|-------------|-------|--------|
| EXCELLENT | 90-100 | Green (#22C55E) | ALLOW |
| GOOD | 75-89 | Lime (#84CC16) | ALLOW_WITH_LOGGING |
| ACCEPTABLE | 60-74 | Yellow (#EAB308) | MODIFY |
| CONCERNING | 40-59 | Orange (#F97316) | REVIEW |
| CRITICAL | 0-39 | Red (#EF4444) | BLOCK |

### 6. Transparency & Explainability Engine

**Location:** `backend/app/ethics_guardian/transparency.py`

Generates comprehensive explanations for every decision:

**Explanation Components:**
- Human-readable summary
- Chain of reasoning (step-by-step)
- Legal basis citations
- Data sources used
- Bias metrics summary
- Risk impact summary
- Safeguard triggers
- Alternative actions
- Limitations

**Audit Logging:**
- SHA-256 hash chain for integrity
- Encrypted storage
- Retention based on severity:
  - INFO: 365 days
  - WARNING: 730 days
  - CRITICAL: 2555 days
  - VIOLATION: 2555 days

## API Endpoints

### Bias Detection
```
POST /api/ethics/check-bias
```
Analyzes AI output for potential bias using fairness metrics.

### Force Risk Assessment
```
POST /api/ethics/force-risk
```
Assesses use-of-force risk and provides de-escalation recommendations.

### Civil Rights Compliance
```
POST /api/ethics/civil-rights
```
Validates action against constitutional and legal requirements.

### Ethics Score
```
POST /api/ethics/ethics-score
```
Computes comprehensive ethics score for an action.

### Explanation
```
GET /api/ethics/explain/{action_id}
```
Retrieves human-readable explanation for a decision.

### Audit Log
```
GET /api/ethics/audit
```
Retrieves ethics audit log entries with filtering.

### Protected Community Check
```
POST /api/ethics/protected-community
```
Checks if action triggers protected community safeguards.

## WebSocket Channels

### /ws/ethics/alerts
Real-time alerts for bias detection and ethics violations.

**Message Types:**
- `BIAS_DETECTED` - Bias found in AI output
- `BIAS_POSSIBLE` - Potential bias flagged for review
- `CIVIL_RIGHTS_VIOLATION` - Constitutional concern
- `FORCE_RISK_HIGH` - Elevated force risk
- `ETHICS_SCORE_LOW` - Low ethics score
- `SAFEGUARD_TRIGGERED` - Protected community safeguard
- `ACTION_BLOCKED` - Action blocked by ethics guardian

### /ws/ethics/review
Human review requests for ethics decisions.

**Review Types:**
- `BIAS_REVIEW` - Bias analysis review
- `FORCE_AUTHORIZATION` - Force authorization request
- `CIVIL_RIGHTS_REVIEW` - Civil rights review
- `ETHICS_APPROVAL` - Ethics approval request
- `COMMUNITY_LIAISON` - Community liaison notification
- `ESCALATION` - Command staff escalation

### /ws/ethics/audit
Real-time transparency audit log stream.

## Frontend Components

### 1. Bias Monitor Console
**Location:** `frontend/app/ethics-center/components/BiasMonitorConsole.tsx`

- Real-time bias analysis dashboard
- Disparate impact visualization by demographic group
- Fairness metrics breakdown
- Analysis history with filtering

### 2. Civil Rights Compliance Panel
**Location:** `frontend/app/ethics-center/components/CivilRightsCompliancePanel.tsx`

- Compliance check history
- Active compliance rules (13 rules)
- Data retention limits display
- Violation details and legal citations

### 3. Ethics Score Dashboard
**Location:** `frontend/app/ethics-center/components/EthicsScoreDashboard.tsx`

- Ethics score distribution visualization
- Component score breakdown
- Score history with trends
- Required action indicators

### 4. Protected Communities Viewer
**Location:** `frontend/app/ethics-center/components/ProtectedCommunitiesViewer.tsx`

- Community profiles with demographics
- Safeguard level indicators
- Engagement requirements
- Safeguard trigger history

### 5. Ethics Audit Center
**Location:** `frontend/app/ethics-center/components/EthicsAuditCenter.tsx`

- Audit log viewer with search/filter
- Hash chain integrity verification
- CSV export functionality
- Entry detail view with full context

## Riviera Beach Adaptations

### City Profile
- **Location:** Riviera Beach, Florida 33404
- **Coordinates:** 26.7753°N, 80.0583°W
- **Population:** 37,964
- **Area:** 9.76 square miles

### Demographic Considerations
The system is calibrated for Riviera Beach's unique demographics:
- Majority Black community (66%)
- Significant aging population (15%)
- Active faith community (50+ places of worship)

### Local Compliance
- Riviera Beach Municipal Code data retention requirements
- Palm Beach County coordination protocols
- Florida state law compliance (privacy, drone surveillance)

## Testing

Phase 26 includes 10 comprehensive test suites:

1. **test_bias_detection.py** - Bias detection and fairness metrics
2. **test_civil_liberties.py** - Civil rights validation
3. **test_protected_communities.py** - Protected class safeguards
4. **test_ethics_score.py** - Ethics scoring
5. **test_transparency.py** - Explainability outputs
6. **test_ethics_api.py** - API endpoints
7. **test_ethics_websocket.py** - WebSocket channels
8. **test_policy_conflicts.py** - Policy conflict detection
9. **test_force_risk.py** - Use-of-force risk classification
10. **test_e2e_ethics.py** - End-to-end ethical decision simulation

## DevOps

### GitHub Actions Workflow
**Location:** `.github/workflows/ethics-selftest.yml`

Automated testing includes:
- Bias detection validation
- Civil rights compliance validation
- Model fairness pre-deployment checks
- All 10 test suites

## Integration with Previous Phases

Phase 26 integrates with:
- **Phase 24 (City Autonomy):** Ethics validation before autonomous actions
- **Phase 25 (Constitution):** Legal framework for compliance rules
- **Phase 22 (City Brain):** Ethics scoring for city decisions
- **Phase 15 (Drones):** Drone surveillance compliance
- **Phase 14 (Ops Continuity):** Ethics monitoring health checks

## Security Considerations

- All audit logs are encrypted
- Hash chain ensures tamper detection
- CJIS-compliant data handling
- Role-based access for review workflows
- No PII in explanations without authorization

## Future Enhancements

- Machine learning model for bias prediction
- Automated remediation suggestions
- Community feedback integration
- Real-time disparity monitoring dashboard
- Integration with body camera systems
