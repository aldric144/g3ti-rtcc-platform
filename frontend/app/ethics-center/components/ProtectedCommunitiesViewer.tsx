"use client";

import React, { useState } from "react";

interface CommunityProfile {
  type: string;
  displayName: string;
  populationEstimate: number;
  populationPercentage: number;
  geographicConcentration: string[];
  safeguardLevel: string;
  biasSensitivityMultiplier: number;
  surveillanceLimitFactor: number;
  engagementRequirements: string[];
  liaisonContacts: string[];
  historicalConcerns: string[];
}

interface SafeguardTrigger {
  id: string;
  timestamp: string;
  communityType: string;
  ruleName: string;
  actionRequired: string;
  escalationLevel: string;
  status: string;
}

const communityProfiles: CommunityProfile[] = [
  {
    type: "BLACK_COMMUNITY",
    displayName: "Black Community",
    populationEstimate: 25056,
    populationPercentage: 66.0,
    geographicConcentration: ["Downtown", "Singer Island", "Riviera Beach Heights"],
    safeguardLevel: "HIGH",
    biasSensitivityMultiplier: 1.5,
    surveillanceLimitFactor: 0.7,
    engagementRequirements: [
      "Quarterly community meetings",
      "Annual disparity report",
      "Community advisory board representation",
    ],
    liaisonContacts: ["Community Relations Unit", "NAACP Riviera Beach Chapter"],
    historicalConcerns: [
      "Historical over-policing",
      "Disparate enforcement rates",
      "Traffic stop disparities",
    ],
  },
  {
    type: "HISPANIC_COMMUNITY",
    displayName: "Hispanic Community",
    populationEstimate: 3037,
    populationPercentage: 8.0,
    geographicConcentration: ["West Riviera Beach", "Industrial District"],
    safeguardLevel: "ELEVATED",
    biasSensitivityMultiplier: 1.3,
    surveillanceLimitFactor: 0.8,
    engagementRequirements: [
      "Bilingual outreach materials",
      "Spanish-speaking liaison",
      "Immigration policy transparency",
    ],
    liaisonContacts: ["Hispanic Affairs Office", "Community Relations Unit"],
    historicalConcerns: [
      "Language barriers",
      "Immigration enforcement concerns",
      "Underreporting of crimes",
    ],
  },
  {
    type: "LGBTQ_YOUTH",
    displayName: "LGBTQ+ Youth",
    populationEstimate: 500,
    populationPercentage: 1.3,
    geographicConcentration: ["Citywide"],
    safeguardLevel: "HIGH",
    biasSensitivityMultiplier: 1.5,
    surveillanceLimitFactor: 0.6,
    engagementRequirements: [
      "LGBTQ+ sensitivity training",
      "Safe space protocols",
      "Mental health co-responder availability",
    ],
    liaisonContacts: ["Youth Services", "LGBTQ+ Resource Center"],
    historicalConcerns: [
      "Harassment and bullying",
      "Mental health crisis response",
      "Family rejection situations",
    ],
  },
  {
    type: "PEOPLE_WITH_DISABILITIES",
    displayName: "People with Disabilities",
    populationEstimate: 4556,
    populationPercentage: 12.0,
    geographicConcentration: ["Citywide"],
    safeguardLevel: "HIGH",
    biasSensitivityMultiplier: 1.4,
    surveillanceLimitFactor: 0.7,
    engagementRequirements: [
      "ADA compliance verification",
      "Disability awareness training",
      "Accessible communication options",
    ],
    liaisonContacts: ["ADA Coordinator", "Disability Rights Florida"],
    historicalConcerns: [
      "ADA compliance",
      "Communication barriers",
      "Use of force incidents",
    ],
  },
  {
    type: "VETERANS",
    displayName: "Veterans",
    populationEstimate: 2278,
    populationPercentage: 6.0,
    geographicConcentration: ["Singer Island", "Riviera Beach Heights"],
    safeguardLevel: "ELEVATED",
    biasSensitivityMultiplier: 1.2,
    surveillanceLimitFactor: 0.85,
    engagementRequirements: [
      "Veteran-specific crisis intervention",
      "VA coordination protocols",
      "Veteran peer support availability",
    ],
    liaisonContacts: ["Veterans Affairs Liaison", "VA Medical Center"],
    historicalConcerns: [
      "PTSD-related incidents",
      "Mental health crisis response",
      "Homelessness",
    ],
  },
  {
    type: "FAITH_COMMUNITIES",
    displayName: "Faith Communities",
    populationEstimate: 20000,
    populationPercentage: 52.7,
    geographicConcentration: ["Citywide - 50+ places of worship"],
    safeguardLevel: "ELEVATED",
    biasSensitivityMultiplier: 1.2,
    surveillanceLimitFactor: 0.8,
    engagementRequirements: [
      "Interfaith council engagement",
      "House of worship security assessments",
      "Religious holiday awareness",
    ],
    liaisonContacts: ["Interfaith Council", "Community Relations Unit"],
    historicalConcerns: [
      "Religious freedom",
      "House of worship security",
      "Religious expression protection",
    ],
  },
  {
    type: "AGING_POPULATION",
    displayName: "Aging Population (65+)",
    populationEstimate: 5695,
    populationPercentage: 15.0,
    geographicConcentration: ["Singer Island", "Riviera Beach Marina"],
    safeguardLevel: "ELEVATED",
    biasSensitivityMultiplier: 1.2,
    surveillanceLimitFactor: 0.85,
    engagementRequirements: [
      "Elder abuse prevention protocols",
      "Senior center partnerships",
      "Medical alert coordination",
    ],
    liaisonContacts: ["Senior Services", "Adult Protective Services"],
    historicalConcerns: [
      "Elder abuse",
      "Financial exploitation",
      "Medical emergency response",
    ],
  },
];

