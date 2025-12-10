"""
Tests for FederatedAnalyticsEngine

Tests regional heatmaps, cross-city trajectories, crime clusters,
and federated risk maps.
"""

import pytest
from datetime import datetime, timedelta

from app.fusion_cloud.federated_analytics import (
    FederatedAnalyticsEngine,
    RegionalHeatmap,
    HeatmapType,
    CrossCityTrajectory,
    RegionalCluster,
    ClusterType,
    FederatedRiskMap,
    RiskLevel,
)


@pytest.fixture
def analytics_engine():
    """Create a fresh FederatedAnalyticsEngine for each test"""
    return FederatedAnalyticsEngine()


class TestRegionalHeatmaps:
    """Tests for regional heatmap management"""

    def test_create_regional_heatmap(self, analytics_engine):
        """Test creating a regional heatmap"""
        heatmap = analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Regional Crime Heatmap",
            region_codes=["CA-METRO", "CA-COUNTY"],
            tenant_ids=["tenant-001", "tenant-002"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )

        assert heatmap is not None
        assert heatmap.heatmap_type == HeatmapType.CRIME
        assert heatmap.name == "Regional Crime Heatmap"
        assert "CA-METRO" in heatmap.region_codes

    def test_create_heatmap_with_resolution(self, analytics_engine):
        """Test creating a heatmap with specific resolution"""
        heatmap = analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.VIOLENCE,
            name="Violence Heatmap",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=7),
            time_range_end=datetime.utcnow(),
            resolution=9,
        )

        assert heatmap is not None
        assert heatmap.resolution == 9

    def test_create_heatmap_types(self, analytics_engine):
        """Test creating different heatmap types"""
        types = [
            HeatmapType.CRIME,
            HeatmapType.VIOLENCE,
            HeatmapType.PROPERTY_CRIME,
            HeatmapType.DRUG_ACTIVITY,
            HeatmapType.GANG_ACTIVITY,
        ]

        for i, heatmap_type in enumerate(types):
            heatmap = analytics_engine.create_regional_heatmap(
                heatmap_type=heatmap_type,
                name=f"Heatmap {i}",
                region_codes=["CA-METRO"],
                tenant_ids=["tenant-001"],
                time_range_start=datetime.utcnow() - timedelta(days=30),
                time_range_end=datetime.utcnow(),
            )
            assert heatmap is not None
            assert heatmap.heatmap_type == heatmap_type

    def test_get_heatmap(self, analytics_engine):
        """Test getting a heatmap by ID"""
        heatmap = analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Test Heatmap",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )

        retrieved = analytics_engine.get_heatmap(heatmap.heatmap_id)
        assert retrieved is not None
        assert retrieved.heatmap_id == heatmap.heatmap_id

    def test_add_heatmap_data(self, analytics_engine):
        """Test adding data to a heatmap"""
        heatmap = analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Test Heatmap",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )

        success = analytics_engine.add_heatmap_data(
            heatmap_id=heatmap.heatmap_id,
            h3_index="8928308280fffff",
            value=15.5,
            incident_count=10,
            tenant_id="tenant-001",
        )
        assert success is True

    def test_get_heatmaps_for_region(self, analytics_engine):
        """Test getting heatmaps for a region"""
        analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Heatmap 1",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )
        analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.VIOLENCE,
            name="Heatmap 2",
            region_codes=["CA-METRO", "CA-COUNTY"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )

        heatmaps = analytics_engine.get_heatmaps_for_region("CA-METRO")
        assert len(heatmaps) == 2


