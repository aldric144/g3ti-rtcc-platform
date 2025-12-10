"use client";

import { useState, useEffect } from "react";

interface Entity {
  id: string;
  type: "person" | "vehicle" | "weapon" | "incident" | "location" | "pattern";
  name: string;
  attributes: Record<string, string>;
  riskScore: number;
  lastSeen: string;
}

interface Correlation {
  id: string;
  sourceEntity: Entity;
  targetEntity: Entity;
  correlationType: string;
  strength: "definite" | "strong" | "moderate" | "weak" | "possible";
  confidence: number;
  evidence: string[];
  timestamp: string;
}

const entityTypeColors = {
  person: { bg: "bg-blue-600", text: "text-blue-300", border: "border-blue-500" },
  vehicle: { bg: "bg-green-600", text: "text-green-300", border: "border-green-500" },
  weapon: { bg: "bg-red-600", text: "text-red-300", border: "border-red-500" },
  incident: { bg: "bg-yellow-600", text: "text-yellow-300", border: "border-yellow-500" },
  location: { bg: "bg-purple-600", text: "text-purple-300", border: "border-purple-500" },
  pattern: { bg: "bg-cyan-600", text: "text-cyan-300", border: "border-cyan-500" },
};

const strengthColors = {
  definite: "bg-green-600 text-white",
  strong: "bg-blue-600 text-white",
  moderate: "bg-yellow-600 text-black",
  weak: "bg-orange-600 text-white",
  possible: "bg-gray-600 text-white",
};

const mockEntities: Entity[] = [
  {
    id: "ent-001",
    type: "person",
    name: "John Doe",
    attributes: { dob: "1985-03-15", ssn: "***-**-1234" },
    riskScore: 85,
    lastSeen: new Date().toISOString(),
  },
  {
    id: "ent-002",
    type: "vehicle",
    name: "Black SUV - ABC123",
    attributes: { make: "Ford", model: "Explorer", year: "2020" },
    riskScore: 72,
    lastSeen: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "ent-003",
    type: "weapon",
    name: "Glock 19 - SN12345",
    attributes: { type: "Handgun", caliber: "9mm" },
    riskScore: 90,
    lastSeen: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: "ent-004",
    type: "incident",
    name: "Armed Robbery - Case #2024-1234",
    attributes: { type: "Robbery", status: "Active" },
    riskScore: 88,
    lastSeen: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: "ent-005",
    type: "location",
    name: "123 Main St, District 5",
    attributes: { type: "Commercial", riskZone: "High" },
    riskScore: 65,
    lastSeen: new Date(Date.now() - 900000).toISOString(),
  },
  {
    id: "ent-006",
    type: "pattern",
    name: "Residential Burglary Series",
    attributes: { incidents: "5", timeframe: "30 days" },
    riskScore: 78,
    lastSeen: new Date(Date.now() - 600000).toISOString(),
  },
];

const mockCorrelations: Correlation[] = [
  {
    id: "corr-001",
    sourceEntity: mockEntities[0],
    targetEntity: mockEntities[1],
    correlationType: "ownership",
    strength: "definite",
    confidence: 0.98,
    evidence: ["DMV records", "Traffic stop 2024-01-15"],
    timestamp: new Date().toISOString(),
  },
  {
    id: "corr-002",
    sourceEntity: mockEntities[0],
    targetEntity: mockEntities[2],
    correlationType: "possession",
    strength: "strong",
    confidence: 0.85,
    evidence: ["Arrest record", "ATF trace"],
    timestamp: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "corr-003",
    sourceEntity: mockEntities[0],
    targetEntity: mockEntities[3],
    correlationType: "suspect",
    strength: "moderate",
    confidence: 0.72,
    evidence: ["Witness statement", "Video footage"],
    timestamp: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: "corr-004",
    sourceEntity: mockEntities[1],
    targetEntity: mockEntities[4],
    correlationType: "geographic",
    strength: "strong",
    confidence: 0.88,
    evidence: ["LPR hit", "Surveillance footage"],
    timestamp: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: "corr-005",
    sourceEntity: mockEntities[3],
    targetEntity: mockEntities[5],
    correlationType: "pattern_match",
    strength: "moderate",
    confidence: 0.75,
    evidence: ["MO analysis", "Temporal correlation"],
    timestamp: new Date(Date.now() - 900000).toISOString(),
  },
];

