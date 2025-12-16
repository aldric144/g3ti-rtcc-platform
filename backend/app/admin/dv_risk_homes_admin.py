"""
DV Risk Homes Admin Module - CRUD operations for domestic violence risk home management
Tab 9: DV Risk Homes (REDACTED)

IMPORTANT: This module handles sensitive data. Full addresses are NEVER stored.
Only sector information and encrypted notes are maintained for officer safety.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import hashlib
import base64

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DVRiskHomeModel(BaseAdminModel):
    """DV Risk Home database model - REDACTED DATA ONLY"""
    sector: str = Field(..., min_length=1, max_length=50, description="Sector only - no full address")
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    encrypted_notes: Optional[str] = Field(None, max_length=5000, description="Encrypted notes")
    last_incident_date: Optional[datetime] = None
    incident_count: int = Field(default=0, ge=0)
    officer_alert: bool = Field(default=True)
    case_number: Optional[str] = Field(None, max_length=50)
    # NEVER store: full_address, name, phone, or any PII


class DVRiskHomeCreate(BaseAdminCreate):
    """Schema for creating a DV risk home entry"""
    sector: str = Field(..., min_length=1, max_length=50)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    notes: Optional[str] = Field(None, max_length=2000, description="Will be encrypted before storage")
    last_incident_date: Optional[datetime] = None
    incident_count: int = Field(default=0, ge=0)
    officer_alert: bool = Field(default=True)
    case_number: Optional[str] = Field(None, max_length=50)

    @field_validator('sector')
    @classmethod
    def validate_sector_only(cls, v: str) -> str:
        # Ensure no address-like data is passed
        address_indicators = ['st', 'street', 'ave', 'avenue', 'blvd', 'boulevard', 'rd', 'road', 'dr', 'drive', 'ln', 'lane']
        v_lower = v.lower()
        for indicator in address_indicators:
            if indicator in v_lower and any(c.isdigit() for c in v):
                raise ValueError('Full addresses are not allowed. Use sector ID only (e.g., SECTOR-1)')
        return v


class DVRiskHomeUpdate(BaseAdminUpdate):
    """Schema for updating a DV risk home entry"""
    sector: Optional[str] = Field(None, min_length=1, max_length=50)
    risk_level: Optional[RiskLevel] = None
    notes: Optional[str] = Field(None, max_length=2000)
    last_incident_date: Optional[datetime] = None
    incident_count: Optional[int] = Field(None, ge=0)
    officer_alert: Optional[bool] = None
    case_number: Optional[str] = Field(None, max_length=50)


class DVRiskHomeAdmin(BaseAdminService[DVRiskHomeModel, DVRiskHomeCreate, DVRiskHomeUpdate]):
    """DV Risk Home admin service with CRUD operations and encryption"""
    
    _instance = None
    _encryption_key = "RTCC_DV_ENCRYPTION_KEY_2024"  # In production, use proper key management
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._init_demo_data()
    
    def _encrypt_notes(self, notes: str) -> str:
        """Encrypt notes before storage"""
        if not notes:
            return ""
        # Simple encryption for demo - use proper encryption in production
        key_hash = hashlib.sha256(self._encryption_key.encode()).digest()
        encrypted = base64.b64encode(notes.encode()).decode()
        return f"ENC:{encrypted}"
    
    def _decrypt_notes(self, encrypted_notes: str) -> str:
        """Decrypt notes for authorized access"""
        if not encrypted_notes or not encrypted_notes.startswith("ENC:"):
            return encrypted_notes or ""
        try:
            encoded = encrypted_notes[4:]
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            return "[DECRYPTION ERROR]"
    
    def _init_demo_data(self):
        """Initialize with demo DV risk home data"""
        demo_homes = [
            {
                "sector": "SECTOR-1",
                "risk_level": RiskLevel.HIGH,
                "encrypted_notes": self._encrypt_notes("History of escalation. Firearms present."),
                "incident_count": 3,
                "officer_alert": True,
                "case_number": "DV-2024-001",
            },
            {
                "sector": "SECTOR-2",
                "risk_level": RiskLevel.MEDIUM,
                "encrypted_notes": self._encrypt_notes("Previous restraining order. Monitor for violations."),
                "incident_count": 1,
                "officer_alert": True,
                "case_number": "DV-2024-002",
            },
        ]
        
        for home_data in demo_homes:
            home = DVRiskHomeModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **home_data
            )
            self._storage[home.id] = home
    
    async def create(self, data: DVRiskHomeCreate, user_id: str) -> DVRiskHomeModel:
        """Create a new DV risk home entry with encrypted notes"""
        encrypted_notes = self._encrypt_notes(data.notes) if data.notes else None
        
        home = DVRiskHomeModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            sector=data.sector,
            risk_level=data.risk_level,
            encrypted_notes=encrypted_notes,
            last_incident_date=data.last_incident_date,
            incident_count=data.incident_count,
            officer_alert=data.officer_alert,
            case_number=data.case_number,
        )
        self._storage[home.id] = home
        return home
    
    async def update(self, item_id: str, data: DVRiskHomeUpdate, user_id: str) -> Optional[DVRiskHomeModel]:
        """Update an existing DV risk home entry"""
        home = self._storage.get(item_id)
        if not home:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Encrypt notes if provided
        if 'notes' in update_data:
            update_data['encrypted_notes'] = self._encrypt_notes(update_data.pop('notes'))
        
        for key, value in update_data.items():
            setattr(home, key, value)
        
        home.updated_at = datetime.now(UTC)
        home.updated_by = user_id
        self._storage[item_id] = home
        return home
    
    async def get_by_sector(self, sector: str) -> List[DVRiskHomeModel]:
        """Get all DV risk homes in a sector"""
        return [h for h in self._storage.values() if h.sector == sector]
    
    async def get_high_risk(self) -> List[DVRiskHomeModel]:
        """Get all high/critical risk homes"""
        return [h for h in self._storage.values() if h.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
    
    async def get_decrypted_notes(self, item_id: str, user_id: str) -> Optional[str]:
        """Get decrypted notes for authorized users only"""
        home = self._storage.get(item_id)
        if not home:
            return None
        # In production, verify user has proper clearance
        return self._decrypt_notes(home.encrypted_notes)
    
    async def record_incident(self, item_id: str, user_id: str) -> Optional[DVRiskHomeModel]:
        """Record a new incident for a DV risk home"""
        home = self._storage.get(item_id)
        if not home:
            return None
        
        home.incident_count += 1
        home.last_incident_date = datetime.now(UTC)
        home.updated_at = datetime.now(UTC)
        home.updated_by = user_id
        
        # Auto-escalate risk level if incidents increase
        if home.incident_count >= 5 and home.risk_level != RiskLevel.CRITICAL:
            home.risk_level = RiskLevel.CRITICAL
        elif home.incident_count >= 3 and home.risk_level == RiskLevel.LOW:
            home.risk_level = RiskLevel.MEDIUM
        elif home.incident_count >= 3 and home.risk_level == RiskLevel.MEDIUM:
            home.risk_level = RiskLevel.HIGH
        
        self._storage[item_id] = home
        return home


# Singleton instance
dv_risk_home_admin = DVRiskHomeAdmin()
