"use client";

import React, { useState, useEffect } from "react";

interface CommunityEvent {
  event_id: string;
  name: string;
  event_type: string;
  description: string;
  location: string;
  address: string;
  start_time: string;
  end_time: string | null;
  status: string;
  expected_attendance: number;
  target_neighborhoods: string[];
}

export default function EventsList() {
  const [events, setEvents] = useState<CommunityEvent[]>([]);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    const now = new Date();
    setEvents([
      {
        event_id: "1",
        name: "Monthly Town Hall Meeting",
        event_type: "town_hall",
        description: "Monthly community town hall to discuss public safety concerns and initiatives.",
        location: "Riviera Beach City Hall",
        address: "600 W Blue Heron Blvd, Riviera Beach, FL 33404",
        start_time: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        end_time: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
        status: "scheduled",
        expected_attendance: 100,
        target_neighborhoods: ["Downtown Riviera Beach", "West Riviera Beach"],
      },
      {
        event_id: "2",
        name: "Police Advisory Board Meeting",
        event_type: "advisory_board",
        description: "Quarterly meeting of the Police Advisory Board.",
        location: "RBPD Headquarters",
        address: "600 W Blue Heron Blvd, Riviera Beach, FL 33404",
        start_time: new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        end_time: new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
        status: "scheduled",
        expected_attendance: 50,
        target_neighborhoods: [],
      },
      {
        event_id: "3",
        name: "Coffee with Cops",
        event_type: "coffee_with_cops",
        description: "Informal community engagement event at local coffee shop.",
        location: "Starbucks - Singer Island",
        address: "2401 PGA Blvd, Palm Beach Gardens, FL 33410",
        start_time: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        end_time: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
        status: "confirmed",
        expected_attendance: 30,
        target_neighborhoods: ["Singer Island"],
      },
    ]);
  }, []);

  const getEventTypeIcon = (type: string): string => {
    switch (type) {
      case "town_hall":
        return "🏛️";
      case "advisory_board":
        return "📋";
      case "coffee_with_cops":
        return "☕";
      case "community_meeting":
        return "👥";
      case "safety_workshop":
        return "🛡️";
      case "youth_program":
        return "🎓";
      default:
        return "📅";
    }
  };

  const getStatusBadge = (status: string): { bg: string; text: string } => {
    switch (status) {
      case "confirmed":
        return { bg: "bg-green-100", text: "text-green-800" };
      case "scheduled":
        return { bg: "bg-blue-100", text: "text-blue-800" };
      case "cancelled":
        return { bg: "bg-red-100", text: "text-red-800" };
      default:
        return { bg: "bg-gray-100", text: "text-gray-800" };
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const filteredEvents = filter === "all" 
    ? events 
    : events.filter((e) => e.event_type === filter);

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Upcoming Events</h3>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-sm border rounded-md px-2 py-1"
        >
          <option value="all">All Events</option>
          <option value="town_hall">Town Halls</option>
          <option value="advisory_board">Advisory Board</option>
          <option value="coffee_with_cops">Coffee with Cops</option>
        </select>
      </div>

      <div className="space-y-4">
        {filteredEvents.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No upcoming events</p>
        ) : (
          filteredEvents.map((event) => {
            const statusStyle = getStatusBadge(event.status);
            return (
              <div
                key={event.event_id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">{getEventTypeIcon(event.event_type)}</span>
                    <div>
                      <h4 className="font-medium text-gray-900">{event.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${statusStyle.bg} ${statusStyle.text}`}>
                    {event.status}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <span className="mr-2">📍</span>
                    {event.location}
                  </div>
                  <div className="flex items-center text-gray-600">
                    <span className="mr-2">🕐</span>
                    {formatDate(event.start_time)}
                  </div>
                  <div className="flex items-center text-gray-600">
                    <span className="mr-2">👥</span>
                    Expected: {event.expected_attendance}
                  </div>
                  {event.target_neighborhoods.length > 0 && (
                    <div className="flex items-center text-gray-600">
                      <span className="mr-2">🏘️</span>
                      {event.target_neighborhoods.join(", ")}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
