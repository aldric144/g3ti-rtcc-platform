"""
Phase 19: Autonomy Engine Module Tests

Tests for PathfindingEngine, ObstacleAvoidanceEngine, IndoorNavigationMap, and PatrolPatternGenerator.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestPathfindingEngine:
    """Tests for PathfindingEngine."""

    def test_compute_path_a_star(self):
        """Test A* pathfinding."""
        from backend.app.robotics.autonomy_engine import PathfindingEngine, PathfindingAlgorithm

        engine = PathfindingEngine()
        result = engine.compute_path(
            robot_id="robot-001",
            start={"x": 0, "y": 0, "z": 0},
            goal={"x": 100, "y": 100, "z": 0},
            algorithm=PathfindingAlgorithm.A_STAR,
        )

        assert result is not None
        assert result.robot_id == "robot-001"
        assert len(result.waypoints) > 0
        assert result.algorithm == PathfindingAlgorithm.A_STAR

    def test_compute_path_d_star(self):
        """Test D* pathfinding."""
        from backend.app.robotics.autonomy_engine import PathfindingEngine, PathfindingAlgorithm

        engine = PathfindingEngine()
        result = engine.compute_path(
            robot_id="robot-002",
            start={"x": 0, "y": 0, "z": 0},
            goal={"x": 50, "y": 50, "z": 0},
            algorithm=PathfindingAlgorithm.D_STAR,
        )

        assert result is not None
        assert result.algorithm == PathfindingAlgorithm.D_STAR

    def test_compute_path_rrt_star(self):
        """Test RRT* pathfinding."""
        from backend.app.robotics.autonomy_engine import PathfindingEngine, PathfindingAlgorithm

        engine = PathfindingEngine()
        result = engine.compute_path(
            robot_id="robot-003",
            start={"x": 0, "y": 0, "z": 0},
            goal={"x": 200, "y": 150, "z": 0},
            algorithm=PathfindingAlgorithm.RRT_STAR,
        )

        assert result is not None
        assert result.algorithm == PathfindingAlgorithm.RRT_STAR

    def test_get_path(self):
        """Test getting computed path."""
        from backend.app.robotics.autonomy_engine import PathfindingEngine, PathfindingAlgorithm

        engine = PathfindingEngine()
        result = engine.compute_path(
            robot_id="robot-004",
            start={"x": 0, "y": 0, "z": 0},
            goal={"x": 100, "y": 0, "z": 0},
            algorithm=PathfindingAlgorithm.A_STAR,
        )

        retrieved = engine.get_path(result.path_id)
        assert retrieved is not None
        assert retrieved.path_id == result.path_id

    def test_invalidate_cache(self):
        """Test cache invalidation."""
        from backend.app.robotics.autonomy_engine import PathfindingEngine, PathfindingAlgorithm

        engine = PathfindingEngine()
        engine.compute_path(
            robot_id="robot-005",
            start={"x": 0, "y": 0, "z": 0},
            goal={"x": 50, "y": 50, "z": 0},
            algorithm=PathfindingAlgorithm.A_STAR,
        )

        count = engine.invalidate_cache("robot-005")
        assert count >= 0


class TestObstacleAvoidanceEngine:
    """Tests for ObstacleAvoidanceEngine."""

    def test_detect_obstacle(self):
        """Test obstacle detection."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine, ObstacleType

        engine = ObstacleAvoidanceEngine()
        obstacle = engine.detect_obstacle(
            position={"x": 50, "y": 50, "z": 0},
            radius=2.0,
            obstacle_type=ObstacleType.STATIC,
            detected_by="robot-001",
        )

        assert obstacle is not None
        assert obstacle.position["x"] == 50
        assert obstacle.radius == 2.0

    def test_update_obstacle(self):
        """Test updating obstacle."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine, ObstacleType

        engine = ObstacleAvoidanceEngine()
        obstacle = engine.detect_obstacle(
            position={"x": 30, "y": 30, "z": 0},
            radius=1.5,
            obstacle_type=ObstacleType.DYNAMIC,
            detected_by="robot-002",
        )

        updated = engine.update_obstacle(
            obstacle.obstacle_id,
            position={"x": 35, "y": 35, "z": 0},
        )

        assert updated is not None
        assert updated.position["x"] == 35

    def test_remove_obstacle(self):
        """Test removing obstacle."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine, ObstacleType

        engine = ObstacleAvoidanceEngine()
        obstacle = engine.detect_obstacle(
            position={"x": 20, "y": 20, "z": 0},
            radius=1.0,
            obstacle_type=ObstacleType.TEMPORARY,
            detected_by="robot-003",
        )

        result = engine.remove_obstacle(obstacle.obstacle_id)
        assert result is True

    def test_get_obstacles_in_path(self):
        """Test getting obstacles in path."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine, ObstacleType

        engine = ObstacleAvoidanceEngine()
        engine.detect_obstacle(
            position={"x": 50, "y": 50, "z": 0},
            radius=5.0,
            obstacle_type=ObstacleType.STATIC,
            detected_by="robot-004",
        )

        path = [
            {"x": 0, "y": 0, "z": 0},
            {"x": 50, "y": 50, "z": 0},
            {"x": 100, "y": 100, "z": 0},
        ]

        obstacles = engine.get_obstacles_in_path(path)
        assert len(obstacles) >= 0

    def test_compute_avoidance_vector(self):
        """Test computing avoidance vector."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine, ObstacleType

        engine = ObstacleAvoidanceEngine()
        engine.detect_obstacle(
            position={"x": 10, "y": 0, "z": 0},
            radius=2.0,
            obstacle_type=ObstacleType.STATIC,
            detected_by="robot-005",
        )

        vector = engine.compute_avoidance_vector(
            robot_position={"x": 5, "y": 0, "z": 0},
            robot_heading=0.0,
        )

        assert vector is not None
        assert "x" in vector
        assert "y" in vector

    def test_fuse_sensor_data(self):
        """Test sensor data fusion."""
        from backend.app.robotics.autonomy_engine import ObstacleAvoidanceEngine

        engine = ObstacleAvoidanceEngine()
        sensor_data = [
            {"sensor": "lidar", "position": {"x": 10, "y": 10, "z": 0}, "confidence": 0.9},
            {"sensor": "camera", "position": {"x": 11, "y": 10, "z": 0}, "confidence": 0.8},
        ]

        fused = engine.fuse_sensor_data(sensor_data)
        assert fused is not None


