/**
 * WebSocket client for real-time events.
 *
 * Provides:
 * - Automatic reconnection
 * - Message handling
 * - Subscription management
 * - Heartbeat monitoring
 */

import { useEventStore } from '@/lib/store/events';
import {
  RTCCEvent,
  WebSocketMessage,
  WebSocketMessageType,
  EventSubscription,
} from '@/shared/schemas/events';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/realtime/ws/events';

/**
 * WebSocket connection state.
 */
type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * WebSocket client class.
 */
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 5000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, (data: unknown) => void> = new Map();
  private state: ConnectionState = 'disconnected';

  /**
   * Connect to the WebSocket server.
   */
  connect(token?: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.state = 'connecting';
    const url = token ? `${WS_URL}?token=${token}` : WS_URL;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.state = 'connected';
        this.reconnectAttempts = 0;
        useEventStore.getState().setConnected(true);
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.state = 'disconnected';
        useEventStore.getState().setConnected(false);
        this.stopHeartbeat();
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.state = 'error';
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.state = 'error';
      this.attemptReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.state = 'disconnected';
    useEventStore.getState().setConnected(false);
  }

  /**
   * Send a message to the server.
   */
  send(type: WebSocketMessageType, payload: Record<string, unknown> = {}): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }

    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Subscribe to specific event types/sources.
   */
  subscribe(subscription: EventSubscription): void {
    this.send(WebSocketMessageType.SUBSCRIBE, subscription as unknown as Record<string, unknown>);
  }

  /**
   * Unsubscribe from all filters.
   */
  unsubscribe(): void {
    this.send(WebSocketMessageType.UNSUBSCRIBE);
  }

  /**
   * Acknowledge an event.
   */
  acknowledgeEvent(eventId: string, notes?: string): void {
    this.send(WebSocketMessageType.ACKNOWLEDGE, { eventId, notes });
  }

  /**
   * Register a message handler.
   */
  onMessage(type: string, handler: (data: unknown) => void): void {
    this.messageHandlers.set(type, handler);
  }

  /**
   * Remove a message handler.
   */
  offMessage(type: string): void {
    this.messageHandlers.delete(type);
  }

  /**
   * Get current connection state.
   */
  getState(): ConnectionState {
    return this.state;
  }

  /**
   * Handle incoming messages.
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case WebSocketMessageType.EVENT:
        const event = message.payload as unknown as RTCCEvent;
        useEventStore.getState().addEvent(event);
        break;

      case WebSocketMessageType.PONG:
        // Heartbeat response received
        break;

      case WebSocketMessageType.SUBSCRIBED:
        console.log('Subscription confirmed:', message.payload);
        break;

      case WebSocketMessageType.ACKNOWLEDGED:
        const { eventId } = message.payload as { eventId: string };
        useEventStore.getState().acknowledgeEvent(eventId);
        break;

      case WebSocketMessageType.ERROR:
        console.error('WebSocket error:', message.payload);
        break;

      default:
        // Call registered handler if exists
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
          handler(message.payload);
        }
    }
  }

  /**
   * Start heartbeat interval.
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send(WebSocketMessageType.PING);
    }, 30000);
  }

  /**
   * Stop heartbeat interval.
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Attempt to reconnect after disconnect.
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      // Get token from auth store
      if (typeof window !== 'undefined') {
        const authStorage = localStorage.getItem('rtcc-auth-storage');
        if (authStorage) {
          try {
            const { state } = JSON.parse(authStorage);
            this.connect(state?.accessToken);
          } catch {
            this.connect();
          }
        } else {
          this.connect();
        }
      }
    }, delay);
  }
}

/**
 * Singleton WebSocket client instance.
 */
export const wsClient = new WebSocketClient();
