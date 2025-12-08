"use client";

/**
 * Tactical Alerts Feed Component
 *
 * Real-time feed of tactical alerts including:
 * - Zone risk updates
 * - New hotspots
 * - Patrol route updates
 * - Tactical alerts
 * - Anomaly notifications
 * - Predicted clusters
 */

import { useMemo } from "react";

interface TacticalAlertsFeedProps {
  alerts: TacticalAlert[];
  maxItems?: number;
}

interface TacticalAlert {
  id: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

export function TacticalAlertsFeed({
  alerts,
  maxItems = 20,
}: TacticalAlertsFeedProps) {
  const displayAlerts = useMemo(
    () => alerts.slice(0, maxItems),
    [alerts, maxItems]
  );

  if (displayAlerts.length === 0) {
    return (
      <div className="text-gray-400 text-sm text-center py-4">
        No recent alerts
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {displayAlerts.map((alert) => (
        <AlertCard key={alert.id} alert={alert} />
      ))}
    </div>
  );
}

function AlertCard({ alert }: { alert: TacticalAlert }) {
  const severityColors: Record<string, string> = {
    critical: "border-red-500 bg-red-900/20",
    high: "border-orange-500 bg-orange-900/20",
    medium: "border-yellow-500 bg-yellow-900/20",
    low: "border-blue-500 bg-blue-900/20",
  };

  const typeIcons: Record<string, string> = {
    zone_risk_update: "Zone",
    new_hotspot: "Hotspot",
    patrol_route_update: "Patrol",
    tactical_alert: "Alert",
    anomaly_relevant_to_zone: "Anomaly",
    predicted_cluster: "Prediction",
  };

  const timeAgo = getTimeAgo(alert.timestamp);

  return (
    <div
      className={`p-3 rounded border-l-4 ${severityColors[alert.severity] || severityColors.low}`}
    >
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 bg-gray-700 rounded">
            {typeIcons[alert.type] || alert.type}
          </span>
          <span
            className={`text-xs uppercase ${
              alert.severity === "critical"
                ? "text-red-400"
                : alert.severity === "high"
                  ? "text-orange-400"
                  : "text-gray-400"
            }`}
          >
            {alert.severity}
          </span>
        </div>
        <span className="text-xs text-gray-500">{timeAgo}</span>
      </div>
      <p className="text-sm mt-1">{alert.message}</p>
    </div>
  );
}

function getTimeAgo(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);

  if (diffSec < 60) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  return then.toLocaleDateString();
}
