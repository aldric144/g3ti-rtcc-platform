'use client';

import { useState } from 'react';
import {
  TrendingUp,
  Car,
  Target,
  Users,
  Clock,
  MapPin,
  ChevronDown,
  ChevronUp,
  BarChart3,
} from 'lucide-react';

interface Pattern {
  id: string;
  type: string;
  description: string;
  frequency: number;
  strength: number;
  entities: string[];
  locations?: { lat: number; lng: number }[];
  time_range?: { start: string; end: string };
}

interface PatternResultsProps {
  patterns: Pattern[];
}

const patternTypeConfig: Record<string, { icon: typeof TrendingUp; color: string; label: string }> =
  {
    vehicle_trajectory: {
      icon: Car,
      color: 'text-green-600 dark:text-green-400',
      label: 'Vehicle Trajectory',
    },
    gunfire_recurrence: {
      icon: Target,
      color: 'text-red-600 dark:text-red-400',
      label: 'Gunfire Recurrence',
    },
    offender_pathway: {
      icon: Users,
      color: 'text-orange-600 dark:text-orange-400',
      label: 'Offender Pathway',
    },
    temporal: {
      icon: Clock,
      color: 'text-blue-600 dark:text-blue-400',
      label: 'Temporal Pattern',
    },
    geographic: {
      icon: MapPin,
      color: 'text-purple-600 dark:text-purple-400',
      label: 'Geographic Cluster',
    },
    crime_heat: {
      icon: BarChart3,
      color: 'text-yellow-600 dark:text-yellow-400',
      label: 'Crime Heat',
    },
  };

function StrengthBar({ strength }: { strength: number }) {
  const percentage = Math.min(100, Math.max(0, strength * 100));
  const getColor = () => {
    if (percentage >= 80) return 'bg-red-500';
    if (percentage >= 60) return 'bg-orange-500';
    if (percentage >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-2 rounded-full ${getColor()}`} style={{ width: `${percentage}%` }} />
      </div>
      <span className="text-xs text-gray-500 dark:text-gray-400">{percentage.toFixed(0)}%</span>
    </div>
  );
}

function PatternCard({ pattern }: { pattern: Pattern }) {
  const [expanded, setExpanded] = useState(false);
  const config = patternTypeConfig[pattern.type] || {
    icon: TrendingUp,
    color: 'text-gray-600 dark:text-gray-400',
    label: pattern.type,
  };
  const Icon = config.icon;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`rounded-lg bg-gray-100 p-2 dark:bg-gray-700 ${config.color}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {config.label}
              </span>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                {pattern.frequency}x frequency
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{pattern.description}</p>
            <div className="mt-2">
              <span className="mr-2 text-xs text-gray-500 dark:text-gray-400">Strength:</span>
              <StrengthBar strength={pattern.strength} />
            </div>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="rounded p-1 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          )}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 border-t border-gray-200 pt-4 dark:border-gray-700">
          {pattern.entities.length > 0 && (
            <div className="mb-3">
              <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                Related Entities
              </p>
              <div className="flex flex-wrap gap-1">
                {pattern.entities.map((entity, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                  >
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}

          {pattern.locations && pattern.locations.length > 0 && (
            <div className="mb-3">
              <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">
                Locations ({pattern.locations.length})
              </p>
              <div className="grid grid-cols-2 gap-2">
                {pattern.locations.slice(0, 4).map((loc, index) => (
                  <span key={index} className="text-xs text-gray-600 dark:text-gray-400">
                    {loc.lat.toFixed(4)}, {loc.lng.toFixed(4)}
                  </span>
                ))}
                {pattern.locations.length > 4 && (
                  <span className="text-xs text-gray-500">
                    +{pattern.locations.length - 4} more
                  </span>
                )}
              </div>
            </div>
          )}

          {pattern.time_range && (
            <div>
              <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">
                Time Range
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {new Date(pattern.time_range.start).toLocaleDateString()} -{' '}
                {new Date(pattern.time_range.end).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function PatternResults({ patterns }: PatternResultsProps) {
  const [filter, setFilter] = useState<string>('all');

  const patternTypes = ['all', ...new Set(patterns.map((p) => p.type))];

  const filteredPatterns = patterns.filter((pattern) => {
    if (filter === 'all') return true;
    return pattern.type === filter;
  });

  if (patterns.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <TrendingUp className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          No patterns detected in the current time window
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        {patternTypes.map((type) => {
          const config = patternTypeConfig[type];
          return (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                filter === type
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {type === 'all' ? 'All' : config?.label || type}
            </button>
          );
        })}
      </div>

      <div className="max-h-[400px] space-y-3 overflow-y-auto">
        {filteredPatterns.map((pattern) => (
          <PatternCard key={pattern.id} pattern={pattern} />
        ))}
      </div>

      {filteredPatterns.length === 0 && (
        <p className="py-4 text-center text-sm text-gray-500 dark:text-gray-400">
          No patterns match the selected filter
        </p>
      )}
    </div>
  );
}
