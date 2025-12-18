'use client';

import { useEffect, useState, useCallback } from 'react';

interface FDOTCamera {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  stream_url: string;
  description: string;
  category: string;
  mjpeg_url: string;
  health_status: string;
}

export default function FDOTLiveNetworkPage() {
  const [cameras, setCameras] = useState<FDOTCamera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<FDOTCamera | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  const [refreshInterval, setRefreshInterval] = useState(2);

  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';

  const fetchCameras = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${backendUrl}/api/cameras/fdot/mjpeg/list`);
      if (!response.ok) throw new Error('Failed to fetch FDOT cameras');
      const data = await response.json();
      setCameras(data.cameras || []);
      if (data.cameras?.length > 0 && !selectedCamera) {
        setSelectedCamera(data.cameras[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cameras');
    } finally {
      setIsLoading(false);
    }
  }, [backendUrl, selectedCamera]);

  const loadSnapshot = useCallback(async (cameraId: string) => {
    try {
      const timestamp = Date.now();
      const response = await fetch(`${backendUrl}/api/v1/fdot/snapshot/${cameraId}?t=${timestamp}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrls(prev => {
          if (prev[cameraId]) URL.revokeObjectURL(prev[cameraId]);
          return { ...prev, [cameraId]: url };
        });
      }
    } catch (err) {
      console.error(`Failed to load snapshot for ${cameraId}:`, err);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  useEffect(() => {
    if (cameras.length === 0) return;
    
    cameras.forEach(cam => loadSnapshot(cam.id));
    
    const interval = setInterval(() => {
      cameras.forEach(cam => loadSnapshot(cam.id));
    }, refreshInterval * 1000);
    
    return () => {
      clearInterval(interval);
      Object.values(imageUrls).forEach(url => URL.revokeObjectURL(url));
    };
  }, [cameras, loadSnapshot, refreshInterval]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-400">Loading FDOT Live Motion Cameras...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">Error: {error}</div>
          <button
            onClick={() => fetchCameras()}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="text-3xl">🛣️</span>
              FDOT Live Motion Cameras
            </h1>
            <p className="text-gray-400 mt-1">
              FDOT traffic cameras with MJPEG motion simulation - refreshing every {refreshInterval} seconds
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Refresh:</span>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="bg-gray-800 text-white rounded px-2 py-1 text-sm border border-gray-700"
              >
                <option value={1}>1s</option>
                <option value={2}>2s</option>
                <option value={3}>3s</option>
                <option value={5}>5s</option>
              </select>
            </div>
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
              {cameras.filter(c => c.health_status === 'online').length} Online
            </span>
          </div>
        </div>

        {/* Main Video Player */}
        {selectedCamera && (
          <div className="bg-gray-800 rounded-xl overflow-hidden mb-6">
            <div className="aspect-video relative">
              {imageUrls[selectedCamera.id] ? (
                <img
                  src={imageUrls[selectedCamera.id]}
                  alt={selectedCamera.name}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-900">
                  <div className="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                <h2 className="text-white font-semibold text-lg">{selectedCamera.name}</h2>
                <p className="text-gray-300 text-sm">{selectedCamera.location}</p>
              </div>
              <div className="absolute top-4 right-4 flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  selectedCamera.health_status === 'online' 
                    ? 'bg-green-500/20 text-green-400' 
                    : selectedCamera.health_status === 'degraded'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {selectedCamera.health_status === 'online' ? 'LIVE' : 
                   selectedCamera.health_status === 'degraded' ? 'DEGRADED' : 'OFFLINE'}
                </span>
                <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs">
                  FDOT MJPEG
                </span>
              </div>
              <div className="absolute top-4 left-4">
                <div className="flex items-center gap-2 bg-black/50 px-2 py-1 rounded">
                  <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-white text-xs">Motion Simulation Active</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Camera Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {cameras.map(camera => (
            <button
              key={camera.id}
              onClick={() => setSelectedCamera(camera)}
              className={`relative rounded-lg overflow-hidden transition-all ${
                selectedCamera?.id === camera.id 
                  ? 'ring-2 ring-orange-500 scale-105' 
                  : 'hover:ring-2 hover:ring-gray-600'
              }`}
            >
              <div className="aspect-video bg-gray-800">
                {imageUrls[camera.id] ? (
                  <img
                    src={imageUrls[camera.id]}
                    alt={camera.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-2">
                <p className="text-white text-xs font-medium truncate">{camera.name}</p>
                <div className="flex items-center gap-1 mt-1">
                  <span className={`w-2 h-2 rounded-full ${
                    camera.health_status === 'online' ? 'bg-green-500' : 
                    camera.health_status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className="text-gray-400 text-xs">FDOT D4</span>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Add to Video Wall Button */}
        <div className="mt-6 flex justify-center gap-4">
          <button className="px-6 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg flex items-center gap-2 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Add to Video Wall
          </button>
          <button 
            onClick={() => fetchCameras()}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh All
          </button>
        </div>
      </div>
    </div>
  );
}
