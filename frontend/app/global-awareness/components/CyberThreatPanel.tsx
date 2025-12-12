"use client";

import React, { useState, useEffect } from "react";

interface CyberSignal {
  signal_id: string;
  threat_type: string;
  threat_actor: string | null;
  target_sector: string;
  target_country: string;
  attack_vector: string;
  iocs: string[];
  severity: number;
  cve_ids: string[];
  ttps: string[];
  timestamp: string;
  confidence_score: number;
}

interface ThreatActorProfile {
  name: string;
  aliases: string[];
  origin: string;
  motivation: string;
  targets: string[];
  capabilities: string[];
  active_campaigns: number;
  threat_level: string;
}

const THREAT_TYPES = [
  { id: "ransomware", label: "Ransomware", color: "bg-red-500" },
  { id: "apt", label: "APT", color: "bg-purple-500" },
  { id: "ddos", label: "DDoS", color: "bg-orange-500" },
  { id: "phishing", label: "Phishing", color: "bg-yellow-500" },
  { id: "malware", label: "Malware", color: "bg-pink-500" },
  { id: "zero_day", label: "Zero-Day", color: "bg-red-600" },
  { id: "supply_chain", label: "Supply Chain", color: "bg-blue-500" },
];

const TARGET_SECTORS = [
  "Energy",
  "Finance",
  "Healthcare",
  "Government",
  "Defense",
  "Technology",
  "Manufacturing",
  "Transportation",
  "Telecommunications",
  "Critical Infrastructure",
];

