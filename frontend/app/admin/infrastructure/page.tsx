'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, TextArea, DropdownSelect, ToggleSwitch } from '@/components/admin/FormInputs';

interface Infrastructure {
  id: string;
  name: string;
  type: string;
  lat: number;
  lng: number;
  address: string;
  is_critical: boolean;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const INFRA_TYPES = [
  { value: 'power_station', label: 'Power Station' },
  { value: 'water_treatment', label: 'Water Treatment' },
  { value: 'telecom_tower', label: 'Telecom Tower' },
  { value: 'bridge', label: 'Bridge' },
  { value: 'hospital', label: 'Hospital' },
  { value: 'government', label: 'Government Building' },
  { value: 'transportation', label: 'Transportation Hub' },
  { value: 'utility', label: 'Utility Facility' },
];

const STATUS_OPTIONS = [
  { value: 'operational', label: 'Operational' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'offline', label: 'Offline' },
  { value: 'critical', label: 'Critical' },
];

const DEMO_INFRASTRUCTURE: Infrastructure[] = [
  { id: 'infra-001', name: 'Main Power Substation', type: 'power_station', lat: 26.7754, lng: -80.0583, address: '500 Industrial Blvd', is_critical: true, status: 'operational', notes: 'Primary power distribution', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'infra-002', name: 'Water Treatment Plant', type: 'water_treatment', lat: 26.7698, lng: -80.0789, address: '1200 Utility Dr', is_critical: true, status: 'operational', notes: 'City water supply', created_at: '2024-02-20', updated_at: '2024-11-15' },
];

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'address', label: 'Address' },
  { key: 'is_critical', label: 'Critical' },
  { key: 'status', label: 'Status' },
];

export default function InfrastructureAdminPage() {
  const [items, setItems] = useState<Infrastructure[]>(DEMO_INFRASTRUCTURE);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<Infrastructure | null>(null);
  const [formData, setFormData] = useState<Partial<Infrastructure>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchItems(); }, []);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/infrastructure`);
      if (response.ok) {
        const data = await response.json();
        if (data.infrastructure?.length > 0) setItems(data.infrastructure);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) newErrors.name = 'Name is required';
    if (!formData.type) newErrors.type = 'Type is required';
    if (!formData.lat || !formData.lng) newErrors.location = 'Location is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({ name: '', type: '', lat: 26.775, lng: -80.058, address: '', is_critical: false, status: 'operational', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (item: Infrastructure) => {
    setEditingItem(item);
    setFormData({ ...item });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (item: Infrastructure) => {
    if (!confirm(`Delete "${item.name}"?`)) return;
    setItems(items.filter((i) => i.id !== item.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newItem: Infrastructure = {
      id: editingItem?.id || `infra-${Date.now()}`,
      name: formData.name || '',
      type: formData.type || '',
      lat: formData.lat || 0,
      lng: formData.lng || 0,
      address: formData.address || '',
      is_critical: formData.is_critical || false,
      status: formData.status || 'operational',
      notes: formData.notes || '',
      created_at: editingItem?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingItem) {
      setItems(items.map((i) => (i.id === editingItem.id ? newItem : i)));
    } else {
      setItems([...items, newItem]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Infrastructure Management</h1>
            <p className="text-gray-400 text-sm">Manage critical infrastructure assets</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Infrastructure</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={items} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search infrastructure..." emptyMessage="No infrastructure found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingItem ? 'Edit Infrastructure' : 'Add New Infrastructure'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <TextInput label="Name" name="name" value={formData.name || ''} onChange={(v) => setFormData({ ...formData, name: v })} required error={errors.name} placeholder="Main Power Substation" />
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Type" name="type" value={formData.type || ''} onChange={(v) => setFormData({ ...formData, type: v })} options={INFRA_TYPES} required error={errors.type} />
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                </div>
                <TextInput label="Address" name="address" value={formData.address || ''} onChange={(v) => setFormData({ ...formData, address: v })} placeholder="500 Industrial Blvd" />
                <ToggleSwitch label="Critical Infrastructure" name="is_critical" checked={formData.is_critical || false} onChange={(v) => setFormData({ ...formData, is_critical: v })} description="Mark as critical for priority monitoring" />
                <MapPointInput label="Location" value={formData.lat && formData.lng ? { lat: formData.lat, lng: formData.lng } : null} onChange={(p) => p ? setFormData({ ...formData, lat: p.lat, lng: p.lng }) : setFormData({ ...formData, lat: undefined, lng: undefined })} required />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={3} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingItem ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
