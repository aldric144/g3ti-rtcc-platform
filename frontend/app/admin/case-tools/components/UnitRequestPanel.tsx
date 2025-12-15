'use client';

import { useState } from 'react';
import { Users, Plus, Clock, CheckCircle, XCircle } from 'lucide-react';

interface UnitRequest {
  id: string;
  case_id: string;
  request_type: string;
  priority: string;
  details: string;
  location: string;
  status: string;
  created_at: string;
}

const REQUEST_TYPES = [
  { value: 'follow_up', label: 'Follow-Up' },
  { value: 'scene_check', label: 'Scene Check' },
  { value: 'interview', label: 'Interview' },
  { value: 'surveillance', label: 'Surveillance' },
  { value: 'patrol', label: 'Patrol Request' },
];

const PRIORITIES = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' },
];

export function UnitRequestPanel() {
  const [requests, setRequests] = useState<UnitRequest[]>([
    {
      id: '1',
      case_id: 'RTCC-2025-00042',
      request_type: 'follow_up',
      priority: 'high',
      details: 'Follow up with witness at 1200 Blue Heron Blvd regarding vehicle description.',
      location: '1200 Blue Heron Blvd',
      status: 'pending',
      created_at: new Date(Date.now() - 30 * 60000).toISOString(),
    },
    {
      id: '2',
      case_id: 'RTCC-2025-00039',
      request_type: 'scene_check',
      priority: 'medium',
      details: 'Check area for additional camera coverage or witnesses.',
      location: 'Marina District',
      status: 'assigned',
      created_at: new Date(Date.now() - 60 * 60000).toISOString(),
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [newRequest, setNewRequest] = useState({
    case_id: '',
    request_type: 'follow_up',
    priority: 'medium',
    details: '',
    location: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const request: UnitRequest = {
      id: Date.now().toString(),
      ...newRequest,
      status: 'pending',
      created_at: new Date().toISOString(),
    };

    setRequests([request, ...requests]);
    setNewRequest({
      case_id: '',
      request_type: 'follow_up',
      priority: 'medium',
      details: '',
      location: '',
    });
    setShowForm(false);
  };

  const updateStatus = (requestId: string, status: string) => {
    setRequests(requests.map(r => r.id === requestId ? { ...r, status } : r));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-amber-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
          <Users className="h-5 w-5" />
          <span className="text-sm font-medium">
            {requests.filter(r => r.status === 'pending').length} Pending Requests
          </span>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Request
        </button>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
            Request Unit Follow-Up
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Case ID
                </label>
                <input
                  type="text"
                  value={newRequest.case_id}
                  onChange={(e) => setNewRequest({ ...newRequest, case_id: e.target.value })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Request Type
                </label>
                <select
                  value={newRequest.request_type}
                  onChange={(e) => setNewRequest({ ...newRequest, request_type: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                >
                  {REQUEST_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Priority
                </label>
                <select
                  value={newRequest.priority}
                  onChange={(e) => setNewRequest({ ...newRequest, priority: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                >
                  {PRIORITIES.map((priority) => (
                    <option key={priority.value} value={priority.value}>
                      {priority.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Location
                </label>
                <input
                  type="text"
                  value={newRequest.location}
                  onChange={(e) => setNewRequest({ ...newRequest, location: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Details
              </label>
              <textarea
                value={newRequest.details}
                onChange={(e) => setNewRequest({ ...newRequest, details: e.target.value })}
                rows={3}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Submit Request
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Request List */}
      <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {requests.map((request) => (
            <div key={request.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {getStatusIcon(request.status)}
                    <span className="text-xs font-medium text-rtcc-primary">
                      {request.case_id}
                    </span>
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                      {REQUEST_TYPES.find(t => t.value === request.request_type)?.label}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITIES.find(p => p.value === request.priority)?.color}`}>
                      {request.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{request.details}</p>
                  {request.location && (
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Location: {request.location}
                    </p>
                  )}
                </div>
                {request.status === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => updateStatus(request.id, 'completed')}
                      className="rounded-lg bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
                    >
                      Complete
                    </button>
                    <button
                      onClick={() => updateStatus(request.id, 'cancelled')}
                      className="rounded-lg bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
