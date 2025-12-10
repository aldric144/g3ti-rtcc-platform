'use client';

import { useState, useEffect } from 'react';

interface NetworkNode {
  node_id: string;
  name: string;
  node_type: string;
  ideology: string;
  threat_level: string;
  activity_level: string;
  follower_count: number;
  influence_score: number;
  is_monitored: boolean;
}

interface NetworkCluster {
  cluster_id: string;
  name: string;
  ideology: string;
  node_count: number;
  threat_level: string;
  total_influence: number;
}

interface RadicalizationAlert {
  node_id: string;
  node_name: string;
  current_stage: string;
  risk_score: number;
  velocity: number;
  intervention_recommended: boolean;
}

export default function ExtremistNetworksGraph() {
  const [nodes, setNodes] = useState<NetworkNode[]>([]);
  const [clusters, setClusters] = useState<NetworkCluster[]>([]);
  const [alerts, setAlerts] = useState<RadicalizationAlert[]>([]);
  const [activeView, setActiveView] = useState<'graph' | 'nodes' | 'clusters' | 'alerts'>('graph');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockNodes: NetworkNode[] = [
      {
        node_id: 'node-001',
        name: 'Alpha Leader',
        node_type: 'individual',
        ideology: 'white_supremacist',
        threat_level: 'high',
        activity_level: 'very_high',
        follower_count: 15000,
        influence_score: 85,
        is_monitored: true,
      },
      {
        node_id: 'node-002',
        name: 'Patriot Front Channel',
        node_type: 'channel',
        ideology: 'militia',
        threat_level: 'moderate',
        activity_level: 'high',
        follower_count: 8500,
        influence_score: 72,
        is_monitored: true,
      },
      {
        node_id: 'node-003',
        name: 'Accelerationist Forum',
        node_type: 'forum',
        ideology: 'accelerationist',
        threat_level: 'severe',
        activity_level: 'high',
        follower_count: 3200,
        influence_score: 68,
        is_monitored: true,
      },
      {
        node_id: 'node-004',
        name: 'Local Cell Beta',
        node_type: 'group',
        ideology: 'anti_government',
        threat_level: 'high',
        activity_level: 'moderate',
        follower_count: 450,
        influence_score: 45,
        is_monitored: true,
      },
    ];

    const mockClusters: NetworkCluster[] = [
      {
        cluster_id: 'clust-001',
        name: 'Northeast Militia Network',
        ideology: 'militia',
        node_count: 24,
        threat_level: 'high',
        total_influence: 450,
      },
      {
        cluster_id: 'clust-002',
        name: 'Online Accelerationist Hub',
        ideology: 'accelerationist',
        node_count: 18,
        threat_level: 'severe',
        total_influence: 380,
      },
      {
        cluster_id: 'clust-003',
        name: 'Regional Supremacist Cell',
        ideology: 'white_supremacist',
        node_count: 12,
        threat_level: 'high',
        total_influence: 290,
      },
    ];

    const mockAlerts: RadicalizationAlert[] = [
      {
        node_id: 'node-005',
        node_name: 'Subject Alpha',
        current_stage: 'indoctrination',
        risk_score: 78,
        velocity: 5.2,
        intervention_recommended: true,
      },
      {
        node_id: 'node-006',
        node_name: 'Subject Beta',
        current_stage: 'self_identification',
        risk_score: 52,
        velocity: 2.8,
        intervention_recommended: false,
      },
      {
        node_id: 'node-007',
        node_name: 'Subject Gamma',
        current_stage: 'action',
        risk_score: 92,
        velocity: 8.5,
        intervention_recommended: true,
      },
    ];

    setTimeout(() => {
      setNodes(mockNodes);
      setClusters(mockClusters);
      setAlerts(mockAlerts);
      setLoading(false);
    }, 500);
  }, []);

  const getThreatColor = (level: string) => {
    const colors: Record<string, string> = {
      unknown: 'text-gray-400 bg-gray-500/20',
      low: 'text-green-400 bg-green-500/20',
      moderate: 'text-yellow-400 bg-yellow-500/20',
      high: 'text-orange-400 bg-orange-500/20',
      severe: 'text-red-400 bg-red-500/20',
      critical: 'text-red-500 bg-red-600/30',
    };
    return colors[level] || 'text-gray-400 bg-gray-500/20';
  };

  const getStageColor = (stage: string) => {
    const colors: Record<string, string> = {
      pre_radicalization: 'text-green-400 bg-green-500/20',
      self_identification: 'text-yellow-400 bg-yellow-500/20',
      indoctrination: 'text-orange-400 bg-orange-500/20',
      action: 'text-red-500 bg-red-600/30',
      post_action: 'text-gray-400 bg-gray-500/20',
    };
    return colors[stage] || 'text-gray-400 bg-gray-500/20';
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-amber-400">
            Extremist Network Analysis
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveView('graph')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'graph'
                  ? 'bg-amber-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Network Graph
            </button>
            <button
              onClick={() => setActiveView('nodes')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'nodes'
                  ? 'bg-amber-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Nodes
            </button>
            <button
              onClick={() => setActiveView('clusters')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'clusters'
                  ? 'bg-amber-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Clusters
            </button>
            <button
              onClick={() => setActiveView('alerts')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'alerts'
                  ? 'bg-amber-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Radicalization Alerts
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
          </div>
        ) : activeView === 'graph' ? (
          <div className="h-96 bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <svg className="w-full h-full">
                <line x1="20%" y1="30%" x2="50%" y2="50%" stroke="#f59e0b" strokeWidth="2" />
                <line x1="80%" y1="25%" x2="50%" y2="50%" stroke="#f59e0b" strokeWidth="2" />
                <line x1="30%" y1="70%" x2="50%" y2="50%" stroke="#f59e0b" strokeWidth="2" />
                <line x1="70%" y1="75%" x2="50%" y2="50%" stroke="#f59e0b" strokeWidth="2" />
                <line x1="20%" y1="30%" x2="30%" y2="70%" stroke="#f59e0b" strokeWidth="1" />
                <line x1="80%" y1="25%" x2="70%" y2="75%" stroke="#f59e0b" strokeWidth="1" />
              </svg>
            </div>
            <div className="absolute" style={{ left: '20%', top: '30%' }}>
              <div className="w-12 h-12 bg-red-500/30 border-2 border-red-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white">A</span>
              </div>
            </div>
            <div className="absolute" style={{ left: '80%', top: '25%' }}>
              <div className="w-10 h-10 bg-orange-500/30 border-2 border-orange-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white">B</span>
              </div>
            </div>
            <div className="absolute" style={{ left: '50%', top: '50%' }}>
              <div className="w-16 h-16 bg-amber-500/30 border-2 border-amber-500 rounded-full flex items-center justify-center">
                <span className="text-sm text-white font-bold">HUB</span>
              </div>
            </div>
            <div className="absolute" style={{ left: '30%', top: '70%' }}>
              <div className="w-10 h-10 bg-yellow-500/30 border-2 border-yellow-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white">C</span>
              </div>
            </div>
            <div className="absolute" style={{ left: '70%', top: '75%' }}>
              <div className="w-10 h-10 bg-orange-500/30 border-2 border-orange-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white">D</span>
              </div>
            </div>
            <div className="absolute bottom-4 left-4 bg-gray-800/80 p-3 rounded">
              <p className="text-xs text-gray-400">Interactive network visualization</p>
              <p className="text-xs text-amber-400">4 nodes • 6 connections</p>
            </div>
          </div>
        ) : activeView === 'nodes' ? (
          <div className="space-y-4">
            {nodes.map((node) => (
              <div
                key={node.node_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-amber-500 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-white flex items-center">
                      {node.name}
                      {node.is_monitored && (
                        <span className="ml-2 w-2 h-2 bg-green-500 rounded-full"></span>
                      )}
                    </h3>
                    <p className="text-sm text-gray-400">
                      {node.node_type} • {node.ideology.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${getThreatColor(node.threat_level)}`}
                    >
                      {node.threat_level}
                    </span>
                    <span className="px-2 py-1 text-sm font-bold text-amber-400 bg-amber-500/20 rounded">
                      {node.influence_score}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <div>
                    <p className="text-xs text-gray-400">Followers</p>
                    <p className="text-lg font-semibold text-white">
                      {node.follower_count.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Activity</p>
                    <p className="text-lg font-semibold text-white capitalize">
                      {node.activity_level.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <button className="px-3 py-1 text-xs bg-amber-600 hover:bg-amber-700 rounded">
                      View Profile
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : activeView === 'clusters' ? (
          <div className="space-y-4">
            {clusters.map((cluster) => (
              <div
                key={cluster.cluster_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-white">{cluster.name}</h3>
                    <p className="text-sm text-gray-400 capitalize">
                      {cluster.ideology.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 text-sm rounded ${getThreatColor(cluster.threat_level)}`}
                  >
                    {cluster.threat_level}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-800 p-3 rounded">
                    <p className="text-2xl font-bold text-amber-400">
                      {cluster.node_count}
                    </p>
                    <p className="text-xs text-gray-400">Nodes</p>
                  </div>
                  <div className="bg-gray-800 p-3 rounded">
                    <p className="text-2xl font-bold text-amber-400">
                      {cluster.total_influence}
                    </p>
                    <p className="text-xs text-gray-400">Total Influence</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div
                key={alert.node_id}
                className={`p-4 rounded-lg border ${
                  alert.intervention_recommended
                    ? 'bg-red-900/20 border-red-500'
                    : 'bg-gray-700/50 border-gray-600'
                }`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-white">{alert.node_name}</h3>
                    <span
                      className={`px-2 py-1 text-xs rounded ${getStageColor(alert.current_stage)}`}
                    >
                      {alert.current_stage.replace(/_/g, ' ')}
                    </span>
                  </div>
                  {alert.intervention_recommended && (
                    <span className="px-3 py-1 text-xs bg-red-600 text-white rounded animate-pulse">
                      INTERVENTION RECOMMENDED
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-400">Risk Score</p>
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-600 rounded-full h-2 mr-2">
                        <div
                          className={`h-2 rounded-full ${
                            alert.risk_score >= 80
                              ? 'bg-red-500'
                              : alert.risk_score >= 60
                                ? 'bg-orange-500'
                                : 'bg-yellow-500'
                          }`}
                          style={{ width: `${alert.risk_score}%` }}
                        ></div>
                      </div>
                      <span className="text-lg font-bold text-white">
                        {alert.risk_score}
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Velocity</p>
                    <p
                      className={`text-lg font-bold ${
                        alert.velocity > 5
                          ? 'text-red-400'
                          : alert.velocity > 2
                            ? 'text-orange-400'
                            : 'text-yellow-400'
                      }`}
                    >
                      +{alert.velocity.toFixed(1)}/day
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
