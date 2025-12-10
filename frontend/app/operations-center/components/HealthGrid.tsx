"use client";

import { useState, useEffect } from "react";

type HealthStatus = "healthy" | "degraded" | "unhealthy" | "offline";

interface ServiceHealth {
  id: string;
  name: string;
  type: string;
  status: HealthStatus;
  latencyMs: number;
  lastCheck: string;
  uptimePercent: number;
  consecutiveFailures: number;
  errorMessage?: string;
}

const mockServices: ServiceHealth[] = [
  {
    id: "neo4j-primary",
    name: "Neo4j Primary",
    type: "database",
    status: "healthy",
    latencyMs: 12,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.99,
    consecutiveFailures: 0,
  },
  {
    id: "elasticsearch-cluster",
    name: "Elasticsearch Cluster",
    type: "search",
    status: "healthy",
    latencyMs: 28,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.95,
    consecutiveFailures: 0,
  },
  {
    id: "redis-cache",
    name: "Redis Cache",
    type: "cache",
    status: "healthy",
    latencyMs: 3,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.99,
    consecutiveFailures: 0,
  },
  {
    id: "postgres-db",
    name: "PostgreSQL",
    type: "database",
    status: "healthy",
    latencyMs: 8,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.98,
    consecutiveFailures: 0,
  },
  {
    id: "websocket-broker",
    name: "WebSocket Broker",
    type: "messaging",
    status: "healthy",
    latencyMs: 5,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.97,
    consecutiveFailures: 0,
  },
  {
    id: "ndex-federal",
    name: "N-DEx Federal",
    type: "federal",
    status: "healthy",
    latencyMs: 145,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.5,
    consecutiveFailures: 0,
  },
  {
    id: "ncic-federal",
    name: "NCIC Federal",
    type: "federal",
    status: "healthy",
    latencyMs: 132,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.6,
    consecutiveFailures: 0,
  },
  {
    id: "etrace-federal",
    name: "eTrace Federal",
    type: "federal",
    status: "degraded",
    latencyMs: 890,
    lastCheck: new Date().toISOString(),
    uptimePercent: 98.2,
    consecutiveFailures: 2,
    errorMessage: "High latency detected",
  },
  {
    id: "dhs-sar",
    name: "DHS-SAR",
    type: "federal",
    status: "healthy",
    latencyMs: 156,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.4,
    consecutiveFailures: 0,
  },
  {
    id: "ai-engine",
    name: "AI Intelligence Engine",
    type: "engine",
    status: "healthy",
    latencyMs: 45,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.9,
    consecutiveFailures: 0,
  },
  {
    id: "tactical-engine",
    name: "Tactical Analytics",
    type: "engine",
    status: "healthy",
    latencyMs: 38,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.92,
    consecutiveFailures: 0,
  },
  {
    id: "intel-orchestrator",
    name: "Intel Orchestrator",
    type: "engine",
    status: "healthy",
    latencyMs: 22,
    lastCheck: new Date().toISOString(),
    uptimePercent: 99.95,
    consecutiveFailures: 0,
  },
];

const statusColors: Record<HealthStatus, string> = {
  healthy: "bg-green-500",
  degraded: "bg-yellow-500",
  unhealthy: "bg-red-500",
  offline: "bg-gray-500",
};

const statusBgColors: Record<HealthStatus, string> = {
  healthy: "bg-green-500/10 border-green-500/30",
  degraded: "bg-yellow-500/10 border-yellow-500/30",
  unhealthy: "bg-red-500/10 border-red-500/30",
  offline: "bg-gray-500/10 border-gray-500/30",
};

const typeIcons: Record<string, string> = {
  database: "DB",
  search: "ES",
  cache: "RD",
  messaging: "WS",
  federal: "FD",
  engine: "EN",
  vendor: "VN",
};

export default function HealthGrid() {
  const [services, setServices] = useState<ServiceHealth[]>(mockServices);
  const [filter, setFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("status");

  useEffect(() => {
    const interval = setInterval(() => {
      setServices((prev) =>
        prev.map((service) => ({
          ...service,
          latencyMs: Math.max(
            1,
            service.latencyMs + (Math.random() - 0.5) * 10
          ),
          lastCheck: new Date().toISOString(),
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const filteredServices = services.filter((service) => {
    if (filter === "all") return true;
    if (filter === "issues") return service.status !== "healthy";
    return service.type === filter;
  });

  const sortedServices = [...filteredServices].sort((a, b) => {
    if (sortBy === "status") {
      const statusOrder = { unhealthy: 0, degraded: 1, offline: 2, healthy: 3 };
      return statusOrder[a.status] - statusOrder[b.status];
    }
    if (sortBy === "latency") return b.latencyMs - a.latencyMs;
    if (sortBy === "name") return a.name.localeCompare(b.name);
    return 0;
  });

  const statusCounts = services.reduce(
    (acc, service) => {
      acc[service.status] = (acc[service.status] || 0) + 1;
      return acc;
    },
    {} as Record<HealthStatus, number>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Service Health Grid</h2>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            {(["healthy", "degraded", "unhealthy", "offline"] as HealthStatus[]).map(
              (status) => (
                <div key={status} className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded-full ${statusColors[status]}`} />
                  <span className="text-sm text-gray-400 capitalize">
                    {statusCounts[status] || 0}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All Services</option>
          <option value="issues">Issues Only</option>
          <option value="database">Databases</option>
          <option value="federal">Federal</option>
          <option value="engine">Engines</option>
          <option value="vendor">Vendors</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="status">Sort by Status</option>
          <option value="latency">Sort by Latency</option>
          <option value="name">Sort by Name</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {sortedServices.map((service) => (
          <div
            key={service.id}
            className={`rounded-lg border p-4 ${statusBgColors[service.status]}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-gray-700 flex items-center justify-center text-xs font-bold">
                  {typeIcons[service.type] || "??"}
                </div>
                <div>
                  <div className="font-medium text-sm">{service.name}</div>
                  <div className="text-xs text-gray-400 capitalize">
                    {service.type}
                  </div>
                </div>
              </div>
              <div
                className={`w-3 h-3 rounded-full ${statusColors[service.status]}`}
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <div className="text-gray-400 text-xs">Latency</div>
                <div
                  className={
                    service.latencyMs > 500
                      ? "text-yellow-400"
                      : service.latencyMs > 1000
                      ? "text-red-400"
                      : "text-white"
                  }
                >
                  {service.latencyMs.toFixed(0)}ms
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-xs">Uptime</div>
                <div
                  className={
                    service.uptimePercent >= 99.9
                      ? "text-green-400"
                      : service.uptimePercent >= 99
                      ? "text-yellow-400"
                      : "text-red-400"
                  }
                >
                  {service.uptimePercent.toFixed(2)}%
                </div>
              </div>
            </div>

            {service.errorMessage && (
              <div className="mt-2 text-xs text-yellow-400 bg-yellow-500/10 rounded px-2 py-1">
                {service.errorMessage}
              </div>
            )}

            {service.consecutiveFailures > 0 && (
              <div className="mt-2 text-xs text-red-400">
                {service.consecutiveFailures} consecutive failure
                {service.consecutiveFailures > 1 ? "s" : ""}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
