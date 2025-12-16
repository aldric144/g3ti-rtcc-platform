'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, TextArea, DropdownSelect } from '@/components/admin/FormInputs';

interface Incident {
  id: string;
  type: string;
  priority: string;
  location: string;
  lat: number;
  lng: number;
  description: string;
  assigned_officer: string;
  assigned_unit: string;
  sector_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const INCIDENT_TYPES = [
  { value: 'traffic_stop', label: 'Traffic Stop' },
  { value: 'domestic', label: 'Domestic' },
  { value: 'burglary', label: 'Burglary' },
  { value: 'assault', label: 'Assault' },
  { value: 'suspicious_activity', label: 'Suspicious Activity' },
  { value: 'medical', label: 'Medical Emergency' },
  { value: 'fire', label: 'Fire' },
  { value: 'accident', label: 'Traffic Accident' },
  { value: 'shots_fired', label: 'Shots Fired' },
  { value: 'other', label: 'Other' },
];

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'responding', label: 'Responding' },
  { value: 'on_scene', label: 'On Scene' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
];

const DEMO_INCIDENTS: Incident[] = [
  { id: 'inc-001', type: 'traffic_stop', priority: 'low', location: '600 W Blue Heron Blvd', lat: 26.7754, lng: -80.0583, description: 'Routine traffic stop', assigned_officer: 'Officer Martinez', assigned_unit: 'Unit 12', sector_id: 'sector-1', status: 'active', created_at: '2024-12-16T10:30:00Z', updated_at: '2024-12-16T10:30:00Z' },
  { id: 'inc-002', type: 'suspicious_activity', priority: 'medium', location: '200 E 13th St', lat: 26.7821, lng: -80.0512, description: 'Suspicious vehicle reported', assigned_officer: 'Officer Johnson', assigned_unit: 'Unit 7', sector_id: 'sector-2', status: 'responding', created_at: '2024-12-16T11:15:00Z', updated_at: '2024-12-16T11:20:00Z' },
];

const columns = [
  { key: 'type', label: 'Type' },
  { key: 'priority', label: 'Priority' },
  { key: 'location', label: 'Location' },
  { key: 'assigned_officer', label: 'Officer' },
  { key: 'status', label: 'Status' },
];

export default function IncidentsAdminPage() {
  const [incidents, setIncidents] = useState<Incident[]>(DEMO_INCIDENTS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingIncident, setEditingIncident] = useState<Incident | null>(null);
  const [formData, setFormData] = useState<Partial<Incident>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchIncidents(); }, []);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/incidents`);
      if (response.ok) {
        const data = await response.json();
        if (data.incidents?.length > 0) setIncidents(data.incidents);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.type) newErrors.type = 'Type is required';
    if (!formData.priority) newErrors.priority = 'Priority is required';
    if (!formData.lat || !formData.lng) newErrors.location = 'Location is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingIncident(null);
    setFormData({ type: '', priority: 'medium', location: '', lat: 26.775, lng: -80.058, description: '', assigned_officer: '', assigned_unit: '', sector_id: '', status: 'active' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (incident: Incident) => {
    setEditingIncident(incident);
    setFormData({ ...incident });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (incident: Incident) => {
    if (!confirm(`Delete incident "${incident.id}"?`)) return;
    setIncidents(incidents.filter((i) => i.id !== incident.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newIncident: Incident = {
      id: editingIncident?.id || `inc-${Date.now()}`,
      type: formData.type || '',
      priority: formData.priority || 'medium',
      location: formData.location || '',
      lat: formData.lat || 0,
      lng: formData.lng || 0,
      description: formData.description || '',
      assigned_officer: formData.assigned_officer || '',
      assigned_unit: formData.assigned_unit || '',
      sector_id: formData.sector_id || '',
      status: formData.status || 'active',
      created_at: editingIncident?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingIncident) {
      setIncidents(incidents.map((i) => (i.id === editingIncident.id ? newIncident : i)));
    } else {
      setIncidents([...incidents, newIncident]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Incident Management</h1>
            <p className="text-gray-400 text-sm">Manage active and historical incidents</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Incident</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={incidents} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search incidents..." emptyMessage="No incidents found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingIncident ? 'Edit Incident' : 'Add New Incident'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Type" name="type" value={formData.type || ''} onChange={(v) => setFormData({ ...formData, type: v })} options={INCIDENT_TYPES} required error={errors.type} />
                  <DropdownSelect label="Priority" name="priority" value={formData.priority || ''} onChange={(v) => setFormData({ ...formData, priority: v })} options={PRIORITY_OPTIONS} required error={errors.priority} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                  <TextInput label="Sector ID" name="sector_id" value={formData.sector_id || ''} onChange={(v) => setFormData({ ...formData, sector_id: v })} placeholder="sector-1" />
                </div>
                <TextInput label="Location Address" name="location" value={formData.location || ''} onChange={(v) => setFormData({ ...formData, location: v })} placeholder="600 W Blue Heron Blvd" />
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Assigned Officer" name="assigned_officer" value={formData.assigned_officer || ''} onChange={(v) => setFormData({ ...formData, assigned_officer: v })} placeholder="Officer Name" />
                  <TextInput label="Assigned Unit" name="assigned_unit" value={formData.assigned_unit || ''} onChange={(v) => setFormData({ ...formData, assigned_unit: v })} placeholder="Unit 12" />
                </div>
                <TextArea label="Description" name="description" value={formData.description || ''} onChange={(v) => setFormData({ ...formData, description: v })} placeholder="Incident details..." rows={3} />
                <MapPointInput label="Incident Location" value={formData.lat && formData.lng ? { lat: formData.lat, lng: formData.lng } : null} onChange={(p) => p ? setFormData({ ...formData, lat: p.lat, lng: p.lng }) : setFormData({ ...formData, lat: undefined, lng: undefined })} required />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingIncident ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
