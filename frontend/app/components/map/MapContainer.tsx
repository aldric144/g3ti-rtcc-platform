'use client';

import { useEffect, useRef, useState } from 'react';
import { MapPin } from 'lucide-react';

interface MapContainerProps {
  onEventSelect?: (eventId: string) => void;
}

/**
 * Main map container component.
 *
 * Uses Mapbox GL JS for rendering the interactive map.
 * Falls back to placeholder if Mapbox token is not configured.
 */
export function MapContainer({ onEventSelect }: MapContainerProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

    if (!mapboxToken) {
      setError('Mapbox token not configured');
      return;
    }

    // Dynamic import of mapbox-gl to avoid SSR issues
    const initMap = async () => {
      try {
        const mapboxgl = (await import('mapbox-gl')).default;
        // @ts-ignore - CSS import for mapbox styles
        await import('mapbox-gl/dist/mapbox-gl.css');

        if (!mapContainer.current) return;

        mapboxgl.accessToken = mapboxToken;

        const map = new mapboxgl.Map({
          container: mapContainer.current,
          style: 'mapbox://styles/mapbox/dark-v11',
          center: [-95.7129, 37.0902], // US center
          zoom: 4,
        });

        map.on('load', () => {
          setMapLoaded(true);

          // Add navigation controls
          map.addControl(new mapboxgl.NavigationControl(), 'top-right');

          // Add sample markers (would be replaced with real data)
          const markers = [
            { lng: -95.3698, lat: 29.7604, type: 'gunshot' },
            { lng: -87.6298, lat: 41.8781, type: 'lpr' },
            { lng: -118.2437, lat: 34.0522, type: 'incident' },
          ];

          markers.forEach((marker) => {
            const el = document.createElement('div');
            el.className = 'map-marker';
            el.style.width = '20px';
            el.style.height = '20px';
            el.style.borderRadius = '50%';
            el.style.cursor = 'pointer';
            el.style.backgroundColor =
              marker.type === 'gunshot' ? '#dc2626' : marker.type === 'lpr' ? '#ea580c' : '#2563eb';

            new mapboxgl.Marker(el).setLngLat([marker.lng, marker.lat]).addTo(map);
          });
        });

        return () => map.remove();
      } catch (err) {
        setError('Failed to load map');
        console.error('Map initialization error:', err);
      }
    };

    initMap();
  }, []);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="text-center">
          <MapPin className="mx-auto h-12 w-12 text-gray-600" />
          <p className="mt-4 text-gray-400">{error}</p>
          <p className="mt-2 text-sm text-gray-500">
            Configure NEXT_PUBLIC_MAPBOX_TOKEN to enable the map
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={mapContainer} className="h-full w-full">
      {!mapLoaded && (
        <div className="flex h-full items-center justify-center bg-gray-900">
          <div className="text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-rtcc-accent border-t-transparent" />
            <p className="mt-4 text-gray-400">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
}
