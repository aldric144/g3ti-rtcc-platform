"use client";

import { useState, useEffect } from "react";

type DiagnosticCategory = "network" | "database" | "federal" | "vendor" | "internal";
type DiagnosticSeverity = "info" | "warning" | "error" | "critical";

interface DiagnosticEvent {
  id: string;
  timestamp: string;
  category: DiagnosticCategory;
  severity: DiagnosticSeverity;
  source: string;
  message: string;
  errorCode?: string;
  resolutionHint?: string;
  acknowledged: boolean;
}

interface SlowQuery {
  id: string;
  timestamp: string;
  database: string;
  queryType: string;
  durationMs: number;
  thresholdMs: number;
  queryPreview: string;
  recommendation: string;
}

interface PredictiveAlert {
  id: string;
  timestamp: string;
  category: DiagnosticCategory;
  predictionType: string;
  confidence: number;
  predictedFailureTime?: string;
  indicators: string[];
  recommendedActions: string[];
  acknowledged: boolean;
}

const mockEvents: DiagnosticEvent[] = [
  {
    id: "diag-001",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    category: "federal",
    severity: "warning",
    source: "eTrace Integration",
    message: "High latency detected on eTrace API calls",
    errorCode: "LATENCY_THRESHOLD",
    resolutionHint: "Check network connectivity to ATF servers",
    acknowledged: false,
  },
  {
    id: "diag-002",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    category: "database",
    severity: "info",
    source: "Neo4j Health Monitor",
    message: "Connection pool utilization at 75%",
    acknowledged: true,
  },
  {
    id: "diag-003",
    timestamp: new Date(Date.now() - 600000).toISOString(),
    category: "network",
    severity: "error",
    source: "WebSocket Broker",
    message: "Client disconnection rate exceeded threshold",
    errorCode: "WS_DISCONNECT_RATE",
    resolutionHint: "Review client-side connection handling",
    acknowledged: false,
  },
  {
    id: "diag-004",
    timestamp: new Date(Date.now() - 900000).toISOString(),
    category: "vendor",
    severity: "warning",
    source: "LPR Network",
    message: "API rate limit approaching (85% utilized)",
    acknowledged: true,
  },
  {
    id: "diag-005",
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    category: "internal",
    severity: "critical",
    source: "ETL Pipeline",
    message: "Data lake ingestion stalled for 15 minutes",
    errorCode: "ETL_STALL",
    resolutionHint: "Check source data availability and pipeline health",
    acknowledged: true,
  },
];

const mockSlowQueries: SlowQuery[] = [
  {
    id: "sq-001",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    database: "Neo4j",
    queryType: "MATCH",
    durationMs: 2500,
    thresholdMs: 1000,
    queryPreview: "MATCH (p:Person)-[:ASSOCIATED_WITH]->(v:Vehicle)...",
    recommendation: "Add index on Person.ssn property",
  },
  {
    id: "sq-002",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    database: "Elasticsearch",
    queryType: "SEARCH",
    durationMs: 1800,
    thresholdMs: 500,
    queryPreview: '{"query": {"bool": {"must": [{"match": {"description":...',
    recommendation: "Consider using filter context for non-scoring queries",
  },
];

const mockPredictiveAlerts: PredictiveAlert[] = [
  {
    id: "pred-001",
    timestamp: new Date(Date.now() - 180000).toISOString(),
    category: "database",
    predictionType: "connection_exhaustion",
    confidence: 0.78,
    predictedFailureTime: new Date(Date.now() + 3600000).toISOString(),
    indicators: [
      "Connection pool growth rate: 15%/hour",
      "Current utilization: 75%",
      "Historical pattern match: 82%",
    ],
    recommendedActions: [
      "Increase connection pool size",
      "Review connection leak sources",
      "Enable connection timeout",
    ],
    acknowledged: false,
  },
];

const severityColors: Record<DiagnosticSeverity, string> = {
  info: "bg-blue-500",
  warning: "bg-yellow-500",
  error: "bg-orange-500",
  critical: "bg-red-500",
};

const severityBgColors: Record<DiagnosticSeverity, string> = {
  info: "bg-blue-500/10 border-blue-500/30",
  warning: "bg-yellow-500/10 border-yellow-500/30",
  error: "bg-orange-500/10 border-orange-500/30",
  critical: "bg-red-500/10 border-red-500/30",
};

const categoryIcons: Record<DiagnosticCategory, string> = {
  network: "NET",
  database: "DB",
  federal: "FED",
  vendor: "VND",
  internal: "INT",
};

