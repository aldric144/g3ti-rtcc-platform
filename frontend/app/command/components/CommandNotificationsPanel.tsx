'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface CommandNotificationsPanelProps {
  incidentId: string | null;
}

interface Notification {
  id: string;
  type: 'alert' | 'update' | 'message' | 'system';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  source: string;
  timestamp: string;
  read: boolean;
}

export function CommandNotificationsPanel({ incidentId }: CommandNotificationsPanelProps) {
  const [filter, setFilter] = useState<string>('all');
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: 'notif-001',
      type: 'alert',
      priority: 'critical',
      title: 'Gunfire Detected',
      message: 'ShotSpotter detected 3 rounds fired at incident location',
      source: 'ShotSpotter',
      timestamp: '2024-01-15T14:42:00Z',
      read: false,
    },
    {
      id: 'notif-002',
      type: 'update',
      priority: 'high',
      title: 'SWAT Team Arrived',
      message: 'SWAT-01 and SWAT-02 are now on scene',
      source: 'CAD',
      timestamp: '2024-01-15T14:40:00Z',
      read: false,
    },
    {
      id: 'notif-003',
      type: 'message',
      priority: 'medium',
      title: 'Message from IC',
      message: 'All units hold perimeter. Entry team staging at south entrance.',
      source: 'Captain Rodriguez',
      timestamp: '2024-01-15T14:38:00Z',
      read: true,
    },
    {
      id: 'notif-004',
      type: 'update',
      priority: 'high',
      title: 'Perimeter Established',
      message: 'Outer perimeter established on Peachtree St',
      source: 'Tactical',
      timestamp: '2024-01-15T14:35:00Z',
      read: true,
    },
    {
      id: 'notif-005',
      type: 'system',
      priority: 'low',
      title: 'ICS Role Assigned',
      message: 'Safety Officer role assigned to Officer Davis',
      source: 'System',
      timestamp: '2024-01-15T14:33:00Z',
      read: true,
    },
    {
      id: 'notif-006',
      type: 'alert',
      priority: 'high',
      title: 'Officer Safety Alert',
      message: 'High-risk location detected near Alpha-11 position',
      source: 'Officer Safety',
      timestamp: '2024-01-15T14:30:00Z',
      read: true,
    },
  ]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'alert': return '🚨';
      case 'update': return '📢';
      case 'message': return '💬';
      case 'system': return '⚙️';
      default: return '📌';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'border-l-red-500 bg-red-900/20';
      case 'high': return 'border-l-orange-500 bg-orange-900/10';
      case 'medium': return 'border-l-yellow-500 bg-yellow-900/10';
      case 'low': return 'border-l-gray-500';
      default: return 'border-l-gray-500';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const markAsRead = (notifId: string) => {
    setNotifications(prev => prev.map(n =>
      n.id === notifId ? { ...n, read: true } : n
    ));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    return n.type === filter;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="h-full flex flex-col">
      <CardHeader className="pb-2 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white text-sm flex items-center gap-2">
            Notifications
            {unreadCount > 0 && (
              <Badge className="bg-red-500">{unreadCount}</Badge>
            )}
          </CardTitle>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={markAllAsRead}
              className="text-xs text-gray-400 hover:text-white"
            >
              Mark all read
            </Button>
          )}
        </div>
      </CardHeader>

      {/* Filters */}
      <div className="p-2 border-b border-gray-700">
        <div className="flex gap-1 flex-wrap">
          {[
            { id: 'all', label: 'All' },
            { id: 'unread', label: 'Unread' },
            { id: 'alert', label: 'Alerts' },
            { id: 'update', label: 'Updates' },
            { id: 'message', label: 'Messages' },
          ].map(f => (
            <Button
              key={f.id}
              variant={filter === f.id ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setFilter(f.id)}
              className={`text-xs ${filter === f.id ? 'bg-blue-600' : ''}`}
            >
              {f.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Notifications List */}
      <CardContent className="flex-1 overflow-y-auto p-2 space-y-2">
        {filteredNotifications.map(notification => (
          <div
            key={notification.id}
            onClick={() => markAsRead(notification.id)}
            className={`p-3 rounded-lg border-l-4 cursor-pointer transition-colors ${
              getPriorityColor(notification.priority)
            } ${notification.read ? 'opacity-60' : ''} hover:opacity-100`}
          >
            <div className="flex items-start gap-2">
              <span className="text-lg">{getTypeIcon(notification.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h4 className={`text-sm font-medium ${notification.read ? 'text-gray-400' : 'text-white'}`}>
                    {notification.title}
                  </h4>
                  {!notification.read && (
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                  )}
                </div>
                <p className="text-xs text-gray-400 line-clamp-2">{notification.message}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">{notification.source}</span>
                  <span className="text-xs text-gray-500">{formatTime(notification.timestamp)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredNotifications.length === 0 && (
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500 text-sm">No notifications</p>
          </div>
        )}
      </CardContent>

      {/* Quick Actions */}
      <div className="p-2 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" className="text-xs">
            Send Alert
          </Button>
          <Button variant="outline" size="sm" className="text-xs">
            Broadcast
          </Button>
        </div>
      </div>
    </div>
  );
}
