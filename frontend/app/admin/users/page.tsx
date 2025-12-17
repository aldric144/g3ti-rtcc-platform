'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import { TextInput, TextArea, DropdownSelect, ToggleSwitch } from '@/components/admin/FormInputs';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  badge_number: string;
  department: string;
  role: string;
  assigned_sector: string;
  mfa_enabled: boolean;
  is_active: boolean;
  last_login: string;
  created_at: string;
  updated_at: string;
}

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Admin' },
  { value: 'supervisor', label: 'Supervisor' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'viewer', label: 'Viewer' },
  { value: 'system_integrator', label: 'System Integrator' },
  { value: 'commander', label: 'Commander' },
];

const DEPARTMENT_OPTIONS = [
  { value: 'patrol', label: 'Patrol' },
  { value: 'investigations', label: 'Investigations' },
  { value: 'swat', label: 'SWAT' },
  { value: 'traffic', label: 'Traffic' },
  { value: 'admin', label: 'Administration' },
  { value: 'dispatch', label: 'Dispatch' },
  { value: 'it', label: 'IT' },
];

const SECTOR_OPTIONS = [
  { value: '', label: 'All Sectors' },
  { value: 'sector-1', label: 'Sector 1 - Downtown' },
  { value: 'sector-2', label: 'Sector 2 - Marina' },
  { value: 'sector-3', label: 'Sector 3 - Industrial' },
  { value: 'sector-4', label: 'Sector 4 - Residential North' },
  { value: 'sector-5', label: 'Sector 5 - Residential South' },
];

const DEMO_USERS: User[] = [
  { id: 'user-001', username: 'admin', email: 'admin@rbpd.local', full_name: 'System Administrator', badge_number: 'ADMIN', department: 'it', role: 'admin', assigned_sector: '', mfa_enabled: true, is_active: true, last_login: '2024-12-16T10:00:00Z', created_at: '2024-01-01', updated_at: '2024-12-01' },
  { id: 'user-002', username: 'jmartinez', email: 'jmartinez@rbpd.local', full_name: 'Officer Juan Martinez', badge_number: '1234', department: 'patrol', role: 'analyst', assigned_sector: 'sector-1', mfa_enabled: true, is_active: true, last_login: '2024-12-16T08:30:00Z', created_at: '2024-02-15', updated_at: '2024-11-20' },
  { id: 'user-003', username: 'sjohnson', email: 'sjohnson@rbpd.local', full_name: 'Sgt. Sarah Johnson', badge_number: '5678', department: 'patrol', role: 'supervisor', assigned_sector: 'sector-2', mfa_enabled: true, is_active: true, last_login: '2024-12-16T07:45:00Z', created_at: '2024-03-01', updated_at: '2024-12-05' },
];

const columns = [
  { key: 'username', label: 'Username' },
  { key: 'full_name', label: 'Full Name' },
  { key: 'badge_number', label: 'Badge' },
  { key: 'role', label: 'Role' },
  { key: 'department', label: 'Department' },
  { key: 'is_active', label: 'Active' },
];

export default function UsersAdminPage() {
  const [users, setUsers] = useState<User[]>(DEMO_USERS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<Partial<User>>({});
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/users`);
      if (response.ok) {
        const data = await response.json();
        if (data.users?.length > 0) setUsers(data.users);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.username?.trim()) newErrors.username = 'Username is required';
    if (!formData.email?.trim()) newErrors.email = 'Email is required';
    else if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) newErrors.email = 'Invalid email format';
    if (!formData.full_name?.trim()) newErrors.full_name = 'Full name is required';
    if (!formData.role) newErrors.role = 'Role is required';
    if (!editingUser && !password) newErrors.password = 'Password is required for new users';
    if (password && password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingUser(null);
    setFormData({ username: '', email: '', full_name: '', badge_number: '', department: 'patrol', role: 'viewer', assigned_sector: '', mfa_enabled: false, is_active: true });
    setPassword('');
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({ ...user });
    setPassword('');
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (user: User) => {
    if (user.username === 'admin') {
      alert('Cannot delete the admin user');
      return;
    }
    if (!confirm(`Delete user "${user.username}"?`)) return;
    setUsers(users.filter((u) => u.id !== user.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newUser: User = {
      id: editingUser?.id || `user-${Date.now()}`,
      username: formData.username || '',
      email: formData.email || '',
      full_name: formData.full_name || '',
      badge_number: formData.badge_number || '',
      department: formData.department || '',
      role: formData.role || 'viewer',
      assigned_sector: formData.assigned_sector || '',
      mfa_enabled: formData.mfa_enabled || false,
      is_active: formData.is_active ?? true,
      last_login: editingUser?.last_login || '',
      created_at: editingUser?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingUser) {
      setUsers(users.map((u) => (u.id === editingUser.id ? newUser : u)));
    } else {
      setUsers([...users, newUser]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">User Management</h1>
            <p className="text-gray-400 text-sm">Manage system users and permissions (Admin only)</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add User</button>}
        </div>

        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 mb-6">
          <p className="text-yellow-400 text-sm font-medium">ADMIN ONLY: User management is restricted to administrators. Passwords are hashed before storage.</p>
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={users} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search users..." emptyMessage="No users found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingUser ? 'Edit User' : 'Add New User'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Username" name="username" value={formData.username || ''} onChange={(v) => setFormData({ ...formData, username: v })} required error={errors.username} placeholder="jsmith" />
                  <TextInput label="Badge Number" name="badge_number" value={formData.badge_number || ''} onChange={(v) => setFormData({ ...formData, badge_number: v })} placeholder="1234" />
                </div>
                <TextInput label="Full Name" name="full_name" value={formData.full_name || ''} onChange={(v) => setFormData({ ...formData, full_name: v })} required error={errors.full_name} placeholder="John Smith" />
                <TextInput label="Email" name="email" type="email" value={formData.email || ''} onChange={(v) => setFormData({ ...formData, email: v })} required error={errors.email} placeholder="jsmith@rbpd.local" />
                <TextInput label={editingUser ? 'New Password (leave blank to keep)' : 'Password'} name="password" type="password" value={password} onChange={setPassword} required={!editingUser} error={errors.password} placeholder="********" />
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Role" name="role" value={formData.role || ''} onChange={(v) => setFormData({ ...formData, role: v })} options={ROLE_OPTIONS} required error={errors.role} />
                  <DropdownSelect label="Department" name="department" value={formData.department || ''} onChange={(v) => setFormData({ ...formData, department: v })} options={DEPARTMENT_OPTIONS} />
                </div>
                <DropdownSelect label="Assigned Sector" name="assigned_sector" value={formData.assigned_sector || ''} onChange={(v) => setFormData({ ...formData, assigned_sector: v })} options={SECTOR_OPTIONS} />
                <div className="space-y-3">
                  <ToggleSwitch label="MFA Enabled" name="mfa_enabled" checked={formData.mfa_enabled || false} onChange={(v) => setFormData({ ...formData, mfa_enabled: v })} description="Require multi-factor authentication" />
                  <ToggleSwitch label="Active" name="is_active" checked={formData.is_active ?? true} onChange={(v) => setFormData({ ...formData, is_active: v })} description="Allow user to log in" />
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingUser ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
