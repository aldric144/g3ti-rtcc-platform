"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";

interface Notification {
  id: string;
  type: string;
  priority: string;
  title: string;
  content: string;
  senderAgency: string;
  createdAt: string;
  requiresAcknowledgment: boolean;
  acknowledged: boolean;
}

interface BOLO {
  id: string;
  type: string;
  priority: string;
  title: string;
  description: string;
  armedDangerous: boolean;
  targetAgencies: string[];
  createdAt: string;
  isActive: boolean;
}

export function FederatedNotificationsPanel() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [bolos, setBOLOs] = useState<BOLO[]>([]);
  const [activeTab, setActiveTab] = useState<"notifications" | "bolos">("notifications");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
    fetchBOLOs();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      // Simulated data
      const mockNotifications: Notification[] = [
        {
          id: "notif-1",
          type: "officer_safety",
          priority: "critical",
          title: "Officer Safety Alert - Armed Suspect",
          content: "Armed suspect last seen in the 400 block of Main St. Exercise extreme caution.",
          senderAgency: "County Sheriff",
          createdAt: "2024-12-09T18:45:00Z",
          requiresAcknowledgment: true,
          acknowledged: false,
        },
        {
          id: "notif-2",
          type: "intelligence_bulletin",
          priority: "high",
          title: "Intelligence Bulletin - Gang Activity",
          content: "Increased gang activity reported in the downtown area. Multiple agencies coordinating response.",
          senderAgency: "State Fusion Center",
          createdAt: "2024-12-09T17:30:00Z",
          requiresAcknowledgment: true,
          acknowledged: true,
        },
        {
          id: "notif-3",
          type: "incident_update",
          priority: "medium",
          title: "Major Incident Update - Highway Closure",
          content: "I-95 northbound closed at Exit 42 due to multi-vehicle accident. Expect delays.",
          senderAgency: "State Highway Patrol",
          createdAt: "2024-12-09T16:15:00Z",
          requiresAcknowledgment: false,
          acknowledged: false,
        },
        {
          id: "notif-4",
          type: "mutual_aid",
          priority: "high",
          title: "Mutual Aid Request - Structure Fire",
          content: "Requesting additional units for structure fire at 789 Industrial Blvd.",
          senderAgency: "Fire Department",
          createdAt: "2024-12-09T15:00:00Z",
          requiresAcknowledgment: true,
          acknowledged: true,
        },
      ];
      setNotifications(mockNotifications);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBOLOs = async () => {
    // Simulated BOLOs
    const mockBOLOs: BOLO[] = [
      {
        id: "bolo-1",
        type: "wanted_person",
        priority: "critical",
        title: "Wanted - Armed Robbery Suspect",
        description: "Male, 30s, 6ft, medium build, last seen wearing black hoodie and jeans. Armed with handgun.",
        armedDangerous: true,
        targetAgencies: ["All Agencies"],
        createdAt: "2024-12-09T14:00:00Z",
        isActive: true,
      },
      {
        id: "bolo-2",
        type: "stolen_vehicle",
        priority: "high",
        title: "Stolen Vehicle - Blue Honda Accord",
        description: "2020 Blue Honda Accord, plate ABC-1234. Taken during carjacking, suspect may still be in vehicle.",
        armedDangerous: false,
        targetAgencies: ["Local PD", "County Sheriff", "State Highway Patrol"],
        createdAt: "2024-12-09T12:30:00Z",
        isActive: true,
      },
      {
        id: "bolo-3",
        type: "missing_person",
        priority: "high",
        title: "Missing Person - Elderly Male",
        description: "John Smith, 78, suffering from dementia. Last seen at 123 Oak St wearing blue jacket.",
        armedDangerous: false,
        targetAgencies: ["All Agencies"],
        createdAt: "2024-12-09T10:00:00Z",
        isActive: true,
      },
    ];
    setBOLOs(mockBOLOs);
  };

  const handleAcknowledge = (notificationId: string) => {
    setNotifications((prev) =>
      prev.map((n) =>
        n.id === notificationId ? { ...n, acknowledged: true } : n
      )
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "officer_safety":
        return "bg-red-600";
      case "intelligence_bulletin":
        return "bg-purple-500";
      case "incident_update":
        return "bg-blue-500";
      case "mutual_aid":
        return "bg-green-500";
      case "bolo_broadcast":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const unacknowledgedCount = notifications.filter(
    (n) => n.requiresAcknowledgment && !n.acknowledged
  ).length;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Multi-Agency Notifications</span>
          {unacknowledgedCount > 0 && (
            <Badge className="bg-red-500">{unacknowledgedCount} pending</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Tabs */}
          <div className="flex gap-2 border-b pb-2">
            <Button
              variant={activeTab === "notifications" ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveTab("notifications")}
            >
              Notifications ({notifications.length})
            </Button>
            <Button
              variant={activeTab === "bolos" ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveTab("bolos")}
            >
              Active BOLOs ({bolos.filter((b) => b.isActive).length})
            </Button>
          </div>

          {/* Content */}
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading...
            </div>
          ) : activeTab === "notifications" ? (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border rounded-lg ${
                    notification.requiresAcknowledgment && !notification.acknowledged
                      ? "border-l-4 border-l-red-500"
                      : ""
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(notification.priority)}>
                        {notification.priority}
                      </Badge>
                      <Badge className={getTypeColor(notification.type)}>
                        {notification.type.replace("_", " ")}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(notification.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <h4 className="font-semibold mb-1">{notification.title}</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    {notification.content}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      From: {notification.senderAgency}
                    </span>
                    {notification.requiresAcknowledgment && (
                      <Button
                        size="sm"
                        variant={notification.acknowledged ? "outline" : "default"}
                        onClick={() => handleAcknowledge(notification.id)}
                        disabled={notification.acknowledged}
                      >
                        {notification.acknowledged ? "Acknowledged" : "Acknowledge"}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {bolos
                .filter((b) => b.isActive)
                .map((bolo) => (
                  <div
                    key={bolo.id}
                    className={`p-4 border rounded-lg ${
                      bolo.armedDangerous ? "border-l-4 border-l-red-500" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getPriorityColor(bolo.priority)}>
                          {bolo.priority}
                        </Badge>
                        <Badge variant="outline">{bolo.type.replace("_", " ")}</Badge>
                        {bolo.armedDangerous && (
                          <Badge className="bg-red-600">ARMED & DANGEROUS</Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {new Date(bolo.createdAt).toLocaleString()}
                      </span>
                    </div>
                    <h4 className="font-semibold mb-1">{bolo.title}</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      {bolo.description}
                    </p>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {bolo.targetAgencies.map((agency) => (
                        <Badge key={agency} variant="outline" className="text-xs">
                          {agency}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                      <Button size="sm" variant="outline">
                        Share
                      </Button>
                    </div>
                  </div>
                ))}
            </div>
          )}

          {/* Actions */}
          <div className="pt-4 border-t flex gap-2">
            <Button variant="outline" className="flex-1">
              Send Notification
            </Button>
            <Button variant="outline" className="flex-1">
              Broadcast BOLO
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
