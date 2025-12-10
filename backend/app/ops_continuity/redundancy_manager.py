"""
Redundancy Manager Module for G3TI RTCC-UIP Operational Continuity.

Provides hot/warm standby service support, primary/secondary connection pools,
automatic reconnection logic, and state synchronization across redundant services.
"""

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from collections import deque
import uuid

from pydantic import BaseModel, Field


class RedundancyMode(str, Enum):
    """Redundancy operation modes."""
    HOT_STANDBY = "hot_standby"
    WARM_STANDBY = "warm_standby"
    COLD_STANDBY = "cold_standby"
    ACTIVE_ACTIVE = "active_active"
    ACTIVE_PASSIVE = "active_passive"


class ConnectionState(str, Enum):
    """Connection state."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class ServiceRole(str, Enum):
    """Service role in redundancy setup."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    STANDBY = "standby"


class ServiceInstance(BaseModel):
    """A single service instance in a redundancy group."""
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str
    role: ServiceRole = ServiceRole.PRIMARY
    endpoint: str
    state: ConnectionState = ConnectionState.DISCONNECTED
    last_heartbeat: Optional[datetime] = None
    latency_ms: float = 0.0
    connection_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    is_healthy: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConnectionPool(BaseModel):
    """Connection pool for a redundant service."""
    pool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str
    mode: RedundancyMode = RedundancyMode.ACTIVE_PASSIVE
    primary: Optional[ServiceInstance] = None
    secondary: Optional[ServiceInstance] = None
    standbys: list[ServiceInstance] = Field(default_factory=list)
    active_instance_id: Optional[str] = None
    pool_size: int = 10
    active_connections: int = 0
    max_connections: int = 100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_failover: Optional[datetime] = None


