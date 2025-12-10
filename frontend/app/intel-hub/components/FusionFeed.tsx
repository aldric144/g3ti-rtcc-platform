"use client";

import { useState, useEffect } from "react";

interface FusedIntelligence {
  id: string;
  tier: "tier1" | "tier2" | "tier3" | "tier4";
  title: string;
  summary: string;
  sources: string[];
  priorityScore: number;
  confidence: number;
  timestamp: string;
  entities: {
    type: string;
    id: string;
    name: string;
  }[];
  correlations: number;
  jurisdiction: string;
}

const tierConfig = {
  tier1: {
    label: "Tier 1 - Officer Safety",
    color: "bg-red-600",
    borderColor: "border-red-500",
    textColor: "text-red-300",
    bgColor: "bg-red-900/30",
  },
  tier2: {
    label: "Tier 2 - High Priority",
    color: "bg-orange-600",
    borderColor: "border-orange-500",
    textColor: "text-orange-300",
    bgColor: "bg-orange-900/30",
  },
  tier3: {
    label: "Tier 3 - Tactical",
    color: "bg-yellow-600",
    borderColor: "border-yellow-500",
    textColor: "text-yellow-300",
    bgColor: "bg-yellow-900/30",
  },
  tier4: {
    label: "Tier 4 - Informational",
    color: "bg-blue-600",
    borderColor: "border-blue-500",
    textColor: "text-blue-300",
    bgColor: "bg-blue-900/30",
  },
};

const mockIntelligence: FusedIntelligence[] = [
  {
    id: "fused-001",
    tier: "tier1",
    title: "Armed Suspect - Active Warrant",
    summary:
      "Cross-referenced federal warrant with local incident reports. Subject has history of violence against officers.",
    sources: ["NCIC", "AI Engine", "Officer Safety"],
    priorityScore: 95,
    confidence: 0.92,
    timestamp: new Date().toISOString(),
    entities: [
      { type: "person", id: "p-123", name: "John Doe" },
      { type: "vehicle", id: "v-456", name: "Black SUV - ABC123" },
    ],
    correlations: 8,
    jurisdiction: "Metro PD",
  },
  {
    id: "fused-002",
    tier: "tier2",
    title: "Pattern Match - Serial Burglary",
    summary:
      "AI pattern analysis detected correlation between 5 recent burglaries. MO matches known offender profile.",
    sources: ["AI Engine", "Tactical Engine", "Data Lake"],
    priorityScore: 78,
    confidence: 0.85,
    timestamp: new Date(Date.now() - 300000).toISOString(),
    entities: [
      { type: "pattern", id: "pat-789", name: "Residential Burglary Series" },
      { type: "location", id: "loc-012", name: "District 5" },
    ],
    correlations: 5,
    jurisdiction: "Metro PD",
  },
  {
    id: "fused-003",
    tier: "tier3",
    title: "Vehicle of Interest - Multi-Agency",
    summary:
      "Vehicle flagged by neighboring agency linked to drug trafficking investigation.",
    sources: ["Federation Hub", "Tactical Engine"],
    priorityScore: 62,
    confidence: 0.78,
    timestamp: new Date(Date.now() - 600000).toISOString(),
    entities: [
      { type: "vehicle", id: "v-789", name: "White Van - XYZ789" },
    ],
    correlations: 3,
    jurisdiction: "County Sheriff",
  },
  {
    id: "fused-004",
    tier: "tier4",
    title: "Historical Trend - Crime Spike",
    summary:
      "Data lake analysis shows 15% increase in property crimes in sector 7 over past 30 days.",
    sources: ["Data Lake", "Historical Analytics"],
    priorityScore: 45,
    confidence: 0.95,
    timestamp: new Date(Date.now() - 900000).toISOString(),
    entities: [
      { type: "location", id: "loc-345", name: "Sector 7" },
    ],
    correlations: 12,
    jurisdiction: "Metro PD",
  },
];

export default function FusionFeed() {
  const [intelligence, setIntelligence] = useState<FusedIntelligence[]>(mockIntelligence);
  const [filterTier, setFilterTier] = useState<string>("all");
  const [isLive, setIsLive] = useState(true);

  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      const tiers: ("tier1" | "tier2" | "tier3" | "tier4")[] = ["tier1", "tier2", "tier3", "tier4"];
      const randomTier = tiers[Math.floor(Math.random() * tiers.length)];
      
      const newIntel: FusedIntelligence = {
        id: `fused-${Date.now()}`,
        tier: randomTier,
        title: `New Intelligence Signal - ${randomTier.toUpperCase()}`,
        summary: "Newly fused intelligence from multiple sources requiring attention.",
        sources: ["AI Engine", "Tactical Engine"],
        priorityScore: Math.floor(Math.random() * 40) + 50,
        confidence: Math.random() * 0.3 + 0.7,
        timestamp: new Date().toISOString(),
        entities: [],
        correlations: Math.floor(Math.random() * 10),
        jurisdiction: "Metro PD",
      };

      setIntelligence((prev) => [newIntel, ...prev.slice(0, 19)]);
    }, 8000);

    return () => clearInterval(interval);
  }, [isLive]);

  const filteredIntelligence =
    filterTier === "all"
      ? intelligence
      : intelligence.filter((i) => i.tier === filterTier);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold">Fused Intelligence Feed</h2>
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-3 py-1 rounded text-sm ${
              isLive
                ? "bg-green-600 text-white"
                : "bg-gray-600 text-gray-300"
            }`}
          >
            {isLive ? "Live" : "Paused"}
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Filter:</span>
          <select
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
          >
            <option value="all">All Tiers</option>
            <option value="tier1">Tier 1 - Officer Safety</option>
            <option value="tier2">Tier 2 - High Priority</option>
            <option value="tier3">Tier 3 - Tactical</option>
            <option value="tier4">Tier 4 - Informational</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 mb-4">
        {Object.entries(tierConfig).map(([tier, config]) => {
          const count = intelligence.filter((i) => i.tier === tier).length;
          return (
            <div
              key={tier}
              className={`${config.bgColor} border ${config.borderColor} rounded p-3`}
            >
              <div className={`text-lg font-bold ${config.textColor}`}>
                {count}
              </div>
              <div className="text-xs text-gray-400">{config.label}</div>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        {filteredIntelligence.map((intel) => {
          const config = tierConfig[intel.tier];
          return (
            <div
              key={intel.id}
              className={`${config.bgColor} border ${config.borderColor} rounded-lg p-4`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`${config.color} px-2 py-0.5 rounded text-xs font-medium text-white`}
                    >
                      {config.label}
                    </span>
                    <span className="text-xs text-gray-400">
                      Score: {intel.priorityScore}
                    </span>
                    <span className="text-xs text-gray-400">
                      Confidence: {(intel.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h3 className={`font-semibold ${config.textColor}`}>
                    {intel.title}
                  </h3>
                  <p className="text-sm text-gray-300 mt-1">{intel.summary}</p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                    <span>Sources: {intel.sources.join(", ")}</span>
                    <span>Correlations: {intel.correlations}</span>
                    <span>Jurisdiction: {intel.jurisdiction}</span>
                  </div>
                  {intel.entities.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {intel.entities.map((entity) => (
                        <span
                          key={entity.id}
                          className="bg-gray-700 px-2 py-1 rounded text-xs"
                        >
                          {entity.type}: {entity.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(intel.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
