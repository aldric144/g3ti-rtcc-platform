'use client';

import { useState } from 'react';
import { Camera, MapPin, Plus, Trash2, Edit, Save, X } from 'lucide-react';

interface CameraEntry {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  camera_type: string;
  source: string;
  stream_url: string;
  status: string;
  description?: string;
}

const CAMERA_TYPES = ['traffic', 'marine', 'public', 'beach', 'cctv'];
const CAMERA_SOURCES = ['FDOT', 'Port of Palm Beach', 'Singer Island', 'Marina', 'Custom'];
const PLACEHOLDER_URL = 'https://via.placeholder.com/640x360?text=No+Live+Feed+Available';

export default function ManualAddCameraPage() {
  const [cameras, setCameras] = useState<CameraEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    latitude: '',
    longitude: '',
    camera_type: 'cctv',
    source: 'Custom',
    stream_url: '',
    description: '',
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  const fetchCameras = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/cameras/public`);
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/cameras/manual-add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude),
          camera_type: formData.camera_type,
          source: formData.source,
          stream_url: formData.stream_url || PLACEHOLDER_URL,
          description: formData.description || null,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Camera "${data.camera.name}" added successfully!`);
        setFormData({
          name: '',
          latitude: '',
          longitude: '',
          camera_type: 'cctv',
          source: 'Custom',
          stream_url: '',
          description: '',
        });
        fetchCameras();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add camera');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (cameraId: string) => {
    if (!confirm('Are you sure you want to delete this camera?')) return;

    try {
      const response = await fetch(`${API_URL}/cameras/manual-add/${cameraId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSuccess('Camera deleted successfully');
        fetchCameras();
      } else {
        setError('Failed to delete camera');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <Camera className="h-8 w-8 text-blue-400" />
          <h1 className="text-2xl font-bold">Manual Camera Management</h1>
        </div>

        {/* Add Camera Form */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add New Camera
          </h2>

          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-900/50 border border-green-500 text-green-200 px-4 py-3 rounded mb-4">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Camera Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                placeholder="e.g., City Hall Entrance Cam"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Camera Type *
              </label>
              <select
                value={formData.camera_type}
                onChange={(e) => setFormData({ ...formData, camera_type: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              >
                {CAMERA_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Latitude *
              </label>
              <input
                type="number"
                step="any"
                value={formData.latitude}
                onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                placeholder="e.g., 26.7753"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Longitude *
              </label>
              <input
                type="number"
                step="any"
                value={formData.longitude}
                onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                placeholder="e.g., -80.0589"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Source
              </label>
              <select
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              >
                {CAMERA_SOURCES.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Stream URL (optional)
              </label>
              <input
                type="url"
                value={formData.stream_url}
                onChange={(e) => setFormData({ ...formData, stream_url: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                placeholder="https://..."
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Description (optional)
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                rows={2}
                placeholder="Camera description..."
              />
            </div>

            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded font-medium flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                {isLoading ? 'Adding...' : 'Add Camera'}
              </button>
            </div>
          </form>
        </div>

        {/* Camera List */}
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Camera Catalog
            </h2>
            <button
              onClick={fetchCameras}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm"
            >
              Refresh List
            </button>
          </div>

          {cameras.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Camera className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No cameras loaded. Click "Refresh List" to load cameras.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-3 px-2">Name</th>
                    <th className="text-left py-3 px-2">Type</th>
                    <th className="text-left py-3 px-2">Source</th>
                    <th className="text-left py-3 px-2">Sector</th>
                    <th className="text-left py-3 px-2">Status</th>
                    <th className="text-left py-3 px-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cameras.map((camera) => (
                    <tr key={camera.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                      <td className="py-3 px-2">
                        <div className="font-medium">{camera.name}</div>
                        <div className="text-xs text-gray-400">
                          {camera.gps?.latitude?.toFixed(4)}, {camera.gps?.longitude?.toFixed(4)}
                        </div>
                      </td>
                      <td className="py-3 px-2">
                        <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">
                          {camera.type}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-gray-300">{camera.source}</td>
                      <td className="py-3 px-2 text-gray-300">{camera.sector}</td>
                      <td className="py-3 px-2">
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            camera.status === 'online'
                              ? 'bg-green-900/50 text-green-300'
                              : 'bg-red-900/50 text-red-300'
                          }`}
                        >
                          {camera.status}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        {camera.id.startsWith('manual-') && (
                          <button
                            onClick={() => handleDelete(camera.id)}
                            className="text-red-400 hover:text-red-300 p-1"
                            title="Delete camera"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
