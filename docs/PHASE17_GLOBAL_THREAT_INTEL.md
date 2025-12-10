# Phase 17: Global Threat Intelligence Engine (GTIE)

## Overview

The Global Threat Intelligence Engine (GTIE) provides national-level intelligence capabilities for city-level Real-Time Crime Centers. This phase implements a full-spectrum threat intelligence fusion engine that monitors dark web signals, OSINT sources, extremist networks, and global incidents to provide comprehensive situational awareness and proactive threat detection.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Global Threat Intelligence Engine                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Dark Web    │  │    OSINT     │  │  Extremist   │  │   Global     │    │
│  │   Monitor    │  │  Harvester   │  │  Networks    │  │  Incidents   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └────────────┬────┴────────┬────────┴────────┬────────┘             │
│                      │             │                 │                       │
│                      ▼             ▼                 ▼                       │
│              ┌───────────────────────────────────────────┐                  │
│              │        Threat Scoring Engine              │                  │
│              │  - 5-Level Threat Model                   │                  │
│              │  - Cross-Domain Fusion                    │                  │
│              │  - ML-Based Scoring                       │                  │
│              └─────────────────┬─────────────────────────┘                  │
│                                │                                             │
│                                ▼                                             │
│              ┌───────────────────────────────────────────┐                  │
│              │         Threat Alert Manager              │                  │
│              │  - Priority-Based Routing                 │                  │
│              │  - WebSocket Broadcasting                 │                  │
│              │  - Escalation Management                  │                  │
│              └───────────────────────────────────────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Modules

### 1. Dark Web Monitor (`dark_web_monitor/`)

Monitors dark web platforms for threat signals related to weapons trafficking, drug distribution, identity fraud, and other criminal activities.

**Features:**
- Tor crawler interface (stubbed for security)
- Keyword profile management with regex pattern support
- Market listing analysis for weapons, drugs, and fraud
- Threat sentiment scoring with violence and urgency indicators
- Entity and location extraction from content
- Signal prioritization and status tracking

**Signal Types:**
- Weapons trafficking
- Drug trafficking
- Identity fraud
- Cyber threats
- Terrorism-related
- Human trafficking
- Financial crimes
- Counterfeit goods
- General threats

**Market Categories:**
- Weapons, Drugs, Fraud, Counterfeit, Hacking, Malware, Data, Services, Digital Goods, Physical Goods, Chemicals, Documents, Cryptocurrency, Other

### 2. OSINT Harvester (`osint_harvester/`)

Harvests open-source intelligence from news, social media, forums, and other public sources.

**Features:**
- RSS feed management and polling
- News article ingestion with relevance scoring
- Social media signal ingestion
- Hate speech classification (stubbed)
- Keyword spike detection with baseline comparison
- Event prediction for protests and gatherings
- Sentiment analysis

**Source Types:**
- News RSS, News API, Social Twitter, Social Facebook, Social Telegram, Social Reddit, Forum, Blog, Government, Academic, Dark Web, Other

**Content Categories:**
- Crime, Terrorism, Protest, Gang Activity, Drug Activity, Cybersecurity, Public Safety, Weather, Traffic, Politics, Economy, Health, Environment, Other

### 3. Extremist Networks (`extremist_networks/`)

Maps and analyzes extremist networks, tracking individuals, groups, channels, and their connections.

**Features:**
- Network node management (individuals, groups, channels, forums)
- Edge creation with relationship types and confidence scores
- Influence scoring based on reach, engagement, and authority
- Radicalization trajectory analysis with stage tracking
- Cluster detection and analysis
- Network graph export for visualization

**Node Types:**
- Individual, Group, Organization, Channel, Forum, Website, Event, Location, Media, Other

**Ideology Types:**
- White Supremacist, Black Nationalist, Anti-Government, Militia, Anarchist, Religious Extremist, Eco-Terrorist, Accelerationist, Incel, QAnon, Foreign Terrorist, Other

**Radicalization Stages:**
- Pre-radicalization, Self-identification, Indoctrination, Action, Post-action

### 4. Global Incidents (`global_incidents/`)

Monitors global incidents from various feeds including natural disasters, terrorism, civil unrest, and cyber attacks.

