'use client';

import React, { useState } from 'react';

interface WorkflowStep {
  id: string;
  name: string;
  action_type: string;
  target_subsystem: string;
  execution_mode: 'sequential' | 'parallel';
  timeout_seconds: number;
  guardrails: string[];
}

interface WorkflowDraft {
  name: string;
  description: string;
  category: string;
  priority: number;
  triggers: string[];
  steps: WorkflowStep[];
  guardrails: string[];
  legal_guardrails: string[];
  ethical_guardrails: string[];
}

const SUBSYSTEMS = [
  'dispatch', 'drone_ops', 'robotics', 'officer_safety', 'tactical_analytics',
  'threat_intel', 'investigations', 'digital_twin', 'predictive_intel',
  'human_stability', 'emergency_mgmt', 'fusion_cloud', 'cyber_intel',
  'public_guardian', 'compliance', 'communications', 'lpr_network',
  'cctv_network', 'traffic_system', 'sensor_grid',
];

const ACTION_TYPES = [
  'drone_dispatch', 'robot_dispatch', 'patrol_reroute', 'officer_alert',
  'emergency_broadcast', 'investigation_create', 'investigation_update',
  'threat_assessment', 'sensor_activate', 'notification_send',
  'resource_allocate', 'lockdown_initiate', 'bolo_issue', 'audit_log',
  'human_stability_alert', 'fusion_cloud_sync', 'co_responder_dispatch',
  'supervisor_alert', 'case_generation', 'evidence_collection',
  'tactical_analysis', 'predictive_alert', 'policy_validation',
];

const GUARDRAILS = [
  'constitutional_compliance', 'use_of_force_policy', 'privacy_protection',
  'officer_safety_priority', 'de_escalation_priority', 'bias_detection',
  'civil_rights_compliance', 'data_accuracy', 'audit_completeness',
  'emergency_protocol', 'notification_protocol', 'evidence_preservation',
];

