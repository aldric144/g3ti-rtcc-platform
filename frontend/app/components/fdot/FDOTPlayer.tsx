'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface FDOTPlayerProps {
  cameraId: string;
  autoPlay?: boolean;
  className?: string;
}

export default function FDOTPlayer({ cameraId, autoPlay = true, className = '' }: FDOTPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://g3ti-rtcc-backend.fly.dev';
  const streamUrl = `${backendUrl}/api/fdot/stream/${cameraId}`;

  const loadStream = useCallback(async () => {
    if (!videoRef.current) return;

    setIsLoading(true);
    setError(null);

    try {
      const Hls = (await import('hls.js')).default;

      if (Hls.isSupported()) {
        if (hlsRef.current) {
          hlsRef.current.destroy();
        }

        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: true,
          backBufferLength: 90,
        });

        hlsRef.current = hls;

        hls.loadSource(streamUrl);
        hls.attachMedia(videoRef.current);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setIsLoading(false);
          if (autoPlay && videoRef.current) {
            videoRef.current.play().catch(() => {});
          }
        });

        hls.on(Hls.Events.ERROR, (_event: any, data: any) => {
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                if (retryCount < maxRetries) {
                  setRetryCount(prev => prev + 1);
                  setTimeout(() => hls.startLoad(), 2000);
                } else {
                  setError('Network error - stream unavailable');
                  setIsLoading(false);
                }
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hls.recoverMediaError();
                break;
              default:
                setError('Stream playback error');
                setIsLoading(false);
                break;
            }
          }
        });
      } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        videoRef.current.src = streamUrl;
        videoRef.current.addEventListener('loadedmetadata', () => {
          setIsLoading(false);
          if (autoPlay) {
            videoRef.current?.play().catch(() => {});
          }
        });
        videoRef.current.addEventListener('error', () => {
          setError('Stream playback error');
          setIsLoading(false);
        });
      } else {
        videoRef.current.src = streamUrl;
        setIsLoading(false);
      }
    } catch (err) {
      setError('Failed to load video player');
      setIsLoading(false);
    }
  }, [cameraId, streamUrl, autoPlay, retryCount]);

  useEffect(() => {
    loadStream();

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [loadStream]);

  const handleRetry = () => {
    setRetryCount(0);
    loadStream();
  };

  return (
    <div className={`relative bg-gray-900 rounded-lg overflow-hidden ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-gray-400">Loading stream...</span>
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

      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        controls
        playsInline
        muted
      />
    </div>
  );
}
