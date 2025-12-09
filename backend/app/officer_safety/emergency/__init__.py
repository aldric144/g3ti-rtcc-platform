"""
Officer Emergency Detection Module

Detects officer down and SOS conditions through various triggers
including sudden deceleration, manual flags, and radio silence.
"""

from datetime import datetime, timedelta
from typing import Any

from app.core.logging import get_logger
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Emergency detection thresholds
THRESHOLDS = {
    "sudden_deceleration_mph": 30,  # Speed drop threshold
    "gps_halt_seconds": 10,  # Time stationary after deceleration
    "radio_silence_minutes": 5,  # Minutes without communication during emergency
    "heart_rate_spike_bpm": 150,  # Future wearable integration
}

# Redis keys
EMERGENCY_PREFIX = "officer:emergency:"
LAST_COMMUNICATION_PREFIX = "officer:last_comm:"
VELOCITY_HISTORY_PREFIX = "officer:velocity:"


class EmergencyDetector:
    """
    Detects officer emergency conditions.

    Triggers:
    - Sudden deceleration + GPS halt
    - Manual "SOS" flag from MDT stream
    - Prolonged radio silence during emergency CAD call
    - Rapid heart-rate spike (future wearable integration placeholder)

    WebSocket broadcasts:
    - officer_down
    - officer_sos
    """

    def __init__(
        self,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the emergency detector.

        Args:
            redis: Redis manager for state tracking
        """
        self.redis = redis

        # Track velocity history for deceleration detection
        self._velocity_history: dict[str, list[dict]] = {}

        # Track active emergencies
        self._active_emergencies: dict[str, dict] = {}

        logger.info("emergency_detector_initialized")

    async def check_conditions(
        self,
        badge: str,
        lat: float,
        lon: float,
        speed: float | None = None,
        status: str | None = None,
        heart_rate: int | None = None,
    ) -> dict[str, Any]:
        """
        Check for emergency conditions.

        Args:
            badge: Officer badge number
            lat: Current latitude
            lon: Current longitude
            speed: Current speed in mph
            status: Current status
            heart_rate: Heart rate (future wearable)

        Returns:
            Emergency check result
        """
        logger.debug(
            "checking_emergency_conditions",
            badge=badge,
            speed=speed,
            status=status,
        )

        result = {
            "badge": badge,
            "emergency": False,
            "type": None,
            "message": None,
            "checked_at": datetime.utcnow().isoformat(),
        }

        # Check for sudden deceleration
        if speed is not None:
            decel_check = await self._check_sudden_deceleration(badge, speed, lat, lon)
            if decel_check.get("detected"):
                result["emergency"] = True
                result["type"] = "officer_down"
                result["message"] = decel_check.get("message")
                result["details"] = decel_check

                # Trigger emergency
                await self._trigger_emergency(badge, "officer_down", "auto_deceleration", decel_check)
                return result

        # Check for radio silence during emergency call
        if status and "emergency" in status.lower():
            silence_check = await self._check_radio_silence(badge)
            if silence_check.get("detected"):
                result["emergency"] = True
                result["type"] = "officer_down"
                result["message"] = silence_check.get("message")
                result["details"] = silence_check

                await self._trigger_emergency(badge, "officer_down", "radio_silence", silence_check)
                return result

        # Check heart rate (future wearable integration)
        if heart_rate is not None:
            hr_check = self._check_heart_rate(badge, heart_rate)
            if hr_check.get("detected"):
                result["emergency"] = True
                result["type"] = "officer_sos"
                result["message"] = hr_check.get("message")
                result["details"] = hr_check

                await self._trigger_emergency(badge, "officer_sos", "heart_rate", hr_check)
                return result

        return result

    async def _check_sudden_deceleration(
        self,
        badge: str,
        current_speed: float,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for sudden deceleration pattern."""
        timestamp = datetime.utcnow()

        # Initialize velocity history if needed
        if badge not in self._velocity_history:
            self._velocity_history[badge] = []

        history = self._velocity_history[badge]

        # Add current reading
        history.append({
            "speed": current_speed,
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp,
        })

        # Keep only last 30 seconds of data
        cutoff = timestamp - timedelta(seconds=30)
        history[:] = [h for h in history if h["timestamp"] > cutoff]

        # Need at least 2 readings
        if len(history) < 2:
            return {"detected": False}

        # Check for sudden deceleration
        recent = history[-5:] if len(history) >= 5 else history
        max_speed = max(h["speed"] for h in recent[:-1]) if len(recent) > 1 else 0

        speed_drop = max_speed - current_speed

        if speed_drop >= THRESHOLDS["sudden_deceleration_mph"] and current_speed < 5:
            # Check if GPS has halted (stationary)
            if len(history) >= 3:
                last_positions = history[-3:]
                lat_variance = max(p["lat"] for p in last_positions) - min(p["lat"] for p in last_positions)
                lon_variance = max(p["lon"] for p in last_positions) - min(p["lon"] for p in last_positions)

                # If position hasn't changed significantly
                if lat_variance < 0.0001 and lon_variance < 0.0001:
                    logger.critical(
                        "sudden_deceleration_detected",
                        badge=badge,
                        speed_drop=speed_drop,
                        current_speed=current_speed,
                    )

                    return {
                        "detected": True,
                        "message": f"OFFICER DOWN: Sudden deceleration detected ({int(speed_drop)} mph drop, now stationary)",
                        "speed_drop": speed_drop,
                        "max_speed": max_speed,
                        "current_speed": current_speed,
                        "location": {"lat": lat, "lon": lon},
                    }

        return {"detected": False}

    async def _check_radio_silence(
        self,
        badge: str,
    ) -> dict[str, Any]:
        """Check for prolonged radio silence during emergency."""
        try:
            # Get last communication time
            last_comm = None

            if self.redis:
                key = f"{LAST_COMMUNICATION_PREFIX}{badge}"
                last_comm_str = await self.redis.get(key)
                if last_comm_str:
                    last_comm = datetime.fromisoformat(last_comm_str)

            if last_comm:
                silence_duration = datetime.utcnow() - last_comm
                silence_minutes = silence_duration.total_seconds() / 60

                if silence_minutes >= THRESHOLDS["radio_silence_minutes"]:
                    logger.critical(
                        "radio_silence_detected",
                        badge=badge,
                        silence_minutes=silence_minutes,
                    )

                    return {
                        "detected": True,
                        "message": f"OFFICER DOWN: Radio silence for {int(silence_minutes)} minutes during emergency call",
                        "silence_minutes": silence_minutes,
                        "last_communication": last_comm.isoformat(),
                    }

            return {"detected": False}

        except Exception as e:
            logger.error("radio_silence_check_error", badge=badge, error=str(e))
            return {"detected": False}

    def _check_heart_rate(
        self,
        badge: str,
        heart_rate: int,
    ) -> dict[str, Any]:
        """Check for abnormal heart rate (future wearable integration)."""
        if heart_rate >= THRESHOLDS["heart_rate_spike_bpm"]:
            logger.warning(
                "heart_rate_spike_detected",
                badge=badge,
                heart_rate=heart_rate,
            )

            return {
                "detected": True,
                "message": f"ALERT: Elevated heart rate detected ({heart_rate} BPM)",
                "heart_rate": heart_rate,
                "threshold": THRESHOLDS["heart_rate_spike_bpm"],
            }

        return {"detected": False}

    async def _trigger_emergency(
        self,
        badge: str,
        emergency_type: str,
        source: str,
        details: dict,
    ) -> None:
        """Trigger an emergency alert."""
        emergency = {
            "badge": badge,
            "type": emergency_type,
            "source": source,
            "details": details,
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        self._active_emergencies[badge] = emergency

        # Store in Redis
        if self.redis:
            key = f"{EMERGENCY_PREFIX}{badge}"
            import json
            await self.redis.set(key, json.dumps(emergency))

        logger.critical(
            "emergency_triggered",
            badge=badge,
            type=emergency_type,
            source=source,
        )

    async def trigger_officer_down(
        self,
        badge: str,
        source: str = "manual",
        details: dict | None = None,
    ) -> dict[str, Any]:
        """
        Manually trigger officer down alert.

        Args:
            badge: Officer badge number
            source: Source of trigger (manual, mdt, radio)
            details: Additional details

        Returns:
            Alert confirmation
        """
        logger.critical(
            "officer_down_triggered",
            badge=badge,
            source=source,
        )

        emergency = {
            "badge": badge,
            "type": "officer_down",
            "source": source,
            "details": details or {},
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        self._active_emergencies[badge] = emergency

        # Store in Redis
        if self.redis:
            key = f"{EMERGENCY_PREFIX}{badge}"
            import json
            await self.redis.set(key, json.dumps(emergency))

        return {
            "success": True,
            "alert_type": "officer_down",
            "badge": badge,
            "message": f"OFFICER DOWN alert triggered for badge {badge}",
            "timestamp": emergency["triggered_at"],
        }

    async def trigger_sos(
        self,
        badge: str,
        source: str = "manual",
        details: dict | None = None,
    ) -> dict[str, Any]:
        """
        Trigger SOS alert.

        Args:
            badge: Officer badge number
            source: Source of trigger (manual, mdt, radio)
            details: Additional details

        Returns:
            Alert confirmation
        """
        logger.critical(
            "sos_triggered",
            badge=badge,
            source=source,
        )

        emergency = {
            "badge": badge,
            "type": "officer_sos",
            "source": source,
            "details": details or {},
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        self._active_emergencies[badge] = emergency

        # Store in Redis
        if self.redis:
            key = f"{EMERGENCY_PREFIX}{badge}"
            import json
            await self.redis.set(key, json.dumps(emergency))

        return {
            "success": True,
            "alert_type": "officer_sos",
            "badge": badge,
            "message": f"SOS alert triggered for badge {badge}",
            "timestamp": emergency["triggered_at"],
        }

    async def clear_emergency(
        self,
        badge: str,
        cleared_by: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Clear an active emergency.

        Args:
            badge: Officer badge number
            cleared_by: Who cleared the emergency
            reason: Reason for clearing

        Returns:
            Confirmation
        """
        if badge not in self._active_emergencies:
            return {
                "success": False,
                "message": f"No active emergency for badge {badge}",
            }

        emergency = self._active_emergencies.pop(badge)
        emergency["status"] = "cleared"
        emergency["cleared_at"] = datetime.utcnow().isoformat()
        emergency["cleared_by"] = cleared_by
        emergency["clear_reason"] = reason

        # Update in Redis
        if self.redis:
            key = f"{EMERGENCY_PREFIX}{badge}"
            await self.redis.delete(key)

        logger.info(
            "emergency_cleared",
            badge=badge,
            cleared_by=cleared_by,
            reason=reason,
        )

        return {
            "success": True,
            "message": f"Emergency cleared for badge {badge}",
            "emergency": emergency,
        }

    async def get_active_emergencies(self) -> list[dict[str, Any]]:
        """Get all active emergencies."""
        return list(self._active_emergencies.values())

    async def get_emergency_status(self, badge: str) -> dict[str, Any] | None:
        """Get emergency status for a specific officer."""
        return self._active_emergencies.get(badge)

    async def update_last_communication(self, badge: str) -> None:
        """Update last communication timestamp for an officer."""
        if self.redis:
            key = f"{LAST_COMMUNICATION_PREFIX}{badge}"
            await self.redis.set(
                key,
                datetime.utcnow().isoformat(),
                ex=3600,  # 1 hour TTL
            )


# Singleton instance
_emergency_detector: EmergencyDetector | None = None


def get_emergency_detector() -> EmergencyDetector:
    """Get or create the singleton EmergencyDetector instance."""
    global _emergency_detector
    if _emergency_detector is None:
        _emergency_detector = EmergencyDetector()
    return _emergency_detector
