'use client';

import React, { useState, useEffect } from 'react';
import { 
  Camera, Plane, Bot, MapPin, Grid3X3, FileText, Building2, School, 
  Home, AlertTriangle, Link2, Calendar, Droplets, Users, Settings,
  Plus, Edit, Trash2, Search, Filter, RefreshCw, Download, Upload,
  ChevronLeft, ChevronRight, Eye, Check, X, Shield
} from 'lucide-react';

interface TabConfig {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  fields: FieldConfig[];
  apiEndpoint: string;
}

interface FieldConfig {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'textarea' | 'gps' | 'polygon' | 'file' | 'toggle' | 'datetime' | 'multiselect' | 'password' | 'encrypted';
  required?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
  min?: number;
  max?: number;
  sensitive?: boolean;
}

const ADMIN_TABS: TabConfig[] = [
  {
    id: 'cameras',
    label: 'Cameras',
    icon: <Camera className="w-4 h-4" />,
    description: 'Manage surveillance cameras',
    apiEndpoint: '/api/admin/cameras',
    fields: [
      { name: 'name', label: 'Camera Name', type: 'text', required: true, placeholder: 'Enter camera name' },
      { name: 'lat', label: 'Latitude', type: 'number', required: true, placeholder: '26.7753' },
      { name: 'lng', label: 'Longitude', type: 'number', required: true, placeholder: '-80.0569' },
      { name: 'address', label: 'Address', type: 'text', placeholder: 'Street address' },
      { name: 'camera_type', label: 'Type', type: 'select', required: true, options: [
        { value: 'traffic', label: 'Traffic' },
        { value: 'cctv', label: 'CCTV' },
        { value: 'lpr', label: 'LPR' },
        { value: 'ptz', label: 'PTZ' },
        { value: 'marine', label: 'Marine' },
        { value: 'tactical', label: 'Tactical' },
        { value: 'fdot', label: 'FDOT' },
        { value: 'rbpd', label: 'RBPD' },
      ]},
      { name: 'jurisdiction', label: 'Jurisdiction', type: 'text', placeholder: 'RBPD' },
      { name: 'sector', label: 'Sector', type: 'text', placeholder: 'SECTOR-1' },
      { name: 'stream_url', label: 'Stream URL', type: 'text', placeholder: 'rtsp://...' },
      { name: 'fallback_url', label: 'Fallback URL', type: 'text', placeholder: 'http://...' },
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'online', label: 'Online' },
        { value: 'offline', label: 'Offline' },
        { value: 'maintenance', label: 'Maintenance' },
        { value: 'unknown', label: 'Unknown' },
      ]},
      { name: 'notes', label: 'Notes', type: 'textarea', placeholder: 'Additional notes...' },
    ],
  },
  {
    id: 'drones',
    label: 'Drones',
    icon: <Plane className="w-4 h-4" />,
    description: 'Manage drone fleet',
    apiEndpoint: '/api/admin/drones',
    fields: [
      { name: 'drone_id', label: 'Drone ID', type: 'text', required: true },
      { name: 'model', label: 'Model', type: 'text', required: true },
      { name: 'serial_number', label: 'Serial Number', type: 'text', required: true },
      { name: 'assigned_officer', label: 'Assigned Officer', type: 'text' },
      { name: 'max_flight_time', label: 'Max Flight Time (min)', type: 'number', min: 1, max: 120 },
      { name: 'battery_count', label: 'Battery Count', type: 'number', min: 1 },
      { name: 'home_lat', label: 'Home Latitude', type: 'number' },
      { name: 'home_lng', label: 'Home Longitude', type: 'number' },
      { name: 'stream_url', label: 'Stream URL', type: 'text' },
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'active', label: 'Active' },
        { value: 'standby', label: 'Standby' },
        { value: 'maintenance', label: 'Maintenance' },
        { value: 'deployed', label: 'Deployed' },
        { value: 'offline', label: 'Offline' },
      ]},
    ],
  },
  {
    id: 'robots',
    label: 'Robots',
    icon: <Bot className="w-4 h-4" />,
    description: 'Manage quadruped robots',
    apiEndpoint: '/api/admin/robots',
    fields: [
      { name: 'robot_id', label: 'Robot ID', type: 'text', required: true },
      { name: 'model', label: 'Model', type: 'text', required: true },
      { name: 'serial_number', label: 'Serial Number', type: 'text', required: true },
      { name: 'assigned_unit', label: 'Assigned Unit', type: 'text' },
      { name: 'patrol_area', label: 'Patrol Area', type: 'polygon' },
      { name: 'stream_url', label: 'Stream URL', type: 'text' },
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'active', label: 'Active' },
        { value: 'standby', label: 'Standby' },
        { value: 'maintenance', label: 'Maintenance' },
        { value: 'deployed', label: 'Deployed' },
        { value: 'offline', label: 'Offline' },
        { value: 'charging', label: 'Charging' },
      ]},
    ],
  },
  {
    id: 'lpr-zones',
    label: 'LPR Zones',
    icon: <MapPin className="w-4 h-4" />,
    description: 'Manage LPR detection zones',
    apiEndpoint: '/api/admin/lpr-zones',
    fields: [
      { name: 'zone_name', label: 'Zone Name', type: 'text', required: true },
      { name: 'boundary', label: 'Boundary Polygon', type: 'polygon', required: true },
      { name: 'camera_ids', label: 'Associated Cameras', type: 'multiselect' },
      { name: 'bolo_rules', label: 'BOLO Rules', type: 'textarea' },
      { name: 'alert_sensitivity', label: 'Alert Sensitivity', type: 'select', options: [
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' },
      ]},
    ],
  },
  {
    id: 'sectors',
    label: 'Sectors',
    icon: <Grid3X3 className="w-4 h-4" />,
    description: 'Manage patrol sectors/beats',
    apiEndpoint: '/api/admin/sectors',
    fields: [
      { name: 'sector_id', label: 'Sector ID', type: 'text', required: true },
      { name: 'name', label: 'Sector Name', type: 'text', required: true },
      { name: 'polygon', label: 'Boundary Polygon', type: 'polygon', required: true },
      { name: 'assigned_officers', label: 'Assigned Officers', type: 'multiselect' },
    ],
  },
  {
    id: 'fire-preplans',
    label: 'Fire Preplans',
    icon: <FileText className="w-4 h-4" />,
    description: 'Manage fire preplans',
    apiEndpoint: '/api/admin/fire-preplans',
    fields: [
      { name: 'building_name', label: 'Building Name', type: 'text', required: true },
      { name: 'address', label: 'Address', type: 'text', required: true },
      { name: 'pdf_url', label: 'PDF Upload', type: 'file' },
      { name: 'hazmat_notes', label: 'Hazmat Notes', type: 'textarea' },
      { name: 'knox_box_location', label: 'Knox Box Location', type: 'text' },
      { name: 'riser_location', label: 'Riser Location', type: 'text' },
      { name: 'lat', label: 'Latitude', type: 'number' },
      { name: 'lng', label: 'Longitude', type: 'number' },
    ],
  },
  {
    id: 'infrastructure',
    label: 'Infrastructure',
    icon: <Building2 className="w-4 h-4" />,
    description: 'Manage critical infrastructure',
    apiEndpoint: '/api/admin/infrastructure',
    fields: [
      { name: 'name', label: 'Name', type: 'text', required: true },
      { name: 'infra_type', label: 'Type', type: 'select', required: true, options: [
        { value: 'water', label: 'Water' },
        { value: 'power', label: 'Power' },
        { value: 'gas', label: 'Gas' },
        { value: 'comms', label: 'Communications' },
        { value: 'sewer', label: 'Sewer' },
        { value: 'lift_station', label: 'Lift Station' },
        { value: 'substation', label: 'Substation' },
        { value: 'pipeline', label: 'Pipeline' },
      ]},
      { name: 'lat', label: 'Latitude', type: 'number', required: true },
      { name: 'lng', label: 'Longitude', type: 'number', required: true },
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'operational', label: 'Operational' },
        { value: 'degraded', label: 'Degraded' },
        { value: 'offline', label: 'Offline' },
        { value: 'maintenance', label: 'Maintenance' },
      ]},
      { name: 'notes', label: 'Notes', type: 'textarea' },
    ],
  },
  {
    id: 'schools',
    label: 'Schools',
    icon: <School className="w-4 h-4" />,
    description: 'Manage school information',
    apiEndpoint: '/api/admin/schools',
    fields: [
      { name: 'school_name', label: 'School Name', type: 'text', required: true },
      { name: 'address', label: 'Address', type: 'text', required: true },
      { name: 'grade_level', label: 'Grade Level', type: 'select', options: [
        { value: 'elementary', label: 'Elementary' },
        { value: 'middle', label: 'Middle' },
        { value: 'high', label: 'High School' },
        { value: 'k12', label: 'K-12' },
        { value: 'charter', label: 'Charter' },
        { value: 'private', label: 'Private' },
      ]},
      { name: 'perimeter', label: 'Perimeter Polygon', type: 'polygon' },
      { name: 'pickup_routes', label: 'Pickup Routes', type: 'textarea' },
      { name: 'access_points', label: 'Access Points', type: 'textarea' },
      { name: 'sro_name', label: 'SRO Name', type: 'text' },
      { name: 'sro_contact', label: 'SRO Contact', type: 'text' },
    ],
  },
  {
    id: 'dv-risk-homes',
    label: 'DV Risk Homes',
    icon: <Home className="w-4 h-4" />,
    description: 'Manage DV risk locations (REDACTED)',
    apiEndpoint: '/api/admin/dv-risk-homes',
    fields: [
      { name: 'sector', label: 'Sector (NO ADDRESS)', type: 'text', required: true, placeholder: 'SECTOR-1 only' },
      { name: 'risk_level', label: 'Risk Level', type: 'select', required: true, options: [
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' },
      ]},
      { name: 'notes', label: 'Notes (Encrypted)', type: 'encrypted', sensitive: true },
      { name: 'case_number', label: 'Case Number', type: 'text' },
      { name: 'officer_alert', label: 'Officer Alert', type: 'toggle' },
    ],
  },
  {
    id: 'incidents',
    label: 'Incidents',
    icon: <AlertTriangle className="w-4 h-4" />,
    description: 'Manage incident feed',
    apiEndpoint: '/api/admin/incidents',
    fields: [
      { name: 'incident_type', label: 'Type', type: 'select', required: true, options: [
        { value: 'crime', label: 'Crime' },
        { value: 'traffic', label: 'Traffic' },
        { value: 'medical', label: 'Medical' },
        { value: 'fire', label: 'Fire' },
        { value: 'hazmat', label: 'Hazmat' },
        { value: 'suspicious', label: 'Suspicious' },
        { value: 'domestic', label: 'Domestic' },
        { value: 'shots_fired', label: 'Shots Fired' },
      ]},
      { name: 'priority', label: 'Priority', type: 'select', options: [
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' },
      ]},
      { name: 'location', label: 'Location', type: 'text', required: true },
      { name: 'lat', label: 'Latitude', type: 'number' },
      { name: 'lng', label: 'Longitude', type: 'number' },
      { name: 'description', label: 'Description', type: 'textarea', required: true },
      { name: 'officer', label: 'Assigned Officer', type: 'text' },
      { name: 'unit', label: 'Unit', type: 'text' },
      { name: 'sector', label: 'Sector', type: 'text' },
    ],
  },
  {
    id: 'api-connections',
    label: 'API Connections',
    icon: <Link2 className="w-4 h-4" />,
    description: 'Manage external API connections',
    apiEndpoint: '/api/admin/api-connections',
    fields: [
      { name: 'api_name', label: 'API Name', type: 'text', required: true },
      { name: 'url', label: 'URL', type: 'text', required: true },
      { name: 'api_key', label: 'API Key (Encrypted)', type: 'encrypted', sensitive: true },
      { name: 'refresh_frequency', label: 'Refresh Frequency', type: 'select', options: [
        { value: 'realtime', label: 'Real-time' },
        { value: '1min', label: '1 Minute' },
        { value: '5min', label: '5 Minutes' },
        { value: '15min', label: '15 Minutes' },
        { value: 'hourly', label: 'Hourly' },
        { value: 'daily', label: 'Daily' },
      ]},
      { name: 'auth_type', label: 'Auth Type', type: 'select', options: [
        { value: 'bearer', label: 'Bearer Token' },
        { value: 'basic', label: 'Basic Auth' },
        { value: 'api_key', label: 'API Key' },
      ]},
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'error', label: 'Error' },
        { value: 'testing', label: 'Testing' },
      ]},
    ],
  },
  {
    id: 'events',
    label: 'Events',
    icon: <Calendar className="w-4 h-4" />,
    description: 'Manage special events',
    apiEndpoint: '/api/admin/events',
    fields: [
      { name: 'event_name', label: 'Event Name', type: 'text', required: true },
      { name: 'event_type', label: 'Type', type: 'select', options: [
        { value: 'parade', label: 'Parade' },
        { value: 'concert', label: 'Concert' },
        { value: 'festival', label: 'Festival' },
        { value: 'sports', label: 'Sports' },
        { value: 'protest', label: 'Protest' },
        { value: 'vip', label: 'VIP' },
        { value: 'construction', label: 'Construction' },
        { value: 'emergency', label: 'Emergency' },
      ]},
      { name: 'boundary', label: 'Boundary Polygon', type: 'polygon', required: true },
      { name: 'start_time', label: 'Start Time', type: 'datetime', required: true },
      { name: 'end_time', label: 'End Time', type: 'datetime', required: true },
      { name: 'expected_attendance', label: 'Expected Attendance', type: 'number' },
      { name: 'organizer', label: 'Organizer', type: 'text' },
      { name: 'road_closures', label: 'Road Closures', type: 'textarea' },
      { name: 'notes', label: 'Notes', type: 'textarea' },
    ],
  },
  {
    id: 'hydrants',
    label: 'Hydrants',
    icon: <Droplets className="w-4 h-4" />,
    description: 'Manage fire hydrants',
    apiEndpoint: '/api/admin/hydrants',
    fields: [
      { name: 'hydrant_id', label: 'Hydrant ID', type: 'text', required: true },
      { name: 'lat', label: 'Latitude', type: 'number', required: true },
      { name: 'lng', label: 'Longitude', type: 'number', required: true },
      { name: 'psi', label: 'PSI', type: 'number', min: 0, max: 300 },
      { name: 'flow_rate', label: 'Flow Rate (GPM)', type: 'number' },
      { name: 'hydrant_type', label: 'Type', type: 'select', options: [
        { value: 'standard', label: 'Standard' },
        { value: 'high_flow', label: 'High Flow' },
        { value: 'dry_barrel', label: 'Dry Barrel' },
        { value: 'wet_barrel', label: 'Wet Barrel' },
      ]},
      { name: 'status', label: 'Status', type: 'select', options: [
        { value: 'operational', label: 'Operational' },
        { value: 'out_of_service', label: 'Out of Service' },
        { value: 'maintenance', label: 'Maintenance' },
      ]},
      { name: 'address', label: 'Address', type: 'text' },
      { name: 'sector', label: 'Sector', type: 'text' },
    ],
  },
  {
    id: 'users',
    label: 'Users',
    icon: <Users className="w-4 h-4" />,
    description: 'Manage system users',
    apiEndpoint: '/api/admin/users',
    fields: [
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'email', label: 'Email', type: 'text' },
      { name: 'password', label: 'Password', type: 'password', sensitive: true },
      { name: 'role', label: 'Role', type: 'select', required: true, options: [
        { value: 'viewer', label: 'Viewer' },
        { value: 'analyst', label: 'Analyst' },
        { value: 'supervisor', label: 'Supervisor' },
        { value: 'admin', label: 'Admin' },
        { value: 'commander', label: 'Commander' },
        { value: 'system-integrator', label: 'System Integrator' },
      ]},
      { name: 'assigned_sector', label: 'Assigned Sector', type: 'text' },
      { name: 'mfa_enabled', label: 'MFA Enabled', type: 'toggle' },
      { name: 'full_name', label: 'Full Name', type: 'text' },
      { name: 'badge_number', label: 'Badge Number', type: 'text' },
      { name: 'department', label: 'Department', type: 'text' },
    ],
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings className="w-4 h-4" />,
    description: 'System settings',
    apiEndpoint: '/api/admin/settings',
    fields: [
      { name: 'setting_key', label: 'Setting Key', type: 'text', required: true },
      { name: 'setting_value', label: 'Setting Value', type: 'text', required: true },
      { name: 'category', label: 'Category', type: 'select', options: [
        { value: 'map', label: 'Map' },
        { value: 'alerts', label: 'Alerts' },
        { value: 'refresh', label: 'Refresh Rates' },
        { value: 'videowall', label: 'Video Wall' },
        { value: 'security', label: 'Security' },
        { value: 'system', label: 'System' },
      ]},
      { name: 'description', label: 'Description', type: 'textarea' },
      { name: 'is_sensitive', label: 'Sensitive', type: 'toggle' },
      { name: 'requires_restart', label: 'Requires Restart', type: 'toggle' },
    ],
  },
];

