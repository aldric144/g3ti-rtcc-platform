'use client';

/**
 * G3TI RTCC-UIP MDT (Mobile Data Terminal) Interface
 * Officer field access to dispatch, messaging, and safety information
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Monitor,
  Radio,
  Shield,
  MessageSquare,
  Settings,
  LogOut,
  Wifi,
  WifiOff,
  Battery,
  Clock,
} from 'lucide-react';

import {
  MDTDispatchViewer,
  MDTStatusPanel,
  MDTMessagingPane,
  MDTOfficerSafetyPanel,
  MDTActionButtons,
} from './components';

type UnitStatus =
  | 'available'
  | 'en_route'
  | 'on_scene'
  | 'transporting'
  | 'at_hospital'
  | 'reports'
  | 'out_of_service'
  | 'off_duty';

interface CADCall {
  id: string;
  call_number: string;
  call_type: string;
  priority: number;
  location: string;
  description?: string;
  assigned_units: string[];
  status: string;
  created_at: string;
  hazards: string[];
}

interface Message {
  id: string;
  sender_badge: string;
  sender_name: string;
  content: string;
  priority: string;
  created_at: string;
  is_rtcc: boolean;
  read: boolean;
}

interface OfficerSafetyStatus {
  badge_number: string;
  officer_name: string;
  threat_level: 'critical' | 'high' | 'elevated' | 'moderate' | 'low' | 'minimal';
  threat_score: number;
  active_warnings: string[];
  nearby_threats: number;
  in_hotzone: boolean;
  hotzone_name?: string;
  last_check_in?: string;
}

interface ProximityWarning {
  id: string;
  warning_type: string;
  title: string;
  description: string;
  threat_level: 'critical' | 'high' | 'elevated' | 'moderate' | 'low' | 'minimal';
  distance_meters: number;
  acknowledged: boolean;
}

export default function MDTPage() {
  const router = useRouter();
  const [isConnected, setIsConnected] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentStatus, setCurrentStatus] = useState<UnitStatus>('available');
  const [selectedCallId, setSelectedCallId] = useState<string | undefined>();

  // Mock data - in production, this would come from API/WebSocket
  const [activeCalls, setActiveCalls] = useState<CADCall[]>([
    {
      id: '1',
      call_number: 'CAD-2024-001234',
      call_type: 'Burglary in Progress',
      priority: 1,
      location: '123 Main St, Apt 4B',
      description: 'Caller reports unknown male attempting to break into apartment. Suspect wearing dark clothing.',
      assigned_units: ['A1', 'A2'],
      status: 'dispatched',
      created_at: new Date(Date.now() - 300000).toISOString(),
      hazards: ['Weapons', 'Prior Violence'],
    },
    {
      id: '2',
      call_number: 'CAD-2024-001235',
      call_type: 'Traffic Accident',
      priority: 3,
      location: 'Oak Ave & 5th St',
      description: 'Two vehicle accident, minor injuries reported.',
      assigned_units: ['B3'],
      status: 'en_route',
      created_at: new Date(Date.now() - 600000).toISOString(),
      hazards: [],
    },
    {
      id: '3',
      call_number: 'CAD-2024-001236',
      call_type: 'Suspicious Person',
      priority: 4,
      location: '500 Park Blvd',
      description: 'Male loitering near school entrance.',
      assigned_units: [],
      status: 'pending',
      created_at: new Date(Date.now() - 120000).toISOString(),
      hazards: [],
    },
  ]);

  const [assignedCalls, setAssignedCalls] = useState<CADCall[]>([activeCalls[0]]);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender_badge: 'RTCC',
      sender_name: 'RTCC Analyst',
      content: 'Be advised: suspect vehicle is a black Honda Accord, plate ABC-1234. Last seen heading northbound on Main St.',
      priority: 'high',
      created_at: new Date(Date.now() - 180000).toISOString(),
      is_rtcc: true,
      read: false,
    },
    {
      id: '2',
      sender_badge: '1234',
      sender_name: 'Officer Smith',
      content: 'Copy that, en route to intercept.',
      priority: 'medium',
      created_at: new Date(Date.now() - 120000).toISOString(),
      is_rtcc: false,
      read: true,
    },
  ]);

  const [safetyStatus, setSafetyStatus] = useState<OfficerSafetyStatus>({
    badge_number: '1234',
    officer_name: 'Officer Smith',
    threat_level: 'elevated',
    threat_score: 0.65,
    active_warnings: ['Known offender in area'],
    nearby_threats: 2,
    in_hotzone: false,
    last_check_in: new Date(Date.now() - 900000).toISOString(),
  });

  const [warnings, setWarnings] = useState<ProximityWarning[]>([
    {
      id: '1',
      warning_type: 'known_offender',
      title: 'Known Violent Offender',
      description: 'John Doe - Prior assault charges, known to carry weapons',
      threat_level: 'high',
      distance_meters: 150,
      acknowledged: false,
    },
  ]);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Handlers
  const handleStatusChange = (status: UnitStatus) => {
    setCurrentStatus(status);
    // In production, this would call the API
  };

  const handleCallSelect = (call: CADCall) => {
    setSelectedCallId(call.id);
  };

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender_badge: '1234',
      sender_name: 'Officer Smith',
      content,
      priority: 'medium',
      created_at: new Date().toISOString(),
      is_rtcc: false,
      read: true,
    };
    setMessages([...messages, newMessage]);
  };

  const handleMarkRead = (messageId: string) => {
    setMessages(
      messages.map((m) => (m.id === messageId ? { ...m, read: true } : m))
    );
  };

  const handleCheckIn = (type: string) => {
    setSafetyStatus({
      ...safetyStatus,
      last_check_in: new Date().toISOString(),
    });
  };

  const handleAcknowledgeWarning = (warningId: string) => {
    setWarnings(
      warnings.map((w) => (w.id === warningId ? { ...w, acknowledged: true } : w))
    );
  };

  const handleRequestBackup = () => {
    // In production, this would call the API
    alert('Backup request sent to dispatch');
  };

  const handleEmergency = () => {
    // In production, this would trigger emergency protocols
    alert('EMERGENCY ACTIVATED - Dispatch notified');
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-700 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Monitor className="h-6 w-6 text-blue-400" />
              <span className="font-bold text-lg">G3TI MDT</span>
            </div>
            <Badge className="bg-blue-600">Unit A1</Badge>
            <Badge variant="outline" className="text-gray-300">
              Badge #1234
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-400" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-400" />
              )}
              <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
                {isConnected ? 'Connected' : 'Offline'}
              </span>
            </div>

            {/* Battery */}
            <div className="flex items-center gap-1 text-gray-400">
              <Battery className="h-4 w-4" />
              <span className="text-sm">85%</span>
            </div>

            {/* Time */}
            <div className="flex items-center gap-1 text-gray-400">
              <Clock className="h-4 w-4" />
              <span className="text-sm font-mono">
                {currentTime.toLocaleTimeString()}
              </span>
            </div>

            {/* Settings */}
            <Button variant="ghost" size="sm" className="text-gray-400">
              <Settings className="h-4 w-4" />
            </Button>

            {/* Logout */}
            <Button
              variant="ghost"
              size="sm"
              className="text-gray-400"
              onClick={() => router.push('/login')}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-4">
        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-120px)]">
          {/* Left Column - Dispatch & Status */}
          <div className="col-span-4 space-y-4 overflow-auto">
            <MDTStatusPanel
              currentStatus={currentStatus}
              unitId="A1"
              badgeNumber="1234"
              officerName="Officer Smith"
              onStatusChange={handleStatusChange}
              lastUpdate={new Date().toISOString()}
            />
            <MDTDispatchViewer
              activeCalls={activeCalls}
              assignedCalls={assignedCalls}
              onCallSelect={handleCallSelect}
              selectedCallId={selectedCallId}
            />
          </div>

          {/* Center Column - Actions & Safety */}
          <div className="col-span-4 space-y-4 overflow-auto">
            <MDTActionButtons
              currentStatus={currentStatus}
              hasActiveCall={assignedCalls.length > 0}
              onStatusChange={handleStatusChange}
              onRequestBackup={handleRequestBackup}
              onEmergency={handleEmergency}
            />
            <MDTOfficerSafetyPanel
              safetyStatus={safetyStatus}
              warnings={warnings}
              onCheckIn={handleCheckIn}
              onAcknowledgeWarning={handleAcknowledgeWarning}
            />
          </div>

          {/* Right Column - Messaging */}
          <div className="col-span-4 h-full">
            <MDTMessagingPane
              messages={messages}
              currentBadge="1234"
              onSendMessage={handleSendMessage}
              onMarkRead={handleMarkRead}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
