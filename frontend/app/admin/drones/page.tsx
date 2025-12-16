'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, DropdownSelect, TextArea, NumberInput } from '@/components/admin/FormInputs';

interface Drone {
  id: string;
  drone_id: string;
  model: string;
  serial_number: string;
  assigned_officer: string;
  total_flight_hours: number;
  battery_count: number;
  home_lat: number;
  home_lng: number;
  stream_url: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const DRONE_MODELS = [
  { value: 'dji_mavic_3', label: 'DJI Mavic 3' },
  { value: 'dji_matrice_300', label: 'DJI Matrice 300 RTK' },
  { value: 'dji_phantom_4', label: 'DJI Phantom 4 Pro' },
  { value: 'autel_evo_2', label: 'Autel EVO II' },
  { value: 'skydio_2', label: 'Skydio 2+' },
];

const STATUS_OPTIONS = [
  { value: 'available', label: 'Available' },
  { value: 'deployed', label: 'Deployed' },
  { value: 'charging', label: 'Charging' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'offline', label: 'Offline' },
];

const DEMO_DRONES: Drone[] = [
  { id: 'drone-001', drone_id: 'RBPD-UAV-001', model: 'dji_matrice_300', serial_number: 'DJI3001234', assigned_officer: 'Officer Martinez', total_flight_hours: 245.5, battery_count: 4, home_lat: 26.7754, home_lng: -80.0583, stream_url: 'rtsp://drone1.rbpd.local/stream', status: 'available', notes: 'Primary tactical drone', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'drone-002', drone_id: 'RBPD-UAV-002', model: 'dji_mavic_3', serial_number: 'DJI3005678', assigned_officer: 'Officer Johnson', total_flight_hours: 128.3, battery_count: 3, home_lat: 26.7821, home_lng: -80.0512, stream_url: 'rtsp://drone2.rbpd.local/stream', status: 'deployed', notes: 'Patrol support drone', created_at: '2024-03-20', updated_at: '2024-12-10' },
];

const columns = [
  { key: 'drone_id', label: 'Drone ID' },
  { key: 'model', label: 'Model' },
  { key: 'assigned_officer', label: 'Assigned Officer' },
  { key: 'total_flight_hours', label: 'Flight Hours' },
  { key: 'battery_count', label: 'Batteries' },
  { key: 'status', label: 'Status' },
];

export default function DronesAdminPage() {
  const [drones, setDrones] = useState<Drone[]>(DEMO_DRONES);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingDrone, setEditingDrone] = useState<Drone | null>(null);
  const [formData, setFormData] = useState<Partial<Drone>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => {
    fetchDrones();
  }, []);

  const fetchDrones = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/drones`);
      if (response.ok) {
        const data = await response.json();
        if (data.drones && data.drones.length > 0) {
          setDrones(data.drones);
        }
      }
    } catch (error) {
      console.log('Using demo data');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.drone_id?.trim()) newErrors.drone_id = 'Drone ID is required';
    if (!formData.model) newErrors.model = 'Model is required';
    if (!formData.serial_number?.trim()) newErrors.serial_number = 'Serial number is required';
    if (!formData.home_lat || !formData.home_lng) newErrors.location = 'Home location is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingDrone(null);
    setFormData({ drone_id: '', model: '', serial_number: '', assigned_officer: '', total_flight_hours: 0, battery_count: 2, home_lat: 26.775, home_lng: -80.058, stream_url: '', status: 'available', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (drone: Drone) => {
    setEditingDrone(drone);
    setFormData({ ...drone });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (drone: Drone) => {
    if (!confirm(`Delete drone "${drone.drone_id}"?`)) return;
    setDrones(drones.filter((d) => d.id !== drone.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newDrone: Drone = {
      id: editingDrone?.id || `drone-${Date.now()}`,
      drone_id: formData.drone_id || '',
      model: formData.model || '',
      serial_number: formData.serial_number || '',
      assigned_officer: formData.assigned_officer || '',
      total_flight_hours: formData.total_flight_hours || 0,
      battery_count: formData.battery_count || 0,
      home_lat: formData.home_lat || 0,
      home_lng: formData.home_lng || 0,
      stream_url: formData.stream_url || '',
      status: formData.status || 'available',
      notes: formData.notes || '',
      created_at: editingDrone?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingDrone) {
      setDrones(drones.map((d) => (d.id === editingDrone.id ? newDrone : d)));
    } else {
      setDrones([...drones, newDrone]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Drone Management</h1>
            <p className="text-gray-400 text-sm">Manage UAV fleet and assignments</p>
          </div>
          {canEdit && (
            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">
              + Add Drone
            </button>
          )}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={drones} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search drones..." emptyMessage="No drones found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingDrone ? 'Edit Drone' : 'Add New Drone'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Drone ID" name="drone_id" value={formData.drone_id || ''} onChange={(v) => setFormData({ ...formData, drone_id: v })} required error={errors.drone_id} placeholder="RBPD-UAV-001" />
                  <TextInput label="Serial Number" name="serial_number" value={formData.serial_number || ''} onChange={(v) => setFormData({ ...formData, serial_number: v })} required error={errors.serial_number} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Model" name="model" value={formData.model || ''} onChange={(v) => setFormData({ ...formData, model: v })} options={DRONE_MODELS} required error={errors.model} />
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                </div>
                <TextInput label="Assigned Officer" name="assigned_officer" value={formData.assigned_officer || ''} onChange={(v) => setFormData({ ...formData, assigned_officer: v })} placeholder="Officer Name" />
                <div className="grid grid-cols-2 gap-4">
                  <NumberInput label="Flight Hours" name="total_flight_hours" value={formData.total_flight_hours || 0} onChange={(v) => setFormData({ ...formData, total_flight_hours: v })} min={0} step={0.1} />
                  <NumberInput label="Battery Count" name="battery_count" value={formData.battery_count || 0} onChange={(v) => setFormData({ ...formData, battery_count: v })} min={0} />
                </div>
                <TextInput label="Stream URL" name="stream_url" value={formData.stream_url || ''} onChange={(v) => setFormData({ ...formData, stream_url: v })} placeholder="rtsp://drone.local/stream" />
                <MapPointInput label="Home Location" value={formData.home_lat && formData.home_lng ? { lat: formData.home_lat, lng: formData.home_lng } : null} onChange={(p) => p ? setFormData({ ...formData, home_lat: p.lat, home_lng: p.lng }) : setFormData({ ...formData, home_lat: undefined, home_lng: undefined })} required />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={3} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingDrone ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
