"use client";

import { useState } from "react";

interface CityAdminInputFormProps {
  onEventCreated?: () => void;
}

type EventType = 
  | "festival"
  | "parade"
  | "school_dismissal"
  | "utility_maintenance"
  | "vip_visit"
  | "police_operation"
  | "road_closure"
  | "emergency_declaration"
  | "sports_event"
  | "concert"
  | "community_event";

type FormType = "event" | "road_closure" | "emergency";

export default function CityAdminInputForm({ onEventCreated }: CityAdminInputFormProps) {
  const [formType, setFormType] = useState<FormType>("event");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [eventType, setEventType] = useState<EventType>("community_event");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [expectedAttendance, setExpectedAttendance] = useState("");
  const [priority, setPriority] = useState("medium");
  const [notifyPatrol, setNotifyPatrol] = useState(false);

  const [roadName, setRoadName] = useState("");
  const [closureReason, setClosureReason] = useState("");
  const [detourAvailable, setDetourAvailable] = useState(false);
  const [detourRoute, setDetourRoute] = useState("");

  const [emergencyType, setEmergencyType] = useState("");
  const [severity, setSeverity] = useState("moderate");
  const [affectedAreas, setAffectedAreas] = useState("");
  const [evacuationRequired, setEvacuationRequired] = useState(false);
  const [evacuationZones, setEvacuationZones] = useState("");
  const [shelterActivation, setShelterActivation] = useState(false);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setStartTime("");
    setEndTime("");
    setExpectedAttendance("");
    setPriority("medium");
    setNotifyPatrol(false);
    setRoadName("");
    setClosureReason("");
    setDetourAvailable(false);
    setDetourRoute("");
    setEmergencyType("");
    setSeverity("moderate");
    setAffectedAreas("");
    setEvacuationRequired(false);
    setEvacuationZones("");
    setShelterActivation(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let endpoint = "";
      let body: Record<string, unknown> = {};

      switch (formType) {
        case "event":
          endpoint = "/api/citybrain/admin/events";
          body = {
            event_type: eventType,
            title,
            description,
            start_time: new Date(startTime).toISOString(),
            end_time: endTime ? new Date(endTime).toISOString() : null,
            expected_attendance: expectedAttendance ? parseInt(expectedAttendance) : null,
            priority,
            notify_patrol: notifyPatrol,
            update_predictions: true,
          };
          break;

        case "road_closure":
          endpoint = "/api/citybrain/admin/road-closures";
          body = {
            road_name: roadName,
            segment_start: { latitude: 26.7753, longitude: -80.0583 },
            segment_end: { latitude: 26.7800, longitude: -80.0550 },
            reason: closureReason,
            start_time: new Date(startTime).toISOString(),
            end_time: endTime ? new Date(endTime).toISOString() : null,
            detour_available: detourAvailable,
            detour_route: detourRoute || null,
            notify_traffic: true,
          };
          break;

        case "emergency":
          endpoint = "/api/citybrain/admin/emergency-declaration";
          body = {
            emergency_type: emergencyType,
            severity,
            affected_areas: affectedAreas.split(",").map((a) => a.trim()),
            description,
            evacuation_required: evacuationRequired,
            evacuation_zones: evacuationRequired
              ? evacuationZones.split(",").map((z) => z.trim())
              : null,
            shelter_activation: shelterActivation,
            effective_time: new Date(startTime).toISOString(),
            expected_duration_hours: endTime
              ? Math.ceil(
                  (new Date(endTime).getTime() - new Date(startTime).getTime()) /
                    (1000 * 60 * 60)
                )
              : null,
          };
          break;
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create entry");
      }

      const data = await response.json();
      setSuccess(`Successfully created: ${data.event_id || data.closure_id || "Entry"}`);
      resetForm();
      onEventCreated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const eventTypes: { value: EventType; label: string }[] = [
    { value: "festival", label: "Festival" },
    { value: "parade", label: "Parade" },
    { value: "school_dismissal", label: "School Dismissal" },
    { value: "utility_maintenance", label: "Utility Maintenance" },
    { value: "vip_visit", label: "VIP Visit" },
    { value: "police_operation", label: "Police Operation" },
    { value: "sports_event", label: "Sports Event" },
    { value: "concert", label: "Concert" },
    { value: "community_event", label: "Community Event" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">City Admin Input Console</h2>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => setFormType("event")}
          className={`px-4 py-2 rounded-lg ${
            formType === "event"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          City Event
        </button>
        <button
          onClick={() => setFormType("road_closure")}
          className={`px-4 py-2 rounded-lg ${
            formType === "road_closure"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Road Closure
        </button>
        <button
          onClick={() => setFormType("emergency")}
          className={`px-4 py-2 rounded-lg ${
            formType === "emergency"
              ? "bg-red-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Emergency Declaration
        </button>
      </div>

      {success && (
        <div className="bg-green-900/50 border border-green-500 rounded-lg p-4">
          <p className="text-green-400">{success}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">Error: {error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        {formType === "event" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Event Type</label>
                <select
                  value={eventType}
                  onChange={(e) => setEventType(e.target.value as EventType)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  required
                >
                  {eventTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                required
                maxLength={200}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                rows={3}
                required
                maxLength={2000}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Start Time</label>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">End Time (optional)</label>
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Expected Attendance</label>
                <input
                  type="number"
                  value={expectedAttendance}
                  onChange={(e) => setExpectedAttendance(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  min="0"
                />
              </div>
              <div className="flex items-center space-x-4 pt-6">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={notifyPatrol}
                    onChange={(e) => setNotifyPatrol(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Notify Patrol Units</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {formType === "road_closure" && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Road Name</label>
              <input
                type="text"
                value={roadName}
                onChange={(e) => setRoadName(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                required
                placeholder="e.g., Blue Heron Blvd"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Reason for Closure</label>
              <textarea
                value={closureReason}
                onChange={(e) => setClosureReason(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                rows={2}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Start Time</label>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">End Time (optional)</label>
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={detourAvailable}
                  onChange={(e) => setDetourAvailable(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Detour Available</span>
              </label>
              {detourAvailable && (
                <input
                  type="text"
                  value={detourRoute}
                  onChange={(e) => setDetourRoute(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  placeholder="Detour route description"
                />
              )}
            </div>
          </div>
        )}

        {formType === "emergency" && (
          <div className="space-y-4">
            <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-400">
                Warning: Emergency declarations will trigger city-wide alerts and may activate
                evacuation procedures.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Emergency Type</label>
                <input
                  type="text"
                  value={emergencyType}
                  onChange={(e) => setEmergencyType(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  required
                  placeholder="e.g., Hurricane, Flood, Chemical Spill"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                >
                  <option value="minor">Minor</option>
                  <option value="moderate">Moderate</option>
                  <option value="severe">Severe</option>
                  <option value="extreme">Extreme</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                rows={3}
                required
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Affected Areas (comma-separated)
              </label>
              <input
                type="text"
                value={affectedAreas}
                onChange={(e) => setAffectedAreas(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                required
                placeholder="e.g., Singer Island, Marina District, Downtown"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Effective Time</label>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Expected End (optional)</label>
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={evacuationRequired}
                  onChange={(e) => setEvacuationRequired(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-red-400">Evacuation Required</span>
              </label>
              {evacuationRequired && (
                <input
                  type="text"
                  value={evacuationZones}
                  onChange={(e) => setEvacuationZones(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  placeholder="Evacuation zones (e.g., A, B, C)"
                />
              )}
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={shelterActivation}
                  onChange={(e) => setShelterActivation(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Activate Emergency Shelters</span>
              </label>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end space-x-3">
          <button
            type="button"
            onClick={resetForm}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={loading}
            className={`px-4 py-2 rounded font-medium ${
              formType === "emergency"
                ? "bg-red-600 hover:bg-red-700"
                : "bg-blue-600 hover:bg-blue-700"
            } disabled:bg-gray-600`}
          >
            {loading ? "Submitting..." : formType === "emergency" ? "Declare Emergency" : "Create Entry"}
          </button>
        </div>
      </form>
    </div>
  );
}
