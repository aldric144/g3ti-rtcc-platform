'use client';

import React, { useState, useEffect } from 'react';

interface WorkflowStatus {
  workflow_id: string;
  name: string;
  status: 'running' | 'pending' | 'completed' | 'failed' | 'paused';
  started_at?: string;
  completed_at?: string;
  triggered_by: string;
  current_step?: string;
  progress: number;
  steps_completed: number;
  steps_total: number;
  errors: string[];
  warnings: string[];
}

interface WorkflowHistory {
  execution_id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  success: boolean;
}

export default function WorkflowMonitor() {
  const [activeWorkflows, setActiveWorkflows] = useState<WorkflowStatus[]>([]);
  const [history, setHistory] = useState<WorkflowHistory[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowStatus | null>(null);
  const [filter, setFilter] = useState<'all' | 'running' | 'completed' | 'failed'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflowStatus();
    const interval = setInterval(fetchWorkflowStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflowStatus = async () => {
    try {
      const response = await fetch('/api/orchestration/status/active');
      if (response.ok) {
        const data = await response.json();
        setActiveWorkflows(data.active_executions?.map((exec: Record<string, unknown>) => ({
          workflow_id: exec.workflow_id,
          name: exec.name,
          status: exec.status || 'running',
          started_at: exec.started_at,
          triggered_by: exec.triggered_by || 'system',
          progress: 50,
          steps_completed: 2,
          steps_total: 5,
          errors: [],
          warnings: [],
        })) || []);
      }
    } catch (error) {
      console.error('Failed to fetch workflow status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'paused':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      running: 'bg-blue-900/50 text-blue-400 border-blue-500',
      completed: 'bg-green-900/50 text-green-400 border-green-500',
      failed: 'bg-red-900/50 text-red-400 border-red-500',
      pending: 'bg-yellow-900/50 text-yellow-400 border-yellow-500',
      paused: 'bg-orange-900/50 text-orange-400 border-orange-500',
    };
    return colors[status] || 'bg-gray-900/50 text-gray-400 border-gray-500';
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const filteredWorkflows = activeWorkflows.filter((wf) => {
    if (filter === 'all') return true;
    return wf.status === filter;
  });

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#c9a227]">Workflow Monitor</h2>
        <div className="flex items-center gap-4">
          <div className="flex bg-[#0a1628] rounded-lg p-1">
            {(['all', 'running', 'completed', 'failed'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  filter === f
                    ? 'bg-[#c9a227] text-[#0a1628]'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
          <button
            onClick={fetchWorkflowStatus}
            className="px-3 py-1 bg-[#c9a227] text-[#0a1628] rounded text-sm font-medium hover:bg-[#d9b237]"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-[#0a1628] rounded-lg p-4 border border-blue-500/30">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
            <span className="text-gray-400">Running</span>
          </div>
          <div className="text-3xl font-bold text-blue-400 mt-2">
            {activeWorkflows.filter((w) => w.status === 'running').length}
          </div>
        </div>
        <div className="bg-[#0a1628] rounded-lg p-4 border border-yellow-500/30">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-400">Pending</span>
          </div>
          <div className="text-3xl font-bold text-yellow-400 mt-2">
            {activeWorkflows.filter((w) => w.status === 'pending').length}
          </div>
        </div>
        <div className="bg-[#0a1628] rounded-lg p-4 border border-green-500/30">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-400">Completed</span>
          </div>
          <div className="text-3xl font-bold text-green-400 mt-2">
            {history.filter((h) => h.success).length}
          </div>
        </div>
        <div className="bg-[#0a1628] rounded-lg p-4 border border-red-500/30">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-400">Failed</span>
          </div>
          <div className="text-3xl font-bold text-red-400 mt-2">
            {activeWorkflows.filter((w) => w.status === 'failed').length}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Active Workflows</h3>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#c9a227]"></div>
              </div>
            ) : filteredWorkflows.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-4xl mb-2">📊</p>
                <p>No {filter === 'all' ? 'active' : filter} workflows</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {filteredWorkflows.map((workflow) => (
                  <div
                    key={workflow.workflow_id}
                    onClick={() => setSelectedWorkflow(workflow)}
                    className={`bg-[#1a2a4a] rounded-lg p-4 border cursor-pointer transition-colors ${
                      selectedWorkflow?.workflow_id === workflow.workflow_id
                        ? 'border-[#c9a227]'
                        : 'border-[#c9a227]/20 hover:border-[#c9a227]/50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(workflow.status)} ${workflow.status === 'running' ? 'animate-pulse' : ''}`}></div>
                        <span className="font-medium">{workflow.name}</span>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs border ${getStatusBadge(workflow.status)}`}>
                        {workflow.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="mb-3">
                      <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                        <span>Progress</span>
                        <span>{workflow.steps_completed}/{workflow.steps_total} steps</span>
                      </div>
                      <div className="h-2 bg-[#0a1628] rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 ${
                            workflow.status === 'failed' ? 'bg-red-500' :
                            workflow.status === 'completed' ? 'bg-green-500' : 'bg-[#c9a227]'
                          }`}
                          style={{ width: `${workflow.progress}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Triggered by: {workflow.triggered_by}</span>
                      {workflow.started_at && (
                        <span>Started: {new Date(workflow.started_at).toLocaleTimeString()}</span>
                      )}
                    </div>

                    {(workflow.errors.length > 0 || workflow.warnings.length > 0) && (
                      <div className="mt-3 pt-3 border-t border-[#c9a227]/10">
                        {workflow.errors.map((error, i) => (
                          <p key={i} className="text-xs text-red-400">⚠️ {error}</p>
                        ))}
                        {workflow.warnings.map((warning, i) => (
                          <p key={i} className="text-xs text-yellow-400">⚡ {warning}</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20 mb-4">
            <h3 className="text-lg font-semibold mb-4">Workflow Details</h3>
            
            {selectedWorkflow ? (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400">Workflow Name</label>
                  <p className="font-medium">{selectedWorkflow.name}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Workflow ID</label>
                  <p className="font-mono text-sm">{selectedWorkflow.workflow_id}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Status</label>
                  <p className={`font-medium ${
                    selectedWorkflow.status === 'completed' ? 'text-green-400' :
                    selectedWorkflow.status === 'running' ? 'text-blue-400' :
                    selectedWorkflow.status === 'failed' ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {selectedWorkflow.status.toUpperCase()}
                  </p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Current Step</label>
                  <p className="text-sm">{selectedWorkflow.current_step || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Progress</label>
                  <p className="font-medium">{selectedWorkflow.progress}% ({selectedWorkflow.steps_completed}/{selectedWorkflow.steps_total})</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Triggered By</label>
                  <p className="text-sm">{selectedWorkflow.triggered_by}</p>
                </div>
                
                <div className="flex gap-2 pt-4 border-t border-[#c9a227]/20">
                  <button className="flex-1 px-3 py-2 bg-yellow-600 text-white rounded text-sm font-medium hover:bg-yellow-700">
                    Pause
                  </button>
                  <button className="flex-1 px-3 py-2 bg-red-600 text-white rounded text-sm font-medium hover:bg-red-700">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>Select a workflow to view details</p>
              </div>
            )}
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Recent History</h3>
            {history.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-sm">No execution history</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[200px] overflow-y-auto">
                {history.map((item) => (
                  <div
                    key={item.execution_id}
                    className="bg-[#1a2a4a] rounded p-2 border border-[#c9a227]/10"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{item.workflow_name}</span>
                      <span className={`text-xs ${item.success ? 'text-green-400' : 'text-red-400'}`}>
                        {item.success ? '✓' : '✗'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                      <span>{formatDuration(item.duration_ms)}</span>
                      <span>{new Date(item.completed_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
