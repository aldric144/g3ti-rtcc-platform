"use client";

import { useState, useEffect, useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Shield,
  MapPin,
  AlertTriangle,
  Radio,
  Users,
  Target,
  FileText,
  Bell,
} from "lucide-react";

import OfficerMap from "./components/OfficerMap";
import SafetyScoreCards from "./components/SafetyScoreCards";
import ThreatProximityPanel from "./components/ThreatProximityPanel";
import SceneIntelPanel from "./components/SceneIntelPanel";
import AmbushAlertsPanel from "./components/AmbushAlertsPanel";
import PerimeterView from "./components/PerimeterView";
import OfficerDownBanner from "./components/OfficerDownBanner";

interface Officer {
  badge: string;
  unit: string;
  lat: number;
  lon: number;
  status: string;
  speed?: number;
  heading?: number;
  safetyScore?: number;
  safetyLevel?: string;
}

interface Emergency {
  badge: string;
  type: string;
  message: string;
  timestamp: string;
  location?: { lat: number; lon: number };
}

export default function OfficerSafetyPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [officers, setOfficers] = useState<Officer[]>([]);
  const [selectedOfficer, setSelectedOfficer] = useState<Officer | null>(null);
  const [emergencies, setEmergencies] = useState<Emergency[]>([]);
  const [threats, setThreats] = useState<any[]>([]);
  const [ambushWarnings, setAmbushWarnings] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  // Mock data for development
  useEffect(() => {
    const mockOfficers: Officer[] = [
      {
        badge: "1234",
        unit: "Charlie-12",
        lat: 33.4484,
        lon: -112.074,
        status: "on_patrol",
        speed: 25,
        heading: 180,
        safetyScore: 0.32,
        safetyLevel: "elevated",
      },
      {
        badge: "5678",
        unit: "Bravo-21",
        lat: 33.4512,
        lon: -112.068,
        status: "en_route",
        speed: 45,
        heading: 90,
        safetyScore: 0.65,
        safetyLevel: "high",
      },
      {
        badge: "9012",
        unit: "Alpha-7",
        lat: 33.4456,
        lon: -112.082,
        status: "on_scene",
        speed: 0,
        heading: 0,
        safetyScore: 0.15,
        safetyLevel: "low",
      },
      {
        badge: "3456",
        unit: "Delta-15",
        lat: 33.4498,
        lon: -112.071,
        status: "available",
        speed: 0,
        heading: 45,
        safetyScore: 0.22,
        safetyLevel: "moderate",
      },
    ];
    setOfficers(mockOfficers);
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/realtime/ws/officer/location`;

        // In development, we'll simulate WebSocket updates
        setWsConnected(true);

        // Simulate periodic updates
        const interval = setInterval(() => {
          setOfficers((prev) =>
            prev.map((officer) => ({
              ...officer,
              lat: officer.lat + (Math.random() - 0.5) * 0.001,
              lon: officer.lon + (Math.random() - 0.5) * 0.001,
              speed: Math.max(0, (officer.speed || 0) + (Math.random() - 0.5) * 5),
            }))
          );
        }, 5000);

        return () => clearInterval(interval);
      } catch (error) {
        console.error("WebSocket connection error:", error);
        setWsConnected(false);
      }
    };

    const cleanup = connectWebSocket();
    return cleanup;
  }, []);

  const handleOfficerSelect = useCallback((officer: Officer) => {
    setSelectedOfficer(officer);
  }, []);

  const handleTriggerSOS = useCallback(async (badge: string) => {
    try {
      const response = await fetch("/api/officer/emergency/sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ badge, source: "manual" }),
      });
      if (response.ok) {
        const data = await response.json();
        setEmergencies((prev) => [
          ...prev,
          {
            badge,
            type: "officer_sos",
            message: data.message,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error("Failed to trigger SOS:", error);
    }
  }, []);

  const handleClearEmergency = useCallback(async (badge: string) => {
    try {
      const response = await fetch("/api/officer/emergency/clear", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ badge, cleared_by: "RTCC", reason: "Situation resolved" }),
      });
      if (response.ok) {
        setEmergencies((prev) => prev.filter((e) => e.badge !== badge));
      }
    } catch (error) {
      console.error("Failed to clear emergency:", error);
    }
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "on_patrol":
        return "bg-green-500";
      case "en_route":
        return "bg-blue-500";
      case "on_scene":
        return "bg-yellow-500";
      case "emergency":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getSafetyLevelColor = (level: string) => {
    switch (level) {
      case "critical":
        return "destructive";
      case "high":
        return "destructive";
      case "elevated":
        return "warning";
      case "moderate":
        return "secondary";
      default:
        return "default";
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Officer Down Banner */}
      {emergencies.length > 0 && (
        <OfficerDownBanner
          emergencies={emergencies}
          onClear={handleClearEmergency}
        />
      )}

      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold">Officer Safety Dashboard</h1>
              <p className="text-gray-400 text-sm">
                Real-time Field Awareness & Situational Intelligence
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Badge
              variant={wsConnected ? "default" : "destructive"}
              className="flex items-center space-x-1"
            >
              <Radio className="h-3 w-3" />
              <span>{wsConnected ? "Connected" : "Disconnected"}</span>
            </Badge>
            <Badge variant="outline" className="flex items-center space-x-1">
              <Users className="h-3 w-3" />
              <span>{officers.length} Officers Active</span>
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Officer List */}
        <aside className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Active Officers
            </h2>
            <div className="space-y-2">
              {officers.map((officer) => (
                <Card
                  key={officer.badge}
                  className={`cursor-pointer transition-colors ${
                    selectedOfficer?.badge === officer.badge
                      ? "bg-blue-900 border-blue-500"
                      : "bg-gray-700 border-gray-600 hover:bg-gray-600"
                  }`}
                  onClick={() => handleOfficerSelect(officer)}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{officer.unit}</div>
                        <div className="text-sm text-gray-400">
                          Badge: {officer.badge}
                        </div>
                      </div>
                      <div className="flex flex-col items-end space-y-1">
                        <div
                          className={`w-3 h-3 rounded-full ${getStatusColor(
                            officer.status
                          )}`}
                        />
                        {officer.safetyLevel && (
                          <Badge
                            variant={getSafetyLevelColor(officer.safetyLevel) as any}
                            className="text-xs"
                          >
                            {officer.safetyLevel}
                          </Badge>
                        )}
                      </div>
                    </div>
                    {officer.safetyScore !== undefined && (
                      <div className="mt-2">
                        <div className="text-xs text-gray-400">Safety Score</div>
                        <div className="w-full bg-gray-600 rounded-full h-2 mt-1">
                          <div
                            className={`h-2 rounded-full ${
                              officer.safetyScore > 0.6
                                ? "bg-red-500"
                                : officer.safetyScore > 0.4
                                ? "bg-yellow-500"
                                : "bg-green-500"
                            }`}
                            style={{ width: `${officer.safetyScore * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="flex-1 flex flex-col"
          >
            <TabsList className="bg-gray-800 border-b border-gray-700 px-4 py-2 justify-start">
              <TabsTrigger value="overview" className="flex items-center space-x-2">
                <MapPin className="h-4 w-4" />
                <span>Overview</span>
              </TabsTrigger>
              <TabsTrigger value="threats" className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4" />
                <span>Threats</span>
              </TabsTrigger>
              <TabsTrigger value="scene-intel" className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Scene Intel</span>
              </TabsTrigger>
              <TabsTrigger value="perimeter" className="flex items-center space-x-2">
                <Target className="h-4 w-4" />
                <span>Perimeter</span>
              </TabsTrigger>
              <TabsTrigger value="ambush" className="flex items-center space-x-2">
                <Bell className="h-4 w-4" />
                <span>Ambush Alerts</span>
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-hidden">
              <TabsContent value="overview" className="h-full m-0 p-4">
                <div className="grid grid-cols-3 gap-4 h-full">
                  <div className="col-span-2 h-full">
                    <OfficerMap
                      officers={officers}
                      selectedOfficer={selectedOfficer}
                      onOfficerSelect={handleOfficerSelect}
                      threats={threats}
                    />
                  </div>
                  <div className="space-y-4 overflow-y-auto">
                    <SafetyScoreCards
                      officers={officers}
                      selectedOfficer={selectedOfficer}
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="threats" className="h-full m-0 p-4">
                <ThreatProximityPanel
                  selectedOfficer={selectedOfficer}
                  threats={threats}
                />
              </TabsContent>

              <TabsContent value="scene-intel" className="h-full m-0 p-4">
                <SceneIntelPanel selectedOfficer={selectedOfficer} />
              </TabsContent>

              <TabsContent value="perimeter" className="h-full m-0 p-4">
                <PerimeterView selectedOfficer={selectedOfficer} />
              </TabsContent>

              <TabsContent value="ambush" className="h-full m-0 p-4">
                <AmbushAlertsPanel
                  warnings={ambushWarnings}
                  selectedOfficer={selectedOfficer}
                />
              </TabsContent>
            </div>
          </Tabs>
        </main>

        {/* Right Panel - Quick Actions */}
        <aside className="w-64 bg-gray-800 border-l border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Button
              variant="destructive"
              className="w-full"
              onClick={() =>
                selectedOfficer && handleTriggerSOS(selectedOfficer.badge)
              }
              disabled={!selectedOfficer}
            >
              <AlertTriangle className="h-4 w-4 mr-2" />
              Trigger SOS
            </Button>
            <Button variant="outline" className="w-full" disabled={!selectedOfficer}>
              <FileText className="h-4 w-4 mr-2" />
              Generate Field Packet
            </Button>
            <Button variant="outline" className="w-full" disabled={!selectedOfficer}>
              <Target className="h-4 w-4 mr-2" />
              Create Perimeter
            </Button>
            <Button variant="outline" className="w-full">
              <Radio className="h-4 w-4 mr-2" />
              Broadcast Alert
            </Button>
          </div>

          {selectedOfficer && (
            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">
                Selected Officer
              </h3>
              <Card className="bg-gray-700 border-gray-600">
                <CardContent className="p-3">
                  <div className="text-lg font-bold">{selectedOfficer.unit}</div>
                  <div className="text-sm text-gray-400">
                    Badge: {selectedOfficer.badge}
                  </div>
                  <div className="text-sm text-gray-400">
                    Status: {selectedOfficer.status}
                  </div>
                  {selectedOfficer.speed !== undefined && (
                    <div className="text-sm text-gray-400">
                      Speed: {selectedOfficer.speed.toFixed(0)} mph
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
