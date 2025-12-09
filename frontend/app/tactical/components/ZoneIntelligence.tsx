"use client";

/**
 * Zone Intelligence Component
 *
 * Provides zone-level intelligence with:
 * - Zone list and selection
 * - Detailed zone information
 * - Risk factors and predictions
 * - Historical trends
 */

import { useState, useEffect, useCallback } from "react";

interface ZoneIntelligenceProps {
  selectedZone: string | null;
  onZoneSelect: (zoneId: string | null) => void;
}

interface Zone {
  id: string;
  level: string;
  bounds: {
    min_lat: number;
    max_lat: number;
    min_lon: number;
    max_lon: number;
  };
  center: { lat: number; lon: number };
  risk_score?: number;
  risk_level?: string;
  activity_score?: number;
  status?: string;
}

interface ZoneDetails extends Zone {
  incident_breakdown?: {
    by_type: Record<string, number>;
    by_severity: Record<string, number>;
    total: number;
  };
  temporal_patterns?: {
    by_hour: Record<string, number>;
    peak_hours: number[];
    peak_activity_period: string;
  };
  entity_summary?: {
    total_entities: number;
    by_type: Record<string, number>;
    high_risk_entities: number;
  };
  historical_trends?: {
    weekly_counts: { week: string; count: number }[];
    trend: number;
    trend_direction: string;
  };
  neighbors?: {
    zone_id: string;
    direction: string;
    activity_score: number;
    status: string;
  }[];
  predictions?: {
    predictions: { type: string; confidence: number }[];
    next_crime_probability: number;
  };
  overlays?: {
    cameras: { id: string; lat: number; lon: number; status: string }[];
    lpr_cameras: { id: string; lat: number; lon: number; status: string }[];
  };
}

