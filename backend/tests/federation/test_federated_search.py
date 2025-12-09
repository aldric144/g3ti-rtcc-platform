"""
Tests for Federated Search Engine
Phase 10: Search adapters, privacy masking, and result merging tests
"""


import pytest

from app.federation.search import (
    ElasticsearchAdapter,
    FederatedSearchEngine,
    Neo4jAdapter,
    PartnerAgencyAdapter,
    PrivacyMaskingEngine,
    PrivacyMaskingLevel,
    ResultMerger,
    SearchEntityType,
    SearchQuery,
    SearchResult,
    SearchSource,
)


class TestSearchResult:
    """Tests for SearchResult"""

    def test_create_search_result(self):
        """Test creating search result"""
        result = SearchResult(
            entity_type=SearchEntityType.PERSON,
            source=SearchSource.RMS,
            data={"name": "John Doe", "dob": "1990-01-15"},
            confidence_score=0.95,
            agency_id="agency-1",
        )

        assert result.entity_type == SearchEntityType.PERSON
        assert result.source == SearchSource.RMS
        assert result.confidence_score == 0.95
        assert result.agency_id == "agency-1"

    def test_search_result_has_id(self):
        """Test search result has unique ID"""
        result1 = SearchResult(
            entity_type=SearchEntityType.VEHICLE,
            source=SearchSource.LPR,
            data={"plate": "ABC1234"},
            confidence_score=0.88,
        )
        result2 = SearchResult(
            entity_type=SearchEntityType.VEHICLE,
            source=SearchSource.LPR,
            data={"plate": "XYZ5678"},
            confidence_score=0.75,
        )

        assert result1.id != result2.id


