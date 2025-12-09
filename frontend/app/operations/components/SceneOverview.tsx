'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Scene {
  id: string;
  incident_id: string;
  incident_type: string;
  address: string;
  status: 'active' | 'contained' | 'clearing' | 'secured' | 'closed';
  threat_level: string;
  units: Array<{
    id: string;
    unit_id: string;
    role: string | null;
  }>;
  commander_unit_id: string | null;
}

interface SceneOverviewProps {
  scene: Scene;
}

const statusColors = {
  active: 'bg-red-500',
  contained: 'bg-orange-500',
  clearing: 'bg-yellow-500',
  secured: 'bg-green-500',
  closed: 'bg-gray-500',
};

const threatColors = {
  low: 'bg-green-500',
  medium: 'bg-yellow-500',
  high: 'bg-orange-500',
  critical: 'bg-red-500',
  unknown: 'bg-gray-500',
};

export function SceneOverview({ scene }: SceneOverviewProps) {
  const commander = scene.units.find(u => u.id === scene.commander_unit_id);

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white">Active Scene</CardTitle>
          <div className="flex items-center gap-2">
            <Badge className={statusColors[scene.status]}>
              {scene.status.toUpperCase()}
            </Badge>
            <Badge className={threatColors[scene.threat_level as keyof typeof threatColors] || threatColors.unknown}>
              Threat: {scene.threat_level.toUpperCase()}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {/* Left column */}
          <div className="space-y-2">
            <div>
              <p className="text-xs text-gray-500">Incident ID</p>
              <p className="text-sm text-white font-mono">{scene.incident_id}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Type</p>
              <p className="text-sm text-white">{scene.incident_type}</p>
            </div>
          </div>

          {/* Right column */}
          <div className="space-y-2">
            <div>
              <p className="text-xs text-gray-500">Location</p>
              <p className="text-sm text-white">{scene.address}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Commander</p>
              <p className="text-sm text-white">
                {commander ? commander.unit_id : 'Not assigned'}
              </p>
            </div>
          </div>
        </div>

        {/* Unit count summary */}
        <div className="mt-4 pt-3 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">Units on Scene</p>
            <Badge variant="outline" className="text-white">
              {scene.units.length} units
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default SceneOverview;
