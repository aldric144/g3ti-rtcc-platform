'use client';

import { useEffect, useState, useCallback } from 'react';
import { 
  Camera, 
  RefreshCw, 
  Grid, 
  Maximize2,
  Minimize2,
  Plus,
  X,
  Save,
  FolderOpen,
  Trash2,
  Move,
  Settings
} from 'lucide-react';
import Link from 'next/link';

interface CameraData {
  id: string;
  name: string;
  stream_url: string;
  camera_type?: string;
  jurisdiction?: string;
  sector?: string;
  status?: string;
  fdot_id?: string;
  supports_mjpeg?: boolean;
  snapshot_url?: string;
}

interface VideoWallSlot {
  position: number;
  camera_id: string | null;
  camera_name: string | null;
  stream_url: string | null;
  is_empty: boolean;
  jurisdiction?: string | null;
  fdot_id?: string | null;
  supports_mjpeg?: boolean;
  snapshot_url?: string | null;
}

interface VideoWallSession {
  session_id: string;
  user_id: string;
  layout: string;
  slots: VideoWallSlot[];
}

type LayoutType = '1x1' | '2x2' | '3x3' | '4x4';

const LAYOUTS: Record<LayoutType, { rows: number; cols: number; slots: number }> = {
  '1x1': { rows: 1, cols: 1, slots: 1 },
  '2x2': { rows: 2, cols: 2, slots: 4 },
  '3x3': { rows: 3, cols: 3, slots: 9 },
  '4x4': { rows: 4, cols: 4, slots: 16 },
};

