"use client";

import { useState } from "react";
import {
  FederalExportPanel,
  NDExExportViewer,
  ETraceExportViewer,
  SARSubmissionPanel,
  NCICReadinessPanel,
  CJISAuditLogViewer,
  AccessControlManager,
} from "./components";

type TabType =
  | "overview"
  | "ndex"
  | "etrace"
  | "sar"
  | "ncic"
  | "audit"
  | "access";

export default function FederalReadinessPage() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");

  const tabs = [
    { id: "overview" as TabType, label: "Overview", icon: "🏛️" },
    { id: "ndex" as TabType, label: "N-DEx Export", icon: "📤" },
    { id: "etrace" as TabType, label: "eTrace", icon: "🔫" },
    { id: "sar" as TabType, label: "SAR Submission", icon: "🚨" },
    { id: "ncic" as TabType, label: "NCIC Readiness", icon: "🔍" },
    { id: "audit" as TabType, label: "CJIS Audit Log", icon: "📋" },
    { id: "access" as TabType, label: "Access Control", icon: "🔐" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              Federal Integration Readiness
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              G3TI RTCC-UIP Phase 11 - Federal Data Exchange Framework
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-300">Systems Ready</span>
            </div>
            <div className="bg-blue-600 px-3 py-1 rounded text-sm">
              CJIS Compliant
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-800 border-b border-gray-700 px-6">
        <div className="flex space-x-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400 bg-gray-700/50"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-700/30"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {activeTab === "overview" && <FederalExportPanel />}
        {activeTab === "ndex" && <NDExExportViewer />}
        {activeTab === "etrace" && <ETraceExportViewer />}
        {activeTab === "sar" && <SARSubmissionPanel />}
        {activeTab === "ncic" && <NCICReadinessPanel />}
        {activeTab === "audit" && <CJISAuditLogViewer />}
        {activeTab === "access" && <AccessControlManager />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-4 mt-auto">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            <span>Federal Readiness Framework v1.0</span>
            <span className="mx-2">|</span>
            <span>CJIS Policy Areas 5, 7, 8, 10 Enforced</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>N-DEx v5.x Ready</span>
            <span>|</span>
            <span>ISE-SAR v1.5 Compliant</span>
            <span>|</span>
            <span>AES-256 Encryption</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
