/**
 * WebSocket Fallback for Demo Mode.
 *
 * Provides a simulated WebSocket event stream when the real
 * WebSocket server is unavailable.
 */

import { generateRandomEvent } from './index';

type EventCallback = (event: { type: string; data: Record<string, unknown> }) => void;

/**
 * Demo WebSocket Manager.
 *
 * Simulates WebSocket events when the real server is unavailable.
 */
export class DemoWebSocketManager {
  private intervalId: NodeJS.Timeout | null = null;
  private callbacks: Set<EventCallback> = new Set();
  private isRunning = false;
  private minInterval = 10000; // 10 seconds
  private maxInterval = 30000; // 30 seconds

  /**
   * Start the simulated event stream.
   */
  start(): void {
    if (this.isRunning) return;
    this.isRunning = true;
    this.scheduleNextEvent();
    console.log('[DEMO_WS] Started simulated WebSocket event stream');
  }

  /**
   * Stop the simulated event stream.
   */
  stop(): void {
    if (this.intervalId) {
      clearTimeout(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
    console.log('[DEMO_WS] Stopped simulated WebSocket event stream');
  }

  /**
   * Subscribe to simulated events.
   */
  subscribe(callback: EventCallback): () => void {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * Schedule the next random event.
   */
  private scheduleNextEvent(): void {
    if (!this.isRunning) return;

    const delay = this.minInterval + Math.random() * (this.maxInterval - this.minInterval);
    
    this.intervalId = setTimeout(() => {
      this.emitRandomEvent();
      this.scheduleNextEvent();
    }, delay);
  }

  /**
   * Emit a random event to all subscribers.
   */
  private emitRandomEvent(): void {
    const event = generateRandomEvent();
    console.log('[DEMO_WS] Emitting simulated event:', event.type);
    
    this.callbacks.forEach((callback) => {
      try {
        callback(event);
      } catch (error) {
        console.error('[DEMO_WS] Error in event callback:', error);
      }
    });
  }

  /**
   * Manually trigger an event (for testing).
   */
  triggerEvent(): void {
    this.emitRandomEvent();
  }
}

// Global demo WebSocket manager instance
let demoWsManager: DemoWebSocketManager | null = null;

/**
 * Get the demo WebSocket manager instance.
 */
export function getDemoWebSocketManager(): DemoWebSocketManager {
  if (!demoWsManager) {
    demoWsManager = new DemoWebSocketManager();
  }
  return demoWsManager;
}

/**
 * WebSocket connection wrapper with demo fallback.
 *
 * Attempts to connect to the real WebSocket server, but falls back
 * to simulated events if the connection fails.
 */
export class WebSocketWithFallback {
  private ws: WebSocket | null = null;
  private demoManager: DemoWebSocketManager;
  private callbacks: Set<EventCallback> = new Set();
  private url: string;
  private isUsingFallback = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectDelay = 2000;

  constructor(url: string) {
    this.url = url;
    this.demoManager = getDemoWebSocketManager();
  }

  /**
   * Connect to WebSocket server with fallback.
   */
  connect(): void {
    this.attemptConnection();
  }

  /**
   * Attempt to connect to the real WebSocket server.
   */
  private attemptConnection(): void {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[WS] Connected to WebSocket server');
        this.reconnectAttempts = 0;
        this.isUsingFallback = false;
        
        // Stop demo fallback if it was running
        this.demoManager.stop();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.callbacks.forEach((callback) => callback(data));
        } catch (error) {
          console.error('[WS] Error parsing message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.warn('[WS] WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('[WS] WebSocket connection closed');
        this.handleDisconnect();
      };

      // Set connection timeout
      setTimeout(() => {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
          console.warn('[WS] Connection timeout, switching to fallback');
          this.ws.close();
          this.switchToFallback();
        }
      }, 5000);

    } catch (error) {
      console.error('[WS] Failed to create WebSocket:', error);
      this.switchToFallback();
    }
  }

  /**
   * Handle WebSocket disconnection.
   */
  private handleDisconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[WS] Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.attemptConnection(), this.reconnectDelay);
    } else {
      this.switchToFallback();
    }
  }

  /**
   * Switch to demo fallback mode.
   */
  private switchToFallback(): void {
    if (this.isUsingFallback) return;
    
    console.log('[WS] Switching to demo fallback mode');
    this.isUsingFallback = true;
    
    // Subscribe to demo events
    this.demoManager.subscribe((event) => {
      this.callbacks.forEach((callback) => callback(event));
    });
    
    // Start the demo event stream
    this.demoManager.start();
    
    // Mark backend as unavailable for demo mode detection
    if (typeof window !== 'undefined') {
      localStorage.setItem('rtcc-backend-status', 'unavailable');
    }
  }

  /**
   * Subscribe to events (real or simulated).
   */
  subscribe(callback: EventCallback): () => void {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * Send a message (only works with real WebSocket).
   */
  send(data: unknown): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else if (this.isUsingFallback) {
      console.log('[WS_FALLBACK] Message would be sent:', data);
    }
  }

  /**
   * Close the connection.
   */
  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.demoManager.stop();
    this.callbacks.clear();
  }

  /**
   * Check if using fallback mode.
   */
  isInFallbackMode(): boolean {
    return this.isUsingFallback;
  }
}

export default WebSocketWithFallback;
