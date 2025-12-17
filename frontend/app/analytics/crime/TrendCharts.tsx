'use client';

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface TimeseriesPoint {
  timestamp: string;
  count: number;
  violent_count: number;
  property_count: number;
  other_count: number;
}

interface TrendInfo {
  direction: string;
  slope: number;
  change_percent: number;
  confidence: number;
}

interface Anomaly {
  timestamp: string;
  expected_count: number;
  actual_count: number;
  deviation: number;
  severity: string;
  description: string;
}

interface TimeseriesData {
  hourly_data: TimeseriesPoint[];
  daily_data: TimeseriesPoint[];
  trend: TrendInfo;
  anomalies: Anomaly[];
  total_incidents: number;
  average_daily: number;
  peak_hour: number;
  peak_day: string;
}

export default function TrendCharts() {
  const [data, setData] = useState<TimeseriesData | null>(null);
  const [days, setDays] = useState(30);
  const [viewMode, setViewMode] = useState<'daily' | 'hourly'>('daily');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/crime/timeseries?days=${days}`);
      if (response.ok) {
        setData(await response.json());
      } else {
        setError('Failed to load trend data');
      }
    } catch (err) {
      setError('Error loading trend data');
    } finally {
      setIsLoading(false);
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'increasing': return 'text-red-400';
      case 'decreasing': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500';
      default: return 'bg-blue-500/20 text-blue-400 border-blue-500';
    }
  };

  const getMaxCount = (points: TimeseriesPoint[]) => {
    return Math.max(...points.map(p => p.count), 1);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-400 text-center py-8">{error}</div>;
  }

  const displayData = viewMode === 'daily' ? data?.daily_data : data?.hourly_data;
  const maxCount = displayData ? getMaxCount(displayData) : 1;

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2">
          <span className="text-gray-400 self-center">Period:</span>
          {[7, 14, 30, 60].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 rounded ${
                days === d
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('daily')}
            className={`px-3 py-1 rounded ${
              viewMode === 'daily'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Daily
          </button>
          <button
            onClick={() => setViewMode('hourly')}
            className={`px-3 py-1 rounded ${
              viewMode === 'hourly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Hourly
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Total Incidents</div>
          <div className="text-2xl font-bold text-white">{data?.total_incidents || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Daily Average</div>
          <div className="text-2xl font-bold text-blue-400">{data?.average_daily.toFixed(1) || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Peak Hour</div>
          <div className="text-2xl font-bold text-purple-400">{data?.peak_hour || 0}:00</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Peak Day</div>
          <div className="text-xl font-bold text-orange-400">{data?.peak_day || 'N/A'}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Trend</div>
          <div className={`text-xl font-bold ${getTrendColor(data?.trend.direction || 'stable')}`}>
            {getTrendIcon(data?.trend.direction || 'stable')} {data?.trend.change_percent.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          {viewMode === 'daily' ? 'Daily' : 'Hourly'} Crime Timeline
        </h3>
        <div className="h-64 flex items-end gap-1">
          {displayData?.slice(-50).map((point, idx) => (
            <div
              key={idx}
              className="flex-1 flex flex-col items-center group relative"
            >
              {/* Stacked bar */}
              <div
                className="w-full flex flex-col-reverse"
                style={{ height: `${(point.count / maxCount) * 100}%`, minHeight: '4px' }}
              >
                <div
                  className="bg-red-500"
                  style={{ height: `${point.count > 0 ? (point.violent_count / point.count) * 100 : 0}%` }}
                />
                <div
                  className="bg-yellow-500"
                  style={{ height: `${point.count > 0 ? (point.property_count / point.count) * 100 : 0}%` }}
                />
                <div
                  className="bg-blue-500"
                  style={{ height: `${point.count > 0 ? (point.other_count / point.count) * 100 : 0}%` }}
                />
              </div>
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs p-2 rounded shadow-lg z-10 whitespace-nowrap">
                <div className="font-semibold">{point.timestamp}</div>
                <div>Total: {point.count}</div>
                <div className="text-red-400">Violent: {point.violent_count}</div>
                <div className="text-yellow-400">Property: {point.property_count}</div>
                <div className="text-blue-400">Other: {point.other_count}</div>
              </div>
            </div>
          ))}
        </div>
        {/* Legend */}
        <div className="flex justify-center gap-6 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-400 text-sm">Violent</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span className="text-gray-400 text-sm">Property</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-gray-400 text-sm">Other</span>
          </div>
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Trend Analysis</h3>
          {data?.trend && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Direction</span>
                <span className={`font-semibold capitalize ${getTrendColor(data.trend.direction)}`}>
                  {getTrendIcon(data.trend.direction)} {data.trend.direction}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Change</span>
                <span className={`font-semibold ${data.trend.change_percent >= 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {data.trend.change_percent >= 0 ? '+' : ''}{data.trend.change_percent.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Slope</span>
                <span className="text-white">{data.trend.slope.toFixed(4)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Confidence</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${data.trend.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-white">{(data.trend.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Anomalies */}
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Detected Anomalies ({data?.anomalies.length || 0})
          </h3>
          <div className="space-y-3 max-h-48 overflow-y-auto">
            {data?.anomalies.map((anomaly, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border ${getSeverityColor(anomaly.severity)}`}
              >
                <div className="flex justify-between items-start">
                  <div className="text-sm font-medium">{anomaly.timestamp}</div>
                  <span className="text-xs uppercase font-semibold">{anomaly.severity}</span>
                </div>
                <div className="text-sm mt-1">{anomaly.description}</div>
                <div className="text-xs mt-1 opacity-75">
                  Expected: {anomaly.expected_count.toFixed(1)} | Actual: {anomaly.actual_count} | Deviation: {anomaly.deviation.toFixed(2)}σ
                </div>
              </div>
            ))}
            {(!data?.anomalies || data.anomalies.length === 0) && (
              <div className="text-gray-500 text-center py-4">No anomalies detected</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
