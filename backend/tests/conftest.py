"""
Pytest configuration and fixtures for RTCC-UIP tests.

This module provides shared fixtures and configuration for all tests.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.security import create_access_token, hash_password
from app.main import app
from app.schemas.auth import Role, UserInDB

# =============================================================================
# Event Loop Configuration
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Application Fixtures
# =============================================================================


@pytest.fixture
def test_app() -> FastAPI:
    """Get the FastAPI application instance."""
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a synchronous test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


# =============================================================================
# User Fixtures
# =============================================================================


@pytest.fixture
def test_user_password() -> str:
    """Get test user password."""
    return "TestPassword123!"


@pytest.fixture
def test_user(test_user_password: str) -> UserInDB:
    """Create a test user."""
    return UserInDB(
        id="test-user-001",
        username="testuser",
        email="testuser@agency.gov",
        hashed_password=hash_password(test_user_password),
        first_name="Test",
        last_name="User",
        badge_number="12345",
        department="Testing",
        role=Role.DETECTIVE,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def admin_user(test_user_password: str) -> UserInDB:
    """Create an admin test user."""
    return UserInDB(
        id="admin-user-001",
        username="adminuser",
        email="admin@agency.gov",
        hashed_password=hash_password(test_user_password),
        first_name="Admin",
        last_name="User",
        badge_number="00001",
        department="Administration",
        role=Role.ADMIN,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def officer_user(test_user_password: str) -> UserInDB:
    """Create an officer test user."""
    return UserInDB(
        id="officer-user-001",
        username="officeruser",
        email="officer@agency.gov",
        hashed_password=hash_password(test_user_password),
        first_name="Officer",
        last_name="User",
        badge_number="54321",
        department="Patrol",
        role=Role.OFFICER,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# =============================================================================
# Token Fixtures
# =============================================================================


@pytest.fixture
def test_user_token(test_user: UserInDB) -> str:
    """Create an access token for test user."""
    return create_access_token(
        subject=test_user.id,
        username=test_user.username,
        role=test_user.role,
    )


@pytest.fixture
def admin_user_token(admin_user: UserInDB) -> str:
    """Create an access token for admin user."""
    return create_access_token(
        subject=admin_user.id,
        username=admin_user.username,
        role=admin_user.role,
    )


@pytest.fixture
def officer_user_token(officer_user: UserInDB) -> str:
    """Create an access token for officer user."""
    return create_access_token(
        subject=officer_user.id,
        username=officer_user.username,
        role=officer_user.role,
    )


@pytest.fixture
def expired_token(test_user: UserInDB) -> str:
    """Create an expired access token."""
    return create_access_token(
        subject=test_user.id,
        username=test_user.username,
        role=test_user.role,
        expires_delta=timedelta(seconds=-1),
    )


# =============================================================================
# Auth Headers Fixtures
# =============================================================================


@pytest.fixture
def auth_headers(test_user_token: str) -> dict[str, str]:
    """Get authorization headers for test user."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def admin_auth_headers(admin_user_token: str) -> dict[str, str]:
    """Get authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_user_token}"}


@pytest.fixture
def officer_auth_headers(officer_user_token: str) -> dict[str, str]:
    """Get authorization headers for officer user."""
    return {"Authorization": f"Bearer {officer_user_token}"}


# =============================================================================
# Mock Database Fixtures
# =============================================================================


@pytest.fixture
def mock_neo4j_driver() -> MagicMock:
    """Create a mock Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return driver


@pytest.fixture
def mock_elasticsearch_client() -> MagicMock:
    """Create a mock Elasticsearch client."""
    client = MagicMock()
    client.search = AsyncMock(return_value={"hits": {"hits": [], "total": {"value": 0}}})
    client.index = AsyncMock(return_value={"result": "created"})
    return client


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Create a mock Redis client."""
    client = MagicMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.publish = AsyncMock(return_value=1)
    return client


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_person_data() -> dict:
    """Get sample person entity data."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-05-15",
        "gender": "male",
        "aliases": ["Johnny D", "JD"],
        "identifiers": ["DL-TX-12345678"],
    }


@pytest.fixture
def sample_vehicle_data() -> dict:
    """Get sample vehicle entity data."""
    return {
        "plate_number": "ABC-1234",
        "plate_state": "TX",
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "color": "Blue",
        "vin": "1HGBH41JXMN109186",
    }


@pytest.fixture
def sample_incident_data() -> dict:
    """Get sample incident entity data."""
    return {
        "incident_number": "2024-001234",
        "incident_type": "robbery",
        "status": "open",
        "reported_at": "2024-01-15T10:30:00Z",
        "location": {"latitude": 29.7604, "longitude": -95.3698},
        "address": "1200 Main St, Houston, TX 77002",
        "description": "Armed robbery at convenience store",
    }


@pytest.fixture
def sample_event_data() -> dict:
    """Get sample RTCC event data."""
    return {
        "id": "event-001",
        "event_type": "gunshot",
        "source": "shotspotter",
        "priority": "critical",
        "title": "Gunshot Detected",
        "description": "3 rounds detected in downtown area",
        "location": {"latitude": 29.7604, "longitude": -95.3698},
        "address": "1200 Main St, Houston, TX 77002",
        "timestamp": "2024-01-15T10:30:00Z",
        "acknowledged": False,
    }
