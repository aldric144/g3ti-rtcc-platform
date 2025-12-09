'use client';

/**
 * G3TI RTCC-UIP MDT Dispatch Viewer Component
 * Displays CAD calls list and assigned calls for MDT interface
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Radio,
  MapPin,
  Clock,
  AlertTriangle,
  Users,
  ChevronRight,
} from 'lucide-react';

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

interface MDTDispatchViewerProps {
  activeCalls: CADCall[];
  assignedCalls: CADCall[];
  onCallSelect: (call: CADCall) => void;
  selectedCallId?: string;
}

const priorityColors: Record<number, string> = {
  1: 'bg-red-600',
  2: 'bg-orange-500',
  3: 'bg-yellow-500',
  4: 'bg-blue-500',
  5: 'bg-gray-500',
};

const priorityLabels: Record<number, string> = {
  1: 'EMERGENCY',
  2: 'URGENT',
  3: 'ROUTINE',
  4: 'LOW',
  5: 'INFO',
};

export function MDTDispatchViewer({
  activeCalls,
  assignedCalls,
  onCallSelect,
  selectedCallId,
}: MDTDispatchViewerProps) {
  const [showAllCalls, setShowAllCalls] = useState(false);

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const CallCard = ({ call, isAssigned }: { call: CADCall; isAssigned: boolean }) => (
    <div
      className={`p-3 rounded-lg cursor-pointer transition-colors ${
        selectedCallId === call.id
          ? 'bg-blue-900/50 border border-blue-500'
          : 'bg-gray-800 hover:bg-gray-700'
      } ${isAssigned ? 'border-l-4 border-l-blue-500' : ''}`}
      onClick={() => onCallSelect(call)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Badge className={`${priorityColors[call.priority]} text-white text-xs`}>
            P{call.priority}
          </Badge>
          <span className="text-white font-medium">{call.call_number}</span>
        </div>
        <span className="text-gray-400 text-sm">{formatTime(call.created_at)}</span>
      </div>

      <div className="text-white font-semibold mb-1">{call.call_type}</div>

      <div className="flex items-center gap-1 text-gray-300 text-sm mb-2">
        <MapPin className="h-3 w-3" />
        <span className="truncate">{call.location}</span>
      </div>

      {call.description && (
        <p className="text-gray-400 text-sm mb-2 line-clamp-2">{call.description}</p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 text-gray-400 text-sm">
          <Users className="h-3 w-3" />
          <span>{call.assigned_units.length} units</span>
        </div>
        <Badge variant="outline" className="text-xs">
          {call.status}
        </Badge>
      </div>

      {call.hazards.length > 0 && (
        <div className="flex items-center gap-1 mt-2 text-red-400 text-sm">
          <AlertTriangle className="h-3 w-3" />
          <span>{call.hazards.join(', ')}</span>
        </div>
      )}
    </div>
  );

  return (
    <Card className="bg-gray-900 border-gray-700 h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-white flex items-center gap-2">
          <Radio className="h-5 w-5 text-blue-400" />
          Dispatch
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {/* Assigned Calls Section */}
        {assignedCalls.length > 0 && (
          <div className="px-4 pb-2">
            <div className="text-sm font-medium text-blue-400 mb-2 flex items-center gap-1">
              <ChevronRight className="h-4 w-4" />
              My Assigned Calls ({assignedCalls.length})
            </div>
            <div className="space-y-2">
              {assignedCalls.map((call) => (
                <CallCard key={call.id} call={call} isAssigned />
              ))}
            </div>
          </div>
        )}

        {/* All Active Calls Section */}
        <div className="px-4 py-2 border-t border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-400">
              All Active Calls ({activeCalls.length})
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllCalls(!showAllCalls)}
              className="text-gray-400 hover:text-white"
            >
              {showAllCalls ? 'Collapse' : 'Expand'}
            </Button>
          </div>

          {showAllCalls && (
            <ScrollArea className="h-[300px]">
              <div className="space-y-2 pr-4">
                {activeCalls.map((call) => (
                  <CallCard
                    key={call.id}
                    call={call}
                    isAssigned={assignedCalls.some((c) => c.id === call.id)}
                  />
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
