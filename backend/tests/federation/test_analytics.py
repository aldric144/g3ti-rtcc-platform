"""
Tests for Multi-Agency Analytics
Phase 10: Cross-jurisdiction analytics, pattern detection, and entity correlation tests
"""


from app.federation.analytics import (
    AnalyticsQuery,
    AnalyticsTimeRange,
    CrossJurisdictionHeatmap,
    DetectedPattern,
    EntityCorrelation,
    HotspotComparison,
    MultiAgencyAnalyticsEngine,
    PatternType,
    RiskLevel,
    SharedRiskScore,
)


class TestCrossJurisdictionHeatmap:
    """Tests for CrossJurisdictionHeatmap"""

    def test_create_heatmap(self):
        """Test creating heatmap"""
        heatmap = CrossJurisdictionHeatmap(
            name="Regional Crime Heatmap",
            participating_agencies=["agency-1", "agency-2", "agency-3"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
            bounds={"min_lat": 37.0, "max_lat": 38.0, "min_lon": -122.5, "max_lon": -121.5},
        )

        assert heatmap.name == "Regional Crime Heatmap"
        assert len(heatmap.participating_agencies) == 3
        assert heatmap.time_range == AnalyticsTimeRange.LAST_30_DAYS


class TestDetectedPattern:
    """Tests for DetectedPattern"""

    def test_create_pattern(self):
        """Test creating detected pattern"""
        pattern = DetectedPattern(
            pattern_type=PatternType.CRIME_SERIES,
            name="Burglary Series",
            description="Series of residential burglaries",
            confidence_score=0.85,
            affected_agencies=["agency-1", "agency-2"],
            affected_areas=["Downtown", "Westside"],
            risk_level=RiskLevel.HIGH,
        )

        assert pattern.pattern_type == PatternType.CRIME_SERIES
        assert pattern.confidence_score == 0.85
        assert pattern.risk_level == RiskLevel.HIGH


class TestMultiAgencyAnalyticsEngine:
    """Tests for MultiAgencyAnalyticsEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = MultiAgencyAnalyticsEngine()

    def test_generate_cross_jurisdiction_heatmap(self):
        """Test generating cross-jurisdiction heatmap"""
        heatmap = self.engine.generate_cross_jurisdiction_heatmap(
            name="Test Heatmap",
            participating_agencies=["agency-1", "agency-2"],
            time_range=AnalyticsTimeRange.LAST_7_DAYS,
        )

        assert heatmap is not None
        assert heatmap.name == "Test Heatmap"
        assert heatmap.id in self.engine.heatmaps

    def test_detect_regional_patterns(self):
        """Test detecting regional patterns"""
        patterns = self.engine.detect_regional_patterns(
            participating_agencies=["agency-1", "agency-2"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
            min_confidence=0.7,
        )

        assert isinstance(patterns, list)

    def test_detect_patterns_with_type_filter(self):
        """Test detecting patterns with type filter"""
        patterns = self.engine.detect_regional_patterns(
            participating_agencies=["agency-1", "agency-2"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
            pattern_types=[PatternType.CRIME_SERIES, PatternType.HOTSPOT],
            min_confidence=0.5,
        )

        assert isinstance(patterns, list)

    def test_correlate_entities(self):
        """Test correlating entities across agencies"""
        correlations = self.engine.correlate_entities(
            entity_type="person",
            entity_ids=["person-1", "person-2"],
            participating_agencies=["agency-1", "agency-2"],
        )

        assert isinstance(correlations, list)

    def test_compare_hotspots(self):
        """Test comparing hotspots between agencies"""
        comparison = self.engine.compare_hotspots(
            agencies=["agency-1", "agency-2", "agency-3"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
        )

        assert comparison is not None
        assert comparison.id in self.engine.comparisons
        assert len(comparison.agencies) == 3

    def test_calculate_shared_risk_score(self):
        """Test calculating shared risk score"""
        risk_score = self.engine.calculate_shared_risk_score(
            entity_type="address",
            entity_id="address-123",
            participating_agencies=["agency-1", "agency-2"],
        )

        assert risk_score is not None
        assert risk_score.entity_type == "address"
        assert risk_score.entity_id == "address-123"
        assert 0 <= risk_score.overall_score <= 100

    def test_get_analytics_summary(self):
        """Test getting analytics summary for agency"""
        # Generate some data first
        self.engine.generate_cross_jurisdiction_heatmap(
            name="Test Heatmap",
            participating_agencies=["agency-1", "agency-2"],
            time_range=AnalyticsTimeRange.LAST_7_DAYS,
        )

        summary = self.engine.get_analytics_summary(
            agency_id="agency-1",
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
        )

        assert summary is not None
        assert "agency_id" in summary
        assert "heatmaps" in summary
        assert "patterns" in summary

    def test_execute_analytics_query(self):
        """Test executing analytics query"""
        query = AnalyticsQuery(
            query_type="heatmap",
            parameters={
                "name": "Query Heatmap",
                "time_range": "last_7_days",
            },
            participating_agencies=["agency-1", "agency-2"],
            requesting_agency="agency-1",
            requesting_user="analyst-1",
        )

        result = self.engine.execute_query(query)
        assert result is not None

    def test_get_trend_analysis(self):
        """Test getting trend analysis"""
        trends = self.engine.get_trend_analysis(
            participating_agencies=["agency-1", "agency-2"],
            metric="incidents",
            time_range=AnalyticsTimeRange.LAST_90_DAYS,
        )

        assert trends is not None
        assert "metric" in trends
        assert "data_points" in trends

    def test_get_cross_agency_statistics(self):
        """Test getting cross-agency statistics"""
        stats = self.engine.get_cross_agency_statistics(
            participating_agencies=["agency-1", "agency-2", "agency-3"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
        )

        assert stats is not None
        assert "total_incidents" in stats
        assert "by_agency" in stats

    def test_identify_cross_border_activity(self):
        """Test identifying cross-border activity"""
        activity = self.engine.identify_cross_border_activity(
            agencies=["agency-1", "agency-2"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
        )

        assert activity is not None
        assert "cross_border_incidents" in activity
        assert "shared_suspects" in activity


class TestEntityCorrelation:
    """Tests for EntityCorrelation"""

    def test_create_correlation(self):
        """Test creating entity correlation"""
        correlation = EntityCorrelation(
            entity_type="person",
            primary_entity_id="person-1",
            correlated_entities=[
                {"id": "person-2", "agency": "agency-2", "confidence": 0.9},
                {"id": "person-3", "agency": "agency-3", "confidence": 0.75},
            ],
            correlation_factors=["name_match", "dob_match", "address_proximity"],
            overall_confidence=0.85,
        )

        assert correlation.entity_type == "person"
        assert len(correlation.correlated_entities) == 2
        assert correlation.overall_confidence == 0.85


class TestSharedRiskScore:
    """Tests for SharedRiskScore"""

    def test_create_risk_score(self):
        """Test creating shared risk score"""
        risk_score = SharedRiskScore(
            entity_type="address",
            entity_id="address-123",
            participating_agencies=["agency-1", "agency-2"],
            overall_score=75.5,
            risk_level=RiskLevel.HIGH,
            contributing_factors=[
                {"factor": "repeat_calls", "weight": 0.3, "score": 80},
                {"factor": "violent_incidents", "weight": 0.4, "score": 70},
                {"factor": "known_offenders", "weight": 0.3, "score": 78},
            ],
        )

        assert risk_score.overall_score == 75.5
        assert risk_score.risk_level == RiskLevel.HIGH
        assert len(risk_score.contributing_factors) == 3


class TestHotspotComparison:
    """Tests for HotspotComparison"""

    def test_create_comparison(self):
        """Test creating hotspot comparison"""
        comparison = HotspotComparison(
            agencies=["agency-1", "agency-2", "agency-3"],
            time_range=AnalyticsTimeRange.LAST_30_DAYS,
            agency_hotspots={
                "agency-1": [{"lat": 37.5, "lon": -122.0, "intensity": 0.8}],
                "agency-2": [{"lat": 37.6, "lon": -122.1, "intensity": 0.7}],
            },
            shared_hotspots=[
                {"lat": 37.55, "lon": -122.05, "agencies": ["agency-1", "agency-2"]},
            ],
            correlation_matrix={
                "agency-1_agency-2": 0.75,
                "agency-1_agency-3": 0.45,
                "agency-2_agency-3": 0.60,
            },
        )

        assert len(comparison.agencies) == 3
        assert len(comparison.shared_hotspots) == 1
        assert comparison.correlation_matrix["agency-1_agency-2"] == 0.75
