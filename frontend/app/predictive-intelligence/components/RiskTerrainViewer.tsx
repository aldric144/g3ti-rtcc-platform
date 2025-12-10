'use client';

import { useState, useEffect } from 'react';

interface RiskZone {
  zone_id: string;
  name: string;
  risk_score: number;
  risk_level: string;
  factors: string[];
  incidents_30d: number;
  trend: string;
}

const riskColors: Record<string, string> = {
  MINIMAL: 'bg-green-500',
  LOW: 'bg-blue-500',
  MODERATE: 'bg-yellow-500',
  HIGH: 'bg-orange-500',
  CRITICAL: 'bg-red-500',
};

export default function RiskTerrainViewer() {
  const [zones, setZones] = useState<RiskZone[]>([]);
  const [selectedZone, setSelectedZone] = useState<RiskZone | null>(null);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');

  useEffect(() => {
    const mockZones: RiskZone[] = [
      {
        zone_id: 'zone-001',
        name: 'Downtown Core',
        risk_score: 78,
        risk_level: 'HIGH',
        factors: ['High foot traffic', 'Bar district', 'Transit hub'],
        incidents_30d: 45,
        trend: 'INCREASING',
      },
      {
        zone_id: 'zone-002',
        name: 'Midtown',
        risk_score: 52,
        risk_level: 'MODERATE',
        factors: ['Commercial area', 'Office buildings'],
        incidents_30d: 23,
        trend: 'STABLE',
      },
      {
        zone_id: 'zone-003',
        name: 'Westside Industrial',
        risk_score: 65,
        risk_level: 'MODERATE',
        factors: ['Abandoned buildings', 'Low lighting', 'Limited patrol'],
        incidents_30d: 31,
        trend: 'DECREASING',
      },
      {
        zone_id: 'zone-004',
        name: 'Buckhead',
        risk_score: 35,
        risk_level: 'LOW',
        factors: ['Residential', 'High security'],
        incidents_30d: 12,
        trend: 'STABLE',
      },
      {
        zone_id: 'zone-005',
        name: 'Airport Corridor',
        risk_score: 88,
        risk_level: 'CRITICAL',
        factors: ['High vehicle theft', 'Transient population', 'Hotel district'],
        incidents_30d: 67,
        trend: 'INCREASING',
      },
    ];
    setZones(mockZones);
  }, [timeRange]);

  const trendIcons: Record<string, JSX.Element> = {
    INCREASING: (
      <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    STABLE: (
      <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
      </svg>
    ),
    DECREASING: (
      <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
      </svg>
    ),
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Risk Terrain Model</h2>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded ${
                timeRange === range ? 'bg-blue-600' : 'bg-gray-700'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-700 rounded-lg aspect-video flex items-center justify-center relative">
            <div className="text-center text-gray-500">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
              <p>Risk Terrain Heatmap</p>
              <p className="text-sm mt-2">
                Color-coded risk zones would render here
              </p>
            </div>

            <div className="absolute bottom-4 left-4 bg-gray-800 bg-opacity-90 rounded-lg p-3">
              <div className="text-xs font-medium mb-2">Risk Levels</div>
              <div className="flex items-center space-x-3 text-xs">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded bg-green-500 mr-1"></div>
                  <span>Minimal</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded bg-yellow-500 mr-1"></div>
                  <span>Moderate</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded bg-red-500 mr-1"></div>
                  <span>Critical</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Risk Zones</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {zones.map((zone) => (
              <button
                key={zone.zone_id}
                onClick={() => setSelectedZone(zone)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedZone?.zone_id === zone.zone_id
                    ? 'bg-blue-600'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{zone.name}</div>
                  <div className="flex items-center space-x-2">
                    {trendIcons[zone.trend]}
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        riskColors[zone.risk_level]
                      }`}
                    >
                      {zone.risk_score}
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  {zone.incidents_30d} incidents (30d)
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {selectedZone && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{selectedZone.name}</h3>
            <button
              onClick={() => setSelectedZone(null)}
              className="text-gray-400 hover:text-white"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Risk Score</div>
              <div className="text-2xl font-bold">{selectedZone.risk_score}</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Risk Level</div>
              <div className={`text-lg font-bold ${
                selectedZone.risk_level === 'CRITICAL' ? 'text-red-400' :
                selectedZone.risk_level === 'HIGH' ? 'text-orange-400' :
                selectedZone.risk_level === 'MODERATE' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {selectedZone.risk_level}
              </div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Incidents (30d)</div>
              <div className="text-2xl font-bold">{selectedZone.incidents_30d}</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Trend</div>
              <div className="flex items-center text-lg font-bold">
                {trendIcons[selectedZone.trend]}
                <span className="ml-2">{selectedZone.trend}</span>
              </div>
            </div>
          </div>

          <div>
            <div className="text-gray-400 text-sm mb-2">Contributing Factors</div>
            <div className="flex flex-wrap gap-2">
              {selectedZone.factors.map((factor, i) => (
                <span
                  key={i}
                  className="bg-gray-600 px-3 py-1 rounded-full text-sm"
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