**Features:**
- Feed configuration for multiple sources (NASA, USGS, DHS, Interpol, etc.)
- Incident ingestion with severity classification
- Crisis alert creation and management
- Geo-threat correlation with local threats
- Crisis map data generation
- Haversine distance calculation for proximity analysis

**Incident Types:**
- Earthquake, Tsunami, Hurricane, Tornado, Flood, Wildfire, Volcanic Eruption, Pandemic, Terrorism, Mass Shooting, Civil Unrest, Coup, War, Cyber Attack, Infrastructure Failure, Chemical Spill, Nuclear Incident, Famine, Refugee Crisis, Piracy, Kidnapping, Assassination, Other

**Feed Sources:**
- NASA, USGS, NOAA, DHS, FBI, Interpol, UN, WHO, CDC, CISA, State Department, Reuters, AP, Custom

### 5. Threat Scoring Engine (`threat_scoring_engine/`)

Calculates threat scores using ML-based rules and cross-domain fusion algorithms.

**Features:**
- 5-level threat scoring model (Minimal, Low, Moderate, High, Critical)
- Rule-based scoring with multiple rule types
- Cross-domain fusion algorithms (Weighted Average, Max Score, Bayesian, Ensemble, Hierarchical)
- Trigger conditions with cooldown management
- ML model registration and management
- Comprehensive metrics collection

**Threat Domains:**
- Dark Web, OSINT, Extremist Network, Global Incident, Local Crime, Cyber, Terrorism, Gang, Drug, Weapons

**Rule Types:**
- Threshold, Pattern, Temporal, Geographic, Entity, Composite, ML Model

**Trigger Actions:**
- Alert, Escalate, Notify, Log, Block, Monitor, Custom

### 6. Threat Alerts (`threat_alerts/`)

Manages threat alerts with priority-based routing and real-time broadcasting.

**Features:**
- Alert creation with priority and category classification
- Routing rules for destination-based distribution
- Subscription management for personalized alerts
- Alert lifecycle management (acknowledge, escalate, resolve)
- Audit logging for all alert actions
- Statistics and metrics collection

**Alert Priorities:**
- P1 Critical, P2 High, P3 Moderate, P4 Low, P5 Informational

**Alert Destinations:**
- RTCC Dashboard, Tactical Dashboard, Command Center, Dispatch, Mobile Units, Investigations, Intel Hub, Fusion Center, External Agency

## API Endpoints

### Dark Web Monitor
- `GET /api/threat-intel/dark-web/profiles` - Get all keyword profiles
- `POST /api/threat-intel/dark-web/profiles` - Create keyword profile
- `POST /api/threat-intel/dark-web/analyze` - Analyze dark web content
- `POST /api/threat-intel/dark-web/market-listing` - Analyze market listing
- `GET /api/threat-intel/dark-web/signals` - Get dark web signals
- `GET /api/threat-intel/dark-web/signals/high-priority` - Get high priority signals
- `GET /api/threat-intel/dark-web/listings` - Get market listings
- `GET /api/threat-intel/dark-web/metrics` - Get metrics

### OSINT Harvester
- `GET /api/threat-intel/osint/feeds` - Get RSS feeds
- `POST /api/threat-intel/osint/feeds` - Add RSS feed
- `POST /api/threat-intel/osint/articles` - Ingest news article
- `GET /api/threat-intel/osint/articles` - Get articles
- `POST /api/threat-intel/osint/social` - Ingest social signal
- `GET /api/threat-intel/osint/social` - Get social signals
- `GET /api/threat-intel/osint/spikes` - Get keyword spikes
- `POST /api/threat-intel/osint/spikes/detect` - Detect keyword spikes
- `POST /api/threat-intel/osint/predictions` - Create event prediction
- `GET /api/threat-intel/osint/predictions` - Get event predictions
- `GET /api/threat-intel/osint/metrics` - Get metrics

