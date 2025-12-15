'use client';

import { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Camera, 
  Car, 
  FileText, 
  Users,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  trend?: number;
  isEditing: boolean;
  onValueChange?: (value: number) => void;
  color: string;
}

function MetricCard({ title, value, icon, trend, isEditing, onValueChange, color }: MetricCardProps) {
  const [editValue, setEditValue] = useState(value);

  useEffect(() => {
    setEditValue(value);
  }, [value]);

  const handleSave = () => {
    onValueChange?.(editValue);
  };

  return (
    <div className={`rounded-xl border p-4 ${color}`}>
      <div className="flex items-center justify-between">
        <div className="rounded-lg bg-white/20 p-2">
          {icon}
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 text-xs ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="mt-3">
        {isEditing ? (
          <input
            type="number"
            value={editValue}
            onChange={(e) => setEditValue(parseInt(e.target.value) || 0)}
            onBlur={handleSave}
            className="w-full rounded border bg-white/50 px-2 py-1 text-2xl font-bold"
          />
        ) : (
          <div className="text-2xl font-bold text-gray-900">{value}</div>
        )}
        <div className="text-sm text-gray-600">{title}</div>
      </div>
    </div>
  );
}

interface AdminOverviewPanelProps {
  isEditing: boolean;
  refreshKey: number;
}

export function AdminOverviewPanel({ isEditing, refreshKey }: AdminOverviewPanelProps) {
  const [metrics, setMetrics] = useState({
    activeIncidents: 12,
    gunshotAlerts: 3,
    lprHits: 47,
    activeCameras: 156,
    openCases: 89,
    officersOnDuty: 234,
  });

  const updateMetric = (key: keyof typeof metrics, value: number) => {
    setMetrics(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
        Operations Overview
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <MetricCard
          title="Active Incidents"
          value={metrics.activeIncidents}
          icon={<Activity className="h-5 w-5 text-red-600" />}
          trend={8}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('activeIncidents', v)}
          color="bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800"
        />
        <MetricCard
          title="Gunshot Alerts (24h)"
          value={metrics.gunshotAlerts}
          icon={<AlertTriangle className="h-5 w-5 text-orange-600" />}
          trend={-15}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('gunshotAlerts', v)}
          color="bg-orange-50 border-orange-200 dark:bg-orange-900/20 dark:border-orange-800"
        />
        <MetricCard
          title="LPR Hits (24h)"
          value={metrics.lprHits}
          icon={<Car className="h-5 w-5 text-blue-600" />}
          trend={12}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('lprHits', v)}
          color="bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800"
        />
        <MetricCard
          title="Active Cameras"
          value={metrics.activeCameras}
          icon={<Camera className="h-5 w-5 text-green-600" />}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('activeCameras', v)}
          color="bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800"
        />
        <MetricCard
          title="Open Cases"
          value={metrics.openCases}
          icon={<FileText className="h-5 w-5 text-purple-600" />}
          trend={5}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('openCases', v)}
          color="bg-purple-50 border-purple-200 dark:bg-purple-900/20 dark:border-purple-800"
        />
        <MetricCard
          title="Officers On Duty"
          value={metrics.officersOnDuty}
          icon={<Users className="h-5 w-5 text-indigo-600" />}
          isEditing={isEditing}
          onValueChange={(v) => updateMetric('officersOnDuty', v)}
          color="bg-indigo-50 border-indigo-200 dark:bg-indigo-900/20 dark:border-indigo-800"
        />
      </div>
    </div>
  );
}
