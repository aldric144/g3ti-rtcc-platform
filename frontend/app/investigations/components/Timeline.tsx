'use client';

import { useState, useEffect } from 'react';
import { Clock, MapPin, FileText, Car, AlertTriangle, Camera, Radio, User, Loader2 } from 'lucide-react';

interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  source: string;
  location?: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  entity_id?: string;
  reliability_score?: number;
  metadata?: Record<string, any>;
}

interface TimelineProps {
  caseId?: string;
  events?: TimelineEvent[];
  onEventClick?: (event: TimelineEvent) => void;
}

/**
 * Timeline component for visualizing case events.
 * 
 * Displays events from multiple sources:
 * - CAD events
 * - RMS reports
 * - LPR timestamps
 * - Gunfire alerts
 * - BWC encounters
 * - Vehicle movements
 * - Entity interactions
 */
export function Timeline({ caseId, events: initialEvents, onEventClick }: TimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>(initialEvents || []);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    if (caseId && !initialEvents) {
      loadTimeline();
    }
  }, [caseId]);

  useEffect(() => {
    if (initialEvents) {
      setEvents(initialEvents);
    }
  }, [initialEvents]);

  const loadTimeline = async () => {
    if (!caseId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/investigations/case/${caseId}/timeline`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load timeline');
      }

      const timelineData = await response.json();
      setEvents(timelineData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline');
    } finally {
      setIsLoading(false);
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType.toLowerCase()) {
      case 'cad':
      case 'call':
        return <Radio className="h-4 w-4" />;
      case 'rms':
      case 'report':
        return <FileText className="h-4 w-4" />;
      case 'lpr':
      case 'vehicle':
        return <Car className="h-4 w-4" />;
      case 'shotspotter':
      case 'gunfire':
        return <AlertTriangle className="h-4 w-4" />;
      case 'bwc':
      case 'camera':
        return <Camera className="h-4 w-4" />;
      case 'entity':
      case 'person':
        return <User className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getEventColor = (source: string) => {
    switch (source.toLowerCase()) {
      case 'cad':
        return 'bg-blue-500';
      case 'rms':
        return 'bg-green-500';
      case 'lpr':
        return 'bg-purple-500';
      case 'shotspotter':
        return 'bg-red-500';
      case 'bwc':
        return 'bg-orange-500';
      case 'ness':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const sources = ['all', ...new Set(events.map(e => e.source.toLowerCase()))];

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.source.toLowerCase() === filter);

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading timeline...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button onClick={loadTimeline} className="mt-4 btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Case Timeline
        </h3>
        
        {/* Source filter */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        >
          {sources.map(source => (
            <option key={source} value={source}>
              {source === 'all' ? 'All Sources' : source.toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      {filteredEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No timeline events available
        </div>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

          {/* Events */}
          <div className="space-y-4">
            {filteredEvents.map((event, index) => {
              const { date, time } = formatTimestamp(event.timestamp);
              
              return (
                <div
                  key={index}
                  className="relative pl-10 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg p-2 -ml-2 transition-colors"
                  onClick={() => onEventClick?.(event)}
                >
                  {/* Event dot */}
                  <div className={`absolute left-2 top-3 w-5 h-5 rounded-full ${getEventColor(event.source)} flex items-center justify-center text-white`}>
                    {getEventIcon(event.event_type)}
                  </div>

                  {/* Event content */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                          {date} {time}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium text-white ${getEventColor(event.source)}`}>
                          {event.source}
                        </span>
                        {event.reliability_score !== undefined && (
                          <span className="text-xs text-gray-400">
                            {(event.reliability_score * 100).toFixed(0)}% reliable
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-900 dark:text-white mt-1">
                        {event.description}
                      </p>
                      {event.location?.address && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {event.location.address}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Sources:</p>
        <div className="flex flex-wrap gap-2">
          {['CAD', 'RMS', 'LPR', 'ShotSpotter', 'BWC', 'NESS'].map(source => (
            <span
              key={source}
              className={`px-2 py-1 rounded text-xs font-medium text-white ${getEventColor(source)}`}
            >
              {source}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Timeline;
