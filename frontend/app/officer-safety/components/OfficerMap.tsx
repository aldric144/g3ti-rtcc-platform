"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, AlertTriangle } from "lucide-react";

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

interface Threat {
  id: string;
  type: string;
  lat: number;
  lon: number;
  severity: string;
  description: string;
}

interface OfficerMapProps {
  officers: Officer[];
  selectedOfficer: Officer | null;
  onOfficerSelect: (officer: Officer) => void;
  threats: Threat[];
}

export default function OfficerMap({
  officers,
  selectedOfficer,
  onOfficerSelect,
  threats,
}: OfficerMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Calculate map bounds
  const getBounds = () => {
    if (officers.length === 0) {
      return { minLat: 33.44, maxLat: 33.46, minLon: -112.08, maxLon: -112.06 };
    }
    const lats = officers.map((o) => o.lat);
    const lons = officers.map((o) => o.lon);
    return {
      minLat: Math.min(...lats) - 0.01,
      maxLat: Math.max(...lats) + 0.01,
      minLon: Math.min(...lons) - 0.01,
      maxLon: Math.max(...lons) + 0.01,
    };
  };

  const bounds = getBounds();

  // Convert lat/lon to pixel coordinates
  const toPixel = (lat: number, lon: number, width: number, height: number) => {
    const x = ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * width;
    const y = ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * height;
    return { x, y };
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "on_patrol":
        return "#22c55e";
      case "en_route":
        return "#3b82f6";
      case "on_scene":
        return "#eab308";
      case "emergency":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  };

  const getSafetyColor = (level: string | undefined) => {
    switch (level) {
      case "critical":
        return "#ef4444";
      case "high":
        return "#f97316";
      case "elevated":
        return "#eab308";
      case "moderate":
        return "#22c55e";
      default:
        return "#6b7280";
    }
  };

  const getThreatColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "#ef4444";
      case "high":
        return "#f97316";
      case "elevated":
        return "#eab308";
      default:
        return "#6b7280";
    }
  };

  return (
    <Card className="h-full bg-gray-800 border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center text-white">
          <MapPin className="h-5 w-5 mr-2" />
          Live Officer Map
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[calc(100%-60px)]">
        <div
          ref={mapContainerRef}
          className="w-full h-full bg-gray-900 rounded-lg relative overflow-hidden"
        >
          {/* Grid lines */}
          <svg className="absolute inset-0 w-full h-full">
            <defs>
              <pattern
                id="grid"
                width="50"
                height="50"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 50 0 L 0 0 0 50"
                  fill="none"
                  stroke="#374151"
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>

          {/* Threat markers */}
          {threats.map((threat) => {
            const pos = toPixel(
              threat.lat,
              threat.lon,
              mapContainerRef.current?.clientWidth || 800,
              mapContainerRef.current?.clientHeight || 600
            );
            return (
              <div
                key={threat.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 z-10"
                style={{ left: pos.x, top: pos.y }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center animate-pulse"
                  style={{ backgroundColor: `${getThreatColor(threat.severity)}40` }}
                >
                  <AlertTriangle
                    className="h-4 w-4"
                    style={{ color: getThreatColor(threat.severity) }}
                  />
                </div>
              </div>
            );
          })}

          {/* Officer markers */}
          {officers.map((officer) => {
            const pos = toPixel(
              officer.lat,
              officer.lon,
              mapContainerRef.current?.clientWidth || 800,
              mapContainerRef.current?.clientHeight || 600
            );
            const isSelected = selectedOfficer?.badge === officer.badge;

            return (
              <div
                key={officer.badge}
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all z-20 ${
                  isSelected ? "scale-125" : "hover:scale-110"
                }`}
                style={{ left: pos.x, top: pos.y }}
                onClick={() => onOfficerSelect(officer)}
              >
                {/* Safety ring */}
                {officer.safetyLevel && (
                  <div
                    className="absolute inset-0 rounded-full animate-ping"
                    style={{
                      backgroundColor: `${getSafetyColor(officer.safetyLevel)}20`,
                      width: "40px",
                      height: "40px",
                      marginLeft: "-8px",
                      marginTop: "-8px",
                    }}
                  />
                )}

                {/* Officer icon */}
                <div
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    isSelected ? "border-white" : "border-gray-600"
                  }`}
                  style={{ backgroundColor: getStatusColor(officer.status) }}
                >
                  <span className="text-xs font-bold text-white">
                    {officer.unit.split("-")[1] || officer.badge.slice(-2)}
                  </span>
                </div>

                {/* Label */}
                {isSelected && (
                  <div className="absolute top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 px-2 py-1 rounded text-xs whitespace-nowrap">
                    <div className="font-bold">{officer.unit}</div>
                    <div className="text-gray-400">{officer.status}</div>
                  </div>
                )}

                {/* Heading indicator */}
                {officer.heading !== undefined && officer.speed && officer.speed > 5 && (
                  <div
                    className="absolute w-0 h-0 border-l-4 border-r-4 border-b-8 border-l-transparent border-r-transparent"
                    style={{
                      borderBottomColor: getStatusColor(officer.status),
                      transform: `rotate(${officer.heading}deg)`,
                      transformOrigin: "center bottom",
                      top: "-12px",
                      left: "50%",
                      marginLeft: "-4px",
                    }}
                  />
                )}
              </div>
            );
          })}

          {/* Legend */}
          <div className="absolute bottom-4 left-4 bg-gray-800 bg-opacity-90 p-3 rounded-lg">
            <div className="text-xs font-semibold mb-2">Status Legend</div>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-xs">On Patrol</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-xs">En Route</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-xs">On Scene</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-xs">Emergency</span>
              </div>
            </div>
          </div>

          {/* Coordinates display */}
          <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 px-3 py-2 rounded-lg">
            <div className="text-xs text-gray-400">
              {officers.length} officers active
            </div>
            {selectedOfficer && (
              <div className="text-xs mt-1">
                <span className="text-gray-400">Selected: </span>
                <span className="text-white">{selectedOfficer.unit}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
