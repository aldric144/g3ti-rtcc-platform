"""
NLP Module for Natural Language Query Interpretation.

This module provides LLM-based query interpretation capabilities for converting
natural language investigative queries into structured DSL queries that can be
executed against Neo4j and Elasticsearch.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Any

from app.ai_engine.models import (
    DSLQuery,
    EntityType,
    GeoLocation,
    TimeRange,
)
from app.ai_engine.pipelines import PipelineContext, PipelineStage
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)


class QueryInterpreter:
    """
    Interprets natural language queries into structured DSL.

    Uses pattern matching and NLP techniques to extract:
    - Entity types (vehicles, persons, incidents)
    - Time ranges (last 30 days, yesterday, etc.)
    - Locations (addresses, areas, coordinates)
    - Relationships (connected to, near, involved in)
    - Filters (plate numbers, names, case numbers)
    """

    ENTITY_PATTERNS = {
        EntityType.VEHICLE: [
            r"\bvehicles?\b",
            r"\bcars?\b",
            r"\btrucks?\b",
            r"\bplates?\b",
            r"\blpr\b",
            r"\blicense\s*plates?\b",
        ],
        EntityType.PERSON: [
            r"\bpersons?\b",
            r"\bpeople\b",
            r"\bsuspects?\b",
            r"\boffenders?\b",
            r"\bindividuals?\b",
            r"\bwitness(?:es)?\b",
            r"\bvictims?\b",
        ],
        EntityType.INCIDENT: [
            r"\bincidents?\b",
            r"\bcrimes?\b",
            r"\bevents?\b",
            r"\bcalls?\b",
            r"\bgunfire\b",
            r"\bshots?\b",
            r"\bshotspotter\b",
            r"\bshootings?\b",
        ],
        EntityType.ADDRESS: [
            r"\baddress(?:es)?\b",
            r"\blocations?\b",
            r"\bplaces?\b",
        ],
        EntityType.WEAPON: [
            r"\bweapons?\b",
            r"\bguns?\b",
            r"\bfirearms?\b",
            r"\bballistics?\b",
        ],
    }

    TIME_PATTERNS = {
        "last_hour": (r"\blast\s+hour\b", timedelta(hours=1)),
        "last_24_hours": (r"\blast\s+24\s+hours?\b", timedelta(hours=24)),
        "today": (r"\btoday\b", timedelta(days=1)),
        "yesterday": (r"\byesterday\b", timedelta(days=1)),
        "last_week": (r"\blast\s+week\b", timedelta(weeks=1)),
        "last_7_days": (r"\blast\s+7\s+days?\b", timedelta(days=7)),
        "last_30_days": (r"\blast\s+30\s+days?\b", timedelta(days=30)),
        "last_month": (r"\blast\s+month\b", timedelta(days=30)),
        "last_90_days": (r"\blast\s+90\s+days?\b", timedelta(days=90)),
        "last_year": (r"\blast\s+year\b", timedelta(days=365)),
    }

    RELATIONSHIP_PATTERNS = [
        (r"\bconnected\s+to\b", "CONNECTED_TO"),
        (r"\brelated\s+to\b", "RELATED_TO"),
        (r"\bassociated\s+with\b", "ASSOCIATED_WITH"),
        (r"\binvolved\s+in\b", "INVOLVED_IN"),
        (r"\bnear\b", "NEAR"),
        (r"\bat\b", "AT_LOCATION"),
        (r"\bwithin\b", "WITHIN_RADIUS"),
        (r"\blinked\s+to\b", "LINKED_TO"),
    ]

    QUERY_TYPE_PATTERNS = {
        "search": [r"\bshow\b", r"\bfind\b", r"\bsearch\b", r"\bget\b", r"\blist\b"],
        "analyze": [r"\banalyze\b", r"\banalysis\b", r"\bpattern\b"],
        "predict": [r"\bpredict\b", r"\bforecast\b", r"\blikely\b"],
        "correlate": [r"\bcorrelate\b", r"\bconnect\b", r"\blink\b", r"\brelationship\b"],
        "risk": [r"\brisk\b", r"\bthreat\b", r"\bdanger\b"],
        "anomaly": [r"\banomaly\b", r"\bunusual\b", r"\babnormal\b", r"\bsuspicious\b"],
    }

    def __init__(self) -> None:
        """Initialize the query interpreter."""
        self._compiled_patterns: dict[str, list[re.Pattern[str]]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            self._compiled_patterns[f"entity_{entity_type.value}"] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

        for time_key, (pattern, _) in self.TIME_PATTERNS.items():
            self._compiled_patterns[f"time_{time_key}"] = [
                re.compile(pattern, re.IGNORECASE)
            ]

        for query_type, patterns in self.QUERY_TYPE_PATTERNS.items():
            self._compiled_patterns[f"query_{query_type}"] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def interpret(self, query: str, role: str | None = None) -> DSLQuery:
        """
        Interpret a natural language query into structured DSL.

        Args:
            query: Natural language query string
            role: User role for access control

        Returns:
            Structured DSL query
        """
        logger.info("interpreting_query", query=query, role=role)

        query_type = self._extract_query_type(query)
        entities = self._extract_entities(query)
        time_range = self._extract_time_range(query)
        location = self._extract_location(query)
        filters = self._extract_filters(query)
        radius = self._extract_radius(query)

        dsl_query = DSLQuery(
            query_type=query_type,
            entities=entities,
            filters=filters,
            time_range=time_range,
            location=location,
            radius_meters=radius,
            limit=self._extract_limit(query),
            include_relationships=self._should_include_relationships(query),
            include_risk_scores=self._should_include_risk_scores(query),
        )

        logger.info(
            "query_interpreted",
            query_type=query_type,
            entity_count=len(entities),
            has_time_range=time_range is not None,
            has_location=location is not None,
        )

        return dsl_query

    def _extract_query_type(self, query: str) -> str:
        """Extract the query type from the query."""
        for query_type, patterns in self.QUERY_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return query_type
        return "search"

    def _extract_entities(self, query: str) -> list[dict[str, Any]]:
        """Extract entity references from the query."""
        entities = []

        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    entities.append(
                        {
                            "type": entity_type.value,
                            "filters": {},
                        }
                    )
                    break

        plate_match = re.search(
            r"\b([A-Z]{1,3}[\s-]?\d{1,4}[\s-]?[A-Z]{0,3})\b", query, re.IGNORECASE
        )
        if plate_match:
            entities.append(
                {
                    "type": EntityType.VEHICLE.value,
                    "filters": {"plate_number": plate_match.group(1).upper()},
                }
            )

        name_match = re.search(
            r"\bnamed?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", query
        )
        if name_match:
            entities.append(
                {
                    "type": EntityType.PERSON.value,
                    "filters": {"name": name_match.group(1)},
                }
            )

        return entities

    def _extract_time_range(self, query: str) -> TimeRange | None:
        """Extract time range from the query."""
        now = datetime.utcnow()

        for _time_key, (pattern, delta) in self.TIME_PATTERNS.items():
            if re.search(pattern, query, re.IGNORECASE):
                return TimeRange(start=now - delta, end=now)

        days_match = re.search(r"\blast\s+(\d+)\s+days?\b", query, re.IGNORECASE)
        if days_match:
            days = int(days_match.group(1))
            return TimeRange(start=now - timedelta(days=days), end=now)

        hours_match = re.search(r"\blast\s+(\d+)\s+hours?\b", query, re.IGNORECASE)
        if hours_match:
            hours = int(hours_match.group(1))
            return TimeRange(start=now - timedelta(hours=hours), end=now)

        return None

    def _extract_location(self, query: str) -> GeoLocation | None:
        """Extract location from the query."""
        near_match = re.search(
            r"\bnear\s+([A-Za-z0-9\s]+?)(?:\s+(?:within|in|during|over|last)|\.|$)",
            query,
            re.IGNORECASE,
        )
        if near_match:
            address = near_match.group(1).strip()
            return GeoLocation(
                latitude=0.0,
                longitude=0.0,
                address=address,
            )

        at_match = re.search(
            r"\bat\s+(\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Way|Ln|Lane))\b",
            query,
            re.IGNORECASE,
        )
        if at_match:
            address = at_match.group(1).strip()
            return GeoLocation(
                latitude=0.0,
                longitude=0.0,
                address=address,
            )

        return None

    def _extract_filters(self, query: str) -> dict[str, Any]:
        """Extract additional filters from the query."""
        filters: dict[str, Any] = {}

        case_match = re.search(r"\bcase\s*#?\s*(\d+)\b", query, re.IGNORECASE)
        if case_match:
            filters["case_number"] = case_match.group(1)

        incident_match = re.search(r"\bincident\s*#?\s*(\d+)\b", query, re.IGNORECASE)
        if incident_match:
            filters["incident_id"] = incident_match.group(1)

        if re.search(r"\bstolen\b", query, re.IGNORECASE):
            filters["is_stolen"] = True

        if re.search(r"\bwanted\b", query, re.IGNORECASE):
            filters["is_wanted"] = True

        if re.search(r"\bhigh[\s-]?risk\b", query, re.IGNORECASE):
            filters["risk_level"] = "high"

        return filters

    def _extract_radius(self, query: str) -> float | None:
        """Extract search radius from the query."""
        miles_match = re.search(r"(\d+(?:\.\d+)?)\s*miles?\b", query, re.IGNORECASE)
        if miles_match:
            return float(miles_match.group(1)) * 1609.34

        km_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:km|kilometers?)\b", query, re.IGNORECASE)
        if km_match:
            return float(km_match.group(1)) * 1000

        meters_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:m|meters?)\b", query, re.IGNORECASE)
        if meters_match:
            return float(meters_match.group(1))

        blocks_match = re.search(r"(\d+)\s*blocks?\b", query, re.IGNORECASE)
        if blocks_match:
            return float(blocks_match.group(1)) * 100

        return None

    def _extract_limit(self, query: str) -> int:
        """Extract result limit from the query."""
        limit_match = re.search(r"\b(?:top|first|limit)\s+(\d+)\b", query, re.IGNORECASE)
        if limit_match:
            return min(int(limit_match.group(1)), 1000)

        if re.search(r"\ball\b", query, re.IGNORECASE):
            return 1000

        return 100

    def _should_include_relationships(self, query: str) -> bool:
        """Determine if relationships should be included."""
        for pattern, _ in self.RELATIONSHIP_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return True

    def _should_include_risk_scores(self, query: str) -> bool:
        """Determine if risk scores should be included."""
        risk_keywords = [r"\brisk\b", r"\bthreat\b", r"\bdanger\b", r"\bscore\b"]
        for keyword in risk_keywords:
            if re.search(keyword, query, re.IGNORECASE):
                return True
        return True


class QueryInterpreterStage(PipelineStage[str, DSLQuery]):
    """Pipeline stage for query interpretation."""

    def __init__(self) -> None:
        """Initialize the stage."""
        super().__init__("query_interpreter")
        self._interpreter = QueryInterpreter()

    async def execute(self, input_data: str, context: PipelineContext) -> DSLQuery:
        """Execute query interpretation."""
        audit_logger.log_system_event(
            event_type="ai_query_interpretation",
            details={
                "request_id": context.request_id,
                "user_id": context.user_id,
                "query_length": len(input_data),
            },
        )

        return self._interpreter.interpret(input_data, context.role)


class DSLExecutor:
    """
    Executes structured DSL queries against Neo4j and Elasticsearch.

    Coordinates searches across multiple data sources and combines results.
    """

    def __init__(self) -> None:
        """Initialize the DSL executor."""
        self._neo4j_manager = None
        self._es_client = None

    async def initialize(
        self, neo4j_manager: Any, es_client: Any
    ) -> None:
        """Initialize with database connections."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client

    async def execute(
        self, dsl_query: DSLQuery, context: PipelineContext
    ) -> dict[str, Any]:
        """
        Execute a DSL query.

        Args:
            dsl_query: The structured DSL query
            context: Pipeline context

        Returns:
            Query results from all data sources
        """
        logger.info(
            "executing_dsl_query",
            query_type=dsl_query.query_type,
            request_id=context.request_id,
        )

        results: dict[str, Any] = {
            "entities": [],
            "incidents": [],
            "relationships": [],
            "metadata": {
                "query_type": dsl_query.query_type,
                "executed_at": datetime.utcnow().isoformat(),
            },
        }

        if self._neo4j_manager:
            neo4j_results = await self._execute_neo4j_query(dsl_query, context)
            results["entities"].extend(neo4j_results.get("entities", []))
            results["relationships"].extend(neo4j_results.get("relationships", []))

        if self._es_client:
            es_results = await self._execute_es_query(dsl_query, context)
            results["incidents"].extend(es_results.get("incidents", []))
            results["entities"].extend(es_results.get("entities", []))

        audit_logger.log_system_event(
            event_type="ai_query_executed",
            details={
                "request_id": context.request_id,
                "user_id": context.user_id,
                "entity_count": len(results["entities"]),
                "incident_count": len(results["incidents"]),
                "relationship_count": len(results["relationships"]),
            },
        )

        return results

    async def _execute_neo4j_query(
        self, dsl_query: DSLQuery, context: PipelineContext
    ) -> dict[str, Any]:
        """Execute query against Neo4j."""
        results: dict[str, Any] = {"entities": [], "relationships": []}

        if not self._neo4j_manager:
            return results

        try:
            for entity_spec in dsl_query.entities:
                entity_type = entity_spec.get("type", "")
                filters = entity_spec.get("filters", {})

                cypher_query = self._build_cypher_query(
                    entity_type, filters, dsl_query
                )

                if cypher_query:
                    query_results = await self._neo4j_manager.execute_query(
                        cypher_query["query"],
                        cypher_query.get("params", {}),
                    )
                    results["entities"].extend(query_results)

            if dsl_query.include_relationships and results["entities"]:
                entity_ids = [e.get("id") for e in results["entities"] if e.get("id")]
                if entity_ids:
                    rel_query = """
                    MATCH (a)-[r]-(b)
                    WHERE a.id IN $entity_ids OR b.id IN $entity_ids
                    RETURN type(r) as relationship_type,
                           a.id as source_id,
                           b.id as target_id,
                           properties(r) as properties
                    LIMIT 500
                    """
                    rel_results = await self._neo4j_manager.execute_query(
                        rel_query, {"entity_ids": entity_ids}
                    )
                    results["relationships"].extend(rel_results)

        except Exception as e:
            context.add_error(f"Neo4j query failed: {str(e)}")
            logger.error("neo4j_query_error", error=str(e))

        return results

    async def _execute_es_query(
        self, dsl_query: DSLQuery, context: PipelineContext
    ) -> dict[str, Any]:
        """Execute query against Elasticsearch."""
        results: dict[str, Any] = {"incidents": [], "entities": []}

        if not self._es_client:
            return results

        try:
            es_query = self._build_es_query(dsl_query)

            search_results = await self._es_client.search(
                index="rtcc_*",
                body=es_query,
                size=dsl_query.limit,
            )

            for hit in search_results.get("hits", {}).get("hits", []):
                source = hit.get("_source", {})
                index = hit.get("_index", "")

                if "incident" in index:
                    results["incidents"].append(source)
                else:
                    results["entities"].append(source)

        except Exception as e:
            context.add_error(f"Elasticsearch query failed: {str(e)}")
            logger.error("es_query_error", error=str(e))

        return results

    def _build_cypher_query(
        self, entity_type: str, filters: dict[str, Any], dsl_query: DSLQuery
    ) -> dict[str, Any] | None:
        """Build a Cypher query for Neo4j."""
        label_map = {
            "vehicle": "Vehicle",
            "person": "Person",
            "incident": "Incident",
            "address": "Address",
            "weapon": "Weapon",
        }

        label = label_map.get(entity_type)
        if not label:
            return None

        conditions = []
        params: dict[str, Any] = {}

        for key, value in filters.items():
            param_name = f"filter_{key}"
            conditions.append(f"n.{key} = ${param_name}")
            params[param_name] = value

        if dsl_query.time_range:
            conditions.append("n.created_at >= $start_time")
            conditions.append("n.created_at <= $end_time")
            params["start_time"] = dsl_query.time_range.start.isoformat()
            params["end_time"] = dsl_query.time_range.end.isoformat()

        where_clause = " AND ".join(conditions) if conditions else "true"

        query = f"""
        MATCH (n:{label})
        WHERE {where_clause}
        RETURN n
        LIMIT {dsl_query.limit}
        """

        return {"query": query, "params": params}

    def _build_es_query(self, dsl_query: DSLQuery) -> dict[str, Any]:
        """Build an Elasticsearch query."""
        must_clauses: list[dict[str, Any]] = []
        filter_clauses: list[dict[str, Any]] = []

        for entity_spec in dsl_query.entities:
            entity_type = entity_spec.get("type", "")
            if entity_type:
                must_clauses.append({"term": {"entity_type": entity_type}})

            for key, value in entity_spec.get("filters", {}).items():
                must_clauses.append({"match": {key: value}})

        for key, value in dsl_query.filters.items():
            if isinstance(value, bool):
                filter_clauses.append({"term": {key: value}})
            else:
                must_clauses.append({"match": {key: value}})

        if dsl_query.time_range:
            filter_clauses.append(
                {
                    "range": {
                        "timestamp": {
                            "gte": dsl_query.time_range.start.isoformat(),
                            "lte": dsl_query.time_range.end.isoformat(),
                        }
                    }
                }
            )

        if dsl_query.location and dsl_query.radius_meters:
            filter_clauses.append(
                {
                    "geo_distance": {
                        "distance": f"{dsl_query.radius_meters}m",
                        "location": {
                            "lat": dsl_query.location.latitude,
                            "lon": dsl_query.location.longitude,
                        },
                    }
                }
            )

        return {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            }
        }


