"use client";

import React, { useState, useEffect } from "react";

interface CallsForService {
  total_calls: number;
  by_category: Record<string, number>;
  average_daily: number;
  trend_vs_previous: number;
}

export default function TransparencyMetricsPanel() {
  const [data, setData] = useState<CallsForService | null>(null);
  const [period, setPeriod] = useState<"weekly" | "monthly" | "quarterly">("weekly");

  useEffect(() => {
    setData({
      total_calls: 315,
      by_category: {
        emergency: 47,
        non_emergency: 79,
        traffic: 38,
        property_crime: 32,
        violent_crime: 16,
        domestic: 25,
        mental_health: 19,
        community_service: 32,
        welfare_check: 16,
        other: 11,
      },
      average_daily: 45,
      trend_vs_previous: -3.2,
    });
  }, [period]);

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

  const categories = Object.entries(data.by_category).sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...Object.values(data.by_category));

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Calls for Service</h3>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value as typeof period)}
          className="text-sm border rounded-md px-2 py-1"
        >
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">{data.total_calls}</p>
          <p className="text-xs text-blue-600">Total Calls</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-900">{data.average_daily}</p>
          <p className="text-xs text-green-600">Daily Average</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className={`text-2xl font-bold ${data.trend_vs_previous < 0 ? "text-green-600" : "text-red-600"}`}>
            {data.trend_vs_previous > 0 ? "+" : ""}{data.trend_vs_previous}%
          </p>
          <p className="text-xs text-gray-600">vs Previous</p>
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700 mb-3">By Category</p>
        {categories.map(([category, count]) => (
          <div key={category} className="flex items-center">
            <span className="text-xs text-gray-600 w-28 capitalize">
              {category.replace("_", " ")}
            </span>
            <div className="flex-1 mx-2">
              <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${(count / maxCount) * 100}%` }}
                ></div>
              </div>
            </div>
            <span className="text-xs font-medium text-gray-900 w-8 text-right">
              {count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
