'use client';

import { useState, useEffect } from 'react';

interface ThreatProjection {
  projection_id: string;
  threat_type: string;
  zone: string;
  current_level: number;
  projected_level: number;
  projection_date: string;
  confidence: number;
  factors: string[];
}

interface TrendData {
  date: string;
  actual: number;
  predicted: number;
}

export default function ThreatProjectionGraphs() {
  const [projections, setProjections] = useState<ThreatProjection[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [selectedThreatType, setSelectedThreatType] = useState<string>('all');
  const [projectionHorizon, setProjectionHorizon] = useState<'7d' | '14d' | '30d'>('7d');

  useEffect(() => {
    const mockProjections: ThreatProjection[] = [
      {
        projection_id: 'proj-001',
        threat_type: 'VIOLENT_CRIME',
        zone: 'Downtown Core',
        current_level: 65,
        projected_level: 72,
        projection_date: '2024-12-16',
        confidence: 78,
        factors: ['Weekend approaching', 'Major event scheduled', 'Historical pattern'],
      },
      {
        projection_id: 'proj-002',
        threat_type: 'PROPERTY_CRIME',
        zone: 'Midtown',
        current_level: 45,
        projected_level: 42,
        projection_date: '2024-12-16',
        confidence: 82,
        factors: ['Increased patrol presence', 'Weather forecast (rain)'],
      },
      {
        projection_id: 'proj-003',
        threat_type: 'GANG_ACTIVITY',
        zone: 'Westside Industrial',
        current_level: 58,
        projected_level: 65,
        projection_date: '2024-12-16',
        confidence: 71,
        factors: ['Recent arrests', 'Retaliation risk', 'Territory dispute'],
      },
      {
        projection_id: 'proj-004',
        threat_type: 'DOMESTIC_VIOLENCE',
        zone: 'Citywide',
        current_level: 52,
        projected_level: 58,
        projection_date: '2024-12-16',
        confidence: 75,
        factors: ['Holiday season', 'Economic stress indicators'],
      },
    ];

    const mockTrendData: TrendData[] = [];
    const today = new Date();
    for (let i = 30; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      mockTrendData.push({
        date: date.toISOString().split('T')[0],
        actual: 40 + Math.random() * 30 + Math.sin(i / 7) * 10,
        predicted: 45 + Math.random() * 25 + Math.sin(i / 7) * 10,
      });
    }

    setProjections(mockProjections);
    setTrendData(mockTrendData);
  }, [projectionHorizon, selectedThreatType]);

  const threatTypes = ['all', 'VIOLENT_CRIME', 'PROPERTY_CRIME', 'GANG_ACTIVITY', 'DOMESTIC_VIOLENCE'];

  const filteredProjections =
    selectedThreatType === 'all'
      ? projections
      : projections.filter((p) => p.threat_type === selectedThreatType);

  const getThreatColor = (level: number) => {
    if (level >= 75) return 'text-red-400';
    if (level >= 50) return 'text-orange-400';
    if (level >= 25) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getChangeIndicator = (current: number, projected: number) => {
    const change = projected - current;
    if (change > 5) {
      return (
        <span className="text-red-400 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          +{change.toFixed(0)}
        </span>
      );
    }
    if (change < -5) {
      return (
        <span className="text-green-400 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
          </svg>
          {change.toFixed(0)}
        </span>
      );
    }
    return <span className="text-yellow-400">Stable</span>;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Threat Projections</h2>
        <div className="flex items-center space-x-4">
          <select
            value={selectedThreatType}
            onChange={(e) => setSelectedThreatType(e.target.value)}
            className="bg-gray-700 text-white px-3 py-1 rounded"
          >
            {threatTypes.map((type) => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Threats' : type.replace('_', ' ')}
              </option>
            ))}
          </select>
          <div className="flex space-x-2">
            {(['7d', '14d', '30d'] as const).map((horizon) => (
              <button
                key={horizon}
                onClick={() => setProjectionHorizon(horizon)}
                className={`px-3 py-1 rounded ${
                  projectionHorizon === horizon ? 'bg-blue-600' : 'bg-gray-700'
                }`}
              >
                {horizon}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Trend Analysis</h3>
          <div className="h-64 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <svg
                className="w-12 h-12 mx-auto mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
              <p className="text-sm">Trend Chart Placeholder</p>
              <p className="text-xs mt-1">Chart.js/Recharts would render here</p>
            </div>
          </div>
          <div className="flex justify-center space-x-6 mt-4 text-sm">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
              <span>Actual</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded mr-2"></div>
              <span>Predicted</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Model Accuracy</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Overall Accuracy</span>
                <span className="text-green-400">87%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '87%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Violent Crime Accuracy</span>
                <span className="text-green-400">82%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '82%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Property Crime Accuracy</span>
                <span className="text-green-400">91%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '91%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>False Positive Rate</span>
                <span className="text-yellow-400">8%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '8%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Active Projections</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredProjections.map((projection) => (
            <div
              key={projection.projection_id}
              className="bg-gray-600 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-medium">
                    {projection.threat_type.replace('_', ' ')}
                  </div>
                  <div className="text-sm text-gray-400">{projection.zone}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-400">Confidence</div>
                  <div className="font-bold">{projection.confidence}%</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-3">
                <div>
                  <div className="text-xs text-gray-400">Current</div>
                  <div className={`text-xl font-bold ${getThreatColor(projection.current_level)}`}>
                    {projection.current_level}
                  </div>
                </div>
                <div className="flex items-center justify-center">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </div>
                <div>
                  <div className="text-xs text-gray-400">Projected</div>
                  <div className={`text-xl font-bold ${getThreatColor(projection.projected_level)}`}>
                    {projection.projected_level}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">
                  By {new Date(projection.projection_date).toLocaleDateString()}
                </span>
                {getChangeIndicator(projection.current_level, projection.projected_level)}
              </div>

              <div className="mt-3 pt-3 border-t border-gray-500">
                <div className="text-xs text-gray-400 mb-1">Contributing Factors</div>
                <div className="flex flex-wrap gap-1">
                  {projection.factors.map((factor, i) => (
                    <span
                      key={i}
                      className="bg-gray-500 px-2 py-0.5 rounded text-xs"
                    >
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
