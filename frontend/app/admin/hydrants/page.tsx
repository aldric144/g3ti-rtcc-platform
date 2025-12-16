'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, TextArea, DropdownSelect, NumberInput } from '@/components/admin/FormInputs';

interface Hydrant {
  id: string;
  hydrant_id: string;
  lat: number;
  lng: number;
  psi: number;
  flow_rate: number;
  hydrant_type: string;
  status: string;
  address: string;
  sector_id: string;
  last_inspection: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const HYDRANT_TYPES = [
  { value: 'standard', label: 'Standard' },
  { value: 'high_flow', label: 'High Flow' },
  { value: 'dry_barrel', label: 'Dry Barrel' },
  { value: 'wet_barrel', label: 'Wet Barrel' },
  { value: 'wall_mount', label: 'Wall Mount' },
];

const STATUS_OPTIONS = [
  { value: 'operational', label: 'Operational' },
  { value: 'out_of_service', label: 'Out of Service' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'damaged', label: 'Damaged' },
];

const DEMO_HYDRANTS: Hydrant[] = [
  { id: 'hyd-001', hydrant_id: 'HYD-001', lat: 26.7754, lng: -80.0583, psi: 65, flow_rate: 1500, hydrant_type: 'standard', status: 'operational', address: '600 W Blue Heron Blvd', sector_id: 'sector-1', last_inspection: '2024-06-15', notes: 'Good condition', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'hyd-002', hydrant_id: 'HYD-002', lat: 26.7821, lng: -80.0512, psi: 72, flow_rate: 1800, hydrant_type: 'high_flow', status: 'operational', address: '200 E 13th St', sector_id: 'sector-2', last_inspection: '2024-07-20', notes: 'Marina area hydrant', created_at: '2024-02-20', updated_at: '2024-11-15' },
  { id: 'hyd-003', hydrant_id: 'HYD-003', lat: 26.7698, lng: -80.0789, psi: 45, flow_rate: 1200, hydrant_type: 'standard', status: 'maintenance', address: '1200 Industrial Blvd', sector_id: 'sector-3', last_inspection: '2024-08-10', notes: 'Needs valve replacement', created_at: '2024-03-10', updated_at: '2024-12-05' },
];

const columns = [
  { key: 'hydrant_id', label: 'Hydrant ID' },
  { key: 'address', label: 'Address' },
  { key: 'psi', label: 'PSI' },
  { key: 'flow_rate', label: 'Flow (GPM)' },
  { key: 'hydrant_type', label: 'Type' },
  { key: 'status', label: 'Status' },
];

export default function HydrantsAdminPage() {
  const [hydrants, setHydrants] = useState<Hydrant[]>(DEMO_HYDRANTS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingHydrant, setEditingHydrant] = useState<Hydrant | null>(null);
  const [formData, setFormData] = useState<Partial<Hydrant>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchHydrants(); }, []);

  const fetchHydrants = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/hydrants`);
      if (response.ok) {
        const data = await response.json();
        if (data.hydrants?.length > 0) setHydrants(data.hydrants);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.hydrant_id?.trim()) newErrors.hydrant_id = 'Hydrant ID is required';
    if (!formData.lat || !formData.lng) newErrors.location = 'Location is required';
    if (!formData.hydrant_type) newErrors.hydrant_type = 'Type is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingHydrant(null);
    setFormData({ hydrant_id: '', lat: 26.775, lng: -80.058, psi: 60, flow_rate: 1500, hydrant_type: 'standard', status: 'operational', address: '', sector_id: '', last_inspection: '', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (hydrant: Hydrant) => {
    setEditingHydrant(hydrant);
    setFormData({ ...hydrant });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (hydrant: Hydrant) => {
    if (!confirm(`Delete hydrant "${hydrant.hydrant_id}"?`)) return;
    setHydrants(hydrants.filter((h) => h.id !== hydrant.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newHydrant: Hydrant = {
      id: editingHydrant?.id || `hyd-${Date.now()}`,
      hydrant_id: formData.hydrant_id || '',
      lat: formData.lat || 0,
      lng: formData.lng || 0,
      psi: formData.psi || 0,
      flow_rate: formData.flow_rate || 0,
      hydrant_type: formData.hydrant_type || 'standard',
      status: formData.status || 'operational',
      address: formData.address || '',
      sector_id: formData.sector_id || '',
      last_inspection: formData.last_inspection || '',
      notes: formData.notes || '',
      created_at: editingHydrant?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingHydrant) {
      setHydrants(hydrants.map((h) => (h.id === editingHydrant.id ? newHydrant : h)));
    } else {
      setHydrants([...hydrants, newHydrant]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Fire Hydrant Management</h1>
            <p className="text-gray-400 text-sm">Manage fire hydrant locations and inspections</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Hydrant</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={hydrants} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search hydrants..." emptyMessage="No hydrants found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingHydrant ? 'Edit Hydrant' : 'Add New Hydrant'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Hydrant ID" name="hydrant_id" value={formData.hydrant_id || ''} onChange={(v) => setFormData({ ...formData, hydrant_id: v })} required error={errors.hydrant_id} placeholder="HYD-001" />
                  <DropdownSelect label="Type" name="hydrant_type" value={formData.hydrant_type || ''} onChange={(v) => setFormData({ ...formData, hydrant_type: v })} options={HYDRANT_TYPES} required error={errors.hydrant_type} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                  <TextInput label="Sector ID" name="sector_id" value={formData.sector_id || ''} onChange={(v) => setFormData({ ...formData, sector_id: v })} placeholder="sector-1" />
                </div>
                <TextInput label="Address" name="address" value={formData.address || ''} onChange={(v) => setFormData({ ...formData, address: v })} placeholder="600 W Blue Heron Blvd" />
                <div className="grid grid-cols-2 gap-4">
                  <NumberInput label="PSI" name="psi" value={formData.psi || 0} onChange={(v) => setFormData({ ...formData, psi: v })} min={0} max={200} />
                  <NumberInput label="Flow Rate (GPM)" name="flow_rate" value={formData.flow_rate || 0} onChange={(v) => setFormData({ ...formData, flow_rate: v })} min={0} />
                </div>
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-300">Last Inspection</label>
                  <input type="date" value={formData.last_inspection || ''} onChange={(e) => setFormData({ ...formData, last_inspection: e.target.value })} className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white" />
                </div>
                <MapPointInput label="Hydrant Location" value={formData.lat && formData.lng ? { lat: formData.lat, lng: formData.lng } : null} onChange={(p) => p ? setFormData({ ...formData, lat: p.lat, lng: p.lng }) : setFormData({ ...formData, lat: undefined, lng: undefined })} required />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingHydrant ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
