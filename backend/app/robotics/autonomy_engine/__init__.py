"""
Autonomy Engine Module

Provides autonomous navigation capabilities including:
- PathfindingEngine: A*, D*, RRT* algorithms (stubbed)
- ObstacleAvoidanceEngine: Sensor fusion for obstacle detection
- IndoorNavigationMap: Floorplans, rooms, access points
- PatrolPatternGenerator: S-patterns, grids, perimeter loops
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid
import math


class PathfindingAlgorithm(Enum):
    """Pathfinding algorithms."""
    A_STAR = "a_star"
    D_STAR = "d_star"
    RRT_STAR = "rrt_star"
    DIJKSTRA = "dijkstra"
    POTENTIAL_FIELD = "potential_field"


class PatrolPatternType(Enum):
    """Types of patrol patterns."""
    S_PATTERN = "s_pattern"
    GRID = "grid"
    PERIMETER_LOOP = "perimeter_loop"
    RANDOM_WALK = "random_walk"
    WAYPOINT_SEQUENCE = "waypoint_sequence"
    COVERAGE = "coverage"
    SPIRAL = "spiral"


class ObstacleType(Enum):
    """Types of obstacles."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    TEMPORARY = "temporary"
    PERSON = "person"
    VEHICLE = "vehicle"
    UNKNOWN = "unknown"


class NavigationNodeType(Enum):
    """Types of navigation nodes."""
    WAYPOINT = "waypoint"
    DOOR = "door"
    ELEVATOR = "elevator"
    STAIRS = "stairs"
    ROOM_ENTRY = "room_entry"
    INTERSECTION = "intersection"
    CHARGING_STATION = "charging_station"


