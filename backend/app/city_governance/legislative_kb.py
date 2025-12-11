"""
Phase 25: Legislative Knowledge Base Engine

Ingests, stores, and versions legal documents including:
- Riviera Beach municipal code
- Florida State Statutes
- Federal frameworks (NIST AI RMF, CJIS, DHS S&T)
- RBPD SOP manuals
- Fire/EMS protocols
- Emergency management ordinances
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4


class LegalSource(Enum):
    """Legal source types."""
    US_CONSTITUTION = "us_constitution"
    FLORIDA_CONSTITUTION = "florida_constitution"
    FLORIDA_STATUTE = "florida_statute"
    RIVIERA_BEACH_CODE = "riviera_beach_code"
    FEDERAL_FRAMEWORK = "federal_framework"
    AGENCY_SOP = "agency_sop"
    EMERGENCY_ORDINANCE = "emergency_ordinance"


class LegalCategory(Enum):
    """Legal category types."""
    CIVIL_RIGHTS = "civil_rights"
    PUBLIC_SAFETY = "public_safety"
    EMERGENCY_POWERS = "emergency_powers"
    CITY_AUTHORITY = "city_authority"
    AUTONOMY_LIMITS = "autonomy_limits"
    PRIVACY = "privacy"
    SURVEILLANCE = "surveillance"
    USE_OF_FORCE = "use_of_force"
    TRAFFIC = "traffic"
    FIRE_EMS = "fire_ems"
    PROPERTY_RIGHTS = "property_rights"
    DATA_PROTECTION = "data_protection"


@dataclass
class LegalSection:
    """Represents a section within a legal document."""
    section_id: str
    number: str
    title: str
    content: str
    subsections: List['LegalSection']
    applicability_tags: List[str]
    keywords: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "subsections": [s.to_dict() for s in self.subsections],
            "applicability_tags": self.applicability_tags,
            "keywords": self.keywords,
        }


@dataclass
class LegalDocument:
    """Represents a legal document in the knowledge base."""
    document_id: str
    source: LegalSource
    title: str
    content: str
    version: str
    effective_date: datetime
    categories: List[LegalCategory]
    sections: List[LegalSection]
    cross_references: List[str]
    applicability_tags: List[str]
    last_updated: datetime
    update_source: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "source": self.source.value,
            "title": self.title,
            "content": self.content,
            "version": self.version,
            "effective_date": self.effective_date.isoformat(),
            "categories": [c.value for c in self.categories],
            "sections": [s.to_dict() for s in self.sections],
            "cross_references": self.cross_references,
            "applicability_tags": self.applicability_tags,
            "last_updated": self.last_updated.isoformat(),
            "update_source": self.update_source,
            "is_active": self.is_active,
        }


class LegislativeKnowledgeBase:
    """
    Legislative Knowledge Base Engine
    
    Ingests, stores, and versions legal documents including:
    - Riviera Beach municipal code
    - Florida State Statutes
    - Federal frameworks (NIST AI RMF, CJIS, DHS S&T)
    - RBPD SOP manuals
    - Fire/EMS protocols
    - Emergency management ordinances
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
        
        self._documents: Dict[str, LegalDocument] = {}
        self._sections_index: Dict[str, LegalSection] = {}
        self._category_index: Dict[LegalCategory, List[str]] = {cat: [] for cat in LegalCategory}
        self._source_index: Dict[LegalSource, List[str]] = {src: [] for src in LegalSource}
        self._keyword_index: Dict[str, List[str]] = {}
        self._cross_reference_graph: Dict[str, List[str]] = {}
        self._update_subscriptions: List[Dict[str, Any]] = []
        
        self._initialize_default_documents()
        self._initialized = True
    
    def _initialize_default_documents(self):
        """Initialize with default legal documents for Riviera Beach."""
        
        # US Constitution - 4th Amendment
        self._add_document(LegalDocument(
            document_id="us-const-4th",
            source=LegalSource.US_CONSTITUTION,
            title="Fourth Amendment - Search and Seizure",
            content="The right of the people to be secure in their persons, houses, papers, and effects, against unreasonable searches and seizures, shall not be violated, and no Warrants shall issue, but upon probable cause, supported by Oath or affirmation, and particularly describing the place to be searched, and the persons or things to be seized.",
            version="1791",
            effective_date=datetime(1791, 12, 15),
            categories=[LegalCategory.CIVIL_RIGHTS, LegalCategory.PRIVACY, LegalCategory.SURVEILLANCE],
            sections=[
                LegalSection(
                    section_id="us-const-4th-main",
                    number="4",
                    title="Search and Seizure",
                    content="Protection against unreasonable searches and seizures",
                    subsections=[],
                    applicability_tags=["surveillance", "drone", "search", "property"],
                    keywords=["search", "seizure", "warrant", "probable cause", "privacy"],
                )
            ],
            cross_references=["florida-const-art1-s12"],
            applicability_tags=["all_actions", "surveillance", "drone", "search"],
            last_updated=datetime.utcnow(),
        ))
        
        # US Constitution - 1st Amendment
        self._add_document(LegalDocument(
            document_id="us-const-1st",
            source=LegalSource.US_CONSTITUTION,
            title="First Amendment - Freedom of Speech, Religion, Press, Assembly",
            content="Congress shall make no law respecting an establishment of religion, or prohibiting the free exercise thereof; or abridging the freedom of speech, or of the press; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances.",
            version="1791",
            effective_date=datetime(1791, 12, 15),
            categories=[LegalCategory.CIVIL_RIGHTS],
            sections=[
                LegalSection(
                    section_id="us-const-1st-main",
                    number="1",
                    title="Freedom of Expression",
                    content="Protection of speech, religion, press, and assembly",
                    subsections=[],
                    applicability_tags=["assembly", "speech", "protest", "crowd"],
                    keywords=["speech", "assembly", "religion", "press", "petition"],
                )
            ],
            cross_references=[],
            applicability_tags=["crowd_management", "surveillance"],
            last_updated=datetime.utcnow(),
        ))
        
        # US Constitution - 14th Amendment
        self._add_document(LegalDocument(
            document_id="us-const-14th",
            source=LegalSource.US_CONSTITUTION,
            title="Fourteenth Amendment - Due Process and Equal Protection",
            content="No State shall make or enforce any law which shall abridge the privileges or immunities of citizens of the United States; nor shall any State deprive any person of life, liberty, or property, without due process of law; nor deny to any person within its jurisdiction the equal protection of the laws.",
            version="1868",
            effective_date=datetime(1868, 7, 9),
            categories=[LegalCategory.CIVIL_RIGHTS],
            sections=[
                LegalSection(
                    section_id="us-const-14th-main",
                    number="14",
                    title="Due Process and Equal Protection",
                    content="Due process and equal protection under the law",
                    subsections=[],
                    applicability_tags=["enforcement", "predictive", "bias"],
                    keywords=["due process", "equal protection", "liberty", "property"],
                )
            ],
            cross_references=[],
            applicability_tags=["all_actions", "predictive_policing", "enforcement"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Constitution - Article I, Section 12
        self._add_document(LegalDocument(
            document_id="florida-const-art1-s12",
            source=LegalSource.FLORIDA_CONSTITUTION,
            title="Florida Constitution - Article I, Section 12 - Searches and Seizures",
            content="The right of the people to be secure in their persons, houses, papers and effects against unreasonable searches and seizures, and against the unreasonable interception of private communications by any means, shall not be violated.",
            version="1968",
            effective_date=datetime(1968, 11, 5),
            categories=[LegalCategory.CIVIL_RIGHTS, LegalCategory.PRIVACY, LegalCategory.SURVEILLANCE],
            sections=[
                LegalSection(
                    section_id="fl-const-art1-s12-main",
                    number="12",
                    title="Searches and Seizures",
                    content="Florida constitutional protection against unreasonable searches",
                    subsections=[],
                    applicability_tags=["surveillance", "drone", "search", "communications"],
                    keywords=["search", "seizure", "privacy", "communications", "interception"],
                )
            ],
            cross_references=["us-const-4th", "fss-934"],
            applicability_tags=["all_actions", "surveillance", "drone", "search"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Constitution - Article I, Section 23 - Right of Privacy
        self._add_document(LegalDocument(
            document_id="florida-const-art1-s23",
            source=LegalSource.FLORIDA_CONSTITUTION,
            title="Florida Constitution - Article I, Section 23 - Right of Privacy",
            content="Every natural person has the right to be let alone and free from governmental intrusion into the person's private life except as otherwise provided herein.",
            version="1980",
            effective_date=datetime(1980, 11, 4),
            categories=[LegalCategory.CIVIL_RIGHTS, LegalCategory.PRIVACY],
            sections=[
                LegalSection(
                    section_id="fl-const-art1-s23-main",
                    number="23",
                    title="Right of Privacy",
                    content="Florida's explicit right to privacy",
                    subsections=[],
                    applicability_tags=["privacy", "surveillance", "data"],
                    keywords=["privacy", "intrusion", "private life"],
                )
            ],
            cross_references=["florida-const-art1-s12"],
            applicability_tags=["surveillance", "data_collection", "tracking"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Statute 934 - Security of Communications
        self._add_document(LegalDocument(
            document_id="fss-934",
            source=LegalSource.FLORIDA_STATUTE,
            title="Florida Statutes Chapter 934 - Security of Communications",
            content="Governs the interception of wire, oral, or electronic communications in Florida.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.PRIVACY, LegalCategory.SURVEILLANCE, LegalCategory.DATA_PROTECTION],
            sections=[
                LegalSection(
                    section_id="fss-934-03",
                    number="934.03",
                    title="Interception and disclosure of communications prohibited",
                    content="Prohibits intentional interception of wire, oral, or electronic communications",
                    subsections=[],
                    applicability_tags=["surveillance", "communications", "wiretap"],
                    keywords=["interception", "wiretap", "communications", "electronic"],
                )
            ],
            cross_references=["florida-const-art1-s12"],
            applicability_tags=["surveillance", "communications"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Statute 252 - Emergency Management
        self._add_document(LegalDocument(
            document_id="fss-252",
            source=LegalSource.FLORIDA_STATUTE,
            title="Florida Statutes Chapter 252 - Emergency Management",
            content="Establishes the framework for emergency management in Florida.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.EMERGENCY_POWERS, LegalCategory.PUBLIC_SAFETY, LegalCategory.CITY_AUTHORITY],
            sections=[
                LegalSection(
                    section_id="fss-252-38",
                    number="252.38",
                    title="Emergency Management Powers of Political Subdivisions",
                    content="Powers granted to cities and counties during emergencies",
                    subsections=[],
                    applicability_tags=["emergency", "evacuation", "curfew"],
                    keywords=["emergency", "evacuation", "curfew", "disaster"],
                )
            ],
            cross_references=["rb-emergency"],
            applicability_tags=["emergency", "disaster", "evacuation"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Statute 316 - Traffic Control
        self._add_document(LegalDocument(
            document_id="fss-316",
            source=LegalSource.FLORIDA_STATUTE,
            title="Florida Statutes Chapter 316 - State Uniform Traffic Control",
            content="Uniform traffic control laws for Florida.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.TRAFFIC, LegalCategory.PUBLIC_SAFETY],
            sections=[
                LegalSection(
                    section_id="fss-316-008",
                    number="316.008",
                    title="Powers of Local Authorities",
                    content="Traffic control powers of local authorities",
                    subsections=[],
                    applicability_tags=["traffic", "signals", "enforcement"],
                    keywords=["traffic", "signals", "speed", "enforcement"],
                )
            ],
            cross_references=[],
            applicability_tags=["traffic", "enforcement"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Statute 776 - Use of Force
        self._add_document(LegalDocument(
            document_id="fss-776",
            source=LegalSource.FLORIDA_STATUTE,
            title="Florida Statutes Chapter 776 - Justifiable Use of Force",
            content="Laws governing the justifiable use of force in Florida.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.USE_OF_FORCE, LegalCategory.PUBLIC_SAFETY],
            sections=[
                LegalSection(
                    section_id="fss-776-05",
                    number="776.05",
                    title="Law Enforcement Officers; Use of Force in Making an Arrest",
                    content="Standards for law enforcement use of force",
                    subsections=[],
                    applicability_tags=["use_of_force", "arrest", "officer"],
                    keywords=["force", "arrest", "deadly force", "officer"],
                )
            ],
            cross_references=["rbpd-sop"],
            applicability_tags=["use_of_force", "robotics", "tactical"],
            last_updated=datetime.utcnow(),
        ))
        
        # Florida Statute 943 - CJIS Compliance
        self._add_document(LegalDocument(
            document_id="fss-943",
            source=LegalSource.FLORIDA_STATUTE,
            title="Florida Statutes Chapter 943 - Department of Law Enforcement",
            content="Establishes FDLE and criminal justice information system requirements.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.PUBLIC_SAFETY, LegalCategory.DATA_PROTECTION],
            sections=[
                LegalSection(
                    section_id="fss-943-0525",
                    number="943.0525",
                    title="Criminal Justice Information",
                    content="Requirements for criminal justice information systems",
                    subsections=[],
                    applicability_tags=["cjis", "data", "criminal_justice"],
                    keywords=["CJIS", "criminal justice", "information", "data"],
                )
            ],
            cross_references=["nist-cjis"],
            applicability_tags=["data_access", "criminal_justice"],
            last_updated=datetime.utcnow(),
        ))
        
        # NIST AI Risk Management Framework
        self._add_document(LegalDocument(
            document_id="nist-ai-rmf",
            source=LegalSource.FEDERAL_FRAMEWORK,
            title="NIST AI Risk Management Framework",
            content="Framework for managing risks associated with AI systems.",
            version="1.0",
            effective_date=datetime(2023, 1, 26),
            categories=[LegalCategory.AUTONOMY_LIMITS, LegalCategory.PUBLIC_SAFETY],
            sections=[
                LegalSection(
                    section_id="nist-ai-rmf-govern",
                    number="GOVERN",
                    title="Governance",
                    content="Cultivate a culture of risk management",
                    subsections=[],
                    applicability_tags=["ai", "autonomy", "governance"],
                    keywords=["AI", "risk", "governance", "accountability"],
                ),
                LegalSection(
                    section_id="nist-ai-rmf-map",
                    number="MAP",
                    title="Map",
                    content="Understand context and identify risks",
                    subsections=[],
                    applicability_tags=["ai", "risk_assessment"],
                    keywords=["context", "risk", "mapping"],
                ),
                LegalSection(
                    section_id="nist-ai-rmf-measure",
                    number="MEASURE",
                    title="Measure",
                    content="Analyze and assess risks",
                    subsections=[],
                    applicability_tags=["ai", "measurement"],
                    keywords=["measure", "assess", "analyze"],
                ),
                LegalSection(
                    section_id="nist-ai-rmf-manage",
                    number="MANAGE",
                    title="Manage",
                    content="Prioritize and act on risks",
                    subsections=[],
                    applicability_tags=["ai", "risk_management"],
                    keywords=["manage", "prioritize", "mitigate"],
                ),
            ],
            cross_references=["nist-cjis"],
            applicability_tags=["ai", "autonomy", "all_actions"],
            last_updated=datetime.utcnow(),
        ))
        
        # CJIS Security Policy
        self._add_document(LegalDocument(
            document_id="nist-cjis",
            source=LegalSource.FEDERAL_FRAMEWORK,
            title="CJIS Security Policy",
            content="FBI Criminal Justice Information Services Security Policy.",
            version="5.9.2",
            effective_date=datetime(2023, 6, 1),
            categories=[LegalCategory.DATA_PROTECTION, LegalCategory.PUBLIC_SAFETY],
            sections=[
                LegalSection(
                    section_id="cjis-5-4",
                    number="5.4",
                    title="Policy Area 4: Auditing and Accountability",
                    content="Requirements for auditing access to criminal justice information",
                    subsections=[],
                    applicability_tags=["audit", "accountability", "cjis"],
                    keywords=["audit", "accountability", "logging", "access"],
                ),
                LegalSection(
                    section_id="cjis-5-5",
                    number="5.5",
                    title="Policy Area 5: Access Control",
                    content="Requirements for controlling access to CJI",
                    subsections=[],
                    applicability_tags=["access_control", "cjis"],
                    keywords=["access", "control", "authorization"],
                ),
            ],
            cross_references=["fss-943"],
            applicability_tags=["data_access", "criminal_justice", "audit"],
            last_updated=datetime.utcnow(),
        ))
        
        # DHS S&T Guidelines
        self._add_document(LegalDocument(
            document_id="dhs-st-guidelines",
            source=LegalSource.FEDERAL_FRAMEWORK,
            title="DHS Science & Technology AI Guidelines",
            content="Department of Homeland Security guidelines for AI in public safety.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.AUTONOMY_LIMITS, LegalCategory.PUBLIC_SAFETY],
            sections=[
                LegalSection(
                    section_id="dhs-st-ai-ethics",
                    number="AI-001",
                    title="AI Ethics in Public Safety",
                    content="Ethical guidelines for AI deployment in public safety",
                    subsections=[],
                    applicability_tags=["ai", "ethics", "public_safety"],
                    keywords=["AI", "ethics", "bias", "fairness"],
                ),
            ],
            cross_references=["nist-ai-rmf"],
            applicability_tags=["ai", "autonomy", "predictive"],
            last_updated=datetime.utcnow(),
        ))
        
        # Riviera Beach Municipal Code - Drones
        self._add_document(LegalDocument(
            document_id="rb-code-drones",
            source=LegalSource.RIVIERA_BEACH_CODE,
            title="Riviera Beach Municipal Code - Unmanned Aircraft Systems",
            content="Regulations governing the use of drones within Riviera Beach city limits.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.PUBLIC_SAFETY, LegalCategory.PRIVACY, LegalCategory.PROPERTY_RIGHTS],
            sections=[
                LegalSection(
                    section_id="rb-drone-001",
                    number="15-201",
                    title="UAS Operations",
                    content="Requirements for UAS operations within city limits",
                    subsections=[],
                    applicability_tags=["drone", "uas", "operations"],
                    keywords=["drone", "UAS", "unmanned", "aircraft"],
                ),
                LegalSection(
                    section_id="rb-drone-002",
                    number="15-202",
                    title="Privacy Protections",
                    content="Privacy requirements for UAS surveillance",
                    subsections=[],
                    applicability_tags=["drone", "privacy", "surveillance"],
                    keywords=["privacy", "surveillance", "recording"],
                ),
                LegalSection(
                    section_id="rb-drone-003",
                    number="15-203",
                    title="Property Entry Restrictions",
                    content="Restrictions on drone entry to private property",
                    subsections=[],
                    applicability_tags=["drone", "property", "entry"],
                    keywords=["property", "entry", "private", "trespass"],
                ),
            ],
            cross_references=["florida-const-art1-s12", "fss-934"],
            applicability_tags=["drone", "surveillance"],
            last_updated=datetime.utcnow(),
        ))
        
        # Riviera Beach Municipal Code - Robotics
        self._add_document(LegalDocument(
            document_id="rb-code-robotics",
            source=LegalSource.RIVIERA_BEACH_CODE,
            title="Riviera Beach Municipal Code - Autonomous Robotics",
            content="Regulations governing the use of autonomous robotics within Riviera Beach.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.PUBLIC_SAFETY, LegalCategory.PROPERTY_RIGHTS, LegalCategory.AUTONOMY_LIMITS],
            sections=[
                LegalSection(
                    section_id="rb-robotics-001",
                    number="15-301",
                    title="Tactical Robotics Operations",
                    content="Requirements for tactical robotics deployment",
                    subsections=[],
                    applicability_tags=["robotics", "tactical", "operations"],
                    keywords=["robotics", "tactical", "autonomous", "deployment"],
                ),
                LegalSection(
                    section_id="rb-robotics-002",
                    number="15-302",
                    title="Property Entry by Robotics",
                    content="Restrictions on robotic entry to private property",
                    subsections=[],
                    applicability_tags=["robotics", "property", "entry"],
                    keywords=["property", "entry", "robotics", "trespass"],
                ),
            ],
            cross_references=["rb-code-drones"],
            applicability_tags=["robotics", "tactical"],
            last_updated=datetime.utcnow(),
        ))
        
        # RBPD Standard Operating Procedures
        self._add_document(LegalDocument(
            document_id="rbpd-sop",
            source=LegalSource.AGENCY_SOP,
            title="Riviera Beach Police Department Standard Operating Procedures",
            content="Standard operating procedures for RBPD officers.",
            version="2024.1",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.PUBLIC_SAFETY, LegalCategory.USE_OF_FORCE],
            sections=[
                LegalSection(
                    section_id="rbpd-sop-uof",
                    number="300",
                    title="Use of Force",
                    content="Guidelines for use of force by officers",
                    subsections=[],
                    applicability_tags=["use_of_force", "officer"],
                    keywords=["force", "deadly", "non-lethal", "restraint"],
                ),
                LegalSection(
                    section_id="rbpd-sop-pursuit",
                    number="301",
                    title="Vehicle Pursuits",
                    content="Guidelines for vehicle pursuits",
                    subsections=[],
                    applicability_tags=["pursuit", "vehicle"],
                    keywords=["pursuit", "chase", "vehicle"],
                ),
                LegalSection(
                    section_id="rbpd-sop-surveillance",
                    number="302",
                    title="Surveillance Operations",
                    content="Guidelines for surveillance operations",
                    subsections=[],
                    applicability_tags=["surveillance", "operations"],
                    keywords=["surveillance", "monitoring", "observation"],
                ),
                LegalSection(
                    section_id="rbpd-sop-drone",
                    number="303",
                    title="Drone Operations",
                    content="Guidelines for police drone operations",
                    subsections=[],
                    applicability_tags=["drone", "uas", "operations"],
                    keywords=["drone", "UAS", "aerial", "surveillance"],
                ),
                LegalSection(
                    section_id="rbpd-sop-predictive",
                    number="304",
                    title="Predictive Policing",
                    content="Guidelines for predictive policing tools",
                    subsections=[],
                    applicability_tags=["predictive", "analytics"],
                    keywords=["predictive", "analytics", "hotspot", "forecast"],
                ),
            ],
            cross_references=["rb-code-drones", "fss-776"],
            applicability_tags=["police", "operations"],
            last_updated=datetime.utcnow(),
        ))
        
        # Fire/EMS Protocols
        self._add_document(LegalDocument(
            document_id="rb-fire-ems",
            source=LegalSource.AGENCY_SOP,
            title="Riviera Beach Fire Rescue Protocols",
            content="Standard protocols for Fire/EMS operations.",
            version="2024.1",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.FIRE_EMS, LegalCategory.PUBLIC_SAFETY, LegalCategory.EMERGENCY_POWERS],
            sections=[
                LegalSection(
                    section_id="rb-fire-response",
                    number="100",
                    title="Emergency Response",
                    content="Emergency response protocols",
                    subsections=[],
                    applicability_tags=["fire", "ems", "emergency"],
                    keywords=["emergency", "response", "fire", "medical"],
                ),
                LegalSection(
                    section_id="rb-fire-mci",
                    number="200",
                    title="Mass Casualty Incidents",
                    content="MCI response protocols",
                    subsections=[],
                    applicability_tags=["mci", "mass_casualty"],
                    keywords=["MCI", "mass casualty", "triage"],
                ),
                LegalSection(
                    section_id="rb-fire-hazmat",
                    number="300",
                    title="Hazardous Materials",
                    content="Hazmat response protocols",
                    subsections=[],
                    applicability_tags=["hazmat", "chemical"],
                    keywords=["hazmat", "chemical", "spill", "contamination"],
                ),
            ],
            cross_references=[],
            applicability_tags=["fire", "ems", "emergency"],
            last_updated=datetime.utcnow(),
        ))
        
        # Emergency Management Ordinances
        self._add_document(LegalDocument(
            document_id="rb-emergency",
            source=LegalSource.EMERGENCY_ORDINANCE,
            title="Riviera Beach Emergency Management Ordinances",
            content="Emergency management and disaster response ordinances.",
            version="2024",
            effective_date=datetime(2024, 1, 1),
            categories=[LegalCategory.EMERGENCY_POWERS, LegalCategory.PUBLIC_SAFETY, LegalCategory.CITY_AUTHORITY],
            sections=[
                LegalSection(
                    section_id="rb-emergency-declaration",
                    number="2-401",
                    title="Emergency Declaration",
                    content="Authority to declare local state of emergency",
                    subsections=[],
                    applicability_tags=["emergency", "declaration"],
                    keywords=["emergency", "declaration", "disaster"],
                ),
                LegalSection(
                    section_id="rb-emergency-evacuation",
                    number="2-402",
                    title="Evacuation Authority",
                    content="Authority to order evacuations",
                    subsections=[],
                    applicability_tags=["evacuation", "emergency"],
                    keywords=["evacuation", "mandatory", "shelter"],
                ),
                LegalSection(
                    section_id="rb-emergency-curfew",
                    number="2-403",
                    title="Curfew Authority",
                    content="Authority to impose curfews during emergencies",
                    subsections=[],
                    applicability_tags=["curfew", "emergency"],
                    keywords=["curfew", "restriction", "movement"],
                ),
                LegalSection(
                    section_id="rb-emergency-resources",
                    number="2-404",
                    title="Emergency Resource Allocation",
                    content="Authority to allocate resources during emergencies",
                    subsections=[],
                    applicability_tags=["resources", "emergency"],
                    keywords=["resources", "allocation", "emergency"],
                ),
            ],
            cross_references=["fss-252"],
            applicability_tags=["emergency", "disaster"],
            last_updated=datetime.utcnow(),
        ))
    
    def _add_document(self, document: LegalDocument):
        """Add a document to the knowledge base."""
        self._documents[document.document_id] = document
        
        # Index by source
        self._source_index[document.source].append(document.document_id)
        
        # Index by category
        for category in document.categories:
            self._category_index[category].append(document.document_id)
        
        # Index sections
        for section in document.sections:
            self._sections_index[section.section_id] = section
            
            # Index by keywords
            for keyword in section.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self._keyword_index:
                    self._keyword_index[keyword_lower] = []
                self._keyword_index[keyword_lower].append(section.section_id)
        
        # Build cross-reference graph
        self._cross_reference_graph[document.document_id] = document.cross_references
    
    def ingest_document(
        self,
        source: LegalSource,
        title: str,
        content: str,
        version: str,
        effective_date: datetime,
        categories: List[LegalCategory],
        sections: List[Dict[str, Any]],
        applicability_tags: List[str],
        cross_references: Optional[List[str]] = None,
    ) -> LegalDocument:
        """Ingest a new legal document into the knowledge base."""
        document_id = f"{source.value}-{uuid4().hex[:8]}"
        
        parsed_sections = []
        for section_data in sections:
            section = LegalSection(
                section_id=f"{document_id}-{section_data.get('number', 'main')}",
                number=section_data.get("number", ""),
                title=section_data.get("title", ""),
                content=section_data.get("content", ""),
                subsections=[],
                applicability_tags=section_data.get("applicability_tags", []),
                keywords=section_data.get("keywords", []),
            )
            parsed_sections.append(section)
        
        document = LegalDocument(
            document_id=document_id,
            source=source,
            title=title,
            content=content,
            version=version,
            effective_date=effective_date,
            categories=categories,
            sections=parsed_sections,
            cross_references=cross_references or [],
            applicability_tags=applicability_tags,
            last_updated=datetime.utcnow(),
        )
        
        self._add_document(document)
        self._notify_update(document)
        
        return document
    
    def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        version: Optional[str] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[LegalDocument]:
        """Update an existing document."""
        document = self._documents.get(document_id)
        if not document:
            return None
        
        if content:
            document.content = content
        if version:
            document.version = version
        if sections:
            parsed_sections = []
            for section_data in sections:
                section = LegalSection(
                    section_id=f"{document_id}-{section_data.get('number', 'main')}",
                    number=section_data.get("number", ""),
                    title=section_data.get("title", ""),
                    content=section_data.get("content", ""),
                    subsections=[],
                    applicability_tags=section_data.get("applicability_tags", []),
                    keywords=section_data.get("keywords", []),
                )
                parsed_sections.append(section)
            document.sections = parsed_sections
        
        document.last_updated = datetime.utcnow()
        self._notify_update(document)
        
        return document
    
    def get_document(self, document_id: str) -> Optional[LegalDocument]:
        """Get a document by ID."""
        return self._documents.get(document_id)
    
    def get_documents(
        self,
        source: Optional[LegalSource] = None,
        category: Optional[LegalCategory] = None,
        active_only: bool = True,
    ) -> List[LegalDocument]:
        """Get documents with optional filtering."""
        documents = list(self._documents.values())
        
        if source:
            doc_ids = set(self._source_index.get(source, []))
            documents = [d for d in documents if d.document_id in doc_ids]
        
        if category:
            doc_ids = set(self._category_index.get(category, []))
            documents = [d for d in documents if d.document_id in doc_ids]
        
        if active_only:
            documents = [d for d in documents if d.is_active]
        
        return documents
    
    def search_by_keyword(self, keyword: str) -> List[LegalSection]:
        """Search sections by keyword."""
        keyword_lower = keyword.lower()
        section_ids = self._keyword_index.get(keyword_lower, [])
        return [self._sections_index[sid] for sid in section_ids if sid in self._sections_index]
    
    def search_by_applicability(self, tag: str) -> List[LegalDocument]:
        """Search documents by applicability tag."""
        return [d for d in self._documents.values() if tag in d.applicability_tags]
    
    def get_cross_references(self, document_id: str) -> List[LegalDocument]:
        """Get cross-referenced documents."""
        ref_ids = self._cross_reference_graph.get(document_id, [])
        return [self._documents[rid] for rid in ref_ids if rid in self._documents]
    
    def get_applicable_documents(self, action_type: str, context: Dict[str, Any]) -> List[LegalDocument]:
        """Get all documents applicable to an action type and context."""
        applicable = []
        
        # Search by action type tag
        applicable.extend(self.search_by_applicability(action_type))
        
        # Search by context tags
        for key, value in context.items():
            if isinstance(value, str):
                applicable.extend(self.search_by_applicability(value))
        
        # Always include constitutional documents
        applicable.extend(self.get_documents(source=LegalSource.US_CONSTITUTION))
        applicable.extend(self.get_documents(source=LegalSource.FLORIDA_CONSTITUTION))
        
        # Deduplicate
        seen = set()
        unique = []
        for doc in applicable:
            if doc.document_id not in seen:
                seen.add(doc.document_id)
                unique.append(doc)
        
        return unique
    
    def subscribe_to_updates(self, callback: Dict[str, Any]):
        """Subscribe to document updates (stub for real-time updates)."""
        self._update_subscriptions.append(callback)
    
    def _notify_update(self, document: LegalDocument):
        """Notify subscribers of document update."""
        for subscription in self._update_subscriptions:
            # In production, this would trigger actual notifications
            pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "total_documents": len(self._documents),
            "documents_by_source": {
                src.value: len(ids) for src, ids in self._source_index.items()
            },
            "documents_by_category": {
                cat.value: len(ids) for cat, ids in self._category_index.items()
            },
            "total_sections": len(self._sections_index),
            "total_keywords": len(self._keyword_index),
            "cross_references": sum(len(refs) for refs in self._cross_reference_graph.values()),
        }


# Singleton accessor
_legislative_kb_instance: Optional[LegislativeKnowledgeBase] = None


def get_legislative_knowledge_base() -> LegislativeKnowledgeBase:
    """Get the singleton LegislativeKnowledgeBase instance."""
    global _legislative_kb_instance
    if _legislative_kb_instance is None:
        _legislative_kb_instance = LegislativeKnowledgeBase()
    return _legislative_kb_instance