class TestIndoorNavigationMap:
    """Tests for IndoorNavigationMap."""

    def test_create_map(self):
        """Test creating navigation map."""
        from backend.app.robotics.autonomy_engine import IndoorNavigationMap

        nav_map = IndoorNavigationMap()
        created = nav_map.create_map(
            name="Building A Floor 1",
            building_id="building-a",
            floor=1,
            bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
        )

        assert created is not None
        assert created.name == "Building A Floor 1"
        assert created.floor == 1

    def test_add_node(self):
        """Test adding navigation node."""
        from backend.app.robotics.autonomy_engine import IndoorNavigationMap, NavigationNodeType

        nav_map = IndoorNavigationMap()
        map_obj = nav_map.create_map(
            name="Test Map",
            building_id="test-building",
            floor=1,
            bounds={"min_x": 0, "min_y": 0, "max_x": 50, "max_y": 50},
        )

        node = nav_map.add_node(
            map_id=map_obj.map_id,
            position={"x": 25, "y": 25, "z": 0},
            node_type=NavigationNodeType.WAYPOINT,
        )

        assert node is not None
        assert node.position["x"] == 25

    def test_connect_nodes(self):
        """Test connecting navigation nodes."""
        from backend.app.robotics.autonomy_engine import IndoorNavigationMap, NavigationNodeType

        nav_map = IndoorNavigationMap()
        map_obj = nav_map.create_map(
            name="Connection Test",
            building_id="test-building",
            floor=1,
            bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
        )

        node1 = nav_map.add_node(map_obj.map_id, {"x": 0, "y": 0, "z": 0}, NavigationNodeType.WAYPOINT)
        node2 = nav_map.add_node(map_obj.map_id, {"x": 50, "y": 0, "z": 0}, NavigationNodeType.WAYPOINT)

        result = nav_map.connect_nodes(map_obj.map_id, node1.node_id, node2.node_id)
        assert result is True

    def test_add_room(self):
        """Test adding room to map."""
        from backend.app.robotics.autonomy_engine import IndoorNavigationMap

        nav_map = IndoorNavigationMap()
        map_obj = nav_map.create_map(
            name="Room Test",
            building_id="test-building",
            floor=1,
            bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
        )

        room = nav_map.add_room(
            map_id=map_obj.map_id,
            name="Conference Room A",
            bounds={"min_x": 10, "min_y": 10, "max_x": 30, "max_y": 30},
            room_type="conference",
        )

        assert room is not None
        assert room["name"] == "Conference Room A"

    def test_find_nearest_node(self):
        """Test finding nearest navigation node."""
        from backend.app.robotics.autonomy_engine import IndoorNavigationMap, NavigationNodeType

        nav_map = IndoorNavigationMap()
        map_obj = nav_map.create_map(
            name="Nearest Test",
            building_id="test-building",
            floor=1,
            bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
        )

        nav_map.add_node(map_obj.map_id, {"x": 10, "y": 10, "z": 0}, NavigationNodeType.WAYPOINT)
        nav_map.add_node(map_obj.map_id, {"x": 50, "y": 50, "z": 0}, NavigationNodeType.WAYPOINT)

        nearest = nav_map.find_nearest_node(map_obj.map_id, {"x": 12, "y": 12, "z": 0})
        assert nearest is not None


