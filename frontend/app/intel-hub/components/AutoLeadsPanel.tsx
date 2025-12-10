"use client";

import { useState, useEffect } from "react";

interface InvestigativeLead {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: "critical" | "high" | "medium" | "low";
  score: number;
  confidence: number;
  sources: string[];
  entities: {
    type: string;
    name: string;
    id: string;
  }[];
  suggestedActions: string[];
  assignedTo?: string;
  status: "new" | "assigned" | "in_progress" | "completed" | "dismissed";
  generatedAt: string;
  caseNumber?: string;
}

const priorityColors = {
  critical: "bg-red-600 text-white",
  high: "bg-orange-600 text-white",
  medium: "bg-yellow-600 text-black",
  low: "bg-blue-600 text-white",
};

const statusColors = {
  new: "bg-purple-600",
  assigned: "bg-blue-600",
  in_progress: "bg-yellow-600",
  completed: "bg-green-600",
  dismissed: "bg-gray-600",
};

const mockLeads: InvestigativeLead[] = [
  {
    id: "lead-001",
    title: "Potential Serial Burglary Suspect Identified",
    description:
      "AI pattern analysis has identified a potential suspect matching MO across 5 residential burglaries in District 7. Subject has prior arrests for similar offenses.",
    category: "Pattern Match",
    priority: "high",
    score: 85,
    confidence: 0.82,
    sources: ["AI Engine", "Pattern Analysis", "Criminal History"],
    entities: [
      { type: "person", name: "Michael Smith", id: "p-456" },
      { type: "pattern", name: "Residential Burglary Series", id: "pat-123" },
    ],
    suggestedActions: [
      "Review surveillance footage from incident locations",
      "Check subject's known associates",
      "Coordinate with patrol for increased presence",
    ],
    status: "new",
    generatedAt: new Date().toISOString(),
  },
  {
    id: "lead-002",
    title: "Vehicle Linked to Multiple Drug Transactions",
    description:
      "LPR data combined with tactical intelligence indicates vehicle has been present at 8 suspected drug transaction locations over past 14 days.",
    category: "Drug Activity",
    priority: "high",
    score: 78,
    confidence: 0.75,
    sources: ["LPR System", "Tactical Engine", "Narcotics Unit Intel"],
    entities: [
      { type: "vehicle", name: "Silver Honda Accord - XYZ789", id: "v-789" },
      { type: "location", name: "Multiple - See Details", id: "loc-multi" },
    ],
    suggestedActions: [
      "Request narcotics unit review",
      "Set up LPR alert for vehicle",
      "Review registered owner information",
    ],
    assignedTo: "Det. Johnson",
    status: "assigned",
    generatedAt: new Date(Date.now() - 3600000).toISOString(),
    caseNumber: "2024-NAR-0456",
  },
  {
    id: "lead-003",
    title: "Federal Warrant Subject - Local Sighting",
    description:
      "Subject with active federal warrant for weapons trafficking was identified via facial recognition at local convenience store.",
    category: "Federal Match",
    priority: "critical",
    score: 95,
    confidence: 0.91,
    sources: ["NCIC", "Facial Recognition", "ATF"],
    entities: [
      { type: "person", name: "Robert Williams", id: "p-fed-123" },
      { type: "location", name: "QuickMart - 456 Oak St", id: "loc-456" },
    ],
    suggestedActions: [
      "Coordinate with US Marshals",
      "Alert patrol units in area",
      "Review additional surveillance",
    ],
    assignedTo: "Sgt. Martinez",
    status: "in_progress",
    generatedAt: new Date(Date.now() - 7200000).toISOString(),
    caseNumber: "2024-FED-0089",
  },
  {
    id: "lead-004",
    title: "Repeat Offender - Theft Pattern",
    description:
      "Known shoplifter with 12 prior arrests detected at multiple retail locations. Pattern suggests organized retail crime involvement.",
    category: "Retail Crime",
    priority: "medium",
    score: 65,
    confidence: 0.78,
    sources: ["Retail Partners", "Criminal History", "AI Engine"],
    entities: [
      { type: "person", name: "Sarah Johnson", id: "p-789" },
      { type: "pattern", name: "Organized Retail Theft", id: "pat-456" },
    ],
    suggestedActions: [
      "Notify retail loss prevention partners",
      "Review recent theft reports",
      "Consider surveillance operation",
    ],
    status: "new",
    generatedAt: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: "lead-005",
    title: "Gang Activity - Territory Expansion",
    description:
      "Social media analysis and incident correlation suggests gang activity expanding into previously neutral territory. Increased violence risk.",
    category: "Gang Intelligence",
    priority: "high",
    score: 82,
    confidence: 0.72,
    sources: ["Social Media Analysis", "Gang Unit Intel", "Incident Correlation"],
    entities: [
      { type: "pattern", name: "Territory Expansion", id: "pat-gang-01" },
      { type: "location", name: "Sector 12 - East Side", id: "loc-s12" },
    ],
    suggestedActions: [
      "Brief gang unit supervisors",
      "Increase patrol presence in affected area",
      "Coordinate with neighboring agencies",
    ],
    assignedTo: "Gang Unit",
    status: "in_progress",
    generatedAt: new Date(Date.now() - 5400000).toISOString(),
    caseNumber: "2024-GANG-0234",
  },
];

