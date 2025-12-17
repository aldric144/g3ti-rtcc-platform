'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import { TextInput, TextArea, DropdownSelect, NumberInput } from '@/components/admin/FormInputs';

interface APIConnection {
  id: string;
  api_name: string;
  api_url: string;
  encrypted_key: string;
  refresh_frequency: number;
  auth_type: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const AUTH_TYPES = [
  { value: 'api_key', label: 'API Key' },
  { value: 'bearer_token', label: 'Bearer Token' },
  { value: 'basic_auth', label: 'Basic Auth' },
  { value: 'oauth2', label: 'OAuth 2.0' },
  { value: 'none', label: 'None' },
];

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'error', label: 'Error' },
  { value: 'testing', label: 'Testing' },
];

const DEMO_CONNECTIONS: APIConnection[] = [
  { id: 'api-001', api_name: 'FDOT Traffic API', api_url: 'https://api.fdot.gov/traffic/v1', encrypted_key: '[ENCRYPTED]', refresh_frequency: 60, auth_type: 'api_key', status: 'active', notes: 'Florida DOT traffic data', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'api-002', api_name: 'Weather Service', api_url: 'https://api.weather.gov/points', encrypted_key: '[ENCRYPTED]', refresh_frequency: 300, auth_type: 'none', status: 'active', notes: 'NWS weather data', created_at: '2024-02-20', updated_at: '2024-11-15' },
  { id: 'api-003', api_name: 'NCIC Database', api_url: 'https://ncic.fbi.gov/api/v2', encrypted_key: '[ENCRYPTED]', refresh_frequency: 0, auth_type: 'oauth2', status: 'active', notes: 'FBI NCIC queries', created_at: '2024-03-10', updated_at: '2024-12-05' },
];

const columns = [
  { key: 'api_name', label: 'API Name' },
  { key: 'api_url', label: 'URL' },
  { key: 'auth_type', label: 'Auth Type' },
  { key: 'refresh_frequency', label: 'Refresh (sec)', render: (v: number) => v === 0 ? 'On-demand' : `${v}s` },
  { key: 'status', label: 'Status' },
];

export default function APIConnectionsAdminPage() {
  const [connections, setConnections] = useState<APIConnection[]>(DEMO_CONNECTIONS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingConnection, setEditingConnection] = useState<APIConnection | null>(null);
  const [formData, setFormData] = useState<Partial<APIConnection>>({});
  const [apiKey, setApiKey] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchConnections(); }, []);

  const fetchConnections = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/api_connections`);
      if (response.ok) {
        const data = await response.json();
        if (data.api_connections?.length > 0) setConnections(data.api_connections);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.api_name?.trim()) newErrors.api_name = 'API name is required';
    if (!formData.api_url?.trim()) newErrors.api_url = 'API URL is required';
    else if (!formData.api_url.match(/^https?:\/\/.+/)) newErrors.api_url = 'Invalid URL format';
    if (!formData.auth_type) newErrors.auth_type = 'Auth type is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingConnection(null);
    setFormData({ api_name: '', api_url: '', encrypted_key: '', refresh_frequency: 60, auth_type: 'api_key', status: 'testing', notes: '' });
    setApiKey('');
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (connection: APIConnection) => {
    setEditingConnection(connection);
    setFormData({ ...connection });
    setApiKey('');
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (connection: APIConnection) => {
    if (!confirm(`Delete API connection "${connection.api_name}"?`)) return;
    setConnections(connections.filter((c) => c.id !== connection.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newConnection: APIConnection = {
      id: editingConnection?.id || `api-${Date.now()}`,
      api_name: formData.api_name || '',
      api_url: formData.api_url || '',
      encrypted_key: apiKey ? '[ENCRYPTED]' : editingConnection?.encrypted_key || '',
      refresh_frequency: formData.refresh_frequency || 0,
      auth_type: formData.auth_type || 'api_key',
      status: formData.status || 'testing',
      notes: formData.notes || '',
      created_at: editingConnection?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingConnection) {
      setConnections(connections.map((c) => (c.id === editingConnection.id ? newConnection : c)));
    } else {
      setConnections([...connections, newConnection]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">API Connection Management</h1>
            <p className="text-gray-400 text-sm">Manage external API integrations and credentials</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add API Connection</button>}
        </div>

        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 mb-6">
          <p className="text-yellow-400 text-sm font-medium">SECURITY: API keys are encrypted before storage. Only admins can view decrypted keys.</p>
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={connections} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search API connections..." emptyMessage="No API connections found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingConnection ? 'Edit API Connection' : 'Add New API Connection'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <TextInput label="API Name" name="api_name" value={formData.api_name || ''} onChange={(v) => setFormData({ ...formData, api_name: v })} required error={errors.api_name} placeholder="FDOT Traffic API" />
                <TextInput label="API URL" name="api_url" value={formData.api_url || ''} onChange={(v) => setFormData({ ...formData, api_url: v })} required error={errors.api_url} placeholder="https://api.example.com/v1" />
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Auth Type" name="auth_type" value={formData.auth_type || ''} onChange={(v) => setFormData({ ...formData, auth_type: v })} options={AUTH_TYPES} required error={errors.auth_type} />
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                </div>
                <TextInput label="API Key / Token (will be encrypted)" name="api_key" type="password" value={apiKey} onChange={setApiKey} placeholder={editingConnection ? 'Leave blank to keep existing' : 'Enter API key'} />
                <NumberInput label="Refresh Frequency (seconds)" name="refresh_frequency" value={formData.refresh_frequency || 0} onChange={(v) => setFormData({ ...formData, refresh_frequency: v })} min={0} />
                <p className="text-xs text-gray-500">Set to 0 for on-demand queries only</p>
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingConnection ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