export default function EntityCorrelationViewer() {
  const [entities, setEntities] = useState<Entity[]>(mockEntities);
  const [correlations, setCorrelations] = useState<Correlation[]>(mockCorrelations);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStrength, setFilterStrength] = useState<string>("all");

  const filteredEntities =
    filterType === "all"
      ? entities
      : entities.filter((e) => e.type === filterType);

  const filteredCorrelations = correlations.filter((c) => {
    if (filterStrength !== "all" && c.strength !== filterStrength) return false;
    if (selectedEntity) {
      return (
        c.sourceEntity.id === selectedEntity.id ||
        c.targetEntity.id === selectedEntity.id
      );
    }
    return true;
  });

  const entityCounts = entities.reduce(
    (acc, e) => {
      acc[e.type] = (acc[e.type] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Entity Correlation Viewer</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Entity Type:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Types</option>
              <option value="person">Person</option>
              <option value="vehicle">Vehicle</option>
              <option value="weapon">Weapon</option>
              <option value="incident">Incident</option>
              <option value="location">Location</option>
              <option value="pattern">Pattern</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Strength:</span>
            <select
              value={filterStrength}
              onChange={(e) => setFilterStrength(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Strengths</option>
              <option value="definite">Definite</option>
              <option value="strong">Strong</option>
              <option value="moderate">Moderate</option>
              <option value="weak">Weak</option>
              <option value="possible">Possible</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-2 mb-4">
        {(["person", "vehicle", "weapon", "incident", "location", "pattern"] as const).map(
          (type) => {
            const colors = entityTypeColors[type];
            return (
              <div
                key={type}
                className={`${colors.bg} rounded p-3 text-center text-white`}
              >
                <div className="text-2xl font-bold">{entityCounts[type] || 0}</div>
                <div className="text-xs capitalize">{type}s</div>
              </div>
            );
          }
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">
            Entities ({filteredEntities.length})
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredEntities.map((entity) => {
              const colors = entityTypeColors[entity.type];
              const isSelected = selectedEntity?.id === entity.id;
              return (
                <button
                  key={entity.id}
                  onClick={() =>
                    setSelectedEntity(isSelected ? null : entity)
                  }
                  className={`w-full text-left p-3 rounded border ${colors.border} ${
                    isSelected ? colors.bg : "bg-gray-700"
                  } hover:opacity-80 transition-opacity`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${colors.text}`}>
                      {entity.name}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${colors.bg} text-white`}
                    >
                      {entity.type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-400">
                      Risk: {entity.riskScore}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(entity.lastSeen).toLocaleTimeString()}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="col-span-2 bg-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">
            Correlations ({filteredCorrelations.length})
            {selectedEntity && (
              <span className="ml-2 text-blue-400">
                for {selectedEntity.name}
              </span>
            )}
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredCorrelations.map((correlation) => {
              const sourceColors = entityTypeColors[correlation.sourceEntity.type];
              const targetColors = entityTypeColors[correlation.targetEntity.type];
              return (
                <div
                  key={correlation.id}
                  className="bg-gray-700 rounded-lg p-3"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`${strengthColors[correlation.strength]} px-2 py-0.5 rounded text-xs font-medium`}
                    >
                      {correlation.strength.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400">
                      {correlation.correlationType}
                    </span>
                    <span className="text-xs text-gray-400">
                      Confidence: {(correlation.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`flex-1 p-2 rounded border ${sourceColors.border} bg-gray-800`}
                    >
                      <div className={`text-sm font-medium ${sourceColors.text}`}>
                        {correlation.sourceEntity.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {correlation.sourceEntity.type}
                      </div>
                    </div>
                    <div className="text-gray-500">→</div>
                    <div
                      className={`flex-1 p-2 rounded border ${targetColors.border} bg-gray-800`}
                    >
                      <div className={`text-sm font-medium ${targetColors.text}`}>
                        {correlation.targetEntity.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {correlation.targetEntity.type}
                      </div>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="text-xs text-gray-400">Evidence:</div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {correlation.evidence.map((ev, idx) => (
                        <span
                          key={idx}
                          className="bg-gray-600 px-2 py-0.5 rounded text-xs"
                        >
                          {ev}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {selectedEntity && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="font-semibold mb-3">
            Entity Details: {selectedEntity.name}
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-400">Type</div>
              <div className="font-medium capitalize">{selectedEntity.type}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Risk Score</div>
              <div
                className={`font-medium ${
                  selectedEntity.riskScore >= 80
                    ? "text-red-400"
                    : selectedEntity.riskScore >= 60
                    ? "text-yellow-400"
                    : "text-green-400"
                }`}
              >
                {selectedEntity.riskScore}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Last Seen</div>
              <div className="font-medium">
                {new Date(selectedEntity.lastSeen).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Correlations</div>
              <div className="font-medium">
                {
                  correlations.filter(
                    (c) =>
                      c.sourceEntity.id === selectedEntity.id ||
                      c.targetEntity.id === selectedEntity.id
                  ).length
                }
              </div>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-400 mb-2">Attributes</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(selectedEntity.attributes).map(([key, value]) => (
                <span
                  key={key}
                  className="bg-gray-700 px-3 py-1 rounded text-sm"
                >
                  <span className="text-gray-400">{key}:</span> {value}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
