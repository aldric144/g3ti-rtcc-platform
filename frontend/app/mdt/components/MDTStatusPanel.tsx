'use client';

/**
 * G3TI RTCC-UIP MDT Status Panel Component
 * Displays unit status and quick status change buttons
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle,
  Navigation,
  MapPin,
  Car,
  Building2,
  FileText,
  XCircle,
  Moon,
} from 'lucide-react';

type UnitStatus =
  | 'available'
  | 'en_route'
  | 'on_scene'
  | 'transporting'
  | 'at_hospital'
  | 'reports'
  | 'out_of_service'
  | 'off_duty';

interface MDTStatusPanelProps {
  currentStatus: UnitStatus;
  unitId: string;
  badgeNumber: string;
  officerName: string;
  onStatusChange: (status: UnitStatus) => void;
  lastUpdate?: string;
}

const statusConfig: Record<
  UnitStatus,
  { label: string; color: string; icon: React.ReactNode; bgColor: string }
> = {
  available: {
    label: 'Available',
    color: 'text-green-400',
    bgColor: 'bg-green-600',
    icon: <CheckCircle className="h-5 w-5" />,
  },
  en_route: {
    label: 'En Route',
    color: 'text-blue-400',
    bgColor: 'bg-blue-600',
    icon: <Navigation className="h-5 w-5" />,
  },
  on_scene: {
    label: 'On Scene',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-600',
    icon: <MapPin className="h-5 w-5" />,
  },
  transporting: {
    label: 'Transporting',
    color: 'text-purple-400',
    bgColor: 'bg-purple-600',
    icon: <Car className="h-5 w-5" />,
  },
  at_hospital: {
    label: 'At Hospital',
    color: 'text-pink-400',
    bgColor: 'bg-pink-600',
    icon: <Building2 className="h-5 w-5" />,
  },
  reports: {
    label: 'Reports',
    color: 'text-indigo-400',
    bgColor: 'bg-indigo-600',
    icon: <FileText className="h-5 w-5" />,
  },
  out_of_service: {
    label: 'Out of Service',
    color: 'text-red-400',
    bgColor: 'bg-red-600',
    icon: <XCircle className="h-5 w-5" />,
  },
  off_duty: {
    label: 'Off Duty',
    color: 'text-gray-400',
    bgColor: 'bg-gray-600',
    icon: <Moon className="h-5 w-5" />,
  },
};

export function MDTStatusPanel({
  currentStatus,
  unitId,
  badgeNumber,
  officerName,
  onStatusChange,
  lastUpdate,
}: MDTStatusPanelProps) {
  const config = statusConfig[currentStatus];

  const quickStatuses: UnitStatus[] = [
    'available',
    'en_route',
    'on_scene',
    'transporting',
    'reports',
  ];

  return (
    <Card className="bg-gray-900 border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-lg">Unit Status</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Current Status Display */}
        <div className={`${config.bgColor} rounded-lg p-4 mb-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-white">{config.icon}</div>
              <div>
                <div className="text-white font-bold text-xl">{config.label}</div>
                <div className="text-white/80 text-sm">Unit {unitId}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-white/80 text-sm">{officerName}</div>
              <div className="text-white/60 text-xs">Badge #{badgeNumber}</div>
            </div>
          </div>
        </div>

        {/* Quick Status Buttons */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          {quickStatuses.map((status) => {
            const statusCfg = statusConfig[status];
            const isActive = currentStatus === status;
            return (
              <Button
                key={status}
                variant={isActive ? 'default' : 'outline'}
                className={`flex flex-col items-center py-3 h-auto ${
                  isActive
                    ? statusCfg.bgColor
                    : 'bg-gray-800 border-gray-600 hover:bg-gray-700'
                }`}
                onClick={() => onStatusChange(status)}
              >
                <span className={isActive ? 'text-white' : statusCfg.color}>
                  {statusCfg.icon}
                </span>
                <span
                  className={`text-xs mt-1 ${isActive ? 'text-white' : 'text-gray-300'}`}
                >
                  {statusCfg.label}
                </span>
              </Button>
            );
          })}
        </div>

        {/* Additional Status Options */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className={`flex-1 ${
              currentStatus === 'out_of_service'
                ? 'bg-red-600 text-white'
                : 'bg-gray-800 border-gray-600 text-gray-300'
            }`}
            onClick={() => onStatusChange('out_of_service')}
          >
            Out of Service
          </Button>
          <Button
            variant="outline"
            size="sm"
            className={`flex-1 ${
              currentStatus === 'off_duty'
                ? 'bg-gray-600 text-white'
                : 'bg-gray-800 border-gray-600 text-gray-300'
            }`}
            onClick={() => onStatusChange('off_duty')}
          >
            Off Duty
          </Button>
        </div>

        {/* Last Update */}
        {lastUpdate && (
          <div className="text-center text-gray-500 text-xs mt-4">
            Last updated: {new Date(lastUpdate).toLocaleTimeString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
