"""
Phase 20: Autonomous Detective AI (ADA) WebSocket Channels

Provides real-time WebSocket channels for ADA updates including:
- /ws/ada/case-updates - Real-time case investigation updates
- /ws/ada/theory-stream - Live hypothesis and theory generation
- /ws/ada/evidence-links - Evidence graph link discoveries
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
import json
import asyncio


@dataclass
class WebSocketConnection:
    connection_id: str
    user_id: str
    subscribed_channels: Set[str] = field(default_factory=set)
    subscribed_cases: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


class ADAWebSocketManager:
    """Manages WebSocket connections for ADA real-time updates."""

    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._case_subscribers: Dict[str, Set[str]] = {}
        self._channel_subscribers: Dict[str, Set[str]] = {}
        self._message_queue: List[Dict[str, Any]] = []

    async def connect(
        self,
        connection_id: str,
        user_id: str,
        channels: Optional[List[str]] = None,
        cases: Optional[List[str]] = None,
    ) -> WebSocketConnection:
        connection = WebSocketConnection(
            connection_id=connection_id,
            user_id=user_id,
            subscribed_channels=set(channels or []),
            subscribed_cases=set(cases or []),
        )
        self._connections[connection_id] = connection

        for channel in connection.subscribed_channels:
            if channel not in self._channel_subscribers:
                self._channel_subscribers[channel] = set()
            self._channel_subscribers[channel].add(connection_id)

        for case_id in connection.subscribed_cases:
            if case_id not in self._case_subscribers:
                self._case_subscribers[case_id] = set()
            self._case_subscribers[case_id].add(connection_id)

        return connection

    async def disconnect(self, connection_id: str) -> None:
        connection = self._connections.get(connection_id)
        if not connection:
            return

        for channel in connection.subscribed_channels:
            if channel in self._channel_subscribers:
                self._channel_subscribers[channel].discard(connection_id)

        for case_id in connection.subscribed_cases:
            if case_id in self._case_subscribers:
                self._case_subscribers[case_id].discard(connection_id)

        del self._connections[connection_id]

    async def subscribe_channel(
        self,
        connection_id: str,
        channel: str,
    ) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.subscribed_channels.add(channel)

        if channel not in self._channel_subscribers:
            self._channel_subscribers[channel] = set()
        self._channel_subscribers[channel].add(connection_id)

        return True

    async def unsubscribe_channel(
        self,
        connection_id: str,
        channel: str,
    ) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.subscribed_channels.discard(channel)

        if channel in self._channel_subscribers:
            self._channel_subscribers[channel].discard(connection_id)

        return True

    async def subscribe_case(
        self,
        connection_id: str,
        case_id: str,
    ) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.subscribed_cases.add(case_id)

        if case_id not in self._case_subscribers:
            self._case_subscribers[case_id] = set()
        self._case_subscribers[case_id].add(connection_id)

        return True

    async def unsubscribe_case(
        self,
        connection_id: str,
        case_id: str,
    ) -> bool:
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.subscribed_cases.discard(case_id)

        if case_id in self._case_subscribers:
            self._case_subscribers[case_id].discard(connection_id)

        return True

    def get_channel_subscribers(self, channel: str) -> Set[str]:
        return self._channel_subscribers.get(channel, set())

    def get_case_subscribers(self, case_id: str) -> Set[str]:
        return self._case_subscribers.get(case_id, set())

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        return self._connections.get(connection_id)

    def get_active_connections(self) -> int:
        return len(self._connections)


ada_ws_manager = ADAWebSocketManager()


class CaseUpdatesChannel:
    """
    WebSocket channel: /ws/ada/case-updates
    
    Broadcasts real-time case investigation updates including:
    - Investigation status changes
    - New evidence discoveries
    - Suspect identification updates
    - Case priority changes
    - Triage notifications
    """

    CHANNEL_NAME = "case-updates"

    def __init__(self, manager: ADAWebSocketManager):
        self._manager = manager

    async def broadcast_investigation_started(
        self,
        case_id: str,
        result_id: str,
        initiated_by: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "investigation_started",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "result_id": result_id,
                "initiated_by": initiated_by,
                "status": "initializing",
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_investigation_progress(
        self,
        case_id: str,
        result_id: str,
        status: str,
        progress_percent: float,
        current_stage: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "investigation_progress",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "result_id": result_id,
                "status": status,
                "progress_percent": progress_percent,
                "current_stage": current_stage,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_investigation_completed(
        self,
        case_id: str,
        result_id: str,
        confidence_score: float,
        suspects_found: int,
        theories_generated: int,
        linked_cases: int,
    ) -> Dict[str, Any]:
        message = {
            "type": "investigation_completed",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "result_id": result_id,
                "confidence_score": confidence_score,
                "suspects_found": suspects_found,
                "theories_generated": theories_generated,
                "linked_cases": linked_cases,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_new_evidence(
        self,
        case_id: str,
        evidence_id: str,
        evidence_type: str,
        description: str,
        significance: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "new_evidence",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "evidence_id": evidence_id,
                "evidence_type": evidence_type,
                "description": description,
                "significance": significance,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_suspect_update(
        self,
        case_id: str,
        suspect_id: str,
        suspect_name: str,
        update_type: str,
        evidence_strength: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "suspect_update",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "suspect_id": suspect_id,
                "suspect_name": suspect_name,
                "update_type": update_type,
                "evidence_strength": evidence_strength,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_triage_alert(
        self,
        case_id: str,
        triage_id: str,
        priority: str,
        reasons: List[str],
        recommended_actions: List[str],
    ) -> Dict[str, Any]:
        message = {
            "type": "triage_alert",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "triage_id": triage_id,
                "priority": priority,
                "reasons": reasons,
                "recommended_actions": recommended_actions,
            },
        }
        await self._broadcast_to_channel(message)
        await self._broadcast_to_case(case_id, message)
        return message

    async def _broadcast_to_case(
        self,
        case_id: str,
        message: Dict[str, Any],
    ) -> None:
        subscribers = self._manager.get_case_subscribers(case_id)
        pass

    async def _broadcast_to_channel(
        self,
        message: Dict[str, Any],
    ) -> None:
        subscribers = self._manager.get_channel_subscribers(self.CHANNEL_NAME)
        pass


class TheoryStreamChannel:
    """
    WebSocket channel: /ws/ada/theory-stream
    
    Streams real-time hypothesis and theory generation including:
    - New hypothesis creation
    - Hypothesis status updates
    - Contradiction discoveries
    - Theory ranking changes
    - Narrative generation progress
    """

    CHANNEL_NAME = "theory-stream"

    def __init__(self, manager: ADAWebSocketManager):
        self._manager = manager

    async def broadcast_hypothesis_generated(
        self,
        case_id: str,
        hypothesis_id: str,
        title: str,
        hypothesis_type: str,
        confidence_score: float,
    ) -> Dict[str, Any]:
        message = {
            "type": "hypothesis_generated",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "hypothesis_id": hypothesis_id,
                "title": title,
                "hypothesis_type": hypothesis_type,
                "confidence_score": confidence_score,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_hypothesis_status_change(
        self,
        case_id: str,
        hypothesis_id: str,
        old_status: str,
        new_status: str,
        reason: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "hypothesis_status_change",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "hypothesis_id": hypothesis_id,
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_contradiction_found(
        self,
        case_id: str,
        hypothesis_id: str,
        contradiction_id: str,
        contradiction_type: str,
        severity: str,
        description: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "contradiction_found",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "hypothesis_id": hypothesis_id,
                "contradiction_id": contradiction_id,
                "contradiction_type": contradiction_type,
                "severity": severity,
                "description": description,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_theory_ranking_update(
        self,
        case_id: str,
        ranked_theories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        message = {
            "type": "theory_ranking_update",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "ranked_theories": ranked_theories,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_narrative_progress(
        self,
        case_id: str,
        narrative_id: str,
        current_section: str,
        progress_percent: float,
        word_count: int,
    ) -> Dict[str, Any]:
        message = {
            "type": "narrative_progress",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "narrative_id": narrative_id,
                "current_section": current_section,
                "progress_percent": progress_percent,
                "word_count": word_count,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_narrative_completed(
        self,
        case_id: str,
        narrative_id: str,
        title: str,
        word_count: int,
        sections_count: int,
    ) -> Dict[str, Any]:
        message = {
            "type": "narrative_completed",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "narrative_id": narrative_id,
                "title": title,
                "word_count": word_count,
                "sections_count": sections_count,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def _broadcast_to_case(
        self,
        case_id: str,
        message: Dict[str, Any],
    ) -> None:
        subscribers = self._manager.get_case_subscribers(case_id)
        pass


class EvidenceLinksChannel:
    """
    WebSocket channel: /ws/ada/evidence-links
    
    Broadcasts evidence graph link discoveries including:
    - New case links discovered
    - Similarity score updates
    - Entity connections found
    - Cluster formations
    - Cross-case pattern matches
    """

    CHANNEL_NAME = "evidence-links"

    def __init__(self, manager: ADAWebSocketManager):
        self._manager = manager

    async def broadcast_case_link_discovered(
        self,
        link_id: str,
        case_id_1: str,
        case_id_2: str,
        link_type: str,
        strength: float,
        common_elements: List[str],
    ) -> Dict[str, Any]:
        message = {
            "type": "case_link_discovered",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "link_id": link_id,
                "case_id_1": case_id_1,
                "case_id_2": case_id_2,
                "link_type": link_type,
                "strength": strength,
                "common_elements": common_elements,
            },
        }
        await self._broadcast_to_case(case_id_1, message)
        await self._broadcast_to_case(case_id_2, message)
        await self._broadcast_to_channel(message)
        return message

    async def broadcast_similarity_update(
        self,
        case_id_1: str,
        case_id_2: str,
        overall_similarity: float,
        behavioral_similarity: float,
        mo_similarity: float,
    ) -> Dict[str, Any]:
        message = {
            "type": "similarity_update",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id_1": case_id_1,
                "case_id_2": case_id_2,
                "overall_similarity": overall_similarity,
                "behavioral_similarity": behavioral_similarity,
                "mo_similarity": mo_similarity,
            },
        }
        await self._broadcast_to_case(case_id_1, message)
        await self._broadcast_to_case(case_id_2, message)
        return message

    async def broadcast_entity_connection(
        self,
        case_id: str,
        entity_type: str,
        entity_label: str,
        connected_cases: List[str],
        connection_strength: float,
    ) -> Dict[str, Any]:
        message = {
            "type": "entity_connection",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "entity_type": entity_type,
                "entity_label": entity_label,
                "connected_cases": connected_cases,
                "connection_strength": connection_strength,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_cluster_formed(
        self,
        cluster_id: str,
        case_ids: List[str],
        cluster_type: str,
        common_patterns: List[str],
    ) -> Dict[str, Any]:
        message = {
            "type": "cluster_formed",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "cluster_id": cluster_id,
                "case_ids": case_ids,
                "cluster_type": cluster_type,
                "common_patterns": common_patterns,
            },
        }
        for case_id in case_ids:
            await self._broadcast_to_case(case_id, message)
        await self._broadcast_to_channel(message)
        return message

    async def broadcast_pattern_match(
        self,
        pattern_type: str,
        pattern_description: str,
        matching_cases: List[str],
        confidence: float,
    ) -> Dict[str, Any]:
        message = {
            "type": "pattern_match",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "pattern_type": pattern_type,
                "pattern_description": pattern_description,
                "matching_cases": matching_cases,
                "confidence": confidence,
            },
        }
        for case_id in matching_cases:
            await self._broadcast_to_case(case_id, message)
        await self._broadcast_to_channel(message)
        return message

    async def broadcast_graph_node_added(
        self,
        case_id: str,
        node_id: str,
        node_type: str,
        label: str,
    ) -> Dict[str, Any]:
        message = {
            "type": "graph_node_added",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "node_id": node_id,
                "node_type": node_type,
                "label": label,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def broadcast_graph_edge_added(
        self,
        case_id: str,
        edge_id: str,
        edge_type: str,
        source_label: str,
        target_label: str,
        weight: float,
    ) -> Dict[str, Any]:
        message = {
            "type": "graph_edge_added",
            "channel": self.CHANNEL_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "case_id": case_id,
                "edge_id": edge_id,
                "edge_type": edge_type,
                "source_label": source_label,
                "target_label": target_label,
                "weight": weight,
            },
        }
        await self._broadcast_to_case(case_id, message)
        return message

    async def _broadcast_to_case(
        self,
        case_id: str,
        message: Dict[str, Any],
    ) -> None:
        subscribers = self._manager.get_case_subscribers(case_id)
        pass

    async def _broadcast_to_channel(
        self,
        message: Dict[str, Any],
    ) -> None:
        subscribers = self._manager.get_channel_subscribers(self.CHANNEL_NAME)
        pass


case_updates_channel = CaseUpdatesChannel(ada_ws_manager)
theory_stream_channel = TheoryStreamChannel(ada_ws_manager)
evidence_links_channel = EvidenceLinksChannel(ada_ws_manager)


__all__ = [
    "ADAWebSocketManager",
    "ada_ws_manager",
    "CaseUpdatesChannel",
    "case_updates_channel",
    "TheoryStreamChannel",
    "theory_stream_channel",
    "EvidenceLinksChannel",
    "evidence_links_channel",
]
