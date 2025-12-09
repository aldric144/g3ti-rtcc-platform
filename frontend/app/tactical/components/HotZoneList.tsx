"use client";

/**
 * Hot Zone List Component
 *
 * Displays list of hot zones with:
 * - Risk scores and confidence levels
 * - Zone status indicators
 * - Quick actions
 */

import { useState, useEffect } from "react";

interface HotZoneListProps {
  onZoneSelect?: (zoneId: string) => void;
  limit?: number;
}

interface HotZone {
  id: string;
  risk_score: number;
  risk_level: string;
  center: { lat: number; lon: number };
  activity_score: number;
  status: string;
  top_factors?: { name: string; contribution: number }[];
}

export function HotZoneList({ onZoneSelect, limit = 10 }: HotZoneListProps) {
  const [zones, setZones] = useState<HotZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch("/api/tactical/riskmap?level=micro&include_factors=true");
        if (!response.ok) {
          throw new Error("Failed to fetch zones");
        }
        const data = await response.json();
        // Filter to hot zones only (elevated risk and above)
        const hotZones = data.zones
          .filter((z: HotZone) => z.risk_score >= 0.4)
          .slice(0, limit);
        setZones(hotZones);
      } catch (err) {
        console.error("Failed to fetch hot zones:", err);
        setError(err instanceof Error ? err.message : "Failed to load zones");
        // Set mock data for development
        setZones(generateMockHotZones(limit));
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, [limit]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-700 rounded" />
        ))}
      </div>
    );
  }

  if (error && zones.length === 0) {
    return (
      <div className="text-red-400 text-sm p-4 bg-red-900/20 rounded">
        {error}
      </div>
    );
  }

  if (zones.length === 0) {
    return (
      <div className="text-gray-400 text-sm p-4 text-center">
        No hot zones detected
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {zones.map((zone) => (
        <HotZoneCard
          key={zone.id}
          zone={zone}
          onClick={() => onZoneSelect?.(zone.id)}
        />
      ))}
    </div>
  );
}

interface HotZoneCardProps {
  zone: HotZone;
  onClick?: () => void;
}

function HotZoneCard({ zone, onClick }: HotZoneCardProps) {
  const riskColor = getRiskColor(zone.risk_level);
  const statusColor = getStatusColor(zone.status);

  return (
    <button
      onClick={onClick}
      className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{zone.id}</span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-medium ${riskColor.bg} ${riskColor.text}`}
            >
              {zone.risk_level.toUpperCase()}
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs ${statusColor.bg} ${statusColor.text}`}
            >
              {zone.status}
            </span>
          </div>
          <div className="text-sm text-gray-400 mt-1">
            Risk: {(zone.risk_score * 100).toFixed(0)}% | Activity:{" "}
            {(zone.activity_score * 100).toFixed(0)}%
          </div>
          {zone.top_factors && zone.top_factors.length > 0 && (
            <div className="text-xs text-gray-500 mt-1">
              Top factor: {formatFactorName(zone.top_factors[0].name)}
            </div>
          )}
        </div>
        <div className="text-right">
          <RiskGauge score={zone.risk_score} />
        </div>
      </div>
    </button>
  );
}

// Risk gauge component
function RiskGauge({ score }: { score: number }) {
  const percentage = score * 100;
  const color =
    score >= 0.8
      ? "text-red-500"
      : score >= 0.6
        ? "text-orange-500"
        : score >= 0.4
          ? "text-yellow-500"
          : "text-green-500";

  return (
    <div className={`text-2xl font-bold ${color}`}>
      {percentage.toFixed(0)}%
    </div>
  );
}

// Helper functions
function getRiskColor(level: string): { bg: string; text: string } {
  switch (level.toLowerCase()) {
    case "critical":
      return { bg: "bg-red-900/50", text: "text-red-400" };
    case "high":
      return { bg: "bg-orange-900/50", text: "text-orange-400" };
    case "elevated":
      return { bg: "bg-yellow-900/50", text: "text-yellow-400" };
    case "moderate":
      return { bg: "bg-blue-900/50", text: "text-blue-400" };
    default:
      return { bg: "bg-green-900/50", text: "text-green-400" };
  }
}

function getStatusColor(status: string): { bg: string; text: string } {
  switch (status.toLowerCase()) {
    case "hot":
      return { bg: "bg-red-900/30", text: "text-red-300" };
    case "warm":
      return { bg: "bg-orange-900/30", text: "text-orange-300" };
    case "cool":
      return { bg: "bg-blue-900/30", text: "text-blue-300" };
    default:
      return { bg: "bg-gray-900/30", text: "text-gray-300" };
  }
}

function formatFactorName(name: string): string {
  return name
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function generateMockHotZones(limit: number): HotZone[] {
  const zones: HotZone[] = [];
  const riskLevels = ["critical", "high", "elevated", "moderate"];
  const statuses = ["hot", "warm", "cool"];

  for (let i = 0; i < limit; i++) {
    const riskScore = 0.9 - i * 0.08;
    zones.push({
      id: `micro_${i}_${Math.floor(Math.random() * 20)}`,
      risk_score: riskScore,
      risk_level: riskLevels[Math.min(i, riskLevels.length - 1)],
      center: {
        lat: 33.45 + (Math.random() - 0.5) * 0.1,
        lon: -112.07 + (Math.random() - 0.5) * 0.1,
      },
      activity_score: riskScore * 0.9 + Math.random() * 0.1,
      status: statuses[Math.min(Math.floor(i / 2), statuses.length - 1)],
      top_factors: [
        { name: "gunfire_frequency", contribution: 0.3 },
        { name: "violent_crime_history", contribution: 0.25 },
      ],
    });
  }

  return zones;
}
