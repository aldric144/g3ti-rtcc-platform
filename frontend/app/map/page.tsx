'use client';

import { useState } from 'react';
import { Layers, Filter, Maximize2, ZoomIn, ZoomOut } from 'lucide-react';
import { MapContainer } from '@/app/components/map/MapContainer';
import { MapControls } from '@/app/components/map/MapControls';
import { MapLegend } from '@/app/components/map/MapLegend';
import { EventPanel } from '@/app/components/map/EventPanel';

/**
 * Full-screen map page for geospatial intelligence.
 * 
 * Features:
 * - Interactive Mapbox map
 * - Real-time event markers
 * - Layer controls
 * - Event filtering
 * - Event detail panel
 */
export default function MapPage() {
  const [showLayers, setShowLayers] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);

  return (
    <div className="relative h-[calc(100vh-8rem)] rounded-lg overflow-hidden">
      {/* Map container */}
      <MapContainer
        onEventSelect={setSelectedEvent}
      />

      {/* Map controls overlay */}
      <div className="absolute top-4 left-4 z-10 space-y-2">
        <button
          onClick={() => setShowLayers(!showLayers)}
          className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 shadow-lg hover:bg-gray-50"
        >
          <Layers className="h-4 w-4" />
          <span className="text-sm font-medium">Layers</span>
        </button>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 shadow-lg hover:bg-gray-50"
        >
          <Filter className="h-4 w-4" />
          <span className="text-sm font-medium">Filters</span>
        </button>
      </div>

      {/* Zoom controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-1">
        <button className="rounded-lg bg-white p-2 shadow-lg hover:bg-gray-50">
          <ZoomIn className="h-4 w-4" />
        </button>
        <button className="rounded-lg bg-white p-2 shadow-lg hover:bg-gray-50">
          <ZoomOut className="h-4 w-4" />
        </button>
        <button className="rounded-lg bg-white p-2 shadow-lg hover:bg-gray-50">
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      {/* Layer controls panel */}
      {showLayers && (
        <div className="absolute top-16 left-4 z-10 w-64">
          <MapControls onClose={() => setShowLayers(false)} />
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10">
        <MapLegend />
      </div>

      {/* Event detail panel */}
      {selectedEvent && (
        <div className="absolute top-4 right-16 z-10 w-80">
          <EventPanel
            eventId={selectedEvent}
            onClose={() => setSelectedEvent(null)}
          />
        </div>
      )}
    </div>
  );
}
