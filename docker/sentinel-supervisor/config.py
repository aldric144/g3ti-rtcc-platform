"""
AI Sentinel Supervisor Configuration

Configuration management for the AI Sentinel Supervisor service.
"""

import os
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class SentinelConfig:
    """Configuration for AI Sentinel Supervisor."""
    
    sentinel_mode: str = field(default_factory=lambda: os.getenv("SENTINEL_MODE", "production"))
    auto_correction_enabled: bool = field(default_factory=lambda: os.getenv("AUTO_CORRECTION_ENABLED", "true").lower() == "true")
    ethics_guard_enabled: bool = field(default_factory=lambda: os.getenv("ETHICS_GUARD_ENABLED", "true").lower() == "true")
    max_autonomy_level: int = field(default_factory=lambda: int(os.getenv("MAX_AUTONOMY_LEVEL", "2")))
    alert_threshold: str = field(default_factory=lambda: os.getenv("ALERT_THRESHOLD", "medium"))
    correction_cooldown_seconds: int = field(default_factory=lambda: int(os.getenv("CORRECTION_COOLDOWN_SECONDS", "300")))
    max_corrections_per_hour: int = field(default_factory=lambda: int(os.getenv("MAX_CORRECTIONS_PER_HOUR", "20")))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    start_time: datetime = field(default_factory=datetime.utcnow)
    
    compliance_frameworks: list = field(default_factory=lambda: [
        "4th_amendment",
        "5th_amendment",
        "14th_amendment",
        "florida_statutes",
        "rbpd_general_orders",
        "cjis_security_policy",
        "nist_800_53",
        "nij_standards",
    ])
    
    protected_classes: list = field(default_factory=lambda: [
        "race",
        "ethnicity",
        "religion",
        "national_origin",
        "gender",
        "sexual_orientation",
        "disability",
        "age",
        "political_affiliation",
    ])
    
    monitored_engines: list = field(default_factory=lambda: [
        "drone_task_force",
        "robotics",
        "intel_orchestration",
        "human_stability",
        "predictive_ai",
        "city_autonomy",
        "global_awareness",
        "emergency_management",
        "cyber_intel",
        "officer_assist",
        "city_brain",
        "ethics_guardian",
        "enterprise_infra",
        "national_security",
        "detective_ai",
        "threat_intel",
    ])
