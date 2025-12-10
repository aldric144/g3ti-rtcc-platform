'use client';

import { useState, useEffect } from 'react';

interface Alert {
  alert_id: string;
  alert_type: string;
  priority: string;
  title: string;
  description: string;
  source_agency: string;
  target_agencies: string[];
  jurisdiction_codes: string[];
  status: string;
  created_at: string;
  expires_at?: string;
  acknowledged_by: string[];
}

export default function InterAgencyAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setAlerts([
      {
        alert_id: 'alert-001',
        alert_type: 'pursuit',
        priority: 'critical',
        title: 'Active Pursuit - Armed Suspect',
        description: 'High-speed pursuit in progress. Suspect armed with handgun. Last seen I-95 NB approaching County line. All units in area requested to assist with containment.',
        source_agency: 'Metro City PD',
        target_agencies: ['County Sheriff', 'State Police', 'Transit Authority'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY'],
        status: 'active',
        created_at: new Date(Date.now() - 5 * 60000).toISOString(),
        acknowledged_by: ['County Sheriff'],
      },
      {
        alert_id: 'alert-002',
        alert_type: 'officer_safety',
        priority: 'urgent',
        title: 'Officer Safety - Known Violent Offender',
        description: 'James Wilson released from custody. History of assaulting officers. Last known address in Metro City. Exercise extreme caution if contact made.',
        source_agency: 'County Sheriff',
        target_agencies: ['Metro City PD', 'Transit Authority'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY'],
        status: 'active',
        created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
        acknowledged_by: ['Metro City PD', 'Transit Authority'],
      },
      {
        alert_id: 'alert-003',
        alert_type: 'bolo',
        priority: 'high',
        title: 'BOLO - Stolen Vehicle',
        description: 'Black BMW X5, CA plate 8ABC123. Stolen during armed carjacking. Suspect may be armed. Vehicle last seen heading east on Highway 10.',
        source_agency: 'Metro City PD',
        target_agencies: ['County Sheriff', 'State Police', 'East District PD'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY', 'CA-EAST'],
        status: 'active',
        created_at: new Date(Date.now() - 4 * 3600000).toISOString(),
        expires_at: new Date(Date.now() + 20 * 3600000).toISOString(),
        acknowledged_by: ['County Sheriff', 'State Police'],
      },
      {
        alert_id: 'alert-004',
        alert_type: 'missing_person',
        priority: 'high',
        title: 'Silver Alert - Missing Elderly',
        description: 'John Smith, 78 years old, white male, gray hair, blue eyes. Has dementia. Last seen downtown Metro City wearing blue jacket. May be disoriented.',
        source_agency: 'Metro City PD',
        target_agencies: ['County Sheriff', 'Transit Authority', 'West District PD'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY', 'CA-WEST'],
        status: 'active',
        created_at: new Date(Date.now() - 6 * 3600000).toISOString(),
        acknowledged_by: ['County Sheriff', 'Transit Authority', 'West District PD'],
      },
      {
        alert_id: 'alert-005',
        alert_type: 'pattern',
        priority: 'normal',
        title: 'Crime Pattern Alert - Vehicle Burglaries',
        description: 'Emerging pattern of vehicle burglaries in shopping center parking lots between 1800-2200 hours. 15 incidents in past 7 days across 3 jurisdictions.',
        source_agency: 'Regional Task Force',
        target_agencies: ['Metro City PD', 'County Sheriff', 'East District PD'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY', 'CA-EAST'],
        status: 'active',
        created_at: new Date(Date.now() - 12 * 3600000).toISOString(),
        acknowledged_by: ['Metro City PD', 'County Sheriff', 'East District PD'],
      },
      {
        alert_id: 'alert-006',
        alert_type: 'federal',
        priority: 'high',
        title: 'Federal Fugitive Alert',
        description: 'US Marshals seeking assistance locating federal fugitive. Armed robbery suspect with federal warrant. May be in Metro City area.',
        source_agency: 'US Marshals',
        target_agencies: ['Metro City PD', 'County Sheriff', 'State Police'],
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY'],
        status: 'active',
        created_at: new Date(Date.now() - 24 * 3600000).toISOString(),
        acknowledged_by: ['Metro City PD', 'County Sheriff'],
      },
    ]);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500 text-white';
      case 'urgent': return 'bg-orange-500 text-white';
      case 'high': return 'bg-yellow-500 text-black';
      case 'normal': return 'bg-blue-500 text-white';
      case 'low': return 'bg-gray-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getAlertTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      pursuit: '🚔',
      officer_safety: '🛡️',
      bolo: '🔍',
      missing_person: '👤',
      pattern: '📈',
      federal: '🏛️',
      terrorism: '⚠️',
      gang: '👥',
    };
    return icons[type] || '📢';
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const filteredAlerts = alerts
    .filter(a => filter === 'all' || a.alert_type === filter)
    .filter(a => priorityFilter === 'all' || a.priority === priorityFilter);

  const criticalCount = alerts.filter(a => a.priority === 'critical').length;
  const urgentCount = alerts.filter(a => a.priority === 'urgent').length;
  const activeCount = alerts.filter(a => a.status === 'active').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Inter-Agency Alerts Dashboard</h2>
          <p className="text-gray-400 text-sm">Cross-jurisdiction alert management</p>
        </div>
        <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm font-medium">
          + Broadcast Alert
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-red-500/50">
          <div className="text-3xl font-bold text-red-400">{criticalCount}</div>
          <div className="text-gray-400 text-sm">Critical Alerts</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/50">
          <div className="text-3xl font-bold text-orange-400">{urgentCount}</div>
          <div className="text-gray-400 text-sm">Urgent Alerts</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-blue-400">{activeCount}</div>
          <div className="text-gray-400 text-sm">Active Alerts</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-green-400">{alerts.length}</div>
          <div className="text-gray-400 text-sm">Total Alerts (24h)</div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
        >
          <option value="all">All Types</option>
          <option value="pursuit">Pursuits</option>
          <option value="officer_safety">Officer Safety</option>
          <option value="bolo">BOLOs</option>
          <option value="missing_person">Missing Persons</option>
          <option value="pattern">Crime Patterns</option>
          <option value="federal">Federal</option>
        </select>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="normal">Normal</option>
        </select>
        <input
          type="text"
          placeholder="Search alerts..."
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm flex-1 max-w-xs"
        />
      </div>

      <div className="space-y-4">
        {filteredAlerts.map((alert) => (
          <div
            key={alert.alert_id}
            className={`bg-gray-800 rounded-lg border ${
              alert.priority === 'critical' ? 'border-red-500' :
              alert.priority === 'urgent' ? 'border-orange-500' :
              'border-gray-700'
            }`}
          >
            <div className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getAlertTypeIcon(alert.alert_type)}</span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${getPriorityColor(alert.priority)}`}>
                        {alert.priority.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500 capitalize">
                        {alert.alert_type.replace('_', ' ')}
                      </span>
                    </div>
                    <h3 className="font-semibold mt-1">{alert.title}</h3>
                    <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-500">{formatTime(alert.created_at)}</span>
                  <p className="text-xs text-gray-500 mt-1">From: {alert.source_agency}</p>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div>
                    <span className="text-xs text-gray-500">Target Agencies:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {alert.target_agencies.map((agency) => (
                        <span
                          key={agency}
                          className={`text-xs px-2 py-0.5 rounded ${
                            alert.acknowledged_by.includes(agency)
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-gray-700 text-gray-400'
                          }`}
                        >
                          {agency} {alert.acknowledged_by.includes(agency) && '✓'}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Jurisdictions:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {alert.jurisdiction_codes.map((code) => (
                        <span key={code} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {alert.acknowledged_by.length}/{alert.target_agencies.length} acknowledged
                  </span>
                </div>
              </div>
            </div>

            <div className="px-4 py-3 bg-gray-700/30 border-t border-gray-700 flex items-center justify-between">
              <div className="flex space-x-2">
                <button className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm">
                  Acknowledge
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">
                  Forward
                </button>
                <button className="bg-gray-600 hover:bg-gray-500 px-3 py-1 rounded text-sm">
                  Add Update
                </button>
              </div>
              <div className="flex space-x-2">
                {alert.status === 'active' && (
                  <button className="bg-yellow-600 hover:bg-yellow-700 px-3 py-1 rounded text-sm">
                    Resolve
                  </button>
                )}
                <button className="bg-gray-600 hover:bg-gray-500 px-3 py-1 rounded text-sm">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAlerts.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <div className="text-4xl mb-4">📢</div>
          <h3 className="text-lg font-medium mb-2">No Alerts Found</h3>
          <p className="text-gray-400 text-sm">
            No alerts match your current filters
          </p>
        </div>
      )}
    </div>
  );
}
