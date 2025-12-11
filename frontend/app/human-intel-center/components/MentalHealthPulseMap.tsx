"use client";

import React, { useState, useEffect } from "react";

interface ZonePulse {
  zone_id: string;
  mental_health_score: number;
  crisis_calls_24h: number;
  welfare_checks_24h: number;
  trend: string;
  primary_concerns: string[];
}

interface CommunityPulse {
  stability_index: number;
  community_shock_level: number;
  trauma_clusters: number;
  trend_direction: string;
}

export default function MentalHealthPulseMap() {
  const [zonePulses, setZonePulses] = useState<ZonePulse[]>([
    { zone_id: "Zone_A", mental_health_score: 68, crisis_calls_24h: 5, welfare_checks_24h: 8, trend: "stable", primary_concerns: ["substance", "mental_health"] },
    { zone_id: "Zone_B", mental_health_score: 82, crisis_calls_24h: 2, welfare_checks_24h: 3, trend: "improving", primary_concerns: [] },
    { zone_id: "Zone_C", mental_health_score: 55, crisis_calls_24h: 9, welfare_checks_24h: 12, trend: "declining", primary_concerns: ["mental_health", "violence"] },
    { zone_id: "Zone_D", mental_health_score: 72, crisis_calls_24h: 4, welfare_checks_24h: 6, trend: "stable", primary_concerns: ["substance"] },
  ]);
  const [communityPulse, setCommunityPulse] = useState<CommunityPulse>({
    stability_index: 72.0,
    community_shock_level: 0.25,
    trauma_clusters: 2,
    trend_direction: "stable",
  });
  const [selectedZone, setSelectedZone] = useState<ZonePulse | null>(null);
  const [timeRange, setTimeRange] = useState<string>("24h");

  useEffect(() => {
    fetchCommunityPulse();
    const interval = setInterval(fetchCommunityPulse, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchCommunityPulse = async () => {
    try {
      const response = await fetch("/api/human-intel/community-pulse");
      if (response.ok) {
        const data = await response.json();
        setCommunityPulse({
          stability_index: data.stability_index || 72.0,
          community_shock_level: data.community_shock_level || 0.25,
          trauma_clusters: data.trauma_clusters?.length || 2,
          trend_direction: data.trend_direction || "stable",
        });
      }
    } catch (error) {
      console.error("Failed to fetch community pulse:", error);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "#22c55e";
    if (score >= 60) return "#eab308";
    if (score >= 40) return "#f97316";
    return "#ef4444";
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case "improving": return "↑";
      case "declining": return "↓";
      default: return "→";
    }
  };

  const getTrendColor = (trend: string): string => {
    switch (trend) {
      case "improving": return "text-green-400";
      case "declining": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  const getShockLevelLabel = (level: number): string => {
    if (level >= 0.7) return "SEVERE";
    if (level >= 0.5) return "HIGH";
    if (level >= 0.3) return "MODERATE";
    return "LOW";
  };

  const getShockLevelColor = (level: number): string => {
    if (level >= 0.7) return "text-red-400";
    if (level >= 0.5) return "text-orange-400";
    if (level >= 0.3) return "text-yellow-400";
    return "text-green-400";
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Mental Health Pulse Map</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-gray-400 text-sm mb-1">Stability Index</div>
          <div className="text-3xl font-bold" style={{ color: getScoreColor(communityPulse.stability_index) }}>
            {communityPulse.stability_index.toFixed(1)}
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-gray-400 text-sm mb-1">Community Shock</div>
          <div className={`text-2xl font-bold ${getShockLevelColor(communityPulse.community_shock_level)}`}>
            {getShockLevelLabel(communityPulse.community_shock_level)}
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-gray-400 text-sm mb-1">Trauma Clusters</div>
          <div className="text-3xl font-bold text-orange-400">{communityPulse.trauma_clusters}</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-gray-400 text-sm mb-1">Trend</div>
          <div className={`text-2xl font-bold ${getTrendColor(communityPulse.trend_direction)}`}>
            {getTrendIcon(communityPulse.trend_direction)} {communityPulse.trend_direction}
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        {["24h", "7d", "30d"].map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className={`px-4 py-2 rounded ${timeRange === range ? "bg-blue-600" : "bg-gray-600"}`}
          >
            {range}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Mental Health Pulse by Zone</h3>
          <svg viewBox="0 0 400 300" className="w-full h-64">
            {zonePulses.map((zone, idx) => {
              const x = (idx % 2) * 200 + 10;
              const y = Math.floor(idx / 2) * 150 + 10;
              const color = getScoreColor(zone.mental_health_score);
              return (
                <g key={zone.zone_id} className="cursor-pointer" onClick={() => setSelectedZone(zone)}>
                  <rect
                    x={x}
                    y={y}
                    width="180"
                    height="130"
                    rx="8"
                    fill={color}
                    fillOpacity="0.3"
                    stroke={color}
                    strokeWidth={selectedZone?.zone_id === zone.zone_id ? "4" : "2"}
                  />
                  <text x={x + 90} y={y + 40} textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
                    {zone.zone_id}
                  </text>
                  <text x={x + 90} y={y + 70} textAnchor="middle" fill="white" fontSize="28" fontWeight="bold">
                    {zone.mental_health_score}
                  </text>
                  <text x={x + 90} y={y + 95} textAnchor="middle" fill={color} fontSize="12">
                    {zone.crisis_calls_24h} crisis | {zone.welfare_checks_24h} welfare
                  </text>
                  <text x={x + 90} y={y + 115} textAnchor="middle" fill={getTrendColor(zone.trend).replace("text-", "#").replace("-400", "")} fontSize="12">
                    {getTrendIcon(zone.trend)} {zone.trend}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Zone Details</h3>
          {selectedZone ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-xl font-bold">{selectedZone.zone_id}</h4>
                <div className="text-3xl font-bold" style={{ color: getScoreColor(selectedZone.mental_health_score) }}>
                  {selectedZone.mental_health_score}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-600 rounded p-3">
                  <div className="text-gray-400 text-sm">Crisis Calls (24h)</div>
                  <div className="text-2xl font-bold">{selectedZone.crisis_calls_24h}</div>
                </div>
                <div className="bg-gray-600 rounded p-3">
                  <div className="text-gray-400 text-sm">Welfare Checks (24h)</div>
                  <div className="text-2xl font-bold">{selectedZone.welfare_checks_24h}</div>
                </div>
              </div>

              <div>
                <div className="text-gray-400 text-sm mb-1">Trend</div>
                <div className={`text-lg font-semibold ${getTrendColor(selectedZone.trend)}`}>
                  {getTrendIcon(selectedZone.trend)} {selectedZone.trend}
                </div>
              </div>

              <div>
                <div className="text-gray-400 text-sm mb-1">Primary Concerns</div>
                {selectedZone.primary_concerns.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {selectedZone.primary_concerns.map((concern, idx) => (
                      <span key={idx} className="bg-gray-600 px-2 py-1 rounded text-sm">
                        {concern.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-green-400">No significant concerns</div>
                )}
              </div>

              <div>
                <div className="text-gray-400 text-sm mb-1">Recommended Interventions</div>
                <ul className="list-disc list-inside text-sm">
                  {selectedZone.mental_health_score < 60 && (
                    <li>Increase community outreach</li>
                  )}
                  {selectedZone.crisis_calls_24h > 5 && (
                    <li>Deploy additional crisis resources</li>
                  )}
                  {selectedZone.primary_concerns.includes("substance") && (
                    <li>Substance abuse intervention programs</li>
                  )}
                  {selectedZone.primary_concerns.includes("mental_health") && (
                    <li>Mental health awareness campaign</li>
                  )}
                  <li>Continue monitoring</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-gray-400 text-center py-12">
              Click on a zone to view details
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Community Resources</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-600 rounded p-3">
            <div className="font-semibold mb-1">988 Suicide & Crisis Lifeline</div>
            <div className="text-sm text-gray-400">24/7 crisis support</div>
          </div>
          <div className="bg-gray-600 rounded p-3">
            <div className="font-semibold mb-1">Community Mental Health Center</div>
            <div className="text-sm text-gray-400">Outpatient services available</div>
          </div>
          <div className="bg-gray-600 rounded p-3">
            <div className="font-semibold mb-1">Mobile Crisis Unit</div>
            <div className="text-sm text-gray-400">On-scene mental health response</div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Privacy Notice</h3>
        <p className="text-gray-400 text-sm">
          All mental health data is aggregated and anonymized. No individual identification.
          HIPAA-adjacent protections applied. Data used only for resource allocation and community support.
        </p>
      </div>
    </div>
  );
}
