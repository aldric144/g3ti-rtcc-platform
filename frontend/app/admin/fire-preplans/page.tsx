'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, TextArea, ToggleSwitch, FileUpload } from '@/components/admin/FormInputs';

interface FirePreplan {
  id: string;
  building_name: string;
  address: string;
  lat: number;
  lng: number;
  pdf_url: string;
  hazmat_notes: string;
  knox_box_location: string;
  riser_location: string;
  has_sprinklers: boolean;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const DEMO_PREPLANS: FirePreplan[] = [
  { id: 'fp-001', building_name: 'City Hall', address: '600 W Blue Heron Blvd', lat: 26.7754, lng: -80.0583, pdf_url: '/preplans/city-hall.pdf', hazmat_notes: 'Chemical storage in basement', knox_box_location: 'Main entrance, east side', riser_location: 'North stairwell, ground floor', has_sprinklers: true, status: 'active', notes: 'Updated 2024', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'fp-002', building_name: 'Marina Plaza', address: '200 E 13th St', lat: 26.7821, lng: -80.0512, pdf_url: '/preplans/marina-plaza.pdf', hazmat_notes: 'Fuel storage near dock', knox_box_location: 'Security office', riser_location: 'Utility room', has_sprinklers: true, status: 'active', notes: 'Marina complex', created_at: '2024-02-20', updated_at: '2024-11-15' },
];

const columns = [
  { key: 'building_name', label: 'Building' },
  { key: 'address', label: 'Address' },
  { key: 'has_sprinklers', label: 'Sprinklers' },
  { key: 'knox_box_location', label: 'Knox Box' },
  { key: 'status', label: 'Status' },
];

export default function FirePreplansAdminPage() {
  const [preplans, setPreplans] = useState<FirePreplan[]>(DEMO_PREPLANS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingPreplan, setEditingPreplan] = useState<FirePreplan | null>(null);
  const [formData, setFormData] = useState<Partial<FirePreplan>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchPreplans(); }, []);

  const fetchPreplans = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/fire_preplans`);
      if (response.ok) {
        const data = await response.json();
        if (data.fire_preplans?.length > 0) setPreplans(data.fire_preplans);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.building_name?.trim()) newErrors.building_name = 'Building name is required';
    if (!formData.address?.trim()) newErrors.address = 'Address is required';
    if (!formData.lat || !formData.lng) newErrors.location = 'Location is required';
    if (pdfFile && !pdfFile.name.toLowerCase().endsWith('.pdf')) newErrors.pdf = 'Only PDF files are accepted';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingPreplan(null);
    setFormData({ building_name: '', address: '', lat: 26.775, lng: -80.058, pdf_url: '', hazmat_notes: '', knox_box_location: '', riser_location: '', has_sprinklers: false, status: 'active', notes: '' });
    setPdfFile(null);
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (preplan: FirePreplan) => {
    setEditingPreplan(preplan);
    setFormData({ ...preplan });
    setPdfFile(null);
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (preplan: FirePreplan) => {
    if (!confirm(`Delete fire preplan for "${preplan.building_name}"?`)) return;
    setPreplans(preplans.filter((p) => p.id !== preplan.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newPreplan: FirePreplan = {
      id: editingPreplan?.id || `fp-${Date.now()}`,
      building_name: formData.building_name || '',
      address: formData.address || '',
      lat: formData.lat || 0,
      lng: formData.lng || 0,
      pdf_url: pdfFile ? `/preplans/${pdfFile.name}` : formData.pdf_url || '',
      hazmat_notes: formData.hazmat_notes || '',
      knox_box_location: formData.knox_box_location || '',
      riser_location: formData.riser_location || '',
      has_sprinklers: formData.has_sprinklers || false,
      status: formData.status || 'active',
      notes: formData.notes || '',
      created_at: editingPreplan?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingPreplan) {
      setPreplans(preplans.map((p) => (p.id === editingPreplan.id ? newPreplan : p)));
    } else {
      setPreplans([...preplans, newPreplan]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Fire Preplan Management</h1>
            <p className="text-gray-400 text-sm">Manage building fire preplans and hazmat information</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Preplan</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={preplans} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search preplans..." emptyMessage="No fire preplans found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingPreplan ? 'Edit Fire Preplan' : 'Add New Fire Preplan'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <TextInput label="Building Name" name="building_name" value={formData.building_name || ''} onChange={(v) => setFormData({ ...formData, building_name: v })} required error={errors.building_name} placeholder="City Hall" />
                <TextInput label="Address" name="address" value={formData.address || ''} onChange={(v) => setFormData({ ...formData, address: v })} required error={errors.address} placeholder="600 W Blue Heron Blvd" />
                <FileUpload label="Preplan PDF" name="pdf" onChange={setPdfFile} accept=".pdf" currentFile={pdfFile?.name || formData.pdf_url} error={errors.pdf} />
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Knox Box Location" name="knox_box_location" value={formData.knox_box_location || ''} onChange={(v) => setFormData({ ...formData, knox_box_location: v })} placeholder="Main entrance" />
                  <TextInput label="Riser Location" name="riser_location" value={formData.riser_location || ''} onChange={(v) => setFormData({ ...formData, riser_location: v })} placeholder="North stairwell" />
                </div>
                <ToggleSwitch label="Has Sprinkler System" name="has_sprinklers" checked={formData.has_sprinklers || false} onChange={(v) => setFormData({ ...formData, has_sprinklers: v })} />
                <TextArea label="Hazmat Notes" name="hazmat_notes" value={formData.hazmat_notes || ''} onChange={(v) => setFormData({ ...formData, hazmat_notes: v })} placeholder="Chemical storage, fuel tanks, etc." rows={3} />
                <MapPointInput label="Building Location" value={formData.lat && formData.lng ? { lat: formData.lat, lng: formData.lng } : null} onChange={(p) => p ? setFormData({ ...formData, lat: p.lat, lng: p.lng }) : setFormData({ ...formData, lat: undefined, lng: undefined })} required />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingPreplan ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
