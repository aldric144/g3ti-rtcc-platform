'use client';

import { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Camera, 
  Car, 
  FileText, 
  Users, 
  RefreshCw,
  Edit3,
  Save,
  X
} from 'lucide-react';
import { AdminOverviewPanel } from './components/AdminOverviewPanel';
import { AdminMetricsEditor } from './components/AdminMetricsEditor';
import { AdminEventFeed } from './components/AdminEventFeed';

export default function RTCCConsolePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const handleRefresh = () => {
    setLastRefresh(new Date());
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            RTCC Admin Console
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Real-Time Operations Management - Internal Only
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500">
            Last refresh: {lastRefresh.toLocaleTimeString()}
          </span>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
              isEditing
                ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400'
                : 'bg-rtcc-primary text-white hover:bg-rtcc-primary/90'
            }`}
          >
            {isEditing ? (
              <>
                <X className="h-4 w-4" />
                Cancel Edit
              </>
            ) : (
              <>
                <Edit3 className="h-4 w-4" />
                Edit Mode
              </>
            )}
          </button>
        </div>
      </div>

      {/* CJIS Warning Banner */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <span className="text-sm font-medium text-amber-800 dark:text-amber-200">
            CJIS-SECURE: This console contains Criminal Justice Information. All actions are logged.
          </span>
        </div>
      </div>

      {/* Overview Panel */}
      <AdminOverviewPanel isEditing={isEditing} refreshKey={lastRefresh.getTime()} />

      {/* Two Column Layout */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Metrics Editor */}
        <AdminMetricsEditor isEditing={isEditing} />

        {/* Event Feed */}
        <AdminEventFeed />
      </div>
    </div>
  );
}
