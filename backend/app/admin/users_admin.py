"""
Users Admin Module - CRUD operations for user management
Tab 14: Users
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import hashlib

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService


class UserRole(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    COMMANDER = "commander"
    SYSTEM_INTEGRATOR = "system-integrator"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class UserModel(BaseAdminModel):
    """User database model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    role: UserRole = Field(default=UserRole.VIEWER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    assigned_sector: Optional[str] = Field(None, max_length=50)
    mfa_enabled: bool = Field(default=False)
    mfa_secret: Optional[str] = None
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    full_name: Optional[str] = Field(None, max_length=200)
    badge_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class UserCreate(BaseAdminCreate):
    """Schema for creating a user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = Field(default=UserRole.VIEWER)
    assigned_sector: Optional[str] = Field(None, max_length=50)
    mfa_enabled: bool = Field(default=False)
    full_name: Optional[str] = Field(None, max_length=200)
    badge_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric (underscores allowed)')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseAdminUpdate):
    """Schema for updating a user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    assigned_sector: Optional[str] = Field(None, max_length=50)
    mfa_enabled: Optional[bool] = None
    full_name: Optional[str] = Field(None, max_length=200)
    badge_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class UserAdmin(BaseAdminService[UserModel, UserCreate, UserUpdate]):
    """User admin service with CRUD operations"""
    
    _instance = None
    
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
    
    def _hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _init_demo_data(self):
        """Initialize with demo user data"""
        demo_users = [
            {
                "username": "admin",
                "email": "admin@rbpd.gov",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "password_hash": self._hash_password("admin123"),
                "full_name": "System Administrator",
                "department": "IT",
                "mfa_enabled": True,
            },
            {
                "username": "commander",
                "email": "commander@rbpd.gov",
                "role": UserRole.COMMANDER,
                "status": UserStatus.ACTIVE,
                "password_hash": self._hash_password("commander123"),
                "full_name": "Chief Williams",
                "badge_number": "001",
                "department": "Command",
            },
            {
                "username": "analyst1",
                "email": "analyst1@rbpd.gov",
                "role": UserRole.ANALYST,
                "status": UserStatus.ACTIVE,
                "password_hash": self._hash_password("analyst123"),
                "full_name": "Jane Analyst",
                "assigned_sector": "SECTOR-1",
                "department": "RTCC",
            },
            {
                "username": "supervisor1",
                "email": "supervisor1@rbpd.gov",
                "role": UserRole.SUPERVISOR,
                "status": UserStatus.ACTIVE,
                "password_hash": self._hash_password("supervisor123"),
                "full_name": "Sgt. Johnson",
                "badge_number": "123",
                "department": "Patrol",
            },
        ]
        
        for user_data in demo_users:
            user = UserModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **user_data
            )
            self._storage[user.id] = user
    
    async def create(self, data: UserCreate, user_id: str) -> UserModel:
        """Create a new user"""
        # Check for duplicate username
        for existing in self._storage.values():
            if existing.username == data.username.lower():
                raise ValueError(f"Username '{data.username}' already exists")
        
        user = UserModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            username=data.username.lower(),
            email=data.email,
            role=data.role,
            status=UserStatus.ACTIVE,
            assigned_sector=data.assigned_sector,
            mfa_enabled=data.mfa_enabled,
            password_hash=self._hash_password(data.password),
            full_name=data.full_name,
            badge_number=data.badge_number,
            department=data.department,
            phone=data.phone,
            notes=data.notes,
        )
        self._storage[user.id] = user
        return user
    
    async def update(self, item_id: str, data: UserUpdate, user_id: str) -> Optional[UserModel]:
        """Update an existing user"""
        user = self._storage.get(item_id)
        if not user:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if 'password' in update_data:
            update_data['password_hash'] = self._hash_password(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.now(UTC)
        user.updated_by = user_id
        self._storage[item_id] = user
        return user
    
    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username"""
        for user in self._storage.values():
            if user.username == username.lower():
                return user
        return None
    
    async def get_by_role(self, role: UserRole) -> List[UserModel]:
        """Get all users with a specific role"""
        return [u for u in self._storage.values() if u.role == role]
    
    async def get_by_sector(self, sector: str) -> List[UserModel]:
        """Get all users assigned to a sector"""
        return [u for u in self._storage.values() if u.assigned_sector == sector]
    
    async def record_login(self, user_id: str, success: bool) -> Optional[UserModel]:
        """Record a login attempt"""
        user = self._storage.get(user_id)
        if not user:
            return None
        
        if success:
            user.last_login = datetime.now(UTC)
            user.failed_login_attempts = 0
            user.locked_until = None
        else:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                from datetime import timedelta
                user.locked_until = datetime.now(UTC) + timedelta(minutes=30)
                user.status = UserStatus.LOCKED
        
        self._storage[user_id] = user
        return user
    
    async def unlock_user(self, user_id: str, admin_user_id: str) -> Optional[UserModel]:
        """Unlock a locked user account"""
        user = self._storage.get(user_id)
        if not user:
            return None
        
        user.status = UserStatus.ACTIVE
        user.failed_login_attempts = 0
        user.locked_until = None
        user.updated_at = datetime.now(UTC)
        user.updated_by = admin_user_id
        self._storage[user_id] = user
        return user
    
    async def reset_mfa(self, user_id: str, admin_user_id: str) -> Optional[UserModel]:
        """Reset MFA for a user"""
        user = self._storage.get(user_id)
        if not user:
            return None
        
        user.mfa_enabled = False
        user.mfa_secret = None
        user.updated_at = datetime.now(UTC)
        user.updated_by = admin_user_id
        self._storage[user_id] = user
        return user


# Singleton instance
user_admin = UserAdmin()