export default function AutoLeadsPanel() {
  const [leads, setLeads] = useState<InvestigativeLead[]>(mockLeads);
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [selectedLead, setSelectedLead] = useState<InvestigativeLead | null>(null);

  const filteredLeads = leads.filter((lead) => {
    if (filterPriority !== "all" && lead.priority !== filterPriority) return false;
    if (filterStatus !== "all" && lead.status !== filterStatus) return false;
    return true;
  });

  const handleAssign = (leadId: string, assignee: string) => {
    setLeads((prev) =>
      prev.map((lead) =>
        lead.id === leadId
          ? { ...lead, assignedTo: assignee, status: "assigned" as const }
          : lead
      )
    );
  };

  const handleStatusChange = (leadId: string, status: InvestigativeLead["status"]) => {
    setLeads((prev) =>
      prev.map((lead) => (lead.id === leadId ? { ...lead, status } : lead))
    );
  };

  const leadCounts = {
    total: leads.length,
    new: leads.filter((l) => l.status === "new").length,
    assigned: leads.filter((l) => l.status === "assigned").length,
    inProgress: leads.filter((l) => l.status === "in_progress").length,
    completed: leads.filter((l) => l.status === "completed").length,
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold">Auto-Generated Leads</h2>
          {leadCounts.new > 0 && (
            <span className="bg-purple-600 text-white px-2 py-1 rounded-full text-xs">
              {leadCounts.new} new
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Priority:</span>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="new">New</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2 mb-4">
        <div className="bg-gray-800 border border-gray-700 rounded p-3 text-center">
          <div className="text-2xl font-bold text-white">{leadCounts.total}</div>
          <div className="text-xs text-gray-400">Total Leads</div>
        </div>
        <div className="bg-purple-900/50 border border-purple-700 rounded p-3 text-center">
          <div className="text-2xl font-bold text-purple-300">{leadCounts.new}</div>
          <div className="text-xs text-gray-400">New</div>
        </div>
        <div className="bg-blue-900/50 border border-blue-700 rounded p-3 text-center">
          <div className="text-2xl font-bold text-blue-300">{leadCounts.assigned}</div>
          <div className="text-xs text-gray-400">Assigned</div>
        </div>
        <div className="bg-yellow-900/50 border border-yellow-700 rounded p-3 text-center">
          <div className="text-2xl font-bold text-yellow-300">{leadCounts.inProgress}</div>
          <div className="text-xs text-gray-400">In Progress</div>
        </div>
        <div className="bg-green-900/50 border border-green-700 rounded p-3 text-center">
          <div className="text-2xl font-bold text-green-300">{leadCounts.completed}</div>
          <div className="text-xs text-gray-400">Completed</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-3">
          {filteredLeads.map((lead) => (
            <div
              key={lead.id}
              className={`bg-gray-800 border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedLead?.id === lead.id
                  ? "border-blue-500"
                  : "border-gray-700 hover:border-gray-600"
              }`}
              onClick={() => setSelectedLead(lead)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`${priorityColors[lead.priority]} px-2 py-0.5 rounded text-xs font-medium`}
                  >
                    {lead.priority.toUpperCase()}
                  </span>
                  <span
                    className={`${statusColors[lead.status]} px-2 py-0.5 rounded text-xs font-medium text-white`}
                  >
                    {lead.status.replace("_", " ").toUpperCase()}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  Score: {lead.score}
                </span>
              </div>
              <h3 className="font-semibold text-white mb-1">{lead.title}</h3>
              <p className="text-sm text-gray-400 line-clamp-2">
                {lead.description}
              </p>
              <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>{lead.category}</span>
                <span>{new Date(lead.generatedAt).toLocaleString()}</span>
              </div>
              {lead.assignedTo && (
                <div className="text-xs text-green-400 mt-1">
                  Assigned to: {lead.assignedTo}
                </div>
              )}
            </div>
          ))}
        </div>

        {selectedLead ? (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Lead Details</h3>
              <div className="flex items-center gap-2">
                <span
                  className={`${priorityColors[selectedLead.priority]} px-2 py-0.5 rounded text-xs font-medium`}
                >
                  {selectedLead.priority.toUpperCase()}
                </span>
                <span className="text-sm text-gray-400">
                  Confidence: {(selectedLead.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <h4 className="font-medium text-white mb-2">{selectedLead.title}</h4>
            <p className="text-sm text-gray-300 mb-4">{selectedLead.description}</p>

            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-gray-400 mb-2">
                  Intelligence Sources
                </div>
                <div className="flex flex-wrap gap-1">
                  {selectedLead.sources.map((source, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-900 text-blue-300 px-2 py-1 rounded text-xs"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-sm font-medium text-gray-400 mb-2">
                  Related Entities
                </div>
                <div className="space-y-1">
                  {selectedLead.entities.map((entity) => (
                    <div
                      key={entity.id}
                      className="bg-gray-700 px-3 py-2 rounded text-sm"
                    >
                      <span className="text-gray-400">{entity.type}:</span>{" "}
                      {entity.name}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-sm font-medium text-gray-400 mb-2">
                  Suggested Actions
                </div>
                <ul className="space-y-1">
                  {selectedLead.suggestedActions.map((action, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-gray-300 flex items-start gap-2"
                    >
                      <span className="text-blue-400">•</span>
                      {action}
                    </li>
                  ))}
                </ul>
              </div>

              {selectedLead.caseNumber && (
                <div>
                  <div className="text-sm font-medium text-gray-400">
                    Case Number
                  </div>
                  <div className="text-sm text-white">{selectedLead.caseNumber}</div>
                </div>
              )}

              <div className="pt-4 border-t border-gray-700">
                <div className="flex items-center gap-2">
                  {selectedLead.status === "new" && (
                    <button
                      onClick={() => handleAssign(selectedLead.id, "Current User")}
                      className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm"
                    >
                      Assign to Me
                    </button>
                  )}
                  {selectedLead.status === "assigned" && (
                    <button
                      onClick={() =>
                        handleStatusChange(selectedLead.id, "in_progress")
                      }
                      className="bg-yellow-600 hover:bg-yellow-500 text-black px-4 py-2 rounded text-sm"
                    >
                      Start Working
                    </button>
                  )}
                  {selectedLead.status === "in_progress" && (
                    <button
                      onClick={() =>
                        handleStatusChange(selectedLead.id, "completed")
                      }
                      className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded text-sm"
                    >
                      Mark Complete
                    </button>
                  )}
                  {selectedLead.status !== "dismissed" &&
                    selectedLead.status !== "completed" && (
                      <button
                        onClick={() =>
                          handleStatusChange(selectedLead.id, "dismissed")
                        }
                        className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm"
                      >
                        Dismiss
                      </button>
                    )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center justify-center">
            <p className="text-gray-400">Select a lead to view details</p>
          </div>
        )}
      </div>
    </div>
  );
}
