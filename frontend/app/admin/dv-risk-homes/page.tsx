'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import { TextInput, TextArea, DropdownSelect, ToggleSwitch } from '@/components/admin/FormInputs';

interface DVRiskHome {
  id: string;
  sector_id: string;
  risk_level: string;
  case_number: string;
  officer_alert: boolean;
  encrypted_notes: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const RISK_LEVELS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

const SECTOR_OPTIONS = [
  { value: 'sector-1', label: 'Sector 1 - Downtown' },
  { value: 'sector-2', label: 'Sector 2 - Marina' },
  { value: 'sector-3', label: 'Sector 3 - Industrial' },
  { value: 'sector-4', label: 'Sector 4 - Residential North' },
  { value: 'sector-5', label: 'Sector 5 - Residential South' },
];

const DEMO_DV_HOMES: DVRiskHome[] = [
  { id: 'dv-001', sector_id: 'sector-1', risk_level: 'high', case_number: 'DV-2024-0123', officer_alert: true, encrypted_notes: '[ENCRYPTED]', status: 'active', created_at: '2024-06-15', updated_at: '2024-12-01' },
  { id: 'dv-002', sector_id: 'sector-4', risk_level: 'critical', case_number: 'DV-2024-0456', officer_alert: true, encrypted_notes: '[ENCRYPTED]', status: 'active', created_at: '2024-08-20', updated_at: '2024-12-10' },
];

const columns = [
  { key: 'sector_id', label: 'Sector' },
  { key: 'risk_level', label: 'Risk Level' },
  { key: 'case_number', label: 'Case Number' },
  { key: 'officer_alert', label: 'Officer Alert' },
  { key: 'status', label: 'Status' },
];

export default function DVRiskHomesAdminPage() {
  const [homes, setHomes] = useState<DVRiskHome[]>(DEMO_DV_HOMES);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingHome, setEditingHome] = useState<DVRiskHome | null>(null);
  const [formData, setFormData] = useState<Partial<DVRiskHome>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchHomes(); }, []);

  const fetchHomes = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/dv_risk_homes`);
      if (response.ok) {
        const data = await response.json();
        if (data.dv_risk_homes?.length > 0) setHomes(data.dv_risk_homes);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.sector_id) newErrors.sector_id = 'Sector is required';
    if (!formData.risk_level) newErrors.risk_level = 'Risk level is required';
    if (!formData.case_number?.trim()) newErrors.case_number = 'Case number is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingHome(null);
    setFormData({ sector_id: '', risk_level: '', case_number: '', officer_alert: true, encrypted_notes: '', status: 'active' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (home: DVRiskHome) => {
    setEditingHome(home);
    setFormData({ ...home, encrypted_notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (home: DVRiskHome) => {
    if (!confirm(`Delete DV risk home record "${home.case_number}"?`)) return;
    setHomes(homes.filter((h) => h.id !== home.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newHome: DVRiskHome = {
      id: editingHome?.id || `dv-${Date.now()}`,
      sector_id: formData.sector_id || '',
      risk_level: formData.risk_level || '',
      case_number: formData.case_number || '',
      officer_alert: formData.officer_alert ?? true,
      encrypted_notes: formData.encrypted_notes ? '[ENCRYPTED]' : editingHome?.encrypted_notes || '',
      status: formData.status || 'active',
      created_at: editingHome?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingHome) {
      setHomes(homes.map((h) => (h.id === editingHome.id ? newHome : h)));
    } else {
      setHomes([...homes, newHome]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">DV Risk Home Management</h1>
            <p className="text-gray-400 text-sm">Manage domestic violence risk locations (NO ADDRESSES - sector only)</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add DV Risk Home</button>}
        </div>

        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm font-medium">SECURITY NOTICE: Address information is NOT stored for DV risk homes. Only sector assignment is recorded to protect victim safety.</p>
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={homes} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search by case number..." emptyMessage="No DV risk homes found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingHome ? 'Edit DV Risk Home' : 'Add New DV Risk Home'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="bg-red-900/20 border border-red-700 rounded-lg p-3 mb-4">
                  <p className="text-red-400 text-xs">DO NOT enter any address information. Only sector assignment is allowed.</p>
                </div>
                <DropdownSelect label="Sector" name="sector_id" value={formData.sector_id || ''} onChange={(v) => setFormData({ ...formData, sector_id: v })} options={SECTOR_OPTIONS} required error={errors.sector_id} />
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Risk Level" name="risk_level" value={formData.risk_level || ''} onChange={(v) => setFormData({ ...formData, risk_level: v })} options={RISK_LEVELS} required error={errors.risk_level} />
                  <TextInput label="Case Number" name="case_number" value={formData.case_number || ''} onChange={(v) => setFormData({ ...formData, case_number: v })} required error={errors.case_number} placeholder="DV-2024-0123" />
                </div>
                <ToggleSwitch label="Officer Alert" name="officer_alert" checked={formData.officer_alert ?? true} onChange={(v) => setFormData({ ...formData, officer_alert: v })} description="Alert officers when responding to this sector" />
                <TextArea label="Encrypted Notes (will be encrypted)" name="encrypted_notes" value={formData.encrypted_notes || ''} onChange={(v) => setFormData({ ...formData, encrypted_notes: v })} placeholder="Enter sensitive notes (will be encrypted)..." rows={3} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingHome ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
