'use client';

import { useEffect, useState } from 'react';
import FDOTPlayer from '@/components/fdot/FDOTPlayer';

interface FDOTCamera {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  stream_url: string;
  description: string;
}

export default function FDOTTestPage() {
  const [cameras, setCameras] = useState<FDOTCamera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<FDOTCamera | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${backendUrl}/api/v1/fdot/list`);
        if (!response.ok) {
          throw new Error('Failed to fetch FDOT cameras');
        }
        const data = await response.json();
        setCameras(data.cameras || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cameras');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCameras();
  }, [backendUrl]);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">FDOT Live Streaming Test</h1>
          <p className="text-gray-400 text-sm">
            Hidden test page for FDOT HLS/MPEG-TS streaming. Not integrated with RTCC modules.
          </p>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="ml-3 text-gray-400">Loading FDOT cameras...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-gray-900 rounded-lg border border-gray-800">
              <div className="p-4 border-b border-gray-800">
                <h2 className="text-lg font-semibold">FDOT Cameras ({cameras.length})</h2>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {cameras.map((camera) => (
                  <button
                    key={camera.id}
                    onClick={() => setSelectedCamera(camera)}
                    className={`w-full text-left p-4 border-b border-gray-800 hover:bg-gray-800/50 transition-colors ${
                      selectedCamera?.id === camera.id ? 'bg-blue-500/10 border-l-2 border-l-blue-500' : ''
                    }`}
                  >
                    <div className="font-medium text-white">{camera.name}</div>
                    <div className="text-sm text-gray-400 mt-1">{camera.location}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {camera.lat.toFixed(4)}, {camera.lng.toFixed(4)}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {selectedCamera ? (
              <div className="bg-gray-900 rounded-lg border border-gray-800">
                <div className="p-4 border-b border-gray-800">
                  <h2 className="text-lg font-semibold">{selectedCamera.name}</h2>
                  <p className="text-sm text-gray-400 mt-1">{selectedCamera.description}</p>
                </div>
                <div className="p-4">
                  <FDOTPlayer
                    cameraId={selectedCamera.id}
                    className="aspect-video w-full"
                  />
                </div>
                <div className="p-4 border-t border-gray-800 bg-gray-900/50">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Camera ID:</span>
                      <span className="ml-2 text-gray-300">{selectedCamera.id}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Location:</span>
                      <span className="ml-2 text-gray-300">{selectedCamera.location}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Latitude:</span>
                      <span className="ml-2 text-gray-300">{selectedCamera.lat}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Longitude:</span>
                      <span className="ml-2 text-gray-300">{selectedCamera.lng}</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-12 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-300 mb-2">Select a Camera</h3>
                <p className="text-gray-500">Click on a camera from the list to view its live stream</p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Test Page Information</h3>
          <ul className="text-xs text-gray-500 space-y-1">
            <li>This is a hidden test page for FDOT live streaming functionality.</li>
            <li>Not integrated with RTCC sidebar or modules.</li>
            <li>Uses HLS.js for video playback with auto-retry on disconnect.</li>
            <li>Backend endpoint: {backendUrl}/api/fdot/list</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
