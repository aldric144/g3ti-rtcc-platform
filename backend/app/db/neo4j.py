"""
Neo4j database connection manager for the G3TI RTCC-UIP Backend.

This module provides connection management and query execution for Neo4j,
the graph database used for storing and querying entity relationships.

The Neo4j database stores:
- Person entities and their relationships
- Vehicle records and associations
- Incident reports and linked entities
- Weapons and shell casing evidence
- Geographic locations and camera positions
- License plate records
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.core.config import settings
from app.core.exceptions import Neo4jConnectionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class Neo4jManager:
    """
    Manages Neo4j database connections and provides query execution methods.

    This class implements the singleton pattern to ensure only one driver
    instance is created per application lifecycle.

    Usage:
        manager = Neo4jManager()
        await manager.connect()

        async with manager.session() as session:
            result = await session.run("MATCH (n) RETURN n LIMIT 10")
            records = await result.data()

        await manager.close()
    """

    _instance: "Neo4jManager | None" = None
    _driver: AsyncDriver | None = None

    def __new__(cls) -> "Neo4jManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """
        Establish connection to Neo4j database.

        Raises:
            Neo4jConnectionError: If connection fails
        """
        if self._driver is not None:
            return

        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
            )

            # Verify connectivity
            await self._driver.verify_connectivity()

            logger.info("neo4j_connected", uri=settings.neo4j_uri, database=settings.neo4j_database)

        except AuthError as e:
            logger.error("neo4j_auth_error", error=str(e))
            raise Neo4jConnectionError(f"Neo4j authentication failed: {e}") from e
        except ServiceUnavailable as e:
            logger.error("neo4j_unavailable", error=str(e))
            raise Neo4jConnectionError(f"Neo4j service unavailable: {e}") from e
        except Exception as e:
            logger.error("neo4j_connection_error", error=str(e))
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}") from e

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info("neo4j_disconnected")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a Neo4j session context manager.

        Yields:
            AsyncSession: Neo4j async session

        Raises:
            Neo4jConnectionError: If driver is not connected
        """
        if self._driver is None:
            raise Neo4jConnectionError("Neo4j driver not initialized. Call connect() first.")

        session = self._driver.session(database=settings.neo4j_database)
        try:
            yield session
        finally:
            await session.close()

    async def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            list: Query results as list of dictionaries
        """
        async with self.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()

    async def execute_write(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute a write transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            list: Query results as list of dictionaries
        """
        async with self.session() as session:
            result = await session.execute_write(lambda tx: tx.run(query, parameters or {}))
            return await result.data()

    async def health_check(self) -> bool:
        """
        Check Neo4j connection health.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if self._driver is None:
                return False
            await self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.warning("neo4j_health_check_failed", error=str(e))
            return False

    async def initialize_schema(self) -> None:
        """
        Initialize Neo4j schema with constraints and indexes.

        Creates necessary constraints and indexes for optimal query performance.
        """
        constraints = [
            # Person constraints
            "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            # Vehicle constraints
            "CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT vehicle_plate IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.license_plate IS UNIQUE",
            # Incident constraints
            "CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
            # Weapon constraints
            "CREATE CONSTRAINT weapon_id IF NOT EXISTS FOR (w:Weapon) REQUIRE w.id IS UNIQUE",
            # ShellCasing constraints
            "CREATE CONSTRAINT shellcasing_id IF NOT EXISTS FOR (s:ShellCasing) REQUIRE s.id IS UNIQUE",
            # Address constraints
            "CREATE CONSTRAINT address_id IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE",
            # Camera constraints
            "CREATE CONSTRAINT camera_id IF NOT EXISTS FOR (c:Camera) REQUIRE c.id IS UNIQUE",
            # LicensePlate constraints
            "CREATE CONSTRAINT licenseplate_id IF NOT EXISTS FOR (l:LicensePlate) REQUIRE l.id IS UNIQUE",
        ]

        indexes = [
            # Person indexes
            "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.last_name, p.first_name)",
            "CREATE INDEX person_dob IF NOT EXISTS FOR (p:Person) ON (p.date_of_birth)",
            # Incident indexes
            "CREATE INDEX incident_date IF NOT EXISTS FOR (i:Incident) ON (i.occurred_at)",
            "CREATE INDEX incident_type IF NOT EXISTS FOR (i:Incident) ON (i.incident_type)",
            # Address indexes
            "CREATE INDEX address_location IF NOT EXISTS FOR (a:Address) ON (a.city, a.state)",
            # Camera indexes
            "CREATE INDEX camera_status IF NOT EXISTS FOR (c:Camera) ON (c.status)",
        ]

        async with self.session() as session:
            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    logger.warning("constraint_creation_warning", query=constraint, error=str(e))

            for index in indexes:
                try:
                    await session.run(index)
                except Exception as e:
                    logger.warning("index_creation_warning", query=index, error=str(e))

        logger.info("neo4j_schema_initialized")


# Global Neo4j manager instance
_neo4j_manager: Neo4jManager | None = None


async def get_neo4j() -> Neo4jManager:
    """
    Get the Neo4j manager instance.

    This function is designed to be used as a FastAPI dependency.
    In demo mode, returns a manager even if connection fails.

    Returns:
        Neo4jManager: The Neo4j manager instance
    """
    global _neo4j_manager
    if _neo4j_manager is None:
        _neo4j_manager = Neo4jManager()
        try:
            await _neo4j_manager.connect()
        except Exception as e:
            logger.warning("neo4j_connection_skipped_demo_mode", error=str(e))
    return _neo4j_manager


async def close_neo4j() -> None:
    """Close the Neo4j connection."""
    global _neo4j_manager
    if _neo4j_manager is not None:
        await _neo4j_manager.close()
        _neo4j_manager = None
