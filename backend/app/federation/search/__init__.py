"""
G3TI RTCC-UIP Federated Search Engine
Phase 10: Cross-agency search with parallel execution and result merging
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class SearchEntityType(str, Enum):
    """Types of entities that can be searched"""
    PERSON = "person"
    VEHICLE = "vehicle"
    ADDRESS = "address"
    FIREARM = "firearm"
    PHONE_NUMBER = "phone_number"
    REPORT = "report"
    CAD_EVENT = "cad_event"
    BOLO = "bolo"
    HOTSHEET = "hotsheet"
    INCIDENT = "incident"


class SearchSource(str, Enum):
    """Sources for federated search"""
    LOCAL_ELASTICSEARCH = "local_elasticsearch"
    LOCAL_NEO4J = "local_neo4j"
    PARTNER_AGENCY = "partner_agency"
    FEDERAL_DATABASE = "federal_database"


class PrivacyMaskingLevel(str, Enum):
    """Privacy masking levels for search results"""
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


class SearchResult:
    """Individual search result from a source"""

    def __init__(
        self,
        result_id: str,
        entity_type: SearchEntityType,
        source: SearchSource,
        source_agency: str,
        data: dict[str, Any],
        confidence_score: float,
        correlation_hits: list[str],
        masked_fields: list[str],
    ):
        self.id = result_id
        self.entity_type = entity_type
        self.source = source
        self.source_agency = source_agency
        self.data = data
        self.confidence_score = confidence_score
        self.correlation_hits = correlation_hits
        self.masked_fields = masked_fields
        self.timestamp = datetime.utcnow()


class SearchQuery:
    """Federated search query"""

    def __init__(
        self,
        query_id: str,
        requesting_user: str,
        requesting_agency: str,
        entity_type: SearchEntityType,
        search_params: dict[str, Any],
        target_sources: list[SearchSource],
        target_agencies: list[str],
        include_correlations: bool = True,
    ):
        self.id = query_id
        self.requesting_user = requesting_user
        self.requesting_agency = requesting_agency
        self.entity_type = entity_type
        self.search_params = search_params
        self.target_sources = target_sources
        self.target_agencies = target_agencies
        self.include_correlations = include_correlations
        self.created_at = datetime.utcnow()
        self.completed_at: datetime | None = None
        self.status = "pending"
        self.results: list[SearchResult] = []
        self.total_results = 0
        self.execution_time_ms = 0


class SearchAdapter:
    """Base adapter for search sources"""

    def __init__(self, source: SearchSource, agency_id: str):
        self.source = source
        self.agency_id = agency_id

    async def search(
        self,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Execute search - to be implemented by subclasses"""
        raise NotImplementedError


