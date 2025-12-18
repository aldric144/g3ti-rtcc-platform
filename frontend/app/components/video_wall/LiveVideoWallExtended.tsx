'use client';

import { useEffect, useState, useCallback, useRef } from 'react';

type CameraNetwork = 'marina' | 'pbc_traffic' | 'rtsp' | 'fdot_mjpeg' | 'all';

interface Camera {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  category: string;
  stream_type: string;
  health_status?: string;
}

interface LiveVideoWallExtendedProps {
  initialNetwork?: CameraNetwork;
  gridSize?: '2x2' | '3x3' | '4x4' | '5x5';
  refreshInterval?: number;
}

const NETWORK_CONFIG = {
  marina: {
    name: 'Marina & Singer Island',
    color: '#0984e3',
    icon: '⚓',
    apiBase: '/api/cameras/marina'
  },
  pbc_traffic: {
    name: 'PBC Traffic',
    color: '#fdcb6e',
    icon: '🚦',
    apiBase: '/api/cameras/pbc'
  },
  rtsp: {
    name: 'RBPD Internal',
    color: '#6c5ce7',
    icon: '🛡️',
    apiBase: '/api/cameras/rtsp'
  },
  fdot_mjpeg: {
    name: 'FDOT Live Motion',
    color: '#e17055',
    icon: '🛣️',
    apiBase: '/api/cameras/fdot/mjpeg'
  }
};

const GRID_CONFIGS = {
  '2x2': { cols: 2, rows: 2, maxCameras: 4 },
  '3x3': { cols: 3, rows: 3, maxCameras: 9 },
  '4x4': { cols: 4, rows: 4, maxCameras: 16 },
  '5x5': { cols: 5, rows: 5, maxCameras: 25 }
};

