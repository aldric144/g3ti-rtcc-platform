"""
Sector Risk Analysis Module.

Scores each sector (1-5 severity) based on:
- Violent crime
- Property crime
- Gunfire incidents
- LPR hits
- DV escalations
- Repeat calls
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict

from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    get_crime_ingestor,
)


class RiskFactor(BaseModel):
    """Individual risk factor contribution."""
    factor_name: str
    count: int
    weight: float
    contribution: float
    trend: str  # "increasing", "decreasing", "stable"


class SectorRiskScore(BaseModel):
    """Complete risk assessment for a sector."""
    sector: str
    overall_score: float  # 1-5
    risk_level: str  # "low", "moderate", "elevated", "high", "critical"
    risk_factors: list[RiskFactor]
    total_incidents: int
    violent_crimes: int
    property_crimes: int
    domestic_violence: int
    repeat_locations: int
    trend: str
    recommendations: list[str]


class SectorComparisonResult(BaseModel):
    """Comparison of all sectors."""
    sectors: list[SectorRiskScore]
    highest_risk_sector: str
    lowest_risk_sector: str
    city_average_score: float
    analysis_period: str
    generated_at: str


class SectorRiskAnalyzer:
    """Analyzes and scores sector risk levels."""
    
    # Risk factor weights
    FACTOR_WEIGHTS = {
        "violent_crime": 3.0,
        "property_crime": 1.5,
        "gunfire": 4.0,
        "lpr_hits": 1.0,
        "domestic_violence": 2.5,
        "repeat_calls": 2.0,
    }
    
    # Risk level thresholds
    RISK_LEVELS = {
        "critical": 4.5,
        "high": 3.5,
        "elevated": 2.5,
        "moderate": 1.5,
        "low": 0,
    }
    
    def __init__(self):
        self.ingestor = get_crime_ingestor()
    
    def _count_violent_crimes(self, records: list[NormalizedCrimeRecord]) -> int:
        """Count violent crimes."""
        return sum(1 for r in records if r.type == CrimeType.VIOLENT)
    
    def _count_property_crimes(self, records: list[NormalizedCrimeRecord]) -> int:
        """Count property crimes."""
        return sum(1 for r in records if r.type == CrimeType.PROPERTY)
    
    def _count_gunfire(self, records: list[NormalizedCrimeRecord]) -> int:
        """Count gunfire-related incidents."""
        gunfire_keywords = ["shooting", "gunshot", "gunfire", "shots fired", "firearm"]
        count = 0
        for r in records:
            desc = (r.subcategory or "").lower() + " " + (r.description or "").lower()
            if any(kw in desc for kw in gunfire_keywords):
                count += 1
            elif r.weapon and "gun" in r.weapon.lower():
                count += 1
        return count
    
    def _count_domestic_violence(self, records: list[NormalizedCrimeRecord]) -> int:
        """Count domestic violence incidents."""
        return sum(1 for r in records if r.domestic_flag)
    
    def _count_repeat_locations(self, records: list[NormalizedCrimeRecord]) -> int:
        """Count locations with multiple incidents."""
        location_counts = defaultdict(int)
        for r in records:
            # Round coordinates to group nearby locations
            loc_key = (round(r.latitude, 4), round(r.longitude, 4))
            location_counts[loc_key] += 1
        
        return sum(1 for count in location_counts.values() if count >= 2)
    
    def _calculate_trend(
        self,
        records: list[NormalizedCrimeRecord],
        days: int = 30,
    ) -> str:
        """Calculate crime trend for sector."""
        now = datetime.utcnow()
        mid_point = now - timedelta(days=days // 2)
        
        first_half = sum(1 for r in records if r.datetime_utc < mid_point)
        second_half = sum(1 for r in records if r.datetime_utc >= mid_point)
        
        if first_half == 0:
            return "stable"
        
        change_ratio = (second_half - first_half) / first_half
        
        if change_ratio > 0.2:
            return "increasing"
        elif change_ratio < -0.2:
            return "decreasing"
        return "stable"
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        for level, threshold in sorted(self.RISK_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return "low"
    
    def _generate_recommendations(
        self,
        risk_factors: list[RiskFactor],
        overall_score: float,
    ) -> list[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        # Sort factors by contribution
        sorted_factors = sorted(risk_factors, key=lambda f: f.contribution, reverse=True)
        
        for factor in sorted_factors[:3]:  # Top 3 factors
            if factor.factor_name == "violent_crime" and factor.count > 0:
                recommendations.append(
                    f"Increase patrol presence - {factor.count} violent crimes detected"
                )
            elif factor.factor_name == "gunfire" and factor.count > 0:
                recommendations.append(
                    f"Deploy ShotSpotter monitoring - {factor.count} gunfire incidents"
                )
            elif factor.factor_name == "domestic_violence" and factor.count > 0:
                recommendations.append(
                    f"Coordinate with DV unit - {factor.count} domestic incidents"
                )
            elif factor.factor_name == "repeat_calls" and factor.count > 0:
                recommendations.append(
                    f"Identify repeat call locations - {factor.count} hotspots detected"
                )
            elif factor.factor_name == "property_crime" and factor.count > 0:
                recommendations.append(
                    f"Increase property crime prevention - {factor.count} incidents"
                )
        
        if overall_score >= 4.0:
            recommendations.insert(0, "PRIORITY: Deploy additional units immediately")
        elif overall_score >= 3.0:
            recommendations.insert(0, "Recommend increased surveillance coverage")
        
        return recommendations[:5]  # Max 5 recommendations
    
    def analyze_sector(
        self,
        sector: str,
        days: int = 30,
    ) -> SectorRiskScore:
        """Analyze risk for a specific sector."""
        # Get all records
        all_records = self.ingestor.get_all_records()
        
        # Filter by sector and time
        cutoff = datetime.utcnow() - timedelta(days=days)
        records = [
            r for r in all_records
            if r.sector == sector and r.datetime_utc >= cutoff
        ]
        
        # Calculate risk factors
        violent_count = self._count_violent_crimes(records)
        property_count = self._count_property_crimes(records)
        gunfire_count = self._count_gunfire(records)
        dv_count = self._count_domestic_violence(records)
        repeat_count = self._count_repeat_locations(records)
        
        # Simulated LPR hits (would come from LPR system)
        lpr_count = len(records) // 5
        
        # Calculate contributions
        risk_factors = []
        total_weighted = 0
        
        factors_data = [
            ("violent_crime", violent_count),
            ("property_crime", property_count),
            ("gunfire", gunfire_count),
            ("lpr_hits", lpr_count),
            ("domestic_violence", dv_count),
            ("repeat_calls", repeat_count),
        ]
        
        for factor_name, count in factors_data:
            weight = self.FACTOR_WEIGHTS[factor_name]
            contribution = count * weight
            total_weighted += contribution
            
            # Calculate trend for this factor
            factor_records = records  # Simplified - would filter by factor type
            trend = self._calculate_trend(factor_records, days)
            
            risk_factors.append(RiskFactor(
                factor_name=factor_name,
                count=count,
                weight=weight,
                contribution=round(contribution, 2),
                trend=trend,
            ))
        
        # Normalize to 1-5 scale
        # Assuming max reasonable weighted score is ~100
        overall_score = min(5.0, max(1.0, 1.0 + (total_weighted / 25)))
        
        # Get overall trend
        trend = self._calculate_trend(records, days)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, overall_score)
        
        return SectorRiskScore(
            sector=sector,
            overall_score=round(overall_score, 2),
            risk_level=self._get_risk_level(overall_score),
            risk_factors=risk_factors,
            total_incidents=len(records),
            violent_crimes=violent_count,
            property_crimes=property_count,
            domestic_violence=dv_count,
            repeat_locations=repeat_count,
            trend=trend,
            recommendations=recommendations,
        )
    
    def analyze_all_sectors(self, days: int = 30) -> SectorComparisonResult:
        """Analyze and compare all sectors."""
        # Get all records
        all_records = self.ingestor.get_all_records()
        
        # Get unique sectors
        sectors = set(r.sector for r in all_records)
        
        # Analyze each sector
        sector_scores = []
        for sector in sectors:
            score = self.analyze_sector(sector, days)
            sector_scores.append(score)
        
        # Sort by risk score
        sector_scores.sort(key=lambda s: s.overall_score, reverse=True)
        
        # Calculate city average
        if sector_scores:
            city_average = sum(s.overall_score for s in sector_scores) / len(sector_scores)
            highest_risk = sector_scores[0].sector
            lowest_risk = sector_scores[-1].sector
        else:
            city_average = 1.0
            highest_risk = "N/A"
            lowest_risk = "N/A"
        
        return SectorComparisonResult(
            sectors=sector_scores,
            highest_risk_sector=highest_risk,
            lowest_risk_sector=lowest_risk,
            city_average_score=round(city_average, 2),
            analysis_period=f"Last {days} days",
            generated_at=datetime.utcnow().isoformat(),
        )


# Global analyzer instance
_analyzer: Optional[SectorRiskAnalyzer] = None


def get_risk_analyzer() -> SectorRiskAnalyzer:
    """Get or create the global risk analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SectorRiskAnalyzer()
    return _analyzer
