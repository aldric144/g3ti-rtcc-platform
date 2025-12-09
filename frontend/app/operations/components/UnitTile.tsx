'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';

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

interface UnitTileProps {
  unit: Unit;
  onDragStart: () => void;
  onDragEnd: () => void;
  isDragging: boolean;
  compact?: boolean;
  showRemove?: boolean;
  onRemove?: () => void;
  onSetCommander?: () => void;
  isCommander?: boolean;
}

const statusColors = {
  available: 'bg-green-500',
  en_route: 'bg-yellow-500',
  on_scene: 'bg-red-500',
  busy: 'bg-gray-500',
};

const safetyColors = {
  green: 'border-green-500',
  yellow: 'border-yellow-500',
  orange: 'border-orange-500',
  red: 'border-red-500',
  black: 'border-gray-900',
};

const safetyBgColors = {
  green: 'bg-green-500/10',
  yellow: 'bg-yellow-500/10',
  orange: 'bg-orange-500/10',
  red: 'bg-red-500/10',
  black: 'bg-gray-900/50',
};

export function UnitTile({
  unit,
  onDragStart,
  onDragEnd,
  isDragging,
  compact = false,
  showRemove = false,
  onRemove,
  onSetCommander,
  isCommander = false,
}: UnitTileProps) {
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('text/plain', unit.id);
    onDragStart();
  };

  const handleDragEnd = () => {
    onDragEnd();
  };

  if (compact) {
    return (
      <div
        className={`
          flex items-center justify-between p-2 rounded-lg border-2 cursor-grab
          ${safetyColors[unit.safety_level]}
          ${safetyBgColors[unit.safety_level]}
          ${isDragging ? 'opacity-50' : ''}
          ${isCommander ? 'ring-2 ring-purple-500' : ''}
          transition-all hover:scale-102
        `}
        draggable
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${statusColors[unit.status]}`} />
          <span className="font-medium text-sm text-white">{unit.unit_id}</span>
          {isCommander && (
            <Badge variant="secondary" className="text-xs bg-purple-600">CMD</Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          {unit.safety_score !== null && (
            <span className="text-xs text-gray-400">{unit.safety_score}%</span>
          )}
          {showRemove && onRemove && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
              className="text-gray-400 hover:text-red-400 text-xs"
            >
              X
            </button>
          )}
          {onSetCommander && !isCommander && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSetCommander();
              }}
              className="text-gray-400 hover:text-purple-400 text-xs"
              title="Set as Commander"
            >
              CMD
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`
        p-3 rounded-lg border-2 cursor-grab
        ${safetyColors[unit.safety_level]}
        ${safetyBgColors[unit.safety_level]}
        ${isDragging ? 'opacity-50 scale-95' : ''}
        transition-all hover:scale-102 active:scale-95
      `}
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`w-3 h-3 rounded-full ${statusColors[unit.status]}`} />
          <span className="font-bold text-white">{unit.unit_id}</span>
        </div>
        {unit.safety_score !== null && (
          <Badge
            variant="outline"
            className={`
              ${unit.safety_score >= 80 ? 'border-green-500 text-green-400' : ''}
              ${unit.safety_score >= 60 && unit.safety_score < 80 ? 'border-yellow-500 text-yellow-400' : ''}
              ${unit.safety_score < 60 ? 'border-red-500 text-red-400' : ''}
            `}
          >
            {unit.safety_score}%
          </Badge>
        )}
      </div>

      {/* Officer Info */}
      <div className="space-y-1">
        {unit.officer_name && (
          <p className="text-sm text-gray-300">{unit.officer_name}</p>
        )}
        {unit.badge && (
          <p className="text-xs text-gray-500">Badge: {unit.badge}</p>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-700">
        <div className="flex items-center gap-2">
          {unit.shift && (
            <Badge variant="secondary" className="text-xs">
              Shift {unit.shift}
            </Badge>
          )}
          {unit.district && (
            <Badge variant="outline" className="text-xs">
              {unit.district}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1">
          {/* Safety level indicator */}
          <div
            className={`
              w-4 h-4 rounded-full flex items-center justify-center text-xs font-bold
              ${unit.safety_level === 'green' ? 'bg-green-500 text-white' : ''}
              ${unit.safety_level === 'yellow' ? 'bg-yellow-500 text-black' : ''}
              ${unit.safety_level === 'orange' ? 'bg-orange-500 text-white' : ''}
              ${unit.safety_level === 'red' ? 'bg-red-500 text-white' : ''}
              ${unit.safety_level === 'black' ? 'bg-gray-900 text-white border border-white' : ''}
            `}
            title={`Safety Level: ${unit.safety_level}`}
          >
            {unit.safety_level === 'black' ? '!' : ''}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UnitTile;
