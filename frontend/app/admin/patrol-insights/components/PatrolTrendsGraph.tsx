'use client';

import { BarChart3 } from 'lucide-react';

interface PatrolTrendsGraphProps {
  refreshKey: number;
}

export function PatrolTrendsGraph({ refreshKey }: PatrolTrendsGraphProps) {
  // Mock hourly data for the last 24 hours
  const hourlyData = Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    visits: Math.floor(Math.random() * 50) + 100,
    incidents: Math.floor(Math.random() * 5),
  }));

  const maxVisits = Math.max(...hourlyData.map(d => d.visits));

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
          <BarChart3 className="h-5 w-5" />
          Patrol Activity Trends (24h)
        </h2>
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-rtcc-primary" />
            Patrol Visits
          </span>
          <span className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-red-500" />
            Incidents
          </span>
        </div>
      </div>

      {/* Simple Bar Chart */}
      <div className="relative h-64">
        <div className="absolute inset-0 flex items-end justify-between gap-1">
          {hourlyData.map((data, index) => (
            <div key={index} className="flex flex-1 flex-col items-center">
              <div className="relative w-full flex flex-col items-center gap-1" style={{ height: '200px' }}>
                {/* Incident marker */}
                {data.incidents > 0 && (
                  <div
                    className="absolute top-0 w-2 rounded-full bg-red-500"
                    style={{ height: `${(data.incidents / 5) * 30}px` }}
                  />
                )}
                {/* Visit bar */}
                <div
                  className="w-full rounded-t bg-rtcc-primary/80 hover:bg-rtcc-primary transition-colors"
                  style={{
                    height: `${(data.visits / maxVisits) * 180}px`,
                    marginTop: 'auto',
                  }}
                />
              </div>
              {index % 4 === 0 && (
                <span className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  {data.hour.toString().padStart(2, '0')}:00
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-4 gap-4 border-t border-gray-200 pt-4 dark:border-gray-700">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {hourlyData.reduce((sum, d) => sum + d.visits, 0).toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Visits</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {Math.round(hourlyData.reduce((sum, d) => sum + d.visits, 0) / 24)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Avg/Hour</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {Math.max(...hourlyData.map(d => d.visits))}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Peak Hour</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-red-600">
            {hourlyData.reduce((sum, d) => sum + d.incidents, 0)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Incidents</p>
        </div>
      </div>
    </div>
  );
}
