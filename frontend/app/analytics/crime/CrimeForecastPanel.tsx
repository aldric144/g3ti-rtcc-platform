'use client';

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface HourlyForecast {
  hour: number;
  date: string;
  predicted_count: number;
  confidence_low: number;
  confidence_high: number;
  risk_level: string;
}

interface DailyForecast {
  date: string;
  day_of_week: string;
  predicted_count: number;
  confidence_low: number;
  confidence_high: number;
  risk_level: string;
  violent_predicted: number;
  property_predicted: number;
}

interface SeasonalPattern {
  pattern_type: string;
  description: string;
  peak_periods: string[];
  low_periods: string[];
  strength: number;
}

interface PatrolRecommendation {
  sector: string;
  start_time: string;
  end_time: string;
  priority: string;
  reason: string;
  expected_incidents: number;
  recommended_units: number;
}

interface ForecastData {
  hourly_forecast: HourlyForecast[];
  daily_forecast: DailyForecast[];
  seasonal_patterns: SeasonalPattern[];
  patrol_recommendations: PatrolRecommendation[];
  model_accuracy: number;
  last_updated: string;
}

export default function CrimeForecastPanel() {
  const [data, setData] = useState<ForecastData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'hourly' | 'daily'>('daily');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/crime/forecast?hours_ahead=48&days_ahead=7`);
      if (response.ok) {
        setData(await response.json());
      } else {
        setError('Failed to load forecast data');
      }
    } catch (err) {
      setError('Error loading forecast data');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      default: return 'bg-green-500 text-white';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-500 border-red-500 bg-red-500/10';
      case 'high': return 'text-orange-500 border-orange-500 bg-orange-500/10';
      case 'medium': return 'text-yellow-500 border-yellow-500 bg-yellow-500/10';
      default: return 'text-green-500 border-green-500 bg-green-500/10';
    }
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

  return (
    <div className="space-y-6">
      {/* Model Info */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="text-gray-400">
            Model Accuracy: 
            <span className="ml-2 text-white font-semibold">
              {((data?.model_accuracy || 0) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-gray-400">
            Last Updated: 
            <span className="ml-2 text-white">
              {data?.last_updated ? new Date(data.last_updated).toLocaleString() : 'N/A'}
            </span>
          </div>
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
            7-Day Forecast
          </button>
          <button
            onClick={() => setViewMode('hourly')}
            className={`px-3 py-1 rounded ${
              viewMode === 'hourly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            48-Hour Forecast
          </button>
        </div>
      </div>

      {/* Forecast Display */}
      {viewMode === 'daily' ? (
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">7-Day Crime Forecast</h3>
          <div className="grid grid-cols-7 gap-2">
            {data?.daily_forecast.map((day, idx) => (
              <div
                key={idx}
                className="bg-gray-600/50 rounded-lg p-4 text-center"
              >
                <div className="text-gray-400 text-sm">{day.day_of_week.slice(0, 3)}</div>
                <div className="text-gray-500 text-xs">{day.date.slice(5)}</div>
                <div className="text-2xl font-bold text-white my-2">
                  {day.predicted_count.toFixed(0)}
                </div>
                <div className={`text-xs px-2 py-1 rounded ${getRiskColor(day.risk_level)}`}>
                  {day.risk_level.toUpperCase()}
                </div>
                <div className="mt-2 text-xs text-gray-400">
                  <div>V: {day.violent_predicted.toFixed(1)}</div>
                  <div>P: {day.property_predicted.toFixed(1)}</div>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {day.confidence_low.toFixed(0)}-{day.confidence_high.toFixed(0)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">48-Hour Crime Forecast</h3>
          <div className="h-48 flex items-end gap-0.5">
            {data?.hourly_forecast.map((hour, idx) => (
              <div
                key={idx}
                className="flex-1 group relative"
              >
                <div
                  className={`w-full rounded-t ${getRiskColor(hour.risk_level)}`}
                  style={{
                    height: `${Math.max((hour.predicted_count / 5) * 100, 10)}%`,
                  }}
                />
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block bg-gray-800 text-white text-xs p-2 rounded shadow-lg z-10 whitespace-nowrap">
                  <div className="font-semibold">{hour.date} {hour.hour}:00</div>
                  <div>Predicted: {hour.predicted_count.toFixed(1)}</div>
                  <div>Range: {hour.confidence_low.toFixed(1)} - {hour.confidence_high.toFixed(1)}</div>
                  <div className="capitalize">Risk: {hour.risk_level}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>Now</span>
            <span>+24h</span>
            <span>+48h</span>
          </div>
        </div>
      )}

      {/* High Risk Time Windows */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">High-Risk Time Windows</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.hourly_forecast
            .filter(h => h.risk_level === 'high' || h.risk_level === 'critical')
            .slice(0, 6)
            .map((hour, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border ${
                  hour.risk_level === 'critical'
                    ? 'border-red-500 bg-red-500/10'
                    : 'border-orange-500 bg-orange-500/10'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-white font-medium">{hour.date}</div>
                    <div className="text-gray-400">{hour.hour}:00 - {(hour.hour + 1) % 24}:00</div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(hour.risk_level)}`}>
                    {hour.risk_level.toUpperCase()}
                  </span>
                </div>
                <div className="mt-2 text-lg font-bold text-white">
                  ~{hour.predicted_count.toFixed(1)} incidents
                </div>
              </div>
            ))}
          {data?.hourly_forecast.filter(h => h.risk_level === 'high' || h.risk_level === 'critical').length === 0 && (
            <div className="col-span-full text-gray-500 text-center py-4">
              No high-risk time windows identified
            </div>
          )}
        </div>
      </div>

      {/* Seasonal Patterns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Seasonal Patterns</h3>
          <div className="space-y-4">
            {data?.seasonal_patterns.map((pattern, idx) => (
              <div key={idx} className="border-b border-gray-600 pb-4 last:border-0">
                <div className="flex justify-between items-start">
                  <div className="text-white font-medium capitalize">{pattern.pattern_type} Pattern</div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${pattern.strength * 100}%` }}
                      />
                    </div>
                    <span className="text-gray-400 text-sm">{(pattern.strength * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <p className="text-gray-400 text-sm mt-1">{pattern.description}</p>
                <div className="mt-2 flex gap-4">
                  <div>
                    <span className="text-gray-500 text-xs">Peak:</span>
                    <div className="flex gap-1 mt-1">
                      {pattern.peak_periods.map((p, i) => (
                        <span key={i} className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs">Low:</span>
                    <div className="flex gap-1 mt-1">
                      {pattern.low_periods.map((p, i) => (
                        <span key={i} className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded text-xs">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Patrol Recommendations */}
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Patrol Recommendations</h3>
          <div className="space-y-3">
            {data?.patrol_recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border ${getPriorityColor(rec.priority)}`}
              >
                <div className="flex justify-between items-start">
                  <div className="font-medium">{rec.sector}</div>
                  <span className="text-xs uppercase font-semibold">{rec.priority}</span>
                </div>
                <div className="text-sm mt-1 opacity-80">
                  {rec.start_time} - {rec.end_time}
                </div>
                <div className="text-sm mt-2">{rec.reason}</div>
                <div className="flex justify-between mt-2 text-xs opacity-75">
                  <span>Expected: ~{rec.expected_incidents} incidents</span>
                  <span>Units: {rec.recommended_units}</span>
                </div>
              </div>
            ))}
            {(!data?.patrol_recommendations || data.patrol_recommendations.length === 0) && (
              <div className="text-gray-500 text-center py-4">
                No patrol recommendations available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
