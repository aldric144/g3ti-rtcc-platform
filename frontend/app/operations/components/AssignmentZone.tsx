'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { UnitTile } from './UnitTile';

interface Unit {
  id: string;
  unit_id: string;
  badge: string | null;
  officer_name: string | null;
  status: 'available' | 'en_route' | 'on_scene' | 'busy';
  safety_level: 'green' | 'yellow' | 'orange' | 'red' | 'black';
  safety_score: number | null;
  role: string | null;
  shift: string | null;
  district: string | null;
}

interface TacticalRole {
  id: string;
  name: string;
  description: string;
  color: string;
}

interface AssignmentZoneProps {
  role: TacticalRole;
  units: Unit[];
  onDrop: () => void;
  onRemoveUnit: (unitId: string) => void;
  onSetCommander: (unitId: string) => void;
  isDropTarget: boolean;
  isCommander: boolean;
}

export function AssignmentZone({
  role,
  units,
  onDrop,
  onRemoveUnit,
  onSetCommander,
  isDropTarget,
  isCommander,
}: AssignmentZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    onDrop();
  };

  return (
    <Card
      className={`
        bg-gray-800 border-2 transition-all
        ${isDragOver && isDropTarget ? 'border-blue-500 bg-blue-500/10' : 'border-gray-700'}
        ${isCommander ? 'ring-2 ring-purple-500' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${role.color}`} />
            <span>{role.name}</span>
          </div>
          <Badge variant="secondary" className="text-xs">
            {units.length}
          </Badge>
        </CardTitle>
        <p className="text-xs text-gray-500">{role.description}</p>
      </CardHeader>
      <CardContent className="min-h-24">
        {units.length > 0 ? (
          <div className="space-y-2">
            {units.map(unit => (
              <UnitTile
                key={unit.id}
                unit={unit}
                onDragStart={() => {}}
                onDragEnd={() => {}}
                isDragging={false}
                compact
                showRemove
                onRemove={() => onRemoveUnit(unit.id)}
                onSetCommander={() => onSetCommander(unit.id)}
                isCommander={isCommander && units.some(u => u.id === unit.id)}
              />
            ))}
          </div>
        ) : (
          <div
            className={`
              h-20 border-2 border-dashed rounded-lg flex items-center justify-center
              ${isDragOver && isDropTarget ? 'border-blue-500 bg-blue-500/5' : 'border-gray-600'}
              transition-colors
            `}
          >
            <p className="text-gray-500 text-sm">
              {isDropTarget ? 'Drop unit here' : 'No units assigned'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default AssignmentZone;