export default function AdminDataEntryPage() {
  const [activeTab, setActiveTab] = useState('cameras');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const currentTab = ADMIN_TABS.find(t => t.id === activeTab) || ADMIN_TABS[0];

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}${currentTab.apiEndpoint}`);
      if (response.ok) {
        const result = await response.json();
        setData(Array.isArray(result) ? result : []);
      } else {
        setData(getDemoData(activeTab));
      }
    } catch (error) {
      console.error('Error loading data:', error);
      setData(getDemoData(activeTab));
    }
    setLoading(false);
  };

  const getDemoData = (tabId: string): any[] => {
    const demoDataMap: Record<string, any[]> = {
      cameras: [
        { id: '1', name: 'FDOT I-95 Mile 71', lat: 26.7755, lng: -80.0565, camera_type: 'fdot', status: 'online', sector: 'SECTOR-1' },
        { id: '2', name: 'RBPD City Hall', lat: 26.7765, lng: -80.0558, camera_type: 'rbpd', status: 'online', sector: 'SECTOR-1' },
        { id: '3', name: 'Marina LPR Entry', lat: 26.7801, lng: -80.0512, camera_type: 'lpr', status: 'online', sector: 'SECTOR-2' },
      ],
      drones: [
        { id: '1', drone_id: 'DRONE-001', model: 'DJI Matrice 300 RTK', status: 'active', assigned_officer: 'Officer Johnson' },
        { id: '2', drone_id: 'DRONE-002', model: 'DJI Mavic 3 Enterprise', status: 'standby', assigned_officer: 'Officer Smith' },
      ],
      robots: [
        { id: '1', robot_id: 'SPOT-001', model: 'Boston Dynamics Spot', status: 'active', assigned_unit: 'K9 Unit' },
      ],
      incidents: [
        { id: '1', incident_type: 'shots_fired', priority: 'critical', location: '1200 Main St', status: 'dispatched' },
        { id: '2', incident_type: 'traffic', priority: 'medium', location: 'Blue Heron & Congress', status: 'on_scene' },
      ],
      users: [
        { id: '1', username: 'admin', role: 'admin', full_name: 'System Administrator', status: 'active' },
        { id: '2', username: 'commander', role: 'commander', full_name: 'Chief Williams', status: 'active' },
      ],
    };
    return demoDataMap[tabId] || [];
  };

  const handleCreate = () => {
    setEditingItem(null);
    setFormData({});
    setShowForm(true);
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    setFormData({ ...item });
    setShowForm(true);
  };

  const handleDelete = async (item: any) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}${currentTab.apiEndpoint}/${item.id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        loadData();
      }
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const url = editingItem 
        ? `${backendUrl}${currentTab.apiEndpoint}/${editingItem.id}`
        : `${backendUrl}${currentTab.apiEndpoint}`;
      
      const response = await fetch(url, {
        method: editingItem ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setShowForm(false);
        loadData();
      }
    } catch (error) {
      console.error('Error saving item:', error);
    }
  };

  const filteredData = data.filter(item => {
    if (!searchQuery) return true;
    return Object.values(item).some(val => 
      String(val).toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const paginatedData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const renderField = (field: FieldConfig) => {
    const value = formData[field.name] || '';
    
    switch (field.type) {
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none"
            required={field.required}
          >
            <option value="">Select...</option>
            {field.options?.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        );
      
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none min-h-[80px]"
            placeholder={field.placeholder}
            required={field.required}
          />
        );
      
      case 'toggle':
        return (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={!!value}
              onChange={(e) => setFormData({ ...formData, [field.name]: e.target.checked })}
              className="w-5 h-5 rounded bg-[#0a0f24] border-[#1a2744] text-[#0050ff] focus:ring-[#0050ff]"
            />
            <span className="text-gray-400">Enabled</span>
          </label>
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => setFormData({ ...formData, [field.name]: parseFloat(e.target.value) || '' })}
            className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none"
            placeholder={field.placeholder}
            min={field.min}
            max={field.max}
            required={field.required}
          />
        );
      
      case 'datetime':
        return (
          <input
            type="datetime-local"
            value={value}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none"
            required={field.required}
          />
        );
      
      case 'password':
      case 'encrypted':
        return (
          <div className="relative">
            <input
              type="password"
              value={value}
              onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none pr-10"
              placeholder={field.placeholder || '********'}
              required={field.required && !editingItem}
            />
            <Shield className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-yellow-500" />
          </div>
        );
      
      case 'polygon':
        return (
          <div className="space-y-2">
            <textarea
              value={typeof value === 'string' ? value : JSON.stringify(value || [], null, 2)}
              onChange={(e) => {
                try {
                  setFormData({ ...formData, [field.name]: JSON.parse(e.target.value) });
                } catch {
                  setFormData({ ...formData, [field.name]: e.target.value });
                }
              }}
              className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none min-h-[80px] font-mono text-sm"
              placeholder='[{"lat": 26.77, "lng": -80.05}, ...]'
              required={field.required}
            />
            <p className="text-xs text-gray-500">Enter polygon points as JSON array</p>
          </div>
        );
      
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            className="w-full px-3 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none"
            placeholder={field.placeholder}
            required={field.required}
          />
        );
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      online: 'bg-green-500/20 text-green-400 border-green-500/30',
      active: 'bg-green-500/20 text-green-400 border-green-500/30',
      operational: 'bg-green-500/20 text-green-400 border-green-500/30',
      offline: 'bg-red-500/20 text-red-400 border-red-500/30',
      error: 'bg-red-500/20 text-red-400 border-red-500/30',
      maintenance: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      standby: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      deployed: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      critical: 'bg-red-500/20 text-red-400 border-red-500/30',
      high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      low: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs border ${statusColors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-[#050a18] text-white">
      {/* Header */}
      <div className="bg-[#0a0f24] border-b border-[#1a2744] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">RTCC Admin Data Entry</h1>
            <p className="text-gray-400 text-sm mt-1">Comprehensive admin configuration suite</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2 bg-[#1a2744] hover:bg-[#243352] rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={handleCreate}
              className="flex items-center gap-2 px-4 py-2 bg-[#0050ff] hover:bg-[#0040cc] rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add New
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar Tabs */}
        <div className="w-64 bg-[#0a0f24] border-r border-[#1a2744] min-h-[calc(100vh-73px)]">
          <div className="p-4">
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search tabs..."
                className="w-full pl-10 pr-4 py-2 bg-[#050a18] border border-[#1a2744] rounded-lg text-white text-sm focus:border-[#0050ff] focus:outline-none"
              />
            </div>
            
            <div className="space-y-1">
              {ADMIN_TABS.map((tab, index) => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setCurrentPage(1);
                    setSearchQuery('');
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-[#0050ff] text-white'
                      : 'text-gray-400 hover:bg-[#1a2744] hover:text-white'
                  }`}
                >
                  <span className="flex items-center justify-center w-6 h-6 rounded bg-[#1a2744] text-xs">
                    {index + 1}
                  </span>
                  {tab.icon}
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Tab Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              {currentTab.icon}
              <h2 className="text-xl font-semibold">{currentTab.label}</h2>
            </div>
            <p className="text-gray-400 text-sm">{currentTab.description}</p>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center gap-4 mb-6">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search records..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 bg-[#0a0f24] border border-[#1a2744] rounded-lg text-white focus:border-[#0050ff] focus:outline-none"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1a2744] hover:bg-[#243352] rounded-lg transition-colors">
              <Filter className="w-4 h-4" />
              Filters
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1a2744] hover:bg-[#243352] rounded-lg transition-colors">
              <Download className="w-4 h-4" />
              Export
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1a2744] hover:bg-[#243352] rounded-lg transition-colors">
              <Upload className="w-4 h-4" />
              Import
            </button>
          </div>

          {/* Data Table */}
          <div className="bg-[#0a0f24] border border-[#1a2744] rounded-xl overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 text-[#0050ff] animate-spin" />
              </div>
            ) : paginatedData.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <AlertTriangle className="w-12 h-12 mb-4 opacity-50" />
                <p>No records found</p>
                <button
                  onClick={handleCreate}
                  className="mt-4 flex items-center gap-2 px-4 py-2 bg-[#0050ff] hover:bg-[#0040cc] rounded-lg transition-colors text-white"
                >
                  <Plus className="w-4 h-4" />
                  Create First Record
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-[#1a2744]">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">ID</th>
                      {currentTab.fields.slice(0, 4).map(field => (
                        <th key={field.name} className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          {field.label}
                        </th>
                      ))}
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1a2744]">
                    {paginatedData.map((item, index) => (
                      <tr key={item.id || index} className="hover:bg-[#1a2744]/50 transition-colors">
                        <td className="px-4 py-3 text-sm text-gray-300 font-mono">
                          {item.id?.slice(0, 8) || index + 1}
                        </td>
                        {currentTab.fields.slice(0, 4).map(field => (
                          <td key={field.name} className="px-4 py-3 text-sm text-white">
                            {field.sensitive ? '********' : String(item[field.name] || '-')}
                          </td>
                        ))}
                        <td className="px-4 py-3">
                          {getStatusBadge(item.status || item.risk_level || 'unknown')}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(item)}
                              className="p-2 text-gray-400 hover:text-white hover:bg-[#1a2744] rounded-lg transition-colors"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(item)}
                              className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-[#1a2744]">
                <p className="text-sm text-gray-400">
                  Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredData.length)} of {filteredData.length} records
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-2 text-gray-400 hover:text-white hover:bg-[#1a2744] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-sm text-gray-400">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-2 text-gray-400 hover:text-white hover:bg-[#1a2744] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0a0f24] border border-[#1a2744] rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#1a2744]">
              <h3 className="text-lg font-semibold">
                {editingItem ? 'Edit' : 'Create'} {currentTab.label.slice(0, -1)}
              </h3>
              <button
                onClick={() => setShowForm(false)}
                className="p-2 text-gray-400 hover:text-white hover:bg-[#1a2744] rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="grid grid-cols-2 gap-4">
                {currentTab.fields.map(field => (
                  <div key={field.name} className={field.type === 'textarea' || field.type === 'polygon' ? 'col-span-2' : ''}>
                    <label className="block text-sm font-medium text-gray-400 mb-1">
                      {field.label}
                      {field.required && <span className="text-red-400 ml-1">*</span>}
                      {field.sensitive && <Shield className="inline w-3 h-3 ml-1 text-yellow-500" />}
                    </label>
                    {renderField(field)}
                  </div>
                ))}
              </div>
              
              <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-[#1a2744]">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-gray-400 hover:text-white hover:bg-[#1a2744] rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-2 px-4 py-2 bg-[#0050ff] hover:bg-[#0040cc] rounded-lg transition-colors"
                >
                  <Check className="w-4 h-4" />
                  {editingItem ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
