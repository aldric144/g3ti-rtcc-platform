'use client';

import { useEffect, useRef, useState } from 'react';
import { MapPin, Maximize2 } from 'lucide-react';
import Link from 'next/link';

/**
 * Mini map component for dashboard.
 * Shows a preview of the full map with recent events.
 * Uses Mapbox GL JS for rendering - centered on Riviera Beach, FL.
 */
export function MiniMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

    if (!mapboxToken) {
      setError('Mapbox token not configured');
      return;
    }

    const initMap = async () => {
      try {
        const mapboxgl = (await import('mapbox-gl')).default;
        // CSS is imported in globals.css

        if (!mapContainer.current) return;

        mapboxgl.accessToken = mapboxToken;

        const map = new mapboxgl.Map({
          container: mapContainer.current,
          style: 'mapbox://styles/mapbox/dark-v11',
          center: [-80.0581, 26.7753], // Riviera Beach, FL
          zoom: 12,
          interactive: true,
        });

        map.on('load', () => {
          setMapLoaded(true);

          // Add sample markers for Riviera Beach area
          const markers = [
            { lng: -80.0581, lat: 26.7753, type: 'incident', label: 'City Hall' },
            { lng: -80.0520, lat: 26.7800, type: 'gunshot', label: 'Alert Zone' },
            { lng: -80.0650, lat: 26.7700, type: 'lpr', label: 'LPR Hit' },
          ];

          markers.forEach((marker) => {
            const el = document.createElement('div');
            el.className = 'map-marker';
            el.style.width = '12px';
            el.style.height = '12px';
            el.style.borderRadius = '50%';
            el.style.cursor = 'pointer';
            el.style.border = '2px solid white';
            el.style.backgroundColor =
              marker.type === 'gunshot' ? '#dc2626' : marker.type === 'lpr' ? '#ea580c' : '#2563eb';

            new mapboxgl.Marker(el).setLngLat([marker.lng, marker.lat]).addTo(map);
          });
        });

        return () => map.remove();
      } catch (err) {
        setError('Failed to load map');
        console.error('MiniMap initialization error:', err);
      }
    };

    initMap();
  }, []);

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

      {/* Map container */}
      <div className="relative h-48 overflow-hidden rounded-lg bg-gray-200 dark:bg-gray-700">
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="mx-auto mb-2 h-8 w-8 text-gray-400" />
              <p className="text-sm text-gray-500 dark:text-gray-400">{error}</p>
            </div>
          </div>
        ) : (
          <>
            <div ref={mapContainer} className="h-full w-full" />
            {!mapLoaded && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-700">
                <div className="text-center">
                  <div className="mx-auto h-6 w-6 animate-spin rounded-full border-2 border-rtcc-accent border-t-transparent" />
                  <p className="mt-2 text-xs text-gray-400">Loading map...</p>
                </div>
              </div>
            )}
          </>
        )}
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
