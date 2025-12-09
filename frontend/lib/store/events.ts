import { create } from 'zustand';
import { EventType, EventPriority, EventSource, RTCCEvent } from '@/shared/schemas/events';

/**
 * Event filter configuration.
 */
export interface EventFilter {
  eventTypes: EventType[];
  sources: EventSource[];
  priorities: EventPriority[];
  acknowledged: boolean | null;
  searchQuery: string;
}

/**
 * Event store state interface.
 */
interface EventState {
  events: RTCCEvent[];
  selectedEvent: RTCCEvent | null;
  filter: EventFilter;
  unreadCount: number;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  addEvent: (event: RTCCEvent) => void;
  updateEvent: (eventId: string, updates: Partial<RTCCEvent>) => void;
  removeEvent: (eventId: string) => void;
  selectEvent: (event: RTCCEvent | null) => void;
  acknowledgeEvent: (eventId: string) => void;
  setFilter: (filter: Partial<EventFilter>) => void;
  resetFilter: () => void;
  setConnected: (connected: boolean) => void;
  clearEvents: () => void;
  markAllRead: () => void;
}

/**
 * Default filter configuration.
 */
const defaultFilter: EventFilter = {
  eventTypes: [],
  sources: [],
  priorities: [],
  acknowledged: null,
  searchQuery: '',
};

/**
 * Event store using Zustand.
 */
export const useEventStore = create<EventState>((set, get) => ({
  events: [],
  selectedEvent: null,
  filter: defaultFilter,
  unreadCount: 0,
  isConnected: false,
  isLoading: false,
  error: null,

  /**
   * Add a new event to the store.
   */
  addEvent: (event: RTCCEvent) => {
    set((state) => ({
      events: [event, ...state.events].slice(0, 500), // Keep last 500 events
      unreadCount: event.acknowledged ? state.unreadCount : state.unreadCount + 1,
    }));
  },

  /**
   * Update an existing event.
   */
  updateEvent: (eventId: string, updates: Partial<RTCCEvent>) => {
    set((state) => ({
      events: state.events.map((event) =>
        event.id === eventId ? { ...event, ...updates } : event
      ),
      selectedEvent:
        state.selectedEvent?.id === eventId
          ? { ...state.selectedEvent, ...updates }
          : state.selectedEvent,
    }));
  },

  /**
   * Remove an event from the store.
   */
  removeEvent: (eventId: string) => {
    set((state) => ({
      events: state.events.filter((event) => event.id !== eventId),
      selectedEvent: state.selectedEvent?.id === eventId ? null : state.selectedEvent,
    }));
  },

  /**
   * Select an event for detail view.
   */
  selectEvent: (event: RTCCEvent | null) => {
    set({ selectedEvent: event });
  },

  /**
   * Acknowledge an event.
   */
  acknowledgeEvent: (eventId: string) => {
    const { events, unreadCount } = get();
    const event = events.find((e) => e.id === eventId);

    if (event && !event.acknowledged) {
      set((state) => ({
        events: state.events.map((e) =>
          e.id === eventId
            ? { ...e, acknowledged: true, acknowledgedAt: new Date().toISOString() }
            : e
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }));
    }
  },

  /**
   * Update filter configuration.
   */
  setFilter: (filter: Partial<EventFilter>) => {
    set((state) => ({
      filter: { ...state.filter, ...filter },
    }));
  },

  /**
   * Reset filter to defaults.
   */
  resetFilter: () => {
    set({ filter: defaultFilter });
  },

  /**
   * Set WebSocket connection status.
   */
  setConnected: (connected: boolean) => {
    set({ isConnected: connected });
  },

  /**
   * Clear all events.
   */
  clearEvents: () => {
    set({ events: [], unreadCount: 0, selectedEvent: null });
  },

  /**
   * Mark all events as read.
   */
  markAllRead: () => {
    set((state) => ({
      events: state.events.map((event) => ({ ...event, acknowledged: true })),
      unreadCount: 0,
    }));
  },
}));

/**
 * Get filtered events from the store.
 */
export function useFilteredEvents(): RTCCEvent[] {
  const { events, filter } = useEventStore();

  return events.filter((event) => {
    // Filter by event types
    if (filter.eventTypes.length > 0 && !filter.eventTypes.includes(event.eventType)) {
      return false;
    }

    // Filter by sources
    if (filter.sources.length > 0 && !filter.sources.includes(event.source)) {
      return false;
    }

    // Filter by priorities
    if (filter.priorities.length > 0 && !filter.priorities.includes(event.priority)) {
      return false;
    }

    // Filter by acknowledged status
    if (filter.acknowledged !== null && event.acknowledged !== filter.acknowledged) {
      return false;
    }

    // Filter by search query
    if (filter.searchQuery) {
      const query = filter.searchQuery.toLowerCase();
      const searchableText =
        `${event.title} ${event.description || ''} ${event.address || ''}`.toLowerCase();
      if (!searchableText.includes(query)) {
        return false;
      }
    }

    return true;
  });
}
