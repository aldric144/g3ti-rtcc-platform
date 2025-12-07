'use client';

import { useState } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Clock,
  MapPin,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Anomaly {
  id: string;
  type: string;
  severity: string;
  description: string;
  detected_at: string;
  entities: string[];
  confidence: number;
  location?: { lat: number; lng: number };
}

interface AnomalyFeedProps {
  anomalies: Anomaly[];
}

const severityConfig: Record<
  string,
  { icon: typeof AlertTriangle; color: string; bgColor: string }
> = {
  critical: {
    icon: AlertTriangle,
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
  },
  high: {
    icon: AlertTriangle,
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
  },
  medium: {
    icon: AlertCircle,
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
  },
  low: {
    icon: Info,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
  },
};

const anomalyTypeLabels: Record<string, string> = {
  vehicle_behavior: 'Vehicle Behavior',
  gunfire_density: 'Gunfire Density',
  offender_clustering: 'Offender Clustering',
  timeline_deviation: 'Timeline Deviation',
  crime_signature_shift: 'Crime Signature Shift',
  repeat_caller: 'Repeat Caller',
};

function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  const [expanded, setExpanded] = useState(false);
  const config = severityConfig[anomaly.severity.toLowerCase()] || severityConfig.low;
  const Icon = config.icon;

  return (
    <div className={`rounded-lg p-3 ${config.bgColor}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <Icon className={`mt-0.5 h-5 w-5 ${config.color}`} />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${config.color}`}>
                {anomalyTypeLabels[anomaly.type] || anomaly.type}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {(anomaly.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{anomaly.description}</p>
            <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatDistanceToNow(new Date(anomaly.detected_at), { addSuffix: true })}
              </span>
              {anomaly.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {anomaly.location.lat.toFixed(4)}, {anomaly.location.lng.toFixed(4)}
                </span>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="rounded p-1 hover:bg-white/50 dark:hover:bg-black/20"
        >
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          )}
        </button>
      </div>

      {expanded && anomaly.entities.length > 0 && (
        <div className="mt-3 border-t border-gray-200 pt-3 dark:border-gray-700">
          <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">
            Related Entities
          </p>
          <div className="flex flex-wrap gap-1">
            {anomaly.entities.map((entity, index) => (
              <span
                key={index}
                className="inline-flex items-center rounded-full bg-white px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              >
                {entity}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function AnomalyFeed({ anomalies }: AnomalyFeedProps) {
  const [filter, setFilter] = useState<string>('all');

  const filteredAnomalies = anomalies.filter((anomaly) => {
    if (filter === 'all') return true;
    return anomaly.severity.toLowerCase() === filter;
  });

  if (anomalies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <AlertCircle className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          No anomalies detected in the current time window
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        {['all', 'critical', 'high', 'medium', 'low'].map((severity) => (
          <button
            key={severity}
            onClick={() => setFilter(severity)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filter === severity
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </button>
        ))}
      </div>

      <div className="max-h-[400px] space-y-3 overflow-y-auto">
        {filteredAnomalies.map((anomaly) => (
          <AnomalyCard key={anomaly.id} anomaly={anomaly} />
        ))}
      </div>

      {filteredAnomalies.length === 0 && (
        <p className="py-4 text-center text-sm text-gray-500 dark:text-gray-400">
          No anomalies match the selected filter
        </p>
      )}
    </div>
  );
}