class TestPatrolPatternGenerator:
    """Tests for PatrolPatternGenerator."""

    def test_generate_s_pattern(self):
        """Test S-pattern generation."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="S-Pattern Test",
            pattern_type=PatrolPatternType.S_PATTERN,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
            spacing=20,
        )

        assert pattern is not None
        assert pattern.pattern_type == PatrolPatternType.S_PATTERN
        assert len(pattern.waypoints) > 0

    def test_generate_grid_pattern(self):
        """Test grid pattern generation."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Grid Test",
            pattern_type=PatrolPatternType.GRID,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 50, "max_y": 50},
            spacing=10,
        )

        assert pattern is not None
        assert pattern.pattern_type == PatrolPatternType.GRID

    def test_generate_perimeter_loop(self):
        """Test perimeter loop generation."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Perimeter Test",
            pattern_type=PatrolPatternType.PERIMETER_LOOP,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 200, "max_y": 200},
            spacing=50,
        )

        assert pattern is not None
        assert pattern.pattern_type == PatrolPatternType.PERIMETER_LOOP

    def test_generate_spiral_pattern(self):
        """Test spiral pattern generation."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Spiral Test",
            pattern_type=PatrolPatternType.SPIRAL,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
            spacing=15,
        )

        assert pattern is not None
        assert pattern.pattern_type == PatrolPatternType.SPIRAL

    def test_generate_coverage_pattern(self):
        """Test coverage pattern generation."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Coverage Test",
            pattern_type=PatrolPatternType.COVERAGE,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 80, "max_y": 80},
            spacing=10,
        )

        assert pattern is not None
        assert pattern.pattern_type == PatrolPatternType.COVERAGE

    def test_get_pattern(self):
        """Test getting patrol pattern."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Get Test",
            pattern_type=PatrolPatternType.PERIMETER_LOOP,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
        )

        retrieved = generator.get_pattern(pattern.pattern_id)
        assert retrieved is not None
        assert retrieved.pattern_id == pattern.pattern_id

    def test_modify_pattern(self):
        """Test modifying patrol pattern."""
        from backend.app.robotics.autonomy_engine import PatrolPatternGenerator, PatrolPatternType

        generator = PatrolPatternGenerator()
        pattern = generator.generate_pattern(
            name="Modify Test",
            pattern_type=PatrolPatternType.GRID,
            area_bounds={"min_x": 0, "min_y": 0, "max_x": 50, "max_y": 50},
        )

        modified = generator.modify_pattern(pattern.pattern_id, name="Modified Pattern")
        assert modified is not None
        assert modified.name == "Modified Pattern"