export default function WorkflowBuilder() {
  const [draft, setDraft] = useState<WorkflowDraft>({
    name: '',
    description: '',
    category: 'custom',
    priority: 3,
    triggers: [],
    steps: [],
    guardrails: [],
    legal_guardrails: [],
    ethical_guardrails: [],
  });
  const [newTrigger, setNewTrigger] = useState('');
  const [showStepModal, setShowStepModal] = useState(false);
  const [editingStep, setEditingStep] = useState<WorkflowStep | null>(null);

  const addTrigger = () => {
    if (newTrigger && !draft.triggers.includes(newTrigger)) {
      setDraft({ ...draft, triggers: [...draft.triggers, newTrigger] });
      setNewTrigger('');
    }
  };

  const removeTrigger = (trigger: string) => {
    setDraft({ ...draft, triggers: draft.triggers.filter((t) => t !== trigger) });
  };

  const addStep = (step: WorkflowStep) => {
    setDraft({ ...draft, steps: [...draft.steps, step] });
    setShowStepModal(false);
    setEditingStep(null);
  };

  const removeStep = (stepId: string) => {
    setDraft({ ...draft, steps: draft.steps.filter((s) => s.id !== stepId) });
  };

  const moveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...draft.steps];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex >= 0 && newIndex < newSteps.length) {
      [newSteps[index], newSteps[newIndex]] = [newSteps[newIndex], newSteps[index]];
      setDraft({ ...draft, steps: newSteps });
    }
  };

  const toggleGuardrail = (guardrail: string) => {
    const guardrails = draft.guardrails.includes(guardrail)
      ? draft.guardrails.filter((g) => g !== guardrail)
      : [...draft.guardrails, guardrail];
    setDraft({ ...draft, guardrails });
  };

  const handleSave = async () => {
    console.log('Saving workflow draft:', draft);
    alert('Workflow Builder is a Phase-ready stub. Full implementation coming in future phases.');
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-[#c9a227]">Workflow Builder</h2>
          <p className="text-sm text-gray-400 mt-1">
            Phase-ready stub for drag-and-drop workflow designer
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setDraft({
              name: '',
              description: '',
              category: 'custom',
              priority: 3,
              triggers: [],
              steps: [],
              guardrails: [],
              legal_guardrails: [],
              ethical_guardrails: [],
            })}
            className="px-3 py-2 bg-gray-600 text-white rounded text-sm font-medium hover:bg-gray-700"
          >
            Clear
          </button>
          <button
            onClick={handleSave}
            className="px-3 py-2 bg-[#c9a227] text-[#0a1628] rounded text-sm font-medium hover:bg-[#d9b237]"
          >
            Save Workflow
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Workflow Name</label>
                <input
                  type="text"
                  value={draft.name}
                  onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                  placeholder="Enter workflow name"
                  className="w-full px-3 py-2 bg-[#1a2a4a] border border-[#c9a227]/30 rounded text-white placeholder-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Category</label>
                <select
                  value={draft.category}
                  onChange={(e) => setDraft({ ...draft, category: e.target.value })}
                  className="w-full px-3 py-2 bg-[#1a2a4a] border border-[#c9a227]/30 rounded text-white"
                >
                  <option value="custom">Custom</option>
                  <option value="critical_incident">Critical Incident</option>
                  <option value="officer_safety">Officer Safety</option>
                  <option value="emergency_management">Emergency Management</option>
                  <option value="crisis_response">Crisis Response</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea
                  value={draft.description}
                  onChange={(e) => setDraft({ ...draft, description: e.target.value })}
                  placeholder="Describe what this workflow does"
                  rows={2}
                  className="w-full px-3 py-2 bg-[#1a2a4a] border border-[#c9a227]/30 rounded text-white placeholder-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Priority</label>
                <select
                  value={draft.priority}
                  onChange={(e) => setDraft({ ...draft, priority: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 bg-[#1a2a4a] border border-[#c9a227]/30 rounded text-white"
                >
                  <option value={1}>Critical (1)</option>
                  <option value={2}>High (2)</option>
                  <option value={3}>Medium (3)</option>
                  <option value={4}>Low (4)</option>
                  <option value={5}>Info (5)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Triggers</h3>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={newTrigger}
                onChange={(e) => setNewTrigger(e.target.value)}
                placeholder="Enter trigger event type"
                className="flex-1 px-3 py-2 bg-[#1a2a4a] border border-[#c9a227]/30 rounded text-white placeholder-gray-500"
                onKeyPress={(e) => e.key === 'Enter' && addTrigger()}
              />
              <button
                onClick={addTrigger}
                className="px-4 py-2 bg-[#c9a227] text-[#0a1628] rounded font-medium hover:bg-[#d9b237]"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {draft.triggers.map((trigger) => (
                <span
                  key={trigger}
                  className="px-3 py-1 bg-blue-900/30 text-blue-400 rounded-full text-sm flex items-center gap-2"
                >
                  {trigger}
                  <button
                    onClick={() => removeTrigger(trigger)}
                    className="text-blue-300 hover:text-white"
                  >
                    ×
                  </button>
                </span>
              ))}
              {draft.triggers.length === 0 && (
                <span className="text-gray-500 text-sm">No triggers defined</span>
              )}
            </div>
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Workflow Steps</h3>
              <button
                onClick={() => {
                  setEditingStep({
                    id: `step-${Date.now()}`,
                    name: '',
                    action_type: ACTION_TYPES[0],
                    target_subsystem: SUBSYSTEMS[0],
                    execution_mode: 'sequential',
                    timeout_seconds: 30,
                    guardrails: [],
                  });
                  setShowStepModal(true);
                }}
                className="px-3 py-1 bg-[#c9a227] text-[#0a1628] rounded text-sm font-medium hover:bg-[#d9b237]"
              >
                + Add Step
              </button>
            </div>

            {draft.steps.length === 0 ? (
              <div className="text-center py-8 text-gray-400 border-2 border-dashed border-[#c9a227]/20 rounded-lg">
                <p className="text-2xl mb-2">🔧</p>
                <p>No steps defined</p>
                <p className="text-sm mt-1">Click "Add Step" to create workflow steps</p>
              </div>
            ) : (
              <div className="space-y-2">
                {draft.steps.map((step, index) => (
                  <div
                    key={step.id}
                    className="bg-[#1a2a4a] rounded-lg p-3 border border-[#c9a227]/20 flex items-center gap-3"
                  >
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => moveStep(index, 'up')}
                        disabled={index === 0}
                        className="text-gray-400 hover:text-white disabled:opacity-30"
                      >
                        ▲
                      </button>
                      <button
                        onClick={() => moveStep(index, 'down')}
                        disabled={index === draft.steps.length - 1}
                        className="text-gray-400 hover:text-white disabled:opacity-30"
                      >
                        ▼
                      </button>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-[#c9a227] text-[#0a1628] flex items-center justify-center font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{step.name || 'Unnamed Step'}</div>
                      <div className="text-sm text-gray-400">
                        {step.action_type} → {step.target_subsystem}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${
                      step.execution_mode === 'parallel'
                        ? 'bg-purple-900/30 text-purple-400'
                        : 'bg-blue-900/30 text-blue-400'
                    }`}>
                      {step.execution_mode.toUpperCase()}
                    </span>
                    <button
                      onClick={() => removeStep(step.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20 mb-4">
            <h3 className="text-lg font-semibold mb-4">Guardrails</h3>
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {GUARDRAILS.map((guardrail) => (
                <label
                  key={guardrail}
                  className="flex items-center gap-2 p-2 bg-[#1a2a4a] rounded cursor-pointer hover:bg-[#2a3a5a]"
                >
                  <input
                    type="checkbox"
                    checked={draft.guardrails.includes(guardrail)}
                    onChange={() => toggleGuardrail(guardrail)}
                    className="rounded"
                  />
                  <span className="text-sm">{guardrail.replace(/_/g, ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Workflow Preview</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-400">Name:</span>
                <span className="ml-2">{draft.name || 'Untitled'}</span>
              </div>
              <div>
                <span className="text-gray-400">Category:</span>
                <span className="ml-2">{draft.category}</span>
              </div>
              <div>
                <span className="text-gray-400">Priority:</span>
                <span className="ml-2">{draft.priority}</span>
              </div>
              <div>
                <span className="text-gray-400">Triggers:</span>
                <span className="ml-2">{draft.triggers.length}</span>
              </div>
              <div>
                <span className="text-gray-400">Steps:</span>
                <span className="ml-2">{draft.steps.length}</span>
              </div>
              <div>
                <span className="text-gray-400">Guardrails:</span>
                <span className="ml-2">{draft.guardrails.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showStepModal && editingStep && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a2a4a] rounded-lg p-6 w-[500px] border border-[#c9a227]">
            <h3 className="text-lg font-bold mb-4">Add Workflow Step</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Step Name</label>
                <input
                  type="text"
                  value={editingStep.name}
                  onChange={(e) => setEditingStep({ ...editingStep, name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Action Type</label>
                <select
                  value={editingStep.action_type}
                  onChange={(e) => setEditingStep({ ...editingStep, action_type: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded text-white"
                >
                  {ACTION_TYPES.map((action) => (
                    <option key={action} value={action}>{action}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Target Subsystem</label>
                <select
                  value={editingStep.target_subsystem}
                  onChange={(e) => setEditingStep({ ...editingStep, target_subsystem: e.target.value })}
                  className="w-full px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded text-white"
                >
                  {SUBSYSTEMS.map((sub) => (
                    <option key={sub} value={sub}>{sub}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Execution Mode</label>
                <select
                  value={editingStep.execution_mode}
                  onChange={(e) => setEditingStep({ ...editingStep, execution_mode: e.target.value as 'sequential' | 'parallel' })}
                  className="w-full px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded text-white"
                >
                  <option value="sequential">Sequential</option>
                  <option value="parallel">Parallel</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Timeout (seconds)</label>
                <input
                  type="number"
                  value={editingStep.timeout_seconds}
                  onChange={(e) => setEditingStep({ ...editingStep, timeout_seconds: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => {
                  setShowStepModal(false);
                  setEditingStep(null);
                }}
                className="px-4 py-2 bg-gray-600 text-white rounded font-medium hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={() => addStep(editingStep)}
                className="px-4 py-2 bg-[#c9a227] text-[#0a1628] rounded font-medium hover:bg-[#d9b237]"
              >
                Add Step
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
