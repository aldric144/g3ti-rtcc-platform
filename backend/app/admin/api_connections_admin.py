"""
API Connections Admin Module - CRUD operations for external API connection management
Tab 11: API Connections
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import hashlib
import base64

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService


class APIStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class RefreshFrequency(str, Enum):
    REALTIME = "realtime"
    MINUTE_1 = "1min"
    MINUTE_5 = "5min"
    MINUTE_15 = "15min"
    MINUTE_30 = "30min"
    HOURLY = "hourly"
    DAILY = "daily"


class APIConnectionModel(BaseAdminModel):
    """API Connection database model"""
    api_name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=1000)
    encrypted_key: Optional[str] = Field(None, max_length=2000)
    refresh_frequency: RefreshFrequency = Field(default=RefreshFrequency.MINUTE_5)
    status: APIStatus = Field(default=APIStatus.INACTIVE)
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = Field(None, max_length=1000)
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, max_length=50)  # bearer, basic, api_key
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    notes: Optional[str] = Field(None, max_length=2000)


class APIConnectionCreate(BaseAdminCreate):
    """Schema for creating an API connection"""
    api_name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=1000)
    api_key: Optional[str] = Field(None, max_length=500, description="Will be encrypted before storage")
    refresh_frequency: RefreshFrequency = Field(default=RefreshFrequency.MINUTE_5)
    status: APIStatus = Field(default=APIStatus.INACTIVE)
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, max_length=50)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class APIConnectionUpdate(BaseAdminUpdate):
    """Schema for updating an API connection"""
    api_name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1, max_length=1000)
    api_key: Optional[str] = Field(None, max_length=500)
    refresh_frequency: Optional[RefreshFrequency] = None
    status: Optional[APIStatus] = None
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, max_length=50)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    notes: Optional[str] = Field(None, max_length=2000)


class APIConnectionAdmin(BaseAdminService[APIConnectionModel, APIConnectionCreate, APIConnectionUpdate]):
    """API Connection admin service with CRUD operations and encryption"""
    
    _instance = None
    _encryption_key = "RTCC_API_ENCRYPTION_KEY_2024"  # In production, use proper key management
    
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
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt API key before storage"""
        if not api_key:
            return ""
        # Simple encryption for demo - use proper encryption in production
        encrypted = base64.b64encode(api_key.encode()).decode()
        return f"ENC:{encrypted}"
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        if not encrypted_key or not encrypted_key.startswith("ENC:"):
            return encrypted_key or ""
        try:
            encoded = encrypted_key[4:]
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            return "[DECRYPTION ERROR]"
    
    def _init_demo_data(self):
        """Initialize with demo API connection data"""
        demo_apis = [
            {
                "api_name": "FDOT Traffic Cameras",
                "url": "https://fl511.com/api/cameras",
                "encrypted_key": self._encrypt_key("demo_fdot_key_123"),
                "refresh_frequency": RefreshFrequency.MINUTE_5,
                "status": APIStatus.ACTIVE,
                "auth_type": "api_key",
            },
            {
                "api_name": "ShotSpotter Integration",
                "url": "https://api.shotspotter.com/v2/alerts",
                "encrypted_key": self._encrypt_key("demo_shotspotter_key"),
                "refresh_frequency": RefreshFrequency.REALTIME,
                "status": APIStatus.ACTIVE,
                "auth_type": "bearer",
            },
            {
                "api_name": "Flock LPR",
                "url": "https://api.flocksafety.com/v1/reads",
                "encrypted_key": self._encrypt_key("demo_flock_key"),
                "refresh_frequency": RefreshFrequency.MINUTE_1,
                "status": APIStatus.ACTIVE,
                "auth_type": "bearer",
            },
        ]
        
        for api_data in demo_apis:
            api = APIConnectionModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **api_data
            )
            self._storage[api.id] = api
    
    async def create(self, data: APIConnectionCreate, user_id: str) -> APIConnectionModel:
        """Create a new API connection with encrypted key"""
        encrypted_key = self._encrypt_key(data.api_key) if data.api_key else None
        
        api = APIConnectionModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            api_name=data.api_name,
            url=data.url,
            encrypted_key=encrypted_key,
            refresh_frequency=data.refresh_frequency,
            status=data.status,
            headers=data.headers,
            auth_type=data.auth_type,
            timeout_seconds=data.timeout_seconds,
            notes=data.notes,
        )
        self._storage[api.id] = api
        return api
    
    async def update(self, item_id: str, data: APIConnectionUpdate, user_id: str) -> Optional[APIConnectionModel]:
        """Update an existing API connection"""
        api = self._storage.get(item_id)
        if not api:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Encrypt key if provided
        if 'api_key' in update_data:
            update_data['encrypted_key'] = self._encrypt_key(update_data.pop('api_key'))
        
        for key, value in update_data.items():
            setattr(api, key, value)
        
        api.updated_at = datetime.now(UTC)
        api.updated_by = user_id
        self._storage[item_id] = api
        return api
    
    async def test_connection(self, item_id: str) -> Dict[str, Any]:
        """Test an API connection"""
        api = self._storage.get(item_id)
        if not api:
            return {"error": "API connection not found"}
        
        # Simulate connection test
        result = {
            "api_id": item_id,
            "api_name": api.api_name,
            "url": api.url,
            "status": "success",
            "latency_ms": 125,
            "tested_at": datetime.now(UTC).isoformat()
        }
        
        api.last_sync = datetime.now(UTC)
        api.status = APIStatus.ACTIVE
        self._storage[item_id] = api
        
        return result
    
    async def get_active(self) -> List[APIConnectionModel]:
        """Get all active API connections"""
        return [a for a in self._storage.values() if a.status == APIStatus.ACTIVE]
    
    async def get_decrypted_key(self, item_id: str, user_id: str) -> Optional[str]:
        """Get decrypted API key for authorized users"""
        api = self._storage.get(item_id)
        if not api:
            return None
        # In production, verify user has proper clearance
        return self._decrypt_key(api.encrypted_key)


# Singleton instance
api_connection_admin = APIConnectionAdmin()
