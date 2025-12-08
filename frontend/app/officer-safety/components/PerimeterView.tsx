"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Target,
  MapPin,
  Navigation,
  Users,
  AlertTriangle,
  Plus,
  RefreshCw,
} from "lucide-react";

interface Officer {
  badge: string;
  unit: string;
  lat: number;
  lon: number;
  status: string;
}

interface Route {
  direction: string;
  approach_point: { lat: number; lon: number };
  waypoints: { lat: number; lon: number; sequence: number }[];
  distance_m: number;
  cover_available: boolean;
  visibility: string;
  recommendation?: string;
  warning?: string;
}

interface StagingArea {
  id: string;
  location: { lat: number; lon: number };
  type: string;
  capacity: number;
  distance_m: number;
}

interface EscapeRoute {
  id: string;
  direction: string;
  road_type: string;
  exit_point: { lat: number; lon: number };
  risk_level: string;
  recommendation: string;
}

interface Perimeter {
  perimeter_id: string;
  incident_id: string;
  center: { lat: number; lon: number };
  generated_at: string;
  inner_perimeter: {
    radius_m: number;
    polygon: { lat: number; lon: number }[];
    description: string;
  };
  outer_perimeter: {
    radius_m: number;
    polygon: { lat: number; lon: number }[];
    description: string;
  };
  routes: {
    blue_routes: Route[];
    red_routes: Route[];
    primary_approach: Route | null;
  };
  staging_areas: StagingArea[];
  escape_routes: EscapeRoute[];
  units_assigned: string[];
  risk_multiplier: number;
  recommendations: string[];
}

interface PerimeterViewProps {
  selectedOfficer: Officer | null;
}

