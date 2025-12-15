# Phase 36: Public Safety Guardian

## Community Transparency & Engagement Layer

The Public Safety Guardian is a two-way trust framework between the RTCC and the public, focusing on transparency, accountability, and community engagement without exposing sensitive intelligence or officer safety data.

### Overview

Phase 36 implements a comprehensive community transparency and engagement system for the Riviera Beach Police Department. This module enables public access to aggregated, redacted statistics while protecting sensitive information in compliance with CJIS, VAWA, HIPAA, FERPA, and Florida Public Records laws.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Public Safety Guardian                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Transparency   │  │   Community     │  │   Trust Score   │ │
│  │  Report Engine  │  │   Engagement    │  │     Engine      │ │
│  │                 │  │     Engine      │  │                 │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌───────┴────────┐ │
│  │ Public Feedback │  │  Data Access    │  │   WebSocket    │ │
│  │     Engine      │  │   Validator     │  │    Manager     │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                         REST API Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                      Frontend Dashboard                         │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Modules

#### 1. Transparency Report Engine

Location: `backend/app/public_guardian/transparency_engine.py`

Generates non-sensitive transparency dashboards with weekly, monthly, and quarterly reports.

**Report Types:**
- `CALLS_FOR_SERVICE` - Aggregated call statistics by category
- `RESPONSE_TIMES` - Response time metrics by priority and district
- `USE_OF_FORCE` - Aggregated UOF statistics (no individual incidents)
- `SAFETY_TRENDS` - Crime index and neighborhood safety trends
- `HEATMAP` - Blurred activity heatmaps (500m grid resolution)
- `COMPREHENSIVE` - Combined report with all metrics

**Key Features:**
- Automatic redaction of sensitive data
- Compliance framework tracking
- PDF and JSON export capabilities
- Historical report storage

**Usage:**
```python
from backend.app.public_guardian.transparency_engine import (
    TransparencyReportEngine, ReportType, ReportPeriod
)

engine = TransparencyReportEngine()
report = engine.generate_report(
    report_type=ReportType.COMPREHENSIVE,
    period=ReportPeriod.WEEKLY
)
```

#### 2. Community Engagement Engine

Location: `backend/app/public_guardian/community_engagement.py`

Manages community events and public safety alerts.

**Event Types:**
- Town Hall meetings
- Police Advisory Board meetings
- Community meetings
- Safety workshops
- Youth programs
- Neighborhood Watch
- Police Open House
- Coffee with Cops
- National Night Out

**Alert Types:**
- Safety alerts
- AMBER alerts
- Silver alerts
- Weather emergencies
- Traffic advisories
- Community notices
- Crime prevention tips
- Public safety announcements

**Notification Channels:**
- SMS
- Email
- Mobile push notifications
- Website
- Social media
- Emergency broadcast

**Usage:**
```python
from backend.app.public_guardian.community_engagement import (
    CommunityEngagementEngine, EventType, AlertType
)

engine = CommunityEngagementEngine()
event = engine.create_event(
    name="Monthly Town Hall",
    event_type=EventType.TOWN_HALL,
    location="City Hall",
    start_time=datetime.now() + timedelta(days=7)
)
```

#### 3. Trust Score Engine

Location: `backend/app/public_guardian/trust_score_engine.py`

Calculates and tracks community trust metrics.

**Trust Metrics (10 total):**
| Metric | Weight | Description |
|--------|--------|-------------|
| Crime Reduction | 15% | Year-over-year crime reduction |
| Response Time | 12% | Meeting response time targets |
| Community Interaction | 12% | Community event participation |
| Complaint Resolution | 10% | Complaint handling efficiency |
| Youth Outreach | 10% | Youth program engagement |
| Transparency | 10% | Public information availability |
| Fairness | 12% | Equitable treatment across demographics |
| Accountability | 8% | Internal accountability measures |
| Accessibility | 6% | Service accessibility |
| Communication | 5% | Public communication effectiveness |

**Trust Levels:**
- Very High (80-100)
- High (65-79)
- Moderate (50-64)
- Low (35-49)
- Very Low (0-34)

**Audits:**
- Fairness audit - Validates equitable treatment
- Bias audit - Detects potential algorithmic bias

**Usage:**
```python
from backend.app.public_guardian.trust_score_engine import TrustScoreEngine

engine = TrustScoreEngine()
score = engine.calculate_trust_score()
fairness_result = engine.run_fairness_audit()
```

#### 4. Public Feedback Engine

Location: `backend/app/public_guardian/public_feedback_engine.py`

Handles public feedback submission and sentiment analysis.

**Feedback Types:**
- Survey responses
- Complaints
- Praise
- Suggestions
- Questions
- Concerns
- Requests
- General feedback

