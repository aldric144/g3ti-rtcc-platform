"use client";

import React, { useState, useEffect } from "react";

interface GlobalSignal {
  signal_id: string;
  domain: string;
  severity: number;
  title: string;
  description: string;
  location: {
    lat: number;
    lon: number;
    region?: string;
  };
  affected_regions: string[];
  affected_countries: string[];
  timestamp: string;
  confidence_score: number;
}

interface RegionSummary {
  name: string;
  signalCount: number;
  highestSeverity: number;
  primaryDomain: string;
  riskLevel: string;
}

const DOMAINS = [
  { id: "crisis", label: "Crisis", color: "bg-red-500" },
  { id: "conflict", label: "Conflict", color: "bg-orange-500" },
  { id: "maritime", label: "Maritime", color: "bg-blue-500" },
  { id: "aviation", label: "Aviation", color: "bg-cyan-500" },
  { id: "cyber", label: "Cyber", color: "bg-purple-500" },
  { id: "economic", label: "Economic", color: "bg-yellow-500" },
  { id: "health", label: "Health", color: "bg-green-500" },
  { id: "environmental", label: "Environmental", color: "bg-emerald-500" },
];

const REGIONS: RegionSummary[] = [
  { name: "North America", signalCount: 12, highestSeverity: 3, primaryDomain: "cyber", riskLevel: "Moderate" },
  { name: "South America", signalCount: 8, highestSeverity: 2, primaryDomain: "economic", riskLevel: "Low" },
  { name: "Western Europe", signalCount: 15, highestSeverity: 3, primaryDomain: "cyber", riskLevel: "Moderate" },
  { name: "Eastern Europe", signalCount: 28, highestSeverity: 5, primaryDomain: "conflict", riskLevel: "Critical" },
  { name: "Middle East", signalCount: 35, highestSeverity: 5, primaryDomain: "conflict", riskLevel: "Critical" },
  { name: "North Africa", signalCount: 18, highestSeverity: 4, primaryDomain: "crisis", riskLevel: "High" },
  { name: "Sub-Saharan Africa", signalCount: 22, highestSeverity: 4, primaryDomain: "health", riskLevel: "High" },
  { name: "Central Asia", signalCount: 10, highestSeverity: 3, primaryDomain: "geopolitical", riskLevel: "Moderate" },
  { name: "South Asia", signalCount: 20, highestSeverity: 4, primaryDomain: "climate", riskLevel: "High" },
  { name: "East Asia", signalCount: 25, highestSeverity: 4, primaryDomain: "geopolitical", riskLevel: "High" },
  { name: "Southeast Asia", signalCount: 14, highestSeverity: 3, primaryDomain: "maritime", riskLevel: "Moderate" },
  { name: "Oceania", signalCount: 6, highestSeverity: 2, primaryDomain: "environmental", riskLevel: "Low" },
];

