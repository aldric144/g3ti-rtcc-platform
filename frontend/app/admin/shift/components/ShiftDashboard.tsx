'use client';

import { useState, useEffect } from 'react';
import { Clock, Play, Square, Users, AlertTriangle } from 'lucide-react';

interface ShiftDashboardProps {
  onShiftChange: () => void;
  refreshKey: number;
}

export function ShiftDashboard({ onShiftChange, refreshKey }: ShiftDashboardProps) {
  const [isShiftActive, setIsShiftActive] = useState(true);
  const [shiftData, setShiftData] = useState({
    id: 'SHIFT-2025-001',
    supervisor: 'Sgt. Johnson',
    startTime: new Date(Date.now() - 4 * 60 * 60000),
    operatorCount: 4,
    majorEventCount: 2,
  });

  const [showOpenForm, setShowOpenForm] = useState(false);
  const [newSupervisor, setNewSupervisor] = useState('');

  const handleOpenShift = () => {
    if (!newSupervisor.trim()) return;
    
    setShiftData({
      id: `SHIFT-${Date.now()}`,
      supervisor: newSupervisor,
      startTime: new Date(),
      operatorCount: 0,
      majorEventCount: 0,
    });
    setIsShiftActive(true);
    setShowOpenForm(false);
    setNewSupervisor('');
    onShiftChange();
  };

  const getShiftDuration = () => {
    const diff = Date.now() - shiftData.startTime.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center justify-between mb-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
          <Clock className="h-5 w-5" />
          Current Shift
        </h2>
        {isShiftActive ? (
          <span className="flex items-center gap-2 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800 dark:bg-green-900/30 dark:text-green-400">
            <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
            Active
          </span>
        ) : (
          <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-400">
            No Active Shift
          </span>
        )}
      </div>

      {isShiftActive ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-700/50">
            <p className="text-sm text-gray-500 dark:text-gray-400">Shift ID</p>
            <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
              {shiftData.id}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-700/50">
            <p className="text-sm text-gray-500 dark:text-gray-400">Supervisor</p>
            <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
              {shiftData.supervisor}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-700/50">
            <p className="text-sm text-gray-500 dark:text-gray-400">Duration</p>
            <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
              {getShiftDuration()}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-700/50">
            <p className="text-sm text-gray-500 dark:text-gray-400">Personnel</p>
            <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
              {shiftData.operatorCount} operators
            </p>
          </div>
        </div>
      ) : showOpenForm ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Supervisor Name
            </label>
            <input
              type="text"
              value={newSupervisor}
              onChange={(e) => setNewSupervisor(e.target.value)}
              placeholder="Enter supervisor name"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowOpenForm(false)}
              className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handleOpenShift}
              className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
            >
              <Play className="h-4 w-4" />
              Open Shift
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Clock className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-gray-500 dark:text-gray-400">No shift is currently active</p>
          <button
            onClick={() => setShowOpenForm(true)}
            className="mt-4 flex items-center gap-2 mx-auto rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
          >
            <Play className="h-4 w-4" />
            Open New Shift
          </button>
        </div>
      )}
    </div>
  );
}