**Categories:**
- Response time
- Officer conduct
- Community programs
- Safety concerns
- Traffic
- Noise
- Property crime
- Youth services
- Communication
- Accessibility
- Other

**Features:**
- Sentiment analysis (keyword-based)
- Trend detection
- Neighborhood insights
- Anonymous submission support

**Usage:**
```python
from backend.app.public_guardian.public_feedback_engine import (
    PublicFeedbackEngine, FeedbackType, FeedbackCategory
)

engine = PublicFeedbackEngine()
feedback = engine.submit_feedback(
    feedback_type=FeedbackType.SUGGESTION,
    category=FeedbackCategory.COMMUNITY_PROGRAMS,
    title="Youth Basketball Program",
    content="Would love to see more youth basketball programs...",
    anonymous=True
)
```

#### 5. Public Data Access Validator

Location: `backend/app/public_guardian/data_access_validator.py`

Ensures all public-facing data complies with privacy regulations.

**Compliance Frameworks:**
- CJIS (Criminal Justice Information Services)
- VAWA (Violence Against Women Act)
- HIPAA (Health Insurance Portability and Accountability Act)
- FERPA (Family Educational Rights and Privacy Act)
- Florida Public Records Law
- ADA (Americans with Disabilities Act)
- FCRA (Fair Credit Reporting Act)

**Redaction Types (17 total):**
1. Social Security Numbers
2. Phone Numbers
3. Email Addresses
4. Dates of Birth
5. Juvenile Identifiers
6. Domestic Violence Locations
7. Mental Health Information
8. Medical Information
9. Victim Data
10. Witness Identity
11. Exact Addresses
12. Financial Information
13. Biometric Data
14. Criminal History
15. Immigration Status
16. Sexual Orientation
17. Religious Affiliation

**Usage:**
```python
from backend.app.public_guardian.data_access_validator import (
    PublicDataAccessValidator
)

validator = PublicDataAccessValidator()
redacted_data, result = validator.validate_and_redact(
    "John Doe SSN: 123-45-6789 Phone: 555-123-4567"
)
# Result: "[REDACTED-NAME] SSN: [REDACTED-SSN] Phone: [REDACTED-PHONE]"
```

### REST API Endpoints

Base URL: `/api/public`

#### Transparency Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transparency/report` | Get transparency report |
| GET | `/transparency/weekly` | Get weekly report |
| GET | `/transparency/monthly` | Get monthly report |
| GET | `/transparency/quarterly` | Get quarterly report |
| GET | `/transparency/export/json/{report_id}` | Export report as JSON |
| GET | `/transparency/export/pdf/{report_id}` | Export report as PDF data |

#### Community Engagement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/community/events` | Get upcoming events |
| POST | `/community/event` | Create new event |
| GET | `/community/event/{event_id}` | Get event details |
| POST | `/community/event/{event_id}/cancel` | Cancel event |
| GET | `/community/alerts` | Get active alerts |
| POST | `/community/alert` | Create new alert |
| POST | `/community/alert/{alert_id}/deactivate` | Deactivate alert |

#### Trust Score Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trust-score/current` | Get current trust score |
| GET | `/trust-score/history` | Get score history |
| GET | `/trust-score/breakdown` | Get metric breakdown |
| GET | `/trust-score/neighborhoods` | Get all neighborhood scores |
| GET | `/trust-score/neighborhood/{id}` | Get specific neighborhood |
| GET | `/trust-score/fairness-audit` | Run fairness audit |
| GET | `/trust-score/bias-audit` | Run bias audit |

#### Feedback Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | Submit feedback |
| GET | `/feedback/trends` | Get feedback trends |
| GET | `/feedback/recent` | Get recent feedback |
| GET | `/feedback/neighborhood/{name}` | Get neighborhood insight |
| GET | `/feedback/sentiment` | Get sentiment summary |
| POST | `/feedback/{id}/status` | Update feedback status |

#### Compliance Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/compliance/check` | Check data compliance |
| POST | `/compliance/redact` | Redact sensitive data |
| GET | `/compliance/rules` | Get all redaction rules |
| GET | `/compliance/summary` | Get compliance summary |

### WebSocket Channels

Location: `backend/app/websockets/public_guardian_ws.py`

#### Channel: `/ws/public/engagement`

Real-time community engagement updates.

**Update Types:**
- `new_event` - New community event created
- `event_update` - Event details updated
- `event_cancelled` - Event cancelled
- `event_reminder` - Event reminder
- `new_alert` - New safety alert
- `alert_update` - Alert updated
- `alert_deactivated` - Alert deactivated
- `community_notice` - General community notice

#### Channel: `/ws/public/trust`

