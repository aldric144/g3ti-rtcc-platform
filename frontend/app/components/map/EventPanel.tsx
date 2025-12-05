'use client';

import { X, MapPin, Clock, User, ExternalLink } from 'lucide-react';

interface EventPanelProps {
  eventId: string;
  onClose: () => void;
}

/**
 * Event detail panel for map view.
 */
export function EventPanel({ eventId, onClose }: EventPanelProps) {
  // Placeholder event data - would fetch from API
  const event = {
    id: eventId,
    type: 'gunshot',
    title: 'Gunshot Detected',
    description: '3 rounds detected with 95% confidence',
    location: '1200 Main St, Houston, TX',
    coordinates: { lat: 29.7604, lng: -95.3698 },
    timestamp: new Date().toISOString(),
    source: 'ShotSpotter',
    acknowledged: false,
    acknowledgedBy: null,
  };

  return (
    <div className="rounded-lg bg-white shadow-lg dark:bg-gray-800">
      <div className="flex items-center justify-between border-b p-4 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-red-500 animate-pulse" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {event.title}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {event.description}
        </p>

        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <MapPin className="h-4 w-4" />
            <span>{event.location}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <Clock className="h-4 w-4" />
            <span>{new Date(event.timestamp).toLocaleString()}</span>
          </div>
        </div>

        <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">Source</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {event.source}
          </p>
        </div>

        <div className="flex gap-2">
          <button className="btn-primary flex-1">Acknowledge</button>
          <button className="btn-outline flex items-center gap-1">
            <ExternalLink className="h-4 w-4" />
            Details
          </button>
        </div>
      </div>
    </div>
  );
}
