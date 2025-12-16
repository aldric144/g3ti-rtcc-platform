'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPolygonInput from '@/components/admin/MapPolygonInput';
import { TextInput, TextArea, MultiSelect } from '@/components/admin/FormInputs';

interface PolygonPoint { lat: number; lng: number; }

interface Sector {
  id: string;
  sector_id: string;
  name: string;
  boundary: PolygonPoint[];
  assigned_officers: string[];
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const DEMO_SECTORS: Sector[] = [
  { id: 'sector-1', sector_id: 'SECTOR-001', name: 'Downtown District', boundary: [{ lat: 26.78, lng: -80.06 }, { lat: 26.78, lng: -80.05 }, { lat: 26.77, lng: -80.05 }, { lat: 26.77, lng: -80.06 }], assigned_officers: ['Officer Martinez', 'Officer Johnson'], status: 'active', notes: 'Primary downtown patrol area', created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'sector-2', sector_id: 'SECTOR-002', name: 'Marina District', boundary: [{ lat: 26.785, lng: -80.055 }, { lat: 26.785, lng: -80.045 }, { lat: 26.775, lng: -80.045 }, { lat: 26.775, lng: -80.055 }], assigned_officers: ['Officer Williams'], status: 'active', notes: 'Marina and waterfront area', created_at: '2024-01-01', updated_at: '2024-12-01' },
];

const OFFICER_OPTIONS = [
  { value: 'Officer Martinez', label: 'Officer Martinez' },
  { value: 'Officer Johnson', label: 'Officer Johnson' },
  { value: 'Officer Williams', label: 'Officer Williams' },
  { value: 'Officer Brown', label: 'Officer Brown' },
  { value: 'Officer Davis', label: 'Officer Davis' },
];

const columns = [
  { key: 'sector_id', label: 'Sector ID' },
  { key: 'name', label: 'Name' },
  { key: 'assigned_officers', label: 'Officers', render: (v: string[]) => v?.length ? `${v.length} assigned` : 'None' },
  { key: 'status', label: 'Status' },
];

export default function SectorsAdminPage() {
  const [sectors, setSectors] = useState<Sector[]>(DEMO_SECTORS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingSector, setEditingSector] = useState<Sector | null>(null);
  const [formData, setFormData] = useState<Partial<Sector>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchSectors(); }, []);

  const fetchSectors = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/sectors`);
      if (response.ok) {
        const data = await response.json();
        if (data.sectors?.length > 0) setSectors(data.sectors);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.sector_id?.trim()) newErrors.sector_id = 'Sector ID is required';
    if (!formData.name?.trim()) newErrors.name = 'Name is required';
    if (!formData.boundary || formData.boundary.length < 3) newErrors.boundary = 'Boundary must have at least 3 points';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingSector(null);
    setFormData({ sector_id: '', name: '', boundary: [], assigned_officers: [], status: 'active', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (sector: Sector) => {
    setEditingSector(sector);
    setFormData({ ...sector });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (sector: Sector) => {
    if (!confirm(`Delete sector "${sector.name}"?`)) return;
    setSectors(sectors.filter((s) => s.id !== sector.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newSector: Sector = {
      id: editingSector?.id || `sector-${Date.now()}`,
      sector_id: formData.sector_id || '',
      name: formData.name || '',
      boundary: formData.boundary || [],
      assigned_officers: formData.assigned_officers || [],
      status: formData.status || 'active',
      notes: formData.notes || '',
      created_at: editingSector?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingSector) {
      setSectors(sectors.map((s) => (s.id === editingSector.id ? newSector : s)));
    } else {
      setSectors([...sectors, newSector]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Sector Management</h1>
            <p className="text-gray-400 text-sm">Define patrol sectors and assign officers</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Sector</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={sectors} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search sectors..." emptyMessage="No sectors found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingSector ? 'Edit Sector' : 'Add New Sector'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Sector ID" name="sector_id" value={formData.sector_id || ''} onChange={(v) => setFormData({ ...formData, sector_id: v })} required error={errors.sector_id} placeholder="SECTOR-001" />
                  <TextInput label="Name" name="name" value={formData.name || ''} onChange={(v) => setFormData({ ...formData, name: v })} required error={errors.name} placeholder="Downtown District" />
                </div>
                <MultiSelect label="Assigned Officers" name="assigned_officers" value={formData.assigned_officers || []} onChange={(v) => setFormData({ ...formData, assigned_officers: v })} options={OFFICER_OPTIONS} />
                <MapPolygonInput label="Sector Boundary" value={formData.boundary} onChange={(v) => setFormData({ ...formData, boundary: v || [] })} required minPoints={3} />
                {errors.boundary && <p className="text-xs text-red-400">{errors.boundary}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={3} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingSector ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
