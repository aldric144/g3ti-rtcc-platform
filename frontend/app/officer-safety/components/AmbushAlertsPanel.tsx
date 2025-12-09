"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  AlertTriangle,
  Eye,
  Car,
  Users,
  Clock,
  MapPin,
  Shield,
  RefreshCw,
  CheckCircle,
} from "lucide-react";

interface Officer {
  badge: string;
  unit: string;
  lat: number;
  lon: number;
  status: string;
}

interface AmbushWarning {
  badge: string;
  location: { lat: number; lon: number };
  warning: boolean;
  risk_score: number;
  indicators: {
    civilian_absence: { detected: boolean; score: number; description?: string };
    vehicle_circling: { detected: boolean; score: number; description?: string };
    weapon_anomalies: { detected: boolean; score: number; description?: string };
    movement_anomalies: { detected: boolean; score: number; description?: string };
    timing_anomalies: { detected: boolean; score: number; description?: string };
    entity_convergence: { detected: boolean; score: number; description?: string };
  };
  warning_factors: string[];
  message?: string;
  severity?: string;
  checked_at: string;
}

interface AmbushAlertsPanelProps {
  warnings: AmbushWarning[];
  selectedOfficer: Officer | null;
}

export default function AmbushAlertsPanel({
  warnings,
  selectedOfficer,
}: AmbushAlertsPanelProps) {
  const [localWarnings, setLocalWarnings] = useState<AmbushWarning[]>([]);
  const [currentCheck, setCurrentCheck] = useState<AmbushWarning | null>(null);
  const [loading, setLoading] = useState(false);

  // Mock warnings for development
  useEffect(() => {
    const mockWarnings: AmbushWarning[] = [
      {
        badge: "5678",
        location: { lat: 33.4512, lon: -112.068 },
        warning: true,
        risk_score: 0.72,
        indicators: {
          civilian_absence: {
            detected: true,
            score: 0.8,
            description: "Unusual lack of civilian presence in normally busy area",
          },
          vehicle_circling: {
            detected: true,
            score: 0.75,
            description: "Suspicious vehicle circling detected (4 passes)",
          },
          weapon_anomalies: { detected: false, score: 0.2 },
          movement_anomalies: { detected: false, score: 0.3 },
          timing_anomalies: { detected: false, score: 0.4 },
          entity_convergence: {
            detected: true,
            score: 0.65,
            description: "Suspicious entity convergence detected (3 entities)",
          },
        },
        warning_factors: [
          "Unusual lack of civilian presence in normally busy area",
          "Suspicious vehicle circling detected (4 passes)",
          "Suspicious entity convergence detected (3 entities)",
        ],
        message:
          "AMBUSH WARNING: Multiple indicators detected - Unusual lack of civilian presence, Suspicious vehicle circling, Entity convergence",
        severity: "critical",
        checked_at: new Date().toISOString(),
      },
    ];
    setLocalWarnings(mockWarnings);
  }, []);

  const checkAmbushPatterns = useCallback(async () => {
    if (!selectedOfficer) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/officer/ambush/${selectedOfficer.badge}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentCheck(data);
      }
    } catch (error) {
      console.error("Failed to check ambush patterns:", error);
      // Use mock data for development
      const mockCheck: AmbushWarning = {
        badge: selectedOfficer.badge,
        location: { lat: selectedOfficer.lat, lon: selectedOfficer.lon },
        warning: Math.random() > 0.7,
        risk_score: Math.random() * 0.5,
        indicators: {
          civilian_absence: { detected: false, score: Math.random() * 0.4 },
          vehicle_circling: { detected: false, score: Math.random() * 0.3 },
          weapon_anomalies: { detected: false, score: Math.random() * 0.2 },
          movement_anomalies: { detected: false, score: Math.random() * 0.3 },
          timing_anomalies: { detected: false, score: Math.random() * 0.2 },
          entity_convergence: { detected: false, score: Math.random() * 0.3 },
        },
        warning_factors: [],
        checked_at: new Date().toISOString(),
      };
      setCurrentCheck(mockCheck);
    } finally {
      setLoading(false);
    }
  }, [selectedOfficer]);

  // Check for ambush patterns when officer is selected
  useEffect(() => {
    if (selectedOfficer) {
      checkAmbushPatterns();
    }
  }, [selectedOfficer, checkAmbushPatterns]);

  const getIndicatorIcon = (indicator: string) => {
    switch (indicator) {
      case "civilian_absence":
        return <Users className="h-4 w-4" />;
      case "vehicle_circling":
        return <Car className="h-4 w-4" />;
      case "weapon_anomalies":
        return <AlertTriangle className="h-4 w-4" />;
      case "movement_anomalies":
        return <MapPin className="h-4 w-4" />;
      case "timing_anomalies":
        return <Clock className="h-4 w-4" />;
      case "entity_convergence":
        return <Eye className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getIndicatorLabel = (indicator: string) => {
    switch (indicator) {
      case "civilian_absence":
        return "Civilian Absence";
      case "vehicle_circling":
        return "Vehicle Circling";
      case "weapon_anomalies":
        return "Weapon Anomalies";
      case "movement_anomalies":
        return "Movement Anomalies";
      case "timing_anomalies":
        return "Timing Anomalies";
      case "entity_convergence":
        return "Entity Convergence";
      default:
        return indicator;
    }
  };

  return (
    <div className="h-full grid grid-cols-3 gap-4">
      {/* Active Warnings */}
      <div className="col-span-2 space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
        {/* Active Warnings Header */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-red-400" />
                Active Ambush Warnings
              </CardTitle>
              <Badge variant={localWarnings.length > 0 ? "destructive" : "default"}>
                {localWarnings.length} Active
              </Badge>
            </div>
          </CardHeader>
        </Card>

        {/* Warning Cards */}
        {localWarnings.length === 0 ? (
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
              <p className="text-gray-400">No active ambush warnings</p>
              <p className="text-sm text-gray-500 mt-2">
                All officers are in safe zones
              </p>
            </CardContent>
          </Card>
        ) : (
          localWarnings.map((warning, index) => (
            <Alert
              key={index}
              variant="destructive"
              className="bg-red-900 border-red-700"
            >
              <AlertTriangle className="h-5 w-5" />
              <AlertTitle className="flex items-center justify-between">
                <span>AMBUSH WARNING - Unit {warning.badge}</span>
                <Badge variant="destructive">{warning.severity?.toUpperCase()}</Badge>
              </AlertTitle>
              <AlertDescription className="mt-2">
                <p className="font-medium mb-2">{warning.message}</p>
                <div className="grid grid-cols-2 gap-2 mt-3">
                  {warning.warning_factors.map((factor, i) => (
                    <div
                      key={i}
                      className="flex items-center space-x-2 text-sm bg-red-800 p-2 rounded"
                    >
                      <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs text-gray-300">
                    Risk Score: {(warning.risk_score * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-gray-300">
                    Checked: {new Date(warning.checked_at).toLocaleTimeString()}
                  </span>
                </div>
              </AlertDescription>
            </Alert>
          ))
        )}

        {/* Current Officer Check */}
        {selectedOfficer && currentCheck && (
          <Card
            className={`border-2 ${
              currentCheck.warning
                ? "bg-red-900 border-red-500"
                : "bg-gray-800 border-gray-700"
            }`}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center text-sm">
                  <Shield className="h-4 w-4 mr-2" />
                  Ambush Check: {selectedOfficer.unit}
                </CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={checkAmbushPatterns}
                  disabled={loading}
                >
                  <RefreshCw
                    className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`}
                  />
                  Recheck
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {currentCheck.warning ? (
                    <AlertTriangle className="h-5 w-5 text-red-400" />
                  ) : (
                    <CheckCircle className="h-5 w-5 text-green-400" />
                  )}
                  <span className="font-medium">
                    {currentCheck.warning ? "Warning Detected" : "Area Clear"}
                  </span>
                </div>
                <Badge
                  variant={currentCheck.warning ? "destructive" : "default"}
                >
                  Risk: {(currentCheck.risk_score * 100).toFixed(0)}%
                </Badge>
              </div>

              {/* Indicator Grid */}
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(currentCheck.indicators).map(([key, value]) => (
                  <div
                    key={key}
                    className={`p-2 rounded flex items-center justify-between ${
                      value.detected ? "bg-red-800" : "bg-gray-700"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {getIndicatorIcon(key)}
                      <span className="text-xs">{getIndicatorLabel(key)}</span>
                    </div>
                    <span className="text-xs font-mono">
                      {(value.score * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>

              {currentCheck.warning_factors.length > 0 && (
                <div className="mt-4 p-3 bg-red-800 rounded">
                  <div className="text-xs font-medium mb-2">Warning Factors:</div>
                  <ul className="text-xs space-y-1">
                    {currentCheck.warning_factors.map((factor, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Side Panel */}
      <div className="space-y-4">
        {/* Detection Indicators Legend */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Detection Indicators</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start space-x-2">
                <Users className="h-4 w-4 mt-0.5 text-blue-400" />
                <div>
                  <div className="text-sm font-medium">Civilian Absence</div>
                  <div className="text-xs text-gray-400">
                    Unusual lack of civilian presence in normally busy areas
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Car className="h-4 w-4 mt-0.5 text-yellow-400" />
                <div>
                  <div className="text-sm font-medium">Vehicle Circling</div>
                  <div className="text-xs text-gray-400">
                    Suspicious LPR vehicle circling patterns
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <AlertTriangle className="h-4 w-4 mt-0.5 text-red-400" />
                <div>
                  <div className="text-sm font-medium">Weapon Anomalies</div>
                  <div className="text-xs text-gray-400">
                    Weapon-related anomalies detected
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <MapPin className="h-4 w-4 mt-0.5 text-purple-400" />
                <div>
                  <div className="text-sm font-medium">Movement Anomalies</div>
                  <div className="text-xs text-gray-400">
                    Multi-point movement anomalies
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Clock className="h-4 w-4 mt-0.5 text-orange-400" />
                <div>
                  <div className="text-sm font-medium">Timing Anomalies</div>
                  <div className="text-xs text-gray-400">
                    Coordinated timing anomalies
                  </div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Eye className="h-4 w-4 mt-0.5 text-green-400" />
                <div>
                  <div className="text-sm font-medium">Entity Convergence</div>
                  <div className="text-xs text-gray-400">
                    Suspicious entity convergence detected
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Thresholds */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Detection Thresholds</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Civilian Absence</span>
                <span>70%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Vehicle Circling</span>
                <span>3 passes</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Weapon Anomaly</span>
                <span>60%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Movement Anomaly</span>
                <span>65%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Timing Anomaly</span>
                <span>70%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Entity Convergence</span>
                <span>3 entities</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={checkAmbushPatterns}
                disabled={!selectedOfficer || loading}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Check Selected Officer
              </Button>
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                View All Checks
              </Button>
              <Button variant="destructive" size="sm" className="w-full">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Broadcast Warning
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
