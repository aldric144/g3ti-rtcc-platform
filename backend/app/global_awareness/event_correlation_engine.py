"""
Phase 32: Global Event Correlation Engine

Cause-effect cascade modeling for global intelligence.

Features:
- Event correlation across domains
- Cascade effect prediction
- Timeline reconstruction
- Pattern detection
- Anomaly identification
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class EventCategory(Enum):
    POLITICAL = "political"
    MILITARY = "military"
    ECONOMIC = "economic"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    TECHNOLOGICAL = "technological"
    HEALTH = "health"
    SECURITY = "security"


class CorrelationType(Enum):
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    THEMATIC = "thematic"
    ACTOR_BASED = "actor_based"
    RESOURCE_BASED = "resource_based"


class CascadeType(Enum):
    LINEAR = "linear"
    BRANCHING = "branching"
    FEEDBACK_LOOP = "feedback_loop"
    AMPLIFYING = "amplifying"
    DAMPENING = "dampening"


class ImpactMagnitude(Enum):
    NEGLIGIBLE = 1
    MINOR = 2
    MODERATE = 3
    SIGNIFICANT = 4
    SEVERE = 5
    CATASTROPHIC = 6


@dataclass
class GlobalEvent:
    event_id: str
    category: EventCategory
    title: str
    description: str
    timestamp: datetime
    location: dict
    affected_regions: list[str]
    affected_countries: list[str]
    actors: list[str]
    impact_magnitude: ImpactMagnitude
    confidence: float
    sources: list[str]
    tags: list[str]
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.event_id}:{self.title}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class EventCorrelation:
    correlation_id: str
    source_event_id: str
    target_event_id: str
    correlation_type: CorrelationType
    strength: float
    confidence: float
    time_lag_hours: int
    evidence: list[str]
    mechanism: str
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.correlation_id}:{self.source_event_id}:{self.target_event_id}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CascadeEffect:
    cascade_id: str
    trigger_event_id: str
    cascade_type: CascadeType
    affected_events: list[str]
    propagation_path: list[dict]
    total_impact_score: float
    time_horizon_days: int
    probability: float
    mitigation_options: list[str]
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.cascade_id}:{self.trigger_event_id}:{self.total_impact_score}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class EventPattern:
    pattern_id: str
    pattern_name: str
    pattern_type: str
    events: list[str]
    frequency: int
    last_occurrence: datetime
    predicted_next: Optional[datetime]
    confidence: float
    description: str
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.pattern_id}:{self.pattern_name}:{self.frequency}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class TimelineReconstruction:
    timeline_id: str
    title: str
    start_date: datetime
    end_date: datetime
    events: list[dict]
    correlations: list[str]
    key_actors: list[str]
    key_locations: list[str]
    narrative_summary: str
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.timeline_id}:{self.title}:{self.start_date.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


class EventCorrelationEngine:
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

        self.events: dict[str, GlobalEvent] = {}
        self.correlations: list[EventCorrelation] = []
        self.cascades: list[CascadeEffect] = []
        self.patterns: list[EventPattern] = []
        self.timelines: list[TimelineReconstruction] = []

        self.correlation_rules = {
            (EventCategory.POLITICAL, EventCategory.ECONOMIC): 0.7,
            (EventCategory.MILITARY, EventCategory.POLITICAL): 0.8,
            (EventCategory.ENVIRONMENTAL, EventCategory.SOCIAL): 0.6,
            (EventCategory.ECONOMIC, EventCategory.SOCIAL): 0.65,
            (EventCategory.HEALTH, EventCategory.ECONOMIC): 0.7,
            (EventCategory.SECURITY, EventCategory.POLITICAL): 0.75,
            (EventCategory.TECHNOLOGICAL, EventCategory.ECONOMIC): 0.6,
        }

        self.cascade_templates = {
            "conflict_escalation": {
                "trigger": EventCategory.MILITARY,
                "effects": [EventCategory.POLITICAL, EventCategory.ECONOMIC, EventCategory.SOCIAL],
                "multiplier": 1.5,
            },
            "economic_crisis": {
                "trigger": EventCategory.ECONOMIC,
                "effects": [EventCategory.SOCIAL, EventCategory.POLITICAL],
                "multiplier": 1.3,
            },
            "pandemic_spread": {
                "trigger": EventCategory.HEALTH,
                "effects": [EventCategory.ECONOMIC, EventCategory.SOCIAL, EventCategory.POLITICAL],
                "multiplier": 1.4,
            },
            "climate_disaster": {
                "trigger": EventCategory.ENVIRONMENTAL,
                "effects": [EventCategory.ECONOMIC, EventCategory.SOCIAL, EventCategory.HEALTH],
                "multiplier": 1.2,
            },
        }

        self.statistics = {
            "total_events": 0,
            "total_correlations": 0,
            "total_cascades": 0,
            "total_patterns": 0,
            "events_by_category": {c.value: 0 for c in EventCategory},
            "correlations_by_type": {t.value: 0 for t in CorrelationType},
        }

    def create_event(
        self,
        category: EventCategory,
        title: str,
        description: str,
        location: dict,
        affected_regions: list[str] = None,
        affected_countries: list[str] = None,
        actors: list[str] = None,
        impact_magnitude: ImpactMagnitude = ImpactMagnitude.MODERATE,
        sources: list[str] = None,
        tags: list[str] = None,
    ) -> GlobalEvent:
        event = GlobalEvent(
            event_id=f"GE-{uuid.uuid4().hex[:8].upper()}",
            category=category,
            title=title,
            description=description,
            timestamp=datetime.utcnow(),
            location=location,
            affected_regions=affected_regions or [],
            affected_countries=affected_countries or [],
            actors=actors or [],
            impact_magnitude=impact_magnitude,
            confidence=0.8,
            sources=sources or [],
            tags=tags or [],
        )

        self.events[event.event_id] = event
        self.statistics["total_events"] += 1
        self.statistics["events_by_category"][category.value] += 1

        self._auto_correlate_event(event)

        return event

    def _auto_correlate_event(self, new_event: GlobalEvent):
        recent_events = [
            e for e in self.events.values()
            if e.event_id != new_event.event_id
            and (new_event.timestamp - e.timestamp).days < 30
        ]

        for existing_event in recent_events:
            correlation_strength = self._calculate_correlation_strength(
                new_event, existing_event
            )

            if correlation_strength > 0.5:
                correlation_type = self._determine_correlation_type(
                    new_event, existing_event
                )

                self.create_correlation(
                    source_event_id=existing_event.event_id,
                    target_event_id=new_event.event_id,
                    correlation_type=correlation_type,
                    strength=correlation_strength,
                )

    def _calculate_correlation_strength(
        self,
        event1: GlobalEvent,
        event2: GlobalEvent,
    ) -> float:
        strength = 0.0

        category_pair = (event1.category, event2.category)
        reverse_pair = (event2.category, event1.category)

        if category_pair in self.correlation_rules:
            strength += self.correlation_rules[category_pair] * 0.4
        elif reverse_pair in self.correlation_rules:
            strength += self.correlation_rules[reverse_pair] * 0.4

        common_regions = set(event1.affected_regions) & set(event2.affected_regions)
        if common_regions:
            strength += 0.2 * min(len(common_regions) / 3, 1.0)

        common_countries = set(event1.affected_countries) & set(event2.affected_countries)
        if common_countries:
            strength += 0.2 * min(len(common_countries) / 3, 1.0)

        common_actors = set(event1.actors) & set(event2.actors)
        if common_actors:
            strength += 0.2 * min(len(common_actors) / 2, 1.0)

        time_diff = abs((event1.timestamp - event2.timestamp).days)
        if time_diff < 7:
            strength += 0.2 * (1 - time_diff / 7)

        return min(strength, 1.0)

    def _determine_correlation_type(
        self,
        event1: GlobalEvent,
        event2: GlobalEvent,
    ) -> CorrelationType:
        time_diff = abs((event1.timestamp - event2.timestamp).total_seconds() / 3600)

        if time_diff < 24:
            return CorrelationType.TEMPORAL

        common_actors = set(event1.actors) & set(event2.actors)
        if common_actors:
            return CorrelationType.ACTOR_BASED

        common_regions = set(event1.affected_regions) & set(event2.affected_regions)
        if common_regions:
            return CorrelationType.SPATIAL

        category_pair = (event1.category, event2.category)
        if category_pair in self.correlation_rules:
            return CorrelationType.CAUSAL

        return CorrelationType.THEMATIC

    def create_correlation(
        self,
        source_event_id: str,
        target_event_id: str,
        correlation_type: CorrelationType,
        strength: float,
        evidence: list[str] = None,
        mechanism: str = None,
    ) -> EventCorrelation:
        source_event = self.events.get(source_event_id)
        target_event = self.events.get(target_event_id)

        time_lag = 0
        if source_event and target_event:
            time_lag = int(
                (target_event.timestamp - source_event.timestamp).total_seconds() / 3600
            )

        correlation = EventCorrelation(
            correlation_id=f"EC-{uuid.uuid4().hex[:8].upper()}",
            source_event_id=source_event_id,
            target_event_id=target_event_id,
            correlation_type=correlation_type,
            strength=strength,
            confidence=0.75,
            time_lag_hours=time_lag,
            evidence=evidence or [],
            mechanism=mechanism or "Automated correlation",
            timestamp=datetime.utcnow(),
        )

        self.correlations.append(correlation)
        self.statistics["total_correlations"] += 1
        self.statistics["correlations_by_type"][correlation_type.value] += 1

        return correlation

    def predict_cascade(
        self,
        trigger_event_id: str,
        time_horizon_days: int = 30,
    ) -> CascadeEffect:
        trigger_event = self.events.get(trigger_event_id)
        if not trigger_event:
            raise ValueError(f"Event {trigger_event_id} not found")

        cascade_type = CascadeType.LINEAR
        affected_events = []
        propagation_path = []
        total_impact = trigger_event.impact_magnitude.value * 10

        template_key = None
        for key, template in self.cascade_templates.items():
            if template["trigger"] == trigger_event.category:
                template_key = key
                break

        if template_key:
            template = self.cascade_templates[template_key]
            cascade_type = CascadeType.BRANCHING

            for i, effect_category in enumerate(template["effects"]):
                effect_impact = (
                    trigger_event.impact_magnitude.value *
                    template["multiplier"] *
                    (0.8 ** i)
                )
                total_impact += effect_impact * 10

                propagation_path.append({
                    "step": i + 1,
                    "category": effect_category.value,
                    "impact": effect_impact,
                    "time_offset_days": (i + 1) * 7,
                })

        related_correlations = [
            c for c in self.correlations
            if c.source_event_id == trigger_event_id
        ]

        for corr in related_correlations:
            affected_events.append(corr.target_event_id)

        probability = 0.6 + (trigger_event.impact_magnitude.value * 0.05)

        mitigation_options = self._generate_mitigation_options(
            trigger_event.category, cascade_type
        )

        cascade = CascadeEffect(
            cascade_id=f"CE-{uuid.uuid4().hex[:8].upper()}",
            trigger_event_id=trigger_event_id,
            cascade_type=cascade_type,
            affected_events=affected_events,
            propagation_path=propagation_path,
            total_impact_score=min(100.0, total_impact),
            time_horizon_days=time_horizon_days,
            probability=min(0.95, probability),
            mitigation_options=mitigation_options,
            timestamp=datetime.utcnow(),
        )

        self.cascades.append(cascade)
        self.statistics["total_cascades"] += 1

        return cascade

    def _generate_mitigation_options(
        self,
        category: EventCategory,
        cascade_type: CascadeType,
    ) -> list[str]:
        options = {
            EventCategory.MILITARY: [
                "Diplomatic intervention",
                "Economic sanctions",
                "Peacekeeping deployment",
                "Arms embargo",
            ],
            EventCategory.ECONOMIC: [
                "Financial stabilization measures",
                "Trade diversification",
                "Emergency funding",
                "Market intervention",
            ],
            EventCategory.HEALTH: [
                "Quarantine measures",
                "Medical resource deployment",
                "Public health campaigns",
                "International coordination",
            ],
            EventCategory.ENVIRONMENTAL: [
                "Disaster relief deployment",
                "Infrastructure reinforcement",
                "Evacuation planning",
                "Resource stockpiling",
            ],
        }

        base_options = options.get(category, ["Monitor situation", "Prepare contingencies"])

        if cascade_type == CascadeType.AMPLIFYING:
            base_options.insert(0, "URGENT: Break amplification cycle")

        return base_options

    def detect_patterns(self, min_frequency: int = 2) -> list[EventPattern]:
        category_sequences = {}

        sorted_events = sorted(self.events.values(), key=lambda e: e.timestamp)

        for i, event in enumerate(sorted_events):
            if i < len(sorted_events) - 1:
                next_event = sorted_events[i + 1]
                sequence = (event.category.value, next_event.category.value)

                if sequence not in category_sequences:
                    category_sequences[sequence] = []
                category_sequences[sequence].append((event, next_event))

        new_patterns = []
        for sequence, occurrences in category_sequences.items():
            if len(occurrences) >= min_frequency:
                pattern = EventPattern(
                    pattern_id=f"EP-{uuid.uuid4().hex[:8].upper()}",
                    pattern_name=f"{sequence[0]} -> {sequence[1]} Pattern",
                    pattern_type="sequential",
                    events=[e[0].event_id for e in occurrences],
                    frequency=len(occurrences),
                    last_occurrence=occurrences[-1][0].timestamp,
                    predicted_next=None,
                    confidence=0.6 + (len(occurrences) * 0.05),
                    description=f"Pattern of {sequence[0]} events followed by {sequence[1]} events",
                )

                new_patterns.append(pattern)
                self.patterns.append(pattern)
                self.statistics["total_patterns"] += 1

        return new_patterns

    def reconstruct_timeline(
        self,
        title: str,
        start_date: datetime,
        end_date: datetime,
        filter_categories: list[EventCategory] = None,
        filter_regions: list[str] = None,
    ) -> TimelineReconstruction:
        filtered_events = [
            e for e in self.events.values()
            if start_date <= e.timestamp <= end_date
        ]

        if filter_categories:
            filtered_events = [
                e for e in filtered_events
                if e.category in filter_categories
            ]

        if filter_regions:
            filtered_events = [
                e for e in filtered_events
                if any(r in e.affected_regions for r in filter_regions)
            ]

        sorted_events = sorted(filtered_events, key=lambda e: e.timestamp)

        event_dicts = [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "title": e.title,
                "category": e.category.value,
                "impact": e.impact_magnitude.value,
            }
            for e in sorted_events
        ]

        event_ids = {e.event_id for e in sorted_events}
        relevant_correlations = [
            c.correlation_id for c in self.correlations
            if c.source_event_id in event_ids or c.target_event_id in event_ids
        ]

        all_actors = set()
        all_locations = set()
        for e in sorted_events:
            all_actors.update(e.actors)
            all_locations.update(e.affected_countries)

        narrative = self._generate_narrative(sorted_events)

        timeline = TimelineReconstruction(
            timeline_id=f"TL-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            start_date=start_date,
            end_date=end_date,
            events=event_dicts,
            correlations=relevant_correlations,
            key_actors=list(all_actors)[:10],
            key_locations=list(all_locations)[:10],
            narrative_summary=narrative,
        )

        self.timelines.append(timeline)
        return timeline

    def _generate_narrative(self, events: list[GlobalEvent]) -> str:
        if not events:
            return "No events in the specified timeframe."

        narrative_parts = []
        narrative_parts.append(
            f"Timeline covers {len(events)} events from "
            f"{events[0].timestamp.strftime('%Y-%m-%d')} to "
            f"{events[-1].timestamp.strftime('%Y-%m-%d')}."
        )

        category_counts = {}
        for e in events:
            category_counts[e.category.value] = category_counts.get(e.category.value, 0) + 1

        dominant_category = max(category_counts, key=category_counts.get)
        narrative_parts.append(
            f"Primary focus: {dominant_category} events ({category_counts[dominant_category]} occurrences)."
        )

        high_impact = [e for e in events if e.impact_magnitude.value >= 4]
        if high_impact:
            narrative_parts.append(
                f"Notable high-impact events: {', '.join(e.title for e in high_impact[:3])}."
            )

        return " ".join(narrative_parts)

    def get_event(self, event_id: str) -> Optional[GlobalEvent]:
        return self.events.get(event_id)

    def get_correlations_for_event(self, event_id: str) -> list[EventCorrelation]:
        return [
            c for c in self.correlations
            if c.source_event_id == event_id or c.target_event_id == event_id
        ]

    def get_recent_events(self, hours: int = 24) -> list[GlobalEvent]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [e for e in self.events.values() if e.timestamp > cutoff]

    def get_events_by_category(self, category: EventCategory) -> list[GlobalEvent]:
        return [e for e in self.events.values() if e.category == category]

    def get_statistics(self) -> dict:
        return self.statistics.copy()
