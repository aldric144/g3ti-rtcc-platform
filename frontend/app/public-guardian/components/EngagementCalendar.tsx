"use client";

import React, { useState, useEffect } from "react";

interface CalendarEvent {
  id: string;
  title: string;
  date: Date;
  type: string;
}

export default function EngagementCalendar() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);

  useEffect(() => {
    const now = new Date();
    setEvents([
      { id: "1", title: "Town Hall", date: new Date(now.getFullYear(), now.getMonth(), 15), type: "town_hall" },
      { id: "2", title: "Coffee with Cops", date: new Date(now.getFullYear(), now.getMonth(), 8), type: "coffee_with_cops" },
      { id: "3", title: "Advisory Board", date: new Date(now.getFullYear(), now.getMonth(), 22), type: "advisory_board" },
      { id: "4", title: "Youth Program", date: new Date(now.getFullYear(), now.getMonth(), 18), type: "youth_program" },
      { id: "5", title: "Safety Workshop", date: new Date(now.getFullYear(), now.getMonth(), 25), type: "safety_workshop" },
    ]);
  }, []);

  const getDaysInMonth = (date: Date): number => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date): number => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getEventTypeColor = (type: string): string => {
    switch (type) {
      case "town_hall":
        return "bg-blue-500";
      case "coffee_with_cops":
        return "bg-yellow-500";
      case "advisory_board":
        return "bg-purple-500";
      case "youth_program":
        return "bg-green-500";
      case "safety_workshop":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const daysInMonth = getDaysInMonth(currentMonth);
  const firstDay = getFirstDayOfMonth(currentMonth);
  const monthName = currentMonth.toLocaleDateString("en-US", { month: "long", year: "numeric" });

  const days = [];
  for (let i = 0; i < firstDay; i++) {
    days.push(<div key={`empty-${i}`} className="h-24 bg-gray-50"></div>);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dayEvents = events.filter(
      (e) =>
        e.date.getDate() === day &&
        e.date.getMonth() === currentMonth.getMonth() &&
        e.date.getFullYear() === currentMonth.getFullYear()
    );

    const isToday =
      day === new Date().getDate() &&
      currentMonth.getMonth() === new Date().getMonth() &&
      currentMonth.getFullYear() === new Date().getFullYear();

    days.push(
      <div
        key={day}
        className={`h-24 border border-gray-100 p-1 ${isToday ? "bg-blue-50" : "bg-white"}`}
      >
        <div className={`text-sm font-medium ${isToday ? "text-blue-600" : "text-gray-700"}`}>
          {day}
        </div>
        <div className="mt-1 space-y-1">
          {dayEvents.slice(0, 2).map((event) => (
            <div
              key={event.id}
              className={`${getEventTypeColor(event.type)} text-white text-xs px-1 py-0.5 rounded truncate`}
              title={event.title}
            >
              {event.title}
            </div>
          ))}
          {dayEvents.length > 2 && (
            <div className="text-xs text-gray-500">+{dayEvents.length - 2} more</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Engagement Calendar</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={prevMonth}
            className="p-1 hover:bg-gray-100 rounded"
          >
            ←
          </button>
          <span className="text-sm font-medium text-gray-700 w-32 text-center">
            {monthName}
          </span>
          <button
            onClick={nextMonth}
            className="p-1 hover:bg-gray-100 rounded"
          >
            →
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-0">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            className="h-8 flex items-center justify-center text-xs font-medium text-gray-500 bg-gray-50"
          >
            {day}
          </div>
        ))}
        {days}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-blue-500 rounded mr-1"></div>
          <span>Town Hall</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-yellow-500 rounded mr-1"></div>
          <span>Coffee with Cops</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-purple-500 rounded mr-1"></div>
          <span>Advisory Board</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
          <span>Youth Program</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
          <span>Safety Workshop</span>
        </div>
      </div>
    </div>
  );
}
