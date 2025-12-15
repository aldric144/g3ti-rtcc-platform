'use client';

import { useState } from 'react';
import { 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  Users, 
  Flag, 
  MapPin,
  ArrowRight
} from 'lucide-react';

interface ShortcutAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const SHORTCUTS: ShortcutAction[] = [
  {
    id: 'create-shell',
    title: 'Create Case Shell',
    description: 'Create a placeholder case for RTCC tracking',
    icon: <FileText className="h-5 w-5" />,
    color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  },
  {
    id: 'add-note',
    title: 'Add RTCC Support Note',
    description: 'Add a support note to an existing case',
    icon: <MessageSquare className="h-5 w-5" />,
    color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  },
  {
    id: 'mark-assisted',
    title: 'Mark as RTCC-Assisted',
    description: 'Flag a case as having RTCC support',
    icon: <CheckCircle className="h-5 w-5" />,
    color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  },
  {
    id: 'request-unit',
    title: 'Request Unit Follow-Up',
    description: 'Request patrol unit to follow up on case',
    icon: <Users className="h-5 w-5" />,
    color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  },
  {
    id: 'intel-review',
    title: 'Flag for Intelligence Review',
    description: 'Mark case for intelligence analyst review',
    icon: <Flag className="h-5 w-5" />,
    color: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  },
  {
    id: 'add-bolo',
    title: 'Add BOLO Zone',
    description: 'Create a geographic alert zone for case',
    icon: <MapPin className="h-5 w-5" />,
    color: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
  },
];

export function CaseShortcutPanel() {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [caseId, setCaseId] = useState('');

  const handleAction = (actionId: string) => {
    setSelectedAction(actionId);
  };

  const executeAction = async () => {
    if (!selectedAction) return;
    
    console.log('Executing action:', selectedAction, 'for case:', caseId);
    // In production, this would call the appropriate API endpoint
    setSelectedAction(null);
    setCaseId('');
  };

  return (
    <div className="space-y-6">
      {/* Quick Actions Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SHORTCUTS.map((shortcut) => (
          <button
            key={shortcut.id}
            onClick={() => handleAction(shortcut.id)}
            className={`flex items-start gap-4 rounded-xl border p-4 text-left transition-all hover:shadow-md ${
              selectedAction === shortcut.id
                ? 'border-rtcc-primary bg-rtcc-primary/5'
                : 'border-gray-200 bg-white hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600'
            }`}
          >
            <div className={`rounded-lg p-2 ${shortcut.color}`}>
              {shortcut.icon}
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">
                {shortcut.title}
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {shortcut.description}
              </p>
            </div>
          </button>
        ))}
      </div>

      {/* Action Form */}
      {selectedAction && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
            {SHORTCUTS.find(s => s.id === selectedAction)?.title}
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Case ID (optional - leave blank to create new)
              </label>
              <input
                type="text"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="e.g., RTCC-2025-00001"
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setSelectedAction(null)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={executeAction}
                className="flex items-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Execute
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
