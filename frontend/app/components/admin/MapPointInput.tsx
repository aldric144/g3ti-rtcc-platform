'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapPointInputProps {
  value?: { lat: number; lng: number } | null;
  onChange: (point: { lat: number; lng: number } | null) => void;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  boundingBox?: {
    minLat: number;
    maxLat: number;
    minLng: number;
    maxLng: number;
  };
}

const RIVIERA_BEACH_BOUNDS = {
  minLat: 26.74,
  maxLat: 26.82,
  minLng: -80.10,
  maxLng: -80.03,
};

const RIVIERA_BEACH_CENTER: [number, number] = [-80.058, 26.775];

export default function MapPointInput({
  value,
  onChange,
  label = 'Location',
  required = false,
  disabled = false,
  boundingBox = RIVIERA_BEACH_BOUNDS,
}: MapPointInputProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const marker = useRef<mapboxgl.Marker | null>(null);
  const [error, setError] = useState<string | null>(null);

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
      center: value ? [value.lng, value.lat] : RIVIERA_BEACH_CENTER,
      zoom: 13,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    if (value) {
      marker.current = new mapboxgl.Marker({ color: '#0050ff', draggable: !disabled })
        .setLngLat([value.lng, value.lat])
        .addTo(map.current);

      if (!disabled) {
        marker.current.on('dragend', () => {
          const lngLat = marker.current?.getLngLat();
          if (lngLat) {
            handlePointChange(lngLat.lat, lngLat.lng);
          }
        });
      }
    }

    if (!disabled) {
      map.current.on('click', (e) => {
        handlePointChange(e.lngLat.lat, e.lngLat.lng);
      });
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  useEffect(() => {
    if (!map.current) return;

    if (value) {
      if (marker.current) {
        marker.current.setLngLat([value.lng, value.lat]);
      } else {
        marker.current = new mapboxgl.Marker({ color: '#0050ff', draggable: !disabled })
          .setLngLat([value.lng, value.lat])
          .addTo(map.current);

        if (!disabled) {
          marker.current.on('dragend', () => {
            const lngLat = marker.current?.getLngLat();
            if (lngLat) {
              handlePointChange(lngLat.lat, lngLat.lng);
            }
          });
        }
      }
    } else if (marker.current) {
      marker.current.remove();
      marker.current = null;
    }
  }, [value, disabled]);

  const handlePointChange = (lat: number, lng: number) => {
    if (boundingBox) {
      if (
        lat < boundingBox.minLat ||
        lat > boundingBox.maxLat ||
        lng < boundingBox.minLng ||
        lng > boundingBox.maxLng
      ) {
        setError('Point must be within Riviera Beach boundaries');
        return;
      }
    }
    setError(null);
    onChange({ lat, lng });
  };

  const handleClear = () => {
    onChange(null);
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
          className="w-full h-64 rounded-lg border border-gray-600"
          style={{ minHeight: '256px' }}
        />
        
        {error && (
          <div className="absolute bottom-2 left-2 right-2 bg-red-900/90 text-red-200 text-xs px-2 py-1 rounded">
            {error}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>
          {value
            ? `Lat: ${value.lat.toFixed(6)}, Lng: ${value.lng.toFixed(6)}`
            : 'Click on map to set location'}
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

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Latitude</label>
          <input
            type="number"
            step="0.000001"
            value={value?.lat ?? ''}
            onChange={(e) => {
              const lat = parseFloat(e.target.value);
              if (!isNaN(lat)) {
                handlePointChange(lat, value?.lng ?? RIVIERA_BEACH_CENTER[0]);
              }
            }}
            disabled={disabled}
            className="w-full px-2 py-1 text-sm bg-gray-800 border border-gray-600 rounded text-white disabled:opacity-50"
            placeholder="26.775"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Longitude</label>
          <input
            type="number"
            step="0.000001"
            value={value?.lng ?? ''}
            onChange={(e) => {
              const lng = parseFloat(e.target.value);
              if (!isNaN(lng)) {
                handlePointChange(value?.lat ?? RIVIERA_BEACH_CENTER[1], lng);
              }
            }}
            disabled={disabled}
            className="w-full px-2 py-1 text-sm bg-gray-800 border border-gray-600 rounded text-white disabled:opacity-50"
            placeholder="-80.058"
          />
        </div>
      </div>
    </div>
  );
}
