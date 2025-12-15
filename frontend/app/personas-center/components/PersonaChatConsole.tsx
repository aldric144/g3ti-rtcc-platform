"use client";

import React, { useState, useEffect, useRef } from "react";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
  role: string;
  status: string;
  emotional_state: string;
  compliance_score: number;
  metrics: {
    total_interactions: number;
    successful_interactions: number;
    average_response_time_ms: number;
    missions_completed: number;
    missions_failed: number;
  };
}

interface ChatMessage {
  id: string;
  sender: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
  emotionalTone?: string;
  confidence?: number;
  actionItems?: Array<{ action: string; description: string }>;
  followUpQuestions?: string[];
  escalationRequired?: boolean;
  escalationReason?: string;
}

interface PersonaChatConsoleProps {
  persona: Persona | null;
  onPersonaSelect: (persona: Persona) => void;
}

export default function PersonaChatConsole({
  persona,
  onPersonaSelect,
}: PersonaChatConsoleProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (persona) {
      setMessages([]);
      setSessionId(null);
      addSystemMessage(`Connected to ${persona.name}. How can I assist you?`);
    }
  }, [persona?.persona_id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addSystemMessage = (content: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      sender: persona?.name || "System",
      content,
      timestamp: new Date(),
      isUser: false,
    };
    setMessages((prev) => [...prev, message]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !persona || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: "You",
      content: inputValue,
      timestamp: new Date(),
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch(`/api/personas/${persona.persona_id}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputValue,
          user_id: "rtcc_operator",
          interaction_type: "rtcc_console",
          session_id: sessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);

        const botMessage: ChatMessage = {
          id: data.response_id,
          sender: persona.name,
          content: data.content,
          timestamp: new Date(),
          isUser: false,
          emotionalTone: data.emotional_tone,
          confidence: data.confidence,
          actionItems: data.action_items,
          followUpQuestions: data.follow_up_questions,
          escalationRequired: data.escalation_required,
          escalationReason: data.escalation_reason,
        };

        setMessages((prev) => [...prev, botMessage]);
      } else {
        addSystemMessage("Failed to get response. Please try again.");
      }
    } catch (error) {
      console.error("Chat error:", error);
      addSystemMessage("Connection error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!persona) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="text-6xl mb-4">💬</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            Select a Persona
          </h3>
          <p className="text-gray-500">
            Choose an Apex AI Officer from the list to start a conversation
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-xl">
              {persona.persona_type === "apex_patrol" && "🚔"}
              {persona.persona_type === "apex_command" && "⭐"}
              {persona.persona_type === "apex_intel" && "🔍"}
              {persona.persona_type === "apex_crisis" && "🤝"}
              {persona.persona_type === "apex_robotics" && "🤖"}
              {persona.persona_type === "apex_investigations" && "🔎"}
            </div>
            <div>
              <h3 className="font-semibold text-white">{persona.name}</h3>
              <p className="text-xs text-gray-400">{persona.role}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`px-2 py-1 rounded text-xs ${
                persona.status === "active"
                  ? "bg-green-600 text-green-100"
                  : "bg-gray-600 text-gray-300"
              }`}
            >
              {persona.status}
            </span>
            <span className="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100 capitalize">
              {persona.emotional_state}
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.isUser
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-100"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium opacity-75">
                  {message.sender}
                </span>
                <span className="text-xs opacity-50">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <p className="whitespace-pre-wrap">{message.content}</p>

              {!message.isUser && message.confidence !== undefined && (
                <div className="mt-2 pt-2 border-t border-gray-600">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">
                      Confidence: {(message.confidence * 100).toFixed(0)}%
                    </span>
                    {message.emotionalTone && (
                      <span className="text-gray-400 capitalize">
                        Tone: {message.emotionalTone}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {message.escalationRequired && (
                <div className="mt-2 p-2 bg-red-900/50 rounded border border-red-700">
                  <div className="flex items-center space-x-2 text-red-300 text-xs">
                    <span>⚠️</span>
                    <span>Escalation Required: {message.escalationReason}</span>
                  </div>
                </div>
              )}

              {message.actionItems && message.actionItems.length > 0 && (
                <div className="mt-2 space-y-1">
                  <span className="text-xs text-gray-400">Action Items:</span>
                  {message.actionItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="text-xs bg-gray-800 rounded p-2"
                    >
                      <span className="font-medium">{item.action}:</span>{" "}
                      {item.description}
                    </div>
                  ))}
                </div>
              )}

              {message.followUpQuestions && message.followUpQuestions.length > 0 && (
                <div className="mt-2 space-y-1">
                  <span className="text-xs text-gray-400">Follow-up:</span>
                  {message.followUpQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputValue(q)}
                      className="block w-full text-left text-xs bg-gray-800 hover:bg-gray-750 rounded p-2 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Message ${persona.name}...`}
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            Send
          </button>
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {sessionId && <span>Session: {sessionId.slice(0, 8)}...</span>}
        </div>
      </div>
    </div>
  );
}
