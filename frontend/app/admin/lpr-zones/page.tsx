'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPolygonInput from '@/components/admin/MapPolygonInput';
import { TextInput, TextArea, DropdownSelect, MultiSelect } from '@/components/admin/FormInputs';

interface PolygonPoint { lat: number; lng: number; }

interface LPRZone {
  id: string;
  zone_name: string;
  boundary: PolygonPoint[];
  camera_ids: string[];
  bolo_rules: string;
  alert_sensitivity: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const SENSITIVITY_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

const CAMERA_OPTIONS = [
  { value: 'cam-001', label: 'City Hall Main' },
  { value: 'cam-002', label: 'Marina District' },
  { value: 'cam-003', label: 'I-95 Overpass' },
  { value: 'cam-004', label: 'School Zone Alpha' },
];

const DEMO_LPR_ZONES: LPRZone[] = [
  { id: 'lpr-001', zone_name: 'Downtown Entry Points', boundary: [{ lat: 26.78, lng: -80.06 }, { lat: 26.78, lng: -80.05 }, { lat: 26.77, lng: -80.05 }, { lat: 26.77, lng: -80.06 }], camera_ids: ['cam-001', 'cam-003'], bolo_rules: 'Alert on stolen vehicles, wanted persons', alert_sensitivity: 'high', status: 'active', notes: 'Primary entry monitoring zone', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'lpr-002', zone_name: 'Marina Access', boundary: [{ lat: 26.785, lng: -80.055 }, { lat: 26.785, lng: -80.045 }, { lat: 26.775, lng: -80.045 }, { lat: 26.775, lng: -80.055 }], camera_ids: ['cam-002'], bolo_rules: 'Monitor suspicious activity', alert_sensitivity: 'medium', status: 'active', notes: 'Marina area monitoring', created_at: '2024-02-20', updated_at: '2024-11-15' },
];

const columns = [
  { key: 'zone_name', label: 'Zone Name' },
  { key: 'camera_ids', label: 'Cameras', render: (v: string[]) => v?.length ? `${v.length} cameras` : 'None' },
  { key: 'alert_sensitivity', label: 'Sensitivity' },
  { key: 'status', label: 'Status' },
];

export default function LPRZonesAdminPage() {
  const [zones, setZones] = useState<LPRZone[]>(DEMO_LPR_ZONES);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingZone, setEditingZone] = useState<LPRZone | null>(null);
  const [formData, setFormData] = useState<Partial<LPRZone>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchZones(); }, []);

  const fetchZones = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/lpr_zones`);
      if (response.ok) {
        const data = await response.json();
        if (data.lpr_zones?.length > 0) setZones(data.lpr_zones);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.zone_name?.trim()) newErrors.zone_name = 'Zone name is required';
    if (!formData.boundary || formData.boundary.length < 3) newErrors.boundary = 'Boundary must have at least 3 points';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingZone(null);
    setFormData({ zone_name: '', boundary: [], camera_ids: [], bolo_rules: '', alert_sensitivity: 'medium', status: 'active', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (zone: LPRZone) => {
    setEditingZone(zone);
    setFormData({ ...zone });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (zone: LPRZone) => {
    if (!confirm(`Delete LPR zone "${zone.zone_name}"?`)) return;
    setZones(zones.filter((z) => z.id !== zone.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newZone: LPRZone = {
      id: editingZone?.id || `lpr-${Date.now()}`,
      zone_name: formData.zone_name || '',
      boundary: formData.boundary || [],
      camera_ids: formData.camera_ids || [],
      bolo_rules: formData.bolo_rules || '',
      alert_sensitivity: formData.alert_sensitivity || 'medium',
      status: formData.status || 'active',
      notes: formData.notes || '',
      created_at: editingZone?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingZone) {
      setZones(zones.map((z) => (z.id === editingZone.id ? newZone : z)));
    } else {
      setZones([...zones, newZone]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">LPR Zone Management</h1>
            <p className="text-gray-400 text-sm">Configure license plate recognition zones and BOLO rules</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add LPR Zone</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={zones} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search LPR zones..." emptyMessage="No LPR zones found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingZone ? 'Edit LPR Zone' : 'Add New LPR Zone'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Zone Name" name="zone_name" value={formData.zone_name || ''} onChange={(v) => setFormData({ ...formData, zone_name: v })} required error={errors.zone_name} placeholder="Downtown Entry Points" />
                  <DropdownSelect label="Alert Sensitivity" name="alert_sensitivity" value={formData.alert_sensitivity || ''} onChange={(v) => setFormData({ ...formData, alert_sensitivity: v })} options={SENSITIVITY_OPTIONS} required />
                </div>
                <MultiSelect label="Assigned Cameras" name="camera_ids" value={formData.camera_ids || []} onChange={(v) => setFormData({ ...formData, camera_ids: v })} options={CAMERA_OPTIONS} />
                <TextArea label="BOLO Rules" name="bolo_rules" value={formData.bolo_rules || ''} onChange={(v) => setFormData({ ...formData, bolo_rules: v })} placeholder="Alert on stolen vehicles, wanted persons..." rows={3} />
                <MapPolygonInput label="Zone Boundary" value={formData.boundary} onChange={(v) => setFormData({ ...formData, boundary: v || [] })} required minPoints={3} />
                {errors.boundary && <p className="text-xs text-red-400">{errors.boundary}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingZone ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