export default function PerimeterView({ selectedOfficer }: PerimeterViewProps) {
  const [perimeter, setPerimeter] = useState<Perimeter | null>(null);
  const [loading, setLoading] = useState(false);
  const [incidentType, setIncidentType] = useState("default");
  const [units, setUnits] = useState<string[]>([]);
  const mapRef = useRef<HTMLDivElement>(null);

  // Mock perimeter for development
  useEffect(() => {
    if (selectedOfficer) {
      const mockPerimeter: Perimeter = {
        perimeter_id: `PER-INC-001-${Date.now()}`,
        incident_id: "INC-001",
        center: { lat: selectedOfficer.lat, lon: selectedOfficer.lon },
        generated_at: new Date().toISOString(),
        inner_perimeter: {
          radius_m: 100,
          polygon: generateCirclePolygon(selectedOfficer.lat, selectedOfficer.lon, 100),
          description: "Inner perimeter - restricted access",
        },
        outer_perimeter: {
          radius_m: 250,
          polygon: generateCirclePolygon(selectedOfficer.lat, selectedOfficer.lon, 250),
          description: "Outer perimeter - controlled access",
        },
        routes: {
          blue_routes: [
            {
              direction: "north",
              approach_point: {
                lat: selectedOfficer.lat + 0.002,
                lon: selectedOfficer.lon,
              },
              waypoints: [
                { lat: selectedOfficer.lat + 0.0015, lon: selectedOfficer.lon, sequence: 1 },
                { lat: selectedOfficer.lat + 0.001, lon: selectedOfficer.lon, sequence: 2 },
              ],
              distance_m: 250,
              cover_available: true,
              visibility: "good",
              recommendation: "Recommended approach",
            },
            {
              direction: "east",
              approach_point: {
                lat: selectedOfficer.lat,
                lon: selectedOfficer.lon + 0.003,
              },
              waypoints: [
                { lat: selectedOfficer.lat, lon: selectedOfficer.lon + 0.002, sequence: 1 },
              ],
              distance_m: 250,
              cover_available: true,
              visibility: "moderate",
              recommendation: "Recommended approach",
            },
          ],
          red_routes: [
            {
              direction: "south",
              approach_point: {
                lat: selectedOfficer.lat - 0.002,
                lon: selectedOfficer.lon,
              },
              waypoints: [],
              distance_m: 250,
              cover_available: false,
              visibility: "limited",
              warning: "High exposure - limited cover",
            },
          ],
          primary_approach: null,
        },
        staging_areas: [
          {
            id: "STAGE-1",
            location: {
              lat: selectedOfficer.lat + 0.003,
              lon: selectedOfficer.lon + 0.002,
            },
            type: "command_post",
            capacity: 10,
            distance_m: 375,
          },
          {
            id: "STAGE-2",
            location: {
              lat: selectedOfficer.lat - 0.002,
              lon: selectedOfficer.lon + 0.003,
            },
            type: "medical",
            capacity: 5,
            distance_m: 400,
          },
        ],
        escape_routes: [
          {
            id: "ESC-1",
            direction: "NW",
            road_type: "Highway",
            exit_point: {
              lat: selectedOfficer.lat + 0.002,
              lon: selectedOfficer.lon - 0.002,
            },
            risk_level: "high",
            recommendation: "Position unit to monitor",
          },
          {
            id: "ESC-2",
            direction: "SE",
            road_type: "Main Street",
            exit_point: {
              lat: selectedOfficer.lat - 0.002,
              lon: selectedOfficer.lon + 0.002,
            },
            risk_level: "medium",
            recommendation: "Block if possible",
          },
        ],
        units_assigned: ["Charlie-12", "Bravo-21", "Alpha-7"],
        risk_multiplier: 1.5,
        recommendations: [
          "Extended perimeter due to elevated threat level",
          "Firearm(s) involved - maintain cover at all times",
          "Consider ballistic shields for approach",
        ],
      };
      mockPerimeter.routes.primary_approach = mockPerimeter.routes.blue_routes[0];
      setPerimeter(mockPerimeter);
      setUnits(mockPerimeter.units_assigned);
    }
  }, [selectedOfficer]);

  const generateCirclePolygon = (
    centerLat: number,
    centerLon: number,
    radiusM: number,
    numPoints: number = 32
  ) => {
    const points: { lat: number; lon: number }[] = [];
    for (let i = 0; i < numPoints; i++) {
      const angle = (2 * Math.PI * i) / numPoints;
      const latOffset = (radiusM / 111320) * Math.cos(angle);
      const lonOffset =
        (radiusM / (111320 * Math.cos((centerLat * Math.PI) / 180))) * Math.sin(angle);
      points.push({
        lat: centerLat + latOffset,
        lon: centerLon + lonOffset,
      });
    }
    points.push(points[0]); // Close the polygon
    return points;
  };

  const generatePerimeter = async () => {
    if (!selectedOfficer) return;

    setLoading(true);
    try {
      const response = await fetch("/api/officer/perimeter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_id: `INC-${Date.now()}`,
          units: units,
          location: [selectedOfficer.lat, selectedOfficer.lon],
          incident_type: incidentType,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setPerimeter(data);
      }
    } catch (error) {
      console.error("Failed to generate perimeter:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRouteColor = (isBlue: boolean) => (isBlue ? "#3b82f6" : "#ef4444");

  if (!selectedOfficer) {
    return (
      <Card className="h-full bg-gray-800 border-gray-700">
        <CardContent className="flex flex-col items-center justify-center h-full">
          <Target className="h-12 w-12 mb-4 text-gray-500" />
          <p className="text-gray-400 mb-4">
            Select an officer to generate tactical perimeter
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="h-full grid grid-cols-3 gap-4">
      {/* Perimeter Map */}
      <div className="col-span-2">
        <Card className="h-full bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <Target className="h-5 w-5 mr-2" />
                Tactical Perimeter View
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={generatePerimeter}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`} />
                Regenerate
              </Button>
            </div>
          </CardHeader>
          <CardContent className="h-[calc(100%-60px)]">
            <div
              ref={mapRef}
              className="w-full h-full bg-gray-900 rounded-lg relative overflow-hidden"
            >
              {/* Grid */}
              <svg className="absolute inset-0 w-full h-full">
                <defs>
                  <pattern
                    id="perimeter-grid"
                    width="40"
                    height="40"
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d="M 40 0 L 0 0 0 40"
                      fill="none"
                      stroke="#374151"
                      strokeWidth="0.5"
                    />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#perimeter-grid)" />

                {perimeter && (
                  <>
                    {/* Outer Perimeter */}
                    <circle
                      cx="50%"
                      cy="50%"
                      r="40%"
                      fill="rgba(239, 68, 68, 0.1)"
                      stroke="#ef4444"
                      strokeWidth="2"
                      strokeDasharray="10,5"
                    />

                    {/* Inner Perimeter */}
                    <circle
                      cx="50%"
                      cy="50%"
                      r="20%"
                      fill="rgba(249, 115, 22, 0.1)"
                      stroke="#f97316"
                      strokeWidth="2"
                    />

                    {/* Blue Routes */}
                    {perimeter.routes.blue_routes.map((route, index) => {
                      const angle =
                        route.direction === "north"
                          ? -90
                          : route.direction === "south"
                          ? 90
                          : route.direction === "east"
                          ? 0
                          : 180;
                      const rad = (angle * Math.PI) / 180;
                      const x2 = 50 + 35 * Math.cos(rad);
                      const y2 = 50 + 35 * Math.sin(rad);
                      return (
                        <line
                          key={`blue-${index}`}
                          x1="50%"
                          y1="50%"
                          x2={`${x2}%`}
                          y2={`${y2}%`}
                          stroke="#3b82f6"
                          strokeWidth="3"
                          markerEnd="url(#arrowhead-blue)"
                        />
                      );
                    })}

                    {/* Red Routes */}
                    {perimeter.routes.red_routes.map((route, index) => {
                      const angle =
                        route.direction === "north"
                          ? -90
                          : route.direction === "south"
                          ? 90
                          : route.direction === "east"
                          ? 0
                          : 180;
                      const rad = (angle * Math.PI) / 180;
                      const x2 = 50 + 35 * Math.cos(rad);
                      const y2 = 50 + 35 * Math.sin(rad);
                      return (
                        <line
                          key={`red-${index}`}
                          x1="50%"
                          y1="50%"
                          x2={`${x2}%`}
                          y2={`${y2}%`}
                          stroke="#ef4444"
                          strokeWidth="3"
                          strokeDasharray="5,5"
                        />
                      );
                    })}

                    {/* Arrow markers */}
                    <defs>
                      <marker
                        id="arrowhead-blue"
                        markerWidth="10"
                        markerHeight="7"
                        refX="9"
                        refY="3.5"
                        orient="auto"
                      >
                        <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6" />
                      </marker>
                    </defs>
                  </>
                )}
              </svg>

              {/* Center Point (Incident) */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                <div className="w-6 h-6 bg-red-500 rounded-full border-2 border-white flex items-center justify-center animate-pulse">
                  <AlertTriangle className="h-3 w-3 text-white" />
                </div>
              </div>

              {/* Staging Areas */}
              {perimeter?.staging_areas.map((area, index) => {
                const offsetX = index === 0 ? 30 : -25;
                const offsetY = index === 0 ? -35 : 30;
                return (
                  <div
                    key={area.id}
                    className="absolute z-10"
                    style={{
                      left: `calc(50% + ${offsetX}%)`,
                      top: `calc(50% + ${offsetY}%)`,
                      transform: "translate(-50%, -50%)",
                    }}
                  >
                    <div className="bg-green-600 px-2 py-1 rounded text-xs flex items-center space-x-1">
                      <Users className="h-3 w-3" />
                      <span>{area.type.replace("_", " ")}</span>
                    </div>
                  </div>
                );
              })}

              {/* Legend */}
              <div className="absolute bottom-4 left-4 bg-gray-800 bg-opacity-90 p-3 rounded-lg">
                <div className="text-xs font-semibold mb-2">Legend</div>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-orange-500" />
                    <span>Inner Perimeter</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-red-500 border-dashed" />
                    <span>Outer Perimeter</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-blue-500" />
                    <span>Blue Route (Safe)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-red-500" style={{ borderStyle: "dashed" }} />
                    <span>Red Route (High Risk)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-600 rounded" />
                    <span>Staging Area</span>
                  </div>
                </div>
              </div>

              {/* Perimeter Info */}
              {perimeter && (
                <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 px-3 py-2 rounded-lg">
                  <div className="text-xs">
                    <div className="text-gray-400">Inner: {perimeter.inner_perimeter.radius_m}m</div>
                    <div className="text-gray-400">Outer: {perimeter.outer_perimeter.radius_m}m</div>
                    <div className="text-gray-400">
                      Risk Multiplier: {perimeter.risk_multiplier}x
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Side Panel */}
      <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
        {/* Generate Perimeter */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Generate Perimeter</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400">Incident Type</label>
                <Select value={incidentType} onValueChange={setIncidentType}>
                  <SelectTrigger className="bg-gray-700 border-gray-600">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default</SelectItem>
                    <SelectItem value="active_shooter">Active Shooter</SelectItem>
                    <SelectItem value="armed_robbery">Armed Robbery</SelectItem>
                    <SelectItem value="hostage">Hostage</SelectItem>
                    <SelectItem value="barricaded_subject">Barricaded Subject</SelectItem>
                    <SelectItem value="domestic_violence">Domestic Violence</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs text-gray-400">Assigned Units</label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {units.map((unit) => (
                    <Badge key={unit} variant="secondary" className="text-xs">
                      {unit}
                    </Badge>
                  ))}
                </div>
              </div>
              <Button
                className="w-full"
                onClick={generatePerimeter}
                disabled={loading}
              >
                <Target className="h-4 w-4 mr-2" />
                Generate Perimeter
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Approach Routes */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <Navigation className="h-4 w-4 mr-2" />
              Approach Routes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-xs text-blue-400 font-medium">Blue Routes (Recommended)</div>
              {perimeter?.routes.blue_routes.map((route, index) => (
                <div key={index} className="p-2 bg-blue-900 rounded text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium capitalize">{route.direction}</span>
                    <Badge variant="default" className="text-xs">
                      {route.visibility}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-300 mt-1">
                    {route.distance_m}m | Cover: {route.cover_available ? "Yes" : "No"}
                  </div>
                </div>
              ))}

              <div className="text-xs text-red-400 font-medium mt-3">Red Routes (High Risk)</div>
              {perimeter?.routes.red_routes.map((route, index) => (
                <div key={index} className="p-2 bg-red-900 rounded text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium capitalize">{route.direction}</span>
                    <Badge variant="destructive" className="text-xs">
                      {route.visibility}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-300 mt-1">{route.warning}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Escape Routes */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Escape Routes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {perimeter?.escape_routes.map((route) => (
                <div key={route.id} className="p-2 bg-gray-700 rounded text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">
                      {route.direction} - {route.road_type}
                    </span>
                    <Badge
                      variant={route.risk_level === "high" ? "destructive" : "secondary"}
                      className="text-xs"
                    >
                      {route.risk_level}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{route.recommendation}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        {perimeter?.recommendations && perimeter.recommendations.length > 0 && (
          <Card className="bg-yellow-900 border-yellow-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Tactical Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {perimeter.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-yellow-400">-</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
