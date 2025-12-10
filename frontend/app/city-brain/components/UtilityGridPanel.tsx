"use client";

import { useState, useEffect } from "react";

interface PowerOutage {
  outage_id: string;
  area_name: string;
  customers_affected: number;
  cause: string;
  start_time: string;
  estimated_restoration: string | null;
  status: string;
}

interface WaterStatus {
  zone_id: string;
  zone_name: string;
  pressure_psi: number;
  status: string;
  last_update: string;
}

interface SewerStatus {
  station_id: string;
  station_name: string;
  capacity_percent: number;
  status: string;
  alerts: string[];
}

interface UtilityData {
  power: {
    grid_status: string;
    outages: PowerOutage[];
  };
  water: WaterStatus[];
  sewer: SewerStatus[];
  flooding: Array<{
    zone_id: string;
    zone_name: string;
    water_level_inches: number;
    risk_level: string;
  }>;
}

export default function UtilityGridPanel() {
  const [utilityData, setUtilityData] = useState<UtilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<"power" | "water" | "sewer" | "flooding">("power");

  useEffect(() => {
    fetchUtilityData();
    const interval = setInterval(fetchUtilityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchUtilityData = async () => {
    try {
      const response = await fetch("/api/citybrain/city/utility");
      if (!response.ok) throw new Error("Failed to fetch utility data");
      const data = await response.json();
      setUtilityData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "normal":
      case "operational":
      case "online":
        return "bg-green-500";
      case "degraded":
      case "warning":
        return "bg-yellow-500";
      case "critical":
      case "offline":
      case "outage":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusTextColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "normal":
      case "operational":
      case "online":
        return "text-green-400";
      case "degraded":
      case "warning":
        return "bg-yellow-400";
      case "critical":
      case "offline":
      case "outage":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "low":
        return "text-green-400";
      case "moderate":
        return "text-yellow-400";
      case "high":
        return "text-orange-400";
      case "severe":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getCapacityColor = (percent: number) => {
    if (percent < 60) return "bg-green-500";
    if (percent < 80) return "bg-yellow-500";
    if (percent < 90) return "bg-orange-500";
    return "bg-red-500";
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
        <h2 className="text-xl font-bold">Utility Grid Monitor</h2>
        <button
          onClick={fetchUtilityData}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button
          onClick={() => setSelectedTab("power")}
          className={`p-4 rounded-lg border ${
            selectedTab === "power"
              ? "bg-blue-600 border-blue-500"
              : "bg-gray-800 border-gray-700 hover:bg-gray-700"
          }`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-2xl">⚡</span>
            <div className="text-left">
              <p className="text-sm font-medium">Power Grid</p>
              <p className={`text-xs ${getStatusTextColor(utilityData?.power?.grid_status || "unknown")}`}>
                {utilityData?.power?.grid_status || "Unknown"}
              </p>
            </div>
          </div>
        </button>

        <button
          onClick={() => setSelectedTab("water")}
          className={`p-4 rounded-lg border ${
            selectedTab === "water"
              ? "bg-blue-600 border-blue-500"
              : "bg-gray-800 border-gray-700 hover:bg-gray-700"
          }`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-2xl">💧</span>
            <div className="text-left">
              <p className="text-sm font-medium">Water System</p>
              <p className="text-xs text-gray-400">
                {utilityData?.water?.length || 0} zones
              </p>
            </div>
          </div>
        </button>

        <button
          onClick={() => setSelectedTab("sewer")}
          className={`p-4 rounded-lg border ${
            selectedTab === "sewer"
              ? "bg-blue-600 border-blue-500"
              : "bg-gray-800 border-gray-700 hover:bg-gray-700"
          }`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🚰</span>
            <div className="text-left">
              <p className="text-sm font-medium">Sewer System</p>
              <p className="text-xs text-gray-400">
                {utilityData?.sewer?.length || 0} stations
              </p>
            </div>
          </div>
        </button>

        <button
          onClick={() => setSelectedTab("flooding")}
          className={`p-4 rounded-lg border ${
            selectedTab === "flooding"
              ? "bg-blue-600 border-blue-500"
              : "bg-gray-800 border-gray-700 hover:bg-gray-700"
          }`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🌊</span>
            <div className="text-left">
              <p className="text-sm font-medium">Flood Monitoring</p>
              <p className="text-xs text-gray-400">
                {utilityData?.flooding?.length || 0} zones
              </p>
            </div>
          </div>
        </button>
      </div>

      {selectedTab === "power" && (
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Grid Status</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(utilityData?.power?.grid_status || "unknown")}`} />
                <span className="text-sm capitalize">{utilityData?.power?.grid_status || "Unknown"}</span>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-700/50 rounded p-3 text-center">
                <p className="text-2xl font-bold text-white">
                  {utilityData?.power?.outages?.length || 0}
                </p>
                <p className="text-xs text-gray-400">Active Outages</p>
              </div>
              <div className="bg-gray-700/50 rounded p-3 text-center">
                <p className="text-2xl font-bold text-white">
                  {utilityData?.power?.outages?.reduce((sum, o) => sum + o.customers_affected, 0) || 0}
                </p>
                <p className="text-xs text-gray-400">Customers Affected</p>
              </div>
              <div className="bg-gray-700/50 rounded p-3 text-center">
                <p className="text-2xl font-bold text-green-400">FPL</p>
                <p className="text-xs text-gray-400">Provider</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-semibold">Active Outages</h3>
            </div>
            <div className="divide-y divide-gray-700">
              {utilityData?.power?.outages && utilityData.power.outages.length > 0 ? (
                utilityData.power.outages.map((outage) => (
                  <div key={outage.outage_id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{outage.area_name}</p>
                        <p className="text-sm text-gray-400">{outage.cause}</p>
                        <p className="text-sm text-gray-500">
                          {outage.customers_affected.toLocaleString()} customers affected
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`px-2 py-1 rounded text-xs ${getStatusColor(outage.status)}`}>
                          {outage.status}
                        </div>
                        {outage.estimated_restoration && (
                          <p className="text-xs text-gray-400 mt-1">
                            Est. restore: {new Date(outage.estimated_restoration).toLocaleTimeString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-gray-500">
                  No active outages
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {selectedTab === "water" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Water System Status</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {utilityData?.water && utilityData.water.length > 0 ? (
              utilityData.water.map((zone) => (
                <div key={zone.zone_id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(zone.status)}`} />
                      <div>
                        <p className="font-medium">{zone.zone_name}</p>
                        <p className="text-sm text-gray-400">
                          Pressure: {zone.pressure_psi} PSI
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm capitalize ${getStatusTextColor(zone.status)}`}>
                        {zone.status}
                      </span>
                      <p className="text-xs text-gray-500">
                        {new Date(zone.last_update).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No water zone data available
              </div>
            )}
          </div>
        </div>
      )}

      {selectedTab === "sewer" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Sewer System Status</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {utilityData?.sewer && utilityData.sewer.length > 0 ? (
              utilityData.sewer.map((station) => (
                <div key={station.station_id} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(station.status)}`} />
                      <p className="font-medium">{station.station_name}</p>
                    </div>
                    <span className={`text-sm capitalize ${getStatusTextColor(station.status)}`}>
                      {station.status}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${getCapacityColor(station.capacity_percent)}`}
                          style={{ width: `${station.capacity_percent}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">
                      {station.capacity_percent}% capacity
                    </span>
                  </div>
                  {station.alerts && station.alerts.length > 0 && (
                    <div className="mt-2">
                      {station.alerts.map((alert, idx) => (
                        <p key={idx} className="text-xs text-yellow-400">
                          ⚠️ {alert}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No sewer station data available
              </div>
            )}
          </div>
        </div>
      )}

      {selectedTab === "flooding" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Flood Monitoring</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {utilityData?.flooding && utilityData.flooding.length > 0 ? (
              utilityData.flooding.map((zone) => (
                <div key={zone.zone_id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{zone.zone_name}</p>
                      <p className="text-sm text-gray-400">
                        Water Level: {zone.water_level_inches} inches
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm font-medium capitalize ${getRiskColor(zone.risk_level)}`}>
                        {zone.risk_level} Risk
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No flooding data available
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
