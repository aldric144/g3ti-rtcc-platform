'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';

interface Message {
  id: string;
  sender_name: string;
  sender_type: string;
  content: string;
  message_type: string;
  timestamp: string;
  priority: string;
}

interface DispatchCall {
  id: string;
  cad_id: string;
  call_type: string;
  priority: string;
  address: string;
  status: string;
  units: string[];
  created_at: string;
}

interface Bulletin {
  id: string;
  title: string;
  summary: string;
  bulletin_type: string;
  priority: string;
  published_at: string;
}

interface Alert {
  id: string;
  title: string;
  body: string;
  alert_type: string;
  priority: string;
  timestamp: string;
  acknowledged: boolean;
}

interface TacticalCommsPanelProps {
  sceneId: string;
}

export function TacticalCommsPanel({ sceneId }: TacticalCommsPanelProps) {
  const [activeTab, setActiveTab] = useState('messages');
  const [messages, setMessages] = useState<Message[]>([]);
  const [dispatchCalls, setDispatchCalls] = useState<DispatchCall[]>([]);
  const [bulletins, setBulletins] = useState<Bulletin[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load mock data
  useEffect(() => {
    // Mock messages
    const mockMessages: Message[] = [
      { id: '1', sender_name: 'RTCC Analyst', sender_type: 'rtcc', content: 'Suspect vehicle spotted heading north on Peachtree', message_type: 'intel', timestamp: new Date(Date.now() - 300000).toISOString(), priority: 'high' },
      { id: '2', sender_name: 'Alpha-11', sender_type: 'patrol', content: 'Copy, en route to intercept', message_type: 'text', timestamp: new Date(Date.now() - 240000).toISOString(), priority: 'normal' },
      { id: '3', sender_name: 'Command', sender_type: 'command', content: 'All units maintain perimeter positions', message_type: 'text', timestamp: new Date(Date.now() - 180000).toISOString(), priority: 'normal' },
      { id: '4', sender_name: 'RTCC System', sender_type: 'system', content: 'LPR hit: Vehicle ABC123 flagged as stolen', message_type: 'alert', timestamp: new Date(Date.now() - 120000).toISOString(), priority: 'urgent' },
    ];

    // Mock dispatch calls
    const mockCalls: DispatchCall[] = [
      { id: '1', cad_id: 'CAD-2024-5678', call_type: 'Armed Robbery', priority: 'P1', address: '123 Main St', status: 'active', units: ['Alpha-11', 'Alpha-12'], created_at: new Date(Date.now() - 600000).toISOString() },
      { id: '2', cad_id: 'CAD-2024-5679', call_type: 'Suspicious Vehicle', priority: 'P2', address: '456 Oak Ave', status: 'dispatched', units: ['Bravo-21'], created_at: new Date(Date.now() - 300000).toISOString() },
    ];

    // Mock bulletins
    const mockBulletins: Bulletin[] = [
      { id: '1', title: 'High-Risk Vehicle Alert', summary: 'Black sedan ABC123 associated with armed robbery suspect', bulletin_type: 'high_risk_vehicle', priority: 'high', published_at: new Date(Date.now() - 900000).toISOString() },
      { id: '2', title: 'Tactical Zone Update', summary: 'Zone 3 elevated to high risk due to recent activity', bulletin_type: 'tactical_zone', priority: 'normal', published_at: new Date(Date.now() - 1800000).toISOString() },
    ];

    // Mock alerts
    const mockAlerts: Alert[] = [
      { id: '1', title: 'GUNFIRE DETECTED', body: '3 rounds at 789 Pine St, 200m from your position', alert_type: 'gunfire', priority: 'critical', timestamp: new Date(Date.now() - 60000).toISOString(), acknowledged: false },
      { id: '2', title: 'Officer Safety Alert', body: 'High-risk individual in vicinity', alert_type: 'officer_safety', priority: 'urgent', timestamp: new Date(Date.now() - 180000).toISOString(), acknowledged: true },
    ];

    setMessages(mockMessages);
    setDispatchCalls(mockCalls);
    setBulletins(mockBulletins);
    setAlerts(mockAlerts);
    setIsConnected(true);
  }, [sceneId]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    const message: Message = {
      id: Date.now().toString(),
      sender_name: 'You',
      sender_type: 'rtcc',
      content: newMessage,
      message_type: 'text',
      timestamp: new Date().toISOString(),
      priority: 'normal',
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const priorityColors = {
    low: 'bg-gray-500',
    normal: 'bg-blue-500',
    high: 'bg-orange-500',
    urgent: 'bg-red-500',
    critical: 'bg-red-600 animate-pulse',
  };

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white text-sm">Tactical Communications</CardTitle>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="w-full bg-gray-900 rounded-none">
            <TabsTrigger value="messages" className="flex-1 text-xs">
              Messages
              {messages.filter(m => m.priority === 'urgent' || m.priority === 'high').length > 0 && (
                <Badge className="ml-1 bg-red-500 text-xs px-1">
                  {messages.filter(m => m.priority === 'urgent' || m.priority === 'high').length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="dispatch" className="flex-1 text-xs">
              Dispatch
              <Badge className="ml-1 bg-blue-500 text-xs px-1">{dispatchCalls.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="bulletins" className="flex-1 text-xs">
              Bulletins
            </TabsTrigger>
            <TabsTrigger value="alerts" className="flex-1 text-xs">
              Alerts
              {alerts.filter(a => !a.acknowledged).length > 0 && (
                <Badge className="ml-1 bg-red-500 text-xs px-1">
                  {alerts.filter(a => !a.acknowledged).length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Messages Tab */}
          <TabsContent value="messages" className="m-0">
            <div className="h-64 overflow-y-auto p-3 space-y-2">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`p-2 rounded-lg ${
                    msg.sender_type === 'system' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                    msg.sender_type === 'rtcc' ? 'bg-blue-500/10' :
                    msg.sender_type === 'command' ? 'bg-purple-500/10' :
                    'bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-white">{msg.sender_name}</span>
                    <span className="text-xs text-gray-500">{formatTime(msg.timestamp)}</span>
                  </div>
                  <p className="text-sm text-gray-300">{msg.content}</p>
                  {msg.priority !== 'normal' && (
                    <Badge className={`mt-1 text-xs ${priorityColors[msg.priority as keyof typeof priorityColors]}`}>
                      {msg.priority.toUpperCase()}
                    </Badge>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="p-3 border-t border-gray-700">
              <div className="flex gap-2">
                <Input
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type message..."
                  className="flex-1 bg-gray-700 border-gray-600 text-white text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Send
                </Button>
              </div>
              <div className="flex gap-2 mt-2">
                <Button variant="outline" size="sm" className="text-xs flex-1">
                  Quick Intel
                </Button>
                <Button variant="outline" size="sm" className="text-xs flex-1">
                  Request Backup
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Dispatch Tab */}
          <TabsContent value="dispatch" className="m-0">
            <div className="h-80 overflow-y-auto p-3 space-y-2">
              {dispatchCalls.map(call => (
                <div
                  key={call.id}
                  className={`p-3 rounded-lg border ${
                    call.priority === 'P1' ? 'bg-red-500/10 border-red-500/30' :
                    call.priority === 'P2' ? 'bg-orange-500/10 border-orange-500/30' :
                    'bg-gray-700 border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={call.priority === 'P1' ? 'bg-red-500' : 'bg-orange-500'}>
                        {call.priority}
                      </Badge>
                      <span className="text-sm font-medium text-white">{call.call_type}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {call.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 mb-1">{call.cad_id}</p>
                  <p className="text-sm text-gray-300">{call.address}</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="text-xs text-gray-500">Units:</span>
                    {call.units.map(unit => (
                      <Badge key={unit} variant="secondary" className="text-xs">
                        {unit}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Bulletins Tab */}
          <TabsContent value="bulletins" className="m-0">
            <div className="h-80 overflow-y-auto p-3 space-y-2">
              {bulletins.map(bulletin => (
                <div
                  key={bulletin.id}
                  className={`p-3 rounded-lg border ${
                    bulletin.priority === 'high' ? 'bg-orange-500/10 border-orange-500/30' :
                    bulletin.priority === 'urgent' ? 'bg-red-500/10 border-red-500/30' :
                    'bg-gray-700 border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{bulletin.title}</span>
                    <Badge className={priorityColors[bulletin.priority as keyof typeof priorityColors]}>
                      {bulletin.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-300">{bulletin.summary}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {formatTime(bulletin.published_at)}
                  </p>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts" className="m-0">
            <div className="h-80 overflow-y-auto p-3 space-y-2">
              {alerts.map(alert => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border ${
                    alert.priority === 'critical' ? 'bg-red-600/20 border-red-500 animate-pulse' :
                    alert.priority === 'urgent' ? 'bg-red-500/10 border-red-500/30' :
                    'bg-gray-700 border-gray-600'
                  } ${alert.acknowledged ? 'opacity-60' : ''}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white">{alert.title}</span>
                    <div className="flex items-center gap-2">
                      <Badge className={priorityColors[alert.priority as keyof typeof priorityColors]}>
                        {alert.priority}
                      </Badge>
                      {alert.acknowledged && (
                        <Badge variant="outline" className="text-xs text-green-400 border-green-400">
                          ACK
                        </Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-300">{alert.body}</p>
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-xs text-gray-500">{formatTime(alert.timestamp)}</p>
                    {!alert.acknowledged && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs h-6"
                        onClick={() => {
                          setAlerts(prev =>
                            prev.map(a =>
                              a.id === alert.id ? { ...a, acknowledged: true } : a
                            )
                          );
                        }}
                      >
                        Acknowledge
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

export default TacticalCommsPanel;
