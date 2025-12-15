"use client";

import React, { useState, useEffect } from "react";

interface ResponseTimeData {
  average_response_time_seconds: number;
  median_response_time_seconds: number;
  emergency_avg_seconds: number;
  non_emergency_avg_seconds: number;
  by_priority: Record<string, number>;
  by_district: Record<string, number>;
  target_met_percentage: number;
  trend_vs_previous: number;
}

export default function ResponseTimeCard() {
  const [data, setData] = useState<ResponseTimeData | null>(null);

  useEffect(() => {
    setData({
      average_response_time_seconds: 420,
      median_response_time_seconds: 360,
      emergency_avg_seconds: 240,
      non_emergency_avg_seconds: 720,
      by_priority: {
        priority_1: 180,
        priority_2: 360,
        priority_3: 600,
        priority_4: 900,
      },
      by_district: {
        Downtown: 300,
        "Singer Island": 420,
        West: 480,
        "Port Area": 360,
        Heights: 450,
      },
      target_met_percentage: 87.3,
      trend_vs_previous: -5.5,
    });
  }, []);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

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

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Response Times</h3>
        <span className={`text-sm font-medium px-2 py-1 rounded ${
          data.target_met_percentage >= 85 ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
        }`}>
          {data.target_met_percentage}% Target Met
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">
            {formatTime(data.average_response_time_seconds)}
          </p>
          <p className="text-xs text-blue-600">Average Response</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-900">
            {formatTime(data.emergency_avg_seconds)}
          </p>
          <p className="text-xs text-green-600">Emergency Avg</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">By Priority Level</p>
        <div className="space-y-2">
          {Object.entries(data.by_priority).map(([priority, seconds]) => (
            <div key={priority} className="flex items-center justify-between">
              <span className="text-xs text-gray-600 capitalize">
                {priority.replace("_", " ")}
              </span>
              <span className="text-xs font-medium text-gray-900">
                {formatTime(seconds)}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">By District</p>
        <div className="space-y-2">
          {Object.entries(data.by_district).map(([district, seconds]) => (
            <div key={district} className="flex items-center justify-between">
              <span className="text-xs text-gray-600">{district}</span>
              <span className="text-xs font-medium text-gray-900">
                {formatTime(seconds)}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Trend vs Previous Period</span>
          <span className={`text-sm font-medium ${
            data.trend_vs_previous < 0 ? "text-green-600" : "text-red-600"
          }`}>
            {data.trend_vs_previous > 0 ? "+" : ""}{data.trend_vs_previous}%
          </span>
        </div>
      </div>
    </div>
  );
}
