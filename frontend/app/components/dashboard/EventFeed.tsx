'use client';

import { useState, useEffect } from 'react';
import {
  Target,
  Car,
  Video,
  AlertTriangle,
  Clock,
  MapPin,
  ChevronRight,
} from 'lucide-react';
import { clsx } from 'clsx';
import { formatRelativeTime } from '@/shared/utils';

interface Event {
  id: string;
  type: 'gunshot' | 'lpr' | 'camera' | 'incident';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  location: string;
  timestamp: string;
  acknowledged: boolean;
}

const eventIcons = {
  gunshot: Target,
  lpr: Car,
  camera: Video,
  incident: AlertTriangle,
};

const priorityColors = {
  critical: 'border-l-red-500 bg-red-50 dark:bg-red-900/20',
  high: 'border-l-orange-500 bg-orange-50 dark:bg-orange-900/20',
  medium: 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/20',
  low: 'border-l-blue-500 bg-blue-50 dark:bg-blue-900/20',
};

/**
 * Real-time event feed component.
 */
export function EventFeed() {
  const [events, setEvents] = useState<Event[]>([
    {
      id: '1',
      type: 'gunshot',
      priority: 'critical',
      title: 'Gunshot Detected',
      description: '3 rounds detected with high confidence',
      location: '1200 Main St',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      acknowledged: false,
    },
    {
      id: '2',
      type: 'lpr',
      priority: 'high',
      title: 'Stolen Vehicle Alert',
      description: 'Plate ABC-1234 matched stolen vehicle list',
      location: 'Oak Ave & 5th St',
      timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
      acknowledged: false,
    },
    {
      id: '3',
      type: 'camera',
      priority: 'medium',
      title: 'Motion Detected',
      description: 'Camera 47 - Warehouse District',
      location: '500 Industrial Blvd',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      acknowledged: true,
    },
    {
      id: '4',
      type: 'incident',
      priority: 'high',
      title: 'New Incident Created',
      description: 'Armed robbery reported at convenience store',
      location: '789 Commerce St',
      timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
      acknowledged: true,
    },
  ]);

  const [filter, setFilter] = useState<'all' | 'unacknowledged'>('all');

  const filteredEvents = events.filter((event) =>
    filter === 'all' ? true : !event.acknowledged
  );

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Live Event Feed
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={clsx(
              'rounded-lg px-3 py-1 text-sm',
              filter === 'all'
                ? 'bg-rtcc-primary text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
            )}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unacknowledged')}
            className={clsx(
              'rounded-lg px-3 py-1 text-sm',
              filter === 'unacknowledged'
                ? 'bg-rtcc-primary text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
            )}
          >
            Unacknowledged
          </button>
        </div>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {filteredEvents.map((event) => {
          const Icon = eventIcons[event.type];
          
          return (
            <div
              key={event.id}
              className={clsx(
                'rounded-lg border-l-4 p-4 transition-colors hover:opacity-90 cursor-pointer',
                priorityColors[event.priority]
              )}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  <Icon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {event.title}
                    </h3>
                    {!event.acknowledged && (
                      <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.description}
                  </p>
                  
                  <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {event.location}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatRelativeTime(new Date(event.timestamp))}
                    </span>
                  </div>
                </div>
                
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