class ElasticsearchAdapter(SearchAdapter):
    """Adapter for local Elasticsearch searches"""

    def __init__(self, agency_id: str = "local"):
        super().__init__(SearchSource.LOCAL_ELASTICSEARCH, agency_id)
        self.index_mappings = {
            SearchEntityType.PERSON: "persons",
            SearchEntityType.VEHICLE: "vehicles",
            SearchEntityType.ADDRESS: "addresses",
            SearchEntityType.FIREARM: "firearms",
            SearchEntityType.PHONE_NUMBER: "phone_numbers",
            SearchEntityType.REPORT: "reports",
            SearchEntityType.CAD_EVENT: "cad_events",
            SearchEntityType.BOLO: "bolos",
            SearchEntityType.HOTSHEET: "hotsheets",
            SearchEntityType.INCIDENT: "incidents",
        }

    async def search(
        self,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Execute Elasticsearch search"""
        # In production, this would query actual Elasticsearch
        # For now, return simulated results
        results = []

        # Simulate search results based on entity type
        if entity_type == SearchEntityType.PERSON:
            results = await self._search_persons(params)
        elif entity_type == SearchEntityType.VEHICLE:
            results = await self._search_vehicles(params)
        elif entity_type == SearchEntityType.ADDRESS:
            results = await self._search_addresses(params)
        elif entity_type == SearchEntityType.BOLO:
            results = await self._search_bolos(params)

        return results

    async def _search_persons(self, params: dict[str, Any]) -> list[SearchResult]:
        """Search persons index"""
        # Simulated search
        return []

    async def _search_vehicles(self, params: dict[str, Any]) -> list[SearchResult]:
        """Search vehicles index"""
        return []

    async def _search_addresses(self, params: dict[str, Any]) -> list[SearchResult]:
        """Search addresses index"""
        return []

    async def _search_bolos(self, params: dict[str, Any]) -> list[SearchResult]:
        """Search BOLOs index"""
        return []


class Neo4jAdapter(SearchAdapter):
    """Adapter for Neo4j graph database searches"""

    def __init__(self, agency_id: str = "local"):
        super().__init__(SearchSource.LOCAL_NEO4J, agency_id)

    async def search(
        self,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Execute Neo4j graph search with entity resolution"""
        # In production, this would query actual Neo4j
        results = []

        # Graph-based entity resolution
        if "resolve_entities" in params and params["resolve_entities"]:
            results = await self._resolve_entities(entity_type, params)

        return results

    async def _resolve_entities(
        self,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Resolve entities using graph relationships"""
        # Simulated entity resolution
        return []


class PartnerAgencyAdapter(SearchAdapter):
    """Adapter for partner agency searches"""

    def __init__(self, agency_id: str, api_endpoint: str, access_token: str):
        super().__init__(SearchSource.PARTNER_AGENCY, agency_id)
        self.api_endpoint = api_endpoint
        self.access_token = access_token
        self.timeout = 30

    async def search(
        self,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Execute search against partner agency API"""
        # In production, this would make HTTP requests to partner API
        # For now, return simulated results
        return []


class PrivacyMaskingEngine:
    """Engine for applying privacy masking to search results"""

    def __init__(self):
        self.masking_rules: dict[str, dict[str, PrivacyMaskingLevel]] = {}
        self.sensitive_fields = {
            SearchEntityType.PERSON: [
                "ssn", "social_security", "date_of_birth", "dob",
                "drivers_license", "dl_number", "home_address",
                "phone_number", "email", "financial_info",
            ],
            SearchEntityType.VEHICLE: [
                "vin", "registration_number", "owner_ssn",
                "owner_address", "insurance_policy",
            ],
            SearchEntityType.ADDRESS: [
                "resident_names", "resident_ssns", "utility_accounts",
            ],
        }

    def register_masking_rule(
        self,
        agency_id: str,
        field: str,
        level: PrivacyMaskingLevel,
    ) -> None:
        """Register a masking rule for an agency"""
        if agency_id not in self.masking_rules:
            self.masking_rules[agency_id] = {}
        self.masking_rules[agency_id][field] = level

    def apply_masking(
        self,
        result: SearchResult,
        requesting_agency: str,
    ) -> SearchResult:
        """Apply privacy masking to a search result"""
        rules = self.masking_rules.get(result.source_agency, {})
        sensitive = self.sensitive_fields.get(result.entity_type, [])

        masked_data = result.data.copy()
        masked_fields = []

        for field in sensitive:
            if field in masked_data:
                level = rules.get(field, PrivacyMaskingLevel.PARTIAL)
                if level == PrivacyMaskingLevel.FULL:
                    masked_data[field] = "[REDACTED]"
                    masked_fields.append(field)
                elif level == PrivacyMaskingLevel.PARTIAL:
                    masked_data[field] = self._partial_mask(masked_data[field])
                    masked_fields.append(field)

        result.data = masked_data
        result.masked_fields = masked_fields
        return result

    def _partial_mask(self, value: Any) -> str:
        """Apply partial masking to a value"""
        if isinstance(value, str):
            if len(value) <= 4:
                return "****"
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        return str(value)


class ResultMerger:
    """Merges and ranks results from multiple sources"""

    def __init__(self):
        self.deduplication_fields = {
            SearchEntityType.PERSON: ["name", "date_of_birth", "ssn"],
            SearchEntityType.VEHICLE: ["plate", "vin"],
            SearchEntityType.ADDRESS: ["street_address", "city", "state", "zip"],
        }

    def merge_results(
        self,
        results: list[SearchResult],
        entity_type: SearchEntityType,
    ) -> list[SearchResult]:
        """Merge and deduplicate results from multiple sources"""
        if not results:
            return []

        # Group by potential duplicates
        groups: dict[str, list[SearchResult]] = {}
        for result in results:
            key = self._generate_dedup_key(result, entity_type)
            if key not in groups:
                groups[key] = []
            groups[key].append(result)

        # Merge each group
        merged = []
        for group in groups.values():
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged.append(self._merge_group(group))

        return merged

    def _generate_dedup_key(
        self,
        result: SearchResult,
        entity_type: SearchEntityType,
    ) -> str:
        """Generate a deduplication key for a result"""
        fields = self.deduplication_fields.get(entity_type, [])
        key_parts = []
        for field in fields:
            if field in result.data:
                key_parts.append(str(result.data[field]).lower())
        return "|".join(key_parts) if key_parts else result.id

    def _merge_group(self, group: list[SearchResult]) -> SearchResult:
        """Merge a group of duplicate results"""
        # Use the result with highest confidence as base
        base = max(group, key=lambda r: r.confidence_score)

        # Merge correlation hits from all results
        all_correlations = set()
        for result in group:
            all_correlations.update(result.correlation_hits)
        base.correlation_hits = list(all_correlations)

        # Boost confidence for results found in multiple sources
        base.confidence_score = min(
            1.0,
            base.confidence_score + (len(group) - 1) * 0.1
        )

        return base

    def rank_results(
        self,
        results: list[SearchResult],
        sort_by: str = "confidence",
    ) -> list[SearchResult]:
        """Rank results by specified criteria"""
        if sort_by == "confidence":
            return sorted(results, key=lambda r: r.confidence_score, reverse=True)
        elif sort_by == "timestamp":
            return sorted(results, key=lambda r: r.timestamp, reverse=True)
        elif sort_by == "correlations":
            return sorted(
                results,
                key=lambda r: len(r.correlation_hits),
                reverse=True
            )
        return results


class FederatedSearchEngine:
    """Main federated search engine"""

    def __init__(self):
        self.adapters: dict[str, SearchAdapter] = {}
        self.masking_engine = PrivacyMaskingEngine()
        self.result_merger = ResultMerger()
        self.queries: dict[str, SearchQuery] = {}
        self.search_history: list[dict[str, Any]] = []

        # Initialize local adapters
        self.adapters["local_es"] = ElasticsearchAdapter()
        self.adapters["local_neo4j"] = Neo4jAdapter()

    def register_adapter(
        self,
        adapter_id: str,
        adapter: SearchAdapter,
    ) -> None:
        """Register a search adapter"""
        self.adapters[adapter_id] = adapter

    def register_partner_agency(
        self,
        agency_id: str,
        api_endpoint: str,
        access_token: str,
    ) -> None:
        """Register a partner agency for federated search"""
        adapter = PartnerAgencyAdapter(agency_id, api_endpoint, access_token)
        self.adapters[f"partner_{agency_id}"] = adapter

    async def search(
        self,
        requesting_user: str,
        requesting_agency: str,
        entity_type: SearchEntityType,
        search_params: dict[str, Any],
        target_sources: list[SearchSource] | None = None,
        target_agencies: list[str] | None = None,
        include_correlations: bool = True,
        apply_masking: bool = True,
        limit: int = 100,
    ) -> SearchQuery:
        """Execute a federated search across multiple sources"""
        query_id = str(uuid4())
        start_time = datetime.utcnow()

        # Default to all sources if not specified
        if not target_sources:
            target_sources = [
                SearchSource.LOCAL_ELASTICSEARCH,
                SearchSource.LOCAL_NEO4J,
                SearchSource.PARTNER_AGENCY,
            ]

        # Default to all registered partner agencies
        if not target_agencies:
            target_agencies = [
                aid.replace("partner_", "")
                for aid in self.adapters.keys()
                if aid.startswith("partner_")
            ]

        query = SearchQuery(
            query_id=query_id,
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=entity_type,
            search_params=search_params,
            target_sources=target_sources,
            target_agencies=target_agencies,
            include_correlations=include_correlations,
        )
        self.queries[query_id] = query

        # Execute searches in parallel
        search_tasks = []

        # Local Elasticsearch
        if SearchSource.LOCAL_ELASTICSEARCH in target_sources:
            adapter = self.adapters.get("local_es")
            if adapter:
                search_tasks.append(
                    self._execute_adapter_search(adapter, entity_type, search_params)
                )

        # Local Neo4j
        if SearchSource.LOCAL_NEO4J in target_sources:
            adapter = self.adapters.get("local_neo4j")
            if adapter:
                search_tasks.append(
                    self._execute_adapter_search(adapter, entity_type, search_params)
                )

        # Partner agencies
        if SearchSource.PARTNER_AGENCY in target_sources:
            for agency_id in target_agencies:
                adapter = self.adapters.get(f"partner_{agency_id}")
                if adapter:
                    search_tasks.append(
                        self._execute_adapter_search(
                            adapter, entity_type, search_params
                        )
                    )

        # Wait for all searches to complete
        all_results = []
        if search_tasks:
            task_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            for result in task_results:
                if isinstance(result, list):
                    all_results.extend(result)

        # Merge and deduplicate results
        merged_results = self.result_merger.merge_results(all_results, entity_type)

        # Apply privacy masking
        if apply_masking:
            merged_results = [
                self.masking_engine.apply_masking(r, requesting_agency)
                for r in merged_results
            ]

        # Rank results
        ranked_results = self.result_merger.rank_results(merged_results)

        # Apply limit
        query.results = ranked_results[:limit]
        query.total_results = len(ranked_results)
        query.status = "completed"
        query.completed_at = datetime.utcnow()
        query.execution_time_ms = int(
            (query.completed_at - start_time).total_seconds() * 1000
        )

        # Log search history
        self._log_search(query)

        return query

    async def _execute_adapter_search(
        self,
        adapter: SearchAdapter,
        entity_type: SearchEntityType,
        params: dict[str, Any],
    ) -> list[SearchResult]:
        """Execute search on a single adapter with error handling"""
        try:
            return await adapter.search(entity_type, params)
        except Exception as e:
            # Log error but don't fail the entire search
            print(f"Search error on {adapter.source}: {e}")
            return []

    async def search_person(
        self,
        requesting_user: str,
        requesting_agency: str,
        name: str | None = None,
        date_of_birth: str | None = None,
        ssn: str | None = None,
        drivers_license: str | None = None,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for persons across all sources"""
        params = {
            "name": name,
            "date_of_birth": date_of_birth,
            "ssn": ssn,
            "drivers_license": drivers_license,
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.PERSON,
            search_params=params,
        )

    async def search_vehicle(
        self,
        requesting_user: str,
        requesting_agency: str,
        plate: str | None = None,
        vin: str | None = None,
        make: str | None = None,
        model: str | None = None,
        color: str | None = None,
        year: int | None = None,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for vehicles across all sources"""
        params = {
            "plate": plate,
            "vin": vin,
            "make": make,
            "model": model,
            "color": color,
            "year": year,
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.VEHICLE,
            search_params=params,
        )

    async def search_address(
        self,
        requesting_user: str,
        requesting_agency: str,
        street_address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for addresses across all sources"""
        params = {
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.ADDRESS,
            search_params=params,
        )

    async def search_bolo(
        self,
        requesting_user: str,
        requesting_agency: str,
        keywords: str | None = None,
        bolo_type: str | None = None,
        active_only: bool = True,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for BOLOs across all sources"""
        params = {
            "keywords": keywords,
            "bolo_type": bolo_type,
            "active_only": active_only,
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.BOLO,
            search_params=params,
        )

    async def search_firearm(
        self,
        requesting_user: str,
        requesting_agency: str,
        serial_number: str | None = None,
        make: str | None = None,
        model: str | None = None,
        caliber: str | None = None,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for firearms across all sources"""
        params = {
            "serial_number": serial_number,
            "make": make,
            "model": model,
            "caliber": caliber,
            **kwargs,
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.FIREARM,
            search_params=params,
        )

    async def search_phone(
        self,
        requesting_user: str,
        requesting_agency: str,
        phone_number: str,
        **kwargs: Any,
    ) -> SearchQuery:
        """Search for phone numbers across all sources"""
        params = {
            "phone_number": phone_number,
            **kwargs,
        }

        return await self.search(
            requesting_user=requesting_user,
            requesting_agency=requesting_agency,
            entity_type=SearchEntityType.PHONE_NUMBER,
            search_params=params,
        )

    def _log_search(self, query: SearchQuery) -> None:
        """Log search to history"""
        self.search_history.append({
            "query_id": query.id,
            "requesting_user": query.requesting_user,
            "requesting_agency": query.requesting_agency,
            "entity_type": query.entity_type.value,
            "result_count": query.total_results,
            "execution_time_ms": query.execution_time_ms,
            "timestamp": query.created_at.isoformat(),
        })

    def get_search_history(
        self,
        requesting_agency: str | None = None,
        entity_type: SearchEntityType | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get search history with optional filtering"""
        history = self.search_history.copy()

        if requesting_agency:
            history = [
                h for h in history
                if h["requesting_agency"] == requesting_agency
            ]
        if entity_type:
            history = [
                h for h in history
                if h["entity_type"] == entity_type.value
            ]

        return history[-limit:]


# Create singleton instance
federated_search_engine = FederatedSearchEngine()
