'use client';

/**
 * G3TI RTCC-UIP MDT Messaging Pane Component
 * Handles RTCC to Officer and Officer to RTCC messaging
 */

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare, Send, Radio } from 'lucide-react';

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

interface MDTMessagingPaneProps {
  messages: Message[];
  currentBadge: string;
  onSendMessage: (content: string) => void;
  onMarkRead: (messageId: string) => void;
}

export function MDTMessagingPane({
  messages,
  currentBadge,
  onSendMessage,
  onMarkRead,
}: MDTMessagingPaneProps) {
  const [newMessage, setNewMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (newMessage.trim()) {
      onSendMessage(newMessage.trim());
      setNewMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-600',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-blue-500',
    info: 'bg-gray-500',
  };

  return (
    <Card className="bg-gray-900 border-gray-700 h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="text-white flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-blue-400" />
          Messages
          {messages.filter((m) => !m.read).length > 0 && (
            <Badge className="bg-red-600 text-white">
              {messages.filter((m) => !m.read).length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages List */}
        <ScrollArea className="flex-1 px-4" ref={scrollRef}>
          <div className="space-y-3 py-2">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No messages yet</p>
              </div>
            ) : (
              messages.map((message) => {
                const isOwn = message.sender_badge === currentBadge;
                return (
                  <div
                    key={message.id}
                    className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                    onClick={() => !message.read && onMarkRead(message.id)}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        isOwn
                          ? 'bg-blue-600 text-white'
                          : message.is_rtcc
                          ? 'bg-purple-900 text-white border border-purple-500'
                          : 'bg-gray-700 text-white'
                      }`}
                    >
                      {!isOwn && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium opacity-80">
                            {message.sender_name}
                          </span>
                          {message.is_rtcc && (
                            <Badge className="bg-purple-600 text-white text-xs py-0">
                              <Radio className="h-3 w-3 mr-1" />
                              RTCC
                            </Badge>
                          )}
                          {message.priority !== 'medium' && (
                            <Badge
                              className={`${
                                priorityColors[message.priority]
                              } text-white text-xs py-0`}
                            >
                              {message.priority.toUpperCase()}
                            </Badge>
                          )}
                        </div>
                      )}
                      <p className="text-sm">{message.content}</p>
                      <div
                        className={`text-xs mt-1 ${
                          isOwn ? 'text-blue-200' : 'text-gray-400'
                        }`}
                      >
                        {formatTime(message.created_at)}
                        {!message.read && !isOwn && (
                          <span className="ml-2 text-yellow-400">New</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>

        {/* Message Input */}
        <div className="p-4 border-t border-gray-700 flex-shrink-0">
          <div className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message to RTCC..."
              className="flex-1 bg-gray-800 border-gray-600 text-white placeholder:text-gray-500"
            />
            <Button
              onClick={handleSend}
              disabled={!newMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
