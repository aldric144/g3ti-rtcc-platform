"use client";

import { useState, useEffect } from "react";

type AlertTier = "tier1" | "tier2" | "tier3" | "tier4";
type AlertStatus = "active" | "acknowledged" | "resolved";

interface OpsAlert {
  id: string;
  timestamp: string;
  tier: AlertTier;
  status: AlertStatus;
  title: string;
  description: string;
  source: string;
  affectedServices: string[];
  escalationLevel: number;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  actions: string[];
}

const mockAlerts: OpsAlert[] = [
  {
    id: "alert-001",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    tier: "tier2",
    status: "active",
    title: "eTrace Federal Endpoint High Latency",
    description:
      "eTrace API response times exceeding 800ms threshold for 5+ minutes",
    source: "Health Monitor",
    affectedServices: ["eTrace", "Federal Integration Layer"],
    escalationLevel: 1,
    actions: ["Check ATF network status", "Enable queue buffering", "Notify federal liaison"],
  },
  {
    id: "alert-002",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    tier: "tier3",
    status: "acknowledged",
    title: "Neo4j Connection Pool Utilization Warning",
    description: "Connection pool at 75% capacity, trending upward",
    source: "Diagnostics Engine",
    affectedServices: ["Neo4j", "Knowledge Graph"],
    escalationLevel: 0,
    acknowledgedBy: "ops-admin",
    acknowledgedAt: new Date(Date.now() - 240000).toISOString(),
    actions: ["Monitor pool growth", "Consider pool expansion"],
  },
  {
    id: "alert-003",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    tier: "tier4",
    status: "resolved",
    title: "WebSocket Client Reconnection Spike",
    description: "Elevated client reconnection rate detected (15% above baseline)",
    source: "WebSocket Broker",
    affectedServices: ["WebSocket Broker", "Real-time Feeds"],
    escalationLevel: 0,
    acknowledgedBy: "system",
    acknowledgedAt: new Date(Date.now() - 850000).toISOString(),
    resolvedAt: new Date(Date.now() - 600000).toISOString(),
    actions: ["Auto-resolved: Rate normalized"],
  },
  {
    id: "alert-004",
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    tier: "tier1",
    status: "resolved",
    title: "Redis Primary Failover Activated",
    description: "Primary Redis instance unresponsive, failover to secondary completed",
    source: "Failover Manager",
    affectedServices: ["Redis", "Cache Layer", "Session Store"],
    escalationLevel: 2,
    acknowledgedBy: "ops-admin",
    acknowledgedAt: new Date(Date.now() - 1750000).toISOString(),
    resolvedAt: new Date(Date.now() - 1500000).toISOString(),
    actions: ["Failover completed", "Primary restored", "Cache rewarmed"],
  },
  {
    id: "alert-005",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    tier: "tier2",
    status: "resolved",
    title: "ETL Pipeline Stall Detected",
    description: "Data lake ingestion pipeline stalled for 10 minutes",
    source: "ETL Monitor",
    affectedServices: ["ETL Pipeline", "Data Lake"],
    escalationLevel: 1,
    acknowledgedBy: "data-ops",
    acknowledgedAt: new Date(Date.now() - 3540000).toISOString(),
    resolvedAt: new Date(Date.now() - 3300000).toISOString(),
    actions: ["Pipeline restarted", "Backlog processed"],
  },
];

const tierConfig: Record<AlertTier, { label: string; color: string; bgColor: string; priority: number }> = {
  tier1: {
    label: "Tier 1 - Critical",
    color: "text-red-400",
    bgColor: "bg-red-500/10 border-red-500/30",
    priority: 1,
  },
  tier2: {
    label: "Tier 2 - High",
    color: "text-orange-400",
    bgColor: "bg-orange-500/10 border-orange-500/30",
    priority: 2,
  },
  tier3: {
    label: "Tier 3 - Medium",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10 border-yellow-500/30",
    priority: 3,
  },
  tier4: {
    label: "Tier 4 - Low",
    color: "text-blue-400",
    bgColor: "bg-blue-500/10 border-blue-500/30",
    priority: 4,
  },
};

const statusConfig: Record<AlertStatus, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-red-500" },
  acknowledged: { label: "Acknowledged", color: "bg-yellow-500" },
  resolved: { label: "Resolved", color: "bg-green-500" },
};

