"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Shield, AlertTriangle, TrendingUp, TrendingDown } from "lucide-react";

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

interface SafetyScoreCardsProps {
  officers: Officer[];
  selectedOfficer: Officer | null;
}

export default function SafetyScoreCards({
  officers,
  selectedOfficer,
}: SafetyScoreCardsProps) {
  const getSafetyLevelColor = (level: string | undefined) => {
    switch (level) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "elevated":
        return "bg-yellow-500";
      case "moderate":
        return "bg-green-500";
      case "low":
        return "bg-green-600";
      default:
        return "bg-gray-500";
    }
  };

  const getSafetyBadgeVariant = (level: string | undefined) => {
    switch (level) {
      case "critical":
      case "high":
        return "destructive";
      case "elevated":
        return "warning";
      default:
        return "default";
    }
  };

  // Calculate aggregate stats
  const criticalCount = officers.filter(
    (o) => o.safetyLevel === "critical" || o.safetyLevel === "high"
  ).length;
  const elevatedCount = officers.filter((o) => o.safetyLevel === "elevated").length;
  const avgScore =
    officers.reduce((sum, o) => sum + (o.safetyScore || 0), 0) / officers.length;

  // Sort officers by safety score (highest risk first)
  const sortedOfficers = [...officers].sort(
    (a, b) => (b.safetyScore || 0) - (a.safetyScore || 0)
  );

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-white flex items-center text-sm">
            <Shield className="h-4 w-4 mr-2" />
            Safety Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-gray-700 rounded p-2">
              <div className="text-2xl font-bold text-red-400">{criticalCount}</div>
              <div className="text-xs text-gray-400">High Risk</div>
            </div>
            <div className="bg-gray-700 rounded p-2">
              <div className="text-2xl font-bold text-yellow-400">{elevatedCount}</div>
              <div className="text-xs text-gray-400">Elevated</div>
            </div>
            <div className="bg-gray-700 rounded p-2">
              <div className="text-2xl font-bold text-green-400">
                {officers.length - criticalCount - elevatedCount}
              </div>
              <div className="text-xs text-gray-400">Normal</div>
            </div>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>Avg Risk Score</span>
              <span>{(avgScore * 100).toFixed(0)}%</span>
            </div>
            <Progress value={avgScore * 100} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Selected Officer Detail */}
      {selectedOfficer && (
        <Card className="bg-blue-900 border-blue-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white flex items-center justify-between text-sm">
              <span className="flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                {selectedOfficer.unit}
              </span>
              <Badge variant={getSafetyBadgeVariant(selectedOfficer.safetyLevel) as any}>
                {selectedOfficer.safetyLevel || "unknown"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-gray-300 mb-1">
                  <span>Safety Score</span>
                  <span>{((selectedOfficer.safetyScore || 0) * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${getSafetyLevelColor(
                      selectedOfficer.safetyLevel
                    )}`}
                    style={{ width: `${(selectedOfficer.safetyScore || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-800 rounded p-2">
                  <div className="text-gray-400">Status</div>
                  <div className="font-medium capitalize">
                    {selectedOfficer.status.replace("_", " ")}
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-2">
                  <div className="text-gray-400">Speed</div>
                  <div className="font-medium">
                    {selectedOfficer.speed?.toFixed(0) || 0} mph
                  </div>
                </div>
              </div>

              <div className="text-xs text-gray-400">
                <div className="font-medium text-white mb-1">Risk Factors:</div>
                <ul className="list-disc list-inside space-y-1">
                  <li>Proximity to high-risk zone</li>
                  <li>Recent gunfire in area</li>
                  <li>Time-of-day patterns</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Officer Risk List */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-sm">Risk Rankings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {sortedOfficers.map((officer, index) => (
              <div
                key={officer.badge}
                className={`flex items-center justify-between p-2 rounded ${
                  selectedOfficer?.badge === officer.badge
                    ? "bg-blue-900"
                    : "bg-gray-700"
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-400 w-4">{index + 1}</span>
                  <div
                    className={`w-2 h-2 rounded-full ${getSafetyLevelColor(
                      officer.safetyLevel
                    )}`}
                  />
                  <span className="text-sm font-medium">{officer.unit}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-400">
                    {((officer.safetyScore || 0) * 100).toFixed(0)}%
                  </span>
                  {(officer.safetyScore || 0) > 0.5 ? (
                    <TrendingUp className="h-3 w-3 text-red-400" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-green-400" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
