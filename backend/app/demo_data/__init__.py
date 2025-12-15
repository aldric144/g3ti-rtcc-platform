"""
Demo Data Module for G3TI RTCC-UIP Platform.

This module provides in-memory mock datasets for demo mode operation,
allowing the platform to function without any database dependencies.

When DEMO_MODE is enabled:
- All database connections are skipped
- Mock data is loaded from JSON files
- API endpoints return simulated data
- Authentication uses demo credentials
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Path to demo data files
DEMO_DATA_DIR = Path(__file__).parent


class DemoDataStore:
    """
    In-memory data store for demo mode operation.
    
    Loads mock data from JSON files and provides methods to access
    and generate simulated real-time data.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if DemoDataStore._initialized:
            return
        
        self.users: list[dict] = []
        self.cameras: list[dict] = []
        self.incidents: list[dict] = []
        self.lpr_hits: list[dict] = []
        self.gunshot_alerts: list[dict] = []
        self.officers: list[dict] = []
        self.cases: list[dict] = []
        self.patrol_beats: list[dict] = []
        self.demo_credentials: dict[str, str] = {}
        
        self._load_all_data()
        DemoDataStore._initialized = True
    
    def _load_json_file(self, filename: str) -> dict:
        """Load a JSON file from the demo data directory."""
        filepath = DEMO_DATA_DIR / filename
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return {}
    
    def _load_all_data(self):
        """Load all demo data from JSON files."""
        # Load users
        users_data = self._load_json_file("users.json")
        self.users = users_data.get("users", [])
        self.demo_credentials = users_data.get("demo_credentials", {
            "demo": "demo123",
            "admin": "admin123"
        })
        
        # Load cameras
        cameras_data = self._load_json_file("cameras.json")
        self.cameras = cameras_data.get("cameras", [])
        
        # Load incidents
        incidents_data = self._load_json_file("incidents.json")
        self.incidents = incidents_data.get("incidents", [])
        
        # Load LPR hits
        lpr_data = self._load_json_file("lpr_hits.json")
        self.lpr_hits = lpr_data.get("lpr_hits", [])
        
        # Load gunshot alerts
        gunshot_data = self._load_json_file("gunshot_alerts.json")
        self.gunshot_alerts = gunshot_data.get("gunshot_alerts", [])
        
        # Load officers
        officers_data = self._load_json_file("officers.json")
        self.officers = officers_data.get("officers", [])
        
        # Load cases
        cases_data = self._load_json_file("cases.json")
        self.cases = cases_data.get("cases", [])
        
        # Load patrol beats
        beats_data = self._load_json_file("patrol_beats.json")
        self.patrol_beats = beats_data.get("patrol_beats", [])
    
    def verify_demo_credentials(self, username: str, password: str) -> dict | None:
        """
        Verify demo credentials and return user data if valid.
        
        Args:
            username: Username to verify
            password: Password to verify
            
        Returns:
            User dict if credentials are valid, None otherwise
        """
        if username in self.demo_credentials:
            if self.demo_credentials[username] == password:
                # Find user data
                for user in self.users:
                    if user["username"] == username:
                        return user
                # Return default demo user if not found in users list
                return {
                    "id": f"demo-{username}",
                    "username": username,
                    "email": f"{username}@g3ti-demo.com",
                    "first_name": username.capitalize(),
                    "last_name": "User",
                    "badge_number": f"DEMO-{username.upper()}",
                    "department": "Demo",
                    "role": "admin",
                    "is_active": True,
                }
        return None
    
    def get_user_by_username(self, username: str) -> dict | None:
        """Get user by username."""
        for user in self.users:
            if user["username"] == username:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> dict | None:
        """Get user by ID."""
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_all_cameras(self) -> list[dict]:
        """Get all cameras."""
        return self.cameras
    
    def get_camera_by_id(self, camera_id: str) -> dict | None:
        """Get camera by ID."""
        for camera in self.cameras:
            if camera["id"] == camera_id:
                return camera
        return None
    
    def get_all_incidents(self, status: str | None = None) -> list[dict]:
        """Get all incidents, optionally filtered by status."""
        if status:
            return [i for i in self.incidents if i["status"] == status]
        return self.incidents
    
    def get_incident_by_id(self, incident_id: str) -> dict | None:
        """Get incident by ID."""
        for incident in self.incidents:
            if incident["id"] == incident_id:
                return incident
        return None
    
    def get_all_lpr_hits(self, status: str | None = None) -> list[dict]:
        """Get all LPR hits, optionally filtered by status."""
        if status:
            return [h for h in self.lpr_hits if h["alert_status"] == status]
        return self.lpr_hits
    
    def get_all_gunshot_alerts(self, status: str | None = None) -> list[dict]:
        """Get all gunshot alerts, optionally filtered by status."""
        if status:
            return [a for a in self.gunshot_alerts if a["status"] == status]
        return self.gunshot_alerts
    
    def get_all_officers(self, status: str | None = None) -> list[dict]:
        """Get all officers, optionally filtered by status."""
        if status:
            return [o for o in self.officers if o["status"] == status]
        return self.officers
    
    def get_officer_by_id(self, officer_id: str) -> dict | None:
        """Get officer by ID."""
        for officer in self.officers:
            if officer["id"] == officer_id:
                return officer
        return None
    
    def get_all_cases(self, status: str | None = None) -> list[dict]:
        """Get all cases, optionally filtered by status."""
        if status:
            return [c for c in self.cases if c["status"] == status]
        return self.cases
    
    def get_case_by_id(self, case_id: str) -> dict | None:
        """Get case by ID."""
        for case in self.cases:
            if case["id"] == case_id:
                return case
        return None
    
    def get_all_patrol_beats(self) -> list[dict]:
        """Get all patrol beats."""
        return self.patrol_beats
    
    def get_beat_by_id(self, beat_id: str) -> dict | None:
        """Get patrol beat by ID."""
        for beat in self.patrol_beats:
            if beat["id"] == beat_id:
                return beat
        return None
    
    def generate_random_event(self) -> dict:
        """
        Generate a random simulated event for WebSocket streaming.
        
        Returns:
            Dict containing a random event (LPR hit, gunshot, or incident)
        """
        event_types = ["lpr_hit", "gunshot_alert", "incident", "officer_update"]
        event_type = random.choice(event_types)
        
        now = datetime.utcnow().isoformat() + "Z"
        
        if event_type == "lpr_hit":
            plates = ["ABC-1234", "XYZ-5678", "DEF-9012", "GHI-3456", "JKL-7890"]
            hit_types = ["stolen_vehicle", "wanted_person", "bolo", "expired_registration"]
            return {
                "type": "lpr_hit",
                "data": {
                    "id": f"lpr-sim-{random.randint(1000, 9999)}",
                    "plate_number": random.choice(plates),
                    "plate_state": "FL",
                    "hit_type": random.choice(hit_types),
                    "confidence": round(random.uniform(85, 99), 1),
                    "location": {
                        "latitude": 26.77 + random.uniform(-0.02, 0.02),
                        "longitude": -80.05 + random.uniform(-0.02, 0.02)
                    },
                    "timestamp": now,
                    "alert_status": "active"
                }
            }
        
        elif event_type == "gunshot_alert":
            return {
                "type": "gunshot_alert",
                "data": {
                    "id": f"gs-sim-{random.randint(1000, 9999)}",
                    "alert_type": "gunshot",
                    "rounds_detected": random.randint(1, 6),
                    "confidence": round(random.uniform(75, 98), 1),
                    "location": {
                        "latitude": 26.77 + random.uniform(-0.02, 0.02),
                        "longitude": -80.06 + random.uniform(-0.02, 0.02)
                    },
                    "timestamp": now,
                    "status": "active"
                }
            }
        
        elif event_type == "incident":
            incident_types = ["traffic_accident", "suspicious_activity", "theft", "disturbance"]
            priorities = ["low", "medium", "high", "critical"]
            return {
                "type": "incident",
                "data": {
                    "id": f"inc-sim-{random.randint(1000, 9999)}",
                    "incident_type": random.choice(incident_types),
                    "status": "active",
                    "priority": random.choice(priorities),
                    "location": {
                        "latitude": 26.77 + random.uniform(-0.02, 0.02),
                        "longitude": -80.05 + random.uniform(-0.02, 0.02)
                    },
                    "timestamp": now
                }
            }
        
        else:  # officer_update
            statuses = ["on_duty", "responding", "on_scene", "available"]
            officer = random.choice(self.officers) if self.officers else {
                "id": "officer-sim",
                "name": "Officer Demo",
                "unit_id": "Unit-01"
            }
            return {
                "type": "officer_update",
                "data": {
                    "officer_id": officer["id"],
                    "name": officer.get("name", "Officer Demo"),
                    "unit_id": officer.get("unit_id", "Unit-01"),
                    "status": random.choice(statuses),
                    "location": {
                        "latitude": 26.77 + random.uniform(-0.02, 0.02),
                        "longitude": -80.05 + random.uniform(-0.02, 0.02)
                    },
                    "timestamp": now
                }
            }
    
    def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics."""
        return {
            "active_incidents": len([i for i in self.incidents if i["status"] == "active"]),
            "total_cameras": len(self.cameras),
            "online_cameras": len([c for c in self.cameras if c["status"] == "online"]),
            "officers_on_duty": len([o for o in self.officers if o["status"] in ["on_duty", "responding", "on_scene"]]),
            "open_cases": len([c for c in self.cases if c["status"] in ["open", "active"]]),
            "lpr_hits_today": len(self.lpr_hits),
            "gunshot_alerts_today": len([g for g in self.gunshot_alerts if g["status"] == "active"]),
            "patrol_beats_active": len(self.patrol_beats),
            "demo_mode": True
        }


# Global demo data store instance
demo_store = DemoDataStore()


def get_demo_store() -> DemoDataStore:
    """Get the global demo data store instance."""
    return demo_store
