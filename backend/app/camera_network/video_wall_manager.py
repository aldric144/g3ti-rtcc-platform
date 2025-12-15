"""
Video Wall Manager for G3TI RTCC-UIP Platform.

Manages video wall layouts, presets, and camera assignments.
Supports 2x2, 3x3, and 4x4 layouts with drag-and-drop functionality.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class VideoWallLayout(str, Enum):
    """Supported video wall layouts."""
    LAYOUT_2X2 = "2x2"
    LAYOUT_3X3 = "3x3"
    LAYOUT_4X4 = "4x4"
    LAYOUT_1X1 = "1x1"  # Single camera fullscreen
    LAYOUT_CUSTOM = "custom"


@dataclass
class VideoWallSlot:
    """A single slot in the video wall."""
    position: int  # 0-indexed position in grid
    camera_id: Optional[str] = None
    camera_name: Optional[str] = None
    stream_url: Optional[str] = None
    is_empty: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "position": self.position,
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "stream_url": self.stream_url,
            "is_empty": self.is_empty,
        }


@dataclass
class VideoWallPreset:
    """A saved video wall configuration preset."""
    id: str
    name: str
    layout: VideoWallLayout
    slots: List[VideoWallSlot]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "layout": self.layout.value,
            "slots": [s.to_dict() for s in self.slots],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
        }


@dataclass
class VideoWallSession:
    """An active video wall session."""
    session_id: str
    user_id: str
    layout: VideoWallLayout
    slots: List[VideoWallSlot]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "layout": self.layout.value,
            "slots": [s.to_dict() for s in self.slots],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


class VideoWallManager:
    """
    Video wall management system.
    
    Handles layout management, camera assignments, presets, and sessions.
    """
    
    _instance: Optional["VideoWallManager"] = None
    
    def __new__(cls) -> "VideoWallManager":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the video wall manager."""
        if self._initialized:
            return
        
        self._sessions: Dict[str, VideoWallSession] = {}
        self._presets: Dict[str, VideoWallPreset] = {}
        self._initialized = True
        
        # Create default presets
        self._create_default_presets()
    
    def _create_default_presets(self):
        """Create default video wall presets."""
        # 2x2 default preset
        self._presets["default-2x2"] = VideoWallPreset(
            id="default-2x2",
            name="Default 2x2",
            layout=VideoWallLayout.LAYOUT_2X2,
            slots=[VideoWallSlot(position=i) for i in range(4)],
        )
        
        # 3x3 default preset
        self._presets["default-3x3"] = VideoWallPreset(
            id="default-3x3",
            name="Default 3x3",
            layout=VideoWallLayout.LAYOUT_3X3,
            slots=[VideoWallSlot(position=i) for i in range(9)],
        )
        
        # 4x4 default preset
        self._presets["default-4x4"] = VideoWallPreset(
            id="default-4x4",
            name="Default 4x4",
            layout=VideoWallLayout.LAYOUT_4X4,
            slots=[VideoWallSlot(position=i) for i in range(16)],
        )
    
    def _get_slot_count(self, layout: VideoWallLayout) -> int:
        """Get number of slots for a layout."""
        if layout == VideoWallLayout.LAYOUT_1X1:
            return 1
        elif layout == VideoWallLayout.LAYOUT_2X2:
            return 4
        elif layout == VideoWallLayout.LAYOUT_3X3:
            return 9
        elif layout == VideoWallLayout.LAYOUT_4X4:
            return 16
        else:
            return 4  # Default to 2x2
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def create_session(
        self,
        user_id: str,
        layout: str = "2x2",
    ) -> VideoWallSession:
        """
        Create a new video wall session.
        
        Args:
            user_id: User identifier.
            layout: Layout type (2x2, 3x3, 4x4).
            
        Returns:
            New VideoWallSession.
        """
        try:
            layout_enum = VideoWallLayout(layout)
        except ValueError:
            layout_enum = VideoWallLayout.LAYOUT_2X2
        
        slot_count = self._get_slot_count(layout_enum)
        
        session = VideoWallSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            layout=layout_enum,
            slots=[VideoWallSlot(position=i) for i in range(slot_count)],
        )
        
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[VideoWallSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def get_user_session(self, user_id: str) -> Optional[VideoWallSession]:
        """Get the active session for a user."""
        for session in self._sessions.values():
            if session.user_id == user_id:
                return session
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    # ========================================================================
    # Camera Assignment
    # ========================================================================
    
    def add_camera_to_wall(
        self,
        session_id: str,
        position: int,
        camera_id: str,
        camera_name: str = "",
        stream_url: str = "",
    ) -> bool:
        """
        Add a camera to a video wall slot.
        
        Args:
            session_id: Session identifier.
            position: Slot position (0-indexed).
            camera_id: Camera identifier.
            camera_name: Camera display name.
            stream_url: Camera stream URL.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if position < 0 or position >= len(session.slots):
            return False
        
        session.slots[position] = VideoWallSlot(
            position=position,
            camera_id=camera_id,
            camera_name=camera_name,
            stream_url=stream_url,
            is_empty=False,
        )
        session.last_activity = datetime.utcnow()
        
        return True
    
    def remove_camera_from_wall(
        self,
        session_id: str,
        position: int,
    ) -> bool:
        """
        Remove a camera from a video wall slot.
        
        Args:
            session_id: Session identifier.
            position: Slot position (0-indexed).
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if position < 0 or position >= len(session.slots):
            return False
        
        session.slots[position] = VideoWallSlot(position=position)
        session.last_activity = datetime.utcnow()
        
        return True
    
    def move_camera(
        self,
        session_id: str,
        from_position: int,
        to_position: int,
    ) -> bool:
        """
        Move a camera from one slot to another (drag-and-drop).
        
        Args:
            session_id: Session identifier.
            from_position: Source slot position.
            to_position: Destination slot position.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if (from_position < 0 or from_position >= len(session.slots) or
            to_position < 0 or to_position >= len(session.slots)):
            return False
        
        # Swap slots
        from_slot = session.slots[from_position]
        to_slot = session.slots[to_position]
        
        # Update positions
        from_slot.position = to_position
        to_slot.position = from_position
        
        session.slots[from_position] = to_slot
        session.slots[to_position] = from_slot
        session.last_activity = datetime.utcnow()
        
        return True
    
    def clear_wall(self, session_id: str) -> bool:
        """
        Clear all cameras from the video wall.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        for i in range(len(session.slots)):
            session.slots[i] = VideoWallSlot(position=i)
        
        session.last_activity = datetime.utcnow()
        return True
    
    def change_layout(
        self,
        session_id: str,
        layout: str,
    ) -> bool:
        """
        Change the video wall layout.
        
        Args:
            session_id: Session identifier.
            layout: New layout type.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        try:
            layout_enum = VideoWallLayout(layout)
        except ValueError:
            return False
        
        new_slot_count = self._get_slot_count(layout_enum)
        old_slots = session.slots
        
        # Create new slots, preserving cameras where possible
        new_slots = []
        for i in range(new_slot_count):
            if i < len(old_slots) and not old_slots[i].is_empty:
                slot = old_slots[i]
                slot.position = i
                new_slots.append(slot)
            else:
                new_slots.append(VideoWallSlot(position=i))
        
        session.layout = layout_enum
        session.slots = new_slots
        session.last_activity = datetime.utcnow()
        
        return True
    
    # ========================================================================
    # Preset Management
    # ========================================================================
    
    def save_preset(
        self,
        session_id: str,
        preset_name: str,
        created_by: Optional[str] = None,
    ) -> Optional[VideoWallPreset]:
        """
        Save current session as a preset.
        
        Args:
            session_id: Session identifier.
            preset_name: Name for the preset.
            created_by: User who created the preset.
            
        Returns:
            Created preset or None.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        preset = VideoWallPreset(
            id=str(uuid.uuid4()),
            name=preset_name,
            layout=session.layout,
            slots=[VideoWallSlot(**s.to_dict()) for s in session.slots],
            created_by=created_by,
        )
        
        self._presets[preset.id] = preset
        return preset
    
    def load_preset(
        self,
        session_id: str,
        preset_id: str,
    ) -> bool:
        """
        Load a preset into a session.
        
        Args:
            session_id: Session identifier.
            preset_id: Preset identifier.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self._sessions.get(session_id)
        preset = self._presets.get(preset_id)
        
        if not session or not preset:
            return False
        
        session.layout = preset.layout
        session.slots = [VideoWallSlot(**s.to_dict()) for s in preset.slots]
        session.last_activity = datetime.utcnow()
        
        return True
    
    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a preset by ID."""
        preset = self._presets.get(preset_id)
        return preset.to_dict() if preset else None
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """List all presets."""
        return [p.to_dict() for p in self._presets.values()]
    
    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset."""
        if preset_id in self._presets and not preset_id.startswith("default-"):
            del self._presets[preset_id]
            return True
        return False
    
    # ========================================================================
    # Video Wall State
    # ========================================================================
    
    def get_wall_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current video wall state.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            Wall state dictionary or None.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        return session.to_dict()
    
    def get_available_layouts(self) -> List[Dict[str, Any]]:
        """Get list of available layouts."""
        return [
            {"id": "1x1", "name": "Single Camera", "slots": 1, "rows": 1, "cols": 1},
            {"id": "2x2", "name": "2x2 Grid", "slots": 4, "rows": 2, "cols": 2},
            {"id": "3x3", "name": "3x3 Grid", "slots": 9, "rows": 3, "cols": 3},
            {"id": "4x4", "name": "4x4 Grid", "slots": 16, "rows": 4, "cols": 4},
        ]


# Singleton accessor
_manager_instance: Optional[VideoWallManager] = None


def get_video_wall_manager() -> VideoWallManager:
    """
    Get the video wall manager singleton.
    
    Returns:
        VideoWallManager instance.
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = VideoWallManager()
    return _manager_instance
