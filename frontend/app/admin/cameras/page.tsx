'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPointInput from '@/components/admin/MapPointInput';
import { TextInput, DropdownSelect, TextArea, ToggleSwitch } from '@/components/admin/FormInputs';

interface Camera {
  id: string;
  name: string;
  lat: number;
  lng: number;
  address: string;
  type: string;
  jurisdiction: string;
  sector_id: string;
  stream_url: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const CAMERA_TYPES = [
  { value: 'fixed', label: 'Fixed' },
  { value: 'ptz', label: 'PTZ' },
  { value: 'dome', label: 'Dome' },
  { value: 'bullet', label: 'Bullet' },
  { value: 'lpr', label: 'LPR' },
  { value: 'thermal', label: 'Thermal' },
];

const JURISDICTIONS = [
  { value: 'rbpd', label: 'RBPD' },
  { value: 'pbso', label: 'PBSO' },
  { value: 'fdot', label: 'FDOT' },
  { value: 'city', label: 'City' },
  { value: 'private', label: 'Private' },
];

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'offline', label: 'Offline' },
];

const DEMO_CAMERAS: Camera[] = [
  { id: 'cam-001', name: 'City Hall Main', lat: 26.7754, lng: -80.0583, address: '600 W Blue Heron Blvd', type: 'ptz', jurisdiction: 'rbpd', sector_id: 'sector-1', stream_url: 'rtsp://camera1.rbpd.local/stream', status: 'active', notes: 'Main entrance coverage', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'cam-002', name: 'Marina District', lat: 26.7821, lng: -80.0512, address: '200 E 13th St', type: 'fixed', jurisdiction: 'city', sector_id: 'sector-2', stream_url: 'rtsp://camera2.rbpd.local/stream', status: 'active', notes: 'Marina area surveillance', created_at: '2024-02-20', updated_at: '2024-11-15' },
  { id: 'cam-003', name: 'I-95 Overpass', lat: 26.7698, lng: -80.0789, address: 'I-95 at Blue Heron', type: 'lpr', jurisdiction: 'fdot', sector_id: 'sector-3', stream_url: 'rtsp://fdot-cam3.fl.gov/stream', status: 'active', notes: 'FDOT traffic camera with LPR', created_at: '2024-03-10', updated_at: '2024-12-05' },
  { id: 'cam-004', name: 'School Zone Alpha', lat: 26.7712, lng: -80.0634, address: '1500 W 10th St', type: 'dome', jurisdiction: 'rbpd', sector_id: 'sector-1', stream_url: 'rtsp://camera4.rbpd.local/stream', status: 'maintenance', notes: 'School zone monitoring', created_at: '2024-04-05', updated_at: '2024-12-10' },
];

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'jurisdiction', label: 'Jurisdiction' },
  { key: 'sector_id', label: 'Sector' },
  { key: 'status', label: 'Status' },
  { key: 'address', label: 'Address' },
];

