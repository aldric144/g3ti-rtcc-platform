'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { 
  Camera, 
  RefreshCw, 
  Layers, 
  MapPin,
  Settings,
  X,
  ChevronDown
} from 'lucide-react';
import Link from 'next/link';
import { 
  MapThemeId, 
  getMapTheme, 
  getThemeOptions, 
  getMarkerColor,
  loadThemePreference,
  saveThemePreference,
  MAP_THEMES
} from '@/lib/map-themes';

interface CameraData {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  gps?: { latitude: number; longitude: number };
  stream_url: string;
  camera_type: string;
  type?: string;
  jurisdiction: string;
  sector: string;
  status: string;
  description?: string;
  marker_color?: string;
}

export default function CameraMapPage() {
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCamera, setSelectedCamera] = useState<CameraData | null>(null);
  const [themeId, setThemeId] = useState<MapThemeId>('tactical_dark');
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
  const theme = getMapTheme(themeId);

  // Load theme preference on mount
  useEffect(() => {
    const savedTheme = loadThemePreference();
    setThemeId(savedTheme);
  }, []);

  const fetchCameras = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/cameras/map`);
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
        setError(null);
      } else {
        throw new Error('Failed to fetch cameras');
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
      setError('Unable to load cameras. Using demo data.');
      // Load demo data
      try {
        const demoResponse = await fetch('/demo_data/public_cameras.json');
        if (demoResponse.ok) {
          const demoData = await demoResponse.json();
          setCameras(demoData.cameras || []);
        }
      } catch {
        setCameras([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  const handleThemeChange = (newThemeId: MapThemeId) => {
    setThemeId(newThemeId);
    saveThemePreference(newThemeId);
    setShowThemeSelector(false);
  };

  const getMarkerColorForCamera = (camera: CameraData) => {
    return getMarkerColor(
      theme,
      camera.camera_type || camera.type,
      camera.jurisdiction
    );
  };

  // Riviera Beach center coordinates
  const mapCenter = { lat: 26.7753, lng: -80.0580 };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen" style={{ backgroundColor: theme.uiColors.background }}>
        <RefreshCw className="h-8 w-8 animate-spin" style={{ color: theme.uiColors.primary }} />
        <span className="ml-3" style={{ color: theme.uiColors.text }}>Loading camera map...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: theme.uiColors.background, color: theme.uiColors.text }}>
      {/* Header */}
      <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between">
        <div className="flex items-center gap-3 px-4 py-2 rounded-lg" style={{ backgroundColor: theme.uiColors.surface }}>
          <MapPin className="h-6 w-6" style={{ color: theme.uiColors.primary }} />
          <h1 className="text-xl font-bold">Camera Map</h1>
          <span className="px-2 py-1 text-sm rounded" style={{ backgroundColor: theme.uiColors.background, color: theme.uiColors.textMuted }}>
            {cameras.length} cameras
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Theme Selector */}
          <div className="relative">
            <button
              onClick={() => setShowThemeSelector(!showThemeSelector)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg"
              style={{ backgroundColor: theme.uiColors.surface }}
            >
              <Layers className="h-5 w-5" style={{ color: theme.uiColors.primary }} />
              <span>{theme.name}</span>
              <ChevronDown className="h-4 w-4" />
            </button>

            {showThemeSelector && (
              <div className="absolute right-0 mt-2 w-64 rounded-lg shadow-lg overflow-hidden" style={{ backgroundColor: theme.uiColors.surface }}>
                {getThemeOptions().map((option) => (
                  <button
                    key={option.id}
                    onClick={() => handleThemeChange(option.id)}
                    className={`w-full px-4 py-3 text-left hover:opacity-80 ${themeId === option.id ? 'ring-2 ring-inset' : ''}`}
                    style={{ 
                      backgroundColor: themeId === option.id ? theme.uiColors.primary + '20' : 'transparent',
                      borderColor: theme.uiColors.primary
                    }}
                  >
                    <div className="font-medium">{option.name}</div>
                    <div className="text-sm" style={{ color: theme.uiColors.textMuted }}>{option.description}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <Link
            href="/cameras"
            className="flex items-center gap-2 px-4 py-2 rounded-lg"
            style={{ backgroundColor: theme.uiColors.surface }}
          >
            <Camera className="h-5 w-5" />
            Directory
          </Link>

          <button
            onClick={fetchCameras}
            className="p-2 rounded-lg"
            style={{ backgroundColor: theme.uiColors.surface }}
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {error && (
        <div className="absolute top-20 left-4 right-4 z-10 bg-amber-900/80 border border-amber-500/50 text-amber-200 px-4 py-2 rounded">
          {error}
        </div>
      )}

      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-screen relative">
        {mapboxToken ? (
          <iframe
            src={`https://api.mapbox.com/styles/v1/mapbox/${theme.mapboxStyle.split('/').pop()}?access_token=${mapboxToken}#14/${mapCenter.lat}/${mapCenter.lng}`}
            className="w-full h-full border-0"
            title="Camera Map"
          />
        ) : (
          /* Fallback map using Leaflet-style static display */
          <div className="w-full h-full flex items-center justify-center" style={{ backgroundColor: theme.uiColors.background }}>
            <div className="text-center">
              <MapPin className="h-16 w-16 mx-auto mb-4" style={{ color: theme.uiColors.primary }} />
              <h2 className="text-xl font-bold mb-2">Map View</h2>
              <p style={{ color: theme.uiColors.textMuted }}>
                Mapbox token required for interactive map.
              </p>
              <p className="mt-2" style={{ color: theme.uiColors.textMuted }}>
                Center: {mapCenter.lat.toFixed(4)}, {mapCenter.lng.toFixed(4)}
              </p>
            </div>
          </div>
        )}

        {/* Camera Markers Overlay (simplified) */}
        <div className="absolute inset-0 pointer-events-none">
          {cameras.slice(0, 20).map((camera, index) => {
            // Simple positioning based on lat/lng relative to center
            const offsetX = ((camera.longitude - mapCenter.lng) * 5000) + 50;
            const offsetY = ((mapCenter.lat - camera.latitude) * 5000) + 50;
            
            return (
              <div
                key={camera.id}
                className="absolute pointer-events-auto cursor-pointer transform -translate-x-1/2 -translate-y-1/2"
                style={{
                  left: `${Math.min(Math.max(offsetX, 5), 95)}%`,
                  top: `${Math.min(Math.max(offsetY, 10), 90)}%`,
                }}
                onClick={() => setSelectedCamera(camera)}
              >
                <div
                  className="w-4 h-4 rounded-full border-2 border-white shadow-lg"
                  style={{ backgroundColor: getMarkerColorForCamera(camera) }}
                  title={camera.name}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 p-4 rounded-lg" style={{ backgroundColor: theme.uiColors.surface }}>
        <h3 className="font-medium mb-2">Legend</h3>
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: theme.markerColors.rbpd }} />
            <span>RBPD Internal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: theme.markerColors.fdot }} />
            <span>FDOT Traffic</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: theme.markerColors.lpr }} />
            <span>LPR Camera</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: theme.markerColors.ptz }} />
            <span>PTZ Camera</span>
          </div>
        </div>
      </div>

      {/* Selected Camera Panel */}
      {selectedCamera && (
        <div className="absolute bottom-4 right-4 w-80 rounded-lg shadow-lg overflow-hidden" style={{ backgroundColor: theme.uiColors.surface }}>
          <div className="relative">
            <img
              src={selectedCamera.stream_url || 'https://via.placeholder.com/640x360?text=Camera'}
              alt={selectedCamera.name}
              className="w-full h-40 object-cover"
            />
            <button
              onClick={() => setSelectedCamera(null)}
              className="absolute top-2 right-2 p-1 rounded-full bg-black/50 hover:bg-black/70"
            >
              <X className="h-4 w-4 text-white" />
            </button>
          </div>
          <div className="p-4">
            <h3 className="font-bold text-lg">{selectedCamera.name}</h3>
            <p className="text-sm mt-1" style={{ color: theme.uiColors.textMuted }}>
              {selectedCamera.description}
            </p>
            <div className="flex items-center gap-4 mt-2 text-sm" style={{ color: theme.uiColors.textMuted }}>
              <span>{selectedCamera.jurisdiction}</span>
              <span>{selectedCamera.sector}</span>
              <span className={`px-2 py-0.5 rounded ${selectedCamera.status === 'online' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
                {selectedCamera.status}
              </span>
            </div>
            <Link
              href={`/cameras/${selectedCamera.id}`}
              className="block mt-3 text-center py-2 rounded-lg"
              style={{ backgroundColor: theme.uiColors.primary, color: '#fff' }}
            >
              View Camera
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
