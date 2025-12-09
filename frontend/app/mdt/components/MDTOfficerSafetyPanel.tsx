'use client';

/**
 * G3TI RTCC-UIP MDT Officer Safety Panel Component
 * Displays officer safety status and threat indicators
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Shield,
  AlertTriangle,
  Flame,
  CheckCircle,
  Clock,
  MapPin,
} from 'lucide-react';

type ThreatLevel = 'critical' | 'high' | 'elevated' | 'moderate' | 'low' | 'minimal';

interface OfficerSafetyStatus {
  badge_number: string;
  officer_name: string;
  threat_level: ThreatLevel;
  threat_score: number;
  active_warnings: string[];
  nearby_threats: number;
  in_hotzone: boolean;
  hotzone_name?: string;
  last_check_in?: string;
}

interface ProximityWarning {
  id: string;
  warning_type: string;
  title: string;
  description: string;
  threat_level: ThreatLevel;
  distance_meters: number;
  acknowledged: boolean;
}

interface MDTOfficerSafetyPanelProps {
  safetyStatus: OfficerSafetyStatus | null;
  warnings: ProximityWarning[];
  onCheckIn: (type: string) => void;
  onAcknowledgeWarning: (warningId: string) => void;
}

const threatLevelConfig: Record<
  ThreatLevel,
  { label: string; color: string; bgColor: string }
> = {
  critical: { label: 'CRITICAL', color: 'text-red-400', bgColor: 'bg-red-600' },
  high: { label: 'HIGH', color: 'text-orange-400', bgColor: 'bg-orange-500' },
  elevated: { label: 'ELEVATED', color: 'text-yellow-400', bgColor: 'bg-yellow-500' },
  moderate: { label: 'MODERATE', color: 'text-amber-400', bgColor: 'bg-amber-500' },
  low: { label: 'LOW', color: 'text-green-400', bgColor: 'bg-green-500' },
  minimal: { label: 'MINIMAL', color: 'text-emerald-400', bgColor: 'bg-emerald-500' },
};

export function MDTOfficerSafetyPanel({
  safetyStatus,
  warnings,
  onCheckIn,
  onAcknowledgeWarning,
}: MDTOfficerSafetyPanelProps) {
  if (!safetyStatus) {
    return (
      <Card className="bg-gray-900 border-gray-700">
        <CardContent className="p-6 text-center text-gray-500">
          <Shield className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>Safety status unavailable</p>
        </CardContent>
      </Card>
    );
  }

  const config = threatLevelConfig[safetyStatus.threat_level];
  const activeWarnings = warnings.filter((w) => !w.acknowledged);

  return (
    <Card className="bg-gray-900 border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-white flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-400" />
          Officer Safety
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Threat Level Indicator */}
        <div className={`${config.bgColor} rounded-lg p-4`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-white" />
              <span className="text-white font-bold text-lg">{config.label}</span>
            </div>
            <span className="text-white/80 text-sm">
              {Math.round(safetyStatus.threat_score * 100)}%
            </span>
          </div>
          <Progress
            value={safetyStatus.threat_score * 100}
            className="h-2 bg-white/20"
          />
        </div>

        {/* Hotzone Warning */}
        {safetyStatus.in_hotzone && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-3 flex items-center gap-2">
            <Flame className="h-5 w-5 text-red-400" />
            <div>
              <span className="text-red-400 font-semibold">IN HOTZONE</span>
              {safetyStatus.hotzone_name && (
                <span className="text-red-300 text-sm ml-2">
                  {safetyStatus.hotzone_name}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Nearby Threats */}
        {safetyStatus.nearby_threats > 0 && (
          <div className="bg-orange-900/50 border border-orange-500 rounded-lg p-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-400" />
            <span className="text-orange-300">
              {safetyStatus.nearby_threats} nearby threat
              {safetyStatus.nearby_threats > 1 ? 's' : ''}
            </span>
          </div>
        )}

        {/* Active Warnings */}
        {activeWarnings.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-400">
              Active Warnings ({activeWarnings.length})
            </div>
            {activeWarnings.slice(0, 3).map((warning) => {
              const warnConfig = threatLevelConfig[warning.threat_level];
              return (
                <div
                  key={warning.id}
                  className="bg-gray-800 rounded-lg p-3 border-l-4"
                  style={{
                    borderLeftColor:
                      warning.threat_level === 'critical'
                        ? '#dc2626'
                        : warning.threat_level === 'high'
                        ? '#ea580c'
                        : '#ca8a04',
                  }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white font-medium text-sm">
                      {warning.title}
                    </span>
                    <Badge className={`${warnConfig.bgColor} text-white text-xs`}>
                      {Math.round(warning.distance_meters)}m
                    </Badge>
                  </div>
                  <p className="text-gray-400 text-xs mb-2">{warning.description}</p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full text-xs"
                    onClick={() => onAcknowledgeWarning(warning.id)}
                  >
                    Acknowledge
                  </Button>
                </div>
              );
            })}
          </div>
        )}

        {/* Check-In Buttons */}
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-400">Quick Check-In</div>
          <div className="grid grid-cols-2 gap-2">
            <Button
              className="bg-green-600 hover:bg-green-700 text-white"
              onClick={() => onCheckIn('safe')}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              I'm Safe
            </Button>
            <Button
              className="bg-blue-600 hover:bg-blue-700 text-white"
              onClick={() => onCheckIn('routine')}
            >
              <Clock className="h-4 w-4 mr-2" />
              Routine
            </Button>
          </div>
        </div>

        {/* Last Check-In */}
        {safetyStatus.last_check_in && (
          <div className="text-center text-gray-500 text-xs">
            Last check-in: {new Date(safetyStatus.last_check_in).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