const mockSafeguardTriggers: SafeguardTrigger[] = [
  {
    id: "sg-001",
    timestamp: "2024-01-15T14:30:00Z",
    communityType: "BLACK_COMMUNITY",
    ruleName: "Disparate Impact Review",
    actionRequired: "Supervisor review and documentation",
    escalationLevel: "SUPERVISOR",
    status: "PENDING",
  },
  {
    id: "sg-002",
    timestamp: "2024-01-15T13:45:00Z",
    communityType: "LGBTQ_YOUTH",
    ruleName: "Youth Protection Protocol",
    actionRequired: "Engage youth services specialist",
    escalationLevel: "SUPERVISOR",
    status: "COMPLETED",
  },
  {
    id: "sg-003",
    timestamp: "2024-01-15T12:15:00Z",
    communityType: "PEOPLE_WITH_DISABILITIES",
    ruleName: "ADA Compliance Check",
    actionRequired: "Verify ADA accommodations provided",
    escalationLevel: "SUPERVISOR",
    status: "COMPLETED",
  },
];

export default function ProtectedCommunitiesViewer() {
  const [selectedCommunity, setSelectedCommunity] = useState<CommunityProfile | null>(communityProfiles[0]);
  const [activeTab, setActiveTab] = useState<"profiles" | "triggers">("profiles");

  const getSafeguardLevelColor = (level: string) => {
    switch (level) {
      case "MAXIMUM":
        return "bg-red-500";
      case "HIGH":
        return "bg-orange-500";
      case "ELEVATED":
        return "bg-yellow-500";
      case "STANDARD":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const getSafeguardLevelBadge = (level: string) => {
    switch (level) {
      case "MAXIMUM":
        return "bg-red-900 text-red-300";
      case "HIGH":
        return "bg-orange-900 text-orange-300";
      case "ELEVATED":
        return "bg-yellow-900 text-yellow-300";
      case "STANDARD":
        return "bg-green-900 text-green-300";
      default:
        return "bg-gray-900 text-gray-300";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-sm text-gray-400">Total Population</div>
          <div className="text-2xl font-bold text-white">37,964</div>
          <div className="text-xs text-gray-500 mt-1">Riviera Beach, FL 33404</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-700">
          <div className="text-sm text-gray-400">High Protection</div>
          <div className="text-2xl font-bold text-orange-400">3</div>
          <div className="text-xs text-orange-500 mt-1">Communities</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-sm text-gray-400">Elevated Protection</div>
          <div className="text-2xl font-bold text-yellow-400">4</div>
          <div className="text-xs text-yellow-500 mt-1">Communities</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-700">
          <div className="text-sm text-gray-400">Active Safeguards</div>
          <div className="text-2xl font-bold text-blue-400">8</div>
          <div className="text-xs text-blue-500 mt-1">Rules enforced</div>
        </div>
      </div>

      <div className="flex space-x-2 border-b border-gray-700 pb-2">
        <button
          onClick={() => setActiveTab("profiles")}
          className={`px-4 py-2 rounded-t text-sm ${
            activeTab === "profiles" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Community Profiles
        </button>
        <button
          onClick={() => setActiveTab("triggers")}
          className={`px-4 py-2 rounded-t text-sm ${
            activeTab === "triggers" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Safeguard Triggers
        </button>
      </div>

      {activeTab === "profiles" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Protected Communities</h3>
            </div>
            <div className="divide-y divide-gray-700 max-h-[600px] overflow-y-auto">
              {communityProfiles.map((community) => (
                <div
                  key={community.type}
                  onClick={() => setSelectedCommunity(community)}
                  className={`p-4 cursor-pointer hover:bg-gray-750 transition-colors ${
                    selectedCommunity?.type === community.type ? "bg-gray-750" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className={`w-3 h-3 rounded-full ${getSafeguardLevelColor(community.safeguardLevel)}`}></span>
                      <div>
                        <div className="text-sm font-medium text-white">{community.displayName}</div>
                        <div className="text-xs text-gray-400">
                          {community.populationEstimate.toLocaleString()} ({community.populationPercentage}%)
                        </div>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded ${getSafeguardLevelBadge(community.safeguardLevel)}`}>
                      {community.safeguardLevel}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Community Details</h3>
            </div>
            {selectedCommunity ? (
              <div className="p-4 space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xl font-bold text-white">{selectedCommunity.displayName}</h4>
                    <p className="text-sm text-gray-400">
                      Population: {selectedCommunity.populationEstimate.toLocaleString()} ({selectedCommunity.populationPercentage}% of city)
                    </p>
                  </div>
                  <span className={`text-sm px-3 py-1 rounded ${getSafeguardLevelBadge(selectedCommunity.safeguardLevel)}`}>
                    {selectedCommunity.safeguardLevel} Protection
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Bias Sensitivity</div>
                    <div className="text-2xl font-bold text-white">{selectedCommunity.biasSensitivityMultiplier}x</div>
                    <div className="text-xs text-gray-500">Multiplier applied</div>
                  </div>
                  <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Surveillance Limit</div>
                    <div className="text-2xl font-bold text-white">{(selectedCommunity.surveillanceLimitFactor * 100).toFixed(0)}%</div>
                    <div className="text-xs text-gray-500">Of standard threshold</div>
                  </div>
                </div>

                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Geographic Concentration</h5>
                  <div className="flex flex-wrap gap-2">
                    {selectedCommunity.geographicConcentration.map((area, idx) => (
                      <span key={idx} className="text-xs bg-blue-900/30 text-blue-300 px-2 py-1 rounded border border-blue-700">
                        {area}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Historical Concerns</h5>
                  <div className="space-y-1">
                    {selectedCommunity.historicalConcerns.map((concern, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-sm text-gray-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                        <span>{concern}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Engagement Requirements</h5>
                  <div className="space-y-1">
                    {selectedCommunity.engagementRequirements.map((req, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-sm text-gray-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                        <span>{req}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Liaison Contacts</h5>
                  <div className="flex flex-wrap gap-2">
                    {selectedCommunity.liaisonContacts.map((contact, idx) => (
                      <span key={idx} className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                        {contact}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                Select a community to view details
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "triggers" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Recent Safeguard Triggers</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {mockSafeguardTriggers.map((trigger) => (
              <div key={trigger.id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`w-3 h-3 rounded-full ${
                      trigger.status === "PENDING" ? "bg-yellow-500 animate-pulse" : "bg-green-500"
                    }`}></span>
                    <div>
                      <div className="text-sm font-medium text-white">{trigger.ruleName}</div>
                      <div className="text-xs text-gray-400">
                        {trigger.communityType.replace(/_/g, " ")} • {new Date(trigger.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    trigger.status === "PENDING" ? "bg-yellow-900 text-yellow-300" : "bg-green-900 text-green-300"
                  }`}>
                    {trigger.status}
                  </span>
                </div>
                <div className="ml-6 text-sm text-gray-400">
                  <span className="text-gray-500">Action: </span>{trigger.actionRequired}
                </div>
                <div className="ml-6 text-xs text-gray-500 mt-1">
                  Escalation: {trigger.escalationLevel}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
