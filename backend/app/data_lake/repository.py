"""
Data Lake Repository for G3TI RTCC-UIP.

This module provides data access layer for the data lake including:
- CRUD operations for incident records
- Partition management
- Historical aggregate queries
- Offender profile management
- Data lineage tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..db.elasticsearch import ElasticsearchManager
from ..db.neo4j import Neo4jManager
from ..db.redis import RedisManager
from .models import (
    CrimeCategory,
    CrimeDataPartition,
    DataLakeStats,
    DataLineageRecord,
    DataQualityMetric,
    DataRetentionPolicy,
    HistoricalAggregate,
    IncidentRecord,
    MultiYearHeatmapData,
    OffenderProfile,
    PartitionMetadata,
    PartitionType,
)

logger = logging.getLogger(__name__)


class DataLakeRepository:
    """
    Repository for data lake operations.

    Provides data access methods for:
    - Incident records storage and retrieval
    - Partition management
    - Historical aggregates
    - Offender profiles
    - Data governance
    """

    # Index names
    INCIDENTS_INDEX = "datalake_incidents"
    AGGREGATES_INDEX = "datalake_aggregates"
    OFFENDERS_INDEX = "datalake_offenders"
    PARTITIONS_INDEX = "datalake_partitions"
    LINEAGE_INDEX = "datalake_lineage"
    QUALITY_INDEX = "datalake_quality"

    # Cache keys
    CACHE_PREFIX = "datalake:"
    STATS_CACHE_KEY = f"{CACHE_PREFIX}stats"
    PARTITION_CACHE_PREFIX = f"{CACHE_PREFIX}partition:"

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Data Lake Repository.

        Args:
            neo4j: Neo4j database manager for graph queries
            es: Elasticsearch manager for document storage
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis
        self._cache_ttl = 3600  # 1 hour default

        logger.info("DataLakeRepository initialized")

    # ==================== Incident Records ====================

    async def store_incident(self, incident: IncidentRecord) -> str:
        """
        Store an incident record in the data lake.

        Args:
            incident: Incident record to store

        Returns:
            Document ID of stored record
        """
        try:
            doc = incident.model_dump()
            doc["timestamp"] = doc["timestamp"].isoformat()
            doc["reported_at"] = doc["reported_at"].isoformat()
            doc["ingested_at"] = doc["ingested_at"].isoformat()

            result = await self.es.index(
                index=self.INCIDENTS_INDEX,
                id=incident.id,
                document=doc,
            )

            # Invalidate stats cache
            await self._invalidate_stats_cache()

            logger.debug(f"Stored incident {incident.id}")
            return result.get("_id", incident.id)

        except Exception as e:
            logger.error(f"Failed to store incident {incident.id}: {e}")
            raise

    async def store_incidents_bulk(self, incidents: list[IncidentRecord]) -> dict[str, Any]:
        """
        Store multiple incident records in bulk.

        Args:
            incidents: List of incident records

        Returns:
            Bulk operation result summary
        """
        try:
            operations = []
            for incident in incidents:
                doc = incident.model_dump()
                doc["timestamp"] = doc["timestamp"].isoformat()
                doc["reported_at"] = doc["reported_at"].isoformat()
                doc["ingested_at"] = doc["ingested_at"].isoformat()

                operations.append({"index": {"_index": self.INCIDENTS_INDEX, "_id": incident.id}})
                operations.append(doc)

            if operations:
                result = await self.es.bulk(operations=operations)
                await self._invalidate_stats_cache()

                return {
                    "total": len(incidents),
                    "successful": len(incidents) - result.get("errors", 0),
                    "failed": result.get("errors", 0),
                }

            return {"total": 0, "successful": 0, "failed": 0}

        except Exception as e:
            logger.error(f"Bulk incident storage failed: {e}")
            raise

    async def get_incident(self, incident_id: str) -> IncidentRecord | None:
        """
        Retrieve an incident record by ID.

        Args:
            incident_id: Incident ID

        Returns:
            Incident record or None if not found
        """
        try:
            result = await self.es.get(index=self.INCIDENTS_INDEX, id=incident_id)
            if result and result.get("found"):
                return IncidentRecord(**result["_source"])
            return None
        except Exception as e:
            logger.error(f"Failed to get incident {incident_id}: {e}")
            return None

    async def query_incidents(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        crime_category: CrimeCategory | None = None,
        jurisdiction: str | None = None,
        beat: str | None = None,
        bounds: dict[str, float] | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> tuple[list[IncidentRecord], int]:
        """
        Query incidents with filters.

        Args:
            start_date: Start date filter
            end_date: End date filter
            crime_category: Crime category filter
            jurisdiction: Jurisdiction filter
            beat: Beat/zone filter
            bounds: Geographic bounds {min_lat, max_lat, min_lon, max_lon}
            limit: Maximum results
            offset: Result offset

        Returns:
            Tuple of (incidents list, total count)
        """
        try:
            must_clauses: list[dict[str, Any]] = []
            filter_clauses: list[dict[str, Any]] = []

            # Date range
            if start_date or end_date:
                date_range: dict[str, Any] = {}
                if start_date:
                    date_range["gte"] = start_date.isoformat()
                if end_date:
                    date_range["lte"] = end_date.isoformat()
                must_clauses.append({"range": {"timestamp": date_range}})

            # Category filter
            if crime_category:
                filter_clauses.append({"term": {"crime_category": crime_category.value}})

            # Jurisdiction filter
            if jurisdiction:
                filter_clauses.append({"term": {"jurisdiction": jurisdiction}})

            # Beat filter
            if beat:
                filter_clauses.append({"term": {"beat": beat}})

            # Geographic bounds
            if bounds:
                filter_clauses.append({
                    "geo_bounding_box": {
                        "location": {
                            "top_left": {
                                "lat": bounds["max_lat"],
                                "lon": bounds["min_lon"],
                            },
                            "bottom_right": {
                                "lat": bounds["min_lat"],
                                "lon": bounds["max_lon"],
                            },
                        }
                    }
                })

            query: dict[str, Any] = {"bool": {}}
            if must_clauses:
                query["bool"]["must"] = must_clauses
            if filter_clauses:
                query["bool"]["filter"] = filter_clauses
            if not must_clauses and not filter_clauses:
                query = {"match_all": {}}

            result = await self.es.search(
                index=self.INCIDENTS_INDEX,
                query=query,
                size=limit,
                from_=offset,
                sort=[{"timestamp": "desc"}],
            )

            hits = result.get("hits", {})
            total = hits.get("total", {}).get("value", 0)
            incidents = [IncidentRecord(**hit["_source"]) for hit in hits.get("hits", [])]

            return incidents, total

        except Exception as e:
            logger.error(f"Incident query failed: {e}")
            return [], 0

    async def get_incidents_by_partition(
        self,
        partition_key: str,
        limit: int = 10000,
    ) -> list[IncidentRecord]:
        """
        Get all incidents in a partition.

        Args:
            partition_key: Partition key (e.g., "2024-01")
            limit: Maximum results

        Returns:
            List of incidents in partition
        """
        try:
            query = {"term": {"partition_month": partition_key}}

            result = await self.es.search(
                index=self.INCIDENTS_INDEX,
                query=query,
                size=limit,
                sort=[{"timestamp": "asc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [IncidentRecord(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to get incidents for partition {partition_key}: {e}")
            return []

    # ==================== Historical Aggregates ====================

    async def store_aggregate(self, aggregate: HistoricalAggregate) -> str:
        """
        Store a historical aggregate.

        Args:
            aggregate: Aggregate to store

        Returns:
            Document ID
        """
        try:
            doc = aggregate.model_dump()
            doc["period_start"] = doc["period_start"].isoformat()
            doc["period_end"] = doc["period_end"].isoformat()
            doc["computed_at"] = doc["computed_at"].isoformat()

            result = await self.es.index(
                index=self.AGGREGATES_INDEX,
                id=aggregate.id,
                document=doc,
            )

            return result.get("_id", aggregate.id)

        except Exception as e:
            logger.error(f"Failed to store aggregate {aggregate.id}: {e}")
            raise

    async def get_aggregates(
        self,
        aggregate_type: str,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        crime_category: CrimeCategory | None = None,
        beat: str | None = None,
    ) -> list[HistoricalAggregate]:
        """
        Query historical aggregates.

        Args:
            aggregate_type: Type (daily, weekly, monthly, yearly)
            jurisdiction: Jurisdiction code
            start_date: Start date
            end_date: End date
            crime_category: Optional crime category filter
            beat: Optional beat filter

        Returns:
            List of aggregates
        """
        try:
            must_clauses = [
                {"term": {"aggregate_type": aggregate_type}},
                {"term": {"jurisdiction": jurisdiction}},
                {"range": {"period_start": {"gte": start_date.isoformat()}}},
                {"range": {"period_end": {"lte": end_date.isoformat()}}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category.value}})
            if beat:
                must_clauses.append({"term": {"beat": beat}})

            result = await self.es.search(
                index=self.AGGREGATES_INDEX,
                query={"bool": {"must": must_clauses}},
                size=1000,
                sort=[{"period_start": "asc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [HistoricalAggregate(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to get aggregates: {e}")
            return []

    async def get_year_over_year_comparison(
        self,
        jurisdiction: str,
        years: list[int],
        crime_category: CrimeCategory | None = None,
    ) -> dict[int, list[HistoricalAggregate]]:
        """
        Get year-over-year comparison data.

        Args:
            jurisdiction: Jurisdiction code
            years: List of years to compare
            crime_category: Optional crime category filter

        Returns:
            Dictionary mapping year to monthly aggregates
        """
        result: dict[int, list[HistoricalAggregate]] = {}

        for year in years:
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31, 23, 59, 59)

            aggregates = await self.get_aggregates(
                aggregate_type="monthly",
                jurisdiction=jurisdiction,
                start_date=start,
                end_date=end,
                crime_category=crime_category,
            )
            result[year] = aggregates

        return result

    # ==================== Offender Profiles ====================

    async def store_offender_profile(self, profile: OffenderProfile) -> str:
        """
        Store or update an offender profile.

        Args:
            profile: Offender profile

        Returns:
            Document ID
        """
        try:
            doc = profile.model_dump()
            doc["first_seen"] = doc["first_seen"].isoformat()
            doc["last_seen"] = doc["last_seen"].isoformat()
            doc["last_updated"] = doc["last_updated"].isoformat()

            # Convert GeoPoint objects
            doc["primary_locations"] = [
                {"latitude": loc["latitude"], "longitude": loc["longitude"]}
                for loc in doc["primary_locations"]
            ]

            result = await self.es.index(
                index=self.OFFENDERS_INDEX,
                id=profile.id,
                document=doc,
            )

            # Also store in Neo4j for relationship queries
            await self._store_offender_in_graph(profile)

            return result.get("_id", profile.id)

        except Exception as e:
            logger.error(f"Failed to store offender profile {profile.id}: {e}")
            raise

    async def _store_offender_in_graph(self, profile: OffenderProfile) -> None:
        """Store offender profile in Neo4j graph."""
        try:
            query = """
            MERGE (o:Offender {id: $id})
            SET o.total_incidents = $total_incidents,
                o.recidivism_risk_score = $recidivism_risk_score,
                o.violence_risk_score = $violence_risk_score,
                o.escalation_trend = $escalation_trend,
                o.last_updated = datetime($last_updated)
            """

            await self.neo4j.execute_write(
                query,
                id=profile.id,
                total_incidents=profile.total_incidents,
                recidivism_risk_score=profile.recidivism_risk_score,
                violence_risk_score=profile.violence_risk_score,
                escalation_trend=profile.escalation_trend,
                last_updated=profile.last_updated.isoformat(),
            )

            # Create associate relationships
            for associate_id in profile.known_associates:
                assoc_query = """
                MATCH (o:Offender {id: $offender_id})
                MERGE (a:Offender {id: $associate_id})
                MERGE (o)-[:ASSOCIATED_WITH]->(a)
                """
                await self.neo4j.execute_write(
                    assoc_query,
                    offender_id=profile.id,
                    associate_id=associate_id,
                )

        except Exception as e:
            logger.warning(f"Failed to store offender in graph: {e}")

    async def get_offender_profile(self, offender_id: str) -> OffenderProfile | None:
        """
        Get an offender profile by ID.

        Args:
            offender_id: Offender ID

        Returns:
            Offender profile or None
        """
        try:
            result = await self.es.get(index=self.OFFENDERS_INDEX, id=offender_id)
            if result and result.get("found"):
                return OffenderProfile(**result["_source"])
            return None
        except Exception as e:
            logger.error(f"Failed to get offender profile {offender_id}: {e}")
            return None

    async def query_offenders(
        self,
        min_incidents: int | None = None,
        min_risk_score: float | None = None,
        jurisdiction: str | None = None,
        escalation_trend: str | None = None,
        limit: int = 100,
    ) -> list[OffenderProfile]:
        """
        Query offender profiles with filters.

        Args:
            min_incidents: Minimum incident count
            min_risk_score: Minimum recidivism risk score
            jurisdiction: Jurisdiction filter (via primary beats)
            escalation_trend: Trend filter
            limit: Maximum results

        Returns:
            List of offender profiles
        """
        try:
            must_clauses: list[dict[str, Any]] = []

            if min_incidents:
                must_clauses.append({"range": {"total_incidents": {"gte": min_incidents}}})

            if min_risk_score:
                must_clauses.append(
                    {"range": {"recidivism_risk_score": {"gte": min_risk_score}}}
                )

            if escalation_trend:
                must_clauses.append({"term": {"escalation_trend": escalation_trend}})

            query: dict[str, Any] = {"bool": {"must": must_clauses}} if must_clauses else {
                "match_all": {}
            }

            result = await self.es.search(
                index=self.OFFENDERS_INDEX,
                query=query,
                size=limit,
                sort=[{"recidivism_risk_score": "desc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [OffenderProfile(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Offender query failed: {e}")
            return []

    async def get_repeat_offenders(
        self,
        min_incidents: int = 3,
        days_back: int = 365,
        limit: int = 50,
    ) -> list[OffenderProfile]:
        """
        Get repeat offenders with recent activity.

        Args:
            min_incidents: Minimum incident threshold
            days_back: Days to look back for recent activity
            limit: Maximum results

        Returns:
            List of repeat offender profiles
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            query = {
                "bool": {
                    "must": [
                        {"range": {"total_incidents": {"gte": min_incidents}}},
                        {"range": {"last_seen": {"gte": cutoff_date.isoformat()}}},
                    ]
                }
            }

            result = await self.es.search(
                index=self.OFFENDERS_INDEX,
                query=query,
                size=limit,
                sort=[
                    {"recidivism_risk_score": "desc"},
                    {"total_incidents": "desc"},
                ],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [OffenderProfile(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to get repeat offenders: {e}")
            return []

    async def get_offender_network(self, offender_id: str, depth: int = 2) -> dict[str, Any]:
        """
        Get offender's associate network from graph.

        Args:
            offender_id: Starting offender ID
            depth: Network traversal depth

        Returns:
            Network graph data
        """
        try:
            query = f"""
            MATCH path = (o:Offender {{id: $offender_id}})-[:ASSOCIATED_WITH*1..{depth}]-(associate:Offender)
            RETURN o, associate, relationships(path) as rels
            LIMIT 100
            """

            result = await self.neo4j.execute_read(query, offender_id=offender_id)

            nodes = []
            edges = []
            seen_nodes: set[str] = set()

            for record in result:
                offender = record.get("o", {})
                associate = record.get("associate", {})

                if offender.get("id") and offender["id"] not in seen_nodes:
                    nodes.append({
                        "id": offender["id"],
                        "risk_score": offender.get("recidivism_risk_score", 0),
                    })
                    seen_nodes.add(offender["id"])

                if associate.get("id") and associate["id"] not in seen_nodes:
                    nodes.append({
                        "id": associate["id"],
                        "risk_score": associate.get("recidivism_risk_score", 0),
                    })
                    seen_nodes.add(associate["id"])

                if offender.get("id") and associate.get("id"):
                    edges.append({
                        "source": offender["id"],
                        "target": associate["id"],
                    })

            return {"nodes": nodes, "edges": edges}

        except Exception as e:
            logger.error(f"Failed to get offender network: {e}")
            return {"nodes": [], "edges": []}

    # ==================== Partition Management ====================

    async def create_partition(self, partition: CrimeDataPartition) -> str:
        """
        Create a new partition record.

        Args:
            partition: Partition metadata

        Returns:
            Partition key
        """
        try:
            doc = partition.model_dump()
            doc["start_date"] = doc["start_date"].isoformat()
            doc["end_date"] = doc["end_date"].isoformat()
            doc["created_at"] = doc["created_at"].isoformat()
            doc["last_updated"] = doc["last_updated"].isoformat()

            await self.es.index(
                index=self.PARTITIONS_INDEX,
                id=partition.partition_key,
                document=doc,
            )

            return partition.partition_key

        except Exception as e:
            logger.error(f"Failed to create partition {partition.partition_key}: {e}")
            raise

    async def get_partition(self, partition_key: str) -> CrimeDataPartition | None:
        """
        Get partition metadata.

        Args:
            partition_key: Partition key

        Returns:
            Partition metadata or None
        """
        try:
            # Check cache first
            cache_key = f"{self.PARTITION_CACHE_PREFIX}{partition_key}"
            cached = await self.redis.get(cache_key)
            if cached:
                return CrimeDataPartition(**cached)

            result = await self.es.get(index=self.PARTITIONS_INDEX, id=partition_key)
            if result and result.get("found"):
                partition = CrimeDataPartition(**result["_source"])
                # Cache the result
                await self.redis.set(
                    cache_key,
                    partition.model_dump(),
                    ex=self._cache_ttl,
                )
                return partition
            return None

        except Exception as e:
            logger.error(f"Failed to get partition {partition_key}: {e}")
            return None

    async def list_partitions(
        self,
        partition_type: PartitionType | None = None,
        is_active: bool | None = None,
        is_archived: bool | None = None,
    ) -> list[CrimeDataPartition]:
        """
        List partitions with optional filters.

        Args:
            partition_type: Filter by partition type
            is_active: Filter by active status
            is_archived: Filter by archived status

        Returns:
            List of partitions
        """
        try:
            must_clauses: list[dict[str, Any]] = []

            if partition_type:
                must_clauses.append({"term": {"partition_type": partition_type.value}})
            if is_active is not None:
                must_clauses.append({"term": {"is_active": is_active}})
            if is_archived is not None:
                must_clauses.append({"term": {"is_archived": is_archived}})

            query: dict[str, Any] = {"bool": {"must": must_clauses}} if must_clauses else {
                "match_all": {}
            }

            result = await self.es.search(
                index=self.PARTITIONS_INDEX,
                query=query,
                size=1000,
                sort=[{"start_date": "desc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [CrimeDataPartition(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to list partitions: {e}")
            return []

    async def update_partition_stats(
        self,
        partition_key: str,
        record_count: int,
        size_bytes: int,
    ) -> None:
        """
        Update partition statistics.

        Args:
            partition_key: Partition key
            record_count: New record count
            size_bytes: New size in bytes
        """
        try:
            await self.es.update(
                index=self.PARTITIONS_INDEX,
                id=partition_key,
                doc={
                    "record_count": record_count,
                    "size_bytes": size_bytes,
                    "last_updated": datetime.utcnow().isoformat(),
                },
            )

            # Invalidate cache
            cache_key = f"{self.PARTITION_CACHE_PREFIX}{partition_key}"
            await self.redis.delete(cache_key)

        except Exception as e:
            logger.error(f"Failed to update partition stats: {e}")

    # ==================== Data Governance ====================

    async def store_lineage_record(self, lineage: DataLineageRecord) -> str:
        """
        Store a data lineage record.

        Args:
            lineage: Lineage record

        Returns:
            Document ID
        """
        try:
            doc = lineage.model_dump()
            doc["source_timestamp"] = doc["source_timestamp"].isoformat()
            doc["created_at"] = doc["created_at"].isoformat()
            if doc["last_accessed"]:
                doc["last_accessed"] = doc["last_accessed"].isoformat()

            result = await self.es.index(
                index=self.LINEAGE_INDEX,
                id=lineage.id,
                document=doc,
            )

            return result.get("_id", lineage.id)

        except Exception as e:
            logger.error(f"Failed to store lineage record: {e}")
            raise

    async def get_lineage(self, record_id: str) -> list[DataLineageRecord]:
        """
        Get lineage records for a data record.

        Args:
            record_id: Data record ID

        Returns:
            List of lineage records
        """
        try:
            query = {"term": {"record_id": record_id}}

            result = await self.es.search(
                index=self.LINEAGE_INDEX,
                query=query,
                size=100,
                sort=[{"created_at": "asc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [DataLineageRecord(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to get lineage for {record_id}: {e}")
            return []

    async def store_quality_metric(self, metric: DataQualityMetric) -> str:
        """
        Store a data quality metric.

        Args:
            metric: Quality metric

        Returns:
            Document ID
        """
        try:
            doc = metric.model_dump()
            doc["computed_at"] = doc["computed_at"].isoformat()

            result = await self.es.index(
                index=self.QUALITY_INDEX,
                id=metric.id,
                document=doc,
            )

            return result.get("_id", metric.id)

        except Exception as e:
            logger.error(f"Failed to store quality metric: {e}")
            raise

    async def get_quality_metrics(
        self,
        partition_key: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[DataQualityMetric]:
        """
        Get data quality metrics.

        Args:
            partition_key: Optional partition filter
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of quality metrics
        """
        try:
            must_clauses: list[dict[str, Any]] = []

            if partition_key:
                must_clauses.append({"term": {"partition_key": partition_key}})

            if start_date or end_date:
                date_range: dict[str, Any] = {}
                if start_date:
                    date_range["gte"] = start_date.isoformat()
                if end_date:
                    date_range["lte"] = end_date.isoformat()
                must_clauses.append({"range": {"computed_at": date_range}})

            query: dict[str, Any] = {"bool": {"must": must_clauses}} if must_clauses else {
                "match_all": {}
            }

            result = await self.es.search(
                index=self.QUALITY_INDEX,
                query=query,
                size=1000,
                sort=[{"computed_at": "desc"}],
            )

            hits = result.get("hits", {}).get("hits", [])
            return [DataQualityMetric(**hit["_source"]) for hit in hits]

        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
            return []

    # ==================== Statistics ====================

    async def get_data_lake_stats(self) -> DataLakeStats:
        """
        Get overall data lake statistics.

        Returns:
            Data lake statistics
        """
        try:
            # Check cache
            cached = await self.redis.get(self.STATS_CACHE_KEY)
            if cached:
                return DataLakeStats(**cached)

            # Count incidents
            incident_count = await self.es.count(index=self.INCIDENTS_INDEX)
            total_records = incident_count.get("count", 0)

            # Get partition stats
            partitions = await self.list_partitions()
            total_partitions = len(partitions)
            active_partitions = sum(1 for p in partitions if p.is_active)
            archived_partitions = sum(1 for p in partitions if p.is_archived)

            total_size = sum(p.size_bytes for p in partitions)
            active_size = sum(p.size_bytes for p in partitions if p.is_active)
            archived_size = sum(p.size_bytes for p in partitions if p.is_archived)

            # Get date range
            earliest_query = await self.es.search(
                index=self.INCIDENTS_INDEX,
                query={"match_all": {}},
                size=1,
                sort=[{"timestamp": "asc"}],
            )
            latest_query = await self.es.search(
                index=self.INCIDENTS_INDEX,
                query={"match_all": {}},
                size=1,
                sort=[{"timestamp": "desc"}],
            )

            earliest_hits = earliest_query.get("hits", {}).get("hits", [])
            latest_hits = latest_query.get("hits", {}).get("hits", [])

            earliest_record = None
            latest_record = None

            if earliest_hits:
                earliest_record = datetime.fromisoformat(
                    earliest_hits[0]["_source"]["timestamp"].replace("Z", "+00:00")
                )
            if latest_hits:
                latest_record = datetime.fromisoformat(
                    latest_hits[0]["_source"]["timestamp"].replace("Z", "+00:00")
                )

            # Get quality metrics
            quality_metrics = await self.get_quality_metrics()
            avg_completeness = 1.0
            avg_accuracy = 1.0
            total_errors = 0

            if quality_metrics:
                avg_completeness = sum(m.completeness_score for m in quality_metrics) / len(
                    quality_metrics
                )
                avg_accuracy = sum(m.accuracy_score for m in quality_metrics) / len(
                    quality_metrics
                )
                total_errors = sum(len(m.issues) for m in quality_metrics)

            stats = DataLakeStats(
                total_records=total_records,
                total_partitions=total_partitions,
                active_partitions=active_partitions,
                archived_partitions=archived_partitions,
                total_size_gb=total_size / (1024**3),
                active_size_gb=active_size / (1024**3),
                archived_size_gb=archived_size / (1024**3),
                earliest_record=earliest_record,
                latest_record=latest_record,
                avg_completeness=avg_completeness,
                avg_accuracy=avg_accuracy,
                total_validation_errors=total_errors,
            )

            # Cache stats
            await self.redis.set(
                self.STATS_CACHE_KEY,
                stats.model_dump(),
                ex=300,  # 5 minutes
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get data lake stats: {e}")
            return DataLakeStats()

    async def _invalidate_stats_cache(self) -> None:
        """Invalidate the stats cache."""
        try:
            await self.redis.delete(self.STATS_CACHE_KEY)
        except Exception as e:
            logger.warning(f"Failed to invalidate stats cache: {e}")

    # ==================== Multi-Year Heatmap Data ====================

    async def store_multiyear_heatmap(self, heatmap: MultiYearHeatmapData) -> str:
        """
        Store multi-year heatmap data.

        Args:
            heatmap: Multi-year heatmap data

        Returns:
            Document ID
        """
        try:
            doc = heatmap.model_dump()
            doc["computed_at"] = doc["computed_at"].isoformat()

            result = await self.es.index(
                index=f"{self.AGGREGATES_INDEX}_heatmaps",
                id=heatmap.id,
                document=doc,
            )

            return result.get("_id", heatmap.id)

        except Exception as e:
            logger.error(f"Failed to store multi-year heatmap: {e}")
            raise

    async def get_multiyear_heatmap(
        self,
        jurisdiction: str,
        start_year: int,
        end_year: int,
        crime_category: CrimeCategory | None = None,
    ) -> MultiYearHeatmapData | None:
        """
        Get multi-year heatmap data.

        Args:
            jurisdiction: Jurisdiction code
            start_year: Start year
            end_year: End year
            crime_category: Optional crime category filter

        Returns:
            Multi-year heatmap data or None
        """
        try:
            must_clauses = [
                {"term": {"jurisdiction": jurisdiction}},
                {"term": {"start_year": start_year}},
                {"term": {"end_year": end_year}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category.value}})

            result = await self.es.search(
                index=f"{self.AGGREGATES_INDEX}_heatmaps",
                query={"bool": {"must": must_clauses}},
                size=1,
            )

            hits = result.get("hits", {}).get("hits", [])
            if hits:
                return MultiYearHeatmapData(**hits[0]["_source"])
            return None

        except Exception as e:
            logger.error(f"Failed to get multi-year heatmap: {e}")
            return None
