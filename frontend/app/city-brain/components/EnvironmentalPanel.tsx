"use client";

import { useState, useEffect } from "react";

interface WeatherData {
  current_conditions: {
    temperature_f: number;
    humidity_percent: number;
    wind_speed_mph: number;
    wind_direction: string;
    conditions: string;
    visibility_miles: number;
    pressure_mb: number;
    uv_index: number;
  } | null;
  marine_conditions: {
    wave_height_ft: number;
    water_temperature_f: number;
    tide_level: string;
    rip_current_risk: string;
    current_speed_knots: number;
  } | null;
  air_quality: {
    aqi: number;
    pm25: number;
    pm10: number;
    ozone: number;
    category: string;
    health_advisory: string | null;
  } | null;
  active_alerts: Array<{
    alert_id: string;
    event_type: string;
    headline: string;
    severity: string;
    expires: string;
  }>;
}

export default function EnvironmentalPanel() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWeatherData();
    const interval = setInterval(fetchWeatherData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchWeatherData = async () => {
    try {
      const response = await fetch("/api/citybrain/city/weather");
      if (!response.ok) throw new Error("Failed to fetch weather data");
      const data = await response.json();
      setWeatherData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "text-green-400";
    if (aqi <= 100) return "text-yellow-400";
    if (aqi <= 150) return "text-orange-400";
    if (aqi <= 200) return "text-red-400";
    if (aqi <= 300) return "text-purple-400";
    return "text-red-600";
  };

  const getAQIBg = (aqi: number) => {
    if (aqi <= 50) return "bg-green-500/20";
    if (aqi <= 100) return "bg-yellow-500/20";
    if (aqi <= 150) return "bg-orange-500/20";
    if (aqi <= 200) return "bg-red-500/20";
    return "bg-purple-500/20";
  };

  const getRipCurrentColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "low": return "text-green-400";
      case "moderate": return "text-yellow-400";
      case "high": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "extreme": return "bg-red-600";
      case "severe": return "bg-orange-600";
      case "moderate": return "bg-yellow-600";
      case "minor": return "bg-blue-600";
      default: return "bg-gray-600";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
        <p className="text-red-400">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Environmental Conditions</h2>
        <button
          onClick={fetchWeatherData}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
        >
          Refresh
        </button>
      </div>

      {weatherData?.active_alerts && weatherData.active_alerts.length > 0 && (
        <div className="space-y-2">
          {weatherData.active_alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`${getSeverityColor(alert.severity)} rounded-lg p-4`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">⚠️</span>
                  <span className="font-bold">{alert.event_type}</span>
                </div>
                <span className="text-sm opacity-75">
                  Expires: {new Date(alert.expires).toLocaleString()}
                </span>
              </div>
              <p className="mt-2 text-sm">{alert.headline}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <span>🌤️</span>
            <span>Current Weather</span>
          </h3>
          {weatherData?.current_conditions ? (
            <div className="space-y-3">
              <div className="text-center py-4">
                <p className="text-5xl font-bold text-white">
                  {weatherData.current_conditions.temperature_f}°F
                </p>
                <p className="text-lg text-gray-400 mt-1">
                  {weatherData.current_conditions.conditions}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700/50 rounded p-2">
                  <p className="text-xs text-gray-400">Humidity</p>
                  <p className="text-sm text-white">
                    {weatherData.current_conditions.humidity_percent}%
                  </p>
                </div>
                <div className="bg-gray-700/50 rounded p-2">
                  <p className="text-xs text-gray-400">Wind</p>
                  <p className="text-sm text-white">
                    {weatherData.current_conditions.wind_speed_mph} mph{" "}
                    {weatherData.current_conditions.wind_direction}
                  </p>
                </div>
                <div className="bg-gray-700/50 rounded p-2">
                  <p className="text-xs text-gray-400">Visibility</p>
                  <p className="text-sm text-white">
                    {weatherData.current_conditions.visibility_miles} mi
                  </p>
                </div>
                <div className="bg-gray-700/50 rounded p-2">
                  <p className="text-xs text-gray-400">Pressure</p>
                  <p className="text-sm text-white">
                    {weatherData.current_conditions.pressure_mb} mb
                  </p>
                </div>
                <div className="bg-gray-700/50 rounded p-2">
                  <p className="text-xs text-gray-400">UV Index</p>
                  <p className="text-sm text-white">
                    {weatherData.current_conditions.uv_index}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No weather data available</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <span>🌊</span>
            <span>Marine Conditions</span>
          </h3>
          {weatherData?.marine_conditions ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700/50 rounded p-3">
                  <p className="text-xs text-gray-400">Wave Height</p>
                  <p className="text-lg font-bold text-white">
                    {weatherData.marine_conditions.wave_height_ft} ft
                  </p>
                </div>
                <div className="bg-gray-700/50 rounded p-3">
                  <p className="text-xs text-gray-400">Water Temp</p>
                  <p className="text-lg font-bold text-white">
                    {weatherData.marine_conditions.water_temperature_f}°F
                  </p>
                </div>
              </div>
              <div className="bg-gray-700/50 rounded p-3">
                <p className="text-xs text-gray-400">Tide Level</p>
                <p className="text-sm text-white capitalize">
                  {weatherData.marine_conditions.tide_level}
                </p>
              </div>
              <div className="bg-gray-700/50 rounded p-3">
                <p className="text-xs text-gray-400">Rip Current Risk</p>
                <p className={`text-sm font-medium capitalize ${getRipCurrentColor(weatherData.marine_conditions.rip_current_risk)}`}>
                  {weatherData.marine_conditions.rip_current_risk}
                </p>
              </div>
              <div className="bg-gray-700/50 rounded p-3">
                <p className="text-xs text-gray-400">Current Speed</p>
                <p className="text-sm text-white">
                  {weatherData.marine_conditions.current_speed_knots} knots
                </p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No marine data available</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <span>💨</span>
            <span>Air Quality</span>
          </h3>
          {weatherData?.air_quality ? (
            <div className="space-y-3">
              <div className={`text-center py-4 rounded-lg ${getAQIBg(weatherData.air_quality.aqi)}`}>
                <p className={`text-5xl font-bold ${getAQIColor(weatherData.air_quality.aqi)}`}>
                  {weatherData.air_quality.aqi}
                </p>
                <p className="text-sm text-gray-400 mt-1">AQI</p>
                <p className={`text-sm font-medium mt-1 ${getAQIColor(weatherData.air_quality.aqi)}`}>
                  {weatherData.air_quality.category}
                </p>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-gray-700/50 rounded p-2 text-center">
                  <p className="text-xs text-gray-400">PM2.5</p>
                  <p className="text-sm text-white">{weatherData.air_quality.pm25}</p>
                </div>
                <div className="bg-gray-700/50 rounded p-2 text-center">
                  <p className="text-xs text-gray-400">PM10</p>
                  <p className="text-sm text-white">{weatherData.air_quality.pm10}</p>
                </div>
                <div className="bg-gray-700/50 rounded p-2 text-center">
                  <p className="text-xs text-gray-400">Ozone</p>
                  <p className="text-sm text-white">{weatherData.air_quality.ozone}</p>
                </div>
              </div>
              {weatherData.air_quality.health_advisory && (
                <div className="bg-yellow-500/20 border border-yellow-500/50 rounded p-2">
                  <p className="text-xs text-yellow-400">
                    {weatherData.air_quality.health_advisory}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">No air quality data available</p>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Environmental Monitoring Locations</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-700/50 rounded p-3">
            <p className="text-sm font-medium">Singer Island Beach</p>
            <p className="text-xs text-gray-400">Beach monitoring station</p>
          </div>
          <div className="bg-gray-700/50 rounded p-3">
            <p className="text-sm font-medium">Riviera Beach Marina</p>
            <p className="text-xs text-gray-400">Marine weather station</p>
          </div>
          <div className="bg-gray-700/50 rounded p-3">
            <p className="text-sm font-medium">Blue Heron Bridge</p>
            <p className="text-xs text-gray-400">Air quality monitor</p>
          </div>
          <div className="bg-gray-700/50 rounded p-3">
            <p className="text-sm font-medium">Port of Palm Beach</p>
            <p className="text-xs text-gray-400">Industrial monitoring</p>
          </div>
        </div>
      </div>
    </div>
  );
}