export default function DiagnosticsTimeline() {
  const [events, setEvents] = useState<DiagnosticEvent[]>(mockEvents);
  const [slowQueries, setSlowQueries] = useState<SlowQuery[]>(mockSlowQueries);
  const [predictiveAlerts, setPredictiveAlerts] = useState<PredictiveAlert[]>(mockPredictiveAlerts);
  const [activeTab, setActiveTab] = useState<string>("events");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  const filteredEvents = events.filter((event) => {
    if (severityFilter !== "all" && event.severity !== severityFilter) return false;
    if (categoryFilter !== "all" && event.category !== categoryFilter) return false;
    return true;
  });

  const handleAcknowledge = (eventId: string) => {
    setEvents((prev) =>
      prev.map((e) => (e.id === eventId ? { ...e, acknowledged: true } : e))
    );
  };

  const handleAcknowledgeAlert = (alertId: string) => {
    setPredictiveAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a))
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

  const severityCounts = events.reduce(
    (acc, event) => {
      acc[event.severity] = (acc[event.severity] || 0) + 1;
      return acc;
    },
    {} as Record<DiagnosticSeverity, number>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Diagnostics Timeline</h2>
        <div className="flex items-center gap-4">
          {(["info", "warning", "error", "critical"] as DiagnosticSeverity[]).map(
            (severity) => (
              <div key={severity} className="flex items-center gap-1">
                <div className={`w-3 h-3 rounded-full ${severityColors[severity]}`} />
                <span className="text-sm text-gray-400 capitalize">
                  {severityCounts[severity] || 0}
                </span>
              </div>
            )
          )}
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        {["events", "slow-queries", "predictions"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-400 hover:bg-gray-600"
            }`}
          >
            {tab === "events"
              ? "Events"
              : tab === "slow-queries"
              ? "Slow Queries"
              : "Predictions"}
            {tab === "predictions" && predictiveAlerts.filter((a) => !a.acknowledged).length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-red-500 rounded-full">
                {predictiveAlerts.filter((a) => !a.acknowledged).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {activeTab === "events" && (
        <>
          <div className="flex gap-4 mb-4">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
            >
              <option value="all">All Categories</option>
              <option value="network">Network</option>
              <option value="database">Database</option>
              <option value="federal">Federal</option>
              <option value="vendor">Vendor</option>
              <option value="internal">Internal</option>
            </select>
          </div>

          <div className="space-y-3">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                className={`rounded-lg border p-4 ${severityBgColors[event.severity]} ${
                  event.acknowledged ? "opacity-60" : ""
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded bg-gray-700 flex items-center justify-center text-xs font-bold">
                      {categoryIcons[event.category]}
                    </div>
                    <div>
                      <div className="font-medium">{event.source}</div>
                      <div className="text-xs text-gray-400">
                        {formatTime(event.timestamp)}
                        {event.errorCode && (
                          <span className="ml-2 px-1.5 py-0.5 bg-gray-700 rounded">
                            {event.errorCode}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 text-xs rounded capitalize ${severityBgColors[event.severity]} border`}
                    >
                      {event.severity}
                    </span>
                    {!event.acknowledged && (
                      <button
                        onClick={() => handleAcknowledge(event.id)}
                        className="px-2 py-1 text-xs bg-gray-600 hover:bg-gray-500 rounded transition-colors"
                      >
                        Ack
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-sm mb-2">{event.message}</div>
                {event.resolutionHint && (
                  <div className="text-xs text-gray-400 bg-gray-800/50 rounded px-2 py-1">
                    Hint: {event.resolutionHint}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === "slow-queries" && (
        <div className="space-y-3">
          {slowQueries.map((query) => (
            <div
              key={query.id}
              className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-medium">{query.database}</div>
                  <div className="text-xs text-gray-400">
                    {formatTime(query.timestamp)} • {query.queryType}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-yellow-400">
                    {query.durationMs}ms
                  </div>
                  <div className="text-xs text-gray-400">
                    Threshold: {query.thresholdMs}ms
                  </div>
                </div>
              </div>
              <div className="text-sm font-mono bg-gray-800 rounded px-2 py-1 mb-2 overflow-x-auto">
                {query.queryPreview}
              </div>
              <div className="text-xs text-blue-400">
                Recommendation: {query.recommendation}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === "predictions" && (
        <div className="space-y-4">
          {predictiveAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-lg border border-purple-500/30 bg-purple-500/10 p-4 ${
                alert.acknowledged ? "opacity-60" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-medium capitalize">
                    {alert.predictionType.replace("_", " ")}
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatTime(alert.timestamp)} • {alert.category}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <div className="text-lg font-bold text-purple-400">
                      {(alert.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-400">confidence</div>
                  </div>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledgeAlert(alert.id)}
                      className="px-2 py-1 text-xs bg-gray-600 hover:bg-gray-500 rounded transition-colors"
                    >
                      Ack
                    </button>
                  )}
                </div>
              </div>

              {alert.predictedFailureTime && (
                <div className="text-sm text-red-400 mb-3">
                  Predicted failure:{" "}
                  {new Date(alert.predictedFailureTime).toLocaleString()}
                </div>
              )}

              <div className="mb-3">
                <div className="text-xs text-gray-400 mb-1">Indicators:</div>
                <ul className="text-sm space-y-1">
                  {alert.indicators.map((indicator, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                      {indicator}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <div className="text-xs text-gray-400 mb-1">Recommended Actions:</div>
                <ul className="text-sm space-y-1">
                  {alert.recommendedActions.map((action, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
