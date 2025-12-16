'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';

interface PolygonPoint {
  lat: number;
  lng: number;
}

interface MapPolygonInputProps {
  value?: PolygonPoint[] | null;
  onChange: (polygon: PolygonPoint[] | null) => void;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  minPoints?: number;
}

const RIVIERA_BEACH_CENTER: [number, number] = [-80.058, 26.775];

export default function MapPolygonInput({
  value,
  onChange,
  label = 'Boundary',
  required = false,
  disabled = false,
  minPoints = 3,
}: MapPolygonInputProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const draw = useRef<MapboxDraw | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pointCount, setPointCount] = useState(value?.length ?? 0);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token) {
      setError('Mapbox token not configured');
      return;
    }

    mapboxgl.accessToken = token;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: RIVIERA_BEACH_CENTER,
      zoom: 13,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    if (!disabled) {
      draw.current = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
          polygon: true,
          trash: true,
        },
        defaultMode: 'simple_select',
        styles: [
          {
            id: 'gl-draw-polygon-fill',
            type: 'fill',
            filter: ['all', ['==', '$type', 'Polygon']],
            paint: {
              'fill-color': '#0050ff',
              'fill-opacity': 0.3,
            },
          },
          {
            id: 'gl-draw-polygon-stroke',
            type: 'line',
            filter: ['all', ['==', '$type', 'Polygon']],
            paint: {
              'line-color': '#0050ff',
              'line-width': 2,
            },
          },
          {
            id: 'gl-draw-point',
            type: 'circle',
            filter: ['all', ['==', '$type', 'Point']],
            paint: {
              'circle-radius': 6,
              'circle-color': '#0050ff',
            },
          },
        ],
      });

      map.current.addControl(draw.current, 'top-left');

      map.current.on('draw.create', updatePolygon);
      map.current.on('draw.update', updatePolygon);
      map.current.on('draw.delete', () => {
        onChange(null);
        setPointCount(0);
        setError(null);
      });
    }

    map.current.on('load', () => {
      if (value && value.length >= minPoints) {
        if (disabled) {
          const coordinates = value.map((p) => [p.lng, p.lat]);
          coordinates.push(coordinates[0]);

          map.current?.addSource('polygon', {
            type: 'geojson',
            data: {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'Polygon',
                coordinates: [coordinates],
              },
            },
          });

          map.current?.addLayer({
            id: 'polygon-fill',
            type: 'fill',
            source: 'polygon',
            paint: {
              'fill-color': '#0050ff',
              'fill-opacity': 0.3,
            },
          });

          map.current?.addLayer({
            id: 'polygon-stroke',
            type: 'line',
            source: 'polygon',
            paint: {
              'line-color': '#0050ff',
              'line-width': 2,
            },
          });
        } else if (draw.current) {
          const coordinates = value.map((p) => [p.lng, p.lat]);
          coordinates.push(coordinates[0]);

          draw.current.add({
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'Polygon',
              coordinates: [coordinates],
            },
          });
        }

        const bounds = new mapboxgl.LngLatBounds();
        value.forEach((p) => bounds.extend([p.lng, p.lat]));
        map.current?.fitBounds(bounds, { padding: 50 });
      }
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  const updatePolygon = () => {
    if (!draw.current) return;

    const data = draw.current.getAll();
    if (data.features.length === 0) {
      onChange(null);
      setPointCount(0);
      return;
    }

    const feature = data.features[0];
    if (feature.geometry.type !== 'Polygon') return;

    const coordinates = feature.geometry.coordinates[0];
    const points: PolygonPoint[] = coordinates.slice(0, -1).map((coord: number[]) => ({
      lat: coord[1],
      lng: coord[0],
    }));

    setPointCount(points.length);

    if (points.length < minPoints) {
      setError(`Polygon must have at least ${minPoints} points`);
      return;
    }

    if (hasSelfIntersection(points)) {
      setError('Polygon cannot have self-intersections');
      return;
    }

    setError(null);
    onChange(points);
  };

  const hasSelfIntersection = (points: PolygonPoint[]): boolean => {
    const n = points.length;
    if (n < 4) return false;

    for (let i = 0; i < n; i++) {
      for (let j = i + 2; j < n; j++) {
        if (i === 0 && j === n - 1) continue;

        const p1 = points[i];
        const p2 = points[(i + 1) % n];
        const p3 = points[j];
        const p4 = points[(j + 1) % n];

        if (linesIntersect(p1, p2, p3, p4)) {
          return true;
        }
      }
    }
    return false;
  };

  const linesIntersect = (
    p1: PolygonPoint,
    p2: PolygonPoint,
    p3: PolygonPoint,
    p4: PolygonPoint
  ): boolean => {
    const d1 = direction(p3, p4, p1);
    const d2 = direction(p3, p4, p2);
    const d3 = direction(p1, p2, p3);
    const d4 = direction(p1, p2, p4);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
      return true;
    }

    return false;
  };

  const direction = (p1: PolygonPoint, p2: PolygonPoint, p3: PolygonPoint): number => {
    return (p3.lng - p1.lng) * (p2.lat - p1.lat) - (p2.lng - p1.lng) * (p3.lat - p1.lat);
  };

  const handleClear = () => {
    if (draw.current) {
      draw.current.deleteAll();
    }
    onChange(null);
    setPointCount(0);
    setError(null);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>

      <div className="relative">
        <div
          ref={mapContainer}
          className="w-full h-80 rounded-lg border border-gray-600"
          style={{ minHeight: '320px' }}
        />

        {error && (
          <div className="absolute bottom-2 left-2 right-2 bg-red-900/90 text-red-200 text-xs px-2 py-1 rounded">
            {error}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>
          {pointCount > 0
            ? `${pointCount} points defined`
            : disabled
            ? 'No boundary defined'
            : 'Click polygon tool to draw boundary'}
        </span>
        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="text-red-400 hover:text-red-300"
          >
            Clear
          </button>
        )}
      </div>

      {!disabled && (
        <p className="text-xs text-gray-500">
          Use the polygon tool (top-left) to draw a boundary. Click to add points, double-click to finish.
        </p>
      )}
    </div>
  );
}
