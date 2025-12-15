"""
Tests for Video Wall Manager.
"""

import pytest

from app.camera_network.video_wall_manager import (
    VideoWallManager,
    VideoWallLayout,
    VideoWallSlot,
    VideoWallPreset,
    VideoWallSession,
    get_video_wall_manager,
)


class TestVideoWallManager:
    """Test suite for VideoWallManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = VideoWallManager()
        self.manager._sessions.clear()
        # Keep default presets
    
    def test_create_session_2x2(self):
        """Test creating a 2x2 video wall session."""
        session = self.manager.create_session("user-001", "2x2")
        
        assert session.user_id == "user-001"
        assert session.layout == VideoWallLayout.LAYOUT_2X2
        assert len(session.slots) == 4
    
    def test_create_session_3x3(self):
        """Test creating a 3x3 video wall session."""
        session = self.manager.create_session("user-002", "3x3")
        
        assert session.layout == VideoWallLayout.LAYOUT_3X3
        assert len(session.slots) == 9
    
    def test_create_session_4x4(self):
        """Test creating a 4x4 video wall session."""
        session = self.manager.create_session("user-003", "4x4")
        
        assert session.layout == VideoWallLayout.LAYOUT_4X4
        assert len(session.slots) == 16
    
    def test_get_session(self):
        """Test getting a session by ID."""
        session = self.manager.create_session("user-004", "2x2")
        
        retrieved = self.manager.get_session(session.session_id)
        
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    def test_get_user_session(self):
        """Test getting a session by user ID."""
        session = self.manager.create_session("user-005", "2x2")
        
        retrieved = self.manager.get_user_session("user-005")
        
        assert retrieved is not None
        assert retrieved.user_id == "user-005"
    
    def test_delete_session(self):
        """Test deleting a session."""
        session = self.manager.create_session("user-006", "2x2")
        
        result = self.manager.delete_session(session.session_id)
        
        assert result is True
        assert self.manager.get_session(session.session_id) is None
    
    def test_add_camera_to_wall(self):
        """Test adding a camera to a video wall slot."""
        session = self.manager.create_session("user-007", "2x2")
        
        result = self.manager.add_camera_to_wall(
            session.session_id,
            position=0,
            camera_id="cam-001",
            camera_name="Test Camera",
            stream_url="https://example.com/stream",
        )
        
        assert result is True
        assert session.slots[0].camera_id == "cam-001"
        assert session.slots[0].is_empty is False
    
    def test_remove_camera_from_wall(self):
        """Test removing a camera from a video wall slot."""
        session = self.manager.create_session("user-008", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Test", "https://example.com"
        )
        
        result = self.manager.remove_camera_from_wall(session.session_id, 0)
        
        assert result is True
        assert session.slots[0].is_empty is True
    
    def test_move_camera(self):
        """Test moving a camera between slots (drag-and-drop)."""
        session = self.manager.create_session("user-009", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Camera 1", "https://example.com/1"
        )
        
        result = self.manager.move_camera(session.session_id, 0, 2)
        
        assert result is True
        assert session.slots[0].is_empty is True
        assert session.slots[2].camera_id == "cam-001"
    
    def test_clear_wall(self):
        """Test clearing all cameras from the video wall."""
        session = self.manager.create_session("user-010", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Camera 1", "https://example.com/1"
        )
        self.manager.add_camera_to_wall(
            session.session_id, 1, "cam-002", "Camera 2", "https://example.com/2"
        )
        
        result = self.manager.clear_wall(session.session_id)
        
        assert result is True
        for slot in session.slots:
            assert slot.is_empty is True
    
    def test_change_layout(self):
        """Test changing the video wall layout."""
        session = self.manager.create_session("user-011", "2x2")
        
        result = self.manager.change_layout(session.session_id, "3x3")
        
        assert result is True
        assert session.layout == VideoWallLayout.LAYOUT_3X3
        assert len(session.slots) == 9
    
    def test_change_layout_preserves_cameras(self):
        """Test that changing layout preserves existing cameras."""
        session = self.manager.create_session("user-012", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Camera 1", "https://example.com/1"
        )
        
        self.manager.change_layout(session.session_id, "3x3")
        
        assert session.slots[0].camera_id == "cam-001"
    
    def test_save_preset(self):
        """Test saving a video wall preset."""
        session = self.manager.create_session("user-013", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Camera 1", "https://example.com/1"
        )
        
        preset = self.manager.save_preset(
            session.session_id, "My Preset", "user-013"
        )
        
        assert preset is not None
        assert preset.name == "My Preset"
        assert preset.layout == VideoWallLayout.LAYOUT_2X2
    
    def test_load_preset(self):
        """Test loading a preset into a session."""
        session = self.manager.create_session("user-014", "2x2")
        self.manager.add_camera_to_wall(
            session.session_id, 0, "cam-001", "Camera 1", "https://example.com/1"
        )
        preset = self.manager.save_preset(session.session_id, "Test Preset")
        
        # Create new session and load preset
        session2 = self.manager.create_session("user-015", "3x3")
        result = self.manager.load_preset(session2.session_id, preset.id)
        
        assert result is True
        assert session2.layout == VideoWallLayout.LAYOUT_2X2
    
    def test_list_presets(self):
        """Test listing all presets."""
        presets = self.manager.list_presets()
        
        # Should have default presets
        assert len(presets) >= 3
    
    def test_delete_preset(self):
        """Test deleting a preset."""
        session = self.manager.create_session("user-016", "2x2")
        preset = self.manager.save_preset(session.session_id, "To Delete")
        
        result = self.manager.delete_preset(preset.id)
        
        assert result is True
    
    def test_cannot_delete_default_preset(self):
        """Test that default presets cannot be deleted."""
        result = self.manager.delete_preset("default-2x2")
        
        assert result is False
    
    def test_get_wall_state(self):
        """Test getting video wall state."""
        session = self.manager.create_session("user-017", "2x2")
        
        state = self.manager.get_wall_state(session.session_id)
        
        assert state is not None
        assert state["layout"] == "2x2"
        assert len(state["slots"]) == 4
    
    def test_get_available_layouts(self):
        """Test getting available layouts."""
        layouts = self.manager.get_available_layouts()
        
        assert len(layouts) == 4  # 1x1, 2x2, 3x3, 4x4
        for layout in layouts:
            assert "id" in layout
            assert "name" in layout
            assert "slots" in layout
    
    def test_singleton_pattern(self):
        """Test that get_video_wall_manager returns singleton."""
        manager1 = get_video_wall_manager()
        manager2 = get_video_wall_manager()
        
        assert manager1 is manager2
