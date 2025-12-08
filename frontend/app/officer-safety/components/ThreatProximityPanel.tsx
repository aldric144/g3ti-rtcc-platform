"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  AlertTriangle,
  Target,
  Car,
  User,
  Home,
  Crosshair,
  RefreshCw,
} from "lucide-react";

interface Officer {
  badge: string;
  unit: string;
  lat: number;
  lon: number;
  status: string;
}

interface Threat {
  id: string;
  type: string;
  severity: string;
  description: string;
  distance_m: number;
  location: { lat: number; lon: number };
}

interface ThreatProximityPanelProps {
  selectedOfficer: Officer | null;
  threats: Threat[];
}

export default function ThreatProximityPanel({
  selectedOfficer,
  threats,
}: ThreatProximityPanelProps) {
  const [localThreats, setLocalThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(false);
  const [radiusFilter, setRadiusFilter] = useState(600);

  // Mock threats for development
  useEffect(() => {
    if (selectedOfficer) {
      const mockThreats: Threat[] = [
        {
          id: "gunfire-1234",
          type: "gunfire",
          severity: "critical",
          description: "Gunfire detected 350m away (last 24h)",
          distance_m: 350,
          location: {
            lat: selectedOfficer.lat + 0.003,
            lon: selectedOfficer.lon + 0.002,
          },
        },
        {
          id: "voi-5678",
          type: "vehicle_of_interest",
          severity: "high",
          description: "Stolen vehicle (ABC123) seen 200m away",
          distance_m: 200,
          location: {
            lat: selectedOfficer.lat - 0.002,
            lon: selectedOfficer.lon + 0.001,
          },
        },
        {
          id: "offender-9012",
          type: "repeat_offender",
          severity: "high",
          description: "Repeat offender (violent crime) residence 150m away",
          distance_m: 150,
          location: {
            lat: selectedOfficer.lat + 0.001,
            lon: selectedOfficer.lon - 0.001,
          },
        },
        {
          id: "dv-3456",
          type: "domestic_violence",
          severity: "elevated",
          description: "DV history at address 100m away",
          distance_m: 100,
          location: {
            lat: selectedOfficer.lat - 0.001,
            lon: selectedOfficer.lon - 0.001,
          },
        },
      ];
      setLocalThreats(mockThreats);
    }
  }, [selectedOfficer]);

  const fetchThreats = async () => {
    if (!selectedOfficer) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/officer/threats/${selectedOfficer.badge}`);
      if (response.ok) {
        const data = await response.json();
        setLocalThreats(data.threats || []);
      }
    } catch (error) {
      console.error("Failed to fetch threats:", error);
    } finally {
      setLoading(false);
    }
  };

  const getThreatIcon = (type: string) => {
    switch (type) {
      case "gunfire":
        return <Target className="h-4 w-4" />;
      case "vehicle_of_interest":
        return <Car className="h-4 w-4" />;
      case "repeat_offender":
        return <User className="h-4 w-4" />;
      case "domestic_violence":
        return <Home className="h-4 w-4" />;
      case "ambush_zone":
        return <Crosshair className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500 text-white";
      case "high":
        return "bg-orange-500 text-white";
      case "elevated":
        return "bg-yellow-500 text-black";
      default:
        return "bg-gray-500 text-white";
    }
  };

  const getSeverityBadgeVariant = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return "destructive";
      case "elevated":
        return "warning";
      default:
        return "secondary";
    }
  };

  const filteredThreats = localThreats.filter((t) => t.distance_m <= radiusFilter);

  if (!selectedOfficer) {
    return (
      <Card className="h-full bg-gray-800 border-gray-700">
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center text-gray-400">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Select an officer to view threat proximity</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="h-full grid grid-cols-3 gap-4">
      {/* Threat List */}
      <div className="col-span-2">
        <Card className="h-full bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-red-400" />
                Threats Near {selectedOfficer.unit}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Input
                  type="number"
                  value={radiusFilter}
                  onChange={(e) => setRadiusFilter(parseInt(e.target.value) || 600)}
                  className="w-24 h-8 bg-gray-700 border-gray-600"
                  placeholder="Radius"
                />
                <span className="text-xs text-gray-400">m</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchThreats}
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto">
              {filteredThreats.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No threats within {radiusFilter}m radius</p>
                </div>
              ) : (
                filteredThreats.map((threat) => (
                  <Card
                    key={threat.id}
                    className={`bg-gray-700 border-l-4 ${
                      threat.severity === "critical"
                        ? "border-l-red-500"
                        : threat.severity === "high"
                        ? "border-l-orange-500"
                        : "border-l-yellow-500"
                    }`}
                  >
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          <div
                            className={`p-2 rounded ${getSeverityColor(threat.severity)}`}
                          >
                            {getThreatIcon(threat.type)}
                          </div>
                          <div>
                            <div className="font-medium text-white capitalize">
                              {threat.type.replace("_", " ")}
                            </div>
                            <div className="text-sm text-gray-300">
                              {threat.description}
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              Distance: {threat.distance_m}m
                            </div>
                          </div>
                        </div>
                        <Badge variant={getSeverityBadgeVariant(threat.severity) as any}>
                          {threat.severity}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Threat Summary */}
      <div className="space-y-4">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Threat Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Threats</span>
                <Badge variant="outline">{filteredThreats.length}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Critical</span>
                <Badge variant="destructive">
                  {filteredThreats.filter((t) => t.severity === "critical").length}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">High</span>
                <Badge className="bg-orange-500">
                  {filteredThreats.filter((t) => t.severity === "high").length}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Elevated</span>
                <Badge className="bg-yellow-500 text-black">
                  {filteredThreats.filter((t) => t.severity === "elevated").length}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Threat Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {["gunfire", "vehicle_of_interest", "repeat_offender", "domestic_violence"].map(
                (type) => {
                  const count = filteredThreats.filter((t) => t.type === type).length;
                  return (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getThreatIcon(type)}
                        <span className="text-sm text-gray-300 capitalize">
                          {type.replace("_", " ")}
                        </span>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  );
                }
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Radius Settings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button
                variant={radiusFilter === 300 ? "default" : "outline"}
                size="sm"
                className="w-full"
                onClick={() => setRadiusFilter(300)}
              >
                300m (Close)
              </Button>
              <Button
                variant={radiusFilter === 600 ? "default" : "outline"}
                size="sm"
                className="w-full"
                onClick={() => setRadiusFilter(600)}
              >
                600m (Default)
              </Button>
              <Button
                variant={radiusFilter === 1000 ? "default" : "outline"}
                size="sm"
                className="w-full"
                onClick={() => setRadiusFilter(1000)}
              >
                1000m (Extended)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
