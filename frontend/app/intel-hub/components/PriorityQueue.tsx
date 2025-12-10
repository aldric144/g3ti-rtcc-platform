"use client";

import { useState, useEffect } from "react";

interface PriorityItem {
  id: string;
  title: string;
  score: number;
  tier: "tier1" | "tier2" | "tier3" | "tier4";
  source: string;
  category: string;
  threatLevel: "critical" | "high" | "medium" | "low" | "minimal";
  timestamp: string;
  acknowledged: boolean;
  assignedTo?: string;
  factors: string[];
}

const threatColors = {
  critical: "bg-red-600 text-white",
  high: "bg-orange-600 text-white",
  medium: "bg-yellow-600 text-black",
  low: "bg-blue-600 text-white",
  minimal: "bg-gray-600 text-white",
};

const mockItems: PriorityItem[] = [
  {
    id: "pq-001",
    title: "Armed Robbery in Progress - District 3",
    score: 98,
    tier: "tier1",
    source: "Dispatch",
    category: "violent_crime",
    threatLevel: "critical",
    timestamp: new Date().toISOString(),
    acknowledged: false,
    factors: ["Active incident", "Weapon involved", "Officer en route"],
  },
  {
    id: "pq-002",
    title: "Federal Warrant Match - High Risk Subject",
    score: 92,
    tier: "tier1",
    source: "NCIC",
    category: "federal_match",
    threatLevel: "critical",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    acknowledged: true,
    assignedTo: "Unit 45",
    factors: ["Federal warrant", "History of violence", "Armed and dangerous"],
  },
  {
    id: "pq-003",
    title: "Pattern Alert - Vehicle Theft Ring",
    score: 75,
    tier: "tier2",
    source: "AI Engine",
    category: "pattern",
    threatLevel: "high",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    acknowledged: false,
    factors: ["5 linked incidents", "Known suspects", "Active investigation"],
  },
  {
    id: "pq-004",
    title: "Suspicious Activity - Critical Infrastructure",
    score: 68,
    tier: "tier2",
    source: "Tactical Engine",
    category: "suspicious_activity",
    threatLevel: "high",
    timestamp: new Date(Date.now() - 450000).toISOString(),
    acknowledged: true,
    assignedTo: "Detective Smith",
    factors: ["Critical location", "Repeat behavior", "DHS notification"],
  },
  {
    id: "pq-005",
    title: "Multi-Agency BOLO - Stolen Vehicle",
    score: 55,
    tier: "tier3",
    source: "Federation Hub",
    category: "bolo",
    threatLevel: "medium",
    timestamp: new Date(Date.now() - 600000).toISOString(),
    acknowledged: false,
    factors: ["Multi-agency", "Recent sighting", "Linked to burglary"],
  },
  {
    id: "pq-006",
    title: "Historical Trend - Assault Increase",
    score: 42,
    tier: "tier4",
    source: "Data Lake",
    category: "trend",
    threatLevel: "low",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    acknowledged: true,
    factors: ["30-day trend", "Sector 12", "Weekend pattern"],
  },
];

export default function PriorityQueue() {
  const [items, setItems] = useState<PriorityItem[]>(mockItems);
  const [sortBy, setSortBy] = useState<"score" | "time">("score");
  const [filterThreat, setFilterThreat] = useState<string>("all");

  const handleAcknowledge = (id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, acknowledged: true } : item
      )
    );
  };

  const sortedItems = [...items].sort((a, b) => {
    if (sortBy === "score") return b.score - a.score;
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });

  const filteredItems =
    filterThreat === "all"
      ? sortedItems
      : sortedItems.filter((i) => i.threatLevel === filterThreat);

  const unacknowledgedCount = items.filter((i) => !i.acknowledged).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold">Priority Queue</h2>
          {unacknowledgedCount > 0 && (
            <span className="bg-red-600 text-white px-2 py-1 rounded-full text-xs">
              {unacknowledgedCount} unacknowledged
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "score" | "time")}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="score">Priority Score</option>
              <option value="time">Time</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Threat:</span>
            <select
              value={filterThreat}
              onChange={(e) => setFilterThreat(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Levels</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="minimal">Minimal</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2 mb-4">
        {(["critical", "high", "medium", "low", "minimal"] as const).map(
          (level) => {
            const count = items.filter((i) => i.threatLevel === level).length;
            return (
              <div
                key={level}
                className={`${threatColors[level]} rounded p-3 text-center`}
              >
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-xs capitalize">{level}</div>
              </div>
            );
          }
        )}
      </div>

      <div className="space-y-2">
        {filteredItems.map((item) => (
          <div
            key={item.id}
            className={`bg-gray-800 border rounded-lg p-4 ${
              !item.acknowledged
                ? "border-yellow-500 animate-pulse"
                : "border-gray-700"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`${threatColors[item.threatLevel]} px-2 py-0.5 rounded text-xs font-medium`}
                  >
                    {item.threatLevel.toUpperCase()}
                  </span>
                  <span className="bg-blue-900 text-blue-300 px-2 py-0.5 rounded text-xs">
                    Score: {item.score}
                  </span>
                  <span className="text-xs text-gray-400">{item.source}</span>
                  <span className="text-xs text-gray-400">{item.category}</span>
                </div>
                <h3 className="font-semibold text-white">{item.title}</h3>
                <div className="flex flex-wrap gap-1 mt-2">
                  {item.factors.map((factor, idx) => (
                    <span
                      key={idx}
                      className="bg-gray-700 px-2 py-0.5 rounded text-xs text-gray-300"
                    >
                      {factor}
                    </span>
                  ))}
                </div>
                {item.assignedTo && (
                  <div className="text-xs text-green-400 mt-2">
                    Assigned to: {item.assignedTo}
                  </div>
                )}
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className="text-xs text-gray-500">
                  {new Date(item.timestamp).toLocaleTimeString()}
                </span>
                {!item.acknowledged && (
                  <button
                    onClick={() => handleAcknowledge(item.id)}
                    className="bg-yellow-600 hover:bg-yellow-500 text-black px-3 py-1 rounded text-xs font-medium"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
