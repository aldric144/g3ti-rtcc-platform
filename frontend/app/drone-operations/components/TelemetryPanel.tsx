'use client';

import { useState, useEffect } from 'react';

interface TelemetryData {
  drone_id: string;
  call_sign: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  altitude_m: number;
  speed_mps: number;
  heading_deg: number;
  battery_percent: number;
  signal_strength_dbm: number;
  gps_satellites: number;
  temperature_c: number;
}

export default function TelemetryPanel() {
  const [selectedDrone, setSelectedDrone] = useState<string>('drone-001');
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [history, setHistory] = useState<TelemetryData[]>([]);

  useEffect(() => {
    const mockTelemetry: TelemetryData = {
      drone_id: selectedDrone,
      call_sign: 'EAGLE-1',
      timestamp: new Date().toISOString(),
      latitude: 33.749 + Math.random() * 0.001,
      longitude: -84.388 + Math.random() * 0.001,
      altitude_m: 120 + Math.random() * 10,
      speed_mps: 15 + Math.random() * 5,
      heading_deg: Math.random() * 360,
      battery_percent: 78 - Math.random() * 2,
      signal_strength_dbm: -50 - Math.random() * 10,
      gps_satellites: 12,
      temperature_c: 25 + Math.random() * 5,
    };
    setTelemetry(mockTelemetry);
    setHistory((prev) => [...prev.slice(-19), mockTelemetry]);

    const interval = setInterval(() => {
      const newTelemetry: TelemetryData = {
        ...mockTelemetry,
        timestamp: new Date().toISOString(),
        latitude: mockTelemetry.latitude + (Math.random() - 0.5) * 0.0001,
        longitude: mockTelemetry.longitude + (Math.random() - 0.5) * 0.0001,
        altitude_m: mockTelemetry.altitude_m + (Math.random() - 0.5) * 2,
        speed_mps: Math.max(0, mockTelemetry.speed_mps + (Math.random() - 0.5) * 2),
        heading_deg: (mockTelemetry.heading_deg + Math.random() * 5) % 360,
        battery_percent: Math.max(0, mockTelemetry.battery_percent - 0.1),
      };
      setTelemetry(newTelemetry);
      setHistory((prev) => [...prev.slice(-19), newTelemetry]);
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedDrone]);

  if (!telemetry) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <select
          value={selectedDrone}
          onChange={(e) => setSelectedDrone(e.target.value)}
          className="bg-gray-700 text-white px-4 py-2 rounded-lg"
        >
          <option value="drone-001">EAGLE-1</option>
          <option value="drone-002">HAWK-2</option>
          <option value="drone-003">FALCON-3</option>
          <option value="drone-004">RAVEN-4</option>
        </select>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Altitude</div>
          <div className="text-2xl font-bold text-blue-400">
            {telemetry.altitude_m.toFixed(1)}m
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Speed</div>
          <div className="text-2xl font-bold text-green-400">
            {telemetry.speed_mps.toFixed(1)} m/s
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Heading</div>
          <div className="text-2xl font-bold text-yellow-400">
            {telemetry.heading_deg.toFixed(0)}°
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Battery</div>
          <div className="text-2xl font-bold text-purple-400">
            {telemetry.battery_percent.toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Position Data</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Latitude</span>
              <span>{telemetry.latitude.toFixed(6)}°</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Longitude</span>
              <span>{telemetry.longitude.toFixed(6)}°</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">GPS Satellites</span>
              <span className="text-green-400">{telemetry.gps_satellites}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Signal Strength</span>
              <span
                className={
                  telemetry.signal_strength_dbm > -60
                    ? 'text-green-400'
                    : telemetry.signal_strength_dbm > -80
                    ? 'text-yellow-400'
                    : 'text-red-400'
                }
              >
                {telemetry.signal_strength_dbm.toFixed(0)} dBm
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Temperature</span>
              <span>{telemetry.temperature_c.toFixed(1)}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Last Update</span>
              <span className="text-xs">
                {new Date(telemetry.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Telemetry History</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-600">
                <th className="text-left py-2">Time</th>
                <th className="text-right py-2">Alt (m)</th>
                <th className="text-right py-2">Speed (m/s)</th>
                <th className="text-right py-2">Heading</th>
                <th className="text-right py-2">Battery</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(-10).reverse().map((t, i) => (
                <tr key={i} className="border-b border-gray-600">
                  <td className="py-2">
                    {new Date(t.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="text-right">{t.altitude_m.toFixed(1)}</td>
                  <td className="text-right">{t.speed_mps.toFixed(1)}</td>
                  <td className="text-right">{t.heading_deg.toFixed(0)}°</td>
                  <td className="text-right">{t.battery_percent.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
