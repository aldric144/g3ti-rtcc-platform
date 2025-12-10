'use client';

import React, { useState, useEffect } from 'react';

interface Report {
  report_id: string;
  case_id: string;
  report_type: string;
  title: string;
  status: string;
  version: number;
  word_count: number;
  created_at: string;
}

interface Brief {
  brief_id: string;
  case_id: string;
  title: string;
  key_findings: string[];
  recommended_actions: string[];
}

interface CourtPacket {
  packet_id: string;
  case_id: string;
  case_number: string;
  defendant_name: string;
  status: string;
  total_pages: number;
}

interface Props {
  caseId: string | null;
}

export default function CaseReportBuilder({ caseId }: Props) {
  const [reports, setReports] = useState<Report[]>([]);
  const [briefs, setBriefs] = useState<Brief[]>([]);
  const [courtPackets, setCourtPackets] = useState<CourtPacket[]>([]);
  const [activeTab, setActiveTab] = useState<'reports' | 'briefs' | 'court'>('reports');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadData();
    }
  }, [caseId]);

  const loadData = async () => {
    setLoading(true);
    setTimeout(() => {
      setReports([
        {
          report_id: 'rpt-001',
          case_id: caseId || '',
          report_type: 'investigative',
          title: 'Initial Investigation Report',
          status: 'draft',
          version: 1,
          word_count: 2450,
          created_at: '2024-01-15T10:30:00Z',
        },
        {
          report_id: 'rpt-002',
          case_id: caseId || '',
          report_type: 'supplemental',
          title: 'Supplemental Report - Witness Interviews',
          status: 'approved',
          version: 2,
          word_count: 1820,
          created_at: '2024-01-18T14:15:00Z',
        },
      ]);
      setBriefs([
        {
          brief_id: 'brief-001',
          case_id: caseId || '',
          title: 'Case Summary Brief',
          key_findings: [
            'Primary suspect identified through forensic evidence',
            'Timeline established from 22:00 to 23:30',
            'Two witnesses corroborate suspect presence',
          ],
          recommended_actions: [
            'Obtain arrest warrant for primary suspect',
            'Interview additional witnesses',
            'Request phone records subpoena',
          ],
        },
      ]);
      setCourtPackets([
        {
          packet_id: 'pkt-001',
          case_id: caseId || '',
          case_number: '2024-CR-001234',
          defendant_name: 'John Doe',
          status: 'pending_review',
          total_pages: 45,
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const generateReport = async (type: string) => {
    setGenerating(true);
    setTimeout(() => {
      const newReport: Report = {
        report_id: `rpt-${Date.now()}`,
        case_id: caseId || '',
        report_type: type,
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Report - ${new Date().toLocaleDateString()}`,
        status: 'draft',
        version: 1,
        word_count: Math.floor(Math.random() * 2000) + 1000,
        created_at: new Date().toISOString(),
      };
      setReports((prev) => [newReport, ...prev]);
      setGenerating(false);
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-yellow-900/50 text-yellow-400',
      pending_review: 'bg-blue-900/50 text-blue-400',
      approved: 'bg-green-900/50 text-green-400',
      rejected: 'bg-red-900/50 text-red-400',
      finalized: 'bg-purple-900/50 text-purple-400',
    };
    return colors[status] || 'bg-gray-700 text-gray-400';
  };

  if (!caseId) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">Select a case to view and build reports</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Case Report Builder</h2>
        <div className="flex items-center gap-4">
          <div className="flex bg-gray-700 rounded-lg p-1">
            {(['reports', 'briefs', 'court'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded text-sm capitalize ${activeTab === tab ? 'bg-blue-600' : ''}`}
              >
                {tab === 'court' ? 'Court Packets' : tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {activeTab === 'reports' && (
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-300">Investigation Reports</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => generateReport('investigative')}
                      disabled={generating}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm"
                    >
                      {generating ? 'Generating...' : 'Generate Report'}
                    </button>
                  </div>
                </div>

                {reports.map((report) => (
                  <div
                    key={report.report_id}
                    className={`bg-gray-800 rounded-lg p-4 cursor-pointer border-2 transition-colors ${
                      selectedReport?.report_id === report.report_id
                        ? 'border-blue-500'
                        : 'border-transparent hover:border-gray-600'
                    }`}
                    onClick={() => setSelectedReport(report)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-medium">{report.title}</h4>
                        <span className="text-xs text-gray-400 capitalize">
                          {report.report_type} Report • v{report.version}
                        </span>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(report.status)}`}>
                        {report.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <span>{report.word_count.toLocaleString()} words</span>
                      <span>{new Date(report.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                {selectedReport ? (
                  <>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <h3 className="font-medium mb-3">Report Details</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Type</span>
                          <span className="capitalize">{selectedReport.report_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Status</span>
                          <span className="capitalize">{selectedReport.status.replace('_', ' ')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Version</span>
                          <span>{selectedReport.version}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Word Count</span>
                          <span>{selectedReport.word_count.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-800 rounded-lg p-4">
                      <h3 className="font-medium mb-3">Actions</h3>
                      <div className="space-y-2">
                        <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                          View Full Report
                        </button>
                        <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                          Export as PDF
                        </button>
                        <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                          Submit for Review
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="bg-gray-800 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Select a report to view details</p>
                  </div>
                )}

                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-medium mb-3">Report Types</h3>
                  <div className="space-y-2">
                    {['investigative', 'supplemental', 'closure', 'arrest'].map((type) => (
                      <button
                        key={type}
                        onClick={() => generateReport(type)}
                        disabled={generating}
                        className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded text-sm text-left capitalize"
                      >
                        Generate {type} Report
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'briefs' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-300">Detective Briefs</h3>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                  Generate New Brief
                </button>
              </div>

              {briefs.map((brief) => (
                <div key={brief.brief_id} className="bg-gray-800 rounded-lg p-4">
                  <h4 className="font-medium mb-4">{brief.title}</h4>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h5 className="text-sm text-gray-400 mb-2">Key Findings</h5>
                      <ul className="space-y-2">
                        {brief.key_findings.map((finding, index) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5"></span>
                            {finding}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h5 className="text-sm text-gray-400 mb-2">Recommended Actions</h5>
                      <ul className="space-y-2">
                        {brief.recommended_actions.map((action, index) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5"></span>
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-700 flex gap-2">
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                      View Full Brief
                    </button>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                      Export
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'court' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-300">Court-Ready Evidence Packets</h3>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                  Generate Court Packet
                </button>
              </div>

              {courtPackets.map((packet) => (
                <div key={packet.packet_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-medium">Case #{packet.case_number}</h4>
                      <p className="text-sm text-gray-400">Defendant: {packet.defendant_name}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(packet.status)}`}>
                      {packet.status.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm mb-4">
                    <div className="bg-gray-700 rounded p-3">
                      <span className="text-gray-400">Total Pages</span>
                      <p className="font-medium text-lg">{packet.total_pages}</p>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <span className="text-gray-400">Evidence Items</span>
                      <p className="font-medium text-lg">12</p>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <span className="text-gray-400">Witnesses</span>
                      <p className="font-medium text-lg">5</p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                      View Packet
                    </button>
                    <button className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                      Finalize for Court
                    </button>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                      Download PDF
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