export default function OpsAlertsFeed() {
  const [alerts, setAlerts] = useState<OpsAlert[]>(mockAlerts);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [tierFilter, setTierFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("time");

  const filteredAlerts = alerts.filter((alert) => {
    if (statusFilter !== "all" && alert.status !== statusFilter) return false;
    if (tierFilter !== "all" && alert.tier !== tierFilter) return false;
    return true;
  });

  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    if (sortBy === "time") {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    }
    if (sortBy === "tier") {
      return tierConfig[a.tier].priority - tierConfig[b.tier].priority;
    }
    if (sortBy === "status") {
      const statusOrder = { active: 0, acknowledged: 1, resolved: 2 };
      return statusOrder[a.status] - statusOrder[b.status];
    }
    return 0;
  });

  const handleAcknowledge = (alertId: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === alertId
          ? {
              ...a,
              status: "acknowledged" as AlertStatus,
              acknowledgedBy: "current-user",
              acknowledgedAt: new Date().toISOString(),
            }
          : a
      )
    );
  };

  const handleResolve = (alertId: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === alertId
          ? {
              ...a,
              status: "resolved" as AlertStatus,
              resolvedAt: new Date().toISOString(),
            }
          : a
      )
    );
  };

  const formatTime = (isoString: string) => {
    const diff = Date.now() - new Date(isoString).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const alertCounts = {
    active: alerts.filter((a) => a.status === "active").length,
    acknowledged: alerts.filter((a) => a.status === "acknowledged").length,
    resolved: alerts.filter((a) => a.status === "resolved").length,
  };

  const tierCounts = {
    tier1: alerts.filter((a) => a.tier === "tier1" && a.status !== "resolved").length,
    tier2: alerts.filter((a) => a.tier === "tier2" && a.status !== "resolved").length,
    tier3: alerts.filter((a) => a.tier === "tier3" && a.status !== "resolved").length,
    tier4: alerts.filter((a) => a.tier === "tier4" && a.status !== "resolved").length,
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Operations Alerts Feed</h2>
        <div className="flex items-center gap-4">
          {alertCounts.active > 0 && (
            <div className="flex items-center gap-2 px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-full">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="text-sm text-red-400">
                {alertCounts.active} Active
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Active Alerts</div>
          <div className="text-2xl font-bold text-red-400">{alertCounts.active}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Acknowledged</div>
          <div className="text-2xl font-bold text-yellow-400">
            {alertCounts.acknowledged}
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Resolved (24h)</div>
          <div className="text-2xl font-bold text-green-400">
            {alertCounts.resolved}
          </div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-sm text-gray-400">Critical (Tier 1)</div>
          <div className="text-2xl font-bold text-red-400">{tierCounts.tier1}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
        <select
          value={tierFilter}
          onChange={(e) => setTierFilter(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All Tiers</option>
          <option value="tier1">Tier 1 - Critical</option>
          <option value="tier2">Tier 2 - High</option>
          <option value="tier3">Tier 3 - Medium</option>
          <option value="tier4">Tier 4 - Low</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
        >
          <option value="time">Sort by Time</option>
          <option value="tier">Sort by Tier</option>
          <option value="status">Sort by Status</option>
        </select>
      </div>

      <div className="space-y-4">
        {sortedAlerts.map((alert) => (
          <div
            key={alert.id}
            className={`rounded-lg border p-4 ${tierConfig[alert.tier].bgColor} ${
              alert.status === "resolved" ? "opacity-60" : ""
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3">
                <div
                  className={`w-2 h-2 rounded-full mt-2 ${statusConfig[alert.status].color} ${
                    alert.status === "active" ? "animate-pulse" : ""
                  }`}
                />
                <div>
                  <div className="font-medium">{alert.title}</div>
                  <div className="text-sm text-gray-400 mt-1">
                    {alert.description}
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span
                  className={`px-2 py-1 text-xs rounded ${tierConfig[alert.tier].bgColor} border ${tierConfig[alert.tier].color}`}
                >
                  {tierConfig[alert.tier].label}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(alert.timestamp)}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-3">
              {alert.affectedServices.map((service) => (
                <span
                  key={service}
                  className="px-2 py-0.5 text-xs bg-gray-700 rounded"
                >
                  {service}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-400">
                Source: {alert.source}
                {alert.acknowledgedBy && (
                  <span className="ml-3">
                    Ack by: {alert.acknowledgedBy} ({formatTime(alert.acknowledgedAt!)})
                  </span>
                )}
                {alert.resolvedAt && (
                  <span className="ml-3">
                    Resolved: {formatTime(alert.resolvedAt)}
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                {alert.status === "active" && (
                  <>
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="px-3 py-1 text-xs bg-yellow-600 hover:bg-yellow-700 rounded transition-colors"
                    >
                      Acknowledge
                    </button>
                    <button
                      onClick={() => handleResolve(alert.id)}
                      className="px-3 py-1 text-xs bg-green-600 hover:bg-green-700 rounded transition-colors"
                    >
                      Resolve
                    </button>
                  </>
                )}
                {alert.status === "acknowledged" && (
                  <button
                    onClick={() => handleResolve(alert.id)}
                    className="px-3 py-1 text-xs bg-green-600 hover:bg-green-700 rounded transition-colors"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>

            {alert.actions.length > 0 && alert.status !== "resolved" && (
              <div className="mt-3 pt-3 border-t border-gray-600">
                <div className="text-xs text-gray-400 mb-2">Recommended Actions:</div>
                <ul className="text-sm space-y-1">
                  {alert.actions.map((action, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}

        {sortedAlerts.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            No alerts match the current filters
          </div>
        )}
      </div>

      <div className="mt-6 bg-gray-700/30 rounded-lg border border-gray-600 p-4">
        <h3 className="text-lg font-medium mb-3">Alert Tier Legend</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`p-3 rounded-lg ${tierConfig.tier1.bgColor} border`}>
            <div className={`font-medium ${tierConfig.tier1.color}`}>Tier 1 - Critical</div>
            <div className="text-xs text-gray-400 mt-1">
              Immediate officer safety threat or system-wide outage
            </div>
          </div>
          <div className={`p-3 rounded-lg ${tierConfig.tier2.bgColor} border`}>
            <div className={`font-medium ${tierConfig.tier2.color}`}>Tier 2 - High</div>
            <div className="text-xs text-gray-400 mt-1">
              Major service degradation or federal feed interruption
            </div>
          </div>
          <div className={`p-3 rounded-lg ${tierConfig.tier3.bgColor} border`}>
            <div className={`font-medium ${tierConfig.tier3.color}`}>Tier 3 - Medium</div>
            <div className="text-xs text-gray-400 mt-1">
              Performance warnings or capacity concerns
            </div>
          </div>
          <div className={`p-3 rounded-lg ${tierConfig.tier4.bgColor} border`}>
            <div className={`font-medium ${tierConfig.tier4.color}`}>Tier 4 - Low</div>
            <div className="text-xs text-gray-400 mt-1">
              Informational alerts or minor anomalies
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