export default function CyberThreatPanel() {
  const [signals, setSignals] = useState<CyberSignal[]>([]);
  const [threatActors, setThreatActors] = useState<ThreatActorProfile[]>([]);
  const [selectedThreatType, setSelectedThreatType] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<"signals" | "actors" | "iocs">("signals");

  useEffect(() => {
    const mockSignals: CyberSignal[] = [
      {
        signal_id: "CYB-001",
        threat_type: "ransomware",
        threat_actor: "LockBit 3.0",
        target_sector: "Healthcare",
        target_country: "United States",
        attack_vector: "Phishing Email",
        iocs: ["192.168.1.100", "malware.exe", "c2.badactor.com"],
        severity: 5,
        cve_ids: ["CVE-2024-1234"],
        ttps: ["T1566", "T1486", "T1027"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.92,
      },
      {
        signal_id: "CYB-002",
        threat_type: "apt",
        threat_actor: "APT29",
        target_sector: "Government",
        target_country: "Germany",
        attack_vector: "Supply Chain Compromise",
        iocs: ["apt29-c2.example.com", "backdoor.dll"],
        severity: 5,
        cve_ids: ["CVE-2024-5678", "CVE-2024-9012"],
        ttps: ["T1195", "T1071", "T1059"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.88,
      },
      {
        signal_id: "CYB-003",
        threat_type: "ddos",
        threat_actor: null,
        target_sector: "Finance",
        target_country: "United Kingdom",
        attack_vector: "Botnet",
        iocs: ["botnet-c2.example.net"],
        severity: 4,
        cve_ids: [],
        ttps: ["T1498", "T1499"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.85,
      },
      {
        signal_id: "CYB-004",
        threat_type: "zero_day",
        threat_actor: "Unknown",
        target_sector: "Technology",
        target_country: "Japan",
        attack_vector: "Browser Exploit",
        iocs: ["exploit-kit.example.org"],
        severity: 5,
        cve_ids: ["CVE-2024-0DAY"],
        ttps: ["T1189", "T1203"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.75,
      },
      {
        signal_id: "CYB-005",
        threat_type: "supply_chain",
        threat_actor: "Lazarus Group",
        target_sector: "Defense",
        target_country: "South Korea",
        attack_vector: "Compromised Software Update",
        iocs: ["lazarus-c2.example.com", "trojan.exe"],
        severity: 5,
        cve_ids: ["CVE-2024-3456"],
        ttps: ["T1195.002", "T1071", "T1105"],
        timestamp: new Date().toISOString(),
        confidence_score: 0.90,
      },
    ];
    setSignals(mockSignals);

    const mockActors: ThreatActorProfile[] = [
      {
        name: "APT29 (Cozy Bear)",
        aliases: ["The Dukes", "CozyDuke", "YTTRIUM"],
        origin: "Russia",
        motivation: "Espionage",
        targets: ["Government", "Defense", "Think Tanks"],
        capabilities: ["Custom Malware", "Zero-Day Exploits", "Supply Chain"],
        active_campaigns: 3,
        threat_level: "Critical",
      },
      {
        name: "Lazarus Group",
        aliases: ["Hidden Cobra", "Zinc", "APT38"],
        origin: "North Korea",
        motivation: "Financial / Espionage",
        targets: ["Finance", "Cryptocurrency", "Defense"],
        capabilities: ["Ransomware", "Banking Trojans", "Destructive Malware"],
        active_campaigns: 5,
        threat_level: "Critical",
      },
      {
        name: "LockBit 3.0",
        aliases: ["LockBit Black"],
        origin: "Unknown (RaaS)",
        motivation: "Financial",
        targets: ["Healthcare", "Manufacturing", "Education"],
        capabilities: ["Ransomware-as-a-Service", "Data Exfiltration"],
        active_campaigns: 12,
        threat_level: "High",
      },
      {
        name: "APT41 (Double Dragon)",
        aliases: ["Winnti", "Barium", "Wicked Panda"],
        origin: "China",
        motivation: "Espionage / Financial",
        targets: ["Technology", "Healthcare", "Gaming"],
        capabilities: ["Supply Chain Attacks", "Custom Malware", "Rootkits"],
        active_campaigns: 4,
        threat_level: "Critical",
      },
    ];
    setThreatActors(mockActors);
  }, []);

  const getSeverityColor = (severity: number) => {
    if (severity >= 5) return "text-red-500";
    if (severity >= 4) return "text-orange-500";
    if (severity >= 3) return "text-yellow-500";
    return "text-green-500";
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case "Critical": return "bg-red-500";
      case "High": return "bg-orange-500";
      case "Medium": return "bg-yellow-500";
      case "Low": return "bg-green-500";
      default: return "bg-gray-500";
    }
  };

  const filteredSignals = signals.filter(s => {
    if (selectedThreatType && s.threat_type !== selectedThreatType) return false;
    if (selectedSector && s.target_sector !== selectedSector) return false;
    return true;
  });

  const allIOCs = signals.flatMap(s => s.iocs.map(ioc => ({
    ioc,
    signal_id: s.signal_id,
    threat_type: s.threat_type,
    threat_actor: s.threat_actor,
  })));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Threat Filters</h2>

          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-400 mb-2">Threat Type</h3>
            <div className="space-y-1">
              <button
                onClick={() => setSelectedThreatType(null)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${
                  selectedThreatType === null ? "bg-blue-600" : "bg-gray-700 hover:bg-gray-600"
                }`}
              >
                All Types
              </button>
              {THREAT_TYPES.map(type => (
                <button
                  key={type.id}
                  onClick={() => setSelectedThreatType(type.id)}
                  className={`w-full text-left px-3 py-2 rounded text-sm flex items-center justify-between ${
                    selectedThreatType === type.id ? "bg-blue-600" : "bg-gray-700 hover:bg-gray-600"
                  }`}
                >
                  <span>{type.label}</span>
                  <span className={`w-3 h-3 rounded-full ${type.color}`} />
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-2">Target Sector</h3>
            <select
              value={selectedSector || ""}
              onChange={(e) => setSelectedSector(e.target.value || null)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            >
              <option value="">All Sectors</option>
              {TARGET_SECTORS.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>

          <div className="mt-6 p-3 bg-gray-700/50 rounded-lg">
            <h3 className="text-sm font-medium mb-2">Statistics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Signals</span>
                <span className="font-bold">{signals.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Critical Severity</span>
                <span className="font-bold text-red-500">
                  {signals.filter(s => s.severity >= 5).length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Actors</span>
                <span className="font-bold">{threatActors.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total IOCs</span>
                <span className="font-bold">{allIOCs.length}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Cyber Threat Intelligence</h2>
            <div className="flex space-x-2">
              {(["signals", "actors", "iocs"] as const).map(view => (
                <button
                  key={view}
                  onClick={() => setActiveView(view)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeView === view
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {view === "iocs" ? "IOCs" : view.charAt(0).toUpperCase() + view.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {activeView === "signals" && (
            <div className="space-y-3">
              {filteredSignals.map(signal => (
                <div key={signal.signal_id} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          THREAT_TYPES.find(t => t.id === signal.threat_type)?.color || "bg-gray-500"
                        }`}>
                          {signal.threat_type.replace(/_/g, " ")}
                        </span>
                        <span className="font-mono text-xs text-gray-400">{signal.signal_id}</span>
                        <span className={`font-bold ${getSeverityColor(signal.severity)}`}>
                          Sev {signal.severity}
                        </span>
                      </div>
                      <div className="mt-2">
                        <span className="text-gray-400">Actor: </span>
                        <span className="font-medium">{signal.threat_actor || "Unknown"}</span>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">
                      {(signal.confidence_score * 100).toFixed(0)}% confidence
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
                    <div>
                      <span className="text-gray-400">Target Sector</span>
                      <p className="font-medium">{signal.target_sector}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Target Country</span>
                      <p className="font-medium">{signal.target_country}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Attack Vector</span>
                      <p className="font-medium">{signal.attack_vector}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">CVEs</span>
                      <p className="font-medium">{signal.cve_ids.length > 0 ? signal.cve_ids.join(", ") : "None"}</p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <span className="text-gray-400 text-sm">TTPs: </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {signal.ttps.map(ttp => (
                        <span key={ttp} className="px-2 py-0.5 bg-purple-600/30 rounded text-xs">
                          {ttp}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-3">
                    <span className="text-gray-400 text-sm">IOCs: </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {signal.iocs.map(ioc => (
                        <span key={ioc} className="px-2 py-0.5 bg-gray-600 rounded text-xs font-mono">
                          {ioc}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeView === "actors" && (
            <div className="space-y-3">
              {threatActors.map(actor => (
                <div key={actor.name} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{actor.name}</h3>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {actor.aliases.map(alias => (
                          <span key={alias} className="px-2 py-0.5 bg-gray-600 rounded text-xs">
                            {alias}
                          </span>
                        ))}
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm ${getThreatLevelColor(actor.threat_level)}`}>
                      {actor.threat_level}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 text-sm">
                    <div>
                      <span className="text-gray-400">Origin</span>
                      <p className="font-medium">{actor.origin}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Motivation</span>
                      <p className="font-medium">{actor.motivation}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Active Campaigns</span>
                      <p className="font-medium text-orange-400">{actor.active_campaigns}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Capabilities</span>
                      <p className="font-medium">{actor.capabilities.length}</p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <span className="text-gray-400 text-sm">Target Sectors: </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {actor.targets.map(target => (
                        <span key={target} className="px-2 py-0.5 bg-blue-600/30 rounded text-xs">
                          {target}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-3">
                    <span className="text-gray-400 text-sm">Capabilities: </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {actor.capabilities.map(cap => (
                        <span key={cap} className="px-2 py-0.5 bg-red-600/30 rounded text-xs">
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeView === "iocs" && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-gray-700">
                    <th className="pb-2 pr-4">IOC</th>
                    <th className="pb-2 pr-4">Type</th>
                    <th className="pb-2 pr-4">Signal</th>
                    <th className="pb-2 pr-4">Threat Type</th>
                    <th className="pb-2">Actor</th>
                  </tr>
                </thead>
                <tbody>
                  {allIOCs.map((item, index) => (
                    <tr key={index} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                      <td className="py-2 pr-4 font-mono text-xs">{item.ioc}</td>
                      <td className="py-2 pr-4">
                        <span className="px-2 py-0.5 bg-gray-600 rounded text-xs">
                          {item.ioc.includes(".") && item.ioc.includes("/") ? "URL" :
                           item.ioc.includes(".") && !item.ioc.includes("/") && /\d/.test(item.ioc) ? "IP" :
                           item.ioc.includes(".") ? "Domain" : "File"}
                        </span>
                      </td>
                      <td className="py-2 pr-4 font-mono text-xs">{item.signal_id}</td>
                      <td className="py-2 pr-4">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          THREAT_TYPES.find(t => t.id === item.threat_type)?.color || "bg-gray-500"
                        }`}>
                          {item.threat_type}
                        </span>
                      </td>
                      <td className="py-2">{item.threat_actor || "Unknown"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
