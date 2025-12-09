"use client";

/**
 * Tactical Dashboard Page
 *
 * Main tactical analytics dashboard providing:
 * - Predictive Heatmap Viewer
 * - Hot Zone List with confidence scores
 * - Patrol Optimizer Panel
 * - Zone Intelligence Cards
 * - Shift Briefing Page
 * - Tactical Alerts Feed (WebSocket)
 * - Overlays for gunfire clusters, LPR hotspots, repeat offender zones
 */

import { useState, useEffect, useCallback } from "react";
import { HeatmapViewer } from "./components/HeatmapViewer";
import { HotZoneList } from "./components/HotZoneList";
import { PatrolOptimizer } from "./components/PatrolOptimizer";
import { ZoneIntelligence } from "./components/ZoneIntelligence";
import { ShiftBriefing } from "./components/ShiftBriefing";
import { TacticalAlertsFeed } from "./components/TacticalAlertsFeed";
import { ForecastPanel } from "./components/ForecastPanel";

// Tab definitions
type TabId =
  | "overview"
  | "heatmap"
  | "zones"
  | "patrol"
  | "briefing"
  | "forecast";

interface Tab {
  id: TabId;
  label: string;
  icon: string;
}

const TABS: Tab[] = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "heatmap", label: "Heatmaps", icon: "map" },
  { id: "zones", label: "Zones", icon: "layers" },
  { id: "patrol", label: "Patrol", icon: "route" },
  { id: "briefing", label: "Briefing", icon: "clipboard" },
  { id: "forecast", label: "Forecast", icon: "chart" },
];

