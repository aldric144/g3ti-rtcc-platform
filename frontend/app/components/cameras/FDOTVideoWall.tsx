'use client';

import { useEffect, useState, useCallback } from 'react';
import { Camera, RefreshCw, Wifi, WifiOff, Maximize2, Grid, List } from 'lucide-react';

interface FDOTCamera {
  fdot_id: string;
  name: string;
  gps: {
    latitude: number;
    longitude: number;
  };
  snapshot_url: string;
  status: string;
  sector: string;
  last_updated: string;
  description?: string;
  source: string;
  type: string;
}

interface FDOTVideoWallProps {
  apiUrl?: string;
  refreshInterval?: number;
  columns?: number;
}

export function FDOTVideoWall({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev/api/v1',
  refreshInterval = 5000,
  columns = 3,
}: FDOTVideoWallProps) {
  const [cameras, setCameras] = useState<FDOTCamera[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const fetchCameras = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/cameras/fdot/list`);
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
        setDemoMode(data.demo_mode || false);
        setError(null);
      } else {
        throw new Error('Failed to fetch cameras');
      }
    } catch (err) {
      console.error('Failed to fetch FDOT cameras:', err);
      setError('Unable to load FDOT cameras. Using demo data.');
      // Load demo data from public folder
      try {
        const demoResponse = await fetch('/demo_data/public_cameras.json');
        if (demoResponse.ok) {
          const demoData = await demoResponse.json();
          const fdotCameras = demoData.cameras.filter(
            (cam: { source: string }) => cam.source === 'FDOT'
          );
          setCameras(fdotCameras);
          setDemoMode(true);
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
    
    // Set up periodic refresh
    const interval = setInterval(fetchCameras, refreshInterval);
    
    return () => clearInterval(interval);
  }, [fetchCameras, refreshInterval]);

  // WebSocket connection for real-time status updates
  useEffect(() => {
    const wsUrl = apiUrl.replace('http', 'ws').replace('/api/v1', '');
    let ws: WebSocket | null = null;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(`${wsUrl}/api/v1/cameras/fdot/status/ws`);
        
        ws.onopen = () => {
          console.log('[FDOT_WS] Connected');
          setWsConnected(true);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
              // Update camera statuses
              console.log('[FDOT_WS] Status update:', data.data);
            }
          } catch (err) {
            console.error('[FDOT_WS] Parse error:', err);
          }
        };
        
        ws.onclose = () => {
          console.log('[FDOT_WS] Disconnected');
          setWsConnected(false);
          // Attempt reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = (err) => {
          console.error('[FDOT_WS] Error:', err);
          setWsConnected(false);
        };
      } catch (err) {
        console.error('[FDOT_WS] Connection failed:', err);
        setWsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [apiUrl]);

  const getStreamUrl = (cameraId: string) => {
    return `${apiUrl}/cameras/fdot/${cameraId}/stream`;
  };

  const getSnapshotUrl = (cameraId: string) => {
    return `${apiUrl}/cameras/fdot/${cameraId}/snapshot?t=${Date.now()}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-800 rounded-lg">
        <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading FDOT cameras...</span>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Camera className="h-6 w-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">FDOT Traffic Cameras</h2>
          {demoMode && (
            <span className="px-2 py-1 bg-amber-900/50 text-amber-300 text-xs rounded">
              Demo Mode
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          {/* WebSocket Status */}
          <div className="flex items-center gap-1 text-sm">
            {wsConnected ? (
              <>
                <Wifi className="h-4 w-4 text-green-400" />
                <span className="text-green-400">Live</span>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4 text-gray-500" />
                <span className="text-gray-500">Offline</span>
              </>
            )}
          </div>
          
          {/* View Toggle */}
          <div className="flex bg-gray-800 rounded">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-l ${viewMode === 'grid' ? 'bg-blue-600' : ''}`}
            >
              <Grid className="h-4 w-4 text-white" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-r ${viewMode === 'list' ? 'bg-blue-600' : ''}`}
            >
              <List className="h-4 w-4 text-white" />
            </button>
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={fetchCameras}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded"
          >
            <RefreshCw className="h-4 w-4 text-white" />
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-amber-900/30 border border-amber-500/50 text-amber-200 px-4 py-2 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Camera Grid */}
      {cameras.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <Camera className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No FDOT cameras available</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${columns} gap-4`}>
          {cameras.map((camera) => (
            <div
              key={camera.fdot_id}
              className={`bg-gray-800 rounded-lg overflow-hidden ${
                selectedCamera === camera.fdot_id ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {/* Camera Feed */}
              <div className="relative aspect-video bg-black">
                {demoMode ? (
                  <img
                    src={camera.snapshot_url}
                    alt={camera.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <img
                    src={getSnapshotUrl(camera.fdot_id)}
                    alt={camera.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = camera.snapshot_url;
                    }}
                  />
                )}
                
                {/* Status Badge */}
                <div className="absolute top-2 left-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      camera.status === 'online'
                        ? 'bg-green-900/80 text-green-300'
                        : 'bg-red-900/80 text-red-300'
                    }`}
                  >
                    {camera.status}
                  </span>
                </div>
                
                {/* Expand Button */}
                <button
                  onClick={() => setSelectedCamera(
                    selectedCamera === camera.fdot_id ? null : camera.fdot_id
                  )}
                  className="absolute top-2 right-2 p-1 bg-black/50 hover:bg-black/70 rounded"
                >
                  <Maximize2 className="h-4 w-4 text-white" />
                </button>
              </div>
              
              {/* Camera Info */}
              <div className="p-3">
                <h3 className="font-medium text-white truncate">{camera.name}</h3>
                <div className="flex items-center justify-between mt-1 text-xs text-gray-400">
                  <span>{camera.sector}</span>
                  <span>{camera.source}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* List View */
        <div className="space-y-2">
          {cameras.map((camera) => (
            <div
              key={camera.fdot_id}
              className="flex items-center gap-4 bg-gray-800 rounded-lg p-3 hover:bg-gray-700/50"
            >
              <div className="w-32 h-20 bg-black rounded overflow-hidden flex-shrink-0">
                <img
                  src={demoMode ? camera.snapshot_url : getSnapshotUrl(camera.fdot_id)}
                  alt={camera.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = camera.snapshot_url;
                  }}
                />
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-white truncate">{camera.name}</h3>
                <p className="text-sm text-gray-400">{camera.description}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                  <span>{camera.sector}</span>
                  <span>
                    {camera.gps.latitude.toFixed(4)}, {camera.gps.longitude.toFixed(4)}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    camera.status === 'online'
                      ? 'bg-green-900/50 text-green-300'
                      : 'bg-red-900/50 text-red-300'
                  }`}
                >
                  {camera.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Camera Count */}
      <div className="mt-4 text-sm text-gray-500 text-center">
        Showing {cameras.length} FDOT traffic cameras
      </div>
    </div>
  );
}

export default FDOTVideoWall;
