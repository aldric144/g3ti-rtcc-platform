'use client';

import { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Camera,
  Car,
  FileText,
  MapPin,
  Target,
  Users,
} from 'lucide-react';
import { StatsCard } from '@/app/components/dashboard/StatsCard';
import { EventFeed } from '@/app/components/dashboard/EventFeed';
import { MiniMap } from '@/app/components/dashboard/MiniMap';
import { SystemStatus } from '@/app/components/dashboard/SystemStatus';

/**
 * Main dashboard page for the RTCC-UIP platform.
 * 
 * Displays:
 * - Key statistics cards
 * - Real-time event feed
 * - Mini map with recent events
 * - System status overview
 */
export default function DashboardPage() {
  const [stats, setStats] = useState({
    activeIncidents: 12,
    gunshotAlerts: 3,
    lprHits: 47,
    activeCameras: 156,
    openInvestigations: 89,
    officersOnDuty: 234,
  });

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Real-time overview of RTCC operations
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatsCard
          title="Active Incidents"
          value={stats.activeIncidents}
          icon={AlertTriangle}
          trend={{ value: 2, direction: 'up' }}
          color="red"
        />
        <StatsCard
          title="Gunshot Alerts"
          value={stats.gunshotAlerts}
          icon={Target}
          trend={{ value: 1, direction: 'down' }}
          color="orange"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="LPR Hits"
          value={stats.lprHits}
          icon={Car}
          trend={{ value: 12, direction: 'up' }}
          color="blue"
          subtitle="Last 24 hours"
        />
        <StatsCard
          title="Active Cameras"
          value={stats.activeCameras}
          icon={Camera}
          color="green"
          subtitle="Online"
        />
        <StatsCard
          title="Open Cases"
          value={stats.openInvestigations}
          icon={FileText}
          trend={{ value: 5, direction: 'up' }}
          color="purple"
        />
        <StatsCard
          title="Officers On Duty"
          value={stats.officersOnDuty}
          icon={Users}
          color="cyan"
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Event feed - takes 2 columns */}
        <div className="lg:col-span-2">
          <EventFeed />
        </div>

        {/* Right sidebar */}
        <div className="space-y-6">
          {/* Mini map */}
          <MiniMap />

          {/* System status */}
          <SystemStatus />
        </div>
      </div>
    </div>
  );
}
