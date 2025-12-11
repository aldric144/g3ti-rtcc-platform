"""
Phase 29: Cyber Intelligence WebSocket Channels

Provides real-time WebSocket channels for cyber threat detection:
- /ws/cyber-intel/threats - Live intrusions, network threats
- /ws/cyber-intel/quantum - Quantum anomalies, crypto attacks
- /ws/cyber-intel/disinfo - Disinformation waves, impersonation alerts
- /ws/cyber-intel/alerts - All critical alerts

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
import asyncio
import json

router = APIRouter()


class CyberIntelConnectionManager:
    """Manages WebSocket connections for cyber intelligence channels"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "threats": [],
            "quantum": [],
            "disinfo": [],
            "alerts": [],
        }
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str, user_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
            self.connection_metadata[websocket] = {
                "channel": channel,
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
            }
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
    
    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all connections on a channel"""
        if channel in self.active_connections:
            disconnected = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, channel)
    
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    def get_connection_count(self, channel: str) -> int:
        """Get number of active connections on a channel"""
        return len(self.active_connections.get(channel, []))


manager = CyberIntelConnectionManager()


def _get_cyber_threat_engine():
    """Get CyberThreatEngine instance"""
    from ..cyber_intel.cyber_threat_engine import CyberThreatEngine
    return CyberThreatEngine()


def _get_quantum_detection_engine():
    """Get QuantumDetectionEngine instance"""
    from ..cyber_intel.quantum_detection_engine import QuantumDetectionEngine
    return QuantumDetectionEngine()


def _get_info_warfare_engine():
    """Get InfoWarfareEngine instance"""
    from ..cyber_intel.info_warfare_engine import InfoWarfareEngine
    return InfoWarfareEngine()


@router.websocket("/ws/cyber-intel/threats")
async def websocket_threats(websocket: WebSocket):
    """
    WebSocket channel for live network threats and intrusions
    
    Emits:
    - Live intrusion alerts
    - Network threat detections
    - Ransomware triggers
    - Endpoint compromise alerts
    """
    await manager.connect(websocket, "threats")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "threats",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to cyber threat channel",
        })
        
        engine = _get_cyber_threat_engine()
        last_threat_count = len(engine.network_threats)
        last_ransomware_count = len(engine.ransomware_alerts)
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=5.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
                elif data.get("type") == "subscribe_filter":
                    metadata = manager.connection_metadata.get(websocket, {})
                    metadata["filter"] = data.get("filter", {})
                    manager.connection_metadata[websocket] = metadata
                    
                    await manager.send_personal(websocket, {
                        "type": "filter_applied",
                        "filter": data.get("filter", {}),
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
            except asyncio.TimeoutError:
                current_threat_count = len(engine.network_threats)
                current_ransomware_count = len(engine.ransomware_alerts)
                
                if current_threat_count > last_threat_count:
                    new_threats = engine.network_threats[last_threat_count:]
                    for threat in new_threats:
                        await manager.broadcast("threats", {
                            "type": "network_threat",
                            "threat_id": threat.threat_id,
                            "threat_type": threat.threat_type.value,
                            "severity": threat.severity.name,
                            "source_ip": threat.source_ip,
                            "destination_ip": threat.destination_ip,
                            "detection_method": threat.detection_method.value,
                            "signature_name": threat.signature_name,
                            "recommended_action": threat.recommended_action,
                            "timestamp": threat.timestamp.isoformat(),
                            "chain_of_custody_hash": threat.chain_of_custody_hash,
                        })
                    last_threat_count = current_threat_count
                
                if current_ransomware_count > last_ransomware_count:
                    new_alerts = engine.ransomware_alerts[last_ransomware_count:]
                    for alert in new_alerts:
                        await manager.broadcast("threats", {
                            "type": "ransomware_alert",
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.name,
                            "affected_host": alert.affected_host,
                            "ransomware_family": alert.ransomware_family,
                            "encryption_detected": alert.encryption_detected,
                            "files_affected": alert.files_affected,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                    last_ransomware_count = current_ransomware_count
                
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_threats": current_threat_count,
                    "ransomware_alerts": current_ransomware_count,
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "threats")
    except Exception as e:
        manager.disconnect(websocket, "threats")


@router.websocket("/ws/cyber-intel/quantum")
async def websocket_quantum(websocket: WebSocket):
    """
    WebSocket channel for quantum anomalies and crypto attacks
    
    Emits:
    - Quantum anomaly detections
    - Crypto attack alerts
    - Deepfake alerts
    - Post-quantum readiness updates
    """
    await manager.connect(websocket, "quantum")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "quantum",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to quantum threat channel",
        })
        
        engine = _get_quantum_detection_engine()
        last_anomaly_count = len(engine.quantum_anomalies)
        last_crypto_count = len(engine.crypto_attacks)
        last_deepfake_count = len(engine.deepfake_alerts)
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=5.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
            except asyncio.TimeoutError:
                current_anomaly_count = len(engine.quantum_anomalies)
                current_crypto_count = len(engine.crypto_attacks)
                current_deepfake_count = len(engine.deepfake_alerts)
                
                if current_anomaly_count > last_anomaly_count:
                    new_anomalies = engine.quantum_anomalies[last_anomaly_count:]
                    for anomaly in new_anomalies:
                        await manager.broadcast("quantum", {
                            "type": "quantum_anomaly",
                            "anomaly_id": anomaly.anomaly_id,
                            "threat_type": anomaly.threat_type.value,
                            "severity": anomaly.severity.name,
                            "source_identifier": anomaly.source_identifier,
                            "qubit_pattern": anomaly.qubit_pattern,
                            "anomaly_description": anomaly.anomaly_description,
                            "recommended_action": anomaly.recommended_action,
                            "timestamp": anomaly.timestamp.isoformat(),
                            "chain_of_custody_hash": anomaly.chain_of_custody_hash,
                        })
                    last_anomaly_count = current_anomaly_count
                
                if current_crypto_count > last_crypto_count:
                    new_attacks = engine.crypto_attacks[last_crypto_count:]
                    for attack in new_attacks:
                        await manager.broadcast("quantum", {
                            "type": "crypto_attack",
                            "attack_id": attack.attack_id,
                            "attack_type": attack.attack_type.value,
                            "severity": attack.severity.name,
                            "target_algorithm": attack.target_algorithm,
                            "target_key_size": attack.target_key_size,
                            "post_quantum_ready": attack.post_quantum_ready,
                            "estimated_decrypt_timeline": attack.estimated_decrypt_timeline,
                            "recommended_action": attack.recommended_action,
                            "timestamp": attack.timestamp.isoformat(),
                            "chain_of_custody_hash": attack.chain_of_custody_hash,
                        })
                    last_crypto_count = current_crypto_count
                
                if current_deepfake_count > last_deepfake_count:
                    new_deepfakes = engine.deepfake_alerts[last_deepfake_count:]
                    for alert in new_deepfakes:
                        await manager.broadcast("quantum", {
                            "type": "deepfake_alert",
                            "alert_id": alert.alert_id,
                            "deepfake_type": alert.deepfake_type.value,
                            "severity": alert.severity.name,
                            "confidence_score": alert.confidence_score,
                            "officer_involved": alert.officer_involved,
                            "evidence_integrity_compromised": alert.evidence_integrity_compromised,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                    last_deepfake_count = current_deepfake_count
                
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "quantum_anomalies": current_anomaly_count,
                    "crypto_attacks": current_crypto_count,
                    "deepfake_alerts": current_deepfake_count,
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "quantum")
    except Exception as e:
        manager.disconnect(websocket, "quantum")


@router.websocket("/ws/cyber-intel/disinfo")
async def websocket_disinfo(websocket: WebSocket):
    """
    WebSocket channel for disinformation and information warfare
    
    Emits:
    - Disinformation wave alerts
    - Police impersonation detections
    - Election interference alerts
    - Crisis manipulation detections
    """
    await manager.connect(websocket, "disinfo")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "disinfo",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to disinformation channel",
        })
        
        engine = _get_info_warfare_engine()
        last_rumor_count = len(engine.rumor_alerts)
        last_impersonation_count = len(engine.impersonation_alerts)
        last_election_count = len(engine.election_threats)
        last_crisis_count = len(engine.crisis_manipulations)
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=5.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
            except asyncio.TimeoutError:
                current_rumor_count = len(engine.rumor_alerts)
                current_impersonation_count = len(engine.impersonation_alerts)
                current_election_count = len(engine.election_threats)
                current_crisis_count = len(engine.crisis_manipulations)
                
                if current_rumor_count > last_rumor_count:
                    new_rumors = engine.rumor_alerts[last_rumor_count:]
                    for alert in new_rumors:
                        await manager.broadcast("disinfo", {
                            "type": "rumor_alert",
                            "alert_id": alert.alert_id,
                            "disinfo_type": alert.disinfo_type.value,
                            "severity": alert.severity.name,
                            "source_platform": alert.source_platform.value,
                            "viral_velocity": alert.viral_velocity,
                            "share_count": alert.share_count,
                            "reach_estimate": alert.reach_estimate,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                    last_rumor_count = current_rumor_count
                
                if current_impersonation_count > last_impersonation_count:
                    new_impersonations = engine.impersonation_alerts[last_impersonation_count:]
                    for alert in new_impersonations:
                        await manager.broadcast("disinfo", {
                            "type": "impersonation_alert",
                            "alert_id": alert.alert_id,
                            "disinfo_type": alert.disinfo_type.value,
                            "severity": alert.severity.name,
                            "source_platform": alert.source_platform.value,
                            "fake_page_name": alert.fake_page_name,
                            "ai_generated_content": alert.ai_generated_content,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                    last_impersonation_count = current_impersonation_count
                
                if current_election_count > last_election_count:
                    new_election = engine.election_threats[last_election_count:]
                    for threat in new_election:
                        await manager.broadcast("disinfo", {
                            "type": "election_threat",
                            "threat_id": threat.threat_id,
                            "disinfo_type": threat.disinfo_type.value,
                            "severity": threat.severity.name,
                            "campaign_type": threat.campaign_type.value,
                            "bot_network_detected": threat.bot_network_detected,
                            "bot_account_count": threat.bot_account_count,
                            "reach_estimate": threat.reach_estimate,
                            "recommended_action": threat.recommended_action,
                            "timestamp": threat.timestamp.isoformat(),
                            "chain_of_custody_hash": threat.chain_of_custody_hash,
                        })
                    last_election_count = current_election_count
                
                if current_crisis_count > last_crisis_count:
                    new_crisis = engine.crisis_manipulations[last_crisis_count:]
                    for manipulation in new_crisis:
                        await manager.broadcast("disinfo", {
                            "type": "crisis_manipulation",
                            "manipulation_id": manipulation.manipulation_id,
                            "disinfo_type": manipulation.disinfo_type.value,
                            "severity": manipulation.severity.name,
                            "crisis_type": manipulation.crisis_type,
                            "community_tension_score": manipulation.community_tension_score,
                            "public_safety_impact": manipulation.public_safety_impact,
                            "recommended_action": manipulation.recommended_action,
                            "timestamp": manipulation.timestamp.isoformat(),
                            "chain_of_custody_hash": manipulation.chain_of_custody_hash,
                        })
                    last_crisis_count = current_crisis_count
                
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "rumor_alerts": current_rumor_count,
                    "impersonation_alerts": current_impersonation_count,
                    "election_threats": current_election_count,
                    "crisis_manipulations": current_crisis_count,
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "disinfo")
    except Exception as e:
        manager.disconnect(websocket, "disinfo")


@router.websocket("/ws/cyber-intel/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket channel for all critical cyber intel alerts
    
    Emits:
    - All critical and high severity alerts from all engines
    - Consolidated alert feed
    """
    await manager.connect(websocket, "alerts")
    
    try:
        await manager.send_personal(websocket, {
            "type": "connection_established",
            "channel": "alerts",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to consolidated alerts channel",
        })
        
        cyber_engine = _get_cyber_threat_engine()
        quantum_engine = _get_quantum_detection_engine()
        info_engine = _get_info_warfare_engine()
        
        last_counts = {
            "network_threats": len(cyber_engine.network_threats),
            "ransomware": len(cyber_engine.ransomware_alerts),
            "quantum": len(quantum_engine.quantum_anomalies),
            "crypto": len(quantum_engine.crypto_attacks),
            "deepfake": len(quantum_engine.deepfake_alerts),
            "rumor": len(info_engine.rumor_alerts),
            "impersonation": len(info_engine.impersonation_alerts),
        }
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=5.0
                )
                
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
            except asyncio.TimeoutError:
                current_counts = {
                    "network_threats": len(cyber_engine.network_threats),
                    "ransomware": len(cyber_engine.ransomware_alerts),
                    "quantum": len(quantum_engine.quantum_anomalies),
                    "crypto": len(quantum_engine.crypto_attacks),
                    "deepfake": len(quantum_engine.deepfake_alerts),
                    "rumor": len(info_engine.rumor_alerts),
                    "impersonation": len(info_engine.impersonation_alerts),
                }
                
                for threat in cyber_engine.network_threats[last_counts["network_threats"]:]:
                    if threat.severity.name in ["CRITICAL", "HIGH"]:
                        await manager.broadcast("alerts", {
                            "type": "alert",
                            "category": "NETWORK_THREAT",
                            "alert_id": threat.threat_id,
                            "severity": threat.severity.name,
                            "description": f"{threat.threat_type.value}: {threat.signature_name or 'Detected'}",
                            "source": threat.source_ip,
                            "recommended_action": threat.recommended_action,
                            "timestamp": threat.timestamp.isoformat(),
                            "chain_of_custody_hash": threat.chain_of_custody_hash,
                        })
                
                for alert in cyber_engine.ransomware_alerts[last_counts["ransomware"]:]:
                    if alert.severity.name in ["CRITICAL", "HIGH"]:
                        await manager.broadcast("alerts", {
                            "type": "alert",
                            "category": "RANSOMWARE",
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.name,
                            "description": f"Ransomware: {alert.ransomware_family or 'Unknown'}",
                            "source": alert.affected_host,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                
                for alert in quantum_engine.deepfake_alerts[last_counts["deepfake"]:]:
                    if alert.severity.name in ["CRITICAL", "HIGH"]:
                        await manager.broadcast("alerts", {
                            "type": "alert",
                            "category": "DEEPFAKE",
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.name,
                            "description": f"Deepfake: {alert.deepfake_type.value}",
                            "officer_involved": alert.officer_involved,
                            "evidence_compromised": alert.evidence_integrity_compromised,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                
                for alert in info_engine.impersonation_alerts[last_counts["impersonation"]:]:
                    if alert.severity.name in ["CRITICAL", "HIGH"]:
                        await manager.broadcast("alerts", {
                            "type": "alert",
                            "category": "IMPERSONATION",
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.name,
                            "description": f"Police impersonation: {alert.fake_page_name}",
                            "source": alert.source_platform.value,
                            "recommended_action": alert.recommended_action,
                            "timestamp": alert.timestamp.isoformat(),
                            "chain_of_custody_hash": alert.chain_of_custody_hash,
                        })
                
                last_counts = current_counts
                
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_alerts": sum(current_counts.values()),
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
    except Exception as e:
        manager.disconnect(websocket, "alerts")


async def broadcast_cyber_threat(threat_data: Dict[str, Any]):
    """Broadcast a cyber threat to all relevant channels"""
    await manager.broadcast("threats", threat_data)
    if threat_data.get("severity") in ["CRITICAL", "HIGH"]:
        await manager.broadcast("alerts", {
            "type": "alert",
            "category": "CYBER_THREAT",
            **threat_data,
        })


async def broadcast_quantum_alert(alert_data: Dict[str, Any]):
    """Broadcast a quantum alert to all relevant channels"""
    await manager.broadcast("quantum", alert_data)
    if alert_data.get("severity") in ["CRITICAL", "HIGH", "CATASTROPHIC"]:
        await manager.broadcast("alerts", {
            "type": "alert",
            "category": "QUANTUM",
            **alert_data,
        })


async def broadcast_disinfo_alert(alert_data: Dict[str, Any]):
    """Broadcast a disinformation alert to all relevant channels"""
    await manager.broadcast("disinfo", alert_data)
    if alert_data.get("severity") in ["CRITICAL", "HIGH", "EMERGENCY"]:
        await manager.broadcast("alerts", {
            "type": "alert",
            "category": "DISINFORMATION",
            **alert_data,
        })
