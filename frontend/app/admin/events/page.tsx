'use client';

import React, { useState, useEffect } from 'react';
import AdminTable from '@/components/admin/AdminTable';
import MapPolygonInput from '@/components/admin/MapPolygonInput';
import { TextInput, TextArea, DropdownSelect, NumberInput } from '@/components/admin/FormInputs';

interface PolygonPoint { lat: number; lng: number; }

interface Event {
  id: string;
  event_name: string;
  event_type: string;
  boundary: PolygonPoint[];
  start_time: string;
  end_time: string;
  expected_attendance: number;
  organizer: string;
  road_closures: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

const EVENT_TYPES = [
  { value: 'parade', label: 'Parade' },
  { value: 'festival', label: 'Festival' },
  { value: 'concert', label: 'Concert' },
  { value: 'sports', label: 'Sports Event' },
  { value: 'protest', label: 'Protest/Rally' },
  { value: 'construction', label: 'Construction' },
  { value: 'emergency', label: 'Emergency' },
  { value: 'other', label: 'Other' },
];

const STATUS_OPTIONS = [
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const DEMO_EVENTS: Event[] = [
  { id: 'event-001', event_name: 'Riviera Beach Festival', event_type: 'festival', boundary: [{ lat: 26.78, lng: -80.06 }, { lat: 26.78, lng: -80.05 }, { lat: 26.77, lng: -80.05 }, { lat: 26.77, lng: -80.06 }], start_time: '2024-12-20T10:00:00Z', end_time: '2024-12-20T22:00:00Z', expected_attendance: 5000, organizer: 'City of Riviera Beach', road_closures: 'Blue Heron Blvd from Avenue E to Avenue H', status: 'scheduled', notes: 'Annual city festival', created_at: '2024-11-01', updated_at: '2024-12-01' },
  { id: 'event-002', event_name: 'Marina Boat Show', event_type: 'festival', boundary: [{ lat: 26.785, lng: -80.055 }, { lat: 26.785, lng: -80.045 }, { lat: 26.775, lng: -80.045 }, { lat: 26.775, lng: -80.055 }], start_time: '2024-12-25T09:00:00Z', end_time: '2024-12-25T18:00:00Z', expected_attendance: 2000, organizer: 'Marina Association', road_closures: 'E 13th St closed to through traffic', status: 'scheduled', notes: 'Annual boat show', created_at: '2024-11-15', updated_at: '2024-12-05' },
];

const columns = [
  { key: 'event_name', label: 'Event Name' },
  { key: 'event_type', label: 'Type' },
  { key: 'start_time', label: 'Start', render: (v: string) => new Date(v).toLocaleDateString() },
  { key: 'expected_attendance', label: 'Attendance' },
  { key: 'status', label: 'Status' },
];

export default function EventsAdminPage() {
  const [events, setEvents] = useState<Event[]>(DEMO_EVENTS);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [formData, setFormData] = useState<Partial<Event>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [userRole] = useState<string>('admin');

  const canEdit = userRole === 'admin' || userRole === 'supervisor';
  const canDelete = userRole === 'admin';

  useEffect(() => { fetchEvents(); }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://g3ti-rtcc-backend.fly.dev';
      const response = await fetch(`${backendUrl}/api/admin/events`);
      if (response.ok) {
        const data = await response.json();
        if (data.events?.length > 0) setEvents(data.events);
      }
    } catch (error) { console.log('Using demo data'); }
    finally { setLoading(false); }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.event_name?.trim()) newErrors.event_name = 'Event name is required';
    if (!formData.event_type) newErrors.event_type = 'Event type is required';
    if (!formData.start_time) newErrors.start_time = 'Start time is required';
    if (!formData.end_time) newErrors.end_time = 'End time is required';
    if (formData.start_time && formData.end_time && new Date(formData.start_time) >= new Date(formData.end_time)) {
      newErrors.end_time = 'End time must be after start time';
    }
    if (!formData.boundary || formData.boundary.length < 3) newErrors.boundary = 'Event boundary must have at least 3 points';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = () => {
    setEditingEvent(null);
    setFormData({ event_name: '', event_type: '', boundary: [], start_time: '', end_time: '', expected_attendance: 0, organizer: '', road_closures: '', status: 'scheduled', notes: '' });
    setErrors({});
    setShowForm(true);
  };

  const handleEdit = (event: Event) => {
    setEditingEvent(event);
    setFormData({ ...event });
    setErrors({});
    setShowForm(true);
  };

  const handleDelete = async (event: Event) => {
    if (!confirm(`Delete event "${event.event_name}"?`)) return;
    setEvents(events.filter((e) => e.id !== event.id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setSaving(true);

    const newEvent: Event = {
      id: editingEvent?.id || `event-${Date.now()}`,
      event_name: formData.event_name || '',
      event_type: formData.event_type || '',
      boundary: formData.boundary || [],
      start_time: formData.start_time || '',
      end_time: formData.end_time || '',
      expected_attendance: formData.expected_attendance || 0,
      organizer: formData.organizer || '',
      road_closures: formData.road_closures || '',
      status: formData.status || 'scheduled',
      notes: formData.notes || '',
      created_at: editingEvent?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    if (editingEvent) {
      setEvents(events.map((e) => (e.id === editingEvent.id ? newEvent : e)));
    } else {
      setEvents([...events, newEvent]);
    }
    setShowForm(false);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0f24] text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Event Management</h1>
            <p className="text-gray-400 text-sm">Manage special events and road closures</p>
          </div>
          {canEdit && <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">+ Add Event</button>}
        </div>

        <div className="bg-gray-900/50 rounded-xl border border-gray-700 p-6">
          <AdminTable columns={columns} data={events} loading={loading} onView={handleEdit} onEdit={canEdit ? handleEdit : undefined} onDelete={canDelete ? handleDelete : undefined} canEdit={canEdit} canDelete={canDelete} searchPlaceholder="Search events..." emptyMessage="No events found" />
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold">{editingEvent ? 'Edit Event' : 'Add New Event'}</h2>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <TextInput label="Event Name" name="event_name" value={formData.event_name || ''} onChange={(v) => setFormData({ ...formData, event_name: v })} required error={errors.event_name} placeholder="Riviera Beach Festival" />
                  <DropdownSelect label="Event Type" name="event_type" value={formData.event_type || ''} onChange={(v) => setFormData({ ...formData, event_type: v })} options={EVENT_TYPES} required error={errors.event_type} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-300">Start Time <span className="text-red-500">*</span></label>
                    <input type="datetime-local" value={formData.start_time?.slice(0, 16) || ''} onChange={(e) => setFormData({ ...formData, start_time: e.target.value })} className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white" />
                    {errors.start_time && <p className="text-xs text-red-400">{errors.start_time}</p>}
                  </div>
                  <div className="space-y-1">
                    <label className="block text-sm font-medium text-gray-300">End Time <span className="text-red-500">*</span></label>
                    <input type="datetime-local" value={formData.end_time?.slice(0, 16) || ''} onChange={(e) => setFormData({ ...formData, end_time: e.target.value })} className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white" />
                    {errors.end_time && <p className="text-xs text-red-400">{errors.end_time}</p>}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <NumberInput label="Expected Attendance" name="expected_attendance" value={formData.expected_attendance || 0} onChange={(v) => setFormData({ ...formData, expected_attendance: v })} min={0} />
                  <DropdownSelect label="Status" name="status" value={formData.status || ''} onChange={(v) => setFormData({ ...formData, status: v })} options={STATUS_OPTIONS} required />
                </div>
                <TextInput label="Organizer" name="organizer" value={formData.organizer || ''} onChange={(v) => setFormData({ ...formData, organizer: v })} placeholder="City of Riviera Beach" />
                <TextArea label="Road Closures" name="road_closures" value={formData.road_closures || ''} onChange={(v) => setFormData({ ...formData, road_closures: v })} placeholder="List affected roads..." rows={2} />
                <MapPolygonInput label="Event Boundary" value={formData.boundary} onChange={(v) => setFormData({ ...formData, boundary: v || [] })} required minPoints={3} />
                {errors.boundary && <p className="text-xs text-red-400">{errors.boundary}</p>}
                <TextArea label="Notes" name="notes" value={formData.notes || ''} onChange={(v) => setFormData({ ...formData, notes: v })} rows={2} />
                <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">Cancel</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50">{saving ? 'Saving...' : editingEvent ? 'Update' : 'Create'}</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