export default function TacticalDashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [selectedShift, setSelectedShift] = useState<string>("A");
  const [alerts, setAlerts] = useState<TacticalAlert[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Handle tactical events from WebSocket
  const handleTacticalEvent = useCallback((event: TacticalEvent) => {
    switch (event.type) {
      case "zone_risk_update":
      case "new_hotspot":
      case "tactical_alert":
      case "anomaly_relevant_to_zone":
      case "predicted_cluster":
        // Add to alerts feed
        setAlerts((prev) => [
          {
            id: `alert-${Date.now()}`,
            type: event.type,
            severity: event.severity || "medium",
            message: event.message || "New tactical event",
            timestamp: new Date().toISOString(),
            data: event.data,
          },
          ...prev.slice(0, 49), // Keep last 50 alerts
        ]);
        break;
      case "patrol_route_update":
        // Handle patrol route updates
        console.log("Patrol route update:", event.data);
        break;
      default:
        console.log("Unknown tactical event:", event);
    }
  }, []);

  // WebSocket connection for real-time alerts
  useEffect(() => {
    const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/realtime/tactical/alerts`;

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log("Tactical WebSocket connected");
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleTacticalEvent(data);
          } catch (e) {
            console.error("Failed to parse tactical event:", e);
          }
        };

        ws.onclose = () => {
          console.log("Tactical WebSocket disconnected");
          setIsConnected(false);
          // Reconnect after 5 seconds
          reconnectTimeout = setTimeout(connect, 5000);
        };

        ws.onerror = (error) => {
          console.error("Tactical WebSocket error:", error);
        };
      } catch (e) {
        console.error("Failed to connect to tactical WebSocket:", e);
        reconnectTimeout = setTimeout(connect, 5000);
      }
    };

    // Connect on mount
    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [handleTacticalEvent]);

  // Handle zone selection
  const handleZoneSelect = useCallback((zoneId: string) => {
    setSelectedZone(zoneId);
    setActiveTab("zones");
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Tactical Analytics</h1>
            <p className="text-gray-400 text-sm">
              Real-time tactical intelligence and predictive analytics
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* Connection status */}
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
              />
              <span className="text-sm text-gray-400">
                {isConnected ? "Connected" : "Disconnected"}
              </span>
            </div>
            {/* Shift selector */}
            <select
              value={selectedShift}
              onChange={(e) => setSelectedShift(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="A">Shift A (Day)</option>
              <option value="B">Shift B (Evening)</option>
              <option value="C">Shift C (Night)</option>
            </select>
          </div>
        </div>

        {/* Tab navigation */}
        <nav className="flex gap-1 mt-4">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-t text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-gray-900 text-white"
                  : "bg-gray-700 text-gray-400 hover:bg-gray-600"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main content */}
      <main className="p-6">
        {activeTab === "overview" && (
          <OverviewTab
            onZoneSelect={handleZoneSelect}
            alerts={alerts}
            selectedShift={selectedShift}
          />
        )}
        {activeTab === "heatmap" && (
          <HeatmapViewer onZoneSelect={handleZoneSelect} />
        )}
        {activeTab === "zones" && (
          <ZoneIntelligence
            selectedZone={selectedZone}
            onZoneSelect={setSelectedZone}
          />
        )}
        {activeTab === "patrol" && (
          <PatrolOptimizer selectedShift={selectedShift} />
        )}
        {activeTab === "briefing" && (
          <ShiftBriefing selectedShift={selectedShift} />
        )}
        {activeTab === "forecast" && <ForecastPanel />}
      </main>
    </div>
  );
}

// Overview tab component
interface OverviewTabProps {
  onZoneSelect: (zoneId: string) => void;
  alerts: TacticalAlert[];
  selectedShift: string;
}

function OverviewTab({ onZoneSelect, alerts, selectedShift }: OverviewTabProps) {
  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left column - Heatmap and Hot Zones */}
      <div className="col-span-8 space-y-6">
        {/* Mini heatmap */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Current Activity Heatmap</h2>
          <div className="h-96">
            <HeatmapViewer compact onZoneSelect={onZoneSelect} />
          </div>
        </div>

        {/* Hot zones */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Hot Zones</h2>
          <HotZoneList onZoneSelect={onZoneSelect} limit={5} />
        </div>
      </div>

      {/* Right column - Alerts and Quick Stats */}
      <div className="col-span-4 space-y-6">
        {/* Quick stats */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Shift {selectedShift} Stats</h2>
          <QuickStats shift={selectedShift} />
        </div>

        {/* Tactical alerts feed */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Tactical Alerts</h2>
          <TacticalAlertsFeed alerts={alerts} maxItems={10} />
        </div>
      </div>
    </div>
  );
}

// Quick stats component
interface QuickStatsProps {
  shift: string;
}

function QuickStats({ shift }: QuickStatsProps) {
  const [stats, setStats] = useState<ShiftStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`/api/tactical/shiftbrief?shift=${shift}`);
        if (response.ok) {
          const data = await response.json();
          setStats(data.statistics);
        }
      } catch (error) {
        console.error("Failed to fetch shift stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [shift]);

  if (loading) {
    return <div className="animate-pulse">Loading stats...</div>;
  }

  if (!stats) {
    return <div className="text-gray-400">Stats unavailable</div>;
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      <StatCard
        label="Critical Zones"
        value={stats.critical_zones || 0}
        color="red"
      />
      <StatCard
        label="High Risk Zones"
        value={stats.high_risk_zones || 0}
        color="orange"
      />
      <StatCard
        label="Stolen Vehicles"
        value={stats.stolen_vehicles || 0}
        color="yellow"
      />
      <StatCard
        label="Active Warrants"
        value={stats.active_warrants || 0}
        color="purple"
      />
    </div>
  );
}

// Stat card component
interface StatCardProps {
  label: string;
  value: number;
  color: "red" | "orange" | "yellow" | "purple" | "blue" | "green";
}

function StatCard({ label, value, color }: StatCardProps) {
  const colorClasses = {
    red: "bg-red-900/50 border-red-700 text-red-400",
    orange: "bg-orange-900/50 border-orange-700 text-orange-400",
    yellow: "bg-yellow-900/50 border-yellow-700 text-yellow-400",
    purple: "bg-purple-900/50 border-purple-700 text-purple-400",
    blue: "bg-blue-900/50 border-blue-700 text-blue-400",
    green: "bg-green-900/50 border-green-700 text-green-400",
  };

  return (
    <div className={`rounded-lg border p-3 ${colorClasses[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm opacity-80">{label}</div>
    </div>
  );
}

// Type definitions
interface TacticalEvent {
  type: string;
  severity?: string;
  message?: string;
  data?: Record<string, unknown>;
}

interface TacticalAlert {
  id: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

interface ShiftStats {
  zones_of_concern_count: number;
  critical_zones: number;
  high_risk_zones: number;
  vehicles_of_interest_count: number;
  stolen_vehicles: number;
  persons_of_interest_count: number;
  active_warrants: number;
  critical_advisories: number;
  high_advisories: number;
}
