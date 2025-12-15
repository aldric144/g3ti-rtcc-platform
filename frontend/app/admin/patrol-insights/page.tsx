'use client';

import { useState } from 'react';
import { Map, BarChart3, MapPin, TrendingUp } from 'lucide-react';
import { PatrolHeatmapPanel } from './components/PatrolHeatmapPanel';
import { ManualInsightMarkerTool } from './components/ManualInsightMarkerTool';
import { PatrolBalanceScoreCard } from './components/PatrolBalanceScoreCard';
import { PatrolTrendsGraph } from './components/PatrolTrendsGraph';

export default function PatrolInsightsPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Patrol Insights & Heatmap
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Officer coverage analysis and patrol balance monitoring
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
        >
          <TrendingUp className="h-4 w-4" />
          Refresh Analysis
        </button>
      </div>

      {/* Balance Score Cards */}
      <PatrolBalanceScoreCard refreshKey={refreshKey} />

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Heatmap - Takes 2 columns */}
        <div className="lg:col-span-2">
          <PatrolHeatmapPanel refreshKey={refreshKey} />
        </div>

        {/* Manual Marker Tool */}
        <div>
          <ManualInsightMarkerTool onMarkerAdded={handleRefresh} />
        </div>
      </div>

      {/* Trends Graph */}
      <PatrolTrendsGraph refreshKey={refreshKey} />
    </div>
  );
}
