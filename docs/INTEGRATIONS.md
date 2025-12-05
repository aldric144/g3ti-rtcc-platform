# G3TI RTCC-UIP Integrations

## Overview

The RTCC-UIP platform integrates with multiple external systems to provide comprehensive situational awareness. This document describes each integration, its capabilities, and configuration requirements.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Integration Framework                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Base Integration Class                          │    │
│  │                                                                      │    │
│  │  - Connection management                                             │    │
│  │  - Authentication handling                                           │    │
│  │  - Health monitoring                                                 │    │
│  │  - Event normalization                                               │    │
│  │  - Error handling                                                    │    │
│  │  - Audit logging                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Milestone     │    │     Flock       │    │  ShotSpotter    │         │
│  │   Integration   │    │   Integration   │    │   Integration   │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Milestone XProtect VMS

### Overview

Milestone XProtect is a Video Management System (VMS) that provides access to camera feeds, recordings, and video analytics.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Camera List | Retrieve all configured cameras | Implemented |
| Camera Status | Get online/offline status | Implemented |
| Live Stream | Access live video feeds | Placeholder |
| Video Clips | Export video segments | Placeholder |
| Snapshots | Capture still images | Placeholder |
| Motion Events | Receive motion detection alerts | Placeholder |

### Configuration

```env
MILESTONE_API_URL=https://milestone.example.com/api
MILESTONE_API_KEY=your-api-key
MILESTONE_USERNAME=rtcc-service
MILESTONE_PASSWORD=secure-password
```

### Event Types

```python
class CameraAlertEvent:
    event_type: EventType.CAMERA_ALERT
    source: EventSource.MILESTONE
    camera_id: str
    camera_name: str
    alert_type: str  # motion, analytics, manual
    thumbnail_url: str
    recording_url: str
```

### API Methods

```python
class MilestoneIntegration:
    async def get_cameras() -> list[Camera]
    async def get_camera_status(camera_id: str) -> CameraStatus
    async def get_video_clip(camera_id: str, start: datetime, end: datetime) -> str
    async def get_snapshot(camera_id: str) -> bytes
```

---

## Flock Safety LPR

### Overview

Flock Safety provides License Plate Recognition (LPR) capabilities with automatic alerts for vehicles of interest.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Plate Search | Search for specific plates | Implemented |
| Hotlist Management | Manage BOLO lists | Implemented |
| Real-time Alerts | Receive LPR hit notifications | Placeholder |
| Historical Data | Query past plate reads | Placeholder |
| Vehicle Attributes | Color, make, model detection | Placeholder |

### Configuration

```env
FLOCK_API_URL=https://api.flocksafety.com/v1
FLOCK_API_KEY=your-api-key
FLOCK_AGENCY_ID=your-agency-id
```

### Event Types

```python
class FlockLPREvent:
    event_type: EventType.LPR_HIT
    source: EventSource.FLOCK
    plate_number: str
    plate_state: str
    vehicle_make: str
    vehicle_model: str
    vehicle_color: str
    camera_id: str
    camera_location: GeoLocation
    image_url: str
    hotlist_match: str  # stolen, wanted, amber_alert, etc.
```

### API Methods

```python
class FlockIntegration:
    async def search_plate(plate: str, state: str = None) -> list[PlateRead]
    async def get_hotlists() -> list[Hotlist]
    async def add_to_hotlist(hotlist_id: str, plate: str, reason: str) -> bool
    async def remove_from_hotlist(hotlist_id: str, plate: str) -> bool
```

---

## ShotSpotter

### Overview

ShotSpotter provides acoustic gunshot detection with precise location information.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Real-time Alerts | Receive gunshot notifications | Implemented |
| Alert Details | Get detailed alert information | Implemented |
| Audio Clips | Access audio recordings | Placeholder |
| Historical Data | Query past alerts | Placeholder |
| Acknowledgment | Mark alerts as reviewed | Placeholder |

### Configuration

