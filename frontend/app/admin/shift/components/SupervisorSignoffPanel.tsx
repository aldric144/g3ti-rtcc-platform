'use client';

import { useState } from 'react';
import { CheckCircle, FileText, AlertTriangle } from 'lucide-react';

interface SupervisorSignoffPanelProps {
  onSignoff: () => void;
  refreshKey: number;
}

export function SupervisorSignoffPanel({ onSignoff, refreshKey }: SupervisorSignoffPanelProps) {
  const [showSignoff, setShowSignoff] = useState(false);
  const [signoffData, setSignoffData] = useState({
    closing_notes: '',
    supervisor_signoff: '',
    confirmations: {
      logsReviewed: false,
      eventsDocumented: false,
      equipmentChecked: false,
      briefingComplete: false,
    },
  });

  const allConfirmed = Object.values(signoffData.confirmations).every(Boolean);

  const handleSignoff = () => {
    if (!allConfirmed || !signoffData.supervisor_signoff.trim()) return;
    
    console.log('Shift closed with signoff:', signoffData);
    setShowSignoff(false);
    setSignoffData({
      closing_notes: '',
      supervisor_signoff: '',
      confirmations: {
        logsReviewed: false,
        eventsDocumented: false,
        equipmentChecked: false,
        briefingComplete: false,
      },
    });
    onSignoff();
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
          <CheckCircle className="h-5 w-5" />
          Supervisor Sign-off
        </h2>
        {!showSignoff && (
          <button
            onClick={() => setShowSignoff(true)}
            className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Close Shift
          </button>
        )}
      </div>

      {showSignoff ? (
        <div className="space-y-6">
          {/* Warning Banner */}
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              <span className="text-sm font-medium text-amber-800 dark:text-amber-200">
                You are about to close the current shift. This action cannot be undone.
              </span>
            </div>
          </div>

          {/* Confirmation Checklist */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Confirm the following before closing:
            </p>
            <label className="flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50">
              <input
                type="checkbox"
                checked={signoffData.confirmations.logsReviewed}
                onChange={(e) => setSignoffData({
                  ...signoffData,
                  confirmations: { ...signoffData.confirmations, logsReviewed: e.target.checked }
                })}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                All activity logs have been reviewed
              </span>
            </label>
            <label className="flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50">
              <input
                type="checkbox"
                checked={signoffData.confirmations.eventsDocumented}
                onChange={(e) => setSignoffData({
                  ...signoffData,
                  confirmations: { ...signoffData.confirmations, eventsDocumented: e.target.checked }
                })}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                All major events have been documented
              </span>
            </label>
            <label className="flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50">
              <input
                type="checkbox"
                checked={signoffData.confirmations.equipmentChecked}
                onChange={(e) => setSignoffData({
                  ...signoffData,
                  confirmations: { ...signoffData.confirmations, equipmentChecked: e.target.checked }
                })}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Equipment status has been verified
              </span>
            </label>
            <label className="flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50">
              <input
                type="checkbox"
                checked={signoffData.confirmations.briefingComplete}
                onChange={(e) => setSignoffData({
                  ...signoffData,
                  confirmations: { ...signoffData.confirmations, briefingComplete: e.target.checked }
                })}
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Shift briefing/handoff is complete
              </span>
            </label>
          </div>

          {/* Closing Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Closing Notes (optional)
            </label>
            <textarea
              value={signoffData.closing_notes}
              onChange={(e) => setSignoffData({ ...signoffData, closing_notes: e.target.value })}
              rows={3}
              placeholder="Any notes for the incoming shift..."
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
            />
          </div>

          {/* Supervisor Signature */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Supervisor Sign-off (type your name)
            </label>
            <input
              type="text"
              value={signoffData.supervisor_signoff}
              onChange={(e) => setSignoffData({ ...signoffData, supervisor_signoff: e.target.value })}
              placeholder="Enter your full name"
              required
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setShowSignoff(false)}
              className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSignoff}
              disabled={!allConfirmed || !signoffData.supervisor_signoff.trim()}
              className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle className="h-4 w-4" />
              Confirm & Close Shift
            </button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Use this panel to officially close the current shift with supervisor sign-off.
          All confirmations must be checked before closing.
        </p>
      )}
    </div>
  );
}
