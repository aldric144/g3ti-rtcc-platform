"use client";

import React, { useState, useEffect } from "react";

interface ZoneStability {
  zone_id: string;
  stability_score: number;
  risk_level: string;
  primary_concerns: string[];
  trend: string;
}

interface StabilityData {
  overall_stability: number;
  zones: ZoneStability[];
  trend_7_day: number;
  trend_30_day: number;
}

export default function CommunityStabilityDashboard() {
  const [stabilityData, setStabilityData] = useState<StabilityData>({
    overall_stability: 74.5,
    zones: [
      { zone_id: "Zone_A", stability_score: 72.0, risk_level: "MODERATE", primary_concerns: ["violence"], trend: "stable" },
      { zone_id: "Zone_B", stability_score: 85.0, risk_level: "LOW", primary_concerns: [], trend: "improving" },
      { zone_id: "Zone_C", stability_score: 65.0, risk_level: "ELEVATED", primary_concerns: ["mental_health", "youth"], trend: "declining" },
      { zone_id: "Zone_D", stability_score: 78.0, risk_level: "MODERATE", primary_concerns: ["substance"], trend: "stable" },
    ],
    trend_7_day: 0.5,
    trend_30_day: 1.2,
  });
  const [selectedZone, setSelectedZone] = useState<ZoneStability | null>(null);

  useEffect(() => {
    fetchStabilityData();
    const interval = setInterval(fetchStabilityData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchStabilityData = async () => {
    try {
      const response = await fetch("/api/human-intel/stability-map");
      if (response.ok) {
        const data = await response.json();
        if (data.high_risk_areas) {
          setStabilityData({
            overall_stability: data.overall_stability_score || 74.5,
            zones: data.high_risk_areas.map((area: any) => ({
              zone_id: area.zone,
              stability_score: area.score || 70,
              risk_level: area.risk_type?.toUpperCase() || "MODERATE",
              primary_concerns: [area.risk_type || "general"],
              trend: "stable",
            })),
            trend_7_day: data.trend_7_day || 0.5,
            trend_30_day: data.trend_30_day || 1.2,
          });
        }
      }
    } catch (error) {
      console.error("Failed to fetch stability data:", error);
    }
  };

  const getStabilityColor = (score: number): string => {
    if (score >= 80) return "#22c55e";
    if (score >= 60) return "#eab308";
    if (score >= 40) return "#f97316";
    return "#ef4444";
  };

  const getRiskBadgeColor = (level: string): string => {
    switch (level) {
      case "LOW": return "bg-green-600";
      case "MODERATE": return "bg-yellow-600";
      case "ELEVATED": return "bg-orange-600";
      case "HIGH": return "bg-red-600";
      case "CRITICAL": return "bg-red-800";
      default: return "bg-gray-600";
    }
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

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Community Stability Dashboard</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Stability Index by Zone</h3>
          <svg viewBox="0 0 400 300" className="w-full h-64">
            <rect x="10" y="10" width="180" height="130" rx="8" fill={getStabilityColor(stabilityData.zones[0]?.stability_score || 70)} fillOpacity="0.3" stroke={getStabilityColor(stabilityData.zones[0]?.stability_score || 70)} strokeWidth="2" className="cursor-pointer hover:fill-opacity-50" onClick={() => setSelectedZone(stabilityData.zones[0])} />
            <text x="100" y="75" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone A</text>
            <text x="100" y="95" textAnchor="middle" fill="white" fontSize="20">{stabilityData.zones[0]?.stability_score.toFixed(0) || "72"}</text>
            
            <rect x="210" y="10" width="180" height="130" rx="8" fill={getStabilityColor(stabilityData.zones[1]?.stability_score || 85)} fillOpacity="0.3" stroke={getStabilityColor(stabilityData.zones[1]?.stability_score || 85)} strokeWidth="2" className="cursor-pointer hover:fill-opacity-50" onClick={() => setSelectedZone(stabilityData.zones[1])} />
            <text x="300" y="75" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone B</text>
            <text x="300" y="95" textAnchor="middle" fill="white" fontSize="20">{stabilityData.zones[1]?.stability_score.toFixed(0) || "85"}</text>
            
            <rect x="10" y="160" width="180" height="130" rx="8" fill={getStabilityColor(stabilityData.zones[2]?.stability_score || 65)} fillOpacity="0.3" stroke={getStabilityColor(stabilityData.zones[2]?.stability_score || 65)} strokeWidth="2" className="cursor-pointer hover:fill-opacity-50" onClick={() => setSelectedZone(stabilityData.zones[2])} />
            <text x="100" y="225" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone C</text>
            <text x="100" y="245" textAnchor="middle" fill="white" fontSize="20">{stabilityData.zones[2]?.stability_score.toFixed(0) || "65"}</text>
            
            <rect x="210" y="160" width="180" height="130" rx="8" fill={getStabilityColor(stabilityData.zones[3]?.stability_score || 78)} fillOpacity="0.3" stroke={getStabilityColor(stabilityData.zones[3]?.stability_score || 78)} strokeWidth="2" className="cursor-pointer hover:fill-opacity-50" onClick={() => setSelectedZone(stabilityData.zones[3])} />
            <text x="300" y="225" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone D</text>
            <text x="300" y="245" textAnchor="middle" fill="white" fontSize="20">{stabilityData.zones[3]?.stability_score.toFixed(0) || "78"}</text>
          </svg>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Trend Analysis</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-600 rounded">
              <span>7-Day Trend</span>
              <span className={stabilityData.trend_7_day >= 0 ? "text-green-400" : "text-red-400"}>
                {stabilityData.trend_7_day >= 0 ? "+" : ""}{stabilityData.trend_7_day.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-600 rounded">
              <span>30-Day Trend</span>
              <span className={stabilityData.trend_30_day >= 0 ? "text-green-400" : "text-red-400"}>
                {stabilityData.trend_30_day >= 0 ? "+" : ""}{stabilityData.trend_30_day.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-600 rounded">
              <span>Overall Stability</span>
              <span className="text-xl font-bold" style={{ color: getStabilityColor(stabilityData.overall_stability) }}>
                {stabilityData.overall_stability.toFixed(1)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Zone Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stabilityData.zones.map((zone) => (
            <div
              key={zone.zone_id}
              className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
                selectedZone?.zone_id === zone.zone_id ? "ring-2 ring-blue-500" : ""
              }`}
              onClick={() => setSelectedZone(zone)}
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-semibold">{zone.zone_id}</h4>
                <span className={`px-2 py-1 rounded text-xs ${getRiskBadgeColor(zone.risk_level)}`}>
                  {zone.risk_level}
                </span>
              </div>
              <div className="text-3xl font-bold mb-2" style={{ color: getStabilityColor(zone.stability_score) }}>
                {zone.stability_score.toFixed(0)}
              </div>
              <div className={`flex items-center gap-1 ${getTrendColor(zone.trend)}`}>
                <span>{getTrendIcon(zone.trend)}</span>
                <span className="text-sm capitalize">{zone.trend}</span>
              </div>
              {zone.primary_concerns.length > 0 && (
                <div className="mt-2 text-xs text-gray-400">
                  Concerns: {zone.primary_concerns.join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {selectedZone && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Selected Zone: {selectedZone.zone_id}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-gray-400 text-sm">Stability Score</div>
              <div className="text-2xl font-bold" style={{ color: getStabilityColor(selectedZone.stability_score) }}>
                {selectedZone.stability_score.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Risk Level</div>
              <div className={`inline-block px-2 py-1 rounded text-sm ${getRiskBadgeColor(selectedZone.risk_level)}`}>
                {selectedZone.risk_level}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Trend</div>
              <div className={`text-lg ${getTrendColor(selectedZone.trend)}`}>
                {getTrendIcon(selectedZone.trend)} {selectedZone.trend}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Primary Concerns</div>
              <div className="text-sm">
                {selectedZone.primary_concerns.length > 0 
                  ? selectedZone.primary_concerns.join(", ")
                  : "None identified"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