export default function WorldMapDashboard() {
  const [signals, setSignals] = useState<GlobalSignal[]>([]);
  const [selectedDomains, setSelectedDomains] = useState<string[]>(DOMAINS.map(d => d.id));
  const [minSeverity, setMinSeverity] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  useEffect(() => {
    const mockSignals: GlobalSignal[] = [
      {
        signal_id: "SIG-001",
        domain: "conflict",
        severity: 5,
        title: "Armed Conflict Escalation",
        description: "Significant military activity detected in border region",
        location: { lat: 50.0, lon: 36.0, region: "Eastern Europe" },
        affected_regions: ["Eastern Europe"],
        affected_countries: ["Ukraine", "Russia"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.92,
      },
      {
        signal_id: "SIG-002",
        domain: "cyber",
        severity: 4,
        title: "Critical Infrastructure Attack",
        description: "Ransomware campaign targeting energy sector",
        location: { lat: 51.5, lon: -0.1, region: "Western Europe" },
        affected_regions: ["Western Europe"],
        affected_countries: ["United Kingdom", "Germany"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.85,
      },
      {
        signal_id: "SIG-003",
        domain: "maritime",
        severity: 3,
        title: "Vessel Anomaly Detected",
        description: "Dark voyage detected in shipping lane",
        location: { lat: 12.0, lon: 114.0, region: "Southeast Asia" },
        affected_regions: ["Southeast Asia", "East Asia"],
        affected_countries: ["Philippines", "Vietnam"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.78,
      },
      {
        signal_id: "SIG-004",
        domain: "crisis",
        severity: 5,
        title: "Humanitarian Crisis",
        description: "Large-scale displacement event",
        location: { lat: 31.5, lon: 34.5, region: "Middle East" },
        affected_regions: ["Middle East"],
        affected_countries: ["Gaza", "Israel"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.95,
      },
      {
        signal_id: "SIG-005",
        domain: "health",
        severity: 4,
        title: "Disease Outbreak",
        description: "Emerging infectious disease cluster",
        location: { lat: -5.0, lon: 20.0, region: "Sub-Saharan Africa" },
        affected_regions: ["Sub-Saharan Africa"],
        affected_countries: ["DRC", "Uganda"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.82,
      },
    ];
    setSignals(mockSignals);
  }, []);

  const toggleDomain = (domainId: string) => {
    setSelectedDomains(prev =>
      prev.includes(domainId)
        ? prev.filter(d => d !== domainId)
        : [...prev, domainId]
    );
  };

  const filteredSignals = signals.filter(
    s => selectedDomains.includes(s.domain) && s.severity >= minSeverity
  );

  const getSeverityColor = (severity: number) => {
    if (severity >= 5) return "text-red-500";
    if (severity >= 4) return "text-orange-500";
    if (severity >= 3) return "text-yellow-500";
    return "text-green-500";
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "Critical": return "bg-red-500";
      case "High": return "bg-orange-500";
      case "Moderate": return "bg-yellow-500";
      case "Low": return "bg-green-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Global Signal Map</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Min Severity:</span>
              <select
                value={minSeverity}
                onChange={(e) => setMinSeverity(Number(e.target.value))}
                className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
              >
                {[1, 2, 3, 4, 5].map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            {DOMAINS.map(domain => (
              <button
                key={domain.id}
                onClick={() => toggleDomain(domain.id)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-opacity ${
                  domain.color
                } ${selectedDomains.includes(domain.id) ? "opacity-100" : "opacity-30"}`}
              >
                {domain.label}
              </button>
            ))}
          </div>

          <div className="bg-gray-900 rounded-lg h-96 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <svg viewBox="0 0 1000 500" className="w-full h-full">
                <path
                  d="M150,200 Q200,150 250,180 Q300,210 350,190 Q400,170 450,200 Q500,230 550,210 Q600,190 650,220 Q700,250 750,230 Q800,210 850,240"
                  fill="none"
                  stroke="#4B5563"
                  strokeWidth="2"
                />
                <ellipse cx="500" cy="250" rx="400" ry="200" fill="none" stroke="#374151" strokeWidth="1" />
              </svg>
            </div>

            {filteredSignals.map((signal, index) => (
              <div
                key={signal.signal_id}
                className="absolute w-4 h-4 rounded-full animate-pulse cursor-pointer"
                style={{
                  left: `${((signal.location.lon + 180) / 360) * 100}%`,
                  top: `${((90 - signal.location.lat) / 180) * 100}%`,
                  backgroundColor: DOMAINS.find(d => d.id === signal.domain)?.color.replace("bg-", "") || "#888",
                }}
                title={signal.title}
              />
            ))}

            <div className="text-gray-500 text-center z-10">
              <p className="text-lg font-medium">Interactive World Map</p>
              <p className="text-sm">{filteredSignals.length} active signals displayed</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Regional Overview</h2>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {REGIONS.map(region => (
              <button
                key={region.name}
                onClick={() => setSelectedRegion(region.name === selectedRegion ? null : region.name)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedRegion === region.name
                    ? "bg-blue-600/30 border border-blue-500"
                    : "bg-gray-700/50 hover:bg-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{region.name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${getRiskLevelColor(region.riskLevel)}`}>
                    {region.riskLevel}
                  </span>
                </div>
                <div className="flex items-center justify-between mt-1 text-xs text-gray-400">
                  <span>{region.signalCount} signals</span>
                  <span>Primary: {region.primaryDomain}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Active Signals Feed</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-2 pr-4">ID</th>
                <th className="pb-2 pr-4">Domain</th>
                <th className="pb-2 pr-4">Severity</th>
                <th className="pb-2 pr-4">Title</th>
                <th className="pb-2 pr-4">Region</th>
                <th className="pb-2 pr-4">Countries</th>
                <th className="pb-2 pr-4">Confidence</th>
                <th className="pb-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {filteredSignals.map(signal => (
                <tr key={signal.signal_id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                  <td className="py-2 pr-4 font-mono text-xs">{signal.signal_id}</td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      DOMAINS.find(d => d.id === signal.domain)?.color || "bg-gray-500"
                    }`}>
                      {signal.domain}
                    </span>
                  </td>
                  <td className={`py-2 pr-4 font-bold ${getSeverityColor(signal.severity)}`}>
                    {signal.severity}
                  </td>
                  <td className="py-2 pr-4">{signal.title}</td>
                  <td className="py-2 pr-4 text-gray-400">{signal.affected_regions.join(", ")}</td>
                  <td className="py-2 pr-4 text-gray-400">{signal.affected_countries.join(", ")}</td>
                  <td className="py-2 pr-4">{(signal.confidence_score * 100).toFixed(0)}%</td>
                  <td className="py-2 text-gray-400">
                    {new Date(signal.timestamp).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
