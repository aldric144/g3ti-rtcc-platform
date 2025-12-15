'use client';

import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';

interface PatrolBalanceScoreCardProps {
  refreshKey: number;
}

export function PatrolBalanceScoreCard({ refreshKey }: PatrolBalanceScoreCardProps) {
  // Mock data - in production would come from API
  const metrics = {
    overallBalance: 0.72,
    overPoliced: 1,
    underPoliced: 2,
    balanced: 3,
    hourlyVisits: 156,
    dailyVisits: 2847,
  };

  const getBalanceColor = (balance: number) => {
    if (balance >= 0.7) return 'text-green-600';
    if (balance >= 0.5) return 'text-amber-600';
    return 'text-red-600';
  };

  const getBalanceLabel = (balance: number) => {
    if (balance >= 0.7) return 'Good';
    if (balance >= 0.5) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* Overall Balance */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Overall Balance
          </span>
          <CheckCircle className={`h-5 w-5 ${getBalanceColor(metrics.overallBalance)}`} />
        </div>
        <div className="mt-2">
          <span className={`text-3xl font-bold ${getBalanceColor(metrics.overallBalance)}`}>
            {Math.round(metrics.overallBalance * 100)}%
          </span>
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
            {getBalanceLabel(metrics.overallBalance)}
          </span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className={`h-full rounded-full ${
              metrics.overallBalance >= 0.7 ? 'bg-green-500' :
              metrics.overallBalance >= 0.5 ? 'bg-amber-500' : 'bg-red-500'
            }`}
            style={{ width: `${metrics.overallBalance * 100}%` }}
          />
        </div>
      </div>

      {/* Sector Status */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
          Sector Status
        </span>
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="h-2 w-2 rounded-full bg-red-500" />
              Over-policed
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{metrics.overPoliced}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="h-2 w-2 rounded-full bg-amber-500" />
              Under-policed
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{metrics.underPoliced}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              Balanced
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{metrics.balanced}</span>
          </div>
        </div>
      </div>

      {/* Hourly Visits */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Hourly Visits
          </span>
          <TrendingUp className="h-5 w-5 text-green-500" />
        </div>
        <div className="mt-2">
          <span className="text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.hourlyVisits}
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          +12% from last hour
        </p>
      </div>

      {/* Daily Visits */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Daily Visits
          </span>
          <TrendingDown className="h-5 w-5 text-amber-500" />
        </div>
        <div className="mt-2">
          <span className="text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.dailyVisits.toLocaleString()}
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          -3% from yesterday
        </p>
      </div>
    </div>
  );
}