@dataclass
class PathResult:
    """Result of pathfinding operation."""
    path_id: str
    algorithm: PathfindingAlgorithm
    start_point: Dict[str, float]
    end_point: Dict[str, float]
    waypoints: List[Dict[str, float]]
    total_distance: float
    estimated_time_seconds: float
    path_cost: float
    is_valid: bool
    obstacles_avoided: int
    computed_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Obstacle:
    """Detected obstacle."""
    obstacle_id: str
    obstacle_type: ObstacleType
    position: Dict[str, float]
    dimensions: Dict[str, float]
    velocity: Optional[Dict[str, float]]
    confidence: float
    detected_at: str
    last_updated: str
    is_active: bool
    sensor_source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationNode:
    """Node in navigation map."""
    node_id: str
    node_type: NavigationNodeType
    position: Dict[str, float]
    floor: int
    room_id: Optional[str]
    connected_nodes: List[str]
    accessibility: Dict[str, bool]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationMap:
    """Indoor navigation map."""
    map_id: str
    name: str
    building_id: str
    floor: int
    dimensions: Dict[str, float]
    nodes: List[NavigationNode]
    obstacles: List[Dict[str, Any]]
    rooms: List[Dict[str, Any]]
    access_points: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatrolPattern:
    """Generated patrol pattern."""
    pattern_id: str
    pattern_type: PatrolPatternType
    name: str
    waypoints: List[Dict[str, float]]
    total_distance: float
    estimated_duration_minutes: float
    coverage_area: float
    repeat_count: int
    created_at: str
    created_by: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PathfindingEngine:
    """Engine for computing optimal paths."""

    def __init__(self):
        self.computed_paths: Dict[str, PathResult] = {}
        self.path_cache: Dict[str, PathResult] = {}

    def compute_path(
        self,
        start_point: Dict[str, float],
        end_point: Dict[str, float],
        algorithm: PathfindingAlgorithm = PathfindingAlgorithm.A_STAR,
        obstacles: Optional[List[Obstacle]] = None,
        navigation_map: Optional[NavigationMap] = None,
        robot_radius: float = 0.5,
        max_iterations: int = 10000,
    ) -> PathResult:
        """Compute optimal path between two points."""
        path_id = f"path-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        cache_key = f"{start_point}_{end_point}_{algorithm.value}"
        if cache_key in self.path_cache:
            cached = self.path_cache[cache_key]
            cached_age = (datetime.utcnow() - datetime.fromisoformat(cached.computed_at.replace('Z', ''))).seconds
            if cached_age < 60:
                return cached

        if algorithm == PathfindingAlgorithm.A_STAR:
            waypoints, distance, cost = self._a_star(start_point, end_point, obstacles, robot_radius)
        elif algorithm == PathfindingAlgorithm.D_STAR:
            waypoints, distance, cost = self._d_star(start_point, end_point, obstacles, robot_radius)
        elif algorithm == PathfindingAlgorithm.RRT_STAR:
            waypoints, distance, cost = self._rrt_star(start_point, end_point, obstacles, robot_radius, max_iterations)
        else:
            waypoints, distance, cost = self._a_star(start_point, end_point, obstacles, robot_radius)

        avg_speed = 1.0
        estimated_time = distance / avg_speed

        obstacles_avoided = len(obstacles) if obstacles else 0

        result = PathResult(
            path_id=path_id,
            algorithm=algorithm,
            start_point=start_point,
            end_point=end_point,
            waypoints=waypoints,
            total_distance=distance,
            estimated_time_seconds=estimated_time,
            path_cost=cost,
            is_valid=len(waypoints) > 0,
            obstacles_avoided=obstacles_avoided,
            computed_at=timestamp,
            metadata={},
        )

        self.computed_paths[path_id] = result
        self.path_cache[cache_key] = result

        return result

    def _a_star(
        self,
        start: Dict[str, float],
        end: Dict[str, float],
        obstacles: Optional[List[Obstacle]],
        robot_radius: float,
    ) -> Tuple[List[Dict[str, float]], float, float]:
        """A* pathfinding algorithm (stub implementation)."""
        waypoints = [start]

        dx = end.get('x', 0) - start.get('x', 0)
        dy = end.get('y', 0) - start.get('y', 0)
        distance = math.sqrt(dx**2 + dy**2)

        if obstacles:
            num_intermediate = min(5, max(1, int(distance / 2)))
            for i in range(1, num_intermediate + 1):
                t = i / (num_intermediate + 1)
                waypoint = {
                    'x': start.get('x', 0) + dx * t,
                    'y': start.get('y', 0) + dy * t,
                    'z': start.get('z', 0),
                }
                waypoints.append(waypoint)

        waypoints.append(end)

        total_distance = 0.0
        for i in range(1, len(waypoints)):
            dx = waypoints[i].get('x', 0) - waypoints[i-1].get('x', 0)
            dy = waypoints[i].get('y', 0) - waypoints[i-1].get('y', 0)
            total_distance += math.sqrt(dx**2 + dy**2)

        cost = total_distance * 1.0

        return waypoints, total_distance, cost

    def _d_star(
        self,
        start: Dict[str, float],
        end: Dict[str, float],
        obstacles: Optional[List[Obstacle]],
        robot_radius: float,
    ) -> Tuple[List[Dict[str, float]], float, float]:
        """D* pathfinding algorithm (stub - uses A* internally)."""
        return self._a_star(start, end, obstacles, robot_radius)

    def _rrt_star(
        self,
        start: Dict[str, float],
        end: Dict[str, float],
        obstacles: Optional[List[Obstacle]],
        robot_radius: float,
        max_iterations: int,
    ) -> Tuple[List[Dict[str, float]], float, float]:
        """RRT* pathfinding algorithm (stub implementation)."""
        return self._a_star(start, end, obstacles, robot_radius)

    def get_path(self, path_id: str) -> Optional[PathResult]:
        """Get a computed path by ID."""
        return self.computed_paths.get(path_id)

    def invalidate_cache(self) -> None:
        """Invalidate the path cache."""
        self.path_cache.clear()


