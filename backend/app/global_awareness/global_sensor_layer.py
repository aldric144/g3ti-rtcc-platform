"""
Phase 32: Multi-Domain Global Sensor Layer

Ingests and normalizes data from multiple global intelligence domains:
- Crisis feeds (GDACS, ReliefWeb, ACLED)
- Conflict indicators (armed conflicts, civil unrest, terrorism)
- Maritime data (AIS, port activity, vessel tracking)
- Aviation data (ADS-B, flight tracking, airspace incidents)
- Cyber signals (threat feeds, vulnerability alerts, attack indicators)
- Economic indicators (market volatility, sanctions, trade disruptions)
- Health signals (disease outbreaks, pandemic indicators)
- Environmental data (climate events, natural disasters)
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class SensorDomain(Enum):
    CRISIS = "crisis"
    CONFLICT = "conflict"
    MARITIME = "maritime"
    AVIATION = "aviation"
    CYBER = "cyber"
    ECONOMIC = "economic"
    HEALTH = "health"
    ENVIRONMENTAL = "environmental"
    GEOPOLITICAL = "geopolitical"
    SUPPLY_CHAIN = "supply_chain"


class DataSource(Enum):
    GDACS = "gdacs"
    RELIEFWEB = "reliefweb"
    ACLED = "acled"
    AIS = "ais"
    ADSB = "adsb"
    THREAT_INTEL = "threat_intel"
    CVE_FEED = "cve_feed"
    WHO = "who"
    NOAA = "noaa"
    USGS = "usgs"
    SANCTIONS_LIST = "sanctions_list"
    TRADE_DATA = "trade_data"
    NEWS_WIRE = "news_wire"
    SOCIAL_OSINT = "social_osint"


class SeverityLevel(Enum):
    INFORMATIONAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class SignalStatus(Enum):
    RAW = "raw"
    VALIDATED = "validated"
    CORRELATED = "correlated"
    ACTIONABLE = "actionable"
    ARCHIVED = "archived"


@dataclass
class GlobalSignal:
    signal_id: str
    domain: SensorDomain
    source: DataSource
    timestamp: datetime
    severity: SeverityLevel
    status: SignalStatus
    title: str
    description: str
    location: dict
    affected_regions: list[str]
    affected_countries: list[str]
    raw_data: dict
    confidence_score: float
    tags: list[str]
    related_entities: list[str]
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        data = f"{self.signal_id}:{self.timestamp.isoformat()}:{self.domain.value}:{self.title}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CrisisEvent:
    event_id: str
    event_type: str
    severity: SeverityLevel
    timestamp: datetime
    location: dict
    affected_population: int
    casualties: int
    displaced: int
    source: DataSource
    description: str
    response_status: str
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.event_id}:{self.timestamp.isoformat()}:{self.event_type}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class MaritimeSignal:
    signal_id: str
    vessel_mmsi: str
    vessel_name: str
    vessel_type: str
    flag_country: str
    position: dict
    speed_knots: float
    heading: float
    destination: str
    eta: Optional[datetime]
    anomaly_type: Optional[str]
    anomaly_score: float
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.signal_id}:{self.vessel_mmsi}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class AviationSignal:
    signal_id: str
    flight_id: str
    aircraft_icao: str
    callsign: str
    origin: str
    destination: str
    position: dict
    altitude_feet: int
    speed_knots: float
    heading: float
    squawk: str
    anomaly_type: Optional[str]
    anomaly_score: float
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.signal_id}:{self.flight_id}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CyberSignal:
    signal_id: str
    threat_type: str
    threat_actor: Optional[str]
    target_sector: str
    target_country: str
    attack_vector: str
    iocs: list[str]
    severity: SeverityLevel
    cve_ids: list[str]
    ttps: list[str]
    timestamp: datetime
    source: DataSource
    confidence_score: float
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.signal_id}:{self.threat_type}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


class GlobalSensorLayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.signals: list[GlobalSignal] = []
        self.crisis_events: list[CrisisEvent] = []
        self.maritime_signals: list[MaritimeSignal] = []
        self.aviation_signals: list[AviationSignal] = []
        self.cyber_signals: list[CyberSignal] = []

        self.data_sources = {
            SensorDomain.CRISIS: [DataSource.GDACS, DataSource.RELIEFWEB, DataSource.ACLED],
            SensorDomain.CONFLICT: [DataSource.ACLED, DataSource.NEWS_WIRE],
            SensorDomain.MARITIME: [DataSource.AIS],
            SensorDomain.AVIATION: [DataSource.ADSB],
            SensorDomain.CYBER: [DataSource.THREAT_INTEL, DataSource.CVE_FEED],
            SensorDomain.HEALTH: [DataSource.WHO],
            SensorDomain.ENVIRONMENTAL: [DataSource.NOAA, DataSource.USGS],
            SensorDomain.ECONOMIC: [DataSource.SANCTIONS_LIST, DataSource.TRADE_DATA],
            SensorDomain.GEOPOLITICAL: [DataSource.NEWS_WIRE, DataSource.SOCIAL_OSINT],
            SensorDomain.SUPPLY_CHAIN: [DataSource.TRADE_DATA, DataSource.AIS],
        }

        self.monitored_regions = [
            "North America", "South America", "Europe", "Africa",
            "Middle East", "Central Asia", "South Asia", "East Asia",
            "Southeast Asia", "Oceania", "Arctic", "Antarctic",
        ]

        self.high_risk_countries = [
            "Syria", "Yemen", "Afghanistan", "Somalia", "Libya",
            "Sudan", "South Sudan", "Myanmar", "Ukraine", "Haiti",
        ]

        self.statistics = {
            "total_signals_ingested": 0,
            "signals_by_domain": {d.value: 0 for d in SensorDomain},
            "signals_by_severity": {s.value: 0 for s in SeverityLevel},
            "last_ingestion_time": None,
        }

    def ingest_crisis_feed(self, feed_data: dict) -> CrisisEvent:
        event = CrisisEvent(
            event_id=f"CE-{uuid.uuid4().hex[:8].upper()}",
            event_type=feed_data.get("event_type", "unknown"),
            severity=SeverityLevel(feed_data.get("severity", 3)),
            timestamp=datetime.utcnow(),
            location={
                "lat": feed_data.get("lat", 0.0),
                "lon": feed_data.get("lon", 0.0),
                "country": feed_data.get("country", "Unknown"),
                "region": feed_data.get("region", "Unknown"),
            },
            affected_population=feed_data.get("affected_population", 0),
            casualties=feed_data.get("casualties", 0),
            displaced=feed_data.get("displaced", 0),
            source=DataSource(feed_data.get("source", "gdacs")),
            description=feed_data.get("description", ""),
            response_status=feed_data.get("response_status", "monitoring"),
        )

        self.crisis_events.append(event)
        self._create_global_signal(event, SensorDomain.CRISIS)
        return event

    def ingest_conflict_indicator(self, indicator_data: dict) -> GlobalSignal:
        signal = GlobalSignal(
            signal_id=f"CI-{uuid.uuid4().hex[:8].upper()}",
            domain=SensorDomain.CONFLICT,
            source=DataSource(indicator_data.get("source", "acled")),
            timestamp=datetime.utcnow(),
            severity=SeverityLevel(indicator_data.get("severity", 3)),
            status=SignalStatus.RAW,
            title=indicator_data.get("title", "Conflict Indicator"),
            description=indicator_data.get("description", ""),
            location={
                "lat": indicator_data.get("lat", 0.0),
                "lon": indicator_data.get("lon", 0.0),
                "country": indicator_data.get("country", "Unknown"),
            },
            affected_regions=[indicator_data.get("region", "Unknown")],
            affected_countries=[indicator_data.get("country", "Unknown")],
            raw_data=indicator_data,
            confidence_score=indicator_data.get("confidence", 0.7),
            tags=indicator_data.get("tags", []),
            related_entities=indicator_data.get("entities", []),
        )

        self.signals.append(signal)
        self._update_statistics(signal)
        return signal

    def ingest_maritime_data(self, ais_data: dict) -> MaritimeSignal:
        anomaly_score = self._calculate_maritime_anomaly(ais_data)
        anomaly_type = None
        if anomaly_score > 0.7:
            anomaly_type = self._classify_maritime_anomaly(ais_data)

        signal = MaritimeSignal(
            signal_id=f"MS-{uuid.uuid4().hex[:8].upper()}",
            vessel_mmsi=ais_data.get("mmsi", ""),
            vessel_name=ais_data.get("vessel_name", "Unknown"),
            vessel_type=ais_data.get("vessel_type", "Unknown"),
            flag_country=ais_data.get("flag", "Unknown"),
            position={
                "lat": ais_data.get("lat", 0.0),
                "lon": ais_data.get("lon", 0.0),
            },
            speed_knots=ais_data.get("speed", 0.0),
            heading=ais_data.get("heading", 0.0),
            destination=ais_data.get("destination", "Unknown"),
            eta=ais_data.get("eta"),
            anomaly_type=anomaly_type,
            anomaly_score=anomaly_score,
            timestamp=datetime.utcnow(),
        )

        self.maritime_signals.append(signal)
        if anomaly_score > 0.5:
            self._create_maritime_alert(signal)
        return signal

    def ingest_aviation_data(self, adsb_data: dict) -> AviationSignal:
        anomaly_score = self._calculate_aviation_anomaly(adsb_data)
        anomaly_type = None
        if anomaly_score > 0.7:
            anomaly_type = self._classify_aviation_anomaly(adsb_data)

        signal = AviationSignal(
            signal_id=f"AS-{uuid.uuid4().hex[:8].upper()}",
            flight_id=adsb_data.get("flight_id", ""),
            aircraft_icao=adsb_data.get("icao", ""),
            callsign=adsb_data.get("callsign", ""),
            origin=adsb_data.get("origin", "Unknown"),
            destination=adsb_data.get("destination", "Unknown"),
            position={
                "lat": adsb_data.get("lat", 0.0),
                "lon": adsb_data.get("lon", 0.0),
            },
            altitude_feet=adsb_data.get("altitude", 0),
            speed_knots=adsb_data.get("speed", 0.0),
            heading=adsb_data.get("heading", 0.0),
            squawk=adsb_data.get("squawk", ""),
            anomaly_type=anomaly_type,
            anomaly_score=anomaly_score,
            timestamp=datetime.utcnow(),
        )

        self.aviation_signals.append(signal)
        if anomaly_score > 0.5:
            self._create_aviation_alert(signal)
        return signal

    def ingest_cyber_signal(self, threat_data: dict) -> CyberSignal:
        signal = CyberSignal(
            signal_id=f"CS-{uuid.uuid4().hex[:8].upper()}",
            threat_type=threat_data.get("threat_type", "unknown"),
            threat_actor=threat_data.get("threat_actor"),
            target_sector=threat_data.get("target_sector", "Unknown"),
            target_country=threat_data.get("target_country", "Unknown"),
            attack_vector=threat_data.get("attack_vector", "Unknown"),
            iocs=threat_data.get("iocs", []),
            severity=SeverityLevel(threat_data.get("severity", 3)),
            cve_ids=threat_data.get("cve_ids", []),
            ttps=threat_data.get("ttps", []),
            timestamp=datetime.utcnow(),
            source=DataSource(threat_data.get("source", "threat_intel")),
            confidence_score=threat_data.get("confidence", 0.7),
        )

        self.cyber_signals.append(signal)
        self._create_global_signal_from_cyber(signal)
        return signal

    def _create_global_signal(self, event: CrisisEvent, domain: SensorDomain) -> GlobalSignal:
        signal = GlobalSignal(
            signal_id=f"GS-{uuid.uuid4().hex[:8].upper()}",
            domain=domain,
            source=event.source,
            timestamp=event.timestamp,
            severity=event.severity,
            status=SignalStatus.VALIDATED,
            title=f"{event.event_type} in {event.location.get('country', 'Unknown')}",
            description=event.description,
            location=event.location,
            affected_regions=[event.location.get("region", "Unknown")],
            affected_countries=[event.location.get("country", "Unknown")],
            raw_data={"event_id": event.event_id},
            confidence_score=0.85,
            tags=[event.event_type, domain.value],
            related_entities=[],
        )

        self.signals.append(signal)
        self._update_statistics(signal)
        return signal

    def _create_global_signal_from_cyber(self, cyber: CyberSignal) -> GlobalSignal:
        signal = GlobalSignal(
            signal_id=f"GS-{uuid.uuid4().hex[:8].upper()}",
            domain=SensorDomain.CYBER,
            source=cyber.source,
            timestamp=cyber.timestamp,
            severity=cyber.severity,
            status=SignalStatus.VALIDATED,
            title=f"Cyber Threat: {cyber.threat_type}",
            description=f"Target: {cyber.target_sector} in {cyber.target_country}",
            location={"country": cyber.target_country},
            affected_regions=[],
            affected_countries=[cyber.target_country],
            raw_data={"signal_id": cyber.signal_id, "iocs": cyber.iocs},
            confidence_score=cyber.confidence_score,
            tags=[cyber.threat_type, "cyber", cyber.attack_vector],
            related_entities=[cyber.threat_actor] if cyber.threat_actor else [],
        )

        self.signals.append(signal)
        self._update_statistics(signal)
        return signal

    def _create_maritime_alert(self, signal: MaritimeSignal):
        global_signal = GlobalSignal(
            signal_id=f"GS-{uuid.uuid4().hex[:8].upper()}",
            domain=SensorDomain.MARITIME,
            source=DataSource.AIS,
            timestamp=signal.timestamp,
            severity=SeverityLevel.HIGH if signal.anomaly_score > 0.8 else SeverityLevel.MODERATE,
            status=SignalStatus.ACTIONABLE,
            title=f"Maritime Anomaly: {signal.anomaly_type}",
            description=f"Vessel {signal.vessel_name} ({signal.vessel_mmsi}) flagged for {signal.anomaly_type}",
            location=signal.position,
            affected_regions=[],
            affected_countries=[signal.flag_country],
            raw_data={"vessel_mmsi": signal.vessel_mmsi, "anomaly_score": signal.anomaly_score},
            confidence_score=signal.anomaly_score,
            tags=["maritime", signal.anomaly_type or "anomaly", signal.vessel_type],
            related_entities=[signal.vessel_name],
        )

        self.signals.append(global_signal)
        self._update_statistics(global_signal)

    def _create_aviation_alert(self, signal: AviationSignal):
        global_signal = GlobalSignal(
            signal_id=f"GS-{uuid.uuid4().hex[:8].upper()}",
            domain=SensorDomain.AVIATION,
            source=DataSource.ADSB,
            timestamp=signal.timestamp,
            severity=SeverityLevel.HIGH if signal.anomaly_score > 0.8 else SeverityLevel.MODERATE,
            status=SignalStatus.ACTIONABLE,
            title=f"Aviation Anomaly: {signal.anomaly_type}",
            description=f"Flight {signal.callsign} flagged for {signal.anomaly_type}",
            location=signal.position,
            affected_regions=[],
            affected_countries=[],
            raw_data={"flight_id": signal.flight_id, "anomaly_score": signal.anomaly_score},
            confidence_score=signal.anomaly_score,
            tags=["aviation", signal.anomaly_type or "anomaly"],
            related_entities=[signal.callsign],
        )

        self.signals.append(global_signal)
        self._update_statistics(global_signal)

    def _calculate_maritime_anomaly(self, ais_data: dict) -> float:
        score = 0.0
        if ais_data.get("ais_off", False):
            score += 0.4
        if ais_data.get("speed", 0) > 25:
            score += 0.2
        if ais_data.get("flag", "") in ["Unknown", "Convenience"]:
            score += 0.2
        if ais_data.get("dark_voyage", False):
            score += 0.3
        if ais_data.get("spoofing_detected", False):
            score += 0.5
        return min(score, 1.0)

    def _classify_maritime_anomaly(self, ais_data: dict) -> str:
        if ais_data.get("spoofing_detected", False):
            return "ais_spoofing"
        if ais_data.get("dark_voyage", False):
            return "dark_voyage"
        if ais_data.get("ais_off", False):
            return "ais_disabled"
        if ais_data.get("speed", 0) > 25:
            return "excessive_speed"
        return "suspicious_behavior"

    def _calculate_aviation_anomaly(self, adsb_data: dict) -> float:
        score = 0.0
        squawk = adsb_data.get("squawk", "")
        if squawk in ["7500", "7600", "7700"]:
            score += 0.8
        if adsb_data.get("altitude", 0) < 500 and adsb_data.get("speed", 0) > 200:
            score += 0.3
        if adsb_data.get("transponder_off", False):
            score += 0.4
        if adsb_data.get("deviation_from_route", 0) > 50:
            score += 0.3
        return min(score, 1.0)

    def _classify_aviation_anomaly(self, adsb_data: dict) -> str:
        squawk = adsb_data.get("squawk", "")
        if squawk == "7500":
            return "hijacking"
        if squawk == "7600":
            return "radio_failure"
        if squawk == "7700":
            return "emergency"
        if adsb_data.get("transponder_off", False):
            return "transponder_disabled"
        return "route_deviation"

    def _update_statistics(self, signal: GlobalSignal):
        self.statistics["total_signals_ingested"] += 1
        self.statistics["signals_by_domain"][signal.domain.value] += 1
        self.statistics["signals_by_severity"][signal.severity.value] += 1
        self.statistics["last_ingestion_time"] = datetime.utcnow().isoformat()

    def get_signals_by_domain(self, domain: SensorDomain) -> list[GlobalSignal]:
        return [s for s in self.signals if s.domain == domain]

    def get_signals_by_severity(self, min_severity: SeverityLevel) -> list[GlobalSignal]:
        return [s for s in self.signals if s.severity.value >= min_severity.value]

    def get_signals_by_region(self, region: str) -> list[GlobalSignal]:
        return [s for s in self.signals if region in s.affected_regions]

    def get_signals_by_country(self, country: str) -> list[GlobalSignal]:
        return [s for s in self.signals if country in s.affected_countries]

    def get_recent_signals(self, hours: int = 24) -> list[GlobalSignal]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [s for s in self.signals if s.timestamp > cutoff]

    def get_actionable_signals(self) -> list[GlobalSignal]:
        return [s for s in self.signals if s.status == SignalStatus.ACTIONABLE]

    def get_statistics(self) -> dict:
        return self.statistics.copy()