class TestCrossCityTrajectories:
    """Tests for cross-city trajectory tracking"""

    def test_create_trajectory(self, analytics_engine):
        """Test creating a trajectory"""
        trajectory = analytics_engine.create_trajectory(
            offender_id="offender-001",
            offender_name="John Doe",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )

        assert trajectory is not None
        assert trajectory.offender_id == "offender-001"
        assert trajectory.offender_name == "John Doe"

    def test_add_trajectory_point(self, analytics_engine):
        """Test adding a point to a trajectory"""
        trajectory = analytics_engine.create_trajectory(
            offender_id="offender-001",
            offender_name="John Doe",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )

        success = analytics_engine.add_trajectory_point(
            trajectory_id=trajectory.trajectory_id,
            latitude=34.0522,
            longitude=-118.2437,
            jurisdiction_code="CA-METRO",
            incident_type="burglary",
            incident_id="incident-001",
        )
        assert success is True

        updated = analytics_engine.get_trajectory(trajectory.trajectory_id)
        assert len(updated.points) == 1

    def test_get_trajectory(self, analytics_engine):
        """Test getting a trajectory by ID"""
        trajectory = analytics_engine.create_trajectory(
            offender_id="offender-001",
            offender_name="John Doe",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )

        retrieved = analytics_engine.get_trajectory(trajectory.trajectory_id)
        assert retrieved is not None
        assert retrieved.trajectory_id == trajectory.trajectory_id

    def test_get_trajectories_for_offender(self, analytics_engine):
        """Test getting trajectories for an offender"""
        analytics_engine.create_trajectory(
            offender_id="offender-001",
            offender_name="John Doe",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )

        trajectories = analytics_engine.get_trajectories_for_offender("offender-001")
        assert len(trajectories) == 1

    def test_get_trajectories_crossing_jurisdiction(self, analytics_engine):
        """Test getting trajectories crossing a jurisdiction"""
        trajectory = analytics_engine.create_trajectory(
            offender_id="offender-001",
            offender_name="John Doe",
            source_tenant_id="tenant-001",
            source_agency_name="Metro PD",
        )
        analytics_engine.add_trajectory_point(
            trajectory_id=trajectory.trajectory_id,
            latitude=34.0522,
            longitude=-118.2437,
            jurisdiction_code="CA-METRO",
            incident_type="burglary",
        )
        analytics_engine.add_trajectory_point(
            trajectory_id=trajectory.trajectory_id,
            latitude=34.1000,
            longitude=-118.3000,
            jurisdiction_code="CA-COUNTY",
            incident_type="theft",
        )

        trajectories = analytics_engine.get_trajectories_crossing_jurisdiction(
            "CA-COUNTY"
        )
        assert len(trajectories) == 1


class TestRegionalClusters:
    """Tests for regional crime cluster management"""

    def test_create_cluster(self, analytics_engine):
        """Test creating a cluster"""
        cluster = analytics_engine.create_cluster(
            cluster_type=ClusterType.EMERGING,
            name="Downtown Burglary Cluster",
            crime_type="burglary",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=1000,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        assert cluster is not None
        assert cluster.cluster_type == ClusterType.EMERGING
        assert cluster.name == "Downtown Burglary Cluster"

    def test_create_cluster_types(self, analytics_engine):
        """Test creating different cluster types"""
        types = [
            ClusterType.EMERGING,
            ClusterType.ACTIVE,
            ClusterType.DECLINING,
            ClusterType.DORMANT,
            ClusterType.SEASONAL,
            ClusterType.PERSISTENT,
        ]

        for i, cluster_type in enumerate(types):
            cluster = analytics_engine.create_cluster(
                cluster_type=cluster_type,
                name=f"Cluster {i}",
                crime_type="theft",
                center_latitude=34.0522 + i * 0.01,
                center_longitude=-118.2437,
                radius_meters=500,
                region_codes=["CA-METRO"],
                tenant_ids=["tenant-001"],
            )
            assert cluster is not None
            assert cluster.cluster_type == cluster_type

    def test_get_cluster(self, analytics_engine):
        """Test getting a cluster by ID"""
        cluster = analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Test Cluster",
            crime_type="theft",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        retrieved = analytics_engine.get_cluster(cluster.cluster_id)
        assert retrieved is not None
        assert retrieved.cluster_id == cluster.cluster_id

    def test_update_cluster_stats(self, analytics_engine):
        """Test updating cluster statistics"""
        cluster = analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Test Cluster",
            crime_type="theft",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        success = analytics_engine.update_cluster_stats(
            cluster_id=cluster.cluster_id,
            incident_count=25,
            trend_direction="increasing",
            trend_percentage=15.5,
        )
        assert success is True

    def test_get_active_clusters(self, analytics_engine):
        """Test getting active clusters"""
        analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Active Cluster",
            crime_type="theft",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )
        analytics_engine.create_cluster(
            cluster_type=ClusterType.DORMANT,
            name="Dormant Cluster",
            crime_type="burglary",
            center_latitude=34.0600,
            center_longitude=-118.2500,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        active = analytics_engine.get_active_clusters()
        assert len(active) == 1
        assert active[0].cluster_type == ClusterType.ACTIVE

    def test_get_clusters_for_region(self, analytics_engine):
        """Test getting clusters for a region"""
        analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Cluster 1",
            crime_type="theft",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )
        analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Cluster 2",
            crime_type="burglary",
            center_latitude=34.0600,
            center_longitude=-118.2500,
            radius_meters=500,
            region_codes=["CA-COUNTY"],
            tenant_ids=["tenant-002"],
        )

        clusters = analytics_engine.get_clusters_for_region("CA-METRO")
        assert len(clusters) == 1


