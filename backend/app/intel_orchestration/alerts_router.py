"""
Alerts Router for G3TI RTCC-UIP.

This module routes fused intelligence to appropriate destinations including
dashboards, dispatch, mobile units, and automated systems.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AlertDestination(str, Enum):
    """Alert routing destinations."""
    RTCC_DASHBOARD = "rtcc_dashboard"
    TACTICAL_DASHBOARD = "tactical_dashboard"
    INVESTIGATIONS_DASHBOARD = "investigations_dashboard"
    OFFICER_SAFETY_ALERTS = "officer_safety_alerts"
    DISPATCH_COMMS = "dispatch_comms"
    MOBILE_MDT = "mobile_mdt"
    COMMAND_CENTER = "command_center"
    AUTO_BULLETIN = "auto_bulletin"
    BOLO_GENERATOR = "bolo_generator"
    WEBSOCKET_FUSED = "websocket_fused"
    WEBSOCKET_ALERTS = "websocket_alerts"
    WEBSOCKET_PRIORITY = "websocket_priority"
    EMAIL_NOTIFICATION = "email_notification"
    SMS_NOTIFICATION = "sms_notification"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    IMMEDIATE = "immediate"
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DeliveryStatus(str, Enum):
    """Alert delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    EXPIRED = "expired"


class RoutingConfig(BaseModel):
    """Configuration for alerts routing."""
    enabled: bool = True
    max_concurrent_deliveries: int = 50
    delivery_timeout_seconds: float = 10.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    enable_websocket_broadcast: bool = True
    enable_auto_bulletins: bool = True
    enable_bolo_generation: bool = True
    enable_email_notifications: bool = False
    enable_sms_notifications: bool = False
    default_destinations: list[AlertDestination] = Field(default_factory=lambda: [
        AlertDestination.RTCC_DASHBOARD,
        AlertDestination.WEBSOCKET_FUSED,
    ])
    tier_routing: dict[str, list[str]] = Field(default_factory=lambda: {
        "tier_1": [
            "rtcc_dashboard",
            "officer_safety_alerts",
            "dispatch_comms",
            "mobile_mdt",
            "tactical_dashboard",
            "command_center",
            "websocket_alerts",
            "websocket_priority",
        ],
        "tier_2": [
            "rtcc_dashboard",
            "investigations_dashboard",
            "tactical_dashboard",
            "websocket_fused",
        ],
        "tier_3": [
            "rtcc_dashboard",
            "tactical_dashboard",
            "websocket_fused",
        ],
        "tier_4": [
            "rtcc_dashboard",
            "websocket_fused",
        ],
    })


