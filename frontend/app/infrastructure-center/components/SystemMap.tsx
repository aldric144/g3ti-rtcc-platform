'use client';

import { useState, useEffect } from 'react';

interface ServiceNode {
  id: string;
  name: string;
  type: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'offline';
  instances: number;
  healthyInstances: number;
  cpuUsage: number;
  memoryUsage: number;
  connections: number;
}

interface DataPathway {
  from: string;
  to: string;
  status: 'active' | 'degraded' | 'inactive';
  throughput: string;
}

const mockServices: ServiceNode[] = [
  { id: 'api-gateway', name: 'API Gateway', type: 'gateway', status: 'healthy', instances: 3, healthyInstances: 3, cpuUsage: 45, memoryUsage: 62, connections: 1250 },
  { id: 'auth-service', name: 'Auth Service', type: 'auth', status: 'healthy', instances: 2, healthyInstances: 2, cpuUsage: 32, memoryUsage: 48, connections: 890 },
  { id: 'ai-engine', name: 'AI Engine', type: 'ai', status: 'healthy', instances: 2, healthyInstances: 2, cpuUsage: 78, memoryUsage: 85, connections: 45 },
  { id: 'websocket-broker', name: 'WebSocket Broker', type: 'websocket', status: 'healthy', instances: 2, healthyInstances: 2, cpuUsage: 28, memoryUsage: 35, connections: 2100 },
  { id: 'postgres-primary', name: 'PostgreSQL', type: 'database', status: 'healthy', instances: 1, healthyInstances: 1, cpuUsage: 55, memoryUsage: 72, connections: 450 },
  { id: 'redis-cluster', name: 'Redis Cluster', type: 'cache', status: 'healthy', instances: 3, healthyInstances: 3, cpuUsage: 22, memoryUsage: 45, connections: 3200 },
  { id: 'elasticsearch', name: 'Elasticsearch', type: 'search', status: 'healthy', instances: 3, healthyInstances: 3, cpuUsage: 48, memoryUsage: 68, connections: 180 },
  { id: 'neo4j-cluster', name: 'Neo4j Cluster', type: 'graph', status: 'healthy', instances: 3, healthyInstances: 3, cpuUsage: 42, memoryUsage: 58, connections: 120 },
  { id: 'drone-service', name: 'Drone Service', type: 'operational', status: 'healthy', instances: 1, healthyInstances: 1, cpuUsage: 35, memoryUsage: 42, connections: 25 },
  { id: 'fusion-cloud', name: 'Fusion Cloud', type: 'federation', status: 'healthy', instances: 2, healthyInstances: 2, cpuUsage: 38, memoryUsage: 52, connections: 85 },
];

const mockPathways: DataPathway[] = [
  { from: 'api-gateway', to: 'auth-service', status: 'active', throughput: '1.2 GB/s' },
  { from: 'api-gateway', to: 'ai-engine', status: 'active', throughput: '850 MB/s' },
  { from: 'api-gateway', to: 'websocket-broker', status: 'active', throughput: '2.1 GB/s' },
  { from: 'ai-engine', to: 'postgres-primary', status: 'active', throughput: '450 MB/s' },
  { from: 'ai-engine', to: 'elasticsearch', status: 'active', throughput: '320 MB/s' },
  { from: 'ai-engine', to: 'neo4j-cluster', status: 'active', throughput: '180 MB/s' },
  { from: 'auth-service', to: 'redis-cluster', status: 'active', throughput: '1.8 GB/s' },
  { from: 'fusion-cloud', to: 'api-gateway', status: 'active', throughput: '650 MB/s' },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy':
    case 'active':
      return 'bg-green-500';
    case 'degraded':
      return 'bg-yellow-500';
    case 'unhealthy':
      return 'bg-red-500';
    case 'offline':
    case 'inactive':
      return 'bg-gray-500';
    default:
      return 'bg-gray-500';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'gateway': return '🚪';
    case 'auth': return '🔐';
    case 'ai': return '🤖';
    case 'websocket': return '📡';
    case 'database': return '🗄️';
    case 'cache': return '⚡';
    case 'search': return '🔍';
    case 'graph': return '🕸️';
    case 'operational': return '🚁';
    case 'federation': return '🌐';
    default: return '📦';
  }
};

