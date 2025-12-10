"use client";

import { useState, useEffect } from "react";

interface LatencyDataPoint {
  timestamp: string;
  value: number;
}

interface ServiceLatency {
  id: string;
  name: string;
  type: string;
  currentLatency: number;
  avgLatency: number;
  p95Latency: number;
  p99Latency: number;
  history: LatencyDataPoint[];
}

const generateHistory = (baseLatency: number): LatencyDataPoint[] => {
  const history: LatencyDataPoint[] = [];
  const now = Date.now();
  for (let i = 59; i >= 0; i--) {
    history.push({
      timestamp: new Date(now - i * 60000).toISOString(),
      value: baseLatency + (Math.random() - 0.5) * baseLatency * 0.4,
    });
  }
  return history;
};

const mockLatencyData: ServiceLatency[] = [
  {
    id: "neo4j",
    name: "Neo4j",
    type: "database",
    currentLatency: 12,
    avgLatency: 15,
    p95Latency: 28,
    p99Latency: 45,
    history: generateHistory(15),
  },
  {
    id: "elasticsearch",
    name: "Elasticsearch",
    type: "search",
    currentLatency: 28,
    avgLatency: 32,
    p95Latency: 65,
    p99Latency: 120,
    history: generateHistory(32),
  },
  {
    id: "redis",
    name: "Redis",
    type: "cache",
    currentLatency: 3,
    avgLatency: 4,
    p95Latency: 8,
    p99Latency: 15,
    history: generateHistory(4),
  },
  {
    id: "postgres",
    name: "PostgreSQL",
    type: "database",
    currentLatency: 8,
    avgLatency: 10,
    p95Latency: 22,
    p99Latency: 38,
    history: generateHistory(10),
  },
  {
    id: "ndex",
    name: "N-DEx",
    type: "federal",
    currentLatency: 145,
    avgLatency: 160,
    p95Latency: 320,
    p99Latency: 580,
    history: generateHistory(160),
  },
  {
    id: "ncic",
    name: "NCIC",
    type: "federal",
    currentLatency: 132,
    avgLatency: 145,
    p95Latency: 290,
    p99Latency: 520,
    history: generateHistory(145),
  },
];

export default function ServiceLatencyPanel() {
  const [services, setServices] = useState<ServiceLatency[]>(mockLatencyData);
  const [selectedService, setSelectedService] = useState<string>("neo4j");
  const [timeRange, setTimeRange] = useState<string>("1h");

  useEffect(() => {
    const interval = setInterval(() => {
      setServices((prev) =>
        prev.map((service) => {
          const newLatency = Math.max(
            1,
            service.currentLatency + (Math.random() - 0.5) * 10
          );
          const newHistory = [
            ...service.history.slice(1),
            { timestamp: new Date().toISOString(), value: newLatency },
          ];
          return {
            ...service,
            currentLatency: newLatency,
            history: newHistory,
          };
        })
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const selectedServiceData = services.find((s) => s.id === selectedService);

  const getLatencyColor = (latency: number, type: string) => {
    const thresholds =
      type === "federal"
        ? { good: 200, warn: 500 }
        : type === "cache"
        ? { good: 10, warn: 25 }
        : { good: 50, warn: 100 };

    if (latency <= thresholds.good) return "text-green-400";
    if (latency <= thresholds.warn) return "text-yellow-400";
    return "text-red-400";
  };

  const renderMiniChart = (history: LatencyDataPoint[]) => {
    const max = Math.max(...history.map((h) => h.value));
    const min = Math.min(...history.map((h) => h.value));
    const range = max - min || 1;

    return (
      <div className="flex items-end h-8 gap-px">
        {history.slice(-30).map((point, i) => {
          const height = ((point.value - min) / range) * 100;
          return (
            <div
              key={i}
              className="flex-1 bg-blue-500/50 rounded-t"
              style={{ height: `${Math.max(10, height)}%` }}
            />
          );
        })}
      </div>
    );
  };

  const renderDetailChart = (history: LatencyDataPoint[]) => {
    const max = Math.max(...history.map((h) => h.value));
    const min = Math.min(...history.map((h) => h.value));
    const range = max - min || 1;

    return (
      <div className="relative h-48 bg-gray-900 rounded-lg p-4">
        <div className="absolute left-0 top-4 bottom-4 w-12 flex flex-col justify-between text-xs text-gray-500">
          <span>{max.toFixed(0)}ms</span>
          <span>{((max + min) / 2).toFixed(0)}ms</span>
          <span>{min.toFixed(0)}ms</span>
        </div>
        <div className="ml-14 h-full flex items-end gap-px">
          {history.map((point, i) => {
            const height = ((point.value - min) / range) * 100;
            return (
              <div
                key={i}
                className="flex-1 bg-blue-500 hover:bg-blue-400 rounded-t transition-colors cursor-pointer"
                style={{ height: `${Math.max(5, height)}%` }}
                title={`${point.value.toFixed(1)}ms at ${new Date(
                  point.timestamp
                ).toLocaleTimeString()}`}
              />
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Service Latency Monitor</h2>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="1h">Last 1 Hour</option>
          <option value="6h">Last 6 Hours</option>
          <option value="24h">Last 24 Hours</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-3">
          {services.map((service) => (
            <div
              key={service.id}
              onClick={() => setSelectedService(service.id)}
              className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                selectedService === service.id
                  ? "bg-blue-500/20 border-blue-500"
                  : "bg-gray-700/50 border-gray-600 hover:border-gray-500"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="font-medium">{service.name}</div>
                  <div className="text-xs text-gray-400 capitalize">
                    {service.type}
                  </div>
                </div>
                <div
                  className={`text-xl font-bold ${getLatencyColor(
                    service.currentLatency,
                    service.type
                  )}`}
                >
                  {service.currentLatency.toFixed(0)}ms
                </div>
              </div>
              {renderMiniChart(service.history)}
            </div>
          ))}
        </div>

        <div className="lg:col-span-2">
          {selectedServiceData && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">
                    {selectedServiceData.name}
                  </h3>
                  <p className="text-sm text-gray-400 capitalize">
                    {selectedServiceData.type} Service
                  </p>
                </div>
                <div
                  className={`text-3xl font-bold ${getLatencyColor(
                    selectedServiceData.currentLatency,
                    selectedServiceData.type
                  )}`}
                >
                  {selectedServiceData.currentLatency.toFixed(0)}ms
                </div>
              </div>

              {renderDetailChart(selectedServiceData.history)}

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Average</div>
                  <div className="text-xl font-bold">
                    {selectedServiceData.avgLatency.toFixed(0)}ms
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400">P95</div>
                  <div className="text-xl font-bold">
                    {selectedServiceData.p95Latency.toFixed(0)}ms
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400">P99</div>
                  <div className="text-xl font-bold">
                    {selectedServiceData.p99Latency.toFixed(0)}ms
                  </div>
                </div>
              </div>

              <div className="bg-gray-700/30 rounded-lg p-4">
                <h4 className="text-sm font-medium mb-2">Latency Thresholds</h4>
                <div className="flex gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-gray-400">Optimal</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <span className="text-gray-400">Degraded</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-gray-400">Critical</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
