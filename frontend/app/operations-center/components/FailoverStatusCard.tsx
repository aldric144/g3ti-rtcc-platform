"use client";

import { useState, useEffect } from "react";

type FailoverState = "normal" | "degraded" | "failover" | "emergency";

interface FailoverEvent {
  id: string;
  timestamp: string;
  serviceType: string;
  fromState: string;
  toState: string;
  triggerReason: string;
  autoTriggered: boolean;
  recoveryTime?: number;
}

interface ServiceFallback {
  serviceType: string;
  primaryTarget: string;
  fallbackTarget: string;
  isActive: boolean;
  activatedAt?: string;
  bufferedOperations: number;
}

const mockFallbacks: ServiceFallback[] = [
  {
    serviceType: "neo4j",
    primaryTarget: "neo4j-primary:7687",
    fallbackTarget: "neo4j-secondary:7687",
    isActive: false,
    bufferedOperations: 0,
  },
  {
    serviceType: "redis",
    primaryTarget: "redis-primary:6379",
    fallbackTarget: "in-memory-cache",
    isActive: false,
    bufferedOperations: 0,
  },
  {
    serviceType: "elasticsearch",
    primaryTarget: "es-cluster:9200",
    fallbackTarget: "es-backup:9200",
    isActive: false,
    bufferedOperations: 0,
  },
  {
    serviceType: "federal_ndex",
    primaryTarget: "ndex-api.fbi.gov",
    fallbackTarget: "queue-buffer",
    isActive: true,
    activatedAt: new Date(Date.now() - 300000).toISOString(),
    bufferedOperations: 12,
  },
];

const mockEvents: FailoverEvent[] = [
  {
    id: "evt-001",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    serviceType: "federal_ndex",
    fromState: "normal",
    toState: "failover",
    triggerReason: "Connection timeout after 3 retries",
    autoTriggered: true,
  },
  {
    id: "evt-002",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    serviceType: "redis",
    fromState: "failover",
    toState: "normal",
    triggerReason: "Primary service recovered",
    autoTriggered: true,
    recoveryTime: 45,
  },
  {
    id: "evt-003",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    serviceType: "redis",
    fromState: "normal",
    toState: "failover",
    triggerReason: "Memory pressure detected",
    autoTriggered: true,
  },
];

const stateColors: Record<FailoverState, string> = {
  normal: "bg-green-500",
  degraded: "bg-yellow-500",
  failover: "bg-orange-500",
  emergency: "bg-red-500",
};

const stateBgColors: Record<FailoverState, string> = {
  normal: "bg-green-500/10 border-green-500/30",
  degraded: "bg-yellow-500/10 border-yellow-500/30",
  failover: "bg-orange-500/10 border-orange-500/30",
  emergency: "bg-red-500/10 border-red-500/30",
};