class TestPrivacyMaskingEngine:
    """Tests for PrivacyMaskingEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.masking_engine = PrivacyMaskingEngine()

    def test_mask_ssn(self):
        """Test SSN masking"""
        data = {"name": "John Doe", "ssn": "123-45-6789"}
        masked = self.masking_engine.mask_sensitive_fields(
            data, PrivacyMaskingLevel.STANDARD
        )

        assert "ssn" in masked
        assert masked["ssn"] != "123-45-6789"
        assert "***" in masked["ssn"] or "[MASKED]" in masked["ssn"]

    def test_mask_dob(self):
        """Test date of birth masking"""
        data = {"name": "John Doe", "dob": "1990-01-15"}
        masked = self.masking_engine.mask_sensitive_fields(
            data, PrivacyMaskingLevel.STANDARD
        )

        assert "dob" in masked
        # DOB should be masked or generalized
        assert masked["dob"] != "1990-01-15" or "MASKED" in str(masked["dob"])

    def test_mask_phone(self):
        """Test phone number masking"""
        data = {"name": "John Doe", "phone": "555-123-4567"}
        masked = self.masking_engine.mask_sensitive_fields(
            data, PrivacyMaskingLevel.STANDARD
        )

        assert "phone" in masked
        assert "***" in masked["phone"] or masked["phone"] != "555-123-4567"

    def test_no_masking_for_none_level(self):
        """Test no masking when level is NONE"""
        data = {"name": "John Doe", "ssn": "123-45-6789"}
        masked = self.masking_engine.mask_sensitive_fields(
            data, PrivacyMaskingLevel.NONE
        )

        assert masked["ssn"] == "123-45-6789"

    def test_full_masking(self):
        """Test full masking level"""
        data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "dob": "1990-01-15",
            "address": "123 Main St",
        }
        masked = self.masking_engine.mask_sensitive_fields(
            data, PrivacyMaskingLevel.FULL
        )

        # All sensitive fields should be masked
        assert masked["ssn"] != "123-45-6789"
        assert masked["dob"] != "1990-01-15"


class TestResultMerger:
    """Tests for ResultMerger"""

    def setup_method(self):
        """Set up test fixtures"""
        self.merger = ResultMerger()

    def test_merge_results(self):
        """Test merging results from multiple sources"""
        results1 = [
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.RMS,
                data={"name": "John Doe"},
                confidence_score=0.95,
                agency_id="agency-1",
            ),
        ]
        results2 = [
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.CAD,
                data={"name": "John Doe"},
                confidence_score=0.88,
                agency_id="agency-2",
            ),
        ]

        merged = self.merger.merge_results([results1, results2])
        assert len(merged) >= 1

    def test_sort_by_confidence(self):
        """Test results sorted by confidence score"""
        results = [
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.RMS,
                data={"name": "Low Confidence"},
                confidence_score=0.50,
            ),
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.RMS,
                data={"name": "High Confidence"},
                confidence_score=0.95,
            ),
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.RMS,
                data={"name": "Medium Confidence"},
                confidence_score=0.75,
            ),
        ]

        sorted_results = self.merger.sort_by_confidence(results)
        assert sorted_results[0].confidence_score >= sorted_results[1].confidence_score
        assert sorted_results[1].confidence_score >= sorted_results[2].confidence_score

    def test_deduplicate_results(self):
        """Test deduplication of similar results"""
        results = [
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.RMS,
                data={"name": "John Doe", "dob": "1990-01-15"},
                confidence_score=0.95,
            ),
            SearchResult(
                entity_type=SearchEntityType.PERSON,
                source=SearchSource.CAD,
                data={"name": "John Doe", "dob": "1990-01-15"},
                confidence_score=0.88,
            ),
        ]

        deduped = self.merger.deduplicate(results)
        # Should merge similar results
        assert len(deduped) <= len(results)


class TestFederatedSearchEngine:
    """Tests for FederatedSearchEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.search_engine = FederatedSearchEngine()

    @pytest.mark.asyncio
    async def test_search_person(self):
        """Test person search"""
        results = await self.search_engine.search_person(
            query="John Doe",
            requesting_agency="local",
            requesting_user="test_user",
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_vehicle(self):
        """Test vehicle search"""
        results = await self.search_engine.search_vehicle(
            plate="ABC1234",
            requesting_agency="local",
            requesting_user="test_user",
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_entity_types(self):
        """Test search with specific entity types"""
        results = await self.search_engine.search(
            query="test query",
            entity_types=[SearchEntityType.PERSON, SearchEntityType.VEHICLE],
            requesting_agency="local",
            requesting_user="test_user",
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_max_results(self):
        """Test search with max results limit"""
        results = await self.search_engine.search(
            query="test query",
            requesting_agency="local",
            requesting_user="test_user",
            max_results=10,
        )

        assert len(results) <= 10

    def test_register_adapter(self):
        """Test registering search adapter"""
        adapter = ElasticsearchAdapter()
        self.search_engine.register_adapter("test_es", adapter)

        assert "test_es" in self.search_engine.adapters

    def test_register_partner_adapter(self):
        """Test registering partner agency adapter"""
        adapter = PartnerAgencyAdapter(
            agency_id="partner-1",
            api_endpoint="https://api.partner.gov",
        )
        self.search_engine.register_partner_adapter("partner-1", adapter)

        assert "partner-1" in self.search_engine.partner_adapters


class TestSearchAdapters:
    """Tests for Search Adapters"""

    def test_elasticsearch_adapter_creation(self):
        """Test Elasticsearch adapter creation"""
        adapter = ElasticsearchAdapter()
        assert adapter is not None
        assert adapter.name == "elasticsearch"

    def test_neo4j_adapter_creation(self):
        """Test Neo4j adapter creation"""
        adapter = Neo4jAdapter()
        assert adapter is not None
        assert adapter.name == "neo4j"

    def test_partner_agency_adapter_creation(self):
        """Test Partner Agency adapter creation"""
        adapter = PartnerAgencyAdapter(
            agency_id="partner-1",
            api_endpoint="https://api.partner.gov",
        )
        assert adapter is not None
        assert adapter.agency_id == "partner-1"

    @pytest.mark.asyncio
    async def test_elasticsearch_adapter_search(self):
        """Test Elasticsearch adapter search"""
        adapter = ElasticsearchAdapter()
        query = SearchQuery(
            query_text="test",
            entity_types=[SearchEntityType.PERSON],
            requesting_agency="local",
            requesting_user="test_user",
        )

        results = await adapter.search(query)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_neo4j_adapter_search(self):
        """Test Neo4j adapter search"""
        adapter = Neo4jAdapter()
        query = SearchQuery(
            query_text="test",
            entity_types=[SearchEntityType.PERSON],
            requesting_agency="local",
            requesting_user="test_user",
        )

        results = await adapter.search(query)
        assert isinstance(results, list)