```env
SHOTSPOTTER_API_URL=https://api.shotspotter.com/v2
SHOTSPOTTER_API_KEY=your-api-key
SHOTSPOTTER_AGENCY_ID=your-agency-id
```

### Event Types

```python
class ShotSpotterEvent:
    event_type: EventType.GUNSHOT
    source: EventSource.SHOTSPOTTER
    alert_id: str
    round_count: int
    confidence: float  # 0.0 - 1.0
    location: GeoLocation
    address: str
    audio_url: str
    detected_at: datetime
```

### API Methods

```python
class ShotSpotterIntegration:
    async def get_recent_alerts(hours: int = 24) -> list[Alert]
    async def get_alert_details(alert_id: str) -> AlertDetails
    async def get_audio_clip(alert_id: str) -> str
    async def acknowledge_alert(alert_id: str, notes: str) -> bool
```

---

## OneSolution RMS

### Overview

OneSolution is a Records Management System (RMS) providing access to incident reports, person records, and case information.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Incident Lookup | Retrieve incident details | Implemented |
| Incident Search | Search incidents by criteria | Implemented |
| Person Lookup | Retrieve person records | Implemented |
| Person Search | Search persons by criteria | Implemented |
| Case Management | Access case information | Placeholder |

### Configuration

```env
ONESOLUTION_API_URL=https://rms.example.com/api
ONESOLUTION_API_KEY=your-api-key
ONESOLUTION_AGENCY_ORI=your-ori-code
```

### Event Types

```python
class IncidentEvent:
    event_type: EventType.INCIDENT_CREATED
    source: EventSource.ONESOLUTION
    incident_number: str
    incident_type: str
    location: GeoLocation
    address: str
    reported_at: datetime
    responding_units: list[str]
```

### API Methods

```python
class OneSolutionIntegration:
    async def get_incident(incident_number: str) -> Incident
    async def search_incidents(query: IncidentQuery) -> list[Incident]
    async def get_person(person_id: str) -> Person
    async def search_persons(query: PersonQuery) -> list[Person]
```

---

## NESS (National Enforcement Support System)

### Overview

NESS provides access to national law enforcement databases including NCIC for warrant checks, criminal history, and vehicle registration.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Warrant Check | Query active warrants | Placeholder |
| Criminal History | Retrieve criminal records | Placeholder |
| License Verification | Verify driver's licenses | Placeholder |
| Vehicle Registration | Query vehicle ownership | Placeholder |

### Configuration

```env
NESS_API_URL=https://ness.example.gov/api
NESS_API_KEY=your-api-key
NESS_ORI=your-ori-code
NESS_OPERATOR_ID=operator-id
```

### CJIS Compliance Note

**IMPORTANT**: NESS integration requires strict CJIS compliance:
- All queries must be logged with purpose code
- Operator must be CJIS certified
- Results must not be cached
- Access requires valid law enforcement purpose

### API Methods

```python
class NESSIntegration:
    async def check_warrants(name: str, dob: date) -> list[Warrant]
    async def get_criminal_history(name: str, dob: date) -> CriminalHistory
    async def verify_license(license_number: str, state: str) -> LicenseInfo
    async def lookup_vehicle_registration(plate: str, state: str) -> VehicleRegistration
```

---

## Body-Worn Camera (BWC)

### Overview

Integration with body-worn camera systems for video evidence management.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Recording List | List available recordings | Placeholder |
| Video Access | Stream/download recordings | Placeholder |
| Officer Assignments | Track camera assignments | Placeholder |
| Incident Linking | Link videos to incidents | Placeholder |

### Configuration

```env
BWC_API_URL=https://bwc.example.com/api
BWC_API_KEY=your-api-key
BWC_AGENCY_ID=your-agency-id
```

### API Methods

```python
class BWCIntegration:
    async def get_recordings(officer_id: str, date: date) -> list[Recording]
    async def get_recording_url(recording_id: str) -> str
    async def get_officer_assignments() -> list[Assignment]
    async def link_to_incident(recording_id: str, incident_id: str) -> bool
```