Real-time trust score updates.

**Update Types:**
- `score_update` - Overall score changed
- `neighborhood_update` - Neighborhood score changed
- `fairness_audit` - Fairness audit completed
- `bias_audit` - Bias audit completed
- `metric_change` - Individual metric changed
- `trend_alert` - Significant trend detected

#### Channel: `/ws/public/sentiment`

Real-time feedback sentiment updates.

**Update Types:**
- `new_feedback` - New feedback submitted
- `sentiment_shift` - Overall sentiment changed
- `trend_detected` - New trend detected
- `concern_spike` - Spike in concerns
- `praise_spike` - Spike in praise
- `neighborhood_insight` - New neighborhood insight

### Frontend Components

Location: `frontend/app/public-guardian/`

#### Main Page

`page.tsx` - Main Public Guardian dashboard with four tabs:
1. Transparency Dashboard
2. Community Engagement
3. Trust Score
4. Public Feedback

#### Transparency Components

- `TransparencyMetricsPanel.tsx` - Calls for service statistics
- `ResponseTimeCard.tsx` - Response time metrics
- `UOFStatisticsCard.tsx` - Use of force statistics (aggregated)
- `SafetyTrendCharts.tsx` - Safety trend visualizations
- `CommunityHeatmap.tsx` - Blurred activity heatmap

#### Engagement Components

- `EventsList.tsx` - Upcoming community events
- `AlertsFeed.tsx` - Active safety alerts
- `EngagementCalendar.tsx` - Event calendar view

#### Trust Score Components

- `TrustScoreGauge.tsx` - Visual trust score gauge
- `TrustScoreHistoryChart.tsx` - Historical score chart
- `NeighborhoodSentimentMap.tsx` - Neighborhood trust map

#### Feedback Components

- `FeedbackForm.tsx` - Public feedback submission form
- `FeedbackSentimentPanel.tsx` - Sentiment distribution
- `CommonConcernsList.tsx` - Top concerns and recent feedback

### Riviera Beach Neighborhoods

The system tracks trust and engagement for five neighborhoods:

1. **Downtown Riviera Beach** - City center and commercial district
2. **Singer Island** - Coastal residential area
3. **West Riviera Beach** - Western residential neighborhoods
4. **Port of Palm Beach Area** - Port and industrial zone
5. **Riviera Beach Heights** - Northern residential area

### Privacy and Compliance

#### Data Protection Measures

1. **Automatic Redaction** - All public data passes through the validator
2. **Aggregation** - Individual incidents are never exposed
3. **Blurring** - Heatmaps use 500m grid resolution minimum
4. **Exclusions** - DV calls, mental health calls, and juvenile data are excluded

#### Compliance Validation

The system validates compliance with:
- CJIS Security Policy
- VAWA confidentiality requirements
- HIPAA privacy rules
- FERPA student privacy
- Florida Public Records exemptions
- ADA accessibility requirements
- FCRA consumer protection

### Testing

Test suites are located in `tests/phase36/`:

1. `test_transparency_engine.py` - Transparency report tests
2. `test_community_engagement.py` - Event and alert tests
3. `test_trust_score_engine.py` - Trust score calculation tests
4. `test_public_feedback_engine.py` - Feedback and sentiment tests
5. `test_data_access_validator.py` - Redaction and compliance tests
6. `test_public_guardian_api.py` - REST API endpoint tests
7. `test_public_guardian_ws.py` - WebSocket channel tests
8. `test_redaction_compliance.py` - Compliance framework tests
9. `test_sentiment_analysis.py` - Sentiment analysis tests
10. `test_e2e_public_guardian.py` - End-to-end integration tests

### DevOps

GitHub Actions workflow: `.github/workflows/public-guardian-selftest.yml`

**Jobs:**
1. `public-guardian-tests` - Backend module tests
2. `frontend-lint` - Frontend TypeScript checks
3. `compliance-validation` - Compliance framework validation

### Integration with Previous Phases

Phase 36 integrates with:
- **Phase 26** (Ethics Guardian) - Ethical compliance checks
- **Phase 28** (Officer Assist) - Officer conduct metrics
- **Phase 30** (Human Stability) - Mental health call handling
- **Phase 33** (AI Sentinel) - System oversight

### Future Enhancements

1. Multi-language support for community engagement
2. Mobile app integration
3. Real-time translation for feedback
4. Advanced sentiment analysis with ML
5. Predictive community engagement
6. Integration with social media platforms

### Contact

For questions about the Public Safety Guardian module, contact the G3TI RTCC development team.

---

**Phase 36 Version:** 1.0.0  
**Last Updated:** December 2025  
**Author:** Devin AI for G3TI RTCC-UIP
