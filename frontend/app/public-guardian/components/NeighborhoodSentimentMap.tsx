"use client";

import React, { useState, useEffect } from "react";

interface NeighborhoodData {
  id: string;
  name: string;
  trust_score: number;
  trust_level: string;
  population: number;
  trend: number;
}

export default function NeighborhoodSentimentMap() {
  const [neighborhoods, setNeighborhoods] = useState<NeighborhoodData[]>([]);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<string | null>(null);

  useEffect(() => {
    setNeighborhoods([
      { id: "1", name: "Downtown Riviera Beach", trust_score: 68.0, trust_level: "high", population: 12000, trend: 2.5 },
      { id: "2", name: "Singer Island", trust_score: 85.0, trust_level: "very_high", population: 5000, trend: 1.2 },
      { id: "3", name: "West Riviera Beach", trust_score: 62.0, trust_level: "moderate", population: 15000, trend: -1.5 },
      { id: "4", name: "Port of Palm Beach Area", trust_score: 78.0, trust_level: "high", population: 3000, trend: 3.0 },
      { id: "5", name: "Riviera Beach Heights", trust_score: 70.0, trust_level: "high", population: 8000, trend: 0.8 },
    ]);
  }, []);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "bg-green-500";
    if (score >= 65) return "bg-blue-500";
    if (score >= 50) return "bg-yellow-500";
    if (score >= 35) return "bg-orange-500";
    return "bg-red-500";
  };

  const getScoreTextColor = (score: number): string => {
    if (score >= 80) return "text-green-600";
    if (score >= 65) return "text-blue-600";
    if (score >= 50) return "text-yellow-600";
    if (score >= 35) return "text-orange-600";
    return "text-red-600";
  };

  const getLevelLabel = (level: string): string => {
    switch (level) {
      case "very_high": return "Very High";
      case "high": return "High";
      case "moderate": return "Moderate";
      case "low": return "Low";
      case "very_low": return "Very Low";
      default: return level;
    }
  };

  const selected = neighborhoods.find((n) => n.id === selectedNeighborhood);

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Neighborhood Trust Map</h3>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="relative bg-gray-100 rounded-lg p-4" style={{ minHeight: "300px" }}>
            <div className="grid grid-cols-3 gap-2 h-full">
              {neighborhoods.map((neighborhood) => (
                <div
                  key={neighborhood.id}
                  onClick={() => setSelectedNeighborhood(neighborhood.id)}
                  className={`${getScoreColor(neighborhood.trust_score)} rounded-lg p-3 cursor-pointer transition-all hover:opacity-90 ${
                    selectedNeighborhood === neighborhood.id ? "ring-2 ring-blue-900" : ""
                  }`}
                >
                  <p className="text-white text-sm font-medium truncate">{neighborhood.name}</p>
                  <p className="text-white text-2xl font-bold">{neighborhood.trust_score}</p>
                  <p className="text-white text-xs opacity-80">{getLevelLabel(neighborhood.trust_level)}</p>
                </div>
              ))}
            </div>

            <div className="absolute bottom-2 right-2 bg-white rounded-lg shadow p-2">
              <p className="text-xs font-medium text-gray-700 mb-1">Trust Level</p>
              <div className="flex items-center space-x-2 text-xs">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
                  <span>Very High</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded mr-1"></div>
                  <span>High</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-yellow-500 rounded mr-1"></div>
                  <span>Moderate</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          {selected ? (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">{selected.name}</h4>
              
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500">Trust Score</p>
                  <p className={`text-2xl font-bold ${getScoreTextColor(selected.trust_score)}`}>
                    {selected.trust_score}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500">Trust Level</p>
                  <p className="text-sm font-medium text-gray-900">
                    {getLevelLabel(selected.trust_level)}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500">Population</p>
                  <p className="text-sm font-medium text-gray-900">
                    {selected.population.toLocaleString()}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500">Trend</p>
                  <p className={`text-sm font-medium ${selected.trend >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {selected.trend >= 0 ? "+" : ""}{selected.trend} points
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center h-full">
              <p className="text-gray-500 text-sm text-center">
                Click on a neighborhood to view details
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