### Extremist Networks
- `POST /api/threat-intel/extremist/nodes` - Add network node
- `GET /api/threat-intel/extremist/nodes` - Get network nodes
- `POST /api/threat-intel/extremist/edges` - Add network edge
- `GET /api/threat-intel/extremist/nodes/{node_id}/connections` - Get connected nodes
- `POST /api/threat-intel/extremist/nodes/{node_id}/influence` - Calculate influence
- `POST /api/threat-intel/extremist/nodes/{node_id}/trajectory` - Analyze trajectory
- `POST /api/threat-intel/extremist/clusters` - Create cluster
- `GET /api/threat-intel/extremist/clusters` - Get clusters
- `POST /api/threat-intel/extremist/clusters/detect` - Detect clusters
- `GET /api/threat-intel/extremist/high-risk` - Get high risk nodes
- `GET /api/threat-intel/extremist/influencers` - Get top influencers
- `GET /api/threat-intel/extremist/graph` - Export network graph
- `GET /api/threat-intel/extremist/metrics` - Get metrics

### Global Incidents
- `POST /api/threat-intel/incidents/feeds` - Configure incident feed
- `GET /api/threat-intel/incidents/feeds` - Get incident feeds
- `POST /api/threat-intel/incidents` - Ingest incident
- `GET /api/threat-intel/incidents` - Get incidents
- `GET /api/threat-intel/incidents/near` - Get incidents near location
- `POST /api/threat-intel/incidents/alerts` - Create crisis alert
- `GET /api/threat-intel/incidents/alerts` - Get crisis alerts
- `GET /api/threat-intel/incidents/map` - Get crisis map data
- `GET /api/threat-intel/incidents/correlations` - Get correlations
- `GET /api/threat-intel/incidents/metrics` - Get metrics

### Threat Scoring
- `POST /api/threat-intel/scoring/rules` - Create scoring rule
- `GET /api/threat-intel/scoring/rules` - Get scoring rules
- `POST /api/threat-intel/scoring/triggers` - Create trigger condition
- `GET /api/threat-intel/scoring/triggers` - Get trigger conditions
- `POST /api/threat-intel/scoring/calculate` - Calculate threat score
- `POST /api/threat-intel/scoring/fuse` - Fuse threat scores
- `GET /api/threat-intel/scoring/scores/{entity_id}` - Get entity scores
- `GET /api/threat-intel/scoring/high-threat` - Get high threat scores
- `GET /api/threat-intel/scoring/metrics` - Get metrics

### Threat Alerts
- `POST /api/threat-intel/alerts` - Create threat alert
- `GET /api/threat-intel/alerts` - Get threat alerts
- `POST /api/threat-intel/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/threat-intel/alerts/{alert_id}/escalate` - Escalate alert
- `POST /api/threat-intel/alerts/{alert_id}/resolve` - Resolve alert
- `GET /api/threat-intel/alerts/destination/{destination}` - Get alerts by destination
- `POST /api/threat-intel/alerts/routing-rules` - Create routing rule
- `GET /api/threat-intel/alerts/routing-rules` - Get routing rules
- `POST /api/threat-intel/alerts/subscriptions` - Create subscription
- `GET /api/threat-intel/alerts/subscriptions/{subscriber_id}` - Get subscriptions
- `GET /api/threat-intel/alerts/audit/{alert_id}` - Get alert audit log
- `GET /api/threat-intel/alerts/statistics` - Get alert statistics
- `GET /api/threat-intel/alerts/metrics` - Get metrics

### Combined
- `GET /api/threat-intel/metrics` - Get all module metrics

## WebSocket Channels

### Main Channel
- `/ws/global-threats` - Main threat intelligence feed (all high-priority signals)

### Module-Specific Channels
- `/ws/global-threats/dark-web` - Dark web signals
- `/ws/global-threats/osint` - OSINT signals and spikes
- `/ws/global-threats/extremist` - Extremist network updates
- `/ws/global-threats/incidents` - Global incident updates
- `/ws/global-threats/alerts` - Threat alerts
- `/ws/global-threats/scoring` - Threat score updates
- `/ws/global-threats/escalations` - Escalated alerts

### Message Types
- `signal` - New signal detected
- `alert` - Threat alert generated
- `update` - Status update
- `score` - Threat score calculated
- `incident` - Global incident reported
- `network` - Network update
- `prediction` - Event prediction
- `spike` - Keyword spike detected
- `correlation` - Geo-threat correlation
- `system` - System message

## Frontend Components

### Dashboard Page: `/global-threat-intel`

**Tabs:**
1. Overview - Combined view of all threat intel
2. Dark Web - Dark web signals and market listings
3. OSINT - News, social signals, and keyword spikes
4. Extremist Networks - Network graph and node analysis
5. Global Incidents - Incident map and crisis alerts
6. Threat Scoring - Scoreboard and fusion timeline

