"use client";

import { useState, useEffect } from "react";

interface UptimeData {
  serviceId: string;
  serviceName: string;
  serviceType: string;
  uptime1h: number;
  uptime24h: number;
  uptime7d: number;
  uptime30d: number;
  totalDowntimeMinutes: number;
  incidentCount: number;
  mttr: number;
  lastIncident?: string;
}

interface UptimeSnapshot {
  timestamp: string;
  overallUptime: number;
  healthyServices: number;
  totalServices: number;
}

const mockUptimeData: UptimeData[] = [
  {
    serviceId: "neo4j",
    serviceName: "Neo4j Primary",
    serviceType: "database",
    uptime1h: 100,
    uptime24h: 99.99,
    uptime7d: 99.95,
    uptime30d: 99.92,
    totalDowntimeMinutes: 35,
    incidentCount: 2,
    mttr: 17.5,
    lastIncident: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    serviceId: "elasticsearch",
    serviceName: "Elasticsearch Cluster",
    serviceType: "search",
    uptime1h: 100,
    uptime24h: 100,
    uptime7d: 99.98,
    uptime30d: 99.95,
    totalDowntimeMinutes: 22,
    incidentCount: 1,
    mttr: 22,
    lastIncident: new Date(Date.now() - 86400000 * 12).toISOString(),
  },
  {
    serviceId: "redis",
    serviceName: "Redis Cache",
    serviceType: "cache",
    uptime1h: 100,
    uptime24h: 100,
    uptime7d: 100,
    uptime30d: 99.99,
    totalDowntimeMinutes: 5,
    incidentCount: 1,
    mttr: 5,
    lastIncident: new Date(Date.now() - 86400000 * 20).toISOString(),
  },
  {
    serviceId: "ndex",
    serviceName: "N-DEx Federal",
    serviceType: "federal",
    uptime1h: 100,
    uptime24h: 99.8,
    uptime7d: 99.5,
    uptime30d: 99.2,
    totalDowntimeMinutes: 345,
    incidentCount: 8,
    mttr: 43,
    lastIncident: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    serviceId: "ncic",
    serviceName: "NCIC Federal",
    serviceType: "federal",
    uptime1h: 100,
    uptime24h: 99.9,
    uptime7d: 99.7,
    uptime30d: 99.5,
    totalDowntimeMinutes: 216,
    incidentCount: 5,
    mttr: 43,
    lastIncident: new Date(Date.now() - 86400000 * 3).toISOString(),
  },
  {
    serviceId: "etrace",
    serviceName: "eTrace Federal",
    serviceType: "federal",
    uptime1h: 98.5,
    uptime24h: 97.2,
    uptime7d: 98.1,
    uptime30d: 97.8,
    totalDowntimeMinutes: 950,
    incidentCount: 15,
    mttr: 63,
    lastIncident: new Date(Date.now() - 3600000).toISOString(),
  },
];

const generateSnapshots = (): UptimeSnapshot[] => {
  const snapshots: UptimeSnapshot[] = [];
  const now = Date.now();
  for (let i = 23; i >= 0; i--) {
    snapshots.push({
      timestamp: new Date(now - i * 3600000).toISOString(),
      overallUptime: 99 + Math.random() * 1,
      healthyServices: Math.floor(22 + Math.random() * 3),
      totalServices: 24,
    });
  }
  return snapshots;
};

