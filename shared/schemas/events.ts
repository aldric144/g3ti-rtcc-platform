/**
 * Event schemas for the G3TI RTCC-UIP Platform.
 */

import { GeoLocation } from './entities';

/**
 * Event type enumeration.
 */
export enum EventType {
  GUNSHOT = 'gunshot',
  GUNSHOT_CONFIRMED = 'gunshot_confirmed',
  LPR_HIT = 'lpr_hit',
  LPR_ALERT = 'lpr_alert',
  CAMERA_ALERT = 'camera_alert',
  CAMERA_MOTION = 'camera_motion',
  CAMERA_STATUS = 'camera_status',
  INCIDENT_CREATED = 'incident_created',
  INCIDENT_UPDATED = 'incident_updated',
  INCIDENT_CLOSED = 'incident_closed',
  OFFICER_DISPATCH = 'officer_dispatch',
  OFFICER_ARRIVAL = 'officer_arrival',
  OFFICER_CLEAR = 'officer_clear',
  SYSTEM_ALERT = 'system_alert',
  SYSTEM_STATUS = 'system_status',
  INTEGRATION_DATA = 'integration_data',
  INTEGRATION_ERROR = 'integration_error',
}

/**
 * Event priority enumeration.
 */
export enum EventPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFO = 'info',
}

/**
 * Event source enumeration.
 */
export enum EventSource {
  SHOTSPOTTER = 'shotspotter',
  FLOCK = 'flock',
  MILESTONE = 'milestone',
  ONESOLUTION = 'onesolution',
  NESS = 'ness',
  BWC = 'bwc',
  HOTSHEETS = 'hotsheets',
  CAD = 'cad',
  MANUAL = 'manual',
  SYSTEM = 'system',
}

/**
 * Real-time event.
 */
export interface RTCCEvent {
  id: string;
  eventType: EventType;
  source: EventSource;
  priority: EventPriority;
  title: string;
  description?: string;
  location?: GeoLocation;
  address?: string;
  timestamp: string;
  metadata: Record<string, unknown>;
  tags: string[];
  sourceEventId?: string;
  createdAt: string;
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  relatedEntityIds: string[];
  relatedIncidentId?: string;
}

/**
 * WebSocket message types.
 */
export enum WebSocketMessageType {
  // Client to server
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  ACKNOWLEDGE = 'acknowledge',
  PING = 'ping',
  // Server to client
  EVENT = 'event',
  SUBSCRIBED = 'subscribed',
  UNSUBSCRIBED = 'unsubscribed',
  ACKNOWLEDGED = 'acknowledged',
  PONG = 'pong',
  ERROR = 'error',
  CONNECTED = 'connected',
}

/**
 * WebSocket message.
 */
export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: Record<string, unknown>;
  timestamp: string;
  messageId?: string;
}

/**
 * Event subscription configuration.
 */
export interface EventSubscription {
  eventTypes?: EventType[];
  sources?: EventSource[];
  priorities?: EventPriority[];
  geographicBounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  tags?: string[];
}

/**
 * Event filter for queries.
 */
export interface EventFilter {
  eventTypes?: EventType[];
  sources?: EventSource[];
  priorities?: EventPriority[];
  startTime?: string;
  endTime?: string;
  acknowledged?: boolean;
  tags?: string[];
  searchQuery?: string;
}

/**
 * Priority color mapping for UI.
 */
export const PRIORITY_COLORS: Record<EventPriority, string> = {
  [EventPriority.CRITICAL]: '#dc2626', // red-600
  [EventPriority.HIGH]: '#ea580c', // orange-600
  [EventPriority.MEDIUM]: '#ca8a04', // yellow-600
  [EventPriority.LOW]: '#2563eb', // blue-600
  [EventPriority.INFO]: '#6b7280', // gray-500
};

/**
 * Event type icons for UI.
 */
export const EVENT_TYPE_ICONS: Record<EventType, string> = {
  [EventType.GUNSHOT]: 'target',
  [EventType.GUNSHOT_CONFIRMED]: 'target',
  [EventType.LPR_HIT]: 'car',
  [EventType.LPR_ALERT]: 'alert-triangle',
  [EventType.CAMERA_ALERT]: 'video',
  [EventType.CAMERA_MOTION]: 'activity',
  [EventType.CAMERA_STATUS]: 'camera',
  [EventType.INCIDENT_CREATED]: 'file-plus',
  [EventType.INCIDENT_UPDATED]: 'file-text',
  [EventType.INCIDENT_CLOSED]: 'file-check',
  [EventType.OFFICER_DISPATCH]: 'radio',
  [EventType.OFFICER_ARRIVAL]: 'map-pin',
  [EventType.OFFICER_CLEAR]: 'check-circle',
  [EventType.SYSTEM_ALERT]: 'bell',
  [EventType.SYSTEM_STATUS]: 'server',
  [EventType.INTEGRATION_DATA]: 'database',
  [EventType.INTEGRATION_ERROR]: 'alert-circle',
};