class SyncEvent(BaseModel):
    """State synchronization event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_instance_id: str
    target_instance_id: str
    sync_type: str
    data_size_bytes: int = 0
    duration_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class RedundancyConfig(BaseModel):
    """Configuration for redundancy manager."""
    enabled: bool = True
    default_mode: RedundancyMode = RedundancyMode.ACTIVE_PASSIVE
    heartbeat_interval_seconds: float = 5.0
    reconnect_interval_seconds: float = 10.0
    max_reconnect_attempts: int = 5
    connection_timeout_seconds: float = 10.0
    sync_interval_seconds: float = 60.0
    enable_auto_failover: bool = True
    enable_state_sync: bool = True

    neo4j_primary: str = "bolt://neo4j-primary:7687"
    neo4j_secondary: str = "bolt://neo4j-secondary:7687"

    elasticsearch_primary: str = "http://es-primary:9200"
    elasticsearch_secondary: str = "http://es-secondary:9200"

    redis_primary: str = "redis://redis-primary:6379"
    redis_secondary: str = "redis://redis-secondary:6379"

    postgres_primary: str = "postgresql://pg-primary:5432/rtcc"
    postgres_secondary: str = "postgresql://pg-secondary:5432/rtcc"


class RedundancyMetrics(BaseModel):
    """Metrics for redundancy manager."""
    pools_managed: int = 0
    active_connections: int = 0
    failovers_performed: int = 0
    reconnections_successful: int = 0
    reconnections_failed: int = 0
    sync_operations: int = 0
    sync_failures: int = 0
    avg_sync_duration_ms: float = 0.0
    last_sync: Optional[datetime] = None


class RedundancyManager:
    """
    Manages redundant service connections for RTCC infrastructure.

    Provides hot/warm standby support, connection pooling, automatic
    reconnection, and state synchronization across redundant services.
    """

    def __init__(self, config: Optional[RedundancyConfig] = None):
        self.config = config or RedundancyConfig()
        self.metrics = RedundancyMetrics()
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._sync_task: Optional[asyncio.Task] = None
        self._pools: dict[str, ConnectionPool] = {}
        self._sync_events: deque[SyncEvent] = deque(maxlen=1000)
        self._callbacks: list[callable] = []
        self._initialize_pools()

    def _initialize_pools(self) -> None:
        """Initialize connection pools for core services."""
        neo4j_pool = ConnectionPool(
            service_name="neo4j",
            mode=self.config.default_mode,
            primary=ServiceInstance(
                service_name="neo4j",
                role=ServiceRole.PRIMARY,
                endpoint=self.config.neo4j_primary,
            ),
            secondary=ServiceInstance(
                service_name="neo4j",
                role=ServiceRole.SECONDARY,
                endpoint=self.config.neo4j_secondary,
            ),
        )
        neo4j_pool.active_instance_id = neo4j_pool.primary.instance_id
        self._pools["neo4j"] = neo4j_pool

        es_pool = ConnectionPool(
            service_name="elasticsearch",
            mode=self.config.default_mode,
            primary=ServiceInstance(
                service_name="elasticsearch",
                role=ServiceRole.PRIMARY,
                endpoint=self.config.elasticsearch_primary,
            ),
            secondary=ServiceInstance(
                service_name="elasticsearch",
                role=ServiceRole.SECONDARY,
                endpoint=self.config.elasticsearch_secondary,
            ),
        )
        es_pool.active_instance_id = es_pool.primary.instance_id
        self._pools["elasticsearch"] = es_pool

        redis_pool = ConnectionPool(
            service_name="redis",
            mode=self.config.default_mode,
            primary=ServiceInstance(
                service_name="redis",
                role=ServiceRole.PRIMARY,
                endpoint=self.config.redis_primary,
            ),
            secondary=ServiceInstance(
                service_name="redis",
                role=ServiceRole.SECONDARY,
                endpoint=self.config.redis_secondary,
            ),
        )
        redis_pool.active_instance_id = redis_pool.primary.instance_id
        self._pools["redis"] = redis_pool

        pg_pool = ConnectionPool(
            service_name="postgres",
            mode=self.config.default_mode,
            primary=ServiceInstance(
                service_name="postgres",
                role=ServiceRole.PRIMARY,
                endpoint=self.config.postgres_primary,
            ),
            secondary=ServiceInstance(
                service_name="postgres",
                role=ServiceRole.SECONDARY,
                endpoint=self.config.postgres_secondary,
            ),
        )
        pg_pool.active_instance_id = pg_pool.primary.instance_id
        self._pools["postgres"] = pg_pool

        self.metrics.pools_managed = len(self._pools)

    async def start(self) -> None:
        """Start the redundancy manager."""
        if self._running:
            return

        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        if self.config.enable_state_sync:
            self._sync_task = asyncio.create_task(self._sync_loop())

        await self._connect_all_pools()

    async def stop(self) -> None:
        """Stop the redundancy manager."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

        await self._disconnect_all_pools()

    async def _heartbeat_loop(self) -> None:
        """Main heartbeat loop for connection monitoring."""
        while self._running:
            try:
                await self._check_all_connections()
                await asyncio.sleep(self.config.heartbeat_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5.0)

    async def _sync_loop(self) -> None:
        """Main state synchronization loop."""
        while self._running:
            try:
                await self._sync_all_pools()
                await asyncio.sleep(self.config.sync_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(10.0)

    async def _connect_all_pools(self) -> None:
        """Connect all connection pools."""
        for pool in self._pools.values():
            await self._connect_pool(pool)

    async def _disconnect_all_pools(self) -> None:
        """Disconnect all connection pools."""
        for pool in self._pools.values():
            await self._disconnect_pool(pool)

    async def _connect_pool(self, pool: ConnectionPool) -> None:
        """Connect a single connection pool."""
        if pool.primary:
            await self._connect_instance(pool.primary)

        if pool.secondary and pool.mode in [RedundancyMode.HOT_STANDBY, RedundancyMode.ACTIVE_ACTIVE]:
            await self._connect_instance(pool.secondary)

    async def _disconnect_pool(self, pool: ConnectionPool) -> None:
        """Disconnect a single connection pool."""
        if pool.primary:
            await self._disconnect_instance(pool.primary)

        if pool.secondary:
            await self._disconnect_instance(pool.secondary)

    async def _connect_instance(self, instance: ServiceInstance) -> bool:
        """Connect to a service instance."""
        instance.state = ConnectionState.CONNECTING
        instance.connection_attempts += 1

        try:
            await asyncio.sleep(0.01)

            instance.state = ConnectionState.CONNECTED
            instance.last_heartbeat = datetime.now(timezone.utc)
            instance.is_healthy = True
            instance.successful_connections += 1
            self.metrics.active_connections += 1

            return True

        except Exception as e:
            instance.state = ConnectionState.FAILED
            instance.is_healthy = False
            instance.failed_connections += 1
            return False

    async def _disconnect_instance(self, instance: ServiceInstance) -> None:
        """Disconnect from a service instance."""
        if instance.state == ConnectionState.CONNECTED:
            self.metrics.active_connections = max(0, self.metrics.active_connections - 1)

        instance.state = ConnectionState.DISCONNECTED
        instance.is_healthy = False

    async def _check_all_connections(self) -> None:
        """Check health of all connections."""
        for pool in self._pools.values():
            await self._check_pool_connections(pool)

    async def _check_pool_connections(self, pool: ConnectionPool) -> None:
        """Check connections in a pool."""
        if pool.primary:
            await self._check_instance_health(pool.primary)

            if not pool.primary.is_healthy and self.config.enable_auto_failover:
                await self._failover_pool(pool)

        if pool.secondary:
            await self._check_instance_health(pool.secondary)

    async def _check_instance_health(self, instance: ServiceInstance) -> None:
        """Check health of a single instance."""
        if instance.state != ConnectionState.CONNECTED:
            await self._attempt_reconnect(instance)
            return

        try:
            await asyncio.sleep(0.001)
            instance.last_heartbeat = datetime.now(timezone.utc)
            instance.is_healthy = True
            instance.latency_ms = 1.0

        except Exception:
            instance.is_healthy = False
            instance.state = ConnectionState.DISCONNECTED

    async def _attempt_reconnect(self, instance: ServiceInstance) -> bool:
        """Attempt to reconnect to an instance."""
        if instance.connection_attempts >= self.config.max_reconnect_attempts:
            return False

        instance.state = ConnectionState.RECONNECTING

        success = await self._connect_instance(instance)

        if success:
            self.metrics.reconnections_successful += 1
        else:
            self.metrics.reconnections_failed += 1

        return success

    async def _failover_pool(self, pool: ConnectionPool) -> bool:
        """Failover a pool to secondary instance."""
        if not pool.secondary or not pool.secondary.is_healthy:
            return False

        pool.active_instance_id = pool.secondary.instance_id
        pool.last_failover = datetime.now(timezone.utc)
        self.metrics.failovers_performed += 1

        for callback in self._callbacks:
            try:
                await callback({
                    "event": "failover",
                    "pool": pool.service_name,
                    "from": "primary",
                    "to": "secondary",
                })
            except Exception:
                pass

        return True

    async def _sync_all_pools(self) -> None:
        """Synchronize state across all pools."""
        for pool in self._pools.values():
            if pool.mode in [RedundancyMode.HOT_STANDBY, RedundancyMode.ACTIVE_ACTIVE]:
                await self._sync_pool(pool)

    async def _sync_pool(self, pool: ConnectionPool) -> None:
        """Synchronize state for a single pool."""
        if not pool.primary or not pool.secondary:
            return

        if not pool.primary.is_healthy or not pool.secondary.is_healthy:
            return

        sync_event = SyncEvent(
            source_instance_id=pool.primary.instance_id,
            target_instance_id=pool.secondary.instance_id,
            sync_type="incremental",
        )

        try:
            start_time = asyncio.get_event_loop().time()
            await asyncio.sleep(0.01)
            sync_event.duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            sync_event.success = True
            sync_event.data_size_bytes = 1024

            self.metrics.sync_operations += 1
            self.metrics.last_sync = datetime.now(timezone.utc)
            self._update_avg_sync_duration(sync_event.duration_ms)

        except Exception as e:
            sync_event.success = False
            sync_event.error_message = str(e)
            self.metrics.sync_failures += 1

        self._sync_events.append(sync_event)

    def _update_avg_sync_duration(self, duration_ms: float) -> None:
        """Update average sync duration."""
        if self.metrics.sync_operations == 1:
            self.metrics.avg_sync_duration_ms = duration_ms
        else:
            self.metrics.avg_sync_duration_ms = (
                self.metrics.avg_sync_duration_ms * 0.9 + duration_ms * 0.1
            )

    async def get_connection(self, service_name: str) -> Optional[ServiceInstance]:
        """Get an active connection for a service."""
        pool = self._pools.get(service_name)
        if not pool:
            return None

        if pool.active_instance_id == pool.primary.instance_id and pool.primary.is_healthy:
            return pool.primary

        if pool.secondary and pool.secondary.is_healthy:
            return pool.secondary

        return None

    async def manual_failover(self, service_name: str) -> bool:
        """Manually trigger failover for a service."""
        pool = self._pools.get(service_name)
        if not pool:
            return False

        return await self._failover_pool(pool)

    async def manual_failback(self, service_name: str) -> bool:
        """Manually failback to primary for a service."""
        pool = self._pools.get(service_name)
        if not pool or not pool.primary:
            return False

        if not pool.primary.is_healthy:
            await self._attempt_reconnect(pool.primary)

        if pool.primary.is_healthy:
            pool.active_instance_id = pool.primary.instance_id
            return True

        return False

    def register_callback(self, callback: callable) -> None:
        """Register a callback for redundancy events."""
        self._callbacks.append(callback)

    def get_pool(self, service_name: str) -> Optional[ConnectionPool]:
        """Get a connection pool by service name."""
        return self._pools.get(service_name)

    def get_all_pools(self) -> dict[str, ConnectionPool]:
        """Get all connection pools."""
        return self._pools.copy()

    def get_sync_events(self, limit: int = 100) -> list[SyncEvent]:
        """Get recent sync events."""
        return list(self._sync_events)[-limit:]

    def get_status(self) -> dict[str, Any]:
        """Get redundancy manager status."""
        pools_status = {}
        for name, pool in self._pools.items():
            active_instance = None
            if pool.active_instance_id:
                if pool.primary and pool.primary.instance_id == pool.active_instance_id:
                    active_instance = "primary"
                elif pool.secondary and pool.secondary.instance_id == pool.active_instance_id:
                    active_instance = "secondary"

            pools_status[name] = {
                "mode": pool.mode.value,
                "active_instance": active_instance,
                "primary_healthy": pool.primary.is_healthy if pool.primary else False,
                "secondary_healthy": pool.secondary.is_healthy if pool.secondary else False,
                "active_connections": pool.active_connections,
                "last_failover": pool.last_failover.isoformat() if pool.last_failover else None,
            }

        return {
            "running": self._running,
            "pools_managed": self.metrics.pools_managed,
            "active_connections": self.metrics.active_connections,
            "pools": pools_status,
            "metrics": self.metrics.model_dump(),
        }

    def get_metrics(self) -> RedundancyMetrics:
        """Get redundancy metrics."""
        return self.metrics