export default function FailoverStatusCard() {
  const [state, setState] = useState<FailoverState>("degraded");
  const [fallbacks, setFallbacks] = useState<ServiceFallback[]>(mockFallbacks);
  const [events, setEvents] = useState<FailoverEvent[]>(mockEvents);
  const [activeFailovers, setActiveFailovers] = useState(1);

  useEffect(() => {
    const active = fallbacks.filter((f) => f.isActive).length;
    setActiveFailovers(active);
    if (active === 0) setState("normal");
    else if (active === 1) setState("degraded");
    else if (active < 3) setState("failover");
    else setState("emergency");
  }, [fallbacks]);

  const handleManualFailover = (serviceType: string) => {
    setFallbacks((prev) =>
      prev.map((f) =>
        f.serviceType === serviceType
          ? {
              ...f,
              isActive: true,
              activatedAt: new Date().toISOString(),
              bufferedOperations: 0,
            }
          : f
      )
    );
    setEvents((prev) => [
      {
        id: `evt-${Date.now()}`,
        timestamp: new Date().toISOString(),
        serviceType,
        fromState: "normal",
        toState: "failover",
        triggerReason: "Manual failover triggered",
        autoTriggered: false,
      },
      ...prev,
    ]);
  };

  const handleManualRecovery = (serviceType: string) => {
    setFallbacks((prev) =>
      prev.map((f) =>
        f.serviceType === serviceType
          ? {
              ...f,
              isActive: false,
              activatedAt: undefined,
              bufferedOperations: 0,
            }
          : f
      )
    );
    setEvents((prev) => [
      {
        id: `evt-${Date.now()}`,
        timestamp: new Date().toISOString(),
        serviceType,
        fromState: "failover",
        toState: "normal",
        triggerReason: "Manual recovery triggered",
        autoTriggered: false,
        recoveryTime: Math.floor(Math.random() * 60) + 10,
      },
      ...prev,
    ]);
  };

  const formatDuration = (isoString: string) => {
    const diff = Date.now() - new Date(isoString).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Failover Status</h2>
        <div className="flex items-center gap-3">
          <div
            className={`px-3 py-1 rounded-full text-sm font-medium ${stateBgColors[state]} border`}
          >
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${stateColors[state]}`} />
              <span className="capitalize">{state}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">System State</div>
          <div className={`text-xl font-bold capitalize ${
            state === "normal" ? "text-green-400" :
            state === "degraded" ? "text-yellow-400" :
            state === "failover" ? "text-orange-400" : "text-red-400"
          }`}>
            {state}
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Active Failovers</div>
          <div className={`text-xl font-bold ${
            activeFailovers === 0 ? "text-green-400" :
            activeFailovers === 1 ? "text-yellow-400" : "text-red-400"
          }`}>
            {activeFailovers}
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Buffered Ops</div>
          <div className="text-xl font-bold text-blue-400">
            {fallbacks.reduce((sum, f) => sum + f.bufferedOperations, 0)}
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Events (24h)</div>
          <div className="text-xl font-bold text-gray-300">{events.length}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Service Fallbacks</h3>
          <div className="space-y-3">
            {fallbacks.map((fallback) => (
              <div
                key={fallback.serviceType}
                className={`rounded-lg border p-4 ${
                  fallback.isActive
                    ? "bg-orange-500/10 border-orange-500/30"
                    : "bg-gray-700/30 border-gray-600"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium capitalize">
                    {fallback.serviceType.replace("_", " ")}
                  </div>
                  <div className="flex items-center gap-2">
                    {fallback.isActive ? (
                      <button
                        onClick={() => handleManualRecovery(fallback.serviceType)}
                        className="px-3 py-1 text-xs bg-green-600 hover:bg-green-700 rounded transition-colors"
                      >
                        Recover
                      </button>
                    ) : (
                      <button
                        onClick={() => handleManualFailover(fallback.serviceType)}
                        className="px-3 py-1 text-xs bg-orange-600 hover:bg-orange-700 rounded transition-colors"
                      >
                        Failover
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-sm text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Primary:</span>
                    <span className={fallback.isActive ? "line-through" : ""}>
                      {fallback.primaryTarget}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fallback:</span>
                    <span className={fallback.isActive ? "text-orange-400" : ""}>
                      {fallback.fallbackTarget}
                    </span>
                  </div>
                  {fallback.isActive && fallback.activatedAt && (
                    <div className="flex justify-between text-orange-400">
                      <span>Active for:</span>
                      <span>{formatDuration(fallback.activatedAt)}</span>
                    </div>
                  )}
                  {fallback.bufferedOperations > 0 && (
                    <div className="flex justify-between text-yellow-400">
                      <span>Buffered:</span>
                      <span>{fallback.bufferedOperations} operations</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-4">Recent Events</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {events.map((event) => (
              <div
                key={event.id}
                className="bg-gray-700/30 rounded-lg border border-gray-600 p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium capitalize">
                    {event.serviceType.replace("_", " ")}
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatDuration(event.timestamp)}
                  </div>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`px-2 py-0.5 text-xs rounded ${
                      event.fromState === "normal"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-orange-500/20 text-orange-400"
                    }`}
                  >
                    {event.fromState}
                  </span>
                  <span className="text-gray-500">→</span>
                  <span
                    className={`px-2 py-0.5 text-xs rounded ${
                      event.toState === "normal"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-orange-500/20 text-orange-400"
                    }`}
                  >
                    {event.toState}
                  </span>
                  {!event.autoTriggered && (
                    <span className="px-2 py-0.5 text-xs rounded bg-blue-500/20 text-blue-400">
                      Manual
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-400">{event.triggerReason}</div>
                {event.recoveryTime && (
                  <div className="text-xs text-green-400 mt-1">
                    Recovered in {event.recoveryTime}s
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