class ObstacleAvoidanceEngine:
    """Engine for obstacle detection and avoidance."""

    def __init__(self):
        self.detected_obstacles: Dict[str, Obstacle] = {}
        self.obstacle_history: List[Obstacle] = []
        self.safety_margin = 0.5

    def detect_obstacle(
        self,
        position: Dict[str, float],
        dimensions: Dict[str, float],
        obstacle_type: ObstacleType = ObstacleType.UNKNOWN,
        velocity: Optional[Dict[str, float]] = None,
        confidence: float = 0.8,
        sensor_source: str = "lidar",
    ) -> Obstacle:
        """Detect and register an obstacle."""
        obstacle_id = f"obs-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        obstacle = Obstacle(
            obstacle_id=obstacle_id,
            obstacle_type=obstacle_type,
            position=position,
            dimensions=dimensions,
            velocity=velocity,
            confidence=confidence,
            detected_at=timestamp,
            last_updated=timestamp,
            is_active=True,
            sensor_source=sensor_source,
            metadata={},
        )

        self.detected_obstacles[obstacle_id] = obstacle
        self.obstacle_history.append(obstacle)

        return obstacle

    def update_obstacle(
        self,
        obstacle_id: str,
        position: Optional[Dict[str, float]] = None,
        velocity: Optional[Dict[str, float]] = None,
        confidence: Optional[float] = None,
    ) -> bool:
        """Update an existing obstacle."""
        obstacle = self.detected_obstacles.get(obstacle_id)
        if not obstacle:
            return False

        if position:
            obstacle.position = position
        if velocity:
            obstacle.velocity = velocity
        if confidence is not None:
            obstacle.confidence = confidence

        obstacle.last_updated = datetime.utcnow().isoformat() + "Z"

        return True

    def remove_obstacle(self, obstacle_id: str) -> bool:
        """Remove an obstacle from tracking."""
        if obstacle_id in self.detected_obstacles:
            self.detected_obstacles[obstacle_id].is_active = False
            del self.detected_obstacles[obstacle_id]
            return True
        return False

    def get_obstacles_in_path(
        self,
        path_waypoints: List[Dict[str, float]],
        robot_radius: float = 0.5,
    ) -> List[Obstacle]:
        """Get obstacles that intersect with a path."""
        obstacles_in_path = []

        for obstacle in self.detected_obstacles.values():
            if not obstacle.is_active:
                continue

            for i in range(len(path_waypoints) - 1):
                if self._obstacle_intersects_segment(
                    obstacle,
                    path_waypoints[i],
                    path_waypoints[i + 1],
                    robot_radius + self.safety_margin,
                ):
                    obstacles_in_path.append(obstacle)
                    break

        return obstacles_in_path

    def _obstacle_intersects_segment(
        self,
        obstacle: Obstacle,
        point_a: Dict[str, float],
        point_b: Dict[str, float],
        clearance: float,
    ) -> bool:
        """Check if obstacle intersects with a line segment."""
        ox = obstacle.position.get('x', 0)
        oy = obstacle.position.get('y', 0)
        ow = obstacle.dimensions.get('width', 1) / 2
        oh = obstacle.dimensions.get('height', 1) / 2

        ax, ay = point_a.get('x', 0), point_a.get('y', 0)
        bx, by = point_b.get('x', 0), point_b.get('y', 0)

        dx = bx - ax
        dy = by - ay
        length = math.sqrt(dx**2 + dy**2)

        if length == 0:
            dist = math.sqrt((ox - ax)**2 + (oy - ay)**2)
            return dist < (max(ow, oh) + clearance)

        t = max(0, min(1, ((ox - ax) * dx + (oy - ay) * dy) / (length**2)))
        closest_x = ax + t * dx
        closest_y = ay + t * dy

        dist = math.sqrt((ox - closest_x)**2 + (oy - closest_y)**2)

        return dist < (max(ow, oh) + clearance)

    def compute_avoidance_vector(
        self,
        robot_position: Dict[str, float],
        robot_heading: float,
        obstacles: List[Obstacle],
    ) -> Dict[str, float]:
        """Compute avoidance vector based on nearby obstacles."""
        avoidance_x = 0.0
        avoidance_y = 0.0

        for obstacle in obstacles:
            dx = robot_position.get('x', 0) - obstacle.position.get('x', 0)
            dy = robot_position.get('y', 0) - obstacle.position.get('y', 0)
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0 and distance < 5.0:
                strength = 1.0 / (distance**2)
                avoidance_x += (dx / distance) * strength
                avoidance_y += (dy / distance) * strength

        magnitude = math.sqrt(avoidance_x**2 + avoidance_y**2)
        if magnitude > 0:
            avoidance_x /= magnitude
            avoidance_y /= magnitude

        return {'x': avoidance_x, 'y': avoidance_y}

    def get_active_obstacles(self) -> List[Obstacle]:
        """Get all active obstacles."""
        return [o for o in self.detected_obstacles.values() if o.is_active]

    def fuse_sensor_data(
        self,
        lidar_obstacles: List[Dict[str, Any]],
        camera_obstacles: List[Dict[str, Any]],
        radar_obstacles: List[Dict[str, Any]],
    ) -> List[Obstacle]:
        """Fuse obstacle data from multiple sensors (stub)."""
        fused_obstacles = []

        for lidar_obs in lidar_obstacles:
            obstacle = self.detect_obstacle(
                position=lidar_obs.get('position', {'x': 0, 'y': 0}),
                dimensions=lidar_obs.get('dimensions', {'width': 1, 'height': 1}),
                obstacle_type=ObstacleType.UNKNOWN,
                confidence=0.9,
                sensor_source="lidar",
            )
            fused_obstacles.append(obstacle)

        return fused_obstacles


