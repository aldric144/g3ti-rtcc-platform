'use client';

import React, { useState, useEffect, useRef } from 'react';

interface TimelineEvent {
  id: string;
  type: string;
  workflow_name?: string;
  step_name?: string;
  status: string;
  timestamp: string;
  duration_ms?: number;
  details?: Record<string, unknown>;
}

interface WorkflowExecution {
  execution_id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  steps: {
    step_id: string;
    name: string;
    status: string;
    started_at?: string;
    completed_at?: string;
    duration_ms?: number;
  }[];
  progress: number;
}

export default function OrchestrationTimeline() {
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const timelineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchActiveExecutions();
    const interval = setInterval(fetchActiveExecutions, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (autoScroll && timelineRef.current) {
      timelineRef.current.scrollTop = timelineRef.current.scrollHeight;
    }
  }, [events, autoScroll]);

  const fetchActiveExecutions = async () => {
    try {
      const response = await fetch('/api/orchestration/status/active');
      if (response.ok) {
        const data = await response.json();
        const mockExecutions: WorkflowExecution[] = data.active_executions?.map((exec: Record<string, unknown>, index: number) => ({
          execution_id: exec.workflow_id || `exec-${index}`,
          workflow_name: exec.name || 'Unknown Workflow',
          status: exec.status || 'running',
          started_at: exec.started_at || new Date().toISOString(),
          steps: [
            { step_id: 'step-1', name: 'Initialize', status: 'completed', duration_ms: 150 },
            { step_id: 'step-2', name: 'Process', status: 'running', duration_ms: 0 },
            { step_id: 'step-3', name: 'Finalize', status: 'pending', duration_ms: 0 },
          ],
          progress: 50,
        })) || [];
        setExecutions(mockExecutions);
      }
    } catch (error) {
      console.error('Failed to fetch active executions:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-green-500';
      case 'running':
      case 'in_progress':
        return 'bg-blue-500 animate-pulse';
      case 'failed':
      case 'error':
        return 'bg-red-500';
      case 'pending':
      case 'queued':
        return 'bg-gray-500';
      case 'paused':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return '✓';
      case 'running':
      case 'in_progress':
        return '⟳';
      case 'failed':
      case 'error':
        return '✗';
      case 'pending':
      case 'queued':
        return '○';
      case 'paused':
        return '⏸';
      default:
        return '?';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#c9a227]">Orchestration Timeline</h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            Auto-scroll
          </label>
          <button
            onClick={fetchActiveExecutions}
            className="px-3 py-1 bg-[#c9a227] text-[#0a1628] rounded text-sm font-medium hover:bg-[#d9b237]"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Active Workflow Executions</h3>
            
            {executions.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-4xl mb-2">⏱️</p>
                <p>No active workflow executions</p>
                <p className="text-sm mt-2">Workflows will appear here when triggered</p>
              </div>
            ) : (
              <div className="space-y-4">
                {executions.map((execution) => (
                  <div
                    key={execution.execution_id}
                    className={`bg-[#1a2a4a] rounded-lg p-4 border cursor-pointer transition-colors ${
                      selectedExecution?.execution_id === execution.execution_id
                        ? 'border-[#c9a227]'
                        : 'border-[#c9a227]/20 hover:border-[#c9a227]/50'
                    }`}
                    onClick={() => setSelectedExecution(execution)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(execution.status)}`}></div>
                        <span className="font-medium">{execution.workflow_name}</span>
                      </div>
                      <span className="text-sm text-gray-400">
                        Started: {formatTime(execution.started_at)}
                      </span>
                    </div>

                    <div className="relative h-2 bg-[#0a1628] rounded-full overflow-hidden mb-3">
                      <div
                        className="absolute left-0 top-0 h-full bg-[#c9a227] transition-all duration-500"
                        style={{ width: `${execution.progress}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center gap-2">
                      {execution.steps.map((step, index) => (
                        <React.Fragment key={step.step_id}>
                          <div
                            className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                              step.status === 'completed'
                                ? 'bg-green-900/50 text-green-400'
                                : step.status === 'running'
                                ? 'bg-blue-900/50 text-blue-400'
                                : 'bg-gray-900/50 text-gray-400'
                            }`}
                          >
                            <span>{getStatusIcon(step.status)}</span>
                            <span>{step.name}</span>
                            {(step.duration_ms ?? 0) > 0 && (
                              <span className="text-gray-500">({formatDuration(step.duration_ms!)})</span>
                            )}
                          </div>
                          {index < execution.steps.length - 1 && (
                            <span className="text-gray-600">→</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20 mt-4">
            <h3 className="text-lg font-semibold mb-4">Timeline Animation</h3>
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-[#c9a227]/30"></div>
              <div ref={timelineRef} className="space-y-4 max-h-[300px] overflow-y-auto pl-8">
                {events.length === 0 ? (
                  <div className="text-gray-400 text-sm py-4">
                    Timeline events will appear here as workflows execute...
                  </div>
                ) : (
                  events.map((event) => (
                    <div key={event.id} className="relative">
                      <div className={`absolute -left-6 w-3 h-3 rounded-full ${getStatusColor(event.status)}`}></div>
                      <div className="bg-[#1a2a4a] rounded p-3">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{event.type}</span>
                          <span className="text-xs text-gray-400">{formatTime(event.timestamp)}</span>
                        </div>
                        {event.workflow_name && (
                          <p className="text-sm text-gray-400">{event.workflow_name}</p>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Execution Details</h3>
            
            {selectedExecution ? (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400">Workflow</label>
                  <p className="font-medium">{selectedExecution.workflow_name}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Execution ID</label>
                  <p className="font-mono text-sm">{selectedExecution.execution_id}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Status</label>
                  <p className={`font-medium ${
                    selectedExecution.status === 'completed' ? 'text-green-400' :
                    selectedExecution.status === 'running' ? 'text-blue-400' :
                    selectedExecution.status === 'failed' ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {selectedExecution.status.toUpperCase()}
                  </p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Progress</label>
                  <p className="font-medium">{selectedExecution.progress}%</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Started At</label>
                  <p className="text-sm">{new Date(selectedExecution.started_at).toLocaleString()}</p>
                </div>
                
                <div className="border-t border-[#c9a227]/20 pt-4">
                  <label className="text-xs text-gray-400">Steps</label>
                  <div className="space-y-2 mt-2">
                    {selectedExecution.steps.map((step) => (
                      <div
                        key={step.step_id}
                        className="flex items-center justify-between bg-[#1a2a4a] rounded p-2"
                      >
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${getStatusColor(step.status)}`}></span>
                          <span className="text-sm">{step.name}</span>
                        </div>
                        {(step.duration_ms ?? 0) > 0 && (
                          <span className="text-xs text-gray-400">{formatDuration(step.duration_ms!)}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>Select an execution to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
