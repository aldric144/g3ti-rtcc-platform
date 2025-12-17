'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

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
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [points, setPoints] = useState<PolygonPoint[]>(value || []);
  const [error, setError] = useState<string | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  const updatePolygonLayer = (pts: PolygonPoint[]) => {
    if (!map.current) return;
    const source = map.current.getSource('polygon-source') as mapboxgl.GeoJSONSource;
    if (!source) return;

    if (pts.length >= 2) {
      const coordinates = pts.map((p) => [p.lng, p.lat]);
      if (pts.length >= 3) coordinates.push(coordinates[0]);

      source.setData({
        type: 'Feature',
        properties: {},
        geometry: pts.length >= 3 ? { type: 'Polygon', coordinates: [coordinates] } : { type: 'LineString', coordinates },
      });
    } else {
      source.setData({ type: 'FeatureCollection', features: [] });
    }
  };

  const clearMarkers = () => {
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];
  };

  const addMarkerForPoint = (point: PolygonPoint, index: number) => {
    if (!map.current || disabled) return;
    const el = document.createElement('div');
    el.style.cssText = 'width: 12px; height: 12px; background: #0050ff; border: 2px solid white; border-radius: 50%; cursor: pointer;';

    const marker = new mapboxgl.Marker({ element: el, draggable: !disabled })
      .setLngLat([point.lng, point.lat])
      .addTo(map.current);

    marker.on('dragend', () => {
      const lngLat = marker.getLngLat();
      setPoints((prev) => {
        const newPts = [...prev];
        newPts[index] = { lat: lngLat.lat, lng: lngLat.lng };
        return newPts;
      });
    });

    markersRef.current.push(marker);
  };

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

    map.current.on('load', () => {
      map.current?.addSource('polygon-source', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
      map.current?.addLayer({ id: 'polygon-fill', type: 'fill', source: 'polygon-source', paint: { 'fill-color': '#0050ff', 'fill-opacity': 0.3 }, filter: ['==', '$type', 'Polygon'] });
      map.current?.addLayer({ id: 'polygon-line', type: 'line', source: 'polygon-source', paint: { 'line-color': '#0050ff', 'line-width': 2 } });

      if (value && value.length > 0) {
        setPoints(value);
        value.forEach((p, i) => addMarkerForPoint(p, i));
        updatePolygonLayer(value);
        const bounds = new mapboxgl.LngLatBounds();
        value.forEach((p) => bounds.extend([p.lng, p.lat]));
        map.current?.fitBounds(bounds, { padding: 50 });
      }
    });

    return () => {
      clearMarkers();
      map.current?.remove();
      map.current = null;
    };
  }, []);

  useEffect(() => {
    if (!map.current) return;

    const handleClick = (e: mapboxgl.MapMouseEvent) => {
      if (!isDrawing) return;
      const newPoint: PolygonPoint = { lat: e.lngLat.lat, lng: e.lngLat.lng };
      setPoints((prev) => {
        const newPts = [...prev, newPoint];
        addMarkerForPoint(newPoint, newPts.length - 1);
        return newPts;
      });
    };

    map.current.on('click', handleClick);
    return () => { map.current?.off('click', handleClick); };
  }, [isDrawing, disabled]);

  useEffect(() => {
    updatePolygonLayer(points);

    if (points.length >= minPoints) {
      if (hasSelfIntersection(points)) {
        setError('Polygon cannot have self-intersections');
        onChange(null);
      } else {
        setError(null);
        onChange(points);
      }
    } else if (points.length > 0) {
      setError(`Need at least ${minPoints} points (${points.length} added)`);
      onChange(null);
    } else {
      setError(null);
      onChange(null);
    }
  }, [points, minPoints]);

  const hasSelfIntersection = (pts: PolygonPoint[]): boolean => {
    const n = pts.length;
    if (n < 4) return false;
    for (let i = 0; i < n; i++) {
      for (let j = i + 2; j < n; j++) {
        if (i === 0 && j === n - 1) continue;
        if (linesIntersect(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n])) return true;
      }
    }
    return false;
  };

  const linesIntersect = (p1: PolygonPoint, p2: PolygonPoint, p3: PolygonPoint, p4: PolygonPoint): boolean => {
    const d1 = direction(p3, p4, p1), d2 = direction(p3, p4, p2), d3 = direction(p1, p2, p3), d4 = direction(p1, p2, p4);
    return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
  };

  const direction = (p1: PolygonPoint, p2: PolygonPoint, p3: PolygonPoint): number => {
    return (p3.lng - p1.lng) * (p2.lat - p1.lat) - (p2.lng - p1.lng) * (p3.lat - p1.lat);
  };

  const handleStartDrawing = () => { setIsDrawing(true); handleClear(); };
  const handleFinishDrawing = () => { setIsDrawing(false); };
  const handleClear = () => { clearMarkers(); setPoints([]); setError(null); };
  const handleUndo = () => {
    if (points.length > 0) {
      markersRef.current.pop()?.remove();
      setPoints((prev) => prev.slice(0, -1));
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>

      <div className="relative">
        <div ref={mapContainer} className={`w-full h-80 rounded-lg border ${isDrawing ? 'border-blue-500 cursor-crosshair' : 'border-gray-600'}`} style={{ minHeight: '320px' }} />
        {error && <div className="absolute bottom-2 left-2 right-2 bg-red-900/90 text-red-200 text-xs px-2 py-1 rounded">{error}</div>}
        {isDrawing && <div className="absolute top-2 left-2 bg-blue-900/90 text-blue-200 text-xs px-2 py-1 rounded">Click on map to add points</div>}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>{points.length > 0 ? `${points.length} points defined` : disabled ? 'No boundary defined' : 'Click "Draw" to start'}</span>
        {!disabled && (
          <div className="flex gap-2">
            {isDrawing ? (
              <>
                <button type="button" onClick={handleUndo} disabled={points.length === 0} className="text-yellow-400 hover:text-yellow-300 disabled:opacity-50">Undo</button>
                <button type="button" onClick={handleFinishDrawing} className="text-green-400 hover:text-green-300">Done</button>
              </>
            ) : (
              <>
                <button type="button" onClick={handleStartDrawing} className="text-blue-400 hover:text-blue-300">{points.length > 0 ? 'Redraw' : 'Draw'}</button>
                {points.length > 0 && <button type="button" onClick={handleClear} className="text-red-400 hover:text-red-300">Clear</button>}
              </>
            )}
          </div>
        )}
      </div>

      {!disabled && !isDrawing && <p className="text-xs text-gray-500">Click &quot;Draw&quot; to start, then click on the map to add polygon points. Drag markers to adjust.</p>}
    </div>
  );
}
