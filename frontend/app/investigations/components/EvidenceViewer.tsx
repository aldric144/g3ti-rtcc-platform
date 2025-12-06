'use client';

import { useState } from 'react';
import { FileText, Volume2, Camera, Car, Shield, Radio, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';

interface Evidence {
  reports: any[];
  audio_metadata: any[];
  ballistics: any[];
  lpr_trail: any[];
  bwc_interactions: any[];
  camera_positions: any[];
  attachments: any[];
}

interface EvidenceViewerProps {
  evidence: Evidence;
  onEvidenceClick?: (item: any, type: string) => void;
}

/**
 * Evidence Viewer component for displaying collected evidence.
 * 
 * Displays evidence from:
 * - RMS reports
 * - CAD history
 * - ShotSpotter audio metadata
 * - LPR hits
 * - BWC metadata
 * - NESS ballistics
 * - Camera snapshots
 */
export function EvidenceViewer({ evidence, onEvidenceClick }: EvidenceViewerProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['reports']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const sections = [
    {
      id: 'reports',
      title: 'Reports',
      icon: FileText,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
      items: evidence.reports || [],
    },
    {
      id: 'audio',
      title: 'Audio Metadata',
      icon: Volume2,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100',
      items: evidence.audio_metadata || [],
    },
    {
      id: 'ballistics',
      title: 'Ballistics',
      icon: Shield,
      color: 'text-red-500',
      bgColor: 'bg-red-100',
      items: evidence.ballistics || [],
    },
    {
      id: 'lpr',
      title: 'LPR Trail',
      icon: Car,
      color: 'text-green-500',
      bgColor: 'bg-green-100',
      items: evidence.lpr_trail || [],
    },
    {
      id: 'bwc',
      title: 'BWC Interactions',
      icon: Camera,
      color: 'text-orange-500',
      bgColor: 'bg-orange-100',
      items: evidence.bwc_interactions || [],
    },
    {
      id: 'cameras',
      title: 'Camera Positions',
      icon: Radio,
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-100',
      items: evidence.camera_positions || [],
    },
  ];

  const totalItems = sections.reduce((sum, section) => sum + section.items.length, 0);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Evidence Collection
        </h3>
        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-sm text-gray-600 dark:text-gray-400">
          {totalItems} items
        </span>
      </div>

      <div className="space-y-2">
        {sections.map((section) => (
          <div key={section.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            {/* Section header */}
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${section.bgColor}`}>
                  <section.icon className={`h-4 w-4 ${section.color}`} />
                </div>
                <span className="font-medium text-gray-900 dark:text-white">
                  {section.title}
                </span>
                <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-xs text-gray-600 dark:text-gray-300">
                  {section.items.length}
                </span>
              </div>
              {expandedSections.has(section.id) ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
            </button>

            {/* Section content */}
            {expandedSections.has(section.id) && section.items.length > 0 && (
              <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
                {section.items.map((item, index) => (
                  <div
                    key={index}
                    onClick={() => onEvidenceClick?.(item, section.id)}
                    className="p-2 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-700 rounded cursor-pointer hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
                  >
                    {renderEvidenceItem(item, section.id)}
                  </div>
                ))}
              </div>
            )}

            {expandedSections.has(section.id) && section.items.length === 0 && (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400 text-sm">
                No {section.title.toLowerCase()} available
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Attachments section */}
      {evidence.attachments && evidence.attachments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">
            Attachments ({evidence.attachments.length})
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {evidence.attachments.map((attachment, index) => (
              <a
                key={index}
                href={attachment.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <FileText className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1">
                  {attachment.name || `Attachment ${index + 1}`}
                </span>
                <ExternalLink className="h-3 w-3 text-gray-400" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function renderEvidenceItem(item: any, type: string) {
  switch (type) {
    case 'reports':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.report_number || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.report_type}</span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">
            {item.summary || item.narrative?.substring(0, 100)}
          </p>
          {item.date && (
            <p className="text-xs text-gray-400 mt-1">{item.date}</p>
          )}
        </div>
      );

    case 'audio':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.alert_id || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.rounds_detected} rounds</span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {item.location?.address || `${item.latitude}, ${item.longitude}`}
          </p>
          {item.timestamp && (
            <p className="text-xs text-gray-400 mt-1">{item.timestamp}</p>
          )}
        </div>
      );

    case 'ballistics':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.caliber} - {item.weapon_type}
            </span>
            {item.match_confidence && (
              <span className="text-xs px-2 py-0.5 bg-red-100 text-red-600 rounded">
                {(item.match_confidence * 100).toFixed(0)}% match
              </span>
            )}
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {item.make} {item.model}
          </p>
          {item.linked_incidents && (
            <p className="text-xs text-gray-400 mt-1">
              {item.linked_incidents.length} linked incidents
            </p>
          )}
        </div>
      );

    case 'lpr':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.plate_number}
            </span>
            <span className="text-xs text-gray-500">{item.state}</span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {item.location?.address || item.camera_location}
          </p>
          {item.timestamp && (
            <p className="text-xs text-gray-400 mt-1">{item.timestamp}</p>
          )}
        </div>
      );

    case 'bwc':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.recording_id || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.duration}</span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Officer: {item.officer_name || item.officer_id}
          </p>
          {item.timestamp && (
            <p className="text-xs text-gray-400 mt-1">{item.timestamp}</p>
          )}
        </div>
      );

    case 'cameras':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm text-gray-900 dark:text-white">
              {item.camera_name || item.camera_id}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded ${item.status === 'online' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}>
              {item.status}
            </span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {item.location?.address || `${item.latitude}, ${item.longitude}`}
          </p>
        </div>
      );

    default:
      return (
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {JSON.stringify(item).substring(0, 100)}...
        </div>
      );
  }
}

export default EvidenceViewer;
