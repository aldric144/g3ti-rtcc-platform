"use client";

import { useState } from "react";

interface TrendData {
  period: string;
  value: number;
}

interface TrendAnalysisResult {
  trend_direction: string;
  trend_strength: number;
  percent_change: number;
  periods: string[];
  values: number[];
  statistics: {
    mean: number;
    median: number;
    std_dev: number;
    min: number;
    max: number;
  };
}

export function TrendAnalytics() {
  const [jurisdiction, setJurisdiction] = useState("ATL");
  const [startDate, setStartDate] = useState("2022-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [granularity, setGranularity] = useState("monthly");
  const [crimeCategory, setCrimeCategory] = useState("");
  const [loading, setLoading] = useState(false);
  const [trendData, setTrendData] = useState<TrendAnalysisResult | null>(null);

  const analyzeTrends = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        jurisdiction,
        start_date: startDate,
        end_date: endDate,
        granularity,
        ...(crimeCategory && { crime_category: crimeCategory }),
      });

      const response = await fetch(`/api/data-lake/analytics/trends?${params}`);
      const data = await response.json();
      setTrendData(data);
    } catch (error) {
      console.error("Failed to analyze trends:", error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case "increasing":
        return "📈";
      case "decreasing":
        return "📉";
      default:
        return "➡️";
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case "increasing":
        return "text-red-400";
      case "decreasing":
        return "text-green-400";
      default:
        return "text-yellow-400";
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Trend Analysis Parameters</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Jurisdiction
            </label>
            <select
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="ATL">Atlanta</option>
              <option value="NYC">New York</option>
              <option value="LAX">Los Angeles</option>
              <option value="CHI">Chicago</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Granularity
            </label>
            <select
              value={granularity}
              onChange={(e) => setGranularity(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Crime Category
            </label>
            <select
              value={crimeCategory}
              onChange={(e) => setCrimeCategory(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="">All Categories</option>
              <option value="violent">Violent</option>
              <option value="property">Property</option>
              <option value="drug">Drug</option>
              <option value="disorder">Disorder</option>
            </select>
          </div>
        </div>

        <button
          onClick={analyzeTrends}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze Trends"}
        </button>
      </div>

      {trendData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Trend Direction</div>
              <div
                className={`text-2xl font-bold ${getTrendColor(trendData.trend_direction)}`}
              >
                {getTrendIcon(trendData.trend_direction)}{" "}
                {trendData.trend_direction.charAt(0).toUpperCase() +
                  trendData.trend_direction.slice(1)}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Percent Change</div>
              <div
                className={`text-2xl font-bold ${trendData.percent_change > 0 ? "text-red-400" : trendData.percent_change < 0 ? "text-green-400" : "text-gray-400"}`}
              >
                {trendData.percent_change > 0 ? "+" : ""}
                {trendData.percent_change.toFixed(1)}%
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Trend Strength</div>
              <div className="text-2xl font-bold text-blue-400">
                {(trendData.trend_strength * 100).toFixed(0)}%
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Data Points</div>
              <div className="text-2xl font-bold text-white">
                {trendData.periods.length}
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Statistical Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <div className="text-sm text-gray-400">Mean</div>
                <div className="text-xl font-semibold">
                  {trendData.statistics.mean.toFixed(1)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Median</div>
                <div className="text-xl font-semibold">
                  {trendData.statistics.median.toFixed(1)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Std Dev</div>
                <div className="text-xl font-semibold">
                  {trendData.statistics.std_dev.toFixed(1)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Min</div>
                <div className="text-xl font-semibold">
                  {trendData.statistics.min.toFixed(0)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Max</div>
                <div className="text-xl font-semibold">
                  {trendData.statistics.max.toFixed(0)}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Trend Visualization</h3>
            <div className="h-64 flex items-end space-x-1">
              {trendData.values.map((value, index) => {
                const maxValue = Math.max(...trendData.values);
                const height = maxValue > 0 ? (value / maxValue) * 100 : 0;
                return (
                  <div
                    key={index}
                    className="flex-1 bg-blue-500 hover:bg-blue-400 transition-colors rounded-t"
                    style={{ height: `${height}%` }}
                    title={`${trendData.periods[index]}: ${value}`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>{trendData.periods[0]}</span>
              <span>{trendData.periods[trendData.periods.length - 1]}</span>
            </div>
          </div>
        </>
      )}

      {!trendData && !loading && (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">No Data Yet</h3>
          <p className="text-gray-400">
            Configure your parameters and click &quot;Analyze Trends&quot; to
            view historical crime trends.
          </p>
        </div>
      )}
    </div>
  );
}
