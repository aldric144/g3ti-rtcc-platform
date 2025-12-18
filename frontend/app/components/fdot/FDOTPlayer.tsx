'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface FDOTPlayerProps {
  cameraId: string;
  autoPlay?: boolean;
  className?: string;
}

export default function FDOTPlayer({ cameraId, autoPlay = true, className = '' }: FDOTPlayerProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';
  const snapshotUrl = `${backendUrl}/api/v1/fdot/snapshot/${cameraId}`;

  const loadSnapshot = useCallback(async () => {
    try {
      const timestamp = Date.now();
      const url = `${snapshotUrl}?t=${timestamp}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to load camera snapshot');
      }
      
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      
      setImageUrl(prev => {
        if (prev) URL.revokeObjectURL(prev);
        return objectUrl;
      });
      setLastUpdate(new Date());
      setIsLoading(false);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load snapshot');
      setIsLoading(false);
    }
  }, [snapshotUrl]);

  useEffect(() => {
    loadSnapshot();

    if (autoPlay) {
      intervalRef.current = setInterval(loadSnapshot, 10000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [loadSnapshot, autoPlay]);

  const handleRetry = () => {
    setIsLoading(true);
    setError(null);
    loadSnapshot();
  };

  return (
    <div className={`relative bg-gray-900 rounded-lg overflow-hidden ${className}`}>
      {isLoading && !imageUrl && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-gray-400">Loading camera...</span>
          </div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/90 z-10">
          <div className="flex flex-col items-center gap-3 text-center p-4">
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <span className="text-sm text-gray-300">{error}</span>
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {imageUrl && (
        <img
          src={imageUrl}
          alt="FDOT Camera Feed"
          className="w-full h-full object-contain"
        />
      )}

      {lastUpdate && (
        <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-gray-300">
          Live - Updated {lastUpdate.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