---

## HotSheets (BOLO System)

### Overview

HotSheets manages Be-On-Lookout (BOLO) alerts for wanted persons and vehicles.

### Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| Active BOLOs | List active alerts | Placeholder |
| Create BOLO | Issue new BOLO | Placeholder |
| Cancel BOLO | Cancel existing BOLO | Placeholder |
| Plate Check | Check plate against BOLOs | Placeholder |
| Person Check | Check person against BOLOs | Placeholder |

### Configuration

```env
HOTSHEETS_API_URL=https://hotsheets.example.com/api
HOTSHEETS_API_KEY=your-api-key
HOTSHEETS_AGENCY_ID=your-agency-id
```

### API Methods

```python
class HotSheetsIntegration:
    async def get_active_bolos() -> list[BOLO]
    async def create_bolo(bolo: BOLOCreate) -> BOLO
    async def cancel_bolo(bolo_id: str, reason: str) -> bool
    async def check_plate(plate: str) -> list[BOLO]
    async def check_person(name: str, dob: date) -> list[BOLO]
```

---

## Adding New Integrations

### Step 1: Create Integration Class

```python
# backend/app/integrations/new_system/__init__.py

from app.integrations.base import BaseIntegration

class NewSystemIntegration(BaseIntegration):
    source = "new_system"
    name = "New System Name"
    
    async def connect(self) -> bool:
        # Implement connection logic
        pass
    
    async def health_check(self) -> bool:
        # Implement health check
        pass
    
    def normalize_event(self, raw_event: dict) -> NormalizedEvent:
        # Convert raw event to standard format
        pass
```

### Step 2: Add Configuration

```python
# backend/app/core/config.py

class Settings:
    NEW_SYSTEM_API_URL: str = ""
    NEW_SYSTEM_API_KEY: str = ""
```

### Step 3: Register Integration

```python
# backend/app/integrations/__init__.py

from .new_system import NewSystemIntegration

INTEGRATIONS = {
    # ... existing integrations
    "new_system": NewSystemIntegration,
}
```

### Step 4: Add Event Types

```python
# backend/app/schemas/events.py

class EventType(str, Enum):
    # ... existing types
    NEW_SYSTEM_EVENT = "new_system_event"

class EventSource(str, Enum):
    # ... existing sources
    NEW_SYSTEM = "new_system"
```

## Integration Status Dashboard

The system provides a status dashboard for monitoring integration health:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Integration Status Dashboard                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Integration      Status      Last Check    Latency    Errors (24h)         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Milestone        ● Online    2 min ago     45ms       0                    │
│  Flock            ● Online    1 min ago     120ms      2                    │
│  ShotSpotter      ● Online    30 sec ago    89ms       0                    │
│  OneSolution      ○ Offline   5 min ago     -          15                   │
│  NESS             ● Online    1 min ago     230ms      0                    │
│  BWC              ◐ Degraded  3 min ago     1200ms     5                    │
│  HotSheets        ● Online    2 min ago     67ms       0                    │
│                                                                              │
│  Legend: ● Online  ◐ Degraded  ○ Offline                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| Connection timeout | Network issue | Check firewall rules |
| Authentication failed | Invalid credentials | Verify API key |
| Rate limited | Too many requests | Implement backoff |
| Data format error | API version mismatch | Update integration |

### Debug Logging

Enable debug logging for integrations:

```env
LOG_LEVEL=DEBUG
INTEGRATION_DEBUG=true
```

### Health Check Endpoint

```bash
curl http://localhost:8000/api/v1/system/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "milestone": {"status": "healthy"},
    "flock": {"status": "healthy"},
    "shotspotter": {"status": "healthy"},
    "onesolution": {"status": "unhealthy", "message": "Connection refused"},
    "ness": {"status": "healthy"},
    "bwc": {"status": "degraded", "message": "High latency"},
    "hotsheets": {"status": "healthy"}
  }
}
```
