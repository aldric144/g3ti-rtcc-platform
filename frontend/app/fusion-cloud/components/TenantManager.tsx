'use client';

import { useState, useEffect } from 'react';

interface Tenant {
  tenant_id: string;
  name: string;
  tenant_type: string;
  status: string;
  profile?: {
    display_name: string;
    city: string;
    state: string;
    ori_number: string;
  };
  data_sources: any[];
  integrations: any[];
  federation_partners: string[];
}

interface TenantMetrics {
  total_tenants: number;
  active_tenants: number;
  tenants_by_type: Record<string, number>;
  tenants_by_status: Record<string, number>;
}

export default function TenantManager() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [metrics, setMetrics] = useState<TenantMetrics | null>(null);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadTenants();
    loadMetrics();
  }, []);

  const loadTenants = async () => {
    setTenants([
      {
        tenant_id: 'tenant-001',
        name: 'Metro City Police Department',
        tenant_type: 'police_department',
        status: 'active',
        profile: {
          display_name: 'Metro City PD',
          city: 'Metro City',
          state: 'CA',
          ori_number: 'CA0123456',
        },
        data_sources: [
          { source_id: 'ds-001', name: 'CAD System', source_type: 'cad', enabled: true },
          { source_id: 'ds-002', name: 'LPR Network', source_type: 'lpr', enabled: true },
        ],
        integrations: [
          { integration_id: 'int-001', name: 'NCIC', status: 'connected' },
        ],
        federation_partners: ['tenant-002', 'tenant-003'],
      },
      {
        tenant_id: 'tenant-002',
        name: 'County Sheriff Office',
        tenant_type: 'sheriff_office',
        status: 'active',
        profile: {
          display_name: 'County SO',
          city: 'County Seat',
          state: 'CA',
          ori_number: 'CA0234567',
        },
        data_sources: [
          { source_id: 'ds-003', name: 'RMS', source_type: 'rms', enabled: true },
        ],
        integrations: [],
        federation_partners: ['tenant-001'],
      },
      {
        tenant_id: 'tenant-003',
        name: 'Regional Task Force',
        tenant_type: 'task_force',
        status: 'active',
        profile: {
          display_name: 'Regional TF',
          city: 'Regional',
          state: 'CA',
          ori_number: 'CA0345678',
        },
        data_sources: [],
        integrations: [],
        federation_partners: ['tenant-001', 'tenant-002'],
      },
    ]);
  };

  const loadMetrics = async () => {
    setMetrics({
      total_tenants: 12,
      active_tenants: 10,
      tenants_by_type: {
        police_department: 5,
        sheriff_office: 3,
        task_force: 2,
        fusion_center: 1,
        transit_authority: 1,
      },
      tenants_by_status: {
        active: 10,
        pending: 1,
        suspended: 1,
      },
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'pending': return 'bg-yellow-500';
      case 'suspended': return 'bg-red-500';
      case 'inactive': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getTenantTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      police_department: 'Police Department',
      sheriff_office: 'Sheriff Office',
      task_force: 'Task Force',
      fusion_center: 'Fusion Center',
      transit_authority: 'Transit Authority',
      city: 'City',
      county: 'County',
      state: 'State',
      federal: 'Federal',
    };
    return labels[type] || type;
  };

  const filteredTenants = filter === 'all' 
    ? tenants 
    : tenants.filter(t => t.tenant_type === filter);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-blue-400">{metrics?.total_tenants || 0}</div>
          <div className="text-gray-400 text-sm">Total Tenants</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-green-400">{metrics?.active_tenants || 0}</div>
          <div className="text-gray-400 text-sm">Active Tenants</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-purple-400">
            {Object.keys(metrics?.tenants_by_type || {}).length}
          </div>
          <div className="text-gray-400 text-sm">Tenant Types</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-orange-400">
            {tenants.reduce((acc, t) => acc + t.federation_partners.length, 0)}
          </div>
          <div className="text-gray-400 text-sm">Federation Links</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
          >
            <option value="all">All Types</option>
            <option value="police_department">Police Departments</option>
            <option value="sheriff_office">Sheriff Offices</option>
            <option value="task_force">Task Forces</option>
            <option value="fusion_center">Fusion Centers</option>
          </select>
          <input
            type="text"
            placeholder="Search tenants..."
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm w-64"
          />
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium"
        >
          + Register Tenant
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredTenants.map((tenant) => (
          <div
            key={tenant.tenant_id}
            onClick={() => setSelectedTenant(tenant)}
            className={`bg-gray-800 rounded-lg p-4 border cursor-pointer transition-colors ${
              selectedTenant?.tenant_id === tenant.tenant_id
                ? 'border-blue-500'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-lg">{tenant.name}</h3>
                <p className="text-gray-400 text-sm">{getTenantTypeLabel(tenant.tenant_type)}</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${getStatusColor(tenant.status)}`}></span>
                <span className="text-sm capitalize">{tenant.status}</span>
              </div>
            </div>

            {tenant.profile && (
              <div className="mt-3 text-sm text-gray-400">
                <p>{tenant.profile.city}, {tenant.profile.state}</p>
                <p>ORI: {tenant.profile.ori_number}</p>
              </div>
            )}

            <div className="mt-4 flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <span className="text-gray-500">Data Sources:</span>
                <span className="text-blue-400">{tenant.data_sources.length}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-500">Integrations:</span>
                <span className="text-green-400">{tenant.integrations.length}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-gray-500">Partners:</span>
                <span className="text-purple-400">{tenant.federation_partners.length}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedTenant && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">{selectedTenant.name} - Details</h3>
            <button
              onClick={() => setSelectedTenant(null)}
              className="text-gray-400 hover:text-white"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Data Sources</h4>
              {selectedTenant.data_sources.length > 0 ? (
                <ul className="space-y-2">
                  {selectedTenant.data_sources.map((ds) => (
                    <li key={ds.source_id} className="flex items-center justify-between bg-gray-700/50 rounded px-3 py-2">
                      <span>{ds.name}</span>
                      <span className={`text-xs px-2 py-1 rounded ${ds.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                        {ds.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No data sources configured</p>
              )}
            </div>

            <div>
              <h4 className="font-medium text-gray-300 mb-2">Integrations</h4>
              {selectedTenant.integrations.length > 0 ? (
                <ul className="space-y-2">
                  {selectedTenant.integrations.map((int) => (
                    <li key={int.integration_id} className="flex items-center justify-between bg-gray-700/50 rounded px-3 py-2">
                      <span>{int.name}</span>
                      <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400">
                        {int.status}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No integrations configured</p>
              )}
            </div>

            <div>
              <h4 className="font-medium text-gray-300 mb-2">Federation Partners</h4>
              {selectedTenant.federation_partners.length > 0 ? (
                <ul className="space-y-2">
                  {selectedTenant.federation_partners.map((partnerId) => {
                    const partner = tenants.find(t => t.tenant_id === partnerId);
                    return (
                      <li key={partnerId} className="bg-gray-700/50 rounded px-3 py-2">
                        {partner?.name || partnerId}
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No federation partners</p>
              )}
            </div>
          </div>

          <div className="mt-6 flex space-x-3">
            <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
              Edit Tenant
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm">
              Add Data Source
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm">
              Add Integration
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded text-sm">
              Add Federation Partner
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