export default function UptimeAnalytics() {
  const [uptimeData, setUptimeData] = useState<UptimeData[]>(mockUptimeData);
  const [snapshots, setSnapshots] = useState<UptimeSnapshot[]>(generateSnapshots());
  const [timeRange, setTimeRange] = useState<string>("24h");
  const [sortBy, setSortBy] = useState<string>("uptime");

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99.9) return "text-green-400";
    if (uptime >= 99) return "text-yellow-400";
    if (uptime >= 95) return "text-orange-400";
    return "text-red-400";
  };

  const getUptimeBgColor = (uptime: number) => {
    if (uptime >= 99.9) return "bg-green-500";
    if (uptime >= 99) return "bg-yellow-500";
    if (uptime >= 95) return "bg-orange-500";
    return "bg-red-500";
  };

  const getUptimeForRange = (data: UptimeData) => {
    switch (timeRange) {
      case "1h":
        return data.uptime1h;
      case "24h":
        return data.uptime24h;
      case "7d":
        return data.uptime7d;
      case "30d":
        return data.uptime30d;
      default:
        return data.uptime24h;
    }
  };

  const sortedData = [...uptimeData].sort((a, b) => {
    if (sortBy === "uptime") {
      return getUptimeForRange(a) - getUptimeForRange(b);
    }
    if (sortBy === "incidents") {
      return b.incidentCount - a.incidentCount;
    }
    if (sortBy === "mttr") {
      return b.mttr - a.mttr;
    }
    return a.serviceName.localeCompare(b.serviceName);
  });

  const overallUptime =
    uptimeData.reduce((sum, d) => sum + getUptimeForRange(d), 0) / uptimeData.length;

  const totalIncidents = uptimeData.reduce((sum, d) => sum + d.incidentCount, 0);
  const avgMttr =
    uptimeData.reduce((sum, d) => sum + d.mttr, 0) / uptimeData.length;

  const formatDaysAgo = (isoString?: string) => {
    if (!isoString) return "Never";
    const diff = Date.now() - new Date(isoString).getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    return `${days} days ago`;
  };

  const renderUptimeChart = () => {
    return (
      <div className="relative h-32 bg-gray-900 rounded-lg p-4">
        <div className="absolute left-0 top-4 bottom-4 w-12 flex flex-col justify-between text-xs text-gray-500">
          <span>100%</span>
          <span>99%</span>
          <span>98%</span>
        </div>
        <div className="ml-14 h-full flex items-end gap-1">
          {snapshots.map((snapshot, i) => {
            const height = ((snapshot.overallUptime - 98) / 2) * 100;
            return (
              <div
                key={i}
                className={`flex-1 rounded-t transition-colors cursor-pointer ${getUptimeBgColor(
                  snapshot.overallUptime
                )} hover:opacity-80`}
                style={{ height: `${Math.max(5, height)}%` }}
                title={`${snapshot.overallUptime.toFixed(2)}% at ${new Date(
                  snapshot.timestamp
                ).toLocaleTimeString()}`}
              />
            );
          })}
        </div>
      </div>
    );
  };

  const renderUptimeBar = (uptime: number) => {
    return (
      <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`absolute left-0 top-0 h-full rounded-full ${getUptimeBgColor(uptime)}`}
          style={{ width: `${uptime}%` }}
        />
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Uptime Analytics</h2>
        <div className="flex gap-2">
          {["1h", "24h", "7d", "30d"].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                timeRange === range
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-400 hover:bg-gray-600"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Overall Uptime</div>
          <div className={`text-2xl font-bold ${getUptimeColor(overallUptime)}`}>
            {overallUptime.toFixed(2)}%
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Total Incidents ({timeRange})</div>
          <div className="text-2xl font-bold text-orange-400">{totalIncidents}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Avg MTTR</div>
          <div className="text-2xl font-bold text-blue-400">
            {avgMttr.toFixed(0)} min
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Services Monitored</div>
          <div className="text-2xl font-bold text-gray-300">{uptimeData.length}</div>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Uptime Trend (24h)</h3>
        {renderUptimeChart()}
      </div>

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium">Service Uptime</h3>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="uptime">Sort by Uptime (Lowest First)</option>
          <option value="incidents">Sort by Incidents</option>
          <option value="mttr">Sort by MTTR</option>
          <option value="name">Sort by Name</option>
        </select>
      </div>

      <div className="space-y-3">
        {sortedData.map((service) => {
          const uptime = getUptimeForRange(service);
          return (
            <div
              key={service.serviceId}
              className="bg-gray-700/30 rounded-lg border border-gray-600 p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-medium">{service.serviceName}</div>
                  <div className="text-xs text-gray-400 capitalize">
                    {service.serviceType}
                  </div>
                </div>
                <div className={`text-2xl font-bold ${getUptimeColor(uptime)}`}>
                  {uptime.toFixed(2)}%
                </div>
              </div>

              {renderUptimeBar(uptime)}

              <div className="grid grid-cols-4 gap-4 mt-3 text-sm">
                <div>
                  <div className="text-gray-400 text-xs">Downtime</div>
                  <div>{service.totalDowntimeMinutes} min</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs">Incidents</div>
                  <div>{service.incidentCount}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs">MTTR</div>
                  <div>{service.mttr.toFixed(0)} min</div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs">Last Incident</div>
                  <div>{formatDaysAgo(service.lastIncident)}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 bg-gray-700/30 rounded-lg border border-gray-600 p-4">
        <h3 className="text-lg font-medium mb-3">SLA Compliance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">99.9% SLA</div>
            <div className="text-2xl font-bold text-green-400">
              {uptimeData.filter((d) => getUptimeForRange(d) >= 99.9).length}/
              {uptimeData.length}
            </div>
            <div className="text-xs text-gray-400">services compliant</div>
          </div>
          <div className="text-center p-4 bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">99% SLA</div>
            <div className="text-2xl font-bold text-yellow-400">
              {uptimeData.filter((d) => getUptimeForRange(d) >= 99).length}/
              {uptimeData.length}
            </div>
            <div className="text-xs text-gray-400">services compliant</div>
          </div>
          <div className="text-center p-4 bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">95% SLA</div>
            <div className="text-2xl font-bold text-orange-400">
              {uptimeData.filter((d) => getUptimeForRange(d) >= 95).length}/
              {uptimeData.length}
            </div>
            <div className="text-xs text-gray-400">services compliant</div>
          </div>
        </div>
      </div>
    </div>
  );
}
