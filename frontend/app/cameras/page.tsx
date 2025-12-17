'use client';

import { useEffect, useState, useCallback } from 'react';
import { 
  Camera, 
  RefreshCw, 
  Search, 
  Filter, 
  Grid, 
  List,
  MapPin,
  Video,
  Eye,
  Plus,
  Settings
} from 'lucide-react';
import Link from 'next/link';

interface CameraData {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  gps?: { latitude: number; longitude: number };
  stream_url: string;
  camera_type: string;
  type?: string;
  jurisdiction: string;
  sector: string;
  status: string;
  description?: string;
  marker_color?: string;
  fdot_id?: string;
  supports_mjpeg?: boolean;
  snapshot_url?: string;
}

export default function CameraDirectoryPage() {
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [filteredCameras, setFilteredCameras] = useState<CameraData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState({
    jurisdiction: '',
    camera_type: '',
    sector: '',
    status: '',
  });

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const fetchCameras = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/cameras`);
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
        setFilteredCameras(data.cameras || []);
        setError(null);
      } else {
        throw new Error('Failed to fetch cameras');
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
      setError('Unable to load cameras. Using demo data.');
      // Load demo data
      try {
        const demoResponse = await fetch('/demo_data/public_cameras.json');
        if (demoResponse.ok) {
          const demoData = await demoResponse.json();
          setCameras(demoData.cameras || []);
          setFilteredCameras(demoData.cameras || []);
        }
      } catch {
        setCameras([]);
        setFilteredCameras([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  // Apply filters and search
  useEffect(() => {
    let result = cameras;

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(cam => 
        cam.name.toLowerCase().includes(query) ||
        cam.sector?.toLowerCase().includes(query) ||
        cam.jurisdiction?.toLowerCase().includes(query)
      );
    }

    // Apply filters
    if (filters.jurisdiction) {
      result = result.filter(cam => cam.jurisdiction === filters.jurisdiction);
    }
    if (filters.camera_type) {
      result = result.filter(cam => 
        (cam.camera_type || cam.type) === filters.camera_type
      );
    }
    if (filters.sector) {
      result = result.filter(cam => cam.sector === filters.sector);
    }
    if (filters.status) {
      result = result.filter(cam => cam.status === filters.status);
    }

    setFilteredCameras(result);
  }, [cameras, searchQuery, filters]);

  // Get unique values for filters
  const jurisdictions = [...new Set(cameras.map(c => c.jurisdiction).filter(Boolean))];
  const cameraTypes = [...new Set(cameras.map(c => c.camera_type || c.type).filter(Boolean))];
  const sectors = [...new Set(cameras.map(c => c.sector).filter(Boolean))];

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'online': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'ptz': return 'bg-amber-600';
      case 'lpr': return 'bg-red-600';
      case 'cctv': return 'bg-blue-600';
      case 'traffic': return 'bg-green-600';
      default: return 'bg-gray-600';
    }
  };

  const getTypeLabel = (camera: CameraData) => {
    const type = camera.camera_type || camera.type || 'cctv';
    if (camera.jurisdiction === 'FDOT') {
      return 'Traffic (FDOT)';
    }
    return type.toUpperCase();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading cameras...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Camera className="h-8 w-8 text-blue-400" />
          <h1 className="text-2xl font-bold">Camera Directory</h1>
          <span className="px-2 py-1 bg-blue-900/50 text-blue-300 text-sm rounded">
            {filteredCameras.length} cameras
          </span>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/cameras/map"
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
          >
            <MapPin className="h-4 w-4" />
            Map View
          </Link>
          <Link
            href="/cameras/video-wall"
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
          >
            <Grid className="h-4 w-4" />
            Video Wall
          </Link>
          <Link
            href="/admin/cameras/manual-add"
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded-lg"
          >
            <Plus className="h-4 w-4" />
            Add Camera
          </Link>
          <button
            onClick={fetchCameras}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-amber-900/30 border border-amber-500/50 text-amber-200 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search cameras..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Filters */}
          <select
            value={filters.jurisdiction}
            onChange={(e) => setFilters({ ...filters, jurisdiction: e.target.value })}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="">All Jurisdictions</option>
            {jurisdictions.map(j => (
              <option key={j} value={j}>{j}</option>
            ))}
          </select>

          <select
            value={filters.camera_type}
            onChange={(e) => setFilters({ ...filters, camera_type: e.target.value })}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="">All Types</option>
            {cameraTypes.map(t => (
              <option key={t} value={t}>{t?.toUpperCase()}</option>
            ))}
          </select>

          <select
            value={filters.sector}
            onChange={(e) => setFilters({ ...filters, sector: e.target.value })}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="">All Sectors</option>
            {sectors.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          {/* View Toggle */}
          <div className="flex bg-gray-700 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-l-lg ${viewMode === 'grid' ? 'bg-blue-600' : ''}`}
            >
              <Grid className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-r-lg ${viewMode === 'list' ? 'bg-blue-600' : ''}`}
            >
              <List className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Camera Grid/List */}
      {filteredCameras.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <Camera className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No cameras found</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredCameras.map((camera) => (
            <Link
              key={camera.id}
              href={`/cameras/detail?id=${camera.id}`}
              className="bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all"
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-black">
                <img
                  src={camera.supports_mjpeg 
                    ? `${apiBaseUrl}${camera.stream_url}`
                    : camera.jurisdiction === 'FDOT' 
                      ? `${apiBaseUrl}/api/cameras/fdot/${camera.fdot_id || camera.id}/snapshot?ts=${Date.now()}`
                      : (camera.snapshot_url || camera.stream_url || 'https://via.placeholder.com/640x360?text=Camera')}
                  alt={camera.name}
                  className="w-full h-full object-cover"
                />
                {/* Status Badge */}
                <div className="absolute top-2 left-2 flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${getStatusColor(camera.status)}`} />
                  <span className="text-xs text-white bg-black/50 px-1 rounded">
                    {camera.status}
                  </span>
                </div>
                {/* Type Badge */}
                <div className="absolute top-2 right-2">
                  <span className={`text-xs text-white px-2 py-0.5 rounded ${getTypeColor(camera.camera_type || camera.type || '')}`}>
                    {getTypeLabel(camera)}
                  </span>
                </div>
              </div>

              {/* Info */}
              <div className="p-3">
                <h3 className="font-medium text-white truncate">{camera.name}</h3>
                <div className="flex items-center justify-between mt-1 text-xs text-gray-400">
                  <span>{camera.jurisdiction}</span>
                  <span>{camera.sector}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredCameras.map((camera) => (
            <Link
              key={camera.id}
              href={`/cameras/detail?id=${camera.id}`}
              className="flex items-center gap-4 bg-gray-800 rounded-lg p-3 hover:bg-gray-700/50"
            >
              {/* Thumbnail */}
              <div className="w-32 h-20 bg-black rounded overflow-hidden flex-shrink-0">
                <img
                  src={camera.supports_mjpeg 
                    ? `${apiBaseUrl}${camera.stream_url}`
                    : camera.jurisdiction === 'FDOT' 
                      ? `${apiBaseUrl}/api/cameras/fdot/${camera.fdot_id || camera.id}/snapshot?ts=${Date.now()}`
                      : (camera.snapshot_url || camera.stream_url || 'https://via.placeholder.com/640x360?text=Camera')}
                  alt={camera.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-white truncate">{camera.name}</h3>
                <p className="text-sm text-gray-400">{camera.description}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                  <span>{camera.jurisdiction}</span>
                  <span>{camera.sector}</span>
                  <span>
                    {camera.latitude?.toFixed(4)}, {camera.longitude?.toFixed(4)}
                  </span>
                </div>
              </div>

              {/* Status & Type */}
              <div className="flex items-center gap-2">
                <span className={`text-xs text-white px-2 py-0.5 rounded ${getTypeColor(camera.camera_type || camera.type || '')}`}>
                  {getTypeLabel(camera)}
                </span>
                <span className={`w-3 h-3 rounded-full ${getStatusColor(camera.status)}`} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
