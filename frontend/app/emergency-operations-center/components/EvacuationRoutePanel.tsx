'use client';

import React, { useState, useEffect } from 'react';

interface EvacuationRoute {
  route_id: string;
  name: string;
  origin_zone: string;
  distance_miles: number;
  estimated_time_minutes: number;
  capacity_vehicles_per_hour: number;
  status: string;
  contraflow_enabled: boolean;
}

interface EvacuationOrder {
  order_id: string;
  zone: string;
  priority: string;
  affected_population: number;
  is_active: boolean;
  recommended_routes: string[];
  shelter_assignments: string[];
}

interface TrafficSimulation {
  simulation_id: string;
  scenario_name: string;
  total_vehicles: number;
  average_speed_mph: number;
  clearance_time_hours: number;
  bottleneck_locations: string[];
}

interface EvacuationMetrics {
  total_routes: number;
  active_routes: number;
  total_orders: number;
  active_orders: number;
  total_population_evacuating: number;
  special_needs_evacuees: number;
}

export default function EvacuationRoutePanel() {
  const [routes, setRoutes] = useState<EvacuationRoute[]>([]);
  const [orders, setOrders] = useState<EvacuationOrder[]>([]);
  const [metrics, setMetrics] = useState<EvacuationMetrics | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<EvacuationRoute | null>(null);
  const [activeTab, setActiveTab] = useState<'routes' | 'orders' | 'simulation'>('routes');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvacuationData();
    const interval = setInterval(fetchEvacuationData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchEvacuationData = async () => {
    try {
      const [routesRes, ordersRes, metricsRes] = await Promise.all([
        fetch('/api/emergency/evacuation/routes'),
        fetch('/api/emergency/evacuation/orders'),
        fetch('/api/emergency/evacuation/metrics'),
      ]);

      if (routesRes.ok) setRoutes(await routesRes.json());
      if (ordersRes.ok) setOrders(await ordersRes.json());
      if (metricsRes.ok) setMetrics(await metricsRes.json());
    } catch (error) {
      console.error('Failed to fetch evacuation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'open': return 'text-green-400';
      case 'congested': return 'text-yellow-400';
      case 'blocked': return 'text-red-400';
      case 'closed': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'immediate': return 'bg-red-600';
      case 'urgent': return 'bg-orange-500';
      case 'mandatory': return 'bg-yellow-500';
      case 'voluntary': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const handleEnableContraflow = async (routeId: string) => {
    try {
      const res = await fetch(`/api/emergency/evacuation/route/${routeId}/contraflow`, {
        method: 'POST',
      });
      if (res.ok) {
        fetchEvacuationData();
      }
    } catch (error) {
      console.error('Failed to enable contraflow:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading evacuation data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🚗</span> Evacuation Routes
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('routes')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'routes' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Routes
          </button>
          <button
            onClick={() => setActiveTab('orders')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'orders' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Orders
          </button>
          <button
            onClick={() => setActiveTab('simulation')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'simulation' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Simulation
          </button>
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Active Routes</div>
            <div className="text-white text-lg font-bold">{metrics.active_routes}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Active Orders</div>
            <div className="text-white text-lg font-bold">{metrics.active_orders}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Evacuating</div>
            <div className="text-white text-lg font-bold">
              {metrics.total_population_evacuating.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Special Needs</div>
            <div className="text-white text-lg font-bold">{metrics.special_needs_evacuees}</div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'routes' && (
          <div className="space-y-2">
            {routes.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No evacuation routes configured</div>
            ) : (
              routes.map(route => (
                <div
                  key={route.route_id}
                  onClick={() => setSelectedRoute(route)}
                  className={`bg-gray-800 p-4 rounded cursor-pointer transition-colors ${
                    selectedRoute?.route_id === route.route_id
                      ? 'ring-2 ring-blue-500'
                      : 'hover:bg-gray-750'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-white font-medium">{route.name}</div>
                      <div className="text-gray-400 text-sm">
                        Zone {route.origin_zone} • {route.distance_miles} mi • {route.estimated_time_minutes} min
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {route.contraflow_enabled && (
                        <span className="bg-purple-600 text-white px-2 py-0.5 rounded text-xs">
                          CONTRAFLOW
                        </span>
                      )}
                      <span className={`font-medium ${getStatusColor(route.status)}`}>
                        {route.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-4 text-sm">
                    <div className="text-gray-400">
                      Capacity: <span className="text-white">{route.capacity_vehicles_per_hour.toLocaleString()}/hr</span>
                    </div>
                    {!route.contraflow_enabled && route.status === 'open' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEnableContraflow(route.route_id);
                        }}
                        className="text-purple-400 hover:text-purple-300 text-xs"
                      >
                        Enable Contraflow
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="space-y-2">
            {orders.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No active evacuation orders</div>
            ) : (
              orders.map(order => (
                <div key={order.order_id} className="bg-gray-800 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs text-white ${getPriorityColor(order.priority)}`}>
                        {order.priority.toUpperCase()}
                      </span>
                      <span className="text-white font-medium">Zone {order.zone}</span>
                    </div>
                    <span className={`text-sm ${order.is_active ? 'text-green-400' : 'text-gray-400'}`}>
                      {order.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400 text-xs">Affected Population</div>
                      <div className="text-white">{order.affected_population.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Recommended Routes</div>
                      <div className="text-white">{order.recommended_routes.length} routes</div>
                    </div>
                  </div>
                  {order.shelter_assignments.length > 0 && (
                    <div className="mt-2 text-sm">
                      <div className="text-gray-400 text-xs">Shelter Assignments</div>
                      <div className="text-gray-300">{order.shelter_assignments.join(', ')}</div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'simulation' && (
          <div className="bg-gray-800 p-4 rounded">
            <div className="text-center py-8">
              <div className="text-4xl mb-4">🚦</div>
              <div className="text-white font-medium">Traffic Simulation</div>
              <div className="text-gray-400 text-sm mt-2">
                Run simulations to predict evacuation clearance times
              </div>
              <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                Run New Simulation
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
