"use client";

import { useState, useEffect } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  Radio,
  MapPin,
  Clock,
  X,
  Volume2,
  Phone,
} from "lucide-react";

interface Emergency {
  badge: string;
  type: string;
  message: string;
  timestamp: string;
  location?: { lat: number; lon: number };
  unit?: string;
  details?: {
    trigger_type?: string;
    last_known_speed?: number;
    last_communication?: string;
  };
}

interface OfficerDownBannerProps {
  emergencies: Emergency[];
  onClear: (badge: string) => void;
}

export default function OfficerDownBanner({
  emergencies,
  onClear,
}: OfficerDownBannerProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);

  // Play alert sound when new emergency arrives
  useEffect(() => {
    if (emergencies.length > 0 && audioEnabled) {
      // In production, this would play an actual alert sound
      console.log("ALERT: Officer emergency detected!");
    }
  }, [emergencies.length, audioEnabled]);

  const getEmergencyColor = (type: string) => {
    switch (type) {
      case "officer_down":
        return "bg-red-600 border-red-500";
      case "officer_sos":
        return "bg-orange-600 border-orange-500";
      default:
        return "bg-red-600 border-red-500";
    }
  };

  const getEmergencyIcon = (type: string) => {
    switch (type) {
      case "officer_down":
        return <AlertTriangle className="h-6 w-6 animate-pulse" />;
      case "officer_sos":
        return <Radio className="h-6 w-6 animate-pulse" />;
      default:
        return <AlertTriangle className="h-6 w-6 animate-pulse" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const getTimeSince = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor((diffMs % 60000) / 1000);

    if (diffMins > 0) {
      return `${diffMins}m ${diffSecs}s ago`;
    }
    return `${diffSecs}s ago`;
  };

  if (emergencies.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      {/* Main Alert Banner */}
      <div
        className={`${getEmergencyColor(emergencies[0].type)} border-b-4 px-4 py-3`}
      >
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {getEmergencyIcon(emergencies[0].type)}
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xl font-bold uppercase tracking-wide">
                    {emergencies[0].type === "officer_down"
                      ? "OFFICER DOWN"
                      : "OFFICER SOS"}
                  </span>
                  <Badge variant="outline" className="bg-white/20 text-white border-white/40">
                    {emergencies.length} Active
                  </Badge>
                </div>
                <div className="text-sm opacity-90">
                  {emergencies[0].message || `Emergency alert for badge ${emergencies[0].badge}`}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                className="bg-white/20 border-white/40 hover:bg-white/30"
                onClick={() => setAudioEnabled(!audioEnabled)}
              >
                <Volume2 className={`h-4 w-4 ${audioEnabled ? "" : "opacity-50"}`} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="bg-white/20 border-white/40 hover:bg-white/30"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? "Collapse" : "Expand"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="bg-gray-900 border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {emergencies.map((emergency, index) => (
                <div
                  key={`${emergency.badge}-${index}`}
                  className={`rounded-lg p-4 ${
                    emergency.type === "officer_down"
                      ? "bg-red-900/50 border border-red-700"
                      : "bg-orange-900/50 border border-orange-700"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      {getEmergencyIcon(emergency.type)}
                      <div>
                        <div className="font-bold text-lg">
                          {emergency.unit || `Badge ${emergency.badge}`}
                        </div>
                        <div className="text-sm opacity-80">
                          Badge: {emergency.badge}
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-white/70 hover:text-white hover:bg-white/10"
                      onClick={() => onClear(emergency.badge)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="mt-4 space-y-2">
                    {emergency.location && (
                      <div className="flex items-center space-x-2 text-sm">
                        <MapPin className="h-4 w-4 opacity-70" />
                        <span>
                          {emergency.location.lat.toFixed(4)},{" "}
                          {emergency.location.lon.toFixed(4)}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center space-x-2 text-sm">
                      <Clock className="h-4 w-4 opacity-70" />
                      <span>
                        {formatTimestamp(emergency.timestamp)} ({getTimeSince(emergency.timestamp)})
                      </span>
                    </div>
                    {emergency.details?.trigger_type && (
                      <div className="text-sm opacity-80">
                        Trigger: {emergency.details.trigger_type}
                      </div>
                    )}
                    {emergency.details?.last_known_speed !== undefined && (
                      <div className="text-sm opacity-80">
                        Last Speed: {emergency.details.last_known_speed} mph
                      </div>
                    )}
                  </div>

                  <div className="mt-4 flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 bg-white/10 border-white/30 hover:bg-white/20"
                    >
                      <MapPin className="h-4 w-4 mr-1" />
                      Locate
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 bg-white/10 border-white/30 hover:bg-white/20"
                    >
                      <Phone className="h-4 w-4 mr-1" />
                      Contact
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div className="mt-4 pt-4 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                All units notified via radio broadcast
              </div>
              <div className="flex space-x-2">
                <Button variant="destructive" size="sm">
                  <Radio className="h-4 w-4 mr-2" />
                  Broadcast All Units
                </Button>
                <Button variant="outline" size="sm">
                  <Phone className="h-4 w-4 mr-2" />
                  Dispatch Backup
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => emergencies.forEach((e) => onClear(e.badge))}
                >
                  Clear All
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pulsing Border Effect */}
      <div
        className={`h-1 ${
          emergencies[0].type === "officer_down" ? "bg-red-500" : "bg-orange-500"
        } animate-pulse`}
      />
    </div>
  );
}
