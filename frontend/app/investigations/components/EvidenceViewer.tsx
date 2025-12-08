'use client';

import { useState } from 'react';
import {
  FileText,
  Volume2,
  Camera,
  Car,
  Shield,
  Radio,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';

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
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Evidence Collection</h3>
        <span className="rounded bg-gray-100 px-2 py-1 text-sm text-gray-600 dark:bg-gray-800 dark:text-gray-400">
          {totalItems} items
        </span>
      </div>

      <div className="space-y-2">
        {sections.map((section) => (
          <div
            key={section.id}
            className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700"
          >
            {/* Section header */}
            <button
              onClick={() => toggleSection(section.id)}
              className="flex w-full items-center justify-between bg-gray-50 p-3 transition-colors hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700"
            >
              <div className="flex items-center gap-3">
                <div className={`rounded-lg p-2 ${section.bgColor}`}>
                  <section.icon className={`h-4 w-4 ${section.color}`} />
                </div>
                <span className="font-medium text-gray-900 dark:text-white">{section.title}</span>
                <span className="rounded bg-gray-200 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-600 dark:text-gray-300">
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
              <div className="max-h-64 space-y-2 overflow-y-auto p-3">
                {section.items.map((item, index) => (
                  <div
                    key={index}
                    onClick={() => onEvidenceClick?.(item, section.id)}
                    className="cursor-pointer rounded border border-gray-100 bg-white p-2 transition-colors hover:border-blue-300 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-blue-600"
                  >
                    {renderEvidenceItem(item, section.id)}
                  </div>
                ))}
              </div>
            )}

            {expandedSections.has(section.id) && section.items.length === 0 && (
              <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                No {section.title.toLowerCase()} available
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Attachments section */}
      {evidence.attachments && evidence.attachments.length > 0 && (
        <div className="mt-4 border-t border-gray-200 pt-4 dark:border-gray-700">
          <h4 className="mb-2 font-medium text-gray-900 dark:text-white">
            Attachments ({evidence.attachments.length})
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {evidence.attachments.map((attachment, index) => (
              <a
                key={index}
                href={attachment.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded bg-gray-50 p-2 transition-colors hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700"
              >
                <FileText className="h-4 w-4 text-gray-500" />
                <span className="flex-1 truncate text-sm text-gray-700 dark:text-gray-300">
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
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.report_number || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.report_type}</span>
          </div>
          <p className="mt-1 truncate text-xs text-gray-600 dark:text-gray-400">
            {item.summary || item.narrative?.substring(0, 100)}
          </p>
          {item.date && <p className="mt-1 text-xs text-gray-400">{item.date}</p>}
        </div>
      );

    case 'audio':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.alert_id || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.rounds_detected} rounds</span>
          </div>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            {item.location?.address || `${item.latitude}, ${item.longitude}`}
          </p>
          {item.timestamp && <p className="mt-1 text-xs text-gray-400">{item.timestamp}</p>}
        </div>
      );

    case 'ballistics':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.caliber} - {item.weapon_type}
            </span>
            {item.match_confidence && (
              <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-600">
                {(item.match_confidence * 100).toFixed(0)}% match
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            {item.make} {item.model}
          </p>
          {item.linked_incidents && (
            <p className="mt-1 text-xs text-gray-400">
              {item.linked_incidents.length} linked incidents
            </p>
          )}
        </div>
      );

    case 'lpr':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.plate_number}
            </span>
            <span className="text-xs text-gray-500">{item.state}</span>
          </div>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            {item.location?.address || item.camera_location}
          </p>
          {item.timestamp && <p className="mt-1 text-xs text-gray-400">{item.timestamp}</p>}
        </div>
      );

    case 'bwc':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.recording_id || item.id}
            </span>
            <span className="text-xs text-gray-500">{item.duration}</span>
          </div>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Officer: {item.officer_name || item.officer_id}
          </p>
          {item.timestamp && <p className="mt-1 text-xs text-gray-400">{item.timestamp}</p>}
        </div>
      );

    case 'cameras':
      return (
        <div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {item.camera_name || item.camera_id}
            </span>
            <span
              className={`rounded px-2 py-0.5 text-xs ${item.status === 'online' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}
            >
              {item.status}
            </span>
          </div>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
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
