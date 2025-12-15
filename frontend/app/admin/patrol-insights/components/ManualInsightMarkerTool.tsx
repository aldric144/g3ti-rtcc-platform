'use client';

import { useState } from 'react';
import { MapPin, Plus, Trash2 } from 'lucide-react';

interface ManualMarker {
  id: string;
  zone_type: string;
  name: string;
  lat: number;
  lng: number;
  radius_meters: number;
}

const ZONE_TYPES = [
  { value: 'hotspot', label: 'Patrol Hotspot' },
  { value: 'high_calls', label: 'High-Calls Zone' },
  { value: 'visibility_gap', label: 'Visibility Gap' },
  { value: 'community_concern', label: 'Community Concern' },
];

interface ManualInsightMarkerToolProps {
  onMarkerAdded: () => void;
}

export function ManualInsightMarkerTool({ onMarkerAdded }: ManualInsightMarkerToolProps) {
  const [markers, setMarkers] = useState<ManualMarker[]>([
    {
      id: '1',
      zone_type: 'high_calls',
      name: 'Blue Heron & Congress',
      lat: 26.7650,
      lng: -80.0700,
      radius_meters: 300,
    },
    {
      id: '2',
      zone_type: 'visibility_gap',
      name: 'Industrial Park East',
      lat: 26.7550,
      lng: -80.0750,
      radius_meters: 500,
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [newMarker, setNewMarker] = useState({
    zone_type: 'hotspot',
    name: '',
    lat: 26.7754,
    lng: -80.0583,
    radius_meters: 500,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const marker: ManualMarker = {
      id: Date.now().toString(),
      ...newMarker,
    };

    setMarkers([...markers, marker]);
    setNewMarker({
      zone_type: 'hotspot',
      name: '',
      lat: 26.7754,
      lng: -80.0583,
      radius_meters: 500,
    });
    setShowForm(false);
    onMarkerAdded();
  };

  const deleteMarker = (markerId: string) => {
    setMarkers(markers.filter(m => m.id !== markerId));
    onMarkerAdded();
  };

  const getZoneTypeColor = (zoneType: string) => {
    switch (zoneType) {
      case 'hotspot':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'high_calls':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400';
      case 'visibility_gap':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
      case 'community_concern':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
            <MapPin className="h-5 w-5" />
            Manual Markers
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-1 rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
          >
            <Plus className="h-4 w-4" />
            Add
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="border-b border-gray-200 p-4 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Zone Type
              </label>
              <select
                value={newMarker.zone_type}
                onChange={(e) => setNewMarker({ ...newMarker, zone_type: e.target.value })}
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              >
                {ZONE_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Name
              </label>
              <input
                type="text"
                value={newMarker.name}
                onChange={(e) => setNewMarker({ ...newMarker, name: e.target.value })}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Latitude
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={newMarker.lat}
                  onChange={(e) => setNewMarker({ ...newMarker, lat: parseFloat(e.target.value) })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Longitude
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={newMarker.lng}
                  onChange={(e) => setNewMarker({ ...newMarker, lng: parseFloat(e.target.value) })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Add Marker
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Marker List */}
      <div className="max-h-80 overflow-y-auto p-4">
        <div className="space-y-2">
          {markers.map((marker) => (
            <div
              key={marker.id}
              className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getZoneTypeColor(marker.zone_type)}`}>
                    {ZONE_TYPES.find(t => t.value === marker.zone_type)?.label}
                  </span>
                </div>
                <p className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                  {marker.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {marker.lat.toFixed(4)}, {marker.lng.toFixed(4)}
                </p>
              </div>
              <button
                onClick={() => deleteMarker(marker.id)}
                className="rounded-lg p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          {markers.length === 0 && (
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              No manual markers added
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