class DSLExecutorStage(PipelineStage[DSLQuery, dict[str, Any]]):
    """Pipeline stage for DSL execution."""

    def __init__(self, executor: DSLExecutor) -> None:
        """Initialize the stage."""
        super().__init__("dsl_executor")
        self._executor = executor

    async def execute(
        self, input_data: DSLQuery, context: PipelineContext
    ) -> dict[str, Any]:
        """Execute DSL query."""
        return await self._executor.execute(input_data, context)


class ResultComposer:
    """
    Composes final query results from multiple data sources.

    Combines entities, incidents, relationships, and risk scores into
    a unified intelligence response.
    """

    def compose(
        self,
        query: str,
        raw_results: dict[str, Any],
        risk_scores: dict[str, Any] | None = None,
        context: PipelineContext | None = None,
    ) -> dict[str, Any]:
        """
        Compose final query results.

        Args:
            query: Original query string
            raw_results: Raw results from data sources
            risk_scores: Risk scores for entities
            context: Pipeline context

        Returns:
            Composed intelligence response
        """
        query_id = str(uuid.uuid4())

        entities = self._deduplicate_entities(raw_results.get("entities", []))
        incidents = raw_results.get("incidents", [])
        relationships = raw_results.get("relationships", [])

        summary = self._generate_summary(query, entities, incidents, relationships)
        recommendations = self._generate_recommendations(
            entities, incidents, relationships, risk_scores
        )

        return {
            "query_id": query_id,
            "original_query": query,
            "summary": summary,
            "entities": entities,
            "incidents": incidents,
            "relationships": relationships,
            "risk_scores": risk_scores or {},
            "recommendations": recommendations,
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": raw_results.get("metadata", {}),
        }

    def _deduplicate_entities(
        self, entities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Remove duplicate entities."""
        seen_ids: set[str] = set()
        unique_entities = []

        for entity in entities:
            entity_id = entity.get("id") or entity.get("entity_id")
            if entity_id and entity_id not in seen_ids:
                seen_ids.add(entity_id)
                unique_entities.append(entity)
            elif not entity_id:
                unique_entities.append(entity)

        return unique_entities

    def _generate_summary(
        self,
        query: str,
        entities: list[dict[str, Any]],
        incidents: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
    ) -> str:
        """Generate a summary of the results."""
        entity_count = len(entities)
        incident_count = len(incidents)
        relationship_count = len(relationships)

        parts = []

        if entity_count > 0:
            entity_types = {}
            for e in entities:
                etype = e.get("entity_type", e.get("type", "unknown"))
                entity_types[etype] = entity_types.get(etype, 0) + 1

            type_summary = ", ".join(
                f"{count} {etype}(s)" for etype, count in entity_types.items()
            )
            parts.append(f"Found {entity_count} entities: {type_summary}")

        if incident_count > 0:
            parts.append(f"Found {incident_count} related incidents")

        if relationship_count > 0:
            parts.append(f"Discovered {relationship_count} relationships")

        if not parts:
            return "No results found matching your query."

        return ". ".join(parts) + "."

    def _generate_recommendations(
        self,
        entities: list[dict[str, Any]],
        incidents: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        risk_scores: dict[str, Any] | None,
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        high_risk_entities = []
        if risk_scores:
            for entity_id, score_data in risk_scores.items():
                if isinstance(score_data, dict):
                    level = score_data.get("level", "")
                    if level in ["critical", "high"]:
                        high_risk_entities.append(entity_id)

        if high_risk_entities:
            recommendations.append(
                f"Priority attention needed for {len(high_risk_entities)} high-risk entities"
            )

        if len(relationships) > 10:
            recommendations.append(
                "Complex relationship network detected - consider graph visualization"
            )

        if len(incidents) > 20:
            recommendations.append(
                "High incident volume - consider narrowing search parameters"
            )

        if not entities and not incidents:
            recommendations.append(
                "No results found - try broadening search criteria or time range"
            )

        return recommendations


__all__ = [
    "QueryInterpreter",
    "QueryInterpreterStage",
    "DSLExecutor",
    "DSLExecutorStage",
    "ResultComposer",
]
