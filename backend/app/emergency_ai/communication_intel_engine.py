"""
Phase 31: Emergency Communication Intelligence Engine

Performs:
- Automated Emergency Messaging
- Automatic Social Signal Extraction
- Cross-Language Translation

City: Riviera Beach, Florida 33404
Agency ORI: FL0500400
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
import uuid


class AlertType(Enum):
    """Types of emergency alerts"""
    EVACUATION_ORDER = "evacuation_order"
    EVACUATION_ADVISORY = "evacuation_advisory"
    SHELTER_IN_PLACE = "shelter_in_place"
    SHELTER_UPDATE = "shelter_update"
    ROAD_CLOSURE = "road_closure"
    WATER_ADVISORY = "water_advisory"
    BOIL_WATER = "boil_water"
    POWER_OUTAGE = "power_outage"
    HAZMAT_WARNING = "hazmat_warning"
    WEATHER_WARNING = "weather_warning"
    ALL_CLEAR = "all_clear"
    CURFEW = "curfew"
    MISSING_PERSON = "missing_person"
    AMBER_ALERT = "amber_alert"


class AlertPriority(Enum):
    """Alert priority levels"""
    INFORMATIONAL = 1
    ADVISORY = 2
    WATCH = 3
    WARNING = 4
    EMERGENCY = 5


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    HAITIAN_CREOLE = "ht"
    PORTUGUESE = "pt"
    FRENCH = "fr"


class DistributionChannel(Enum):
    """Alert distribution channels"""
    REVERSE_911 = "reverse_911"
    TEXT_ALERT = "text_alert"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    SIRENS = "sirens"
    RADIO = "radio"
    TV = "tv"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"


class SignalType(Enum):
    """Types of social signals"""
    CRISIS_REPORT = "crisis_report"
    RESOURCE_REQUEST = "resource_request"
    DAMAGE_REPORT = "damage_report"
    MISSING_PERSON = "missing_person"
    RUMOR = "rumor"
    MISINFORMATION = "misinformation"
    POSITIVE_UPDATE = "positive_update"
    VOLUNTEER_OFFER = "volunteer_offer"


@dataclass
class EmergencyAlert:
    """Emergency alert message"""
    alert_id: str
    timestamp: datetime
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    affected_zones: List[str]
    effective_time: datetime
    expiration_time: Optional[datetime]
    distribution_channels: List[DistributionChannel]
    languages: List[Language]
    translations: Dict[str, str] = field(default_factory=dict)
    sender: str = "Riviera Beach Emergency Management"
    callback_number: str = ""
    web_link: str = ""
    recipients_count: int = 0
    delivery_status: str = "pending"
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.alert_id}:{self.timestamp.isoformat()}:{self.alert_type.value}:{self.priority.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class MultilingualMessage:
    """Multi-language message"""
    message_id: str
    timestamp: datetime
    original_language: Language
    original_text: str
    translations: Dict[str, str]
    context: str
    verified: bool = False
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.message_id}:{self.timestamp.isoformat()}:{self.original_text[:50]}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class SocialSignal:
    """Social media signal detection"""
    signal_id: str
    timestamp: datetime
    signal_type: SignalType
    source_platform: str
    content_summary: str
    location_mentioned: Optional[str]
    zone_inferred: Optional[str]
    urgency_score: float
    credibility_score: float
    sentiment: str
    keywords: List[str] = field(default_factory=list)
    requires_response: bool = False
    response_recommendation: str = ""
    is_public_post: bool = True
    
    def __post_init__(self):
        self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.signal_id}:{self.timestamp.isoformat()}:{self.signal_type.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RumorDebunk:
    """Rumor debunking record"""
    debunk_id: str
    timestamp: datetime
    rumor_summary: str
    fact_check_result: str
    official_statement: str
    sources: List[str]
    distribution_channels: List[DistributionChannel]
    languages: List[Language]
    translations: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertDistributionLog:
    """Alert distribution log entry"""
    log_id: str
    alert_id: str
    timestamp: datetime
    channel: DistributionChannel
    recipients_targeted: int
    recipients_reached: int
    delivery_rate: float
    failures: int
    failure_reasons: List[str] = field(default_factory=list)


class CommunicationIntelEngine:
    """
    Emergency Communication Intelligence Engine
    
    Provides automated emergency messaging, social signal
    extraction, and multi-language translation.
    """
    
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
        
        self.agency_config = {
            "ori": "FL0500400",
            "city": "Riviera Beach",
            "state": "FL",
            "zip": "33404",
            "county": "Palm Beach",
        }
        
        self.city_zones = [
            "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
            "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
        ]
        
        self.zone_populations = {
            "Zone_A": 3500, "Zone_B": 4200, "Zone_C": 3800,
            "Zone_D": 2900, "Zone_E": 4500, "Zone_F": 3200,
            "Zone_G": 2800, "Zone_H": 3600, "Zone_I": 4100,
            "Zone_J": 3400,
        }
        
        self.alert_templates = {
            AlertType.EVACUATION_ORDER: {
                Language.ENGLISH: "MANDATORY EVACUATION ORDER for {zones}. Leave immediately. Proceed to {shelter}. For assistance call {phone}.",
                Language.SPANISH: "ORDEN DE EVACUACIÓN OBLIGATORIA para {zones}. Salga inmediatamente. Diríjase a {shelter}. Para asistencia llame al {phone}.",
                Language.HAITIAN_CREOLE: "LÒD EVAKUASYON OBLIGATWA pou {zones}. Kite imedyatman. Ale nan {shelter}. Pou asistans rele {phone}.",
            },
            AlertType.EVACUATION_ADVISORY: {
                Language.ENGLISH: "EVACUATION ADVISORY for {zones}. Residents are advised to evacuate. Shelter available at {shelter}.",
                Language.SPANISH: "AVISO DE EVACUACIÓN para {zones}. Se recomienda a los residentes evacuar. Refugio disponible en {shelter}.",
                Language.HAITIAN_CREOLE: "KONSÈY EVAKUASYON pou {zones}. Yo konseye rezidan yo evakye. Abri disponib nan {shelter}.",
            },
            AlertType.SHELTER_IN_PLACE: {
                Language.ENGLISH: "SHELTER IN PLACE for {zones}. Stay indoors. Close windows and doors. Await further instructions.",
                Language.SPANISH: "REFUGIARSE EN EL LUGAR para {zones}. Permanezca adentro. Cierre ventanas y puertas. Espere más instrucciones.",
                Language.HAITIAN_CREOLE: "RETE ANNDAN pou {zones}. Rete anndan kay. Fèmen fenèt ak pòt. Tann plis enstriksyon.",
            },
            AlertType.WATER_ADVISORY: {
                Language.ENGLISH: "WATER ADVISORY for {zones}. Do not drink tap water until further notice. Use bottled water only.",
                Language.SPANISH: "AVISO DE AGUA para {zones}. No beba agua del grifo hasta nuevo aviso. Use solo agua embotellada.",
                Language.HAITIAN_CREOLE: "KONSÈY DLO pou {zones}. Pa bwè dlo tiyo jiskaske yo di ou. Sèvi ak dlo nan boutèy sèlman.",
            },
            AlertType.BOIL_WATER: {
                Language.ENGLISH: "BOIL WATER NOTICE for {zones}. Boil tap water for at least 1 minute before drinking or cooking.",
                Language.SPANISH: "AVISO DE HERVIR AGUA para {zones}. Hierva el agua del grifo durante al menos 1 minuto antes de beber o cocinar.",
                Language.HAITIAN_CREOLE: "AVI BOUYI DLO pou {zones}. Bouyi dlo tiyo pou omwen 1 minit anvan ou bwè oswa kwit manje.",
            },
            AlertType.ROAD_CLOSURE: {
                Language.ENGLISH: "ROAD CLOSURE: {road_name} is closed due to {reason}. Use alternate routes.",
                Language.SPANISH: "CIERRE DE CARRETERA: {road_name} está cerrada debido a {reason}. Use rutas alternativas.",
                Language.HAITIAN_CREOLE: "WOUT FÈMEN: {road_name} fèmen akòz {reason}. Sèvi ak lòt wout.",
            },
            AlertType.ALL_CLEAR: {
                Language.ENGLISH: "ALL CLEAR for {zones}. The emergency has ended. It is safe to return to normal activities.",
                Language.SPANISH: "TODO DESPEJADO para {zones}. La emergencia ha terminado. Es seguro volver a las actividades normales.",
                Language.HAITIAN_CREOLE: "TOUT KLÈ pou {zones}. Ijans lan fini. Li an sekirite pou retounen nan aktivite nòmal yo.",
            },
        }
        
        self.crisis_keywords = {
            Language.ENGLISH: [
                "help", "emergency", "flood", "fire", "trapped", "injured",
                "missing", "evacuation", "shelter", "water", "power out",
                "road closed", "damage", "destroyed", "rescue", "stranded",
            ],
            Language.SPANISH: [
                "ayuda", "emergencia", "inundación", "fuego", "atrapado", "herido",
                "desaparecido", "evacuación", "refugio", "agua", "sin luz",
                "carretera cerrada", "daño", "destruido", "rescate", "varado",
            ],
            Language.HAITIAN_CREOLE: [
                "ede", "ijans", "inondasyon", "dife", "bloke", "blese",
                "pèdi", "evakuasyon", "abri", "dlo", "pa gen kouran",
                "wout fèmen", "domaj", "detwi", "sovtaj", "kole",
            ],
        }
        
        self.distribution_log: List[AlertDistributionLog] = []
        
        self.statistics = {
            "total_alerts_sent": 0,
            "total_recipients_reached": 0,
            "total_signals_detected": 0,
            "total_rumors_debunked": 0,
            "total_translations": 0,
        }
    
    def create_emergency_alert(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        affected_zones: List[str],
        custom_message: Optional[str] = None,
        template_params: Optional[Dict[str, str]] = None,
        channels: Optional[List[DistributionChannel]] = None,
        languages: Optional[List[Language]] = None,
        expiration_hours: float = 24.0,
    ) -> EmergencyAlert:
        """
        Create an emergency alert with multi-language support.
        """
        alert_id = f"EA-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()
        
        if languages is None:
            languages = [Language.ENGLISH, Language.SPANISH, Language.HAITIAN_CREOLE]
        
        if channels is None:
            if priority == AlertPriority.EMERGENCY:
                channels = [
                    DistributionChannel.REVERSE_911,
                    DistributionChannel.TEXT_ALERT,
                    DistributionChannel.SIRENS,
                    DistributionChannel.SOCIAL_MEDIA,
                    DistributionChannel.RADIO,
                    DistributionChannel.TV,
                ]
            elif priority == AlertPriority.WARNING:
                channels = [
                    DistributionChannel.REVERSE_911,
                    DistributionChannel.TEXT_ALERT,
                    DistributionChannel.SOCIAL_MEDIA,
                ]
            else:
                channels = [
                    DistributionChannel.TEXT_ALERT,
                    DistributionChannel.SOCIAL_MEDIA,
                    DistributionChannel.WEBSITE,
                ]
        
        params = template_params or {}
        params["zones"] = ", ".join(affected_zones)
        params.setdefault("shelter", "Riviera Beach Community Center")
        params.setdefault("phone", "561-845-4000")
        
        if custom_message:
            english_message = custom_message
        else:
            template = self.alert_templates.get(alert_type, {})
            english_message = template.get(Language.ENGLISH, f"Emergency alert for {', '.join(affected_zones)}")
            english_message = english_message.format(**params)
        
        translations = {Language.ENGLISH.value: english_message}
        for lang in languages:
            if lang != Language.ENGLISH:
                translated = self._translate_message(english_message, Language.ENGLISH, lang)
                translations[lang.value] = translated
        
        title = self._generate_alert_title(alert_type, priority)
        
        recipients_count = sum(
            self.zone_populations.get(z, 0) for z in affected_zones
        )
        
        expiration = timestamp + timedelta(hours=expiration_hours) if expiration_hours > 0 else None
        
        alert = EmergencyAlert(
            alert_id=alert_id,
            timestamp=timestamp,
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=english_message,
            affected_zones=affected_zones,
            effective_time=timestamp,
            expiration_time=expiration,
            distribution_channels=channels,
            languages=languages,
            translations=translations,
            callback_number="561-845-4000",
            web_link="https://rivierabeach.gov/emergency",
            recipients_count=recipients_count,
            delivery_status="ready",
        )
        
        self.statistics["total_alerts_sent"] += 1
        self.statistics["total_translations"] += len(languages) - 1
        
        return alert
    
    def distribute_alert(
        self,
        alert: EmergencyAlert,
    ) -> List[AlertDistributionLog]:
        """
        Distribute alert through all specified channels.
        """
        logs = []
        
        for channel in alert.distribution_channels:
            log_id = f"DL-{uuid.uuid4().hex[:8].upper()}"
            
            targeted = alert.recipients_count
            
            delivery_rates = {
                DistributionChannel.REVERSE_911: 0.85,
                DistributionChannel.TEXT_ALERT: 0.92,
                DistributionChannel.EMAIL: 0.75,
                DistributionChannel.SOCIAL_MEDIA: 0.60,
                DistributionChannel.SIRENS: 0.95,
                DistributionChannel.RADIO: 0.70,
                DistributionChannel.TV: 0.65,
                DistributionChannel.WEBSITE: 0.40,
                DistributionChannel.MOBILE_APP: 0.55,
            }
            
            rate = delivery_rates.get(channel, 0.5)
            reached = int(targeted * rate)
            failures = targeted - reached
            
            failure_reasons = []
            if failures > 0:
                if channel == DistributionChannel.REVERSE_911:
                    failure_reasons.append("Phone not answered")
                    failure_reasons.append("Invalid phone number")
                elif channel == DistributionChannel.TEXT_ALERT:
                    failure_reasons.append("Phone powered off")
                    failure_reasons.append("No cell service")
                elif channel == DistributionChannel.EMAIL:
                    failure_reasons.append("Invalid email")
                    failure_reasons.append("Spam filter")
            
            log = AlertDistributionLog(
                log_id=log_id,
                alert_id=alert.alert_id,
                timestamp=datetime.utcnow(),
                channel=channel,
                recipients_targeted=targeted,
                recipients_reached=reached,
                delivery_rate=rate,
                failures=failures,
                failure_reasons=failure_reasons[:2],
            )
            
            logs.append(log)
            self.distribution_log.append(log)
            self.statistics["total_recipients_reached"] += reached
        
        alert.delivery_status = "distributed"
        
        return logs
    
    def detect_social_signals(
        self,
        public_posts: List[Dict[str, Any]],
    ) -> List[SocialSignal]:
        """
        Detect crisis-related signals from public social media posts.
        Only processes public posts - no private data.
        """
        signals = []
        
        for post in public_posts:
            if not post.get("is_public", True):
                continue
            
            content = post.get("content", "").lower()
            platform = post.get("platform", "unknown")
            location = post.get("location_mentioned")
            
            signal_type = self._classify_signal(content)
            if signal_type is None:
                continue
            
            urgency = self._calculate_urgency(content, signal_type)
            credibility = self._calculate_credibility(post)
            sentiment = self._analyze_sentiment(content)
            keywords = self._extract_keywords(content)
            
            zone = self._infer_zone(location, content)
            
            requires_response = urgency > 0.7 and signal_type in [
                SignalType.CRISIS_REPORT,
                SignalType.RESOURCE_REQUEST,
                SignalType.MISSING_PERSON,
            ]
            
            response_rec = ""
            if requires_response:
                response_rec = self._generate_response_recommendation(signal_type, content)
            
            signal = SocialSignal(
                signal_id=f"SS-{uuid.uuid4().hex[:8].upper()}",
                timestamp=datetime.utcnow(),
                signal_type=signal_type,
                source_platform=platform,
                content_summary=content[:200],
                location_mentioned=location,
                zone_inferred=zone,
                urgency_score=urgency,
                credibility_score=credibility,
                sentiment=sentiment,
                keywords=keywords,
                requires_response=requires_response,
                response_recommendation=response_rec,
                is_public_post=True,
            )
            
            signals.append(signal)
            self.statistics["total_signals_detected"] += 1
        
        return signals
    
    def debunk_rumor(
        self,
        rumor_summary: str,
        fact_check_result: str,
        official_statement: str,
        sources: List[str],
    ) -> RumorDebunk:
        """
        Create rumor debunking message.
        """
        debunk_id = f"RD-{uuid.uuid4().hex[:8].upper()}"
        
        languages = [Language.ENGLISH, Language.SPANISH, Language.HAITIAN_CREOLE]
        channels = [
            DistributionChannel.SOCIAL_MEDIA,
            DistributionChannel.WEBSITE,
            DistributionChannel.TEXT_ALERT,
        ]
        
        translations = {Language.ENGLISH.value: official_statement}
        for lang in languages:
            if lang != Language.ENGLISH:
                translated = self._translate_message(official_statement, Language.ENGLISH, lang)
                translations[lang.value] = translated
        
        debunk = RumorDebunk(
            debunk_id=debunk_id,
            timestamp=datetime.utcnow(),
            rumor_summary=rumor_summary,
            fact_check_result=fact_check_result,
            official_statement=official_statement,
            sources=sources,
            distribution_channels=channels,
            languages=languages,
            translations=translations,
        )
        
        self.statistics["total_rumors_debunked"] += 1
        
        return debunk
    
    def translate_message(
        self,
        text: str,
        source_language: Language,
        target_languages: List[Language],
        context: str = "emergency",
    ) -> MultilingualMessage:
        """
        Translate message to multiple languages.
        """
        message_id = f"TM-{uuid.uuid4().hex[:8].upper()}"
        
        translations = {source_language.value: text}
        
        for target in target_languages:
            if target != source_language:
                translated = self._translate_message(text, source_language, target)
                translations[target.value] = translated
        
        self.statistics["total_translations"] += len(target_languages)
        
        return MultilingualMessage(
            message_id=message_id,
            timestamp=datetime.utcnow(),
            original_language=source_language,
            original_text=text,
            translations=translations,
            context=context,
            verified=False,
        )
    
    def get_alert_templates(self, alert_type: AlertType) -> Dict[str, str]:
        """
        Get alert templates for a specific alert type.
        """
        return self.alert_templates.get(alert_type, {})
    
    def get_distribution_summary(self) -> Dict[str, Any]:
        """
        Get summary of alert distribution.
        """
        total_targeted = sum(log.recipients_targeted for log in self.distribution_log)
        total_reached = sum(log.recipients_reached for log in self.distribution_log)
        
        by_channel = {}
        for log in self.distribution_log:
            channel = log.channel.value
            if channel not in by_channel:
                by_channel[channel] = {"targeted": 0, "reached": 0, "rate": 0}
            by_channel[channel]["targeted"] += log.recipients_targeted
            by_channel[channel]["reached"] += log.recipients_reached
        
        for channel in by_channel:
            if by_channel[channel]["targeted"] > 0:
                by_channel[channel]["rate"] = (
                    by_channel[channel]["reached"] / by_channel[channel]["targeted"]
                )
        
        return {
            "total_alerts": len(set(log.alert_id for log in self.distribution_log)),
            "total_targeted": total_targeted,
            "total_reached": total_reached,
            "overall_delivery_rate": total_reached / total_targeted if total_targeted > 0 else 0,
            "by_channel": by_channel,
        }
    
    def _translate_message(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str:
        """
        Translate message between languages.
        In production, this would use a translation API.
        """
        if target == Language.SPANISH:
            common_translations = {
                "emergency": "emergencia",
                "evacuation": "evacuación",
                "shelter": "refugio",
                "flood": "inundación",
                "warning": "advertencia",
                "immediately": "inmediatamente",
                "safe": "seguro",
                "danger": "peligro",
                "help": "ayuda",
                "water": "agua",
                "power": "electricidad",
                "road": "carretera",
                "closed": "cerrado",
            }
            result = text
            for eng, spa in common_translations.items():
                result = result.replace(eng, spa)
            return f"[ES] {result}"
        
        elif target == Language.HAITIAN_CREOLE:
            common_translations = {
                "emergency": "ijans",
                "evacuation": "evakuasyon",
                "shelter": "abri",
                "flood": "inondasyon",
                "warning": "avètisman",
                "immediately": "imedyatman",
                "safe": "an sekirite",
                "danger": "danje",
                "help": "ede",
                "water": "dlo",
                "power": "kouran",
                "road": "wout",
                "closed": "fèmen",
            }
            result = text
            for eng, ht in common_translations.items():
                result = result.replace(eng, ht)
            return f"[HT] {result}"
        
        return text
    
    def _generate_alert_title(self, alert_type: AlertType, priority: AlertPriority) -> str:
        """Generate alert title."""
        priority_prefix = {
            AlertPriority.EMERGENCY: "EMERGENCY",
            AlertPriority.WARNING: "WARNING",
            AlertPriority.WATCH: "WATCH",
            AlertPriority.ADVISORY: "ADVISORY",
            AlertPriority.INFORMATIONAL: "INFO",
        }
        
        type_names = {
            AlertType.EVACUATION_ORDER: "Evacuation Order",
            AlertType.EVACUATION_ADVISORY: "Evacuation Advisory",
            AlertType.SHELTER_IN_PLACE: "Shelter in Place",
            AlertType.SHELTER_UPDATE: "Shelter Update",
            AlertType.ROAD_CLOSURE: "Road Closure",
            AlertType.WATER_ADVISORY: "Water Advisory",
            AlertType.BOIL_WATER: "Boil Water Notice",
            AlertType.POWER_OUTAGE: "Power Outage",
            AlertType.HAZMAT_WARNING: "Hazmat Warning",
            AlertType.WEATHER_WARNING: "Weather Warning",
            AlertType.ALL_CLEAR: "All Clear",
            AlertType.CURFEW: "Curfew Notice",
        }
        
        prefix = priority_prefix.get(priority, "ALERT")
        name = type_names.get(alert_type, "Emergency Alert")
        
        return f"{prefix}: {name}"
    
    def _classify_signal(self, content: str) -> Optional[SignalType]:
        """Classify social signal type."""
        content_lower = content.lower()
        
        crisis_words = ["help", "emergency", "trapped", "injured", "rescue", "ede", "ayuda"]
        if any(word in content_lower for word in crisis_words):
            return SignalType.CRISIS_REPORT
        
        resource_words = ["need", "looking for", "where can i get", "necesito", "bezwen"]
        if any(word in content_lower for word in resource_words):
            return SignalType.RESOURCE_REQUEST
        
        damage_words = ["destroyed", "damaged", "flooded", "collapsed", "destruido", "detwi"]
        if any(word in content_lower for word in damage_words):
            return SignalType.DAMAGE_REPORT
        
        missing_words = ["missing", "lost", "can't find", "desaparecido", "pèdi"]
        if any(word in content_lower for word in missing_words):
            return SignalType.MISSING_PERSON
        
        rumor_words = ["heard that", "is it true", "rumor", "they say"]
        if any(word in content_lower for word in rumor_words):
            return SignalType.RUMOR
        
        positive_words = ["safe", "okay", "rescued", "thank you", "grateful"]
        if any(word in content_lower for word in positive_words):
            return SignalType.POSITIVE_UPDATE
        
        volunteer_words = ["volunteer", "help out", "donate", "assist"]
        if any(word in content_lower for word in volunteer_words):
            return SignalType.VOLUNTEER_OFFER
        
        return None
    
    def _calculate_urgency(self, content: str, signal_type: SignalType) -> float:
        """Calculate urgency score."""
        base_urgency = {
            SignalType.CRISIS_REPORT: 0.8,
            SignalType.RESOURCE_REQUEST: 0.6,
            SignalType.DAMAGE_REPORT: 0.5,
            SignalType.MISSING_PERSON: 0.9,
            SignalType.RUMOR: 0.3,
            SignalType.MISINFORMATION: 0.4,
            SignalType.POSITIVE_UPDATE: 0.1,
            SignalType.VOLUNTEER_OFFER: 0.2,
        }
        
        urgency = base_urgency.get(signal_type, 0.5)
        
        urgent_words = ["now", "immediately", "urgent", "dying", "critical", "hurry"]
        if any(word in content.lower() for word in urgent_words):
            urgency = min(urgency + 0.2, 1.0)
        
        return urgency
    
    def _calculate_credibility(self, post: Dict[str, Any]) -> float:
        """Calculate credibility score."""
        credibility = 0.5
        
        if post.get("verified_account"):
            credibility += 0.3
        
        if post.get("follower_count", 0) > 1000:
            credibility += 0.1
        
        if post.get("has_media"):
            credibility += 0.1
        
        if post.get("location_tagged"):
            credibility += 0.1
        
        return min(credibility, 1.0)
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content."""
        negative_words = ["help", "emergency", "danger", "scared", "worried", "bad", "terrible"]
        positive_words = ["safe", "okay", "good", "thank", "grateful", "rescued"]
        
        content_lower = content.lower()
        
        neg_count = sum(1 for word in negative_words if word in content_lower)
        pos_count = sum(1 for word in positive_words if word in content_lower)
        
        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        return "neutral"
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        all_keywords = []
        for lang_keywords in self.crisis_keywords.values():
            all_keywords.extend(lang_keywords)
        
        content_lower = content.lower()
        found = [kw for kw in all_keywords if kw in content_lower]
        
        return list(set(found))[:5]
    
    def _infer_zone(self, location: Optional[str], content: str) -> Optional[str]:
        """Infer zone from location or content."""
        if location:
            for zone in self.city_zones:
                if zone.lower() in location.lower():
                    return zone
        
        zone_indicators = {
            "Zone_A": ["blue heron", "community center"],
            "Zone_B": ["broadway", "downtown"],
            "Zone_C": ["avenue l", "high school"],
            "Zone_E": ["marina", "13th street"],
            "Zone_J": ["singer island", "ocean"],
        }
        
        content_lower = content.lower()
        for zone, indicators in zone_indicators.items():
            if any(ind in content_lower for ind in indicators):
                return zone
        
        return None
    
    def _generate_response_recommendation(self, signal_type: SignalType, content: str) -> str:
        """Generate response recommendation."""
        recommendations = {
            SignalType.CRISIS_REPORT: "Dispatch emergency services to verify and respond",
            SignalType.RESOURCE_REQUEST: "Direct to nearest distribution point or shelter",
            SignalType.MISSING_PERSON: "Forward to search and rescue coordination",
            SignalType.DAMAGE_REPORT: "Add to damage assessment queue",
            SignalType.RUMOR: "Prepare official clarification statement",
        }
        return recommendations.get(signal_type, "Review and assess")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.statistics,
            "agency": self.agency_config,
            "supported_languages": [lang.value for lang in Language],
            "distribution_channels": [ch.value for ch in DistributionChannel],
        }
