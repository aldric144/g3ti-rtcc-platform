'use client';

/**
 * G3TI RTCC-UIP MDT Action Buttons Component
 * Quick action buttons for common MDT operations
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Navigation,
  MapPin,
  Car,
  CheckCircle,
  AlertTriangle,
  Phone,
  Radio,
  FileText,
  Users,
  Shield,
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

interface MDTActionButtonsProps {
  currentStatus: UnitStatus;
  hasActiveCall: boolean;
  onStatusChange: (status: UnitStatus) => void;
  onRequestBackup: () => void;
  onEmergency: () => void;
}

export function MDTActionButtons({
  currentStatus,
  hasActiveCall,
  onStatusChange,
  onRequestBackup,
  onEmergency,
}: MDTActionButtonsProps) {
  const quickActions = [
    {
      label: 'Responding',
      icon: <Navigation className="h-6 w-6" />,
      status: 'en_route' as UnitStatus,
      color: 'bg-blue-600 hover:bg-blue-700',
      disabled: !hasActiveCall,
    },
    {
      label: 'Arrived',
      icon: <MapPin className="h-6 w-6" />,
      status: 'on_scene' as UnitStatus,
      color: 'bg-yellow-600 hover:bg-yellow-700',
      disabled: currentStatus !== 'en_route',
    },
    {
      label: 'Transporting',
      icon: <Car className="h-6 w-6" />,
      status: 'transporting' as UnitStatus,
      color: 'bg-purple-600 hover:bg-purple-700',
      disabled: currentStatus !== 'on_scene',
    },
    {
      label: 'Clear',
      icon: <CheckCircle className="h-6 w-6" />,
      status: 'available' as UnitStatus,
      color: 'bg-green-600 hover:bg-green-700',
      disabled: currentStatus === 'available',
    },
  ];

  return (
    <Card className="bg-gray-900 border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-lg">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Primary Status Actions */}
        <div className="grid grid-cols-2 gap-3">
          {quickActions.map((action) => (
            <Button
              key={action.status}
              className={`${action.color} text-white h-20 flex flex-col items-center justify-center ${
                currentStatus === action.status ? 'ring-2 ring-white' : ''
              }`}
              disabled={action.disabled}
              onClick={() => onStatusChange(action.status)}
            >
              {action.icon}
              <span className="mt-1 text-sm font-medium">{action.label}</span>
            </Button>
          ))}
        </div>

        {/* Secondary Actions */}
        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 h-14 flex flex-col items-center justify-center"
            onClick={() => onStatusChange('reports')}
          >
            <FileText className="h-5 w-5" />
            <span className="text-xs mt-1">Reports</span>
          </Button>
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 h-14 flex flex-col items-center justify-center"
            onClick={onRequestBackup}
          >
            <Users className="h-5 w-5" />
            <span className="text-xs mt-1">Backup</span>
          </Button>
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 h-14 flex flex-col items-center justify-center"
          >
            <Radio className="h-5 w-5" />
            <span className="text-xs mt-1">Radio</span>
          </Button>
        </div>

        {/* Emergency Button */}
        <Button
          className="w-full h-16 bg-red-600 hover:bg-red-700 text-white font-bold text-lg"
          onClick={onEmergency}
        >
          <AlertTriangle className="h-6 w-6 mr-2" />
          EMERGENCY
        </Button>

        {/* Additional Quick Actions */}
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700"
          >
            <Phone className="h-4 w-4 mr-2" />
            Call Dispatch
          </Button>
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700"
          >
            <Shield className="h-4 w-4 mr-2" />
            Safety Check
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
