'use client';

import { MapPin, Maximize2 } from 'lucide-react';
import Link from 'next/link';

/**
 * Mini map component for dashboard.
 * Shows a preview of the full map with recent events.
 */
export function MiniMap() {
  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Activity Map</h2>
        <Link
          href="/map"
          className="flex items-center gap-1 text-sm text-rtcc-accent hover:underline"
        >
          <Maximize2 className="h-4 w-4" />
          Full Map
        </Link>
      </div>

      {/* Map placeholder */}
      <div className="relative h-48 overflow-hidden rounded-lg bg-gray-200 dark:bg-gray-700">
        {/* This would be replaced with actual Mapbox map */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="mx-auto mb-2 h-8 w-8 text-gray-400" />
            <p className="text-sm text-gray-500 dark:text-gray-400">Map requires Mapbox token</p>
          </div>
        </div>

        {/* Event markers placeholder */}
        <div className="absolute left-4 top-4">
          <div className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
        </div>
        <div className="absolute right-8 top-12">
          <div className="h-3 w-3 animate-pulse rounded-full bg-orange-500" />
        </div>
        <div className="absolute bottom-8 left-12">
          <div className="h-3 w-3 rounded-full bg-blue-500" />
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-red-500" />
          <span className="text-gray-600 dark:text-gray-400">Gunshots</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-orange-500" />
          <span className="text-gray-600 dark:text-gray-400">LPR Hits</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-blue-500" />
          <span className="text-gray-600 dark:text-gray-400">Incidents</span>
        </div>
      </div>
    </div>
  );
}
