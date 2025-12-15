'use client';

import { useState } from 'react';
import { Save, RotateCcw } from 'lucide-react';

interface AdminMetricsEditorProps {
  isEditing: boolean;
}

export function AdminMetricsEditor({ isEditing }: AdminMetricsEditorProps) {
  const [metrics, setMetrics] = useState({
    shiftTotal: 24,
    caseCount: 156,
    rtccWorkload: 78,
    queueLength: 12,
    avgResponseTime: 4.5,
    callsHandled: 89,
  });

  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (key: keyof typeof metrics, value: string) => {
    const numValue = parseFloat(value) || 0;
    setMetrics(prev => ({ ...prev, [key]: numValue }));
    setHasChanges(true);
  };

  const handleSave = () => {
    // In production, this would call the API
    console.log('Saving metrics:', metrics);
    setHasChanges(false);
  };

  const handleReset = () => {
    setMetrics({
      shiftTotal: 24,
      caseCount: 156,
      rtccWorkload: 78,
      queueLength: 12,
      avgResponseTime: 4.5,
      callsHandled: 89,
    });
    setHasChanges(false);
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Metrics Editor
        </h2>
        {isEditing && hasChanges && (
          <div className="flex gap-2">
            <button
              onClick={handleReset}
              className="flex items-center gap-1 rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-1 rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
            >
              <Save className="h-4 w-4" />
              Save
            </button>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Shift Total (Personnel)
            </label>
            <input
              type="number"
              value={metrics.shiftTotal}
              onChange={(e) => handleChange('shiftTotal', e.target.value)}
              disabled={!isEditing}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Case Count
            </label>
            <input
              type="number"
              value={metrics.caseCount}
              onChange={(e) => handleChange('caseCount', e.target.value)}
              disabled={!isEditing}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              RTCC Workload (%)
            </label>
            <input
              type="number"
              value={metrics.rtccWorkload}
              onChange={(e) => handleChange('rtccWorkload', e.target.value)}
              disabled={!isEditing}
              min={0}
              max={100}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Queue Length
            </label>
            <input
              type="number"
              value={metrics.queueLength}
              onChange={(e) => handleChange('queueLength', e.target.value)}
              disabled={!isEditing}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Avg Response Time (min)
            </label>
            <input
              type="number"
              step="0.1"
              value={metrics.avgResponseTime}
              onChange={(e) => handleChange('avgResponseTime', e.target.value)}
              disabled={!isEditing}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Calls Handled (Today)
            </label>
            <input
              type="number"
              value={metrics.callsHandled}
              onChange={(e) => handleChange('callsHandled', e.target.value)}
              disabled={!isEditing}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:disabled:bg-gray-800"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