class IndoorNavigationMap:
    """Manager for indoor navigation maps."""

    def __init__(self):
        self.maps: Dict[str, NavigationMap] = {}
        self.nodes: Dict[str, NavigationNode] = {}

    def create_map(
        self,
        name: str,
        building_id: str,
        floor: int,
        dimensions: Dict[str, float],
        rooms: Optional[List[Dict[str, Any]]] = None,
        access_points: Optional[List[Dict[str, Any]]] = None,
    ) -> NavigationMap:
        """Create a new navigation map."""
        map_id = f"map-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        nav_map = NavigationMap(
            map_id=map_id,
            name=name,
            building_id=building_id,
            floor=floor,
            dimensions=dimensions,
            nodes=[],
            obstacles=[],
            rooms=rooms or [],
            access_points=access_points or [],
            created_at=timestamp,
            updated_at=timestamp,
            metadata={},
        )

        self.maps[map_id] = nav_map

        return nav_map

    def add_node(
        self,
        map_id: str,
        node_type: NavigationNodeType,
        position: Dict[str, float],
        room_id: Optional[str] = None,
        connected_nodes: Optional[List[str]] = None,
        accessibility: Optional[Dict[str, bool]] = None,
    ) -> Optional[NavigationNode]:
        """Add a navigation node to a map."""
        nav_map = self.maps.get(map_id)
        if not nav_map:
            return None

        node_id = f"node-{uuid.uuid4().hex[:12]}"

        node = NavigationNode(
            node_id=node_id,
            node_type=node_type,
            position=position,
            floor=nav_map.floor,
            room_id=room_id,
            connected_nodes=connected_nodes or [],
            accessibility=accessibility or {"wheelchair": True, "robot": True},
            metadata={},
        )

        nav_map.nodes.append(node)
        self.nodes[node_id] = node
        nav_map.updated_at = datetime.utcnow().isoformat() + "Z"

        return node

    def connect_nodes(self, node_id_a: str, node_id_b: str) -> bool:
        """Connect two navigation nodes."""
        node_a = self.nodes.get(node_id_a)
        node_b = self.nodes.get(node_id_b)

        if not node_a or not node_b:
            return False

        if node_id_b not in node_a.connected_nodes:
            node_a.connected_nodes.append(node_id_b)
        if node_id_a not in node_b.connected_nodes:
            node_b.connected_nodes.append(node_id_a)

        return True

    def add_room(
        self,
        map_id: str,
        room_id: str,
        name: str,
        bounds: Dict[str, float],
        room_type: str = "general",
        entry_points: Optional[List[Dict[str, float]]] = None,
    ) -> bool:
        """Add a room to a map."""
        nav_map = self.maps.get(map_id)
        if not nav_map:
            return False

        room = {
            "room_id": room_id,
            "name": name,
            "bounds": bounds,
            "room_type": room_type,
            "entry_points": entry_points or [],
        }

        nav_map.rooms.append(room)
        nav_map.updated_at = datetime.utcnow().isoformat() + "Z"

        return True

    def add_obstacle(
        self,
        map_id: str,
        position: Dict[str, float],
        dimensions: Dict[str, float],
        obstacle_type: str = "static",
    ) -> bool:
        """Add a static obstacle to a map."""
        nav_map = self.maps.get(map_id)
        if not nav_map:
            return False

        obstacle = {
            "position": position,
            "dimensions": dimensions,
            "type": obstacle_type,
        }

        nav_map.obstacles.append(obstacle)
        nav_map.updated_at = datetime.utcnow().isoformat() + "Z"

        return True

    def get_map(self, map_id: str) -> Optional[NavigationMap]:
        """Get a navigation map by ID."""
        return self.maps.get(map_id)

    def get_maps(
        self,
        building_id: Optional[str] = None,
        floor: Optional[int] = None,
    ) -> List[NavigationMap]:
        """Get navigation maps with optional filtering."""
        maps = list(self.maps.values())

        if building_id:
            maps = [m for m in maps if m.building_id == building_id]

        if floor is not None:
            maps = [m for m in maps if m.floor == floor]

        return maps

    def find_nearest_node(
        self,
        map_id: str,
        position: Dict[str, float],
        node_type: Optional[NavigationNodeType] = None,
    ) -> Optional[NavigationNode]:
        """Find the nearest navigation node to a position."""
        nav_map = self.maps.get(map_id)
        if not nav_map:
            return None

        nearest = None
        min_distance = float('inf')

        for node in nav_map.nodes:
            if node_type and node.node_type != node_type:
                continue

            dx = node.position.get('x', 0) - position.get('x', 0)
            dy = node.position.get('y', 0) - position.get('y', 0)
            distance = math.sqrt(dx**2 + dy**2)

            if distance < min_distance:
                min_distance = distance
                nearest = node

        return nearest


