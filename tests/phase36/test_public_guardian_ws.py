"""
Test Suite: Public Guardian WebSocket Manager
Phase 36: Public Safety Guardian
"""

import pytest
import asyncio
from datetime import datetime

from backend.app.websockets.public_guardian_ws import (
    PublicGuardianWSManager,
    PublicWSChannel,
    EngagementUpdateType,
    TrustUpdateType,
    SentimentUpdateType,
    UpdateSeverity,
    PublicWSConnection,
    PublicWSMessage,
    EngagementUpdate,
    TrustUpdate,
    SentimentUpdate,
)


class TestPublicGuardianWSManager:
    def setup_method(self):
        self.manager = PublicGuardianWSManager()

    def test_manager_singleton(self):
        manager2 = PublicGuardianWSManager()
        assert self.manager is manager2

    @pytest.mark.asyncio
    async def test_connect(self):
        conn = await self.manager.connect()
        assert conn is not None
        assert conn.connection_id is not None
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_connect_with_channels(self):
        conn = await self.manager.connect(
            channels=[PublicWSChannel.ENGAGEMENT, PublicWSChannel.TRUST]
        )
        assert PublicWSChannel.ENGAGEMENT in conn.channels
        assert PublicWSChannel.TRUST in conn.channels
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_connect_with_metadata(self):
        conn = await self.manager.connect(
            metadata={"user_type": "public", "neighborhood": "Downtown"}
        )
        assert conn.metadata["user_type"] == "public"
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_disconnect(self):
        conn = await self.manager.connect()
        success = await self.manager.disconnect(conn.connection_id)
        assert success is True

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self):
        success = await self.manager.disconnect("nonexistent-id")
        assert success is False

    @pytest.mark.asyncio
    async def test_subscribe(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.ENGAGEMENT])
        success = await self.manager.subscribe(conn.connection_id, PublicWSChannel.TRUST)
        assert success is True
        assert PublicWSChannel.TRUST in conn.channels
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        conn = await self.manager.connect(
            channels=[PublicWSChannel.ENGAGEMENT, PublicWSChannel.TRUST]
        )
        success = await self.manager.unsubscribe(conn.connection_id, PublicWSChannel.TRUST)
        assert success is True
        assert PublicWSChannel.TRUST not in conn.channels
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.ENGAGEMENT])
        message = PublicWSMessage(
            channel=PublicWSChannel.ENGAGEMENT,
            update_type="test",
            title="Test Message",
            message="Test broadcast",
        )
        sent_count = await self.manager.broadcast_to_channel(
            PublicWSChannel.ENGAGEMENT, message
        )
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_engagement_update(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.ENGAGEMENT])
        update = EngagementUpdate(
            update_type=EngagementUpdateType.NEW_EVENT,
            event_id="event-001",
            title="New Town Hall",
            description="Monthly town hall meeting",
        )
        sent_count = await self.manager.broadcast_engagement_update(update)
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_trust_update(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.TRUST])
        update = TrustUpdate(
            update_type=TrustUpdateType.SCORE_UPDATE,
            previous_score=70.0,
            current_score=72.5,
            change=2.5,
            trust_level="high",
        )
        sent_count = await self.manager.broadcast_trust_update(update)
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_sentiment_update(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.SENTIMENT])
        update = SentimentUpdate(
            update_type=SentimentUpdateType.NEW_FEEDBACK,
            feedback_id="fb-001",
            sentiment_level="positive",
            sentiment_score=0.75,
        )
        sent_count = await self.manager.broadcast_sentiment_update(update)
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_new_event(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.ENGAGEMENT])
        sent_count = await self.manager.broadcast_new_event(
            event_id="event-002",
            title="Coffee with Cops",
            description="Informal community engagement",
            location="Local Coffee Shop",
            start_time=datetime.utcnow(),
        )
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_new_alert(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.ENGAGEMENT])
        sent_count = await self.manager.broadcast_new_alert(
            alert_id="alert-001",
            title="Traffic Advisory",
            message="Road closure on Blue Heron Blvd",
            severity=UpdateSeverity.LOW,
        )
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_score_change(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.TRUST])
        sent_count = await self.manager.broadcast_score_change(
            previous_score=70.0,
            current_score=75.0,
            trust_level="high",
        )
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    @pytest.mark.asyncio
    async def test_broadcast_new_feedback(self):
        conn = await self.manager.connect(channels=[PublicWSChannel.SENTIMENT])
        sent_count = await self.manager.broadcast_new_feedback(
            feedback_id="fb-002",
            sentiment_level="positive",
            sentiment_score=0.8,
        )
        assert sent_count >= 1
        await self.manager.disconnect(conn.connection_id)

    def test_get_connection(self):
        pass

    def test_get_channel_subscribers(self):
        subscribers = self.manager.get_channel_subscribers(PublicWSChannel.ENGAGEMENT)
        assert isinstance(subscribers, list)

    def test_get_message_history(self):
        history = self.manager.get_message_history(limit=10)
        assert isinstance(history, list)

    def test_get_message_history_by_channel(self):
        history = self.manager.get_message_history(
            channel=PublicWSChannel.ENGAGEMENT, limit=10
        )
        assert isinstance(history, list)

    def test_get_statistics(self):
        stats = self.manager.get_statistics()
        assert "total_connections" in stats
        assert "active_connections" in stats
        assert "messages_sent" in stats


class TestPublicWSChannel:
    def test_all_channels_exist(self):
        expected = ["engagement", "trust", "sentiment"]
        for channel in expected:
            assert hasattr(PublicWSChannel, channel.upper())


class TestEngagementUpdateType:
    def test_all_types_exist(self):
        expected = [
            "new_event", "event_update", "event_cancelled", "event_reminder",
            "new_alert", "alert_update", "alert_deactivated", "community_notice"
        ]
        for ut in expected:
            assert hasattr(EngagementUpdateType, ut.upper())


class TestTrustUpdateType:
    def test_all_types_exist(self):
        expected = [
            "score_update", "neighborhood_update", "fairness_audit",
            "bias_audit", "metric_change", "trend_alert"
        ]
        for ut in expected:
            assert hasattr(TrustUpdateType, ut.upper())


class TestSentimentUpdateType:
    def test_all_types_exist(self):
        expected = [
            "new_feedback", "sentiment_shift", "trend_detected",
            "concern_spike", "praise_spike", "neighborhood_insight"
        ]
        for ut in expected:
            assert hasattr(SentimentUpdateType, ut.upper())


class TestPublicWSMessage:
    def test_message_creation(self):
        message = PublicWSMessage(
            channel=PublicWSChannel.ENGAGEMENT,
            update_type="test",
            title="Test",
            message="Test message",
        )
        assert message.message_id is not None
        assert message.message_hash is not None

    def test_message_to_dict(self):
        message = PublicWSMessage(
            channel=PublicWSChannel.TRUST,
            update_type="score_update",
            title="Score Update",
            message="Trust score changed",
        )
        msg_dict = message.to_dict()
        assert "message_id" in msg_dict
        assert "channel" in msg_dict
        assert "title" in msg_dict

    def test_message_to_json(self):
        message = PublicWSMessage(
            channel=PublicWSChannel.SENTIMENT,
            update_type="new_feedback",
            title="New Feedback",
            message="New feedback received",
        )
        json_str = message.to_json()
        assert isinstance(json_str, str)
        assert "message_id" in json_str
