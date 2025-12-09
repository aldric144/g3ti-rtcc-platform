"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  FileText,
  MapPin,
  User,
  Car,
  AlertTriangle,
  History,
  Search,
  Download,
  Shield,
} from "lucide-react";

interface Officer {
  badge: string;
  unit: string;
  lat: number;
  lon: number;
  status: string;
}

interface SceneIntel {
  packet_id: string;
  location: { lat: number; lon: number; address: string };
  generated_at: string;
  risk_level: string;
  history: any[];
  known_associates: any[];
  prior_violence: boolean;
  weapons_associated: any[];
  vehicles_of_interest: any[];
  nearby_offenders: any[];
  recommendations: string[];
  summary: string;
}

interface SceneIntelPanelProps {
  selectedOfficer: Officer | null;
}

export default function SceneIntelPanel({ selectedOfficer }: SceneIntelPanelProps) {
  const [sceneIntel, setSceneIntel] = useState<SceneIntel | null>(null);
  const [loading, setLoading] = useState(false);
  const [addressSearch, setAddressSearch] = useState("");

  // Mock scene intel for development
  useEffect(() => {
    if (selectedOfficer) {
      const mockIntel: SceneIntel = {
        packet_id: `FP-${Date.now()}`,
        location: {
          lat: selectedOfficer.lat,
          lon: selectedOfficer.lon,
          address: "123 Main Street, Phoenix, AZ 85001",
        },
        generated_at: new Date().toISOString(),
        risk_level: "elevated",
        history: [
          {
            report_id: "RMS-12345",
            type: "Assault",
            date: "2024-11-15T10:30:00Z",
            summary: "Report filed for assault at location",
            source: "RMS",
          },
          {
            call_id: "CAD-567890",
            type: "Domestic",
            date: "2024-10-20T22:15:00Z",
            disposition: "Report Taken",
            source: "CAD",
          },
          {
            call_id: "CAD-456789",
            type: "Disturbance",
            date: "2024-09-05T18:45:00Z",
            disposition: "Cleared",
            source: "CAD",
          },
        ],
        known_associates: [
          {
            person_id: "P-12345",
            name: "John Doe",
            relationship: "Resident",
            risk_score: 0.75,
            prior_offenses: 3,
            active_warrants: true,
          },
          {
            person_id: "P-67890",
            name: "Jane Smith",
            relationship: "Frequent Visitor",
            risk_score: 0.45,
            prior_offenses: 1,
            active_warrants: false,
          },
        ],
        prior_violence: true,
        weapons_associated: [
          {
            weapon_id: "W-1234",
            type: "Handgun",
            caliber: "9mm",
            recovered: false,
            ballistic_match: true,
          },
        ],
        vehicles_of_interest: [
          {
            plate: "ABC123",
            vehicle_description: "Black Sedan",
            alert_type: "BOLO",
            last_seen: "2024-12-01T14:30:00Z",
            distance_m: 150,
          },
        ],
        nearby_offenders: [
          {
            offender_id: "OFF-12345",
            offense_type: "Violent Crime",
            distance_m: 200,
            risk_level: "high",
            supervision_status: "Probation",
          },
        ],
        recommendations: [
          "Request backup before approach",
          "History of violence at location - exercise extreme caution",
          "Weapons associated with location: Handgun",
          "1 individual(s) with active warrants may be present",
        ],
        summary:
          "Risk Level: ELEVATED | 3 prior calls/reports | PRIOR VIOLENCE | 1 weapon(s) associated | 2 known associate(s)",
      };
      setSceneIntel(mockIntel);
    }
  }, [selectedOfficer]);

  const fetchSceneIntel = async (address?: string) => {
    setLoading(true);
    try {
      const url = address
        ? `/api/officer/sceneintel?address=${encodeURIComponent(address)}`
        : selectedOfficer
        ? `/api/officer/sceneintel/location?lat=${selectedOfficer.lat}&lon=${selectedOfficer.lon}`
        : null;

      if (url) {
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          setSceneIntel(data);
        }
      }
    } catch (error) {
      console.error("Failed to fetch scene intel:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "elevated":
        return "bg-yellow-500";
      case "moderate":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const getRiskBadgeVariant = (level: string) => {
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

  if (!selectedOfficer && !sceneIntel) {
    return (
      <Card className="h-full bg-gray-800 border-gray-700">
        <CardContent className="flex flex-col items-center justify-center h-full">
          <FileText className="h-12 w-12 mb-4 text-gray-500" />
          <p className="text-gray-400 mb-4">
            Select an officer or search an address for scene intelligence
          </p>
          <div className="flex space-x-2 w-full max-w-md">
            <Input
              placeholder="Enter address..."
              value={addressSearch}
              onChange={(e) => setAddressSearch(e.target.value)}
              className="bg-gray-700 border-gray-600"
            />
            <Button onClick={() => fetchSceneIntel(addressSearch)} disabled={!addressSearch}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="h-full grid grid-cols-3 gap-4">
      {/* Main Intel Panel */}
      <div className="col-span-2 space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
        {/* Header Card */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                RTCC Field Packet
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Badge variant={getRiskBadgeVariant(sceneIntel?.risk_level || "") as any}>
                  {sceneIntel?.risk_level?.toUpperCase()}
                </Badge>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-1" />
                  Export
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center text-gray-400">
                <MapPin className="h-4 w-4 mr-1" />
                {sceneIntel?.location.address}
              </div>
              <div className="text-gray-500">|</div>
              <div className="text-gray-400">
                Packet ID: {sceneIntel?.packet_id}
              </div>
            </div>
            <div className="mt-3 p-3 bg-gray-700 rounded text-sm">
              {sceneIntel?.summary}
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        {sceneIntel?.recommendations && sceneIntel.recommendations.length > 0 && (
          <Card className="bg-red-900 border-red-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Tactical Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {sceneIntel.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm">
                    <Shield className="h-4 w-4 mt-0.5 text-red-400 flex-shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* History */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <History className="h-4 w-4 mr-2" />
              Location History ({sceneIntel?.history.length || 0} records)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sceneIntel?.history.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-700 rounded"
                >
                  <div className="flex items-center space-x-3">
                    <Badge variant="outline" className="text-xs">
                      {item.source}
                    </Badge>
                    <div>
                      <div className="font-medium text-sm">{item.type}</div>
                      <div className="text-xs text-gray-400">
                        {new Date(item.date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  {item.disposition && (
                    <span className="text-xs text-gray-400">{item.disposition}</span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Known Associates */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <User className="h-4 w-4 mr-2" />
              Known Associates ({sceneIntel?.known_associates.length || 0})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sceneIntel?.known_associates.map((associate, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-700 rounded"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        associate.risk_score > 0.6 ? "bg-red-600" : "bg-gray-600"
                      }`}
                    >
                      <User className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-medium text-sm">{associate.name}</div>
                      <div className="text-xs text-gray-400">
                        {associate.relationship} | {associate.prior_offenses} prior
                        offense(s)
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {associate.active_warrants && (
                      <Badge variant="destructive" className="text-xs">
                        WARRANT
                      </Badge>
                    )}
                    <span className="text-xs text-gray-400">
                      Risk: {(associate.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Side Panel */}
      <div className="space-y-4">
        {/* Address Search */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Search Address</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <Input
                placeholder="Enter address..."
                value={addressSearch}
                onChange={(e) => setAddressSearch(e.target.value)}
                className="bg-gray-700 border-gray-600"
              />
              <Button
                onClick={() => fetchSceneIntel(addressSearch)}
                disabled={loading || !addressSearch}
                size="sm"
              >
                <Search className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Weapons */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2 text-red-400" />
              Weapons Associated
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sceneIntel?.weapons_associated.length === 0 ? (
              <p className="text-gray-400 text-sm">No weapons associated</p>
            ) : (
              <div className="space-y-2">
                {sceneIntel?.weapons_associated.map((weapon, index) => (
                  <div key={index} className="p-2 bg-gray-700 rounded text-sm">
                    <div className="font-medium">{weapon.type}</div>
                    <div className="text-xs text-gray-400">
                      {weapon.caliber && `Caliber: ${weapon.caliber}`}
                      {weapon.ballistic_match && " | Ballistic Match"}
                    </div>
                    <Badge
                      variant={weapon.recovered ? "default" : "destructive"}
                      className="text-xs mt-1"
                    >
                      {weapon.recovered ? "Recovered" : "Not Recovered"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Vehicles of Interest */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <Car className="h-4 w-4 mr-2" />
              Vehicles of Interest
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sceneIntel?.vehicles_of_interest.length === 0 ? (
              <p className="text-gray-400 text-sm">No vehicles of interest</p>
            ) : (
              <div className="space-y-2">
                {sceneIntel?.vehicles_of_interest.map((vehicle, index) => (
                  <div key={index} className="p-2 bg-gray-700 rounded text-sm">
                    <div className="font-medium font-mono">{vehicle.plate}</div>
                    <div className="text-xs text-gray-400">
                      {vehicle.vehicle_description}
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <Badge variant="outline" className="text-xs">
                        {vehicle.alert_type}
                      </Badge>
                      <span className="text-xs text-gray-400">
                        {vehicle.distance_m}m away
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Nearby Offenders */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center">
              <User className="h-4 w-4 mr-2 text-orange-400" />
              Nearby Offenders
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sceneIntel?.nearby_offenders.length === 0 ? (
              <p className="text-gray-400 text-sm">No nearby offenders</p>
            ) : (
              <div className="space-y-2">
                {sceneIntel?.nearby_offenders.map((offender, index) => (
                  <div key={index} className="p-2 bg-gray-700 rounded text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{offender.offense_type}</span>
                      <Badge
                        variant={
                          offender.risk_level === "high" ? "destructive" : "secondary"
                        }
                        className="text-xs"
                      >
                        {offender.risk_level}
                      </Badge>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {offender.distance_m}m away | {offender.supervision_status}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
