'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPolygonInput from '@/components/admin/MapPolygonInput';
import { TextInput, TextArea, DropdownSelect, ToggleSwitch } from '@/components/admin/FormInputs';

interface PolygonPoint { lat: number; lng: number; }

interface School {
  id: string;
  name: string;
  grade_level: string;
  address: string;
  perimeter: PolygonPoint[];
  pickup_routes: string;
  access_points: string;
  sro_assigned: string;
  has_sro: boolean;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const GRADE_LEVELS = [
  { value: 'elementary', label: 'Elementary' },
  { value: 'middle', label: 'Middle School' },
  { value: 'high', label: 'High School' },
  { value: 'k12', label: 'K-12' },
  { value: 'charter', label: 'Charter' },
  { value: 'private', label: 'Private' },
];

const DEMO_SCHOOLS: School[] = [
  { id: 'school-001', name: 'Riviera Beach Elementary', grade_level: 'elementary', address: '1500 W 10th St', perimeter: [{ lat: 26.775, lng: -80.065 }, { lat: 26.775, lng: -80.060 }, { lat: 26.770, lng: -80.060 }, { lat: 26.770, lng: -80.065 }], pickup_routes: 'Main entrance on 10th St, bus loop on west side', access_points: 'Main entrance, gym entrance, cafeteria', sro_assigned: 'Officer Davis', has_sro: true, status: 'active', notes: 'Primary elementary school', created_at: '2024-01-15', updated_at: '2024-12-01' },
  { id: 'school-002', name: 'Riviera Beach High', grade_level: 'high', address: '2000 Avenue L', perimeter: [{ lat: 26.780, lng: -80.055 }, { lat: 26.780, lng: -80.045 }, { lat: 26.772, lng: -80.045 }, { lat: 26.772, lng: -80.055 }], pickup_routes: 'Student parking on east, parent pickup on Avenue L', access_points: 'Main entrance, athletic complex, auditorium', sro_assigned: 'Officer Martinez', has_sro: true, status: 'active', notes: 'Main high school', created_at: '2024-02-20', updated_at: '2024-11-15' },
];

const columns = [
  { key: 'name', label: 'School Name' },
  { key: 'grade_level', label: 'Grade Level' },
  { key: 'address', label: 'Address' },
  { key: 'has_sro', label: 'SRO Assigned' },
  { key: 'status', label: 'Status' },
];

export default function SchoolsAdminPage() {
  const [schools, setSchools] = useState<School[]>(DEMO_SCHOOLS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingSchool, setEditingSchool] = useState<School | null>(null);
  const [formData, setFormData] = useState<Partial<School>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchSchools(); }, []);

  const fetchSchools = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend-harpclib.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/schools`);
      if (response.ok) {
        const data = await response.json();
        if (data.schools?.length > 0) setSchools(data.schools);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) newErrors.name = 'School name is required';
    if (!formData.grade_level) newErrors.grade_level = 'Grade level is required';
    if (!formData.perimeter || formData.perimeter.length < 3) newErrors.perimeter = 'Perimeter must have at least 3 points';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingSchool(null);
    setFormData({ name: '', grade_level: '', address: '', perimeter: [], pickup_routes: '', access_points: '', sro_assigned: '', has_sro: false, status: 'active', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (school: School) => {
    setEditingSchool(school);
    setFormData({ ...school });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (school: School) => {
    if (!confirm(`Delete "${school.name}"?`)) return;
    setSchools(schools.filter((s) => s.id !== school.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newSchool: School = {
      id: editingSchool?.id || `school-${Date.now()}`,
      name: formData.name || '',
      grade_level: formData.grade_level || '',
      address: formData.address || '',
      perimeter: formData.perimeter || [],
      pickup_routes: formData.pickup_routes || '',
      access_points: formData.access_points || '',
      sro_assigned: formData.sro_assigned || '',
      has_sro: formData.has_sro || false,
      status: formData.status || 'active',
      notes: formData.notes || '',
      created_at: editingSchool?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingSchool) {
      setSchools(schools.map((s) => (s.id === editingSchool.id ? newSchool : s)));
    } else {
      setSchools([...schools, newSchool]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">School Management</h1>
            <p className="text-gray-400 text-sm">Manage school perimeters and SRO assignments</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add School</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={schools} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search schools..." emptyMessage="No schools found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingSchool ? 'Edit School' : 'Add New School'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="School Name" name="name" value={formData.name || ''} onChange={(v) => setFormData({ ...formData, name: v })} required error={errors.name} placeholder="Riviera Beach Elementary" />
                  <DropdownSelect label="Grade Level" name="grade_level" value={formData.grade_level || ''} onChange={(v) => setFormData({ ...formData, grade_level: v })} options={GRADE_LEVELS} required error={errors.grade_level} />
                </div>
                <TextInput label="Address" name="address" value={formData.address || ''} onChange={(v) => setFormData({ ...formData, address: v })} placeholder="1500 W 10th St" />
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="SRO Assigned" name="sro_assigned" value={formData.sro_assigned || ''} onChange={(v) => setFormData({ ...formData, sro_assigned: v })} placeholder="Officer Name" />
                  <div className="flex items-end">
                    <ToggleSwitch label="Has SRO" name="has_sro" checked={formData.has_sro || false} onChange={(v) => setFormData({ ...formData, has_sro: v })} />
                  </div>
                </div>
                <TextArea label="Pickup Routes" name="pickup_routes" value={formData.pickup_routes || ''} onChange={(v) => setFormData({ ...formData, pickup_routes: v })} placeholder="Describe pickup and drop-off routes..." rows={2} />
                <TextArea label="Access Points" name="access_points" value={formData.access_points || ''} onChange={(v) => setFormData({ ...formData, access_points: v })} placeholder="Main entrance, gym entrance, etc." rows={2} />
                <MapPolygonInput label="School Perimeter" value={formData.perimeter} onChange={(v) => setFormData({ ...formData, perimeter: v || [] })} required minPoints={3} />
                {errors.perimeter && <p className="text-xs text-red-400">{errors.perimeter}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingSchool ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
