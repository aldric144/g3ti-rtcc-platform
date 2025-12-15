'use client';

import { useState } from 'react';
import { MapPin, Plus, Trash2, AlertTriangle } from 'lucide-react';

interface BOLOZone {
  id: string;
  case_id: string;
  zone_name: string;
  description: string;
  lat: number;
  lng: number;
  radius_meters: number;
  alert_types: string[];
  is_active: boolean;
  created_at: string;
}

export function BOLOZonePanel() {
  const [zones, setZones] = useState<BOLOZone[]>([
    {
      id: '1',
      case_id: 'RTCC-2025-00042',
      zone_name: 'Marina District Alert',
      description: 'Suspect vehicle last seen in this area',
      lat: 26.7754,
      lng: -80.0583,
      radius_meters: 500,
      alert_types: ['lpr', 'camera'],
      is_active: true,
      created_at: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [newZone, setNewZone] = useState({
    case_id: '',
    zone_name: '',
    description: '',
    lat: 26.7754,
    lng: -80.0583,
    radius_meters: 500,
    alert_types: ['lpr', 'camera'],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const zone: BOLOZone = {
      id: Date.now().toString(),
      ...newZone,
      is_active: true,
      created_at: new Date().toISOString(),
    };

    setZones([zone, ...zones]);
    setNewZone({
      case_id: '',
      zone_name: '',
      description: '',
      lat: 26.7754,
      lng: -80.0583,
      radius_meters: 500,
      alert_types: ['lpr', 'camera'],
    });
    setShowForm(false);
  };

  const deactivateZone = (zoneId: string) => {
    setZones(zones.map(z => z.id === zoneId ? { ...z, is_active: false } : z));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
          <AlertTriangle className="h-5 w-5" />
          <span className="text-sm font-medium">
            {zones.filter(z => z.is_active).length} Active BOLO Zones
          </span>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add BOLO Zone
        </button>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
            Create BOLO Zone
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Case ID
                </label>
                <input
                  type="text"
                  value={newZone.case_id}
                  onChange={(e) => setNewZone({ ...newZone, case_id: e.target.value })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Zone Name
                </label>
                <input
                  type="text"
                  value={newZone.zone_name}
                  onChange={(e) => setNewZone({ ...newZone, zone_name: e.target.value })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Description
              </label>
              <textarea
                value={newZone.description}
                onChange={(e) => setNewZone({ ...newZone, description: e.target.value })}
                rows={2}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Latitude
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={newZone.lat}
                  onChange={(e) => setNewZone({ ...newZone, lat: parseFloat(e.target.value) })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Longitude
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={newZone.lng}
                  onChange={(e) => setNewZone({ ...newZone, lng: parseFloat(e.target.value) })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Radius (meters)
                </label>
                <input
                  type="number"
                  value={newZone.radius_meters}
                  onChange={(e) => setNewZone({ ...newZone, radius_meters: parseInt(e.target.value) })}
                  min={100}
                  max={10000}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Create Zone
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Zone List */}
      <div className="grid gap-4 sm:grid-cols-2">
        {zones.map((zone) => (
          <div
            key={zone.id}
            className={`rounded-xl border p-4 ${
              zone.is_active
                ? 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-900/20'
                : 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <MapPin className={`h-5 w-5 ${zone.is_active ? 'text-amber-600' : 'text-gray-400'}`} />
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">{zone.zone_name}</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{zone.case_id}</p>
                </div>
              </div>
              {zone.is_active && (
                <button
                  onClick={() => deactivateZone(zone.id)}
                  className="rounded-lg p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{zone.description}</p>
            <div className="mt-3 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span>Radius: {zone.radius_meters}m</span>
              <span>Alerts: {zone.alert_types.join(', ')}</span>
            </div>
            {!zone.is_active && (
              <span className="mt-2 inline-block rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                Inactive
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
