'use client';

import { useState } from 'react';

interface VideoStream {
  drone_id: string;
  call_sign: string;
  status: string;
  resolution: string;
  fps: number;
  bitrate_kbps: number;
  latency_ms: number;
}

export default function LiveDroneVideo() {
  const [selectedStream, setSelectedStream] = useState<string>('drone-001');
  const [streams] = useState<VideoStream[]>([
    {
      drone_id: 'drone-001',
      call_sign: 'EAGLE-1',
      status: 'STREAMING',
      resolution: '1920x1080',
      fps: 30,
      bitrate_kbps: 4500,
      latency_ms: 120,
    },
    {
      drone_id: 'drone-003',
      call_sign: 'FALCON-3',
      status: 'STREAMING',
      resolution: '1280x720',
      fps: 30,
      bitrate_kbps: 2500,
      latency_ms: 150,
    },
  ]);

  const activeStream = streams.find((s) => s.drone_id === selectedStream);

  return (
    <div>
      <div className="flex space-x-4 mb-6">
        {streams.map((stream) => (
          <button
            key={stream.drone_id}
            onClick={() => setSelectedStream(stream.drone_id)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedStream === stream.drone_id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {stream.call_sign}
            <span
              className={`ml-2 inline-block w-2 h-2 rounded-full ${
                stream.status === 'STREAMING' ? 'bg-green-400' : 'bg-gray-400'
              }`}
            ></span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-black rounded-lg aspect-video flex items-center justify-center relative">
            <div className="absolute top-4 left-4 bg-red-600 px-2 py-1 rounded text-xs font-bold flex items-center">
              <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
              LIVE
            </div>
            <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-75 px-3 py-1 rounded text-sm">
              {activeStream?.call_sign}
            </div>
            <div className="text-gray-500 text-center">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              <p>Video Stream Placeholder</p>
              <p className="text-sm mt-2">WebRTC connection would display here</p>
            </div>
            <div className="absolute bottom-4 left-4 right-4 flex justify-between text-xs text-gray-400">
              <span>{activeStream?.resolution}</span>
              <span>{activeStream?.fps} FPS</span>
              <span>{activeStream?.latency_ms}ms latency</span>
            </div>
          </div>

          <div className="mt-4 flex space-x-2">
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
              Zoom In
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
              Zoom Out
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Snapshot
            </button>
            <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="8" />
              </svg>
              Record
            </button>
          </div>
        </div>

        <div>
          <div className="bg-gray-700 rounded-lg p-4 mb-4">
            <h3 className="text-lg font-semibold mb-4">Stream Info</h3>
            {activeStream && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status</span>
                  <span className="text-green-400">{activeStream.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Resolution</span>
                  <span>{activeStream.resolution}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Frame Rate</span>
                  <span>{activeStream.fps} FPS</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Bitrate</span>
                  <span>{activeStream.bitrate_kbps} kbps</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Latency</span>
                  <span
                    className={
                      activeStream.latency_ms < 100
                        ? 'text-green-400'
                        : activeStream.latency_ms < 200
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }
                  >
                    {activeStream.latency_ms}ms
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Camera Controls</h3>
            <div className="grid grid-cols-3 gap-2">
              <div></div>
              <button className="bg-gray-600 hover:bg-gray-500 p-3 rounded-lg">
                <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <div></div>
              <button className="bg-gray-600 hover:bg-gray-500 p-3 rounded-lg">
                <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button className="bg-gray-600 hover:bg-gray-500 p-3 rounded-lg text-xs">
                CENTER
              </button>
              <button className="bg-gray-600 hover:bg-gray-500 p-3 rounded-lg">
                <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <div></div>
              <button className="bg-gray-600 hover:bg-gray-500 p-3 rounded-lg">
                <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
