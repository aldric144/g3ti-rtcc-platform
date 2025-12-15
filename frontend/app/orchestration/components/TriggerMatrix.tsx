'use client';

import React, { useState, useEffect } from 'react';

interface Trigger {
  trigger_id: string;
  type: string;
  event_types: string[];
  event_sources: string[];
  conditions: Record<string, unknown>;
}

interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  category: string;
  priority: number;
  enabled: boolean;
  triggers: Trigger[];
  steps_count: number;
  guardrails: string[];
}

interface TriggerActivation {
  id: string;
  trigger_id: string;
  workflow_name: string;
  event_type: string;
  source: string;
  timestamp: string;
  matched_conditions: string[];
}

export default function TriggerMatrix() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [activations, setActivations] = useState<TriggerActivation[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('/api/orchestration/workflows');
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data.workflows || []);
      }
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(workflows.map((w) => w.category))];

  const filteredWorkflows = workflows.filter((workflow) => {
    const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
    const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'text-red-400 bg-red-900/30';
      case 2:
        return 'text-orange-400 bg-orange-900/30';
      case 3:
        return 'text-yellow-400 bg-yellow-900/30';
      case 4:
        return 'text-blue-400 bg-blue-900/30';
      default:
        return 'text-gray-400 bg-gray-900/30';
    }
  };

  const getPriorityLabel = (priority: number) => {
    switch (priority) {
      case 1:
        return 'CRITICAL';
      case 2:
        return 'HIGH';
      case 3:
        return 'MEDIUM';
      case 4:
        return 'LOW';
      default:
        return 'INFO';
    }
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      critical_incident: '🚨',
      officer_safety: '👮',
      vehicle_crime: '🚗',
      crisis_response: '🆘',
      search_rescue: '🔍',
      emergency_management: '🏥',
      cyber_security: '🔒',
      public_order: '👥',
      missing_child: '👶',
      national_security: '🛡️',
      narcotics: '💊',
      gang_violence: '⚠️',
      crisis_intervention: '🧠',
      traffic_investigation: '🚦',
      domestic_violence: '🏠',
      vehicle_pursuit: '🚔',
    };
    return icons[category] || '📋';
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#c9a227]">Trigger Matrix</h2>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#c9a227]"
          />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg text-white focus:outline-none focus:border-[#c9a227]"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Workflow Triggers ({filteredWorkflows.length})</h3>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#c9a227]"></div>
              </div>
            ) : filteredWorkflows.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p>No workflows found</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {filteredWorkflows.map((workflow) => (
                  <div
                    key={workflow.workflow_id}
                    className="bg-[#1a2a4a] rounded-lg p-4 border border-[#c9a227]/20 hover:border-[#c9a227]/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{getCategoryIcon(workflow.category)}</span>
                        <div>
                          <h4 className="font-medium text-white">{workflow.name}</h4>
                          <p className="text-sm text-gray-400">{workflow.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(workflow.priority)}`}>
                          {getPriorityLabel(workflow.priority)}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${workflow.enabled ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                          {workflow.enabled ? 'ENABLED' : 'DISABLED'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mt-3">
                      <div>
                        <label className="text-xs text-gray-500">Trigger Events</label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {workflow.triggers.flatMap((t) => t.event_types).slice(0, 5).map((event, i) => (
                            <span key={i} className="px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded text-xs">
                              {event}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs text-gray-500">Guardrails</label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {workflow.guardrails.slice(0, 3).map((guardrail, i) => (
                            <span key={i} className="px-2 py-0.5 bg-purple-900/30 text-purple-400 rounded text-xs">
                              {guardrail}
                            </span>
                          ))}
                          {workflow.guardrails.length > 3 && (
                            <span className="px-2 py-0.5 bg-gray-900/30 text-gray-400 rounded text-xs">
                              +{workflow.guardrails.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#c9a227]/10">
                      <span className="text-xs text-gray-500">
                        {workflow.steps_count} steps | Category: {workflow.category.replace(/_/g, ' ')}
                      </span>
                      <button className="text-xs text-[#c9a227] hover:underline">
                        View Details →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20 mb-4">
            <h3 className="text-lg font-semibold mb-4">Trigger Statistics</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Workflows</span>
                <span className="font-bold text-[#c9a227]">{workflows.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Enabled</span>
                <span className="font-bold text-green-400">
                  {workflows.filter((w) => w.enabled).length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Critical Priority</span>
                <span className="font-bold text-red-400">
                  {workflows.filter((w) => w.priority === 1).length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Categories</span>
                <span className="font-bold text-blue-400">{categories.length - 1}</span>
              </div>
            </div>
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Recent Activations</h3>
            {activations.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-2xl mb-2">🎯</p>
                <p className="text-sm">No recent trigger activations</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {activations.map((activation) => (
                  <div
                    key={activation.id}
                    className="bg-[#1a2a4a] rounded p-3 border border-[#c9a227]/10"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{activation.workflow_name}</span>
                      <span className="text-xs text-gray-400">
                        {new Date(activation.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Triggered by: {activation.event_type}
                    </p>
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
