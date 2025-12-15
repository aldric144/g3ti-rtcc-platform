"use client";

import React, { useState, useEffect } from "react";

interface SafetyTrends {
  overall_crime_index: number;
  violent_crime_trend: number;
  property_crime_trend: number;
  by_neighborhood: Record<string, number>;
  improvement_areas: string[];
  concern_areas: string[];
  year_over_year_change: number;
}

export default function SafetyTrendCharts() {
  const [data, setData] = useState<SafetyTrends | null>(null);

  useEffect(() => {
    setData({
      overall_crime_index: 72.5,
      violent_crime_trend: -4.2,
      property_crime_trend: -2.8,
      by_neighborhood: {
        "Downtown Riviera Beach": 68.0,
        "Singer Island": 85.0,
        "West Riviera Beach": 65.0,
        "Port of Palm Beach Area": 78.0,
        "Riviera Beach Heights": 70.0,
      },
      improvement_areas: ["Singer Island", "Port of Palm Beach Area"],
      concern_areas: ["West Riviera Beach"],
      year_over_year_change: -6.5,
    });
  }, []);

  if (!data) {
    return (
      <div className="bg-white rounded-lg border p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "text-green-600";
    if (score >= 65) return "text-blue-600";
    if (score >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  const getBarColor = (score: number): string => {
    if (score >= 80) return "bg-green-500";
    if (score >= 65) return "bg-blue-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Safety Trends</h3>
        <span className={`text-sm font-medium ${
          data.year_over_year_change < 0 ? "text-green-600" : "text-red-600"
        }`}>
          {data.year_over_year_change > 0 ? "+" : ""}{data.year_over_year_change}% YoY
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <p className={`text-2xl font-bold ${getScoreColor(data.overall_crime_index)}`}>
            {data.overall_crime_index}
          </p>
          <p className="text-xs text-blue-600">Safety Index</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className={`text-2xl font-bold ${
            data.violent_crime_trend < 0 ? "text-green-600" : "text-red-600"
          }`}>
            {data.violent_crime_trend > 0 ? "+" : ""}{data.violent_crime_trend}%
          </p>
          <p className="text-xs text-green-600">Violent Crime</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className={`text-2xl font-bold ${
            data.property_crime_trend < 0 ? "text-green-600" : "text-red-600"
          }`}>
            {data.property_crime_trend > 0 ? "+" : ""}{data.property_crime_trend}%
          </p>
          <p className="text-xs text-gray-600">Property Crime</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-3">By Neighborhood</p>
        <div className="space-y-3">
          {Object.entries(data.by_neighborhood).map(([neighborhood, score]) => (
            <div key={neighborhood}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">{neighborhood}</span>
                <span className={`text-xs font-medium ${getScoreColor(score)}`}>
                  {score}
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(score)} rounded-full`}
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs font-medium text-green-700 mb-2">Improving Areas</p>
          <ul className="space-y-1">
            {data.improvement_areas.map((area) => (
              <li key={area} className="text-xs text-gray-600 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {area}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium text-yellow-700 mb-2">Areas of Concern</p>
          <ul className="space-y-1">
            {data.concern_areas.map((area) => (
              <li key={area} className="text-xs text-gray-600 flex items-center">
                <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                {area}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
