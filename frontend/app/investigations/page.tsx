'use client';

import { useState } from 'react';
import { Search, Filter, Plus, FileText, Clock, User, Link2, Network } from 'lucide-react';
import { SearchBar } from '@/app/components/investigations/SearchBar';
import { SearchResults } from '@/app/components/investigations/SearchResults';
import { SearchFilters } from '@/app/components/investigations/SearchFilters';
import { CaseBuilder } from './components/CaseBuilder';
import { IncidentLinker } from './components/IncidentLinker';
import { EntityProfile } from './components/EntityProfile';
import { Timeline } from './components/Timeline';
import { EvidenceViewer } from './components/EvidenceViewer';
import { CaseExport } from './components/CaseExport';
import { EntityGraph } from './components/EntityGraph';

type TabType = 'search' | 'build' | 'link' | 'entity' | 'case';

interface CaseData {
  case_id: string;
  case_number: string;
  summary: string;
  timeline: any[];
  evidence: any;
  linked_incidents: any[];
  suspects: any[];
  vehicles: any[];
  addresses: string[];
  risk_assessment: any;
  recommendations: string[];
}

/**
 * Investigations Dashboard - Phase 4
 * 
 * Provides comprehensive investigation management:
 * - Case search and management
 * - Auto case building from incidents/suspects
 * - Incident linking analysis
 * - Entity profile lookup
 * - Timeline visualization
 * - Evidence collection viewer
 * - Entity relationship graphs
 * - Case export (PDF/JSON)
 */
export default function InvestigationsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [currentCase, setCurrentCase] = useState<CaseData | null>(null);
  const [stats] = useState({
    openCases: 89,
    pendingReview: 12,
    assignedToYou: 5,
  });

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    setIsSearching(true);
    
    try {
      const response = await fetch(`/api/investigations/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCaseCreated = (caseData: CaseData) => {
    setCurrentCase(caseData);
    setActiveTab('case');
  };

  const tabs = [
    { id: 'search', label: 'Search', icon: Search },
    { id: 'build', label: 'Build Case', icon: Plus },
    { id: 'link', label: 'Link Incidents', icon: Link2 },
    { id: 'entity', label: 'Entity Lookup', icon: User },
    { id: 'case', label: 'Current Case', icon: FileText, disabled: !currentCase },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Investigations Engine
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Automated case building, incident linking, and entity correlation
          </p>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-blue-100 p-3">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.openCases}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Open Cases</p>
          </div>
        </div>
        
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-orange-100 p-3">
            <Clock className="h-6 w-6 text-orange-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.pendingReview}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Pending Review</p>
          </div>
        </div>
        
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-green-100 p-3">
            <User className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.assignedToYou}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Assigned to You</p>
          </div>
        </div>

        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-purple-100 p-3">
            <Network className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">247</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Linked Entities</p>
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-4" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => !tab.disabled && setActiveTab(tab.id as TabType)}
              disabled={tab.disabled}
              className={`
                flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }
                ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="mt-6">
        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            <div className="card">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <SearchBar
                    value={query}
                    onChange={setQuery}
                    onSearch={handleSearch}
                    placeholder="Search persons, vehicles, incidents, addresses..."
                  />
                </div>
                
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`btn-outline flex items-center gap-2 ${showFilters ? 'bg-gray-100' : ''}`}
                >
                  <Filter className="h-4 w-4" />
                  Filters
                </button>
              </div>

              {showFilters && (
                <div className="mt-4 border-t pt-4">
                  <SearchFilters />
                </div>
              )}
            </div>

            <SearchResults
              results={results}
              isLoading={isSearching}
              query={query}
            />
          </div>
        )}

        {/* Build Case Tab */}
        {activeTab === 'build' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CaseBuilder onCaseCreated={handleCaseCreated} />
            
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Recent Cases
              </h3>
              <div className="space-y-3">
                {[
                  { id: 'CASE-2025-00123', title: 'Armed Robbery Investigation', status: 'active', priority: 'high' },
                  { id: 'CASE-2025-00122', title: 'Vehicle Theft Ring', status: 'active', priority: 'medium' },
                  { id: 'CASE-2025-00121', title: 'Shooting Incident Analysis', status: 'review', priority: 'high' },
                ].map((caseItem) => (
                  <div
                    key={caseItem.id}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900 dark:text-white">{caseItem.id}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        caseItem.priority === 'high' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'
                      }`}>
                        {caseItem.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{caseItem.title}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Link Incidents Tab */}
        {activeTab === 'link' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <IncidentLinker />
            <EntityGraph />
          </div>
        )}

        {/* Entity Lookup Tab */}
        {activeTab === 'entity' && (
          <EntityProfile />
        )}

        {/* Current Case Tab */}
        {activeTab === 'case' && currentCase && (
          <div className="space-y-6">
            {/* Case header */}
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    {currentCase.case_number}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    {currentCase.summary}
                  </p>
                </div>
                {currentCase.risk_assessment && (
                  <div className={`px-4 py-2 rounded-lg ${
                    currentCase.risk_assessment.overall_score >= 0.7 ? 'bg-red-100 text-red-700' :
                    currentCase.risk_assessment.overall_score >= 0.4 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    <div className="text-2xl font-bold">
                      {(currentCase.risk_assessment.overall_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs">Risk Score</div>
                  </div>
                )}
              </div>

              {/* Case stats */}
              <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {currentCase.linked_incidents.length}
                  </div>
                  <div className="text-xs text-gray-500">Linked Incidents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {currentCase.suspects.length}
                  </div>
                  <div className="text-xs text-gray-500">Suspects</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {currentCase.vehicles.length}
                  </div>
                  <div className="text-xs text-gray-500">Vehicles</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {currentCase.timeline.length}
                  </div>
                  <div className="text-xs text-gray-500">Timeline Events</div>
                </div>
              </div>
            </div>

            {/* Case content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Timeline events={currentCase.timeline} />
              <EvidenceViewer evidence={currentCase.evidence} />
            </div>

            {/* Suspects and Vehicles */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Suspects ({currentCase.suspects.length})
                </h3>
                <div className="space-y-2">
                  {currentCase.suspects.map((suspect, index) => (
                    <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {suspect.name || `Suspect ${index + 1}`}
                        </span>
                        {suspect.risk_score && (
                          <span className={`px-2 py-1 rounded text-xs ${
                            suspect.risk_score >= 0.7 ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'
                          }`}>
                            {(suspect.risk_score * 100).toFixed(0)}% risk
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {suspect.description || 'No description available'}
                      </p>
                    </div>
                  ))}
                  {currentCase.suspects.length === 0 && (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                      No suspects identified
                    </p>
                  )}
                </div>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Vehicles ({currentCase.vehicles.length})
                </h3>
                <div className="space-y-2">
                  {currentCase.vehicles.map((vehicle, index) => (
                    <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {vehicle.plate_number || `Vehicle ${index + 1}`}
                        </span>
                        <span className="text-xs text-gray-500">{vehicle.state}</span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {vehicle.year} {vehicle.make} {vehicle.model} - {vehicle.color}
                      </p>
                    </div>
                  ))}
                  {currentCase.vehicles.length === 0 && (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                      No vehicles identified
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {currentCase.recommendations && currentCase.recommendations.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Investigative Recommendations
                </h3>
                <ul className="space-y-2">
                  {currentCase.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                      <span className="text-blue-500 mt-1">-</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Export */}
            <CaseExport caseId={currentCase.case_id} caseNumber={currentCase.case_number} />
          </div>
        )}
      </div>
    </div>
  );
}
