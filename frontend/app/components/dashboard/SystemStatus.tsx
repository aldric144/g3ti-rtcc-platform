'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { clsx } from 'clsx';

interface SystemComponent {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  message?: string;
}

/**
 * System status component showing health of all services.
 */
export function SystemStatus() {
  const [components, setComponents] = useState<SystemComponent[]>([
    { name: 'API Server', status: 'healthy' },
    { name: 'Neo4j Database', status: 'healthy' },
    { name: 'Elasticsearch', status: 'healthy' },
    { name: 'Redis Cache', status: 'healthy' },
    { name: 'ShotSpotter', status: 'degraded', message: 'High latency' },
    { name: 'Flock LPR', status: 'healthy' },
    { name: 'Milestone VMS', status: 'healthy' },
  ]);

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Placeholder - would call health check API
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const getStatusIcon = (status: SystemComponent['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const healthyCount = components.filter((c) => c.status === 'healthy').length;
  const totalCount = components.length;

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          System Status
        </h2>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="rounded-lg p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <RefreshCw
            className={clsx('h-4 w-4', isRefreshing && 'animate-spin')}
          />
        </button>
      </div>

      {/* Overall status */}
      <div className="mb-4 rounded-lg bg-gray-50 p-3 dark:bg-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Overall Health
          </span>
          <span
            className={clsx(
              'text-sm font-medium',
              healthyCount === totalCount
                ? 'text-green-600'
                : healthyCount >= totalCount - 1
                ? 'text-yellow-600'
                : 'text-red-600'
            )}
          >
            {healthyCount}/{totalCount} Operational
          </span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-600">
          <div
            className={clsx(
              'h-full rounded-full transition-all',
              healthyCount === totalCount
                ? 'bg-green-500'
                : healthyCount >= totalCount - 1
                ? 'bg-yellow-500'
                : 'bg-red-500'
            )}
            style={{ width: `${(healthyCount / totalCount) * 100}%` }}
          />
        </div>
      </div>

      {/* Component list */}
      <div className="space-y-2">
        {components.map((component) => (
          <div
            key={component.name}
            className="flex items-center justify-between py-1"
          >
            <div className="flex items-center gap-2">
              {getStatusIcon(component.status)}
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {component.name}
              </span>
            </div>
            {component.message && (
              <span className="text-xs text-gray-500">{component.message}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