class TestFederatedRiskMaps:
    """Tests for federated risk map management"""

    def test_create_risk_map(self, analytics_engine):
        """Test creating a risk map"""
        risk_map = analytics_engine.create_risk_map(
            name="Regional Risk Map",
            region_codes=["CA-METRO", "CA-COUNTY"],
            tenant_ids=["tenant-001", "tenant-002"],
        )

        assert risk_map is not None
        assert risk_map.name == "Regional Risk Map"
        assert "CA-METRO" in risk_map.region_codes

    def test_add_risk_data(self, analytics_engine):
        """Test adding risk data to a map"""
        risk_map = analytics_engine.create_risk_map(
            name="Test Risk Map",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        success = analytics_engine.add_risk_data(
            risk_map_id=risk_map.risk_map_id,
            h3_index="8928308280fffff",
            risk_level=RiskLevel.HIGH,
            risk_score=75.5,
            contributing_factors=["high_crime_rate", "gang_activity"],
        )
        assert success is True

    def test_get_risk_map(self, analytics_engine):
        """Test getting a risk map by ID"""
        risk_map = analytics_engine.create_risk_map(
            name="Test Risk Map",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        retrieved = analytics_engine.get_risk_map(risk_map.risk_map_id)
        assert retrieved is not None
        assert retrieved.risk_map_id == risk_map.risk_map_id

    def test_get_risk_at_location(self, analytics_engine):
        """Test getting risk at a specific location"""
        risk_map = analytics_engine.create_risk_map(
            name="Test Risk Map",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )
        analytics_engine.add_risk_data(
            risk_map_id=risk_map.risk_map_id,
            h3_index="8928308280fffff",
            risk_level=RiskLevel.HIGH,
            risk_score=75.5,
        )

        risk = analytics_engine.get_risk_at_location(
            risk_map_id=risk_map.risk_map_id,
            latitude=34.0522,
            longitude=-118.2437,
        )
        assert risk is not None


class TestAnalyticsQueries:
    """Tests for analytics queries"""

    def test_query_analytics(self, analytics_engine):
        """Test querying analytics"""
        analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Test Heatmap",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )

        results = analytics_engine.query_analytics(
            query_type="heatmaps",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )
        assert results is not None


class TestMetrics:
    """Tests for analytics metrics"""

    def test_get_metrics(self, analytics_engine):
        """Test getting analytics metrics"""
        analytics_engine.create_regional_heatmap(
            heatmap_type=HeatmapType.CRIME,
            name="Test Heatmap",
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
            time_range_start=datetime.utcnow() - timedelta(days=30),
            time_range_end=datetime.utcnow(),
        )
        analytics_engine.create_cluster(
            cluster_type=ClusterType.ACTIVE,
            name="Test Cluster",
            crime_type="theft",
            center_latitude=34.0522,
            center_longitude=-118.2437,
            radius_meters=500,
            region_codes=["CA-METRO"],
            tenant_ids=["tenant-001"],
        )

        metrics = analytics_engine.get_metrics()
        assert metrics["total_heatmaps"] == 1
        assert metrics["total_clusters"] == 1