export default function VideoWallPage() {
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [slots, setSlots] = useState<VideoWallSlot[]>([]);
  const [layout, setLayout] = useState<LayoutType>('2x2');
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showCameraSelector, setShowCameraSelector] = useState<number | null>(null);
  const [draggedSlot, setDraggedSlot] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev/api/v1';

  // Initialize slots based on layout
  useEffect(() => {
    const slotCount = LAYOUTS[layout].slots;
    setSlots(prev => {
      const newSlots: VideoWallSlot[] = [];
      for (let i = 0; i < slotCount; i++) {
        if (prev[i] && !prev[i].is_empty) {
          newSlots.push({ ...prev[i], position: i });
        } else {
          newSlots.push({
            position: i,
            camera_id: null,
            camera_name: null,
            stream_url: null,
            is_empty: true,
          });
        }
      }
      return newSlots;
    });
  }, [layout]);

  const fetchCameras = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/cameras`);
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
      } else {
        throw new Error('Failed to fetch cameras');
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
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

  const addCameraToSlot = (position: number, camera: CameraData) => {
    setSlots(prev => prev.map(slot => 
      slot.position === position
        ? {
            ...slot,
            camera_id: camera.id,
            camera_name: camera.name,
            stream_url: camera.stream_url,
            is_empty: false,
            jurisdiction: camera.jurisdiction || null,
            fdot_id: camera.fdot_id || null,
            supports_mjpeg: camera.supports_mjpeg || (camera.jurisdiction === 'FDOT'),
            snapshot_url: camera.snapshot_url || null,
          }
        : slot
    ));
    setShowCameraSelector(null);
  };

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';

  const getStreamUrl = (slot: VideoWallSlot) => {
    if (slot.supports_mjpeg && slot.stream_url) {
      return `${apiBaseUrl}${slot.stream_url}`;
    }
    if (slot.jurisdiction === 'FDOT' && slot.fdot_id) {
      return `${apiBaseUrl}/api/cameras/fdot/${slot.fdot_id}/stream`;
    }
    return slot.snapshot_url || slot.stream_url || 'https://via.placeholder.com/640x360?text=Camera';
  };

  const removeCameraFromSlot = (position: number) => {
    setSlots(prev => prev.map(slot =>
      slot.position === position
        ? {
            ...slot,
            camera_id: null,
            camera_name: null,
            stream_url: null,
            is_empty: true,
          }
        : slot
    ));
  };

  const clearAllSlots = () => {
    setSlots(prev => prev.map(slot => ({
      ...slot,
      camera_id: null,
      camera_name: null,
      stream_url: null,
      is_empty: true,
    })));
  };

  const handleDragStart = (position: number) => {
    setDraggedSlot(position);
  };

  const handleDragOver = (e: React.DragEvent, position: number) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, targetPosition: number) => {
    e.preventDefault();
    if (draggedSlot === null || draggedSlot === targetPosition) {
      setDraggedSlot(null);
      return;
    }

    // Swap slots
    setSlots(prev => {
      const newSlots = [...prev];
      const sourceSlot = { ...newSlots[draggedSlot] };
      const targetSlot = { ...newSlots[targetPosition] };

      newSlots[draggedSlot] = {
        ...targetSlot,
        position: draggedSlot,
      };
      newSlots[targetPosition] = {
        ...sourceSlot,
        position: targetPosition,
      };

      return newSlots;
    });

    setDraggedSlot(null);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const { rows, cols } = LAYOUTS[layout];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading video wall...</span>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-black text-white ${isFullscreen ? 'p-0' : 'p-4'}`}>
      {/* Header - Hidden in fullscreen */}
      {!isFullscreen && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Grid className="h-8 w-8 text-purple-400" />
            <h1 className="text-2xl font-bold">Video Wall</h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Layout Selector */}
            <div className="flex bg-gray-800 rounded-lg">
              {(Object.keys(LAYOUTS) as LayoutType[]).map((l) => (
                <button
                  key={l}
                  onClick={() => setLayout(l)}
                  className={`px-3 py-2 text-sm ${layout === l ? 'bg-purple-600' : ''} ${l === '1x1' ? 'rounded-l-lg' : ''} ${l === '4x4' ? 'rounded-r-lg' : ''}`}
                >
                  {l}
                </button>
              ))}
            </div>

            <button
              onClick={clearAllSlots}
              className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
            >
              <Trash2 className="h-4 w-4" />
              Clear
            </button>

            <button
              onClick={toggleFullscreen}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
            >
              <Maximize2 className="h-5 w-5" />
            </button>

            <Link
              href="/cameras"
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
            >
              <Camera className="h-4 w-4" />
              Directory
            </Link>
          </div>
        </div>
      )}

      {/* Fullscreen Exit Button */}
      {isFullscreen && (
        <button
          onClick={toggleFullscreen}
          className="absolute top-4 right-4 z-50 p-2 bg-black/50 hover:bg-black/70 rounded-lg"
        >
          <Minimize2 className="h-5 w-5 text-white" />
        </button>
      )}

      {/* Video Wall Grid */}
      <div
        className={`grid gap-1 ${isFullscreen ? 'h-screen' : 'h-[calc(100vh-120px)]'}`}
        style={{
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
        }}
      >
        {slots.map((slot) => (
          <div
            key={slot.position}
            className={`relative bg-gray-900 rounded overflow-hidden ${
              draggedSlot === slot.position ? 'opacity-50' : ''
            }`}
            draggable={!slot.is_empty}
            onDragStart={() => handleDragStart(slot.position)}
            onDragOver={(e) => handleDragOver(e, slot.position)}
            onDrop={(e) => handleDrop(e, slot.position)}
          >
            {slot.is_empty ? (
              /* Empty Slot */
              <div
                className="w-full h-full flex flex-col items-center justify-center cursor-pointer hover:bg-gray-800 transition-colors"
                onClick={() => setShowCameraSelector(slot.position)}
              >
                <Plus className="h-8 w-8 text-gray-600 mb-2" />
                <span className="text-gray-500 text-sm">Add Camera</span>
              </div>
            ) : (
              /* Camera Feed */
              <>
                <img
                  src={getStreamUrl(slot)}
                  alt={slot.camera_name || 'Camera'}
                  className="w-full h-full object-cover"
                />

                {/* Camera Info Overlay */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium truncate">{slot.camera_name}</span>
                    <div className="flex items-center gap-1">
                      <Move className="h-4 w-4 text-gray-400 cursor-move" />
                      <button
                        onClick={() => removeCameraFromSlot(slot.position)}
                        className="p-1 hover:bg-red-600/50 rounded"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {/* Camera Selector Modal */}
      {showCameraSelector !== null && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-lg font-bold">Select Camera</h2>
              <button
                onClick={() => setShowCameraSelector(null)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {cameras.map((camera) => (
                  <button
                    key={camera.id}
                    onClick={() => addCameraToSlot(showCameraSelector, camera)}
                    className="bg-gray-700 rounded-lg overflow-hidden hover:ring-2 hover:ring-purple-500 transition-all text-left"
                  >
                    <div className="aspect-video bg-black">
                      <img
                        src={camera.stream_url || 'https://via.placeholder.com/640x360?text=Camera'}
                        alt={camera.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-2">
                      <div className="font-medium text-sm truncate">{camera.name}</div>
                      <div className="text-xs text-gray-400 truncate">
                        {camera.jurisdiction} - {camera.sector}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
