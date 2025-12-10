"""
Risk Terrain Modeling Engine.

Analyzes geographic risk factors to identify high-risk areas for crime.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class RiskFactorType(str, Enum):
    """Types of risk factors."""
    HISTORICAL_CRIME = "historical_crime"
    LIGHTING = "lighting"
    VACANT_PROPERTY = "vacant_property"
    ALCOHOL_OUTLET = "alcohol_outlet"
    TRANSIT_STOP = "transit_stop"
    SCHOOL = "school"
    PARK = "park"
    COMMERCIAL_AREA = "commercial_area"
    RESIDENTIAL_DENSITY = "residential_density"
    UNEMPLOYMENT = "unemployment"
    POVERTY = "poverty"
    GANG_TERRITORY = "gang_territory"
    DRUG_MARKET = "drug_market"
    DOMESTIC_VIOLENCE_HISTORY = "domestic_violence_history"
    REPEAT_OFFENDER_RESIDENCE = "repeat_offender_residence"


class RiskLevel(str, Enum):
    """Risk levels for terrain cells."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFactor(BaseModel):
    """Risk factor for terrain modeling."""
    factor_id: str
    factor_type: RiskFactorType
    name: str
    description: str = ""
    weight: float = 1.0
    decay_distance_m: float = 500.0
    latitude: float
    longitude: float
    radius_m: float = 100.0
    intensity: float = 1.0
    active: bool = True
    source: str = ""
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskCell(BaseModel):
    """Grid cell in the risk terrain model."""
    cell_id: str
    row: int
    col: int
    center_lat: float
    center_lon: float
    size_m: float = 100.0
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.MINIMAL
    contributing_factors: list[str] = Field(default_factory=list)
    factor_scores: dict[str, float] = Field(default_factory=dict)
    historical_incidents: int = 0
    predicted_incidents: float = 0.0
    last_incident: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TerrainModel(BaseModel):
    """Complete risk terrain model."""
    model_id: str
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    bounds: dict[str, float] = Field(default_factory=dict)
    cell_size_m: float = 100.0
    rows: int = 0
    cols: int = 0
    total_cells: int = 0
    high_risk_cells: int = 0
    factors_used: list[str] = Field(default_factory=list)
    version: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)


class TerrainConfig(BaseModel):
    """Configuration for risk terrain engine."""
    default_cell_size_m: float = 100.0
    max_cells: int = 100000
    risk_thresholds: dict[str, float] = Field(default_factory=lambda: {
        "minimal": 0.0,
        "low": 0.2,
        "moderate": 0.4,
        "high": 0.6,
        "critical": 0.8,
    })
    default_decay_distance_m: float = 500.0
    max_factors: int = 10000


class TerrainMetrics(BaseModel):
    """Metrics for risk terrain engine."""
    total_models: int = 0
    total_factors: int = 0
    factors_by_type: dict[str, int] = Field(default_factory=dict)
    total_cells: int = 0
    cells_by_risk: dict[str, int] = Field(default_factory=dict)
    avg_risk_score: float = 0.0


