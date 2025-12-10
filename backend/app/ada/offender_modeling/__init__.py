"""
Phase 20: Offender Modeling Module

Provides behavioral signature analysis, offender prediction, MO clustering,
and unknown suspect profiling for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid
import math


class BehaviorCategory(str, Enum):
    MODUS_OPERANDI = "modus_operandi"
    SIGNATURE = "signature"
    RITUAL = "ritual"
    TROPHY_TAKING = "trophy_taking"
    STAGING = "staging"
    PRECAUTIONARY = "precautionary"
    OPPORTUNISTIC = "opportunistic"
    ORGANIZED = "organized"
    DISORGANIZED = "disorganized"


class OffenseType(str, Enum):
    HOMICIDE = "homicide"
    ASSAULT = "assault"
    ROBBERY = "robbery"
    BURGLARY = "burglary"
    THEFT = "theft"
    ARSON = "arson"
    SEXUAL_ASSAULT = "sexual_assault"
    KIDNAPPING = "kidnapping"
    FRAUD = "fraud"
    DRUG_OFFENSE = "drug_offense"
    VANDALISM = "vandalism"
    OTHER = "other"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProfileConfidence(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class BehavioralSignature:
    signature_id: str
    case_id: str
    offender_id: Optional[str]
    category: BehaviorCategory
    behaviors: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    frequency_score: float = 0.0
    uniqueness_score: float = 0.0
    consistency_score: float = 0.0
    overall_score: float = 0.0
    linked_cases: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OffenderPrediction:
    prediction_id: str
    offender_id: Optional[str]
    signature_id: str
    predicted_offense_type: OffenseType
    predicted_location: Dict[str, float]
    predicted_timeframe: Dict[str, Any]
    risk_level: RiskLevel
    confidence_score: float
    contributing_factors: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MOCluster:
    cluster_id: str
    cluster_name: str
    offense_type: OffenseType
    case_ids: List[str] = field(default_factory=list)
    common_behaviors: List[Dict[str, Any]] = field(default_factory=list)
    geographic_center: Optional[Dict[str, float]] = None
    temporal_pattern: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.7
    cluster_confidence: float = 0.0
    potential_offender_count: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SuspectProfile:
    profile_id: str
    case_ids: List[str]
    profile_type: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    psychological_traits: List[str] = field(default_factory=list)
    behavioral_indicators: List[str] = field(default_factory=list)
    geographic_profile: Dict[str, Any] = field(default_factory=dict)
    temporal_profile: Dict[str, Any] = field(default_factory=dict)
    victimology_preferences: Dict[str, Any] = field(default_factory=dict)
    modus_operandi: List[str] = field(default_factory=list)
    signature_behaviors: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    confidence: ProfileConfidence = ProfileConfidence.LOW
    confidence_score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "ada_profiler"
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BehavioralSignatureEngine:
    """Analyzes and extracts behavioral signatures from crime data."""

    def __init__(self):
        self._signatures: Dict[str, BehavioralSignature] = {}
        self._case_signatures: Dict[str, List[str]] = {}

    def analyze_case(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        offender_id: Optional[str] = None,
    ) -> List[BehavioralSignature]:
        signatures = []

        mo_signature = self._extract_modus_operandi(case_id, case_data, offender_id)
        if mo_signature:
            signatures.append(mo_signature)

        sig_signature = self._extract_signature_behaviors(case_id, case_data, offender_id)
        if sig_signature:
            signatures.append(sig_signature)

        precautionary = self._extract_precautionary_acts(case_id, case_data, offender_id)
        if precautionary:
            signatures.append(precautionary)

        self._case_signatures[case_id] = [s.signature_id for s in signatures]

        return signatures

    def _extract_modus_operandi(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        offender_id: Optional[str],
    ) -> Optional[BehavioralSignature]:
        signature_id = f"sig-mo-{uuid.uuid4().hex[:12]}"

        behaviors = []
        patterns = []

        entry_method = case_data.get("entry_method")
        if entry_method:
            behaviors.append({"type": "entry_method", "value": entry_method})
            patterns.append(f"entry:{entry_method}")

        weapon_used = case_data.get("weapon_used")
        if weapon_used:
            behaviors.append({"type": "weapon", "value": weapon_used})
            patterns.append(f"weapon:{weapon_used}")

        time_of_day = case_data.get("time_of_day")
        if time_of_day:
            behaviors.append({"type": "time_preference", "value": time_of_day})
            patterns.append(f"time:{time_of_day}")

        target_type = case_data.get("target_type")
        if target_type:
            behaviors.append({"type": "target_selection", "value": target_type})
            patterns.append(f"target:{target_type}")

        approach_method = case_data.get("approach_method")
        if approach_method:
            behaviors.append({"type": "approach", "value": approach_method})
            patterns.append(f"approach:{approach_method}")

        if not behaviors:
            return None

        signature = BehavioralSignature(
            signature_id=signature_id,
            case_id=case_id,
            offender_id=offender_id,
            category=BehaviorCategory.MODUS_OPERANDI,
            behaviors=behaviors,
            patterns=patterns,
            frequency_score=0.5,
            uniqueness_score=0.3,
            consistency_score=0.6,
            overall_score=0.47,
        )
        self._signatures[signature_id] = signature
        return signature

    def _extract_signature_behaviors(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        offender_id: Optional[str],
    ) -> Optional[BehavioralSignature]:
        signature_id = f"sig-beh-{uuid.uuid4().hex[:12]}"

        behaviors = []
        patterns = []

        post_offense = case_data.get("post_offense_behavior")
        if post_offense:
            behaviors.append({"type": "post_offense", "value": post_offense})
            patterns.append(f"post:{post_offense}")

        trophy_taken = case_data.get("trophy_taken")
        if trophy_taken:
            behaviors.append({"type": "trophy", "value": trophy_taken})
            patterns.append(f"trophy:{trophy_taken}")

        staging = case_data.get("scene_staging")
        if staging:
            behaviors.append({"type": "staging", "value": staging})
            patterns.append(f"staging:{staging}")

        ritual = case_data.get("ritual_behavior")
        if ritual:
            behaviors.append({"type": "ritual", "value": ritual})
            patterns.append(f"ritual:{ritual}")

        if not behaviors:
            return None

        uniqueness = min(1.0, len(behaviors) * 0.25)

        signature = BehavioralSignature(
            signature_id=signature_id,
            case_id=case_id,
            offender_id=offender_id,
            category=BehaviorCategory.SIGNATURE,
            behaviors=behaviors,
            patterns=patterns,
            frequency_score=0.3,
            uniqueness_score=uniqueness,
            consistency_score=0.7,
            overall_score=(0.3 + uniqueness + 0.7) / 3,
        )
        self._signatures[signature_id] = signature
        return signature

    def _extract_precautionary_acts(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        offender_id: Optional[str],
    ) -> Optional[BehavioralSignature]:
        signature_id = f"sig-pre-{uuid.uuid4().hex[:12]}"

        behaviors = []
        patterns = []

        forensic_awareness = case_data.get("forensic_awareness")
        if forensic_awareness:
            behaviors.append({"type": "forensic_countermeasure", "value": forensic_awareness})
            patterns.append(f"forensic:{forensic_awareness}")

        disguise = case_data.get("disguise_used")
        if disguise:
            behaviors.append({"type": "disguise", "value": disguise})
            patterns.append(f"disguise:{disguise}")

        escape_route = case_data.get("escape_planning")
        if escape_route:
            behaviors.append({"type": "escape", "value": escape_route})
            patterns.append(f"escape:{escape_route}")

        if not behaviors:
            return None

        signature = BehavioralSignature(
            signature_id=signature_id,
            case_id=case_id,
            offender_id=offender_id,
            category=BehaviorCategory.PRECAUTIONARY,
            behaviors=behaviors,
            patterns=patterns,
            frequency_score=0.4,
            uniqueness_score=0.5,
            consistency_score=0.6,
            overall_score=0.5,
        )
        self._signatures[signature_id] = signature
        return signature

    def compare_signatures(
        self,
        signature_id_1: str,
        signature_id_2: str,
    ) -> float:
        sig1 = self._signatures.get(signature_id_1)
        sig2 = self._signatures.get(signature_id_2)

        if not sig1 or not sig2:
            return 0.0

        if sig1.category != sig2.category:
            return 0.0

        patterns1 = set(sig1.patterns)
        patterns2 = set(sig2.patterns)

        if not patterns1 or not patterns2:
            return 0.0

        intersection = patterns1.intersection(patterns2)
        union = patterns1.union(patterns2)

        jaccard = len(intersection) / len(union) if union else 0.0

        return jaccard

    def find_similar_signatures(
        self,
        signature_id: str,
        threshold: float = 0.5,
    ) -> List[Tuple[str, float]]:
        target = self._signatures.get(signature_id)
        if not target:
            return []

        similar = []
        for sig_id, sig in self._signatures.items():
            if sig_id == signature_id:
                continue
            if sig.category != target.category:
                continue

            similarity = self.compare_signatures(signature_id, sig_id)
            if similarity >= threshold:
                similar.append((sig_id, similarity))

        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    def link_cases_by_signature(
        self,
        signature_id: str,
        threshold: float = 0.6,
    ) -> List[str]:
        similar = self.find_similar_signatures(signature_id, threshold)

        linked_cases = []
        for sig_id, _ in similar:
            sig = self._signatures.get(sig_id)
            if sig and sig.case_id not in linked_cases:
                linked_cases.append(sig.case_id)

        target = self._signatures.get(signature_id)
        if target:
            target.linked_cases = linked_cases
            target.updated_at = datetime.utcnow()

        return linked_cases

    def get_signature(self, signature_id: str) -> Optional[BehavioralSignature]:
        return self._signatures.get(signature_id)

    def get_case_signatures(self, case_id: str) -> List[BehavioralSignature]:
        sig_ids = self._case_signatures.get(case_id, [])
        return [self._signatures[sid] for sid in sig_ids if sid in self._signatures]

    def get_metrics(self) -> Dict[str, Any]:
        signatures = list(self._signatures.values())
        return {
            "total_signatures": len(signatures),
            "by_category": {
                cat.value: len([s for s in signatures if s.category == cat])
                for cat in BehaviorCategory
            },
            "average_score": (
                sum(s.overall_score for s in signatures) / len(signatures)
                if signatures else 0.0
            ),
            "cases_analyzed": len(self._case_signatures),
        }


class OffenderPredictionModel:
    """Predicts future offenses based on behavioral patterns."""

    def __init__(self, signature_engine: BehavioralSignatureEngine):
        self._signature_engine = signature_engine
        self._predictions: Dict[str, OffenderPrediction] = {}
        self._offense_history: Dict[str, List[Dict[str, Any]]] = {}

    def record_offense(
        self,
        offender_id: str,
        offense_type: OffenseType,
        location: Dict[str, float],
        timestamp: datetime,
        case_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        if offender_id not in self._offense_history:
            self._offense_history[offender_id] = []

        self._offense_history[offender_id].append({
            "offense_type": offense_type,
            "location": location,
            "timestamp": timestamp,
            "case_id": case_id,
            "details": details or {},
        })

    def predict_next_offense(
        self,
        offender_id: Optional[str] = None,
        signature_id: Optional[str] = None,
    ) -> Optional[OffenderPrediction]:
        if not offender_id and not signature_id:
            return None

        prediction_id = f"pred-{uuid.uuid4().hex[:12]}"

        if offender_id and offender_id in self._offense_history:
            history = self._offense_history[offender_id]
            return self._predict_from_history(prediction_id, offender_id, signature_id or "", history)

        if signature_id:
            signature = self._signature_engine.get_signature(signature_id)
            if signature:
                return self._predict_from_signature(prediction_id, signature)

        return None

    def _predict_from_history(
        self,
        prediction_id: str,
        offender_id: str,
        signature_id: str,
        history: List[Dict[str, Any]],
    ) -> OffenderPrediction:
        offense_counts: Dict[str, int] = {}
        for offense in history:
            ot = offense["offense_type"]
            if isinstance(ot, OffenseType):
                ot = ot.value
            offense_counts[ot] = offense_counts.get(ot, 0) + 1

        most_common = max(offense_counts.items(), key=lambda x: x[1])[0]
        predicted_type = OffenseType(most_common)

        locations = [o["location"] for o in history if o.get("location")]
        if locations:
            avg_lat = sum(l.get("lat", 0) for l in locations) / len(locations)
            avg_lng = sum(l.get("lng", 0) for l in locations) / len(locations)
            predicted_location = {"lat": avg_lat, "lng": lng, "radius_km": 5.0}
        else:
            predicted_location = {"lat": 0, "lng": 0, "radius_km": 10.0}

        timestamps = [o["timestamp"] for o in history if o.get("timestamp")]
        if len(timestamps) >= 2:
            timestamps.sort()
            intervals = []
            for i in range(1, len(timestamps)):
                delta = (timestamps[i] - timestamps[i-1]).days
                intervals.append(delta)
            avg_interval = sum(intervals) / len(intervals)
            next_date = timestamps[-1] + timedelta(days=int(avg_interval))
            predicted_timeframe = {
                "earliest": timestamps[-1].isoformat(),
                "most_likely": next_date.isoformat(),
                "latest": (next_date + timedelta(days=int(avg_interval * 0.5))).isoformat(),
            }
        else:
            predicted_timeframe = {
                "earliest": datetime.utcnow().isoformat(),
                "most_likely": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "latest": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            }

        offense_count = len(history)
        if offense_count >= 5:
            risk_level = RiskLevel.CRITICAL
        elif offense_count >= 3:
            risk_level = RiskLevel.HIGH
        elif offense_count >= 2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        confidence = min(0.9, 0.3 + offense_count * 0.1)

        prediction = OffenderPrediction(
            prediction_id=prediction_id,
            offender_id=offender_id,
            signature_id=signature_id,
            predicted_offense_type=predicted_type,
            predicted_location=predicted_location,
            predicted_timeframe=predicted_timeframe,
            risk_level=risk_level,
            confidence_score=confidence,
            contributing_factors=[
                {"factor": "offense_history", "weight": 0.4, "value": offense_count},
                {"factor": "pattern_consistency", "weight": 0.3, "value": offense_counts.get(most_common, 0) / offense_count},
                {"factor": "recency", "weight": 0.3, "value": 0.8},
            ],
            recommended_actions=[
                "Increase patrol in predicted area",
                "Alert potential targets",
                "Review surveillance footage",
                "Coordinate with neighboring jurisdictions",
            ],
        )
        self._predictions[prediction_id] = prediction
        return prediction

    def _predict_from_signature(
        self,
        prediction_id: str,
        signature: BehavioralSignature,
    ) -> OffenderPrediction:
        offense_type = OffenseType.OTHER
        for behavior in signature.behaviors:
            if behavior.get("type") == "target_selection":
                target = behavior.get("value", "")
                if "person" in target.lower():
                    offense_type = OffenseType.ASSAULT
                elif "property" in target.lower():
                    offense_type = OffenseType.BURGLARY
                break

        prediction = OffenderPrediction(
            prediction_id=prediction_id,
            offender_id=signature.offender_id,
            signature_id=signature.signature_id,
            predicted_offense_type=offense_type,
            predicted_location={"lat": 0, "lng": 0, "radius_km": 15.0},
            predicted_timeframe={
                "earliest": datetime.utcnow().isoformat(),
                "most_likely": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "latest": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            },
            risk_level=RiskLevel.MEDIUM,
            confidence_score=signature.overall_score * 0.7,
            contributing_factors=[
                {"factor": "signature_strength", "weight": 0.5, "value": signature.overall_score},
                {"factor": "pattern_uniqueness", "weight": 0.3, "value": signature.uniqueness_score},
                {"factor": "consistency", "weight": 0.2, "value": signature.consistency_score},
            ],
            recommended_actions=[
                "Monitor for similar behavioral patterns",
                "Cross-reference with unsolved cases",
                "Establish surveillance in likely areas",
            ],
        )
        self._predictions[prediction_id] = prediction
        return prediction

    def get_prediction(self, prediction_id: str) -> Optional[OffenderPrediction]:
        return self._predictions.get(prediction_id)

    def get_offender_predictions(self, offender_id: str) -> List[OffenderPrediction]:
        return [
            p for p in self._predictions.values()
            if p.offender_id == offender_id
        ]

    def get_high_risk_predictions(self) -> List[OffenderPrediction]:
        return [
            p for p in self._predictions.values()
            if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]


class ModusOperandiClusterer:
    """Clusters unsolved cases by modus operandi similarity."""

    def __init__(self, signature_engine: BehavioralSignatureEngine):
        self._signature_engine = signature_engine
        self._clusters: Dict[str, MOCluster] = {}

    def cluster_cases(
        self,
        case_ids: List[str],
        offense_type: OffenseType,
        similarity_threshold: float = 0.6,
    ) -> List[MOCluster]:
        case_signatures: Dict[str, List[BehavioralSignature]] = {}
        for case_id in case_ids:
            sigs = self._signature_engine.get_case_signatures(case_id)
            mo_sigs = [s for s in sigs if s.category == BehaviorCategory.MODUS_OPERANDI]
            if mo_sigs:
                case_signatures[case_id] = mo_sigs

        if len(case_signatures) < 2:
            return []

        clusters = []
        clustered_cases = set()

        case_list = list(case_signatures.keys())
        for i, case_id in enumerate(case_list):
            if case_id in clustered_cases:
                continue

            cluster_cases = [case_id]
            clustered_cases.add(case_id)

            for j in range(i + 1, len(case_list)):
                other_case = case_list[j]
                if other_case in clustered_cases:
                    continue

                similarity = self._calculate_case_similarity(
                    case_signatures[case_id],
                    case_signatures[other_case],
                )

                if similarity >= similarity_threshold:
                    cluster_cases.append(other_case)
                    clustered_cases.add(other_case)

            if len(cluster_cases) >= 2:
                cluster = self._create_cluster(
                    cluster_cases,
                    offense_type,
                    case_signatures,
                    similarity_threshold,
                )
                clusters.append(cluster)

        return clusters

    def _calculate_case_similarity(
        self,
        sigs1: List[BehavioralSignature],
        sigs2: List[BehavioralSignature],
    ) -> float:
        if not sigs1 or not sigs2:
            return 0.0

        max_similarity = 0.0
        for s1 in sigs1:
            for s2 in sigs2:
                sim = self._signature_engine.compare_signatures(
                    s1.signature_id,
                    s2.signature_id,
                )
                max_similarity = max(max_similarity, sim)

        return max_similarity

    def _create_cluster(
        self,
        case_ids: List[str],
        offense_type: OffenseType,
        case_signatures: Dict[str, List[BehavioralSignature]],
        threshold: float,
    ) -> MOCluster:
        cluster_id = f"cluster-{uuid.uuid4().hex[:12]}"

        all_behaviors = []
        for case_id in case_ids:
            for sig in case_signatures.get(case_id, []):
                all_behaviors.extend(sig.behaviors)

        behavior_counts: Dict[str, int] = {}
        for b in all_behaviors:
            key = f"{b.get('type')}:{b.get('value')}"
            behavior_counts[key] = behavior_counts.get(key, 0) + 1

        common_behaviors = [
            {"behavior": k, "frequency": v / len(case_ids)}
            for k, v in behavior_counts.items()
            if v >= len(case_ids) * 0.5
        ]

        cluster = MOCluster(
            cluster_id=cluster_id,
            cluster_name=f"{offense_type.value.title()} Cluster {cluster_id[-6:]}",
            offense_type=offense_type,
            case_ids=case_ids,
            common_behaviors=common_behaviors,
            similarity_threshold=threshold,
            cluster_confidence=min(0.9, 0.5 + len(case_ids) * 0.1),
            potential_offender_count=1,
        )
        self._clusters[cluster_id] = cluster
        return cluster

    def get_cluster(self, cluster_id: str) -> Optional[MOCluster]:
        return self._clusters.get(cluster_id)

    def get_clusters(
        self,
        offense_type: Optional[OffenseType] = None,
        min_cases: int = 2,
    ) -> List[MOCluster]:
        results = list(self._clusters.values())

        if offense_type:
            results = [c for c in results if c.offense_type == offense_type]

        results = [c for c in results if len(c.case_ids) >= min_cases]

        return results

    def add_case_to_cluster(
        self,
        cluster_id: str,
        case_id: str,
    ) -> Optional[MOCluster]:
        cluster = self._clusters.get(cluster_id)
        if not cluster:
            return None

        if case_id not in cluster.case_ids:
            cluster.case_ids.append(case_id)
            cluster.updated_at = datetime.utcnow()

        return cluster


class UnknownSuspectProfiler:
    """Generates AI-powered profiles for unknown suspects."""

    def __init__(self, signature_engine: BehavioralSignatureEngine):
        self._signature_engine = signature_engine
        self._profiles: Dict[str, SuspectProfile] = {}

    def generate_profile(
        self,
        case_ids: List[str],
        case_data: List[Dict[str, Any]],
    ) -> SuspectProfile:
        profile_id = f"profile-{uuid.uuid4().hex[:12]}"

        demographics = self._infer_demographics(case_data)
        psychological = self._infer_psychological_traits(case_data)
        behavioral = self._infer_behavioral_indicators(case_data)
        geographic = self._infer_geographic_profile(case_data)
        temporal = self._infer_temporal_profile(case_data)
        victimology = self._infer_victimology(case_data)

        mo_patterns = []
        sig_patterns = []
        for case_id in case_ids:
            sigs = self._signature_engine.get_case_signatures(case_id)
            for sig in sigs:
                if sig.category == BehaviorCategory.MODUS_OPERANDI:
                    mo_patterns.extend(sig.patterns)
                elif sig.category == BehaviorCategory.SIGNATURE:
                    sig_patterns.extend(sig.patterns)

        risk = self._assess_risk(case_data, len(case_ids))

        confidence_score = self._calculate_confidence(
            len(case_ids),
            len(demographics),
            len(psychological),
            len(behavioral),
        )

        if confidence_score >= 0.8:
            confidence = ProfileConfidence.VERY_HIGH
        elif confidence_score >= 0.6:
            confidence = ProfileConfidence.HIGH
        elif confidence_score >= 0.4:
            confidence = ProfileConfidence.MODERATE
        else:
            confidence = ProfileConfidence.LOW

        profile = SuspectProfile(
            profile_id=profile_id,
            case_ids=case_ids,
            profile_type="unknown_suspect",
            demographics=demographics,
            psychological_traits=psychological,
            behavioral_indicators=behavioral,
            geographic_profile=geographic,
            temporal_profile=temporal,
            victimology_preferences=victimology,
            modus_operandi=list(set(mo_patterns)),
            signature_behaviors=list(set(sig_patterns)),
            risk_assessment=risk,
            confidence=confidence,
            confidence_score=confidence_score,
        )
        self._profiles[profile_id] = profile
        return profile

    def _infer_demographics(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        demographics = {
            "age_range": {"min": 18, "max": 45},
            "gender": "unknown",
            "employment_status": "likely_employed",
            "education_level": "high_school_or_above",
            "relationship_status": "unknown",
            "residence_type": "within_offense_area",
        }

        for case in case_data:
            if case.get("physical_strength_required"):
                demographics["gender"] = "likely_male"
                demographics["age_range"] = {"min": 20, "max": 40}

            if case.get("technical_skill_required"):
                demographics["education_level"] = "some_college_or_above"

            if case.get("time_of_offense") in ["weekday_daytime"]:
                demographics["employment_status"] = "unemployed_or_flexible"

        return demographics

    def _infer_psychological_traits(self, case_data: List[Dict[str, Any]]) -> List[str]:
        traits = []

        organized_count = sum(1 for c in case_data if c.get("scene_organized"))
        if organized_count > len(case_data) / 2:
            traits.extend([
                "organized_personality",
                "above_average_intelligence",
                "planning_capability",
                "impulse_control",
            ])
        else:
            traits.extend([
                "disorganized_personality",
                "impulsive_behavior",
                "possible_substance_use",
            ])

        violence_level = sum(c.get("violence_level", 0) for c in case_data) / len(case_data) if case_data else 0
        if violence_level > 7:
            traits.extend([
                "high_aggression",
                "possible_antisocial_personality",
                "lack_of_empathy",
            ])
        elif violence_level > 4:
            traits.append("moderate_aggression")

        for case in case_data:
            if case.get("trophy_taken"):
                traits.append("trophy_collector")
            if case.get("scene_staging"):
                traits.append("manipulative")
            if case.get("forensic_awareness"):
                traits.append("forensically_aware")

        return list(set(traits))

    def _infer_behavioral_indicators(self, case_data: List[Dict[str, Any]]) -> List[str]:
        indicators = []

        for case in case_data:
            if case.get("surveillance_evidence"):
                indicators.append("conducts_pre_offense_surveillance")
            if case.get("victim_selection_pattern"):
                indicators.append("selective_victim_targeting")
            if case.get("escape_planning"):
                indicators.append("plans_escape_routes")
            if case.get("weapon_brought"):
                indicators.append("brings_weapon_to_scene")
            if case.get("bindings_used"):
                indicators.append("uses_restraints")
            if case.get("vehicle_used"):
                indicators.append("uses_vehicle_in_offenses")

        return list(set(indicators))

    def _infer_geographic_profile(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        locations = [c.get("location") for c in case_data if c.get("location")]

        if not locations:
            return {"analysis": "insufficient_data"}

        lats = [l.get("lat", 0) for l in locations]
        lngs = [l.get("lng", 0) for l in locations]

        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)

        distances = []
        for l in locations:
            d = math.sqrt((l.get("lat", 0) - center_lat)**2 + (l.get("lng", 0) - center_lng)**2)
            distances.append(d)

        avg_distance = sum(distances) / len(distances) if distances else 0

        return {
            "probable_residence_area": {
                "center": {"lat": center_lat, "lng": center_lng},
                "radius_km": avg_distance * 111 * 1.5,
            },
            "offense_distribution": "clustered" if avg_distance < 0.05 else "dispersed",
            "likely_commuter": avg_distance > 0.1,
            "familiar_with_area": True,
        }

    def _infer_temporal_profile(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        times = [c.get("time_of_offense") for c in case_data if c.get("time_of_offense")]
        days = [c.get("day_of_week") for c in case_data if c.get("day_of_week")]

        time_counts: Dict[str, int] = {}
        for t in times:
            time_counts[t] = time_counts.get(t, 0) + 1

        day_counts: Dict[str, int] = {}
        for d in days:
            day_counts[d] = day_counts.get(d, 0) + 1

        preferred_time = max(time_counts.items(), key=lambda x: x[1])[0] if time_counts else "unknown"
        preferred_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else "unknown"

        return {
            "preferred_time": preferred_time,
            "preferred_day": preferred_day,
            "time_distribution": time_counts,
            "day_distribution": day_counts,
            "pattern_consistency": len(set(times)) == 1 if times else False,
        }

    def _infer_victimology(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        victim_data = [c.get("victim_profile", {}) for c in case_data if c.get("victim_profile")]

        if not victim_data:
            return {"analysis": "insufficient_data"}

        ages = [v.get("age") for v in victim_data if v.get("age")]
        genders = [v.get("gender") for v in victim_data if v.get("gender")]

        gender_counts: Dict[str, int] = {}
        for g in genders:
            gender_counts[g] = gender_counts.get(g, 0) + 1

        return {
            "age_preference": {
                "min": min(ages) if ages else None,
                "max": max(ages) if ages else None,
                "average": sum(ages) / len(ages) if ages else None,
            },
            "gender_preference": max(gender_counts.items(), key=lambda x: x[1])[0] if gender_counts else "unknown",
            "victim_count": len(victim_data),
            "victim_relationship": "stranger" if len(case_data) > 2 else "unknown",
        }

    def _assess_risk(self, case_data: List[Dict[str, Any]], case_count: int) -> Dict[str, Any]:
        violence_scores = [c.get("violence_level", 0) for c in case_data]
        avg_violence = sum(violence_scores) / len(violence_scores) if violence_scores else 0

        escalation = False
        if len(violence_scores) >= 3:
            recent = violence_scores[-3:]
            if recent == sorted(recent):
                escalation = True

        if case_count >= 5 and avg_violence >= 7:
            level = "critical"
        elif case_count >= 3 or avg_violence >= 5:
            level = "high"
        elif case_count >= 2:
            level = "medium"
        else:
            level = "low"

        return {
            "risk_level": level,
            "violence_trend": "escalating" if escalation else "stable",
            "reoffense_likelihood": "high" if case_count >= 3 else "moderate",
            "recommended_priority": "immediate" if level == "critical" else "standard",
        }

    def _calculate_confidence(
        self,
        case_count: int,
        demo_count: int,
        psych_count: int,
        behav_count: int,
    ) -> float:
        base = 0.2
        case_bonus = min(0.3, case_count * 0.1)
        data_bonus = min(0.3, (demo_count + psych_count + behav_count) * 0.02)
        return min(0.95, base + case_bonus + data_bonus)

    def get_profile(self, profile_id: str) -> Optional[SuspectProfile]:
        return self._profiles.get(profile_id)

    def get_profiles(
        self,
        confidence: Optional[ProfileConfidence] = None,
        limit: int = 100,
    ) -> List[SuspectProfile]:
        results = list(self._profiles.values())

        if confidence:
            results = [p for p in results if p.confidence == confidence]

        return results[:limit]

    def update_profile(
        self,
        profile_id: str,
        additional_case_ids: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Optional[SuspectProfile]:
        profile = self._profiles.get(profile_id)
        if not profile:
            return None

        if additional_case_ids:
            profile.case_ids.extend(additional_case_ids)
            profile.case_ids = list(set(profile.case_ids))

        if notes:
            profile.notes = notes

        return profile


from datetime import timedelta

__all__ = [
    "BehaviorCategory",
    "OffenseType",
    "RiskLevel",
    "ProfileConfidence",
    "BehavioralSignature",
    "OffenderPrediction",
    "MOCluster",
    "SuspectProfile",
    "BehavioralSignatureEngine",
    "OffenderPredictionModel",
    "ModusOperandiClusterer",
    "UnknownSuspectProfiler",
]