export default function SystemMap() {
  const [services, setServices] = useState<ServiceNode[]>(mockServices);
  const [pathways] = useState<DataPathway[]>(mockPathways);
  const [selectedService, setSelectedService] = useState<ServiceNode | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setServices(prev => prev.map(service => ({
        ...service,
        cpuUsage: Math.max(10, Math.min(95, service.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(20, Math.min(95, service.memoryUsage + (Math.random() - 0.5) * 5)),
        connections: Math.max(0, service.connections + Math.floor((Math.random() - 0.5) * 100)),
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Real-Time System Map</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-green-500 rounded-full"></span>
            <span className="text-sm text-gray-400">Healthy</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
            <span className="text-sm text-gray-400">Degraded</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-red-500 rounded-full"></span>
            <span className="text-sm text-gray-400">Unhealthy</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        {services.map((service) => (
          <div
            key={service.id}
            onClick={() => setSelectedService(service)}
            className={`bg-gray-800 rounded-lg p-4 border cursor-pointer transition-all hover:border-blue-500 ${
              selectedService?.id === service.id ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-gray-700'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{getTypeIcon(service.type)}</span>
              <span className={`w-3 h-3 rounded-full ${getStatusColor(service.status)}`}></span>
            </div>
            <h3 className="font-medium text-sm mb-1">{service.name}</h3>
            <p className="text-xs text-gray-400 mb-3">
              {service.healthyInstances}/{service.instances} instances
            </p>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">CPU</span>
                  <span>{service.cpuUsage.toFixed(0)}%</span>
                </div>
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      service.cpuUsage > 80 ? 'bg-red-500' : service.cpuUsage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${service.cpuUsage}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Memory</span>
                  <span>{service.memoryUsage.toFixed(0)}%</span>
                </div>
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      service.memoryUsage > 85 ? 'bg-red-500' : service.memoryUsage > 70 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${service.memoryUsage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-4">Data Pathways</h3>
          <div className="space-y-2">
            {pathways.map((pathway, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${getStatusColor(pathway.status)}`}></span>
                  <span className="text-gray-300">{pathway.from}</span>
                  <span className="text-gray-500">→</span>
                  <span className="text-gray-300">{pathway.to}</span>
                </div>
                <span className="text-gray-400">{pathway.throughput}</span>
              </div>
            ))}
          </div>
        </div>

        {selectedService && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-medium mb-4">Service Details: {selectedService.name}</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Service ID:</span>
                <p className="font-mono">{selectedService.id}</p>
              </div>
              <div>
                <span className="text-gray-400">Type:</span>
                <p className="capitalize">{selectedService.type}</p>
              </div>
              <div>
                <span className="text-gray-400">Status:</span>
                <p className={`capitalize ${
                  selectedService.status === 'healthy' ? 'text-green-400' :
                  selectedService.status === 'degraded' ? 'text-yellow-400' : 'text-red-400'
                }`}>{selectedService.status}</p>
              </div>
              <div>
                <span className="text-gray-400">Instances:</span>
                <p>{selectedService.healthyInstances}/{selectedService.instances}</p>
              </div>
              <div>
                <span className="text-gray-400">CPU Usage:</span>
                <p>{selectedService.cpuUsage.toFixed(1)}%</p>
              </div>
              <div>
                <span className="text-gray-400">Memory Usage:</span>
                <p>{selectedService.memoryUsage.toFixed(1)}%</p>
              </div>
              <div>
                <span className="text-gray-400">Active Connections:</span>
                <p>{selectedService.connections.toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
