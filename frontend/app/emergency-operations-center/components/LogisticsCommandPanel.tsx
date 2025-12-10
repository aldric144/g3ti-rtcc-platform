'use client';

import React, { useState, useEffect } from 'react';

interface DeploymentUnit {
  unit_id: string;
  name: string;
  deployment_type: string;
  personnel_count: number;
  status: string;
  assigned_location?: {
    lat: number;
    lng: number;
    name: string;
  };
}

interface SupplyItem {
  item_id: string;
  name: string;
  category: string;
  quantity: number;
  status: string;
  minimum_stock: number;
}

interface InfrastructureOutage {
  asset_id: string;
  name: string;
  infrastructure_type: string;
  status: string;
  affected_population: number;
  estimated_restoration: string;
}

interface ResourceMetrics {
  shelters: {
    total: number;
    open: number;
    total_capacity: number;
    total_occupancy: number;
  };
  supplies: {
    total_items: number;
    low_stock: number;
    critical: number;
  };
  deployments: {
    total_units: number;
    deployed: number;
    available: number;
  };
  infrastructure: {
    total_assets: number;
    operational: number;
    outages: number;
  };
}

export default function LogisticsCommandPanel() {
  const [units, setUnits] = useState<DeploymentUnit[]>([]);
  const [supplies, setSupplies] = useState<SupplyItem[]>([]);
  const [outages, setOutages] = useState<InfrastructureOutage[]>([]);
  const [metrics, setMetrics] = useState<ResourceMetrics | null>(null);
  const [activeTab, setActiveTab] = useState<'deployments' | 'supplies' | 'infrastructure'>('deployments');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogisticsData();
    const interval = setInterval(fetchLogisticsData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogisticsData = async () => {
    try {
      const [unitsRes, suppliesRes, outagesRes, metricsRes] = await Promise.all([
        fetch('/api/emergency/resources/deployments'),
        fetch('/api/emergency/resources/supplies/low-stock'),
        fetch('/api/emergency/resources/infrastructure/outages'),
        fetch('/api/emergency/resources/metrics'),
      ]);

      if (unitsRes.ok) setUnits(await unitsRes.json());
      if (suppliesRes.ok) setSupplies(await suppliesRes.json());
      if (outagesRes.ok) setOutages(await outagesRes.json());
      if (metricsRes.ok) setMetrics(await metricsRes.json());
    } catch (error) {
      console.error('Failed to fetch logistics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'available': return 'text-green-400';
      case 'deployed': return 'text-blue-400';
      case 'in_transit': return 'text-yellow-400';
      case 'returning': return 'text-purple-400';
      case 'maintenance': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getInfraStatusColor = (status: string): string => {
    switch (status) {
      case 'operational': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'offline': return 'text-red-400';
      case 'damaged': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading logistics data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>📦</span> Logistics Command
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('deployments')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'deployments' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Deployments
          </button>
          <button
            onClick={() => setActiveTab('supplies')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'supplies' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Supplies
          </button>
          <button
            onClick={() => setActiveTab('infrastructure')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'infrastructure' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Infrastructure
          </button>
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Units Deployed</div>
            <div className="text-blue-400 text-lg font-bold">
              {metrics.deployments?.deployed || 0} / {metrics.deployments?.total_units || 0}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Low Stock Items</div>
            <div className={`text-lg font-bold ${(metrics.supplies?.low_stock || 0) > 0 ? 'text-yellow-400' : 'text-green-400'}`}>
              {metrics.supplies?.low_stock || 0}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Infrastructure Outages</div>
            <div className={`text-lg font-bold ${(metrics.infrastructure?.outages || 0) > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {metrics.infrastructure?.outages || 0}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Shelter Occupancy</div>
            <div className="text-white text-lg font-bold">
              {Math.round(((metrics.shelters?.total_occupancy || 0) / (metrics.shelters?.total_capacity || 1)) * 100)}%
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'deployments' && (
          <div className="space-y-2">
            {units.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No deployment units registered</div>
            ) : (
              units.map(unit => (
                <div key={unit.unit_id} className="bg-gray-800 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-white font-medium">{unit.name}</div>
                      <div className="text-gray-400 text-sm">
                        {unit.deployment_type} • {unit.personnel_count} personnel
                      </div>
                    </div>
                    <span className={`font-medium ${getStatusColor(unit.status)}`}>
                      {unit.status.toUpperCase().replace('_', ' ')}
                    </span>
                  </div>
                  {unit.assigned_location && (
                    <div className="mt-2 text-sm text-gray-400">
                      📍 {unit.assigned_location.name}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'supplies' && (
          <div className="space-y-2">
            {supplies.length === 0 ? (
              <div className="text-gray-500 text-center py-8">All supplies adequately stocked</div>
            ) : (
              <>
                <div className="text-yellow-400 text-sm mb-2">⚠️ Low Stock Alerts</div>
                {supplies.map(item => (
                  <div key={item.item_id} className="bg-gray-800 p-4 rounded">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">{item.name}</div>
                        <div className="text-gray-400 text-sm">{item.category}</div>
                      </div>
                      <div className="text-right">
                        <div className={`font-medium ${item.quantity < item.minimum_stock / 2 ? 'text-red-400' : 'text-yellow-400'}`}>
                          {item.quantity} units
                        </div>
                        <div className="text-gray-500 text-xs">Min: {item.minimum_stock}</div>
                      </div>
                    </div>
                    <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${item.quantity < item.minimum_stock / 2 ? 'bg-red-500' : 'bg-yellow-500'}`}
                        style={{ width: `${Math.min(100, (item.quantity / item.minimum_stock) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {activeTab === 'infrastructure' && (
          <div className="space-y-2">
            {outages.length === 0 ? (
              <div className="text-gray-500 text-center py-8">All infrastructure operational</div>
            ) : (
              <>
                <div className="text-red-400 text-sm mb-2">⚡ Active Outages</div>
                {outages.map(outage => (
                  <div key={outage.asset_id} className="bg-gray-800 p-4 rounded">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">{outage.name}</div>
                        <div className="text-gray-400 text-sm">{outage.infrastructure_type}</div>
                      </div>
                      <span className={`font-medium ${getInfraStatusColor(outage.status)}`}>
                        {outage.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Affected: </span>
                        <span className="text-white">{outage.affected_population.toLocaleString()} people</span>
                      </div>
                      {outage.estimated_restoration && (
                        <div>
                          <span className="text-gray-400">Est. Restoration: </span>
                          <span className="text-white">{outage.estimated_restoration}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