export default function CamerasAdminPage() {
  const [cameras, setCameras] = useState<Camera[]>(DEMO_CAMERAS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  const [formData, setFormData] = useState<Partial<Camera>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/cameras`);
      if (response.ok) {
        const data = await response.json();
        if (data.cameras && data.cameras.length > 0) {
          setCameras(data.cameras);
        }
      }
    } catch (error) {
      console.log('Using demo data');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.lat || !formData.lng) {
      newErrors.location = 'Location is required';
    } else {
      if (formData.lat < 26.74 || formData.lat > 26.82 || formData.lng < -80.10 || formData.lng > -80.03) {
        newErrors.location = 'Location must be within Riviera Beach boundaries';
      }
    }
    if (!formData.type) {
      newErrors.type = 'Type is required';
    }
    if (!formData.stream_url?.trim()) {
      newErrors.stream_url = 'Stream URL is required';
    } else if (!formData.stream_url.match(/^(rtsp|http|https):\/\/.+/)) {
      newErrors.stream_url = 'Invalid stream URL format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingCamera(null);
    setFormData({
      name: '',
      lat: 26.775,
      lng: -80.058,
      address: '',
      type: '',
      jurisdiction: 'rbpd',
      sector_id: '',
      stream_url: '',
      status: 'active',
      notes: '',
    });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (camera: Camera) => {
    setEditingCamera(camera);
    setFormData({ ...camera });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (camera: Camera) => {
    if (!confirm(`Are you sure you want to delete camera "${camera.name}"?`)) {
      return;
    }

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/cameras/${camera.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setCameras(cameras.filter((c) => c.id !== camera.id));
      } else {
        setCameras(cameras.filter((c) => c.id !== camera.id));
      }
    } catch (error) {
      setCameras(cameras.filter((c) => c.id !== camera.id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaving(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const url = editingCamera
        ? `${backendUrl}/api/admin/cameras/${editingCamera.id}`
        : `${backendUrl}/api/admin/cameras`;
      const method = editingCamera ? 'PATCH' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const savedCamera = await response.json();
        if (editingCamera) {
          setCameras(cameras.map((c) => (c.id === editingCamera.id ? savedCamera : c)));
        } else {
          setCameras([...cameras, savedCamera]);
        }
        setShowForm(false);
      } else {
        const newCamera: Camera = {
          id: editingCamera?.id || `cam-${Date.now()}`,
          name: formData.name || '',
          lat: formData.lat || 0,
          lng: formData.lng || 0,
          address: formData.address || '',
          type: formData.type || '',
          jurisdiction: formData.jurisdiction || '',
          sector_id: formData.sector_id || '',
          stream_url: formData.stream_url || '',
          status: formData.status || 'active',
          notes: formData.notes || '',
          created_at: editingCamera?.created_at || new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        if (editingCamera) {
          setCameras(cameras.map((c) => (c.id === editingCamera.id ? newCamera : c)));
        } else {
          setCameras([...cameras, newCamera]);
        }
        setShowForm(false);
      }
    } catch (error) {
      const newCamera: Camera = {
        id: editingCamera?.id || `cam-${Date.now()}`,
        name: formData.name || '',
        lat: formData.lat || 0,
        lng: formData.lng || 0,
        address: formData.address || '',
        type: formData.type || '',
        jurisdiction: formData.jurisdiction || '',
        sector_id: formData.sector_id || '',
        stream_url: formData.stream_url || '',
        status: formData.status || 'active',
        notes: formData.notes || '',
        created_at: editingCamera?.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      if (editingCamera) {
        setCameras(cameras.map((c) => (c.id === editingCamera.id ? newCamera : c)));
      } else {
        setCameras([...cameras, newCamera]);
      }
      setShowForm(false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Camera Management</h1>
            <p className="text-gray-400 text-sm">Manage surveillance cameras across all jurisdictions</p>
          </div>
          {canEdit && (
            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
            >
              + Add Camera
            </button>
          )}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable
            columns={columns}
            data={cameras}
            loading={loading}
            onView={(camera) => handleEdit(camera)}
            onEdit={canEdit ? handleEdit : undefined}
            onDelete={canDelete ? handleDelete : undefined}
            canEdit={canEdit}
            canDelete={canDelete}
            searchPlaceholder="Search cameras..."
            emptyMessage="No cameras found"
          />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">
                  {editingCamera ? 'Edit Camera' : 'Add New Camera'}
                </h2>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <TextInput
                  label="Camera Name"
                  name="name"
                  value={formData.name || ''}
                  onChange={(value) => setFormData({ ...formData, name: value })}
                  required
                  error={errors.name}
                  placeholder="e.g., City Hall Main Entrance"
                />

                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect
                    label="Type"
                    name="type"
                    value={formData.type || ''}
                    onChange={(value) => setFormData({ ...formData, type: value })}
                    options={CAMERA_TYPES}
                    required
                    error={errors.type}
                  />

                  <DropdownSelect
                    label="Jurisdiction"
                    name="jurisdiction"
                    value={formData.jurisdiction || ''}
                    onChange={(value) => setFormData({ ...formData, jurisdiction: value })}
                    options={JURISDICTIONS}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <DropdownSelect
                    label="Status"
                    name="status"
                    value={formData.status || ''}
                    onChange={(value) => setFormData({ ...formData, status: value })}
                    options={STATUS_OPTIONS}
                    required
                  />

                  <TextInput
                    label="Sector ID"
                    name="sector_id"
                    value={formData.sector_id || ''}
                    onChange={(value) => setFormData({ ...formData, sector_id: value })}
                    placeholder="e.g., sector-1"
                  />
                </div>

                <TextInput
                  label="Address"
                  name="address"
                  value={formData.address || ''}
                  onChange={(value) => setFormData({ ...formData, address: value })}
                  placeholder="e.g., 600 W Blue Heron Blvd"
                />

                <TextInput
                  label="Stream URL"
                  name="stream_url"
                  value={formData.stream_url || ''}
                  onChange={(value) => setFormData({ ...formData, stream_url: value })}
                  required
                  error={errors.stream_url}
                  placeholder="rtsp://camera.local/stream"
                />

                <MapPointInput
                  label="Location"
                  value={formData.lat && formData.lng ? { lat: formData.lat, lng: formData.lng } : null}
                  onChange={(point) => {
                    if (point) {
                      setFormData({ ...formData, lat: point.lat, lng: point.lng });
                    } else {
                      setFormData({ ...formData, lat: undefined, lng: undefined });
                    }
                  }}
                  required
                />
                {errors.location && <p className="text-xs text-red-400">{errors.location}</p>}

                <TextArea
                  label="Notes"
                  name="notes"
                  value={formData.notes || ''}
                  onChange={(value) => setFormData({ ...formData, notes: value })}
                  placeholder="Additional notes about this camera..."
                  rows={3}
                />

                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : editingCamera ? 'Update Camera' : 'Create Camera'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
