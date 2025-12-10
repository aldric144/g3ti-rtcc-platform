'use client';

import { useState, useEffect } from 'react';

interface IntelChannel {
  channel_id: string;
  channel_type: string;
  name: string;
  description: string;
  message_count: number;
  subscriber_count: number;
  is_public: boolean;
}

interface IntelMessage {
  message_id: string;
  channel_type: string;
  source_agency_name: string;
  priority: string;
  title: string;
  summary: string;
  content: string;
  jurisdiction_codes: string[];
  tags: string[];
  created_at: string;
  status: string;
}

export default function SharedIntelHub() {
  const [channels, setChannels] = useState<IntelChannel[]>([]);
  const [messages, setMessages] = useState<IntelMessage[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>('all');
  const [selectedMessage, setSelectedMessage] = useState<IntelMessage | null>(null);

  useEffect(() => {
    loadChannels();
    loadMessages();
  }, []);

  const loadChannels = async () => {
    setChannels([
      { channel_id: 'ch-001', channel_type: 'pursuits', name: 'Active Pursuits', description: 'Real-time pursuit coordination', message_count: 45, subscriber_count: 12, is_public: true },
      { channel_id: 'ch-002', channel_type: 'bolos', name: 'BOLOs', description: 'Be On the Lookout alerts', message_count: 128, subscriber_count: 15, is_public: true },
      { channel_id: 'ch-003', channel_type: 'patterns', name: 'Crime Patterns', description: 'Emerging crime pattern alerts', message_count: 67, subscriber_count: 10, is_public: true },
      { channel_id: 'ch-004', channel_type: 'high_risk_suspects', name: 'High-Risk Suspects', description: 'High-risk individual tracking', message_count: 34, subscriber_count: 8, is_public: false },
      { channel_id: 'ch-005', channel_type: 'regional_alerts', name: 'Regional Alerts', description: 'Multi-jurisdiction alerts', message_count: 89, subscriber_count: 14, is_public: true },
      { channel_id: 'ch-006', channel_type: 'officer_safety', name: 'Officer Safety', description: 'Officer safety bulletins', message_count: 23, subscriber_count: 15, is_public: true },
    ]);
  };

  const loadMessages = async () => {
    setMessages([
      {
        message_id: 'msg-001',
        channel_type: 'pursuits',
        source_agency_name: 'Metro City PD',
        priority: 'critical',
        title: 'Active Pursuit - Armed Robbery Suspect',
        summary: 'High-speed pursuit in progress on I-95 northbound',
        content: 'Armed robbery suspect fleeing in black sedan. Last seen I-95 NB mile marker 45. Suspect considered armed and dangerous. All units in area requested to assist.',
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY'],
        tags: ['pursuit', 'armed', 'robbery'],
        created_at: new Date(Date.now() - 5 * 60000).toISOString(),
        status: 'published',
      },
      {
        message_id: 'msg-002',
        channel_type: 'bolos',
        source_agency_name: 'County Sheriff',
        priority: 'high',
        title: 'BOLO - Missing Elderly Person',
        summary: '78-year-old male with dementia, last seen downtown area',
        content: 'Missing person: John Smith, 78 years old, white male, gray hair, blue eyes. Last seen wearing blue jacket and khaki pants. Has dementia and may be disoriented.',
        jurisdiction_codes: ['CA-COUNTY'],
        tags: ['missing', 'elderly', 'silver_alert'],
        created_at: new Date(Date.now() - 30 * 60000).toISOString(),
        status: 'published',
      },
      {
        message_id: 'msg-003',
        channel_type: 'patterns',
        source_agency_name: 'Regional Task Force',
        priority: 'normal',
        title: 'Emerging Pattern - Vehicle Burglaries',
        summary: 'Cluster of vehicle burglaries in shopping center parking lots',
        content: 'Analysis shows emerging pattern of vehicle burglaries targeting shopping center parking lots between 1800-2200 hours. 15 incidents in past 7 days across 3 jurisdictions.',
        jurisdiction_codes: ['CA-METRO', 'CA-COUNTY', 'CA-EAST'],
        tags: ['pattern', 'burglary', 'vehicle'],
        created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
        status: 'published',
      },
      {
        message_id: 'msg-004',
        channel_type: 'officer_safety',
        source_agency_name: 'Metro City PD',
        priority: 'urgent',
        title: 'Officer Safety Alert - Known Cop Fighter',
        summary: 'Subject with history of assaulting officers released from custody',
        content: 'Subject James Wilson released from county jail today. History of violent resistance and assault on officers. Last known address: 123 Main St. Exercise caution if contact made.',
        jurisdiction_codes: ['CA-METRO'],
        tags: ['officer_safety', 'violent', 'released'],
        created_at: new Date(Date.now() - 4 * 3600000).toISOString(),
        status: 'published',
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

  const getChannelIcon = (type: string) => {
    const icons: Record<string, string> = {
      pursuits: '🚔',
      bolos: '🔍',
      patterns: '📈',
      high_risk_suspects: '⚠️',
      regional_alerts: '📢',
      officer_safety: '🛡️',
    };
    return icons[type] || '📋';
  };

  const filteredMessages = selectedChannel === 'all'
    ? messages
    : messages.filter(m => m.channel_type === selectedChannel);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="grid grid-cols-12 gap-6">
      <div className="col-span-3">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Intelligence Channels</h3>
          </div>
          <div className="p-2">
            <button
              onClick={() => setSelectedChannel('all')}
              className={`w-full text-left px-3 py-2 rounded transition-colors ${
                selectedChannel === 'all' ? 'bg-blue-600' : 'hover:bg-gray-700'
              }`}
            >
              <span className="mr-2">📋</span>
              All Channels
            </button>
            {channels.map((channel) => (
              <button
                key={channel.channel_id}
                onClick={() => setSelectedChannel(channel.channel_type)}
                className={`w-full text-left px-3 py-2 rounded transition-colors ${
                  selectedChannel === channel.channel_type ? 'bg-blue-600' : 'hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>
                    <span className="mr-2">{getChannelIcon(channel.channel_type)}</span>
                    {channel.name}
                  </span>
                  <span className="text-xs bg-gray-700 px-2 py-1 rounded">
                    {channel.message_count}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 mt-4 p-4">
          <h4 className="font-medium mb-3">Channel Stats</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Messages</span>
              <span>{channels.reduce((acc, c) => acc + c.message_count, 0)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Active Channels</span>
              <span>{channels.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Subscribers</span>
              <span>{channels.reduce((acc, c) => acc + c.subscriber_count, 0)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="col-span-5">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <h3 className="font-semibold">Intelligence Feed</h3>
            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">
              + New Message
            </button>
          </div>
          <div className="divide-y divide-gray-700 max-h-[600px] overflow-y-auto">
            {filteredMessages.map((message) => (
              <div
                key={message.message_id}
                onClick={() => setSelectedMessage(message)}
                className={`p-4 cursor-pointer transition-colors ${
                  selectedMessage?.message_id === message.message_id
                    ? 'bg-gray-700'
                    : 'hover:bg-gray-700/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${getPriorityColor(message.priority)}`}>
                        {message.priority.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-400">
                        {getChannelIcon(message.channel_type)} {message.channel_type}
                      </span>
                    </div>
                    <h4 className="font-medium">{message.title}</h4>
                    <p className="text-sm text-gray-400 mt-1">{message.summary}</p>
                  </div>
                  <span className="text-xs text-gray-500">{formatTime(message.created_at)}</span>
                </div>
                <div className="mt-2 flex items-center space-x-2">
                  <span className="text-xs text-gray-500">{message.source_agency_name}</span>
                  <span className="text-xs text-gray-600">|</span>
                  {message.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="text-xs bg-gray-700 px-2 py-0.5 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="col-span-4">
        {selectedMessage ? (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="flex items-center justify-between mb-4">
              <span className={`text-sm px-3 py-1 rounded ${getPriorityColor(selectedMessage.priority)}`}>
                {selectedMessage.priority.toUpperCase()}
              </span>
              <button
                onClick={() => setSelectedMessage(null)}
                className="text-gray-400 hover:text-white"
              >
                Close
              </button>
            </div>

            <h3 className="text-xl font-semibold mb-2">{selectedMessage.title}</h3>
            
            <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
              <span>{selectedMessage.source_agency_name}</span>
              <span>|</span>
              <span>{formatTime(selectedMessage.created_at)}</span>
            </div>

            <div className="bg-gray-700/50 rounded p-4 mb-4">
              <p className="whitespace-pre-wrap">{selectedMessage.content}</p>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-400">Jurisdictions:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {selectedMessage.jurisdiction_codes.map((code) => (
                    <span key={code} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                      {code}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-sm text-gray-400">Tags:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {selectedMessage.tags.map((tag) => (
                    <span key={tag} className="text-xs bg-gray-700 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex space-x-3">
              <button className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm">
                Acknowledge
              </button>
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
                Forward
              </button>
              <button className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm">
                Add Note
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
            <div className="text-4xl mb-4">📡</div>
            <h3 className="text-lg font-medium mb-2">Select a Message</h3>
            <p className="text-gray-400 text-sm">
              Click on a message from the feed to view details
            </p>
          </div>
        )}

        <div className="bg-gray-800 rounded-lg border border-gray-700 mt-4 p-4">
          <h4 className="font-medium mb-3">Cross-Agency BOLO Board</h4>
          <div className="space-y-2">
            {messages.filter(m => m.channel_type === 'bolos').slice(0, 3).map((bolo) => (
              <div key={bolo.message_id} className="bg-gray-700/50 rounded p-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{bolo.title}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${getPriorityColor(bolo.priority)}`}>
                    {bolo.priority}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">{bolo.source_agency_name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
