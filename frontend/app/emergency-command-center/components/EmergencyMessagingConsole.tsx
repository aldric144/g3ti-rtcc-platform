"use client";

import React, { useState } from "react";

interface AlertPreview {
  alert_id: string;
  alert_type: string;
  priority: number;
  title: string;
  message: string;
  affected_zones: string[];
  translations: Record<string, string>;
  distribution_channels: string[];
  recipients_count: number;
}

export default function EmergencyMessagingConsole() {
  const [alertType, setAlertType] = useState("evacuation_order");
  const [priority, setPriority] = useState(4);
  const [selectedZones, setSelectedZones] = useState<string[]>(["Zone_A"]);
  const [customMessage, setCustomMessage] = useState("");
  const [alertPreview, setAlertPreview] = useState<AlertPreview | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [loading, setLoading] = useState(false);

  const alertTypes = [
    { value: "evacuation_order", label: "Evacuation Order", icon: "🚨" },
    { value: "evacuation_advisory", label: "Evacuation Advisory", icon: "⚠️" },
    { value: "shelter_in_place", label: "Shelter in Place", icon: "🏠" },
    { value: "water_advisory", label: "Water Advisory", icon: "💧" },
    { value: "boil_water", label: "Boil Water Notice", icon: "🔥" },
    { value: "road_closure", label: "Road Closure", icon: "🚧" },
    { value: "all_clear", label: "All Clear", icon: "✅" },
  ];

  const zones = [
    "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
    "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
  ];

  const languages = [
    { code: "en", name: "English", flag: "🇺🇸" },
    { code: "es", name: "Spanish", flag: "🇪🇸" },
    { code: "ht", name: "Haitian Creole", flag: "🇭🇹" },
  ];

  const distributionChannels = [
    { id: "reverse_911", name: "Reverse 911", icon: "📞" },
    { id: "text_alert", name: "Text Alert", icon: "📱" },
    { id: "social_media", name: "Social Media", icon: "📢" },
    { id: "sirens", name: "Sirens", icon: "🔊" },
    { id: "radio", name: "Radio", icon: "📻" },
    { id: "tv", name: "TV", icon: "📺" },
  ];

  const toggleZone = (zone: string) => {
    setSelectedZones((prev) =>
      prev.includes(zone)
        ? prev.filter((z) => z !== zone)
        : [...prev, zone]
    );
  };

  const generatePreview = () => {
    const zonePopulations: Record<string, number> = {
      Zone_A: 3500, Zone_B: 4200, Zone_C: 3800, Zone_D: 2900, Zone_E: 4500,
      Zone_F: 3200, Zone_G: 2800, Zone_H: 3600, Zone_I: 4100, Zone_J: 3400,
    };

    const totalRecipients = selectedZones.reduce(
      (sum, zone) => sum + (zonePopulations[zone] || 0),
      0
    );

    const templates: Record<string, Record<string, string>> = {
      evacuation_order: {
        en: `MANDATORY EVACUATION ORDER for ${selectedZones.join(", ")}. Leave immediately. Proceed to Riviera Beach Community Center. For assistance call 561-845-4000.`,
        es: `ORDEN DE EVACUACIÓN OBLIGATORIA para ${selectedZones.join(", ")}. Salga inmediatamente. Diríjase a Riviera Beach Community Center. Para asistencia llame al 561-845-4000.`,
        ht: `LÒD EVAKUASYON OBLIGATWA pou ${selectedZones.join(", ")}. Kite imedyatman. Ale nan Riviera Beach Community Center. Pou asistans rele 561-845-4000.`,
      },
      shelter_in_place: {
        en: `SHELTER IN PLACE for ${selectedZones.join(", ")}. Stay indoors. Close windows and doors. Await further instructions.`,
        es: `REFUGIARSE EN EL LUGAR para ${selectedZones.join(", ")}. Permanezca adentro. Cierre ventanas y puertas. Espere más instrucciones.`,
        ht: `RETE ANNDAN pou ${selectedZones.join(", ")}. Rete anndan kay. Fèmen fenèt ak pòt. Tann plis enstriksyon.`,
      },
      water_advisory: {
        en: `WATER ADVISORY for ${selectedZones.join(", ")}. Do not drink tap water until further notice. Use bottled water only.`,
        es: `AVISO DE AGUA para ${selectedZones.join(", ")}. No beba agua del grifo hasta nuevo aviso. Use solo agua embotellada.`,
        ht: `KONSÈY DLO pou ${selectedZones.join(", ")}. Pa bwè dlo tiyo jiskaske yo di ou. Sèvi ak dlo nan boutèy sèlman.`,
      },
      all_clear: {
        en: `ALL CLEAR for ${selectedZones.join(", ")}. The emergency has ended. It is safe to return to normal activities.`,
        es: `TODO DESPEJADO para ${selectedZones.join(", ")}. La emergencia ha terminado. Es seguro volver a las actividades normales.`,
        ht: `TOUT KLÈ pou ${selectedZones.join(", ")}. Ijans lan fini. Li an sekirite pou retounen nan aktivite nòmal yo.`,
      },
    };

    const message = customMessage || templates[alertType]?.en || `Emergency alert for ${selectedZones.join(", ")}`;

    const channels = priority >= 4
      ? ["reverse_911", "text_alert", "sirens", "social_media", "radio", "tv"]
      : priority >= 3
      ? ["reverse_911", "text_alert", "social_media"]
      : ["text_alert", "social_media"];

    setAlertPreview({
      alert_id: `EA-${Date.now().toString(36).toUpperCase()}`,
      alert_type: alertType,
      priority,
      title: `${priority >= 4 ? "EMERGENCY" : priority >= 3 ? "WARNING" : "ADVISORY"}: ${alertTypes.find(t => t.value === alertType)?.label}`,
      message,
      affected_zones: selectedZones,
      translations: templates[alertType] || { en: message, es: `[ES] ${message}`, ht: `[HT] ${message}` },
      distribution_channels: channels,
      recipients_count: totalRecipients,
    });
  };

  const getPriorityLabel = (p: number) => {
    switch (p) {
      case 5: return "Emergency";
      case 4: return "Warning";
      case 3: return "Watch";
      case 2: return "Advisory";
      default: return "Informational";
    }
  };

  const getPriorityColor = (p: number) => {
    switch (p) {
      case 5: return "bg-red-500";
      case 4: return "bg-orange-500";
      case 3: return "bg-yellow-500";
      case 2: return "bg-blue-500";
      default: return "bg-green-500";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Create Emergency Alert</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Alert Type
              </label>
              <select
                value={alertType}
                onChange={(e) => setAlertType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              >
                {alertTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Priority: {getPriorityLabel(priority)}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400">
                <span>Info</span>
                <span>Advisory</span>
                <span>Watch</span>
                <span>Warning</span>
                <span>Emergency</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Affected Zones
              </label>
              <div className="grid grid-cols-5 gap-2">
                {zones.map((zone) => (
                  <button
                    key={zone}
                    onClick={() => toggleZone(zone)}
                    className={`px-2 py-1 rounded text-xs ${
                      selectedZones.includes(zone)
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                  >
                    {zone.replace("Zone_", "")}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Custom Message (optional)
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="Leave empty to use template..."
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white h-24"
              />
            </div>

            <button
              onClick={generatePreview}
              disabled={selectedZones.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Generate Preview
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Multi-Language Preview</h2>
          {alertPreview ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span
                  className={`px-3 py-1 rounded ${getPriorityColor(
                    alertPreview.priority
                  )}`}
                >
                  {alertPreview.title}
                </span>
                <span className="text-sm text-gray-400">
                  {alertPreview.recipients_count.toLocaleString()} recipients
                </span>
              </div>

              <div className="flex space-x-2">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => setSelectedLanguage(lang.code)}
                    className={`px-3 py-1 rounded text-sm ${
                      selectedLanguage === lang.code
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                  >
                    {lang.flag} {lang.name}
                  </button>
                ))}
              </div>

              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-2">Message Preview:</p>
                <p className="text-white">
                  {alertPreview.translations[selectedLanguage] ||
                    alertPreview.message}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-400 mb-2">Distribution Channels:</p>
                <div className="flex flex-wrap gap-2">
                  {alertPreview.distribution_channels.map((channel) => {
                    const channelInfo = distributionChannels.find(
                      (c) => c.id === channel
                    );
                    return (
                      <span
                        key={channel}
                        className="bg-gray-700 px-3 py-1 rounded text-sm"
                      >
                        {channelInfo?.icon} {channelInfo?.name || channel}
                      </span>
                    );
                  })}
                </div>
              </div>

              <button
                className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                🚨 Send Emergency Alert
              </button>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <p className="text-4xl mb-2">📢</p>
              <p>Configure and generate preview</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Distribution Log</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-3">Time</th>
                <th className="pb-3">Alert Type</th>
                <th className="pb-3">Zones</th>
                <th className="pb-3">Channels</th>
                <th className="pb-3">Recipients</th>
                <th className="pb-3">Delivery Rate</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-700">
                <td className="py-3 text-sm">12:45 PM</td>
                <td className="py-3">Evacuation Advisory</td>
                <td className="py-3">Zone_A, Zone_B</td>
                <td className="py-3">📞 📱 📢</td>
                <td className="py-3">7,700</td>
                <td className="py-3">
                  <span className="text-green-400">92%</span>
                </td>
                <td className="py-3">
                  <span className="bg-green-600 px-2 py-1 rounded text-xs">
                    Delivered
                  </span>
                </td>
              </tr>
              <tr className="border-b border-gray-700">
                <td className="py-3 text-sm">11:30 AM</td>
                <td className="py-3">Weather Warning</td>
                <td className="py-3">All Zones</td>
                <td className="py-3">📱 📢 📻</td>
                <td className="py-3">36,000</td>
                <td className="py-3">
                  <span className="text-green-400">88%</span>
                </td>
                <td className="py-3">
                  <span className="bg-green-600 px-2 py-1 rounded text-xs">
                    Delivered
                  </span>
                </td>
              </tr>
              <tr className="border-b border-gray-700">
                <td className="py-3 text-sm">10:15 AM</td>
                <td className="py-3">Shelter Update</td>
                <td className="py-3">Zone_E, Zone_F</td>
                <td className="py-3">📱 📢</td>
                <td className="py-3">7,700</td>
                <td className="py-3">
                  <span className="text-green-400">95%</span>
                </td>
                <td className="py-3">
                  <span className="bg-green-600 px-2 py-1 rounded text-xs">
                    Delivered
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Social Signal Monitor</h2>
          <div className="space-y-3">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Crisis Report</span>
                <span className="text-xs text-red-400">High Urgency</span>
              </div>
              <p className="text-sm text-gray-400">
                "Need help! Flooding on Blue Heron Blvd, car stuck..."
              </p>
              <p className="text-xs text-gray-500 mt-1">Zone_A | Twitter | 2 min ago</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Resource Request</span>
                <span className="text-xs text-yellow-400">Medium Urgency</span>
              </div>
              <p className="text-sm text-gray-400">
                "Where can we get water? Store shelves empty..."
              </p>
              <p className="text-xs text-gray-500 mt-1">Zone_C | Facebook | 15 min ago</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Rumor Detected</span>
                <span className="text-xs text-orange-400">Needs Debunking</span>
              </div>
              <p className="text-sm text-gray-400">
                "Heard that the bridge collapsed, is it true?"
              </p>
              <p className="text-xs text-gray-500 mt-1">Zone_B | Twitter | 30 min ago</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Rumor Debunking Queue</h2>
          <div className="space-y-3">
            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-yellow-400">Pending Review</span>
                <button className="text-xs bg-blue-600 px-2 py-1 rounded">
                  Create Response
                </button>
              </div>
              <p className="text-sm text-gray-300 mb-2">
                Rumor: "Bridge on 13th Street collapsed"
              </p>
              <p className="text-xs text-gray-400">
                Fact: Bridge is intact and open. Minor flooding on approach roads.
              </p>
            </div>
            <div className="bg-green-900/30 border border-green-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-green-400">Debunked</span>
                <span className="text-xs text-gray-400">Distributed 1h ago</span>
              </div>
              <p className="text-sm text-gray-300 mb-2">
                Rumor: "City water contaminated"
              </p>
              <p className="text-xs text-gray-400">
                Official: Water is safe. Boil water notice only for Zone_E.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
