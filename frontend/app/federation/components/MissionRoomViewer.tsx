"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";

interface MissionRoom {
  id: string;
  name: string;
  type: string;
  status: string;
  leadAgency: string;
  participatingAgencies: string[];
  participantCount: number;
  messageCount: number;
  createdAt: string;
}

interface MissionMessage {
  id: string;
  senderAgency: string;
  senderName: string;
  content: string;
  type: string;
  priority: string;
  createdAt: string;
}

export function MissionRoomViewer() {
  const [missions, setMissions] = useState<MissionRoom[]>([]);
  const [selectedMission, setSelectedMission] = useState<MissionRoom | null>(null);
  const [messages, setMessages] = useState<MissionMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMissions();
  }, []);

  const fetchMissions = async () => {
    try {
      setLoading(true);
      // Simulated data
      const mockMissions: MissionRoom[] = [
        {
          id: "mission-1",
          name: "Operation Crossroads",
          type: "joint_operation",
          status: "active",
          leadAgency: "Local PD",
          participatingAgencies: ["County Sheriff", "State Fusion Center", "DEA"],
          participantCount: 12,
          messageCount: 45,
          createdAt: "2024-12-01T10:00:00Z",
        },
        {
          id: "mission-2",
          name: "Regional Gang Task Force",
          type: "task_force",
          status: "active",
          leadAgency: "Regional Task Force",
          participatingAgencies: ["Local PD", "County Sheriff", "FBI"],
          participantCount: 8,
          messageCount: 128,
          createdAt: "2024-11-15T08:00:00Z",
        },
        {
          id: "mission-3",
          name: "Special Event - City Marathon",
          type: "special_event",
          status: "planning",
          leadAgency: "Local PD",
          participatingAgencies: ["Transit Police", "Fire Department", "EMS"],
          participantCount: 5,
          messageCount: 23,
          createdAt: "2024-12-05T14:00:00Z",
        },
      ];
      setMissions(mockMissions);
    } catch (error) {
      console.error("Failed to fetch missions:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (missionId: string) => {
    // Simulated messages
    const mockMessages: MissionMessage[] = [
      {
        id: "msg-1",
        senderAgency: "Local PD",
        senderName: "Sgt. Johnson",
        content: "All units, we have confirmed intel on the target location.",
        type: "announcement",
        priority: "high",
        createdAt: "2024-12-09T18:30:00Z",
      },
      {
        id: "msg-2",
        senderAgency: "County Sheriff",
        senderName: "Deputy Martinez",
        content: "Sheriff units are in position on the north perimeter.",
        type: "chat",
        priority: "normal",
        createdAt: "2024-12-09T18:32:00Z",
      },
      {
        id: "msg-3",
        senderAgency: "State Fusion Center",
        senderName: "Analyst Chen",
        content: "Updated threat assessment uploaded to shared files.",
        type: "intel_share",
        priority: "normal",
        createdAt: "2024-12-09T18:35:00Z",
      },
      {
        id: "msg-4",
        senderAgency: "System",
        senderName: "System",
        content: "DEA team has joined the mission room.",
        type: "system",
        priority: "normal",
        createdAt: "2024-12-09T18:40:00Z",
      },
    ];
    setMessages(mockMessages);
  };

  const handleSelectMission = (mission: MissionRoom) => {
    setSelectedMission(mission);
    fetchMessages(mission.id);
  };

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedMission) return;

    const message: MissionMessage = {
      id: `msg-${Date.now()}`,
      senderAgency: "Local PD",
      senderName: "Current User",
      content: newMessage,
      type: "chat",
      priority: "normal",
      createdAt: new Date().toISOString(),
    };
    setMessages([...messages, message]);
    setNewMessage("");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "planning":
        return "bg-blue-500";
      case "standby":
        return "bg-yellow-500";
      case "closed":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "joint_operation":
        return "bg-purple-500";
      case "task_force":
        return "bg-indigo-500";
      case "special_event":
        return "bg-orange-500";
      case "emergency_response":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case "announcement":
        return "border-l-4 border-l-yellow-500";
      case "alert":
        return "border-l-4 border-l-red-500";
      case "intel_share":
        return "border-l-4 border-l-blue-500";
      case "system":
        return "border-l-4 border-l-gray-500 bg-muted/50";
      default:
        return "";
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Interagency Mission Rooms</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 h-[600px]">
          {/* Mission List */}
          <div className="col-span-1 border-r pr-4">
            <h3 className="font-semibold mb-3">Active Missions</h3>
            {loading ? (
              <div className="text-center py-4 text-muted-foreground">
                Loading missions...
              </div>
            ) : (
              <div className="space-y-2">
                {missions.map((mission) => (
                  <div
                    key={mission.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedMission?.id === mission.id
                        ? "bg-accent border-primary"
                        : "hover:bg-accent/50"
                    }`}
                    onClick={() => handleSelectMission(mission)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{mission.name}</span>
                      <Badge className={`${getStatusColor(mission.status)} text-xs`}>
                        {mission.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {mission.participantCount} participants
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {mission.messageCount} msgs
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <Button className="w-full mt-4" variant="outline">
              Create New Mission
            </Button>
          </div>

          {/* Mission Details & Chat */}
          <div className="col-span-2 flex flex-col">
            {selectedMission ? (
              <>
                {/* Mission Header */}
                <div className="pb-3 border-b mb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">{selectedMission.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        Lead: {selectedMission.leadAgency}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Badge className={getTypeColor(selectedMission.type)}>
                        {selectedMission.type.replace("_", " ")}
                      </Badge>
                      <Badge className={getStatusColor(selectedMission.status)}>
                        {selectedMission.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {selectedMission.participatingAgencies.map((agency) => (
                      <Badge key={agency} variant="outline" className="text-xs">
                        {agency}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-3 mb-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`p-3 rounded-lg ${getMessageTypeColor(message.type)}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">
                            {message.senderName}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {message.senderAgency}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(message.createdAt).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm">{message.content}</p>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="flex gap-2 pt-3 border-t">
                  <Input
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={handleSendMessage}>Send</Button>
                  <Button variant="outline">Share File</Button>
                  <Button variant="outline">Add Note</Button>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                Select a mission room to view details and chat
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