class RiskTerrainEngine:
    """
    Risk Terrain Modeling Engine.
    
    Analyzes geographic risk factors to identify high-risk areas for crime.
    """
    
    def __init__(self, config: Optional[TerrainConfig] = None):
        self.config = config or TerrainConfig()
        self._models: dict[str, TerrainModel] = {}
        self._factors: dict[str, RiskFactor] = {}
        self._cells: dict[str, dict[str, RiskCell]] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = TerrainMetrics()
    
    async def start(self) -> None:
        """Start the risk terrain engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the risk terrain engine."""
        self._running = False
    
    def create_model(
        self,
        name: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        cell_size_m: Optional[float] = None,
        description: str = "",
    ) -> TerrainModel:
        """Create a new risk terrain model."""
        model_id = f"rtm-{uuid.uuid4().hex[:12]}"
        cell_size = cell_size_m or self.config.default_cell_size_m
        
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        
        lat_cells = int((lat_range * 111320) / cell_size) + 1
        lon_cells = int((lon_range * 111320 * 0.7) / cell_size) + 1
        
        model = TerrainModel(
            model_id=model_id,
            name=name,
            description=description,
            bounds={
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon,
            },
            cell_size_m=cell_size,
            rows=lat_cells,
            cols=lon_cells,
            total_cells=lat_cells * lon_cells,
        )
        
        self._models[model_id] = model
        self._cells[model_id] = {}
        
        self._initialize_cells(model)
        self._update_metrics()
        
        return model
    
    def _initialize_cells(self, model: TerrainModel) -> None:
        """Initialize grid cells for a model."""
        bounds = model.bounds
        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / model.rows
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / model.cols
        
        for row in range(model.rows):
            for col in range(model.cols):
                cell_id = f"{model.model_id}-{row}-{col}"
                center_lat = bounds["min_lat"] + (row + 0.5) * lat_step
                center_lon = bounds["min_lon"] + (col + 0.5) * lon_step
                
                cell = RiskCell(
                    cell_id=cell_id,
                    row=row,
                    col=col,
                    center_lat=center_lat,
                    center_lon=center_lon,
                    size_m=model.cell_size_m,
                )
                
                self._cells[model.model_id][cell_id] = cell
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a risk terrain model."""
        if model_id not in self._models:
            return False
        
        del self._models[model_id]
        if model_id in self._cells:
            del self._cells[model_id]
        
        self._update_metrics()
        return True
    
    def get_model(self, model_id: str) -> Optional[TerrainModel]:
        """Get a model by ID."""
        return self._models.get(model_id)
    
    def get_all_models(self) -> list[TerrainModel]:
        """Get all models."""
        return list(self._models.values())
    
    def add_factor(
        self,
        factor_type: RiskFactorType,
        name: str,
        latitude: float,
        longitude: float,
        weight: float = 1.0,
        decay_distance_m: Optional[float] = None,
        radius_m: float = 100.0,
        intensity: float = 1.0,
        source: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> RiskFactor:
        """Add a risk factor."""
        factor_id = f"factor-{uuid.uuid4().hex[:12]}"
        
        factor = RiskFactor(
            factor_id=factor_id,
            factor_type=factor_type,
            name=name,
            latitude=latitude,
            longitude=longitude,
            weight=weight,
            decay_distance_m=decay_distance_m or self.config.default_decay_distance_m,
            radius_m=radius_m,
            intensity=intensity,
            source=source,
            metadata=metadata or {},
        )
        
        self._factors[factor_id] = factor
        self._update_metrics()
        
        return factor
    
    def remove_factor(self, factor_id: str) -> bool:
        """Remove a risk factor."""
        if factor_id not in self._factors:
            return False
        
        del self._factors[factor_id]
        self._update_metrics()
        return True
    
    def get_factor(self, factor_id: str) -> Optional[RiskFactor]:
        """Get a factor by ID."""
        return self._factors.get(factor_id)
    
    def get_all_factors(self) -> list[RiskFactor]:
        """Get all factors."""
        return list(self._factors.values())
    
    def get_factors_by_type(self, factor_type: RiskFactorType) -> list[RiskFactor]:
        """Get factors by type."""
        return [f for f in self._factors.values() if f.factor_type == factor_type]
    
    def get_factors_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[RiskFactor]:
        """Get factors within a geographic area."""
        result = []
        for factor in self._factors.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                factor.latitude, factor.longitude,
            )
            if distance <= radius_km:
                result.append(factor)
        return result
    
    async def calculate_risk(self, model_id: str) -> Optional[TerrainModel]:
        """Calculate risk scores for all cells in a model."""
        model = self._models.get(model_id)
        if not model:
            return None
        
        cells = self._cells.get(model_id, {})
        factors_used = set()
        high_risk_count = 0
        
        for cell in cells.values():
            cell.risk_score = 0.0
            cell.contributing_factors = []
            cell.factor_scores = {}
            
            for factor in self._factors.values():
                if not factor.active:
                    continue
                
                distance = self._calculate_distance(
                    cell.center_lat, cell.center_lon,
                    factor.latitude, factor.longitude,
                ) * 1000
                
                if distance <= factor.decay_distance_m:
                    decay = 1.0 - (distance / factor.decay_distance_m)
                    contribution = factor.weight * factor.intensity * decay
                    
                    cell.risk_score += contribution
                    cell.contributing_factors.append(factor.factor_id)
                    cell.factor_scores[factor.factor_id] = contribution
                    factors_used.add(factor.factor_type.value)
            
            cell.risk_score = min(1.0, cell.risk_score)
            cell.risk_level = self._score_to_level(cell.risk_score)
            
            if cell.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                high_risk_count += 1
        
        model.factors_used = list(factors_used)
        model.high_risk_cells = high_risk_count
        model.updated_at = datetime.now(timezone.utc)
        model.version += 1
        
        self._update_metrics()
        await self._notify_callbacks(model, "risk_calculated")
        
        return model
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level."""
        thresholds = self.config.risk_thresholds
        
        if score >= thresholds["critical"]:
            return RiskLevel.CRITICAL
        if score >= thresholds["high"]:
            return RiskLevel.HIGH
        if score >= thresholds["moderate"]:
            return RiskLevel.MODERATE
        if score >= thresholds["low"]:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def get_cell(self, model_id: str, row: int, col: int) -> Optional[RiskCell]:
        """Get a specific cell."""
        cells = self._cells.get(model_id, {})
        cell_id = f"{model_id}-{row}-{col}"
        return cells.get(cell_id)
    
    def get_cell_at_location(
        self,
        model_id: str,
        latitude: float,
        longitude: float,
    ) -> Optional[RiskCell]:
        """Get the cell containing a specific location."""
        model = self._models.get(model_id)
        if not model:
            return None
        
        bounds = model.bounds
        if not (bounds["min_lat"] <= latitude <= bounds["max_lat"] and
                bounds["min_lon"] <= longitude <= bounds["max_lon"]):
            return None
        
        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / model.rows
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / model.cols
        
        row = int((latitude - bounds["min_lat"]) / lat_step)
        col = int((longitude - bounds["min_lon"]) / lon_step)
        
        row = min(row, model.rows - 1)
        col = min(col, model.cols - 1)
        
        return self.get_cell(model_id, row, col)
    
    def get_high_risk_cells(self, model_id: str) -> list[RiskCell]:
        """Get all high-risk cells in a model."""
        cells = self._cells.get(model_id, {})
        return [
            c for c in cells.values()
            if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
    
    def get_cells_by_risk_level(
        self,
        model_id: str,
        risk_level: RiskLevel,
    ) -> list[RiskCell]:
        """Get cells by risk level."""
        cells = self._cells.get(model_id, {})
        return [c for c in cells.values() if c.risk_level == risk_level]
    
    def get_risk_heatmap_data(self, model_id: str) -> list[dict[str, Any]]:
        """Get heatmap data for visualization."""
        cells = self._cells.get(model_id, {})
        
        return [
            {
                "lat": cell.center_lat,
                "lon": cell.center_lon,
                "weight": cell.risk_score,
                "level": cell.risk_level.value,
            }
            for cell in cells.values()
            if cell.risk_score > 0
        ]
    
    def record_incident(
        self,
        model_id: str,
        latitude: float,
        longitude: float,
        incident_time: Optional[datetime] = None,
    ) -> bool:
        """Record an incident at a location."""
        cell = self.get_cell_at_location(model_id, latitude, longitude)
        if not cell:
            return False
        
        cell.historical_incidents += 1
        cell.last_incident = incident_time or datetime.now(timezone.utc)
        
        return True
    
    def get_metrics(self) -> TerrainMetrics:
        """Get terrain metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "running": self._running,
            "total_models": len(self._models),
            "total_factors": len(self._factors),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for terrain events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update terrain metrics."""
        factor_counts: dict[str, int] = {}
        for factor in self._factors.values():
            factor_counts[factor.factor_type.value] = factor_counts.get(factor.factor_type.value, 0) + 1
        
        total_cells = 0
        risk_counts: dict[str, int] = {}
        total_score = 0.0
        
        for model_cells in self._cells.values():
            for cell in model_cells.values():
                total_cells += 1
                risk_counts[cell.risk_level.value] = risk_counts.get(cell.risk_level.value, 0) + 1
                total_score += cell.risk_score
        
        self._metrics.total_models = len(self._models)
        self._metrics.total_factors = len(self._factors)
        self._metrics.factors_by_type = factor_counts
        self._metrics.total_cells = total_cells
        self._metrics.cells_by_risk = risk_counts
        self._metrics.avg_risk_score = total_score / total_cells if total_cells > 0 else 0.0
    
    async def _notify_callbacks(self, data: Any, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
