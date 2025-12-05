'use client';

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { clsx } from 'clsx';

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  color?: 'red' | 'orange' | 'blue' | 'green' | 'purple' | 'cyan';
  subtitle?: string;
}

const colorClasses = {
  red: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  cyan: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
};

/**
 * Statistics card component for dashboard metrics.
 */
export function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
  color = 'blue',
  subtitle,
}: StatsCardProps) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className={clsx('rounded-lg p-2', colorClasses[color])}>
          <Icon className="h-5 w-5" />
        </div>
        
        {trend && (
          <div
            className={clsx(
              'flex items-center gap-1 text-xs font-medium',
              trend.direction === 'up' ? 'text-red-500' : 'text-green-500'
            )}
          >
            {trend.direction === 'up' ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingDown className="h-3 w-3" />
            )}
            {trend.value}
          </div>
        )}
      </div>
      
      <div className="mt-3">
        <p className="text-2xl font-bold text-gray-900 dark:text-white">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
        {subtitle && (
          <p className="text-xs text-gray-500 dark:text-gray-500">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
