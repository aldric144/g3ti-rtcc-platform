'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, DropdownSelect, TextArea } from '@/components/admin/FormInputs';

interface Robot {
  id: string;
  robot_id: string;
  model: string;
  serial_number: string;
  assigned_unit: string;
  patrol_area: string;
  home_lat: number;
  home_lng: number;
  stream_url: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const ROBOT_MODELS = [
  { value: 'boston_dynamics_spot', label: 'Boston Dynamics Spot' },
  { value: 'ghost_robotics_v60', label: 'Ghost Robotics V60' },
  { value: 'unitree_go2', label: 'Unitree Go2' },
  { value: 'anymal_c', label: 'ANYmal C' },
];

const STATUS_OPTIONS = [
  { value: 'available', label: 'Available' },
  { value: 'patrolling', label: 'Patrolling' },
  { value: 'charging', label: 'Charging' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'offline', label: 'Offline' },
];

const DEMO_ROBOTS: Robot[] = [
  { id: 'robot-001', robot_id: 'RBPD-K9R-001', model: 'boston_dynamics_spot', serial_number: 'BD-SPOT-2024-001', assigned_unit: 'Patrol Unit Alpha', patrol_area: 'Downtown District', home_lat: 26.7754, home_lng: -80.0583, stream_url: 'rtsp://robot1.rbpd.local/stream', status: 'available', notes: 'Primary patrol robot', created_at: '2024-06-01', updated_at: '2024-12-01' },
  { id: 'robot-002', robot_id: 'RBPD-K9R-002', model: 'ghost_robotics_v60', serial_number: 'GR-V60-2024-001', assigned_unit: 'SWAT', patrol_area: 'Industrial Zone', home_lat: 26.7698, home_lng: -80.0789, stream_url: 'rtsp://robot2.rbpd.local/stream', status: 'patrolling', notes: 'Tactical operations robot', created_at: '2024-07-15', updated_at: '2024-12-10' },
];

const columns = [
  { key: 'robot_id', label: 'Robot ID' },
  { key: 'model', label: 'Model' },
  { key: 'assigned_unit', label: 'Assigned Unit' },
  { key: 'patrol_area', label: 'Patrol Area' },
  { key: 'status', label: 'Status' },
];

export default function RobotsAdminPage() {
  const [robots, setRobots] = useState<Robot[]>(DEMO_ROBOTS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingRobot, setEditingRobot] = useState<Robot | null>(null);
  const [formData, setFormData] = useState<Partial<Robot>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => {
    fetchRobots();
  }, []);

  const fetchRobots = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/robots`);
      if (response.ok) {
        const data = await response.json();
        if (data.robots && data.robots.length > 0) setRobots(data.robots);
      }
    } catch (error) {
      console.log('Using demo data');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.robot_id?.trim()) newErrors.robot_id = 'Robot ID is required';
    if (!formData.model) newErrors.model = 'Model is required';
    if (!formData.serial_number?.trim()) newErrors.serial_number = 'Serial number is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingRobot(null);
    setFormData({ robot_id: '', model: '', serial_number: '', assigned_unit: '', patrol_area: '', home_lat: 26.775, home_lng: -80.058, stream_url: '', status: 'available', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (robot: Robot) => {
    setEditingRobot(robot);
    setFormData({ ...robot });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (robot: Robot) => {
    if (!confirm(`Delete robot "${robot.robot_id}"?`)) return;
    setRobots(robots.filter((r) => r.id !== robot.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newRobot: Robot = {
      id: editingRobot?.id || `robot-${Date.now()}`,
      robot_id: formData.robot_id || '',
      model: formData.model || '',
      serial_number: formData.serial_number || '',
      assigned_unit: formData.assigned_unit || '',
      patrol_area: formData.patrol_area || '',
      home_lat: formData.home_lat || 0,
      home_lng: formData.home_lng || 0,
      stream_url: formData.stream_url || '',
      status: formData.status || 'available',
      notes: formData.notes || '',
      created_at: editingRobot?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingRobot) {
      setRobots(robots.map((r) => (r.id === editingRobot.id ? newRobot : r)));
    } else {
      setRobots([...robots, newRobot]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Robot Management</h1>
            <p className="text-gray-400 text-sm">Manage quadruped patrol robots</p>
          </div>
          {canEdit && (
            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Robot</button>
          )}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={robots} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search robots..." emptyMessage="No robots found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingRobot ? 'Edit Robot' : 'Add New Robot'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Robot ID" name="robot_id" value={formData.robot_id || ''} onChange={(v) => setFormData({ ...formData, robot_id: v })} required error={errors.robot_id} placeholder="RBPD-K9R-001" />
                  <TextInput label="Serial Number" name="serial_number" value={formData.serial_number || ''} onChange={(v) => setFormData({ ...formData, serial_number: v })} required error={errors.serial_number} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect label="Model" name="model" value={formData.model || ''} onChange={(v) => setFormData({ ...formData, model: v })} options={ROBOT_MODELS} required error={errors.model} />
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Assigned Unit" name="assigned_unit" value={formData.assigned_unit || ''} onChange={(v) => setFormData({ ...formData, assigned_unit: v })} placeholder="Patrol Unit Alpha" />
                  <TextInput label="Patrol Area" name="patrol_area" value={formData.patrol_area || ''} onChange={(v) => setFormData({ ...formData, patrol_area: v })} placeholder="Downtown District" />
                </div>
                <TextInput label="Stream URL" name="stream_url" value={formData.stream_url || ''} onChange={(v) => setFormData({ ...formData, stream_url: v })} placeholder="rtsp://robot.local/stream" />
                <MapPointInput label="Home Location" value={formData.home_lat && formData.home_lng ? { lat: formData.home_lat, lng: formData.home_lng } : null} onChange={(p) => p ? setFormData({ ...formData, home_lat: p.lat, home_lng: p.lng }) : setFormData({ ...formData, home_lat: undefined, home_lng: undefined })} />
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={3} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingRobot ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
