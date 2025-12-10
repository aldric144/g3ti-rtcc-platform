'use client';

import { useState } from 'react';

interface TimeTravelScrubberProps {
  currentTime: Date;
  onTimeChange: (time: Date) => void;
  isLive: boolean;
  onLiveToggle: () => void;
}

export default function TimeTravelScrubber({
  currentTime,
  onTimeChange,
  isLive,
  onLiveToggle,
}: TimeTravelScrubberProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const now = new Date();
  const minTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const maxTime = now;

  const progress =
    ((currentTime.getTime() - minTime.getTime()) /
      (maxTime.getTime() - minTime.getTime())) *
    100;

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    const newTime = new Date(
      minTime.getTime() + (value / 100) * (maxTime.getTime() - minTime.getTime())
    );
    onTimeChange(newTime);
  };

  const skipTime = (minutes: number) => {
    const newTime = new Date(currentTime.getTime() + minutes * 60 * 1000);
    if (newTime <= maxTime && newTime >= minTime) {
      onTimeChange(newTime);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => skipTime(-60)}
            className="bg-gray-700 hover:bg-gray-600 p-2 rounded"
            disabled={isLive}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={() => skipTime(-5)}
            className="bg-gray-700 hover:bg-gray-600 p-2 rounded"
            disabled={isLive}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`p-2 rounded ${
              isPlaying ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
            disabled={isLive}
          >
            {isPlaying ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
          <button
            onClick={() => skipTime(5)}
            className="bg-gray-700 hover:bg-gray-600 p-2 rounded"
            disabled={isLive}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            onClick={() => skipTime(60)}
            className="bg-gray-700 hover:bg-gray-600 p-2 rounded"
            disabled={isLive}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
            className="bg-gray-700 text-white px-2 py-1 rounded text-sm"
            disabled={isLive}
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
            <option value={10}>10x</option>
          </select>

          <button
            onClick={onLiveToggle}
            className={`px-3 py-1 rounded text-sm font-medium ${
              isLive
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isLive ? 'LIVE' : 'Go Live'}
          </button>
        </div>
      </div>

      <div className="relative">
        <input
          type="range"
          min="0"
          max="100"
          value={isLive ? 100 : progress}
          onChange={handleSliderChange}
          disabled={isLive}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-2">
          <span>{minTime.toLocaleTimeString()}</span>
          <span className="font-medium text-white">
            {currentTime.toLocaleTimeString()}
          </span>
          <span>{maxTime.toLocaleTimeString()}</span>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-center space-x-4 text-sm">
        <button
          onClick={() => {
            const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
            onTimeChange(oneHourAgo);
          }}
          className="text-gray-400 hover:text-white"
          disabled={isLive}
        >
          1 hour ago
        </button>
        <button
          onClick={() => {
            const sixHoursAgo = new Date(now.getTime() - 6 * 60 * 60 * 1000);
            onTimeChange(sixHoursAgo);
          }}
          className="text-gray-400 hover:text-white"
          disabled={isLive}
        >
          6 hours ago
        </button>
        <button
          onClick={() => {
            const twelveHoursAgo = new Date(now.getTime() - 12 * 60 * 60 * 1000);
            onTimeChange(twelveHoursAgo);
          }}
          className="text-gray-400 hover:text-white"
          disabled={isLive}
        >
          12 hours ago
        </button>
      </div>
    </div>
  );
}
