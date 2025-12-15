'use client';

import React, { useState, useEffect } from 'react';
import OrchestrationTimeline from './components/OrchestrationTimeline';
import TriggerMatrix from './components/TriggerMatrix';
import WorkflowMonitor from './components/WorkflowMonitor';
import UnifiedEventStream from './components/UnifiedEventStream';
import WorkflowBuilder from './components/WorkflowBuilder';

interface OrchestrationStatus {
  status: string;
  kernel: {
    total_actions_executed: number;
    total_workflows_completed: number;
    actions_in_queue: number;
  };
  event_router: {
    total_events_routed: number;
    active_rules: number;
  };
  workflow_engine: {
    active_executions: number;
    total_executions: number;
  };
  policy_engine: {
    total_checks: number;
    violations_blocked: number;
  };
  resource_manager: {
    total_resources: number;
    active_allocations: number;
  };
  event_bus: {
    total_events_received: number;
    total_events_fused: number;
  };
  available_workflows: number;
}

export default function OrchestrationControlCenter() {
  const [activeTab, setActiveTab] = useState<'timeline' | 'triggers' | 'monitor' | 'events' | 'builder'>('timeline');
  const [status, setStatus] = useState<OrchestrationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [kernelRunning, setKernelRunning] = useState(false);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/orchestration/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        setKernelRunning(data.status === 'running');
      }
    } catch (error) {
      console.error('Failed to fetch orchestration status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKernelToggle = async () => {
    try {
      const endpoint = kernelRunning ? '/api/orchestration/kernel/stop' : '/api/orchestration/kernel/start';
      await fetch(endpoint, { method: 'POST' });
      await fetchStatus();
    } catch (error) {
      console.error('Failed to toggle kernel:', error);
    }
  };

  const tabs = [
    { id: 'timeline', label: 'Orchestration Timeline', icon: '⏱️' },
    { id: 'triggers', label: 'Trigger Matrix', icon: '🎯' },
    { id: 'monitor', label: 'Workflow Monitor', icon: '📊' },
    { id: 'events', label: 'Event Stream', icon: '📡' },
    { id: 'builder', label: 'Workflow Builder', icon: '🔧' },
  ];

  return (
    <div className="min-h-screen bg-[#0a1628] text-white p-6">
      <div className="max-w-[1920px] mx-auto">
        <header className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-[#c9a227]">
                System-Wide Orchestration Engine
              </h1>
              <p className="text-gray-400 mt-1">
                Phase 38: Unified Intelligence Fabric - The Brainstem of the RTCC Platform
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className={`px-4 py-2 rounded-lg ${kernelRunning ? 'bg-green-900/50 border border-green-500' : 'bg-red-900/50 border border-red-500'}`}>
                <span className="text-sm">Kernel Status: </span>
                <span className={`font-bold ${kernelRunning ? 'text-green-400' : 'text-red-400'}`}>
                  {status?.status?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              <button
                onClick={handleKernelToggle}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  kernelRunning
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {kernelRunning ? 'Stop Kernel' : 'Start Kernel'}
              </button>
            </div>
          </div>
        </header>

        {status && (
          <div className="grid grid-cols-6 gap-4 mb-6">
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-[#c9a227]">
                {status.available_workflows}
              </div>
              <div className="text-sm text-gray-400">Available Workflows</div>
            </div>
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-green-400">
                {status.workflow_engine?.active_executions || 0}
              </div>
              <div className="text-sm text-gray-400">Active Executions</div>
            </div>
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-blue-400">
                {status.event_bus?.total_events_received || 0}
              </div>
              <div className="text-sm text-gray-400">Events Received</div>
            </div>
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-purple-400">
                {status.event_bus?.total_events_fused || 0}
              </div>
              <div className="text-sm text-gray-400">Events Fused</div>
            </div>
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-yellow-400">
                {status.resource_manager?.active_allocations || 0}
              </div>
              <div className="text-sm text-gray-400">Active Allocations</div>
            </div>
            <div className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/30">
              <div className="text-2xl font-bold text-red-400">
                {status.policy_engine?.violations_blocked || 0}
              </div>
              <div className="text-sm text-gray-400">Violations Blocked</div>
            </div>
          </div>
        )}

        <div className="flex gap-2 mb-6 border-b border-[#c9a227]/30 pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-[#c9a227] text-[#0a1628]'
                  : 'bg-[#1a2a4a] text-gray-300 hover:bg-[#2a3a5a]'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="bg-[#1a2a4a] rounded-lg border border-[#c9a227]/30 min-h-[600px]">
          {loading ? (
            <div className="flex items-center justify-center h-[600px]">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#c9a227]"></div>
            </div>
          ) : (
            <>
              {activeTab === 'timeline' && <OrchestrationTimeline />}
              {activeTab === 'triggers' && <TriggerMatrix />}
              {activeTab === 'monitor' && <WorkflowMonitor />}
              {activeTab === 'events' && <UnifiedEventStream />}
              {activeTab === 'builder' && <WorkflowBuilder />}
            </>
          )}
        </div>

        <footer className="mt-6 text-center text-gray-500 text-sm">
          <p>G3TI RTCC-UIP | Phase 38: System-Wide Orchestration Engine</p>
          <p>Riviera Beach, Florida 33404</p>
        </footer>
      </div>
    </div>
  );
}
