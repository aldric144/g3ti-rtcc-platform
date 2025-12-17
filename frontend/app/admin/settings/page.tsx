'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import { TextInput, TextArea, DropdownSelect, ToggleSwitch } from '@/components/admin/FormInputs';

interface SystemSetting {
  id: string;
  setting_key: string;
  setting_value: string;
  category: string;
  description: string;
  is_sensitive: boolean;
  requires_restart: boolean;
  created_at: string;
  updated_at: string;
}

const CATEGORY_OPTIONS = [
  { value: 'general', label: 'General' },
  { value: 'security', label: 'Security' },
  { value: 'video_wall', label: 'Video Wall' },
  { value: 'alerts', label: 'Alerts' },
  { value: 'integrations', label: 'Integrations' },
  { value: 'performance', label: 'Performance' },
  { value: 'ui', label: 'User Interface' },
];

const DEMO_SETTINGS: SystemSetting[] = [
  { id: 'set-001', setting_key: 'video_wall_layout', setting_value: '4x4', category: 'video_wall', description: 'Default video wall grid layout', is_sensitive: false, requires_restart: false, created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'set-002', setting_key: 'alert_threshold_critical', setting_value: '90', category: 'alerts', description: 'Threshold for critical alerts (0-100)', is_sensitive: false, requires_restart: false, created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'set-003', setting_key: 'session_timeout_minutes', setting_value: '30', category: 'security', description: 'User session timeout in minutes', is_sensitive: false, requires_restart: true, created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'set-004', setting_key: 'max_concurrent_streams', setting_value: '16', category: 'performance', description: 'Maximum concurrent video streams', is_sensitive: false, requires_restart: true, created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'set-005', setting_key: 'encryption_key', setting_value: '[ENCRYPTED]', category: 'security', description: 'System encryption key', is_sensitive: true, requires_restart: true, created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'set-006', setting_key: 'default_theme', setting_value: 'neural_cosmic_matrix', category: 'ui', description: 'Default UI theme', is_sensitive: false, requires_restart: false, created_at: '2024-01-01', updated_at: '2024-12-01' },
];

const columns = [
  { key: 'setting_key', label: 'Setting Key' },
  { key: 'setting_value', label: 'Value', render: (v: string, row: SystemSetting) => row.is_sensitive ? '[HIDDEN]' : v },
  { key: 'category', label: 'Category' },
  { key: 'requires_restart', label: 'Restart Required' },
];

export default function SettingsAdminPage() {
  const [settings, setSettings] = useState<SystemSetting[]>(DEMO_SETTINGS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingSetting, setEditingSetting] = useState<SystemSetting | null>(null);
  const [formData, setFormData] = useState<Partial<SystemSetting>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchSettings(); }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/system_settings`);
      if (response.ok) {
        const data = await response.json();
        if (data.system_settings?.length > 0) setSettings(data.system_settings);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.setting_key?.trim()) newErrors.setting_key = 'Setting key is required';
    if (!formData.setting_value?.trim()) newErrors.setting_value = 'Value is required';
    if (!formData.category) newErrors.category = 'Category is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingSetting(null);
    setFormData({ setting_key: '', setting_value: '', category: 'general', description: '', is_sensitive: false, requires_restart: false });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (setting: SystemSetting) => {
    setEditingSetting(setting);
    setFormData({ ...setting, setting_value: setting.is_sensitive ? '' : setting.setting_value });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (setting: SystemSetting) => {
    if (!confirm(`Delete setting "${setting.setting_key}"?`)) return;
    setSettings(settings.filter((s) => s.id !== setting.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newSetting: SystemSetting = {
      id: editingSetting?.id || `set-${Date.now()}`,
      setting_key: formData.setting_key || '',
      setting_value: formData.is_sensitive && !formData.setting_value ? (editingSetting?.setting_value || '[ENCRYPTED]') : (formData.setting_value || ''),
      category: formData.category || 'general',
      description: formData.description || '',
      is_sensitive: formData.is_sensitive || false,
      requires_restart: formData.requires_restart || false,
      created_at: editingSetting?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingSetting) {
      setSettings(settings.map((s) => (s.id === editingSetting.id ? newSetting : s)));
    } else {
      setSettings([...settings, newSetting]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">System Settings</h1>
            <p className="text-gray-400 text-sm">Manage global system configuration (Admin only)</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Setting</button>}
        </div>

        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 mb-6">
          <p className="text-yellow-400 text-sm font-medium">WARNING: Changing system settings may affect platform stability. Settings marked "Restart Required" need a system restart to take effect.</p>
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={settings} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search settings..." emptyMessage="No settings found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingSetting ? 'Edit Setting' : 'Add New Setting'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <TextInput label="Setting Key" name="setting_key" value={formData.setting_key || ''} onChange={(v) => setFormData({ ...formData, setting_key: v })} required error={errors.setting_key} placeholder="video_wall_layout" disabled={!!editingSetting} />
                <TextInput label={editingSetting?.is_sensitive ? 'Value (leave blank to keep existing)' : 'Value'} name="setting_value" value={formData.setting_value || ''} onChange={(v) => setFormData({ ...formData, setting_value: v })} required={!editingSetting?.is_sensitive} error={errors.setting_value} placeholder="Enter value" type={formData.is_sensitive ? 'password' : 'text'} />
                <DropdownSelect label="Category" name="category" value={formData.category || ''} onChange={(v) => setFormData({ ...formData, category: v })} options={CATEGORY_OPTIONS} required error={errors.category} />
                <TextArea label="Description" name="description" value={formData.description || ''} onChange={(v) => setFormData({ ...formData, description: v })} placeholder="Describe what this setting controls..." rows={2} />
                <div className="space-y-3">
                  <ToggleSwitch label="Sensitive Value" name="is_sensitive" checked={formData.is_sensitive || false} onChange={(v) => setFormData({ ...formData, is_sensitive: v })} description="Hide value in UI and encrypt in storage" />
                  <ToggleSwitch label="Requires Restart" name="requires_restart" checked={formData.requires_restart || false} onChange={(v) => setFormData({ ...formData, requires_restart: v })} description="System restart needed for changes to take effect" />
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingSetting ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
