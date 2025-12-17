'use client';

import { useEffect, useState, useCallback, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Camera, 
  RefreshCw, 
  ArrowLeft,
  MapPin,
  Video,
  Grid,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Home,
  Plus,
  Clock,
  Activity,
  Settings
} from 'lucide-react';
import Link from 'next/link';

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
  address?: string;
  created_at?: string;
  updated_at?: string;
  supports_mjpeg?: boolean;
  snapshot_url?: string;
}

interface HealthData {
  camera_id: string;
  status: string;
  response_time_ms: number;
  last_check: string;
  error_message?: string;
  consecutive_failures: number;
}

function CameraDetailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const cameraId = searchParams.get('id') || '';

  const [camera, setCamera] = useState<CameraData | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPTZ, setIsPTZ] = useState(false);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const fetchCamera = useCallback(async () => {
    if (!cameraId) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/cameras/public/${cameraId}`);
      if (response.ok) {
        const data = await response.json();
        setCamera(data);
        setIsPTZ((data.camera_type || data.type) === 'ptz');
        setError(null);
      } else {
        throw new Error('Camera not found');
      }
    } catch (err) {
      console.error('Failed to fetch camera:', err);
      setError('Unable to load camera. Using demo data.');
      // Try to find in demo data
      try {
        const demoResponse = await fetch('/demo_data/public_cameras.json');
        if (demoResponse.ok) {
          const demoData = await demoResponse.json();
          const found = demoData.cameras?.find((c: CameraData) => c.id === cameraId);
          if (found) {
            setCamera(found);
            setIsPTZ((found.camera_type || found.type) === 'ptz');
          }
        }
      } catch {
        setCamera(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, [apiBaseUrl, cameraId]);

  useEffect(() => {
    if (cameraId) {
      fetchCamera();
    }
  }, [cameraId, fetchCamera]);

  const sendPTZCommand = async (command: string, value?: number) => {
    if (!isPTZ) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/cameras/ptz/${cameraId}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, value }),
      });

      if (!response.ok) {
        console.error('PTZ command failed');
      }
    } catch (err) {
      console.error('PTZ command error:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'online': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'ptz': return 'bg-amber-600';
      case 'lpr': return 'bg-red-600';
      case 'cctv': return 'bg-blue-600';
      case 'traffic': return 'bg-green-600';
      default: return 'bg-gray-600';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading camera...</span>
      </div>
    );
  }

  if (!cameraId || !camera) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
        <Camera className="h-16 w-16 text-gray-600 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Camera Not Found</h1>
        <p className="text-gray-400 mb-4">The camera you are looking for does not exist or no ID was provided.</p>
        <Link
          href="/cameras"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Directory
        </Link>
      </div>
    );
  }

  const camType = camera.camera_type || camera.type || 'cctv';

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-700 rounded-lg"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold">{camera.name}</h1>
              <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
                <span>{camera.jurisdiction}</span>
                <span>-</span>
                <span>{camera.sector}</span>
                <span>-</span>
                <span className={`px-2 py-0.5 rounded text-white ${getTypeColor(camType)}`}>
                  {camType.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/cameras/video-wall"
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
            >
              <Plus className="h-4 w-4" />
              Add to Video Wall
            </Link>
            <button
              onClick={fetchCamera}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
            >
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-4 bg-amber-900/30 border border-amber-500/50 text-amber-200 px-4 py-2 rounded">
          {error}
        </div>
      )}

      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Video Feed */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg overflow-hidden">
              {/* Video */}
              <div className="relative aspect-video bg-black">
                {camera.supports_mjpeg || camera.jurisdiction === 'FDOT' ? (
                  <img
                    src={camera.stream_url 
                      ? `${apiBaseUrl}${camera.stream_url}`
                      : `${apiBaseUrl}/api/cameras/fdot/${camera.id}/stream`}
                    alt={camera.name}
                    className="w-full h-full object-contain"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <img
                    src={camera.snapshot_url || camera.stream_url || 'https://via.placeholder.com/1280x720?text=Camera+Feed'}
                    alt={camera.name}
                    className="w-full h-full object-contain"
                  />
                )}

                {/* Status Overlay */}
                <div className="absolute top-4 left-4 flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${getStatusColor(camera.status)} animate-pulse`} />
                  <span className="text-sm text-white bg-black/50 px-2 py-1 rounded">
                    {camera.status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>

                {/* Live Badge */}
                <div className="absolute top-4 right-4">
                  <span className="flex items-center gap-1 text-sm text-white bg-red-600 px-2 py-1 rounded">
                    <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    LIVE
                  </span>
                </div>
              </div>

              {/* PTZ Controls */}
              {isPTZ && (
                <div className="p-4 border-t border-gray-700">
                  <h3 className="text-sm font-medium text-gray-400 mb-3">PTZ Controls</h3>
                  <div className="flex items-center justify-center gap-8">
                    {/* Direction Pad */}
                    <div className="grid grid-cols-3 gap-1">
                      <div />
                      <button
                        onClick={() => sendPTZCommand('tilt_up')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ChevronUp className="h-5 w-5" />
                      </button>
                      <div />
                      <button
                        onClick={() => sendPTZCommand('pan_left')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ChevronLeft className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => sendPTZCommand('preset', 1)}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <Home className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => sendPTZCommand('pan_right')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ChevronRight className="h-5 w-5" />
                      </button>
                      <div />
                      <button
                        onClick={() => sendPTZCommand('tilt_down')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ChevronDown className="h-5 w-5" />
                      </button>
                      <div />
                    </div>

                    {/* Zoom Controls */}
                    <div className="flex flex-col gap-2">
                      <button
                        onClick={() => sendPTZCommand('zoom_in')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ZoomIn className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => sendPTZCommand('zoom_out')}
                        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                      >
                        <ZoomOut className="h-5 w-5" />
                      </button>
                    </div>

                    {/* Presets */}
                    <div className="flex flex-col gap-2">
                      <span className="text-xs text-gray-400">Presets</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4].map((preset) => (
                          <button
                            key={preset}
                            onClick={() => sendPTZCommand('preset', preset)}
                            className="w-8 h-8 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                          >
                            {preset}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Camera Info */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <Camera className="h-4 w-4 text-blue-400" />
                Camera Information
              </h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-400">ID</dt>
                  <dd className="font-mono">{camera.id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Type</dt>
                  <dd>{camType.toUpperCase()}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Jurisdiction</dt>
                  <dd>{camera.jurisdiction}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Sector</dt>
                  <dd>{camera.sector}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Status</dt>
                  <dd className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${getStatusColor(camera.status)}`} />
                    {camera.status}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Location */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <MapPin className="h-4 w-4 text-green-400" />
                Location
              </h3>
              <dl className="space-y-2 text-sm">
                {camera.address && (
                  <div>
                    <dt className="text-gray-400">Address</dt>
                    <dd className="mt-1">{camera.address}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-gray-400">Latitude</dt>
                  <dd className="font-mono">{camera.latitude?.toFixed(6)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Longitude</dt>
                  <dd className="font-mono">{camera.longitude?.toFixed(6)}</dd>
                </div>
              </dl>
              <Link
                href="/cameras/map"
                className="flex items-center justify-center gap-2 mt-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
              >
                <MapPin className="h-4 w-4" />
                View on Map
              </Link>
            </div>

            {/* Health Status */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <Activity className="h-4 w-4 text-purple-400" />
                Health Status
              </h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-400">Response Time</dt>
                  <dd>{health?.response_time_ms?.toFixed(0) || '50'}ms</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Last Check</dt>
                  <dd>{health?.last_check ? new Date(health.last_check).toLocaleTimeString() : 'Just now'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-400">Failures</dt>
                  <dd>{health?.consecutive_failures || 0}</dd>
                </div>
              </dl>
            </div>

            {/* Description */}
            {camera.description && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-2">Description</h3>
                <p className="text-sm text-gray-400">{camera.description}</p>
              </div>
            )}

            {/* Timestamps */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-400" />
                Timestamps
              </h3>
              <dl className="space-y-2 text-sm">
                {camera.created_at && (
                  <div className="flex justify-between">
                    <dt className="text-gray-400">Created</dt>
                    <dd>{new Date(camera.created_at).toLocaleDateString()}</dd>
                  </div>
                )}
                {camera.updated_at && (
                  <div className="flex justify-between">
                    <dt className="text-gray-400">Updated</dt>
                    <dd>{new Date(camera.updated_at).toLocaleDateString()}</dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CameraDetailPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading camera...</span>
      </div>
    }>
      <CameraDetailContent />
    </Suspense>
  );
}
