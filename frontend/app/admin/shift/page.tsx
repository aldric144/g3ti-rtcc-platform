'use client';

import { useState } from 'react';
import { Clock, Users, AlertTriangle, CheckCircle } from 'lucide-react';
import { ShiftDashboard } from './components/ShiftDashboard';
import { OperatorListPanel } from './components/OperatorListPanel';
import { MajorEventRecorder } from './components/MajorEventRecorder';
import { SupervisorSignoffPanel } from './components/SupervisorSignoffPanel';

export default function ShiftManagementPage() {
  const [currentShift, setCurrentShift] = useState<any>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleShiftChange = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Shift Management
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            RTCC Supervisor Tools - Shift lifecycle and personnel tracking
          </p>
        </div>
      </div>

      {/* Shift Dashboard */}
      <ShiftDashboard 
        onShiftChange={handleShiftChange} 
        refreshKey={refreshKey}
      />

      {/* Two Column Layout */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Operator List */}
        <OperatorListPanel refreshKey={refreshKey} />

        {/* Major Event Recorder */}
        <MajorEventRecorder refreshKey={refreshKey} />
      </div>

      {/* Supervisor Sign-off */}
      <SupervisorSignoffPanel 
        onSignoff={handleShiftChange}
        refreshKey={refreshKey}
      />
    </div>
  );
}