export default function LiveVideoWallExtended({
  initialNetwork = 'all',
  gridSize = '3x3',
  refreshInterval = 3
}: LiveVideoWallExtendedProps) {
  const [selectedNetwork, setSelectedNetwork] = useState<CameraNetwork>(initialNetwork);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCameras, setSelectedCameras] = useState<Camera[]>([]);
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentGridSize, setCurrentGridSize] = useState(gridSize);
  const [currentRefreshInterval, setCurrentRefreshInterval] = useState(refreshInterval);
  const containerRef = useRef<HTMLDivElement>(null);

  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';

  const fetchCameras = useCallback(async () => {
    try {
      setIsLoading(true);
      let allCameras: Camera[] = [];

      if (selectedNetwork === 'all') {
        // Fetch from all networks
        const networks = ['marina', 'pbc', 'rtsp'] as const;
        const promises = networks.map(async (network) => {
          try {
            const response = await fetch(`${backendUrl}/api/cameras/${network}/list`);
            if (response.ok) {
              const data = await response.json();
              return data.cameras || [];
            }
          } catch (e) {
            console.error(`Failed to fetch ${network} cameras:`, e);
          }
          return [];
        });

        // Also fetch FDOT MJPEG cameras
        promises.push(
          fetch(`${backendUrl}/api/cameras/fdot/mjpeg/list`)
            .then(r => r.ok ? r.json() : { cameras: [] })
            .then(d => d.cameras || [])
            .catch(() => [])
        );

        const results = await Promise.all(promises);
        allCameras = results.flat();
      } else {
        // Fetch from specific network
        const apiBase = selectedNetwork === 'fdot_mjpeg' 
          ? '/api/cameras/fdot/mjpeg'
          : `/api/cameras/${selectedNetwork === 'pbc_traffic' ? 'pbc' : selectedNetwork}`;
        
        const response = await fetch(`${backendUrl}${apiBase}/list`);
        if (response.ok) {
          const data = await response.json();
          allCameras = data.cameras || [];
        }
      }

      setCameras(allCameras);
      
      // Auto-select cameras for the grid
      const gridConfig = GRID_CONFIGS[currentGridSize];
      const camerasToSelect = allCameras.slice(0, gridConfig.maxCameras);
      setSelectedCameras(camerasToSelect);
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl, selectedNetwork, currentGridSize]);

  const loadSnapshot = useCallback(async (camera: Camera) => {
    try {
      const timestamp = Date.now();
      let snapshotUrl: string;

      // Determine the correct snapshot URL based on camera category
      if (camera.category === 'fdot_mjpeg_sim' || camera.id.startsWith('fdot-stream')) {
        snapshotUrl = `${backendUrl}/api/v1/fdot/snapshot/${camera.id}?t=${timestamp}`;
      } else if (camera.category === 'marina_live' || camera.category === 'singer_island') {
        snapshotUrl = `${backendUrl}/api/cameras/marina/${camera.id}/snapshot?t=${timestamp}`;
      } else if (camera.category === 'pbc_traffic') {
        snapshotUrl = `${backendUrl}/api/cameras/pbc/${camera.id}/snapshot?t=${timestamp}`;
      } else if (camera.category === 'rbpd_rtsp') {
        snapshotUrl = `${backendUrl}/api/cameras/rtsp/${camera.id}/snapshot?t=${timestamp}`;
      } else {
        // Default fallback
        snapshotUrl = `${backendUrl}/api/cameras/marina/${camera.id}/snapshot?t=${timestamp}`;
      }

      const response = await fetch(snapshotUrl);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrls(prev => {
          if (prev[camera.id]) URL.revokeObjectURL(prev[camera.id]);
          return { ...prev, [camera.id]: url };
        });
      }
    } catch (err) {
      console.error(`Failed to load snapshot for ${camera.id}:`, err);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  useEffect(() => {
    if (selectedCameras.length === 0) return;

    // Load initial snapshots
    selectedCameras.forEach(cam => loadSnapshot(cam));

    // Set up refresh interval
    const interval = setInterval(() => {
      selectedCameras.forEach(cam => loadSnapshot(cam));
    }, currentRefreshInterval * 1000);

    return () => {
      clearInterval(interval);
    };
  }, [selectedCameras, loadSnapshot, currentRefreshInterval]);

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      Object.values(imageUrls).forEach(url => URL.revokeObjectURL(url));
    };
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const addCameraToWall = (camera: Camera) => {
    const gridConfig = GRID_CONFIGS[currentGridSize];
    if (selectedCameras.length < gridConfig.maxCameras) {
      if (!selectedCameras.find(c => c.id === camera.id)) {
        setSelectedCameras([...selectedCameras, camera]);
      }
    }
  };

  const removeCameraFromWall = (cameraId: string) => {
    setSelectedCameras(selectedCameras.filter(c => c.id !== cameraId));
  };

  const gridConfig = GRID_CONFIGS[currentGridSize];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-400">Loading Video Wall...</span>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="min-h-screen bg-gray-900 p-4">
      {/* Header Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-white">Extended Video Wall</h1>
          
          {/* Network Filter */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedNetwork('all')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                selectedNetwork === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              All Networks
            </button>
            {Object.entries(NETWORK_CONFIG).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setSelectedNetwork(key as CameraNetwork)}
                className={`px-3 py-1 rounded text-sm transition-colors flex items-center gap-1 ${
                  selectedNetwork === key 
                    ? 'text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
                style={selectedNetwork === key ? { backgroundColor: config.color } : {}}
              >
                <span>{config.icon}</span>
                <span className="hidden md:inline">{config.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Grid Size Selector */}
          <select
            value={currentGridSize}
            onChange={(e) => setCurrentGridSize(e.target.value as typeof currentGridSize)}
            className="bg-gray-800 text-white rounded px-3 py-1 text-sm border border-gray-700"
          >
            <option value="2x2">2x2 Grid</option>
            <option value="3x3">3x3 Grid</option>
            <option value="4x4">4x4 Grid</option>
            <option value="5x5">5x5 Grid</option>
          </select>

          {/* Refresh Interval */}
          <select
            value={currentRefreshInterval}
            onChange={(e) => setCurrentRefreshInterval(Number(e.target.value))}
            className="bg-gray-800 text-white rounded px-3 py-1 text-sm border border-gray-700"
          >
            <option value={1}>1s refresh</option>
            <option value={2}>2s refresh</option>
            <option value={3}>3s refresh</option>
            <option value={5}>5s refresh</option>
            <option value={10}>10s refresh</option>
          </select>

          {/* Fullscreen Toggle */}
          <button
            onClick={toggleFullscreen}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm flex items-center gap-2"
          >
            {isFullscreen ? (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Exit
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
                Fullscreen
              </>
            )}
          </button>

          {/* Camera Count */}
          <span className="text-gray-400 text-sm">
            {selectedCameras.length}/{gridConfig.maxCameras} cameras
          </span>
        </div>
      </div>

      {/* Video Wall Grid */}
      <div 
        className="grid gap-2"
        style={{
          gridTemplateColumns: `repeat(${gridConfig.cols}, 1fr)`,
          gridTemplateRows: `repeat(${gridConfig.rows}, 1fr)`,
          height: isFullscreen ? 'calc(100vh - 80px)' : 'calc(100vh - 160px)'
        }}
      >
        {Array.from({ length: gridConfig.maxCameras }).map((_, index) => {
          const camera = selectedCameras[index];
          
          if (!camera) {
            return (
              <div
                key={`empty-${index}`}
                className="bg-gray-800 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-700"
              >
                <div className="text-center text-gray-500">
                  <svg className="w-8 h-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="text-sm">Add Camera</span>
                </div>
              </div>
            );
          }

          const networkConfig = Object.entries(NETWORK_CONFIG).find(
            ([_, config]) => camera.category?.includes(Object.keys(NETWORK_CONFIG).find(k => 
              camera.category?.toLowerCase().includes(k.replace('_', ''))
            ) || '')
          );

          return (
            <div
              key={camera.id}
              className="relative bg-gray-800 rounded-lg overflow-hidden group"
            >
              {imageUrls[camera.id] ? (
                <img
                  src={imageUrls[camera.id]}
                  alt={camera.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}

              {/* Camera Info Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="text-white text-xs font-medium truncate">{camera.name}</p>
                <p className="text-gray-300 text-xs truncate">{camera.location}</p>
              </div>

              {/* Status Badge */}
              <div className="absolute top-2 left-2 flex items-center gap-1">
                <span className={`w-2 h-2 rounded-full ${
                  camera.health_status === 'online' ? 'bg-green-500' : 'bg-red-500'
                } animate-pulse`} />
                <span className="text-white text-xs bg-black/50 px-1 rounded">LIVE</span>
              </div>

              {/* Remove Button */}
              <button
                onClick={() => removeCameraFromWall(camera.id)}
                className="absolute top-2 right-2 w-6 h-6 bg-red-500/80 hover:bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Network Badge */}
              {networkConfig && (
                <div 
                  className="absolute top-2 right-10 px-2 py-0.5 rounded text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ backgroundColor: networkConfig[1].color }}
                >
                  {networkConfig[1].icon}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Available Cameras Panel */}
      {!isFullscreen && (
        <div className="mt-4 bg-gray-800 rounded-lg p-4">
          <h3 className="text-white font-medium mb-3">Available Cameras ({cameras.length})</h3>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {cameras.filter(c => !selectedCameras.find(sc => sc.id === c.id)).map(camera => (
              <button
                key={camera.id}
                onClick={() => addCameraToWall(camera)}
                disabled={selectedCameras.length >= gridConfig.maxCameras}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  selectedCameras.length >= gridConfig.maxCameras
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    : 'bg-gray-700 text-white hover:bg-gray-600'
                }`}
              >
                {camera.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