**Components:**
- `DarkWebSignalsPanel` - Dark web signal list and market listings
- `OSINTTrendsPanel` - News articles, social signals, keyword spikes
- `ExtremistNetworksGraph` - Network visualization and node management
- `GlobalIncidentMap` - Interactive incident map with crisis alerts
- `ThreatScoreboard` - Threat score rankings and metrics
- `FusionTimeline` - Chronological view of all threat events

## Threat Scoring Model

### 5-Level Threat Model

| Level | Score Range | Description |
|-------|-------------|-------------|
| Level 1 - Minimal | 0-20 | Low risk, routine monitoring |
| Level 2 - Low | 21-40 | Elevated awareness, standard protocols |
| Level 3 - Moderate | 41-60 | Active monitoring, enhanced protocols |
| Level 4 - High | 61-80 | Immediate attention, tactical response |
| Level 5 - Critical | 81-100 | Emergency response, all resources |

### Cross-Domain Fusion Methods

1. **Weighted Average** - Domain scores weighted by configured importance
2. **Max Score** - Highest domain score determines overall threat
3. **Bayesian** - Probabilistic fusion considering prior probabilities
4. **Ensemble** - Combination of multiple fusion methods
5. **Hierarchical** - Tiered fusion based on domain relationships

## Docker Services

### threat-intel-osint
OSINT harvesting pipeline for news and social media monitoring.

### threat-intel-darkweb
Dark web monitoring pipeline (Tor disabled by default for security).

### threat-intel-scoring
ML-based threat scoring engine with GPU support.

## Configuration

### Environment Variables

```bash
# OSINT Harvester
OSINT_RSS_POLL_INTERVAL=300
OSINT_SOCIAL_POLL_INTERVAL=60
OSINT_SPIKE_DETECTION_ENABLED=true
OSINT_HATE_SPEECH_CLASSIFIER_ENABLED=true

# Dark Web Monitor
DARKWEB_TOR_ENABLED=false
DARKWEB_KEYWORD_DETECTION_ENABLED=true
DARKWEB_MARKET_ANALYSIS_ENABLED=true
DARKWEB_SENTIMENT_SCORING_ENABLED=true

# Threat Scoring
SCORING_ML_ENABLED=true
SCORING_FUSION_METHOD=bayesian
SCORING_ALERT_THRESHOLD=70
```

## Security Considerations

1. **Dark Web Access** - Tor crawler is stubbed by default for security. Enable only in controlled environments with proper authorization.

2. **Data Handling** - All threat intelligence data should be handled according to CJIS security policies.

3. **Access Control** - Implement role-based access control for sensitive threat intelligence.

4. **Audit Logging** - All actions are logged for compliance and accountability.

5. **Encryption** - Sensitive data should be encrypted at rest and in transit.

## Testing

Run Phase 17 tests:

```bash
# Run all Phase 17 tests
pytest tests/phase17/ -v

# Run specific module tests
pytest tests/phase17/test_dark_web_monitor.py -v
pytest tests/phase17/test_osint_harvester.py -v
pytest tests/phase17/test_extremist_networks.py -v
pytest tests/phase17/test_global_incidents.py -v
pytest tests/phase17/test_threat_scoring_engine.py -v
pytest tests/phase17/test_threat_alerts.py -v
```

## Integration with Previous Phases

Phase 17 integrates with:

- **Phase 12 (Data Lake)** - Historical threat data storage and analytics
- **Phase 13 (Intel Orchestration)** - Threat signals feed into orchestration pipelines
- **Phase 14 (Ops Continuity)** - Health monitoring for threat intel services
- **Phase 15 (Autonomous Ops)** - Threat-triggered drone dispatch and sensor correlation
- **Phase 16 (Fusion Cloud)** - Cross-agency threat intelligence sharing

## Future Enhancements

1. Real Tor integration for dark web monitoring (with proper authorization)
2. Advanced ML models for threat prediction
3. Natural language processing for content analysis
4. Real-time video/image analysis for threat detection
5. Integration with external threat intelligence feeds (STIX/TAXII)
6. Automated response playbooks for high-priority threats
