'use client';

import { useState } from 'react';
import { FileText, Flag, Users, MapPin, Plus } from 'lucide-react';
import { CaseShortcutPanel } from './components/CaseShortcutPanel';
import { CaseQuickNotePanel } from './components/CaseQuickNotePanel';
import { BOLOZonePanel } from './components/BOLOZonePanel';
import { UnitRequestPanel } from './components/UnitRequestPanel';

export default function CaseToolsPage() {
  const [activeTab, setActiveTab] = useState<'shortcuts' | 'notes' | 'bolo' | 'units'>('shortcuts');

  const tabs = [
    { id: 'shortcuts', label: 'Quick Actions', icon: FileText },
    { id: 'notes', label: 'Case Notes', icon: Flag },
    { id: 'bolo', label: 'BOLO Zones', icon: MapPin },
    { id: 'units', label: 'Unit Requests', icon: Users },
  ] as const;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Case Management Tools
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Rapid case actions and shortcuts for RTCC operations
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-rtcc-primary text-rtcc-primary'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'shortcuts' && <CaseShortcutPanel />}
        {activeTab === 'notes' && <CaseQuickNotePanel />}
        {activeTab === 'bolo' && <BOLOZonePanel />}
        {activeTab === 'units' && <UnitRequestPanel />}
      </div>
    </div>
  );
}