class PatrolPatternGenerator:
    """Generator for patrol patterns."""

    def __init__(self):
        self.patterns: Dict[str, PatrolPattern] = {}

    def generate_pattern(
        self,
        pattern_type: PatrolPatternType,
        name: str,
        area_bounds: Dict[str, float],
        spacing: float = 5.0,
        start_point: Optional[Dict[str, float]] = None,
        created_by: str = "system",
    ) -> PatrolPattern:
        """Generate a patrol pattern."""
        pattern_id = f"patrol-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        if pattern_type == PatrolPatternType.S_PATTERN:
            waypoints = self._generate_s_pattern(area_bounds, spacing, start_point)
        elif pattern_type == PatrolPatternType.GRID:
            waypoints = self._generate_grid_pattern(area_bounds, spacing, start_point)
        elif pattern_type == PatrolPatternType.PERIMETER_LOOP:
            waypoints = self._generate_perimeter_loop(area_bounds, start_point)
        elif pattern_type == PatrolPatternType.SPIRAL:
            waypoints = self._generate_spiral_pattern(area_bounds, spacing, start_point)
        elif pattern_type == PatrolPatternType.COVERAGE:
            waypoints = self._generate_coverage_pattern(area_bounds, spacing, start_point)
        else:
            waypoints = self._generate_perimeter_loop(area_bounds, start_point)

        total_distance = self._calculate_total_distance(waypoints)
        avg_speed = 1.0
        estimated_duration = (total_distance / avg_speed) / 60.0

        coverage_area = (
            (area_bounds.get('max_x', 0) - area_bounds.get('min_x', 0)) *
            (area_bounds.get('max_y', 0) - area_bounds.get('min_y', 0))
        )

        pattern = PatrolPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            name=name,
            waypoints=waypoints,
            total_distance=total_distance,
            estimated_duration_minutes=estimated_duration,
            coverage_area=coverage_area,
            repeat_count=1,
            created_at=timestamp,
            created_by=created_by,
            metadata={},
        )

        self.patterns[pattern_id] = pattern

        return pattern

    def _generate_s_pattern(
        self,
        bounds: Dict[str, float],
        spacing: float,
        start: Optional[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        """Generate S-pattern waypoints."""
        waypoints = []
        min_x = bounds.get('min_x', 0)
        max_x = bounds.get('max_x', 100)
        min_y = bounds.get('min_y', 0)
        max_y = bounds.get('max_y', 100)

        y = min_y
        direction = 1

        while y <= max_y:
            if direction == 1:
                waypoints.append({'x': min_x, 'y': y, 'z': 0})
                waypoints.append({'x': max_x, 'y': y, 'z': 0})
            else:
                waypoints.append({'x': max_x, 'y': y, 'z': 0})
                waypoints.append({'x': min_x, 'y': y, 'z': 0})

            y += spacing
            direction *= -1

        return waypoints

    def _generate_grid_pattern(
        self,
        bounds: Dict[str, float],
        spacing: float,
        start: Optional[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        """Generate grid pattern waypoints."""
        waypoints = []
        min_x = bounds.get('min_x', 0)
        max_x = bounds.get('max_x', 100)
        min_y = bounds.get('min_y', 0)
        max_y = bounds.get('max_y', 100)

        x = min_x
        while x <= max_x:
            y = min_y
            while y <= max_y:
                waypoints.append({'x': x, 'y': y, 'z': 0})
                y += spacing
            x += spacing

        return waypoints

    def _generate_perimeter_loop(
        self,
        bounds: Dict[str, float],
        start: Optional[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        """Generate perimeter loop waypoints."""
        min_x = bounds.get('min_x', 0)
        max_x = bounds.get('max_x', 100)
        min_y = bounds.get('min_y', 0)
        max_y = bounds.get('max_y', 100)

        waypoints = [
            {'x': min_x, 'y': min_y, 'z': 0},
            {'x': max_x, 'y': min_y, 'z': 0},
            {'x': max_x, 'y': max_y, 'z': 0},
            {'x': min_x, 'y': max_y, 'z': 0},
            {'x': min_x, 'y': min_y, 'z': 0},
        ]

        return waypoints

    def _generate_spiral_pattern(
        self,
        bounds: Dict[str, float],
        spacing: float,
        start: Optional[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        """Generate spiral pattern waypoints."""
        waypoints = []
        min_x = bounds.get('min_x', 0)
        max_x = bounds.get('max_x', 100)
        min_y = bounds.get('min_y', 0)
        max_y = bounds.get('max_y', 100)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        max_radius = min(max_x - center_x, max_y - center_y)

        angle = 0
        radius = 0
        while radius <= max_radius:
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            waypoints.append({'x': x, 'y': y, 'z': 0})
            angle += 0.5
            radius += spacing / (2 * math.pi)

        return waypoints

    def _generate_coverage_pattern(
        self,
        bounds: Dict[str, float],
        spacing: float,
        start: Optional[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        """Generate coverage pattern (boustrophedon)."""
        return self._generate_s_pattern(bounds, spacing, start)

    def _calculate_total_distance(self, waypoints: List[Dict[str, float]]) -> float:
        """Calculate total distance of a path."""
        total = 0.0
        for i in range(1, len(waypoints)):
            dx = waypoints[i].get('x', 0) - waypoints[i-1].get('x', 0)
            dy = waypoints[i].get('y', 0) - waypoints[i-1].get('y', 0)
            total += math.sqrt(dx**2 + dy**2)
        return total

    def get_pattern(self, pattern_id: str) -> Optional[PatrolPattern]:
        """Get a patrol pattern by ID."""
        return self.patterns.get(pattern_id)

    def get_patterns(
        self,
        pattern_type: Optional[PatrolPatternType] = None,
    ) -> List[PatrolPattern]:
        """Get patrol patterns with optional filtering."""
        patterns = list(self.patterns.values())

        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]

        return patterns

    def modify_pattern(
        self,
        pattern_id: str,
        waypoints: Optional[List[Dict[str, float]]] = None,
        repeat_count: Optional[int] = None,
    ) -> bool:
        """Modify an existing patrol pattern."""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return False

        if waypoints:
            pattern.waypoints = waypoints
            pattern.total_distance = self._calculate_total_distance(waypoints)
            pattern.estimated_duration_minutes = (pattern.total_distance / 1.0) / 60.0

        if repeat_count is not None:
            pattern.repeat_count = repeat_count

        return True


__all__ = [
    "PathfindingEngine",
    "ObstacleAvoidanceEngine",
    "IndoorNavigationMap",
    "PatrolPatternGenerator",
    "PathResult",
    "Obstacle",
    "NavigationNode",
    "NavigationMap",
    "PatrolPattern",
    "PathfindingAlgorithm",
    "PatrolPatternType",
    "ObstacleType",
    "NavigationNodeType",
]