class RoutedAlert(BaseModel):
    """An alert that has been routed."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str  # ID of the source intelligence
    destination: AlertDestination
    priority: AlertPriority
    status: DeliveryStatus = DeliveryStatus.PENDING
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    delivered_at: datetime | None = None
    acknowledged_at: datetime | None = None
    retry_count: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeliveryResult(BaseModel):
    """Result of alert delivery."""
    alert_id: str
    destination: AlertDestination
    success: bool
    status: DeliveryStatus
    delivered_at: datetime | None = None
    error: str | None = None


class RoutingMetrics(BaseModel):
    """Metrics for routing operations."""
    alerts_routed: int = 0
    alerts_delivered: int = 0
    alerts_failed: int = 0
    alerts_acknowledged: int = 0
    avg_delivery_time_ms: float = 0.0
    by_destination: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)


class AlertsRouter:
    """
    Routes fused intelligence to appropriate destinations.

    Supports multiple delivery channels including dashboards, dispatch,
    mobile units, and automated bulletin generation.
    """

    def __init__(self, config: RoutingConfig | None = None):
        self.config = config or RoutingConfig()
        self.metrics = RoutingMetrics()
        self._delivery_queue: asyncio.Queue[RoutedAlert] = asyncio.Queue()
        self._pending_alerts: dict[str, RoutedAlert] = {}
        self._destination_handlers: dict[AlertDestination, Callable] = {}
        self._websocket_connections: dict[str, set] = {
            "fused": set(),
            "alerts": set(),
            "priority": set(),
            "pipelines": set(),
        }
        self._running = False
        self._workers: list[asyncio.Task] = []

        # Register default handlers
        self._register_default_handlers()

        logger.info("AlertsRouter initialized")

    def _register_default_handlers(self):
        """Register default destination handlers."""
        self._destination_handlers[AlertDestination.RTCC_DASHBOARD] = self._handle_dashboard
        self._destination_handlers[AlertDestination.TACTICAL_DASHBOARD] = self._handle_dashboard
        self._destination_handlers[AlertDestination.INVESTIGATIONS_DASHBOARD] = self._handle_dashboard
        self._destination_handlers[AlertDestination.OFFICER_SAFETY_ALERTS] = self._handle_officer_safety
        self._destination_handlers[AlertDestination.DISPATCH_COMMS] = self._handle_dispatch
        self._destination_handlers[AlertDestination.MOBILE_MDT] = self._handle_mobile
        self._destination_handlers[AlertDestination.COMMAND_CENTER] = self._handle_command_center
        self._destination_handlers[AlertDestination.AUTO_BULLETIN] = self._handle_auto_bulletin
        self._destination_handlers[AlertDestination.BOLO_GENERATOR] = self._handle_bolo
        self._destination_handlers[AlertDestination.WEBSOCKET_FUSED] = self._handle_websocket_fused
        self._destination_handlers[AlertDestination.WEBSOCKET_ALERTS] = self._handle_websocket_alerts
        self._destination_handlers[AlertDestination.WEBSOCKET_PRIORITY] = self._handle_websocket_priority

    async def start(self):
        """Start the router."""
        if self._running:
            return

        self._running = True

        # Start delivery workers
        for i in range(min(4, self.config.max_concurrent_deliveries)):
            worker = asyncio.create_task(self._delivery_worker(i))
            self._workers.append(worker)

        logger.info("AlertsRouter started with %d workers", len(self._workers))

    async def stop(self):
        """Stop the router."""
        self._running = False

        for worker in self._workers:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

        self._workers.clear()
        logger.info("AlertsRouter stopped")

    async def route(self, intelligence: Any) -> list[DeliveryResult]:
        """
        Route fused intelligence to appropriate destinations.

        Returns list of delivery results.
        """
        if not self.config.enabled:
            return []

        # Extract routing information
        tier = self._get_tier(intelligence)
        priority = self._get_priority(tier)
        destinations = self._get_destinations(intelligence, tier)
        payload = self._create_payload(intelligence)

        results = []
        source_id = intelligence.id if hasattr(intelligence, "id") else str(uuid4())

        for destination in destinations:
            alert = RoutedAlert(
                source_id=source_id,
                destination=destination,
                priority=priority,
                payload=payload,
            )

            self._pending_alerts[alert.id] = alert
            await self._delivery_queue.put(alert)
            self.metrics.alerts_routed += 1

            # Update metrics
            dest_key = destination.value
            self.metrics.by_destination[dest_key] = (
                self.metrics.by_destination.get(dest_key, 0) + 1
            )
            self.metrics.by_priority[priority.value] = (
                self.metrics.by_priority.get(priority.value, 0) + 1
            )

        return results

    def _get_tier(self, intelligence: Any) -> str:
        """Get tier from intelligence."""
        if hasattr(intelligence, "tier"):
            return intelligence.tier.value if hasattr(intelligence.tier, "value") else str(intelligence.tier)
        return "tier_4"

    def _get_priority(self, tier: str) -> AlertPriority:
        """Get alert priority from tier."""
        priority_map = {
            "tier_1": AlertPriority.IMMEDIATE,
            "tier_2": AlertPriority.HIGH,
            "tier_3": AlertPriority.NORMAL,
            "tier_4": AlertPriority.LOW,
        }
        return priority_map.get(tier, AlertPriority.NORMAL)

    def _get_destinations(
        self, intelligence: Any, tier: str
    ) -> list[AlertDestination]:
        """Get routing destinations based on intelligence and tier."""
        destinations = set()

        # Get tier-based destinations
        tier_dests = self.config.tier_routing.get(tier, [])
        for dest_str in tier_dests:
            try:
                destinations.add(AlertDestination(dest_str))
            except ValueError:
                pass

        # Get explicit destinations from intelligence
        if hasattr(intelligence, "routing_destinations"):
            for dest_str in intelligence.routing_destinations:
                try:
                    destinations.add(AlertDestination(dest_str))
                except ValueError:
                    pass

        # Add default destinations
        for dest in self.config.default_destinations:
            destinations.add(dest)

        # Filter based on config
        if not self.config.enable_auto_bulletins:
            destinations.discard(AlertDestination.AUTO_BULLETIN)
        if not self.config.enable_bolo_generation:
            destinations.discard(AlertDestination.BOLO_GENERATOR)
        if not self.config.enable_email_notifications:
            destinations.discard(AlertDestination.EMAIL_NOTIFICATION)
        if not self.config.enable_sms_notifications:
            destinations.discard(AlertDestination.SMS_NOTIFICATION)

        return list(destinations)

    def _create_payload(self, intelligence: Any) -> dict[str, Any]:
        """Create alert payload from intelligence."""
        if hasattr(intelligence, "model_dump"):
            return intelligence.model_dump(mode="json")
        elif isinstance(intelligence, dict):
            return intelligence
        else:
            return {"data": str(intelligence)}

    async def _delivery_worker(self, worker_id: int):
        """Worker task to deliver alerts."""
        while self._running:
            try:
                alert = await asyncio.wait_for(
                    self._delivery_queue.get(),
                    timeout=1.0,
                )

                start_time = datetime.now(UTC)
                result = await self._deliver_alert(alert)
                elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

                # Update metrics
                self.metrics.avg_delivery_time_ms = (
                    self.metrics.avg_delivery_time_ms * 0.9 + elapsed_ms * 0.1
                )

                if result.success:
                    self.metrics.alerts_delivered += 1
                else:
                    self.metrics.alerts_failed += 1

                    # Retry if applicable
                    if alert.retry_count < self.config.retry_attempts:
                        alert.retry_count += 1
                        await asyncio.sleep(self.config.retry_delay_seconds)
                        await self._delivery_queue.put(alert)

            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Delivery worker %d error: %s", worker_id, e)

    async def _deliver_alert(self, alert: RoutedAlert) -> DeliveryResult:
        """Deliver an alert to its destination."""
        handler = self._destination_handlers.get(alert.destination)

        if not handler:
            return DeliveryResult(
                alert_id=alert.id,
                destination=alert.destination,
                success=False,
                status=DeliveryStatus.FAILED,
                error=f"No handler for destination: {alert.destination}",
            )

        try:
            await asyncio.wait_for(
                handler(alert),
                timeout=self.config.delivery_timeout_seconds,
            )

            alert.status = DeliveryStatus.DELIVERED
            alert.delivered_at = datetime.now(UTC)

            return DeliveryResult(
                alert_id=alert.id,
                destination=alert.destination,
                success=True,
                status=DeliveryStatus.DELIVERED,
                delivered_at=alert.delivered_at,
            )

        except TimeoutError:
            alert.status = DeliveryStatus.FAILED
            alert.error_message = "Delivery timeout"

            return DeliveryResult(
                alert_id=alert.id,
                destination=alert.destination,
                success=False,
                status=DeliveryStatus.FAILED,
                error="Delivery timeout",
            )

        except Exception as e:
            alert.status = DeliveryStatus.FAILED
            alert.error_message = str(e)

            return DeliveryResult(
                alert_id=alert.id,
                destination=alert.destination,
                success=False,
                status=DeliveryStatus.FAILED,
                error=str(e),
            )

    async def _handle_dashboard(self, alert: RoutedAlert):
        """Handle dashboard delivery."""
        # Dashboard delivery is handled via WebSocket
        channel = "fused"
        await self._broadcast_to_channel(channel, {
            "type": "dashboard_alert",
            "destination": alert.destination.value,
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_officer_safety(self, alert: RoutedAlert):
        """Handle officer safety alert delivery."""
        # High priority broadcast
        await self._broadcast_to_channel("alerts", {
            "type": "officer_safety_alert",
            "priority": "immediate",
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
            "requires_acknowledgment": True,
        })

        # Also broadcast to priority channel
        await self._broadcast_to_channel("priority", {
            "type": "officer_safety",
            "alert_id": alert.id,
            "payload": alert.payload,
        })

    async def _handle_dispatch(self, alert: RoutedAlert):
        """Handle dispatch/comms delivery."""
        await self._broadcast_to_channel("alerts", {
            "type": "dispatch_alert",
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_mobile(self, alert: RoutedAlert):
        """Handle mobile/MDT delivery."""
        await self._broadcast_to_channel("alerts", {
            "type": "mobile_alert",
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_command_center(self, alert: RoutedAlert):
        """Handle command center delivery."""
        await self._broadcast_to_channel("priority", {
            "type": "command_center_alert",
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_auto_bulletin(self, alert: RoutedAlert):
        """Handle automatic bulletin generation."""
        if not self.config.enable_auto_bulletins:
            return

        bulletin = self._generate_bulletin(alert)

        await self._broadcast_to_channel("fused", {
            "type": "auto_bulletin",
            "bulletin": bulletin,
            "source_alert_id": alert.id,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def _generate_bulletin(self, alert: RoutedAlert) -> dict[str, Any]:
        """Generate an automatic bulletin from alert."""
        payload = alert.payload

        return {
            "id": str(uuid4()),
            "type": "intelligence_bulletin",
            "priority": alert.priority.value,
            "title": payload.get("title", "Intelligence Bulletin"),
            "summary": payload.get("summary", ""),
            "details": payload.get("entities", {}),
            "recommended_actions": payload.get("recommended_actions", []),
            "generated_at": datetime.now(UTC).isoformat(),
            "valid_until": None,
            "distribution": "all_units",
        }

    async def _handle_bolo(self, alert: RoutedAlert):
        """Handle BOLO generation."""
        if not self.config.enable_bolo_generation:
            return

        bolo = self._generate_bolo(alert)

        if bolo:
            await self._broadcast_to_channel("alerts", {
                "type": "bolo",
                "bolo": bolo,
                "source_alert_id": alert.id,
                "timestamp": datetime.now(UTC).isoformat(),
            })

    def _generate_bolo(self, alert: RoutedAlert) -> dict[str, Any] | None:
        """Generate BOLO from alert if applicable."""
        payload = alert.payload
        entities = payload.get("entities", {})

        # Check if BOLO-worthy
        categories = payload.get("categories", [])
        if not any(c in ["person", "vehicle"] for c in categories):
            return None

        bolo = {
            "id": str(uuid4()),
            "type": "bolo",
            "priority": alert.priority.value,
            "subject": {},
            "description": payload.get("summary", ""),
            "last_known_location": entities.get("location"),
            "issued_at": datetime.now(UTC).isoformat(),
            "issued_by": "RTCC Intelligence System",
        }

        # Add person details
        if "person" in entities:
            bolo["subject"]["person"] = entities["person"]

        # Add vehicle details
        if "vehicle" in entities:
            bolo["subject"]["vehicle"] = entities["vehicle"]

        return bolo

    async def _handle_websocket_fused(self, alert: RoutedAlert):
        """Handle WebSocket fused channel delivery."""
        await self._broadcast_to_channel("fused", {
            "type": "fused_intelligence",
            "alert_id": alert.id,
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_websocket_alerts(self, alert: RoutedAlert):
        """Handle WebSocket alerts channel delivery."""
        await self._broadcast_to_channel("alerts", {
            "type": "alert",
            "alert_id": alert.id,
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _handle_websocket_priority(self, alert: RoutedAlert):
        """Handle WebSocket priority channel delivery."""
        await self._broadcast_to_channel("priority", {
            "type": "priority_alert",
            "alert_id": alert.id,
            "priority": alert.priority.value,
            "payload": alert.payload,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def _broadcast_to_channel(self, channel: str, message: dict[str, Any]):
        """Broadcast message to WebSocket channel."""
        connections = self._websocket_connections.get(channel, set())

        for ws in list(connections):
            try:
                await ws.send_json(message)
            except Exception:
                connections.discard(ws)

    def register_websocket(self, channel: str, websocket):
        """Register a WebSocket connection to a channel."""
        if channel in self._websocket_connections:
            self._websocket_connections[channel].add(websocket)

    def unregister_websocket(self, channel: str, websocket):
        """Unregister a WebSocket connection from a channel."""
        if channel in self._websocket_connections:
            self._websocket_connections[channel].discard(websocket)

    def register_destination_handler(
        self, destination: AlertDestination, handler: Callable
    ):
        """Register a custom handler for a destination."""
        self._destination_handlers[destination] = handler

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert."""
        alert = self._pending_alerts.get(alert_id)
        if not alert:
            return False

        alert.status = DeliveryStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(UTC)
        alert.metadata["acknowledged_by"] = user_id

        self.metrics.alerts_acknowledged += 1

        return True

    def get_pending_alerts(self) -> list[RoutedAlert]:
        """Get all pending alerts."""
        return [
            a for a in self._pending_alerts.values()
            if a.status == DeliveryStatus.PENDING
        ]

    def get_alert(self, alert_id: str) -> RoutedAlert | None:
        """Get a specific alert."""
        return self._pending_alerts.get(alert_id)

    def get_metrics(self) -> RoutingMetrics:
        """Get routing metrics."""
        return self.metrics

    def get_status(self) -> dict[str, Any]:
        """Get router status."""
        return {
            "running": self._running,
            "workers": len(self._workers),
            "queue_size": self._delivery_queue.qsize(),
            "pending_alerts": len(self._pending_alerts),
            "websocket_connections": {
                channel: len(conns)
                for channel, conns in self._websocket_connections.items()
            },
            "metrics": self.metrics.model_dump(),
            "config": self.config.model_dump(),
        }