export function ZoneIntelligence({
  selectedZone,
  onZoneSelect,
}: ZoneIntelligenceProps) {
  const [zones, setZones] = useState<Zone[]>([]);
  const [zoneDetails, setZoneDetails] = useState<ZoneDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Fetch all zones
  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch(
          "/api/tactical/zones?include_risk=true&level=micro"
        );
        if (!response.ok) throw new Error("Failed to fetch zones");
        const data = await response.json();
        setZones(data.zones || []);
      } catch (err) {
        console.error("Failed to fetch zones:", err);
        setZones(generateMockZones());
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, []);

  // Fetch zone details when selected
  const fetchZoneDetails = useCallback(async (zoneId: string) => {
    setDetailsLoading(true);
    try {
      const response = await fetch(
        `/api/tactical/zones/${zoneId}?include_history=true`
      );
      if (!response.ok) throw new Error("Failed to fetch zone details");
      const data = await response.json();
      setZoneDetails(data);
    } catch (err) {
      console.error("Failed to fetch zone details:", err);
      setZoneDetails(generateMockZoneDetails(zoneId));
    } finally {
      setDetailsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedZone) {
      fetchZoneDetails(selectedZone);
    } else {
      setZoneDetails(null);
    }
  }, [selectedZone, fetchZoneDetails]);

  // Filter zones
  const filteredZones = zones.filter((zone) => {
    const matchesSearch = zone.id
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesStatus =
      filterStatus === "all" || zone.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Zone list */}
      <div className="col-span-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Tactical Zones</h2>

          {/* Search and filter */}
          <div className="space-y-2 mb-4">
            <input
              type="text"
              placeholder="Search zones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="hot">Hot</option>
              <option value="warm">Warm</option>
              <option value="cool">Cool</option>
              <option value="cold">Cold</option>
            </select>
          </div>

          {/* Zone list */}
          {loading ? (
            <div className="animate-pulse space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-700 rounded" />
              ))}
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredZones.map((zone) => (
                <button
                  key={zone.id}
                  onClick={() => onZoneSelect(zone.id)}
                  className={`w-full text-left p-3 rounded transition-colors ${
                    selectedZone === zone.id
                      ? "bg-blue-600"
                      : "bg-gray-700 hover:bg-gray-600"
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-sm">{zone.id}</span>
                    <StatusBadge status={zone.status || "unknown"} />
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Risk: {((zone.risk_score || 0) * 100).toFixed(0)}% |
                    Activity: {((zone.activity_score || 0) * 100).toFixed(0)}%
                  </div>
                </button>
              ))}
              {filteredZones.length === 0 && (
                <div className="text-gray-400 text-sm text-center py-4">
                  No zones match your criteria
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Zone details */}
      <div className="col-span-8">
        {selectedZone && zoneDetails ? (
          <ZoneDetailsPanel
            zone={zoneDetails}
            loading={detailsLoading}
            onClose={() => onZoneSelect(null)}
          />
        ) : (
          <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-400">
            <p>Select a zone to view details</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Zone details panel
interface ZoneDetailsPanelProps {
  zone: ZoneDetails;
  loading: boolean;
  onClose: () => void;
}

function ZoneDetailsPanel({ zone, loading, onClose }: ZoneDetailsPanelProps) {
  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 animate-pulse">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-4" />
        <div className="space-y-4">
          <div className="h-32 bg-gray-700 rounded" />
          <div className="h-32 bg-gray-700 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold">{zone.id}</h2>
            <div className="flex gap-2 mt-2">
              <StatusBadge status={zone.status || "unknown"} />
              <RiskBadge level={zone.risk_level || "unknown"} />
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1"
          >
            Close
          </button>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-4 gap-4 mt-4">
          <MetricCard
            label="Risk Score"
            value={`${((zone.risk_score || 0) * 100).toFixed(0)}%`}
            color="red"
          />
          <MetricCard
            label="Activity"
            value={`${((zone.activity_score || 0) * 100).toFixed(0)}%`}
            color="orange"
          />
          <MetricCard
            label="Incidents (7d)"
            value={zone.incident_breakdown?.total?.toString() || "0"}
            color="yellow"
          />
          <MetricCard
            label="High Risk Entities"
            value={zone.entity_summary?.high_risk_entities?.toString() || "0"}
            color="purple"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Incident breakdown */}
        {zone.incident_breakdown && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-3">Incident Breakdown</h3>
            <div className="space-y-2">
              {Object.entries(zone.incident_breakdown.by_type).map(
                ([type, count]) => (
                  <div key={type} className="flex justify-between text-sm">
                    <span className="text-gray-400 capitalize">{type}</span>
                    <span>{count}</span>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {/* Temporal patterns */}
        {zone.temporal_patterns && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-3">Temporal Patterns</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Peak Period</span>
                <span className="capitalize">
                  {zone.temporal_patterns.peak_activity_period}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Peak Hours</span>
                <span>
                  {zone.temporal_patterns.peak_hours
                    .map((h) => `${h}:00`)
                    .join(", ")}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Entity summary */}
        {zone.entity_summary && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-3">Entity Summary</h3>
            <div className="space-y-2">
              {Object.entries(zone.entity_summary.by_type).map(
                ([type, count]) => (
                  <div key={type} className="flex justify-between text-sm">
                    <span className="text-gray-400">{type}</span>
                    <span>{count}</span>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {/* Historical trends */}
        {zone.historical_trends && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-3">Historical Trends</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Trend</span>
                <span
                  className={
                    zone.historical_trends.trend_direction === "increasing"
                      ? "text-red-400"
                      : zone.historical_trends.trend_direction === "decreasing"
                        ? "text-green-400"
                        : "text-gray-400"
                  }
                >
                  {zone.historical_trends.trend_direction} (
                  {(zone.historical_trends.trend * 100).toFixed(0)}%)
                </span>
              </div>
            </div>
            {/* Mini chart */}
            <div className="mt-3 h-16 flex items-end gap-1">
              {zone.historical_trends.weekly_counts.slice(-8).map((w, i) => (
                <div
                  key={i}
                  className="flex-1 bg-blue-500 rounded-t"
                  style={{
                    height: `${Math.max(10, (w.count / 20) * 100)}%`,
                  }}
                  title={`${w.week}: ${w.count}`}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Predictions */}
      {zone.predictions && zone.predictions.next_crime_probability > 0 && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-3">Predictions (24h)</h3>
          <div className="flex items-center gap-4">
            <div className="text-3xl font-bold text-orange-400">
              {(zone.predictions.next_crime_probability * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-400">
              Probability of incident in next 24 hours
            </div>
          </div>
        </div>
      )}

      {/* Neighboring zones */}
      {zone.neighbors && zone.neighbors.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-3">Neighboring Zones</h3>
          <div className="grid grid-cols-4 gap-2">
            {zone.neighbors.map((n) => (
              <div
                key={n.zone_id}
                className="p-2 bg-gray-700 rounded text-center text-sm"
              >
                <div className="text-xs text-gray-400 capitalize">
                  {n.direction}
                </div>
                <StatusBadge status={n.status} small />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper components
function StatusBadge({ status, small = false }: { status: string; small?: boolean }) {
  const colors: Record<string, string> = {
    hot: "bg-red-900/50 text-red-400",
    warm: "bg-orange-900/50 text-orange-400",
    cool: "bg-blue-900/50 text-blue-400",
    cold: "bg-gray-700 text-gray-400",
    unknown: "bg-gray-700 text-gray-400",
  };

  return (
    <span
      className={`px-2 py-0.5 rounded ${small ? "text-xs" : "text-xs"} ${colors[status] || colors.unknown}`}
    >
      {status}
    </span>
  );
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    critical: "bg-red-900/50 text-red-400",
    high: "bg-orange-900/50 text-orange-400",
    elevated: "bg-yellow-900/50 text-yellow-400",
    moderate: "bg-blue-900/50 text-blue-400",
    low: "bg-green-900/50 text-green-400",
    unknown: "bg-gray-700 text-gray-400",
  };

  return (
    <span className={`px-2 py-0.5 rounded text-xs ${colors[level] || colors.unknown}`}>
      {level}
    </span>
  );
}

function MetricCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: "red" | "orange" | "yellow" | "purple" | "blue" | "green";
}) {
  const colors = {
    red: "border-red-700 text-red-400",
    orange: "border-orange-700 text-orange-400",
    yellow: "border-yellow-700 text-yellow-400",
    purple: "border-purple-700 text-purple-400",
    blue: "border-blue-700 text-blue-400",
    green: "border-green-700 text-green-400",
  };

  return (
    <div className={`p-3 bg-gray-700/50 rounded border-l-4 ${colors[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  );
}

// Mock data generators
function generateMockZones(): Zone[] {
  const zones: Zone[] = [];
  const statuses = ["hot", "warm", "cool", "cold"];
  const riskLevels = ["critical", "high", "elevated", "moderate", "low"];

  for (let i = 0; i < 20; i++) {
    const riskScore = Math.random();
    zones.push({
      id: `micro_${i}_${Math.floor(Math.random() * 20)}`,
      level: "micro",
      bounds: {
        min_lat: 33.35 + i * 0.01,
        max_lat: 33.36 + i * 0.01,
        min_lon: -112.15,
        max_lon: -112.14,
      },
      center: { lat: 33.355 + i * 0.01, lon: -112.145 },
      risk_score: riskScore,
      risk_level: riskLevels[Math.floor((1 - riskScore) * 5)],
      activity_score: Math.random(),
      status: statuses[Math.floor(Math.random() * statuses.length)],
    });
  }

  return zones.sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));
}

function generateMockZoneDetails(zoneId: string): ZoneDetails {
  return {
    id: zoneId,
    level: "micro",
    bounds: { min_lat: 33.44, max_lat: 33.46, min_lon: -112.08, max_lon: -112.06 },
    center: { lat: 33.45, lon: -112.07 },
    risk_score: 0.75,
    risk_level: "high",
    activity_score: 0.68,
    status: "warm",
    incident_breakdown: {
      by_type: { theft: 5, assault: 3, burglary: 4, vandalism: 2 },
      by_severity: { low: 6, medium: 5, high: 3 },
      total: 14,
    },
    temporal_patterns: {
      by_hour: Object.fromEntries(
        Array.from({ length: 24 }, (_, i) => [i, Math.floor(Math.random() * 10)])
      ),
      peak_hours: [22, 23, 0],
      peak_activity_period: "night",
    },
    entity_summary: {
      total_entities: 45,
      by_type: { Person: 20, Vehicle: 15, Address: 10 },
      high_risk_entities: 5,
    },
    historical_trends: {
      weekly_counts: Array.from({ length: 12 }, (_, i) => ({
        week: `Week ${i + 1}`,
        count: 5 + Math.floor(Math.random() * 15),
      })),
      trend: 0.15,
      trend_direction: "increasing",
    },
    neighbors: [
      { zone_id: "micro_1_1", direction: "north", activity_score: 0.5, status: "cool" },
      { zone_id: "micro_1_2", direction: "east", activity_score: 0.7, status: "warm" },
      { zone_id: "micro_2_1", direction: "south", activity_score: 0.3, status: "cold" },
      { zone_id: "micro_2_0", direction: "west", activity_score: 0.6, status: "warm" },
    ],
    predictions: {
      predictions: [{ type: "crime", confidence: 0.65 }],
      next_crime_probability: 0.65,
    },
  };
}
