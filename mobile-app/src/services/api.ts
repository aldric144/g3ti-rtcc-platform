/**
 * G3TI RTCC Mobile App API Service
 * Handles all API communication with the backend
 */

import * as SecureStore from 'expo-secure-store';
import type {
  AuthSession,
  MobileAlert,
  DispatchCall,
  MobileMessage,
  OfficerSafetyStatus,
  ProximityWarning,
  IntelPacket,
  UnitTelemetry,
  UnitStatus,
} from '../types';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  async init(): Promise<void> {
    this.accessToken = await SecureStore.getItemAsync('access_token');
    this.refreshToken = await SecureStore.getItemAsync('refresh_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401 && this.refreshToken) {
      // Try to refresh token
      const refreshed = await this.refreshSession();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers,
        });
        if (!retryResponse.ok) {
          throw new Error(`API Error: ${retryResponse.status}`);
        }
        return retryResponse.json();
      }
    }

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Authentication
  async registerDevice(
    badgeNumber: string,
    officerId: string,
    deviceId: string,
    deviceType: string,
    pushToken?: string
  ): Promise<{ success: boolean; device_id: string; device_token: string }> {
    return this.request('/api/mobile/auth/device-register', {
      method: 'POST',
      body: JSON.stringify({
        badge_number: badgeNumber,
        officer_id: officerId,
        device_id: deviceId,
        device_type: deviceType,
        push_token: pushToken,
      }),
    });
  }

  async login(
    badgeNumber: string,
    password: string,
    deviceId: string
  ): Promise<AuthSession | null> {
    const response = await this.request<{
      success: boolean;
      session_id?: string;
      access_token?: string;
      refresh_token?: string;
      expires_at?: string;
      error?: string;
    }>('/api/mobile/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        badge_number: badgeNumber,
        password,
        device_id: deviceId,
      }),
    });

    if (response.success && response.access_token && response.refresh_token) {
      this.accessToken = response.access_token;
      this.refreshToken = response.refresh_token;
      await SecureStore.setItemAsync('access_token', response.access_token);
      await SecureStore.setItemAsync('refresh_token', response.refresh_token);

      return {
        session_id: response.session_id!,
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_at: response.expires_at!,
        user: {
          id: '',
          badge_number: badgeNumber,
          name: '',
          role: 'officer',
        },
      };
    }

    return null;
  }

  async refreshSession(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await this.request<{
        success: boolean;
        access_token?: string;
        refresh_token?: string;
      }>('/api/mobile/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.success && response.access_token) {
        this.accessToken = response.access_token;
        this.refreshToken = response.refresh_token || this.refreshToken;
        await SecureStore.setItemAsync('access_token', response.access_token);
        if (response.refresh_token) {
          await SecureStore.setItemAsync('refresh_token', response.refresh_token);
        }
        return true;
      }
    } catch {
      // Refresh failed
    }

    return false;
  }

  async logout(): Promise<void> {
    this.accessToken = null;
    this.refreshToken = null;
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
  }

  // Alerts
  async getAlerts(
    badgeNumber: string,
    unitId?: string,
    limit = 50
  ): Promise<MobileAlert[]> {
    const params = new URLSearchParams({
      badge_number: badgeNumber,
      limit: limit.toString(),
    });
    if (unitId) params.append('unit_id', unitId);

    return this.request(`/api/mobile/alerts?${params}`);
  }

  async markAlertRead(alertId: string, badgeNumber: string): Promise<void> {
    await this.request(`/api/mobile/alerts/${alertId}/read?badge_number=${badgeNumber}`, {
      method: 'POST',
    });
  }

  async acknowledgeAlert(alertId: string, badgeNumber: string): Promise<void> {
    await this.request(`/api/mobile/alerts/${alertId}/acknowledge?badge_number=${badgeNumber}`, {
      method: 'POST',
    });
  }

  // Dispatch
  async getActiveDispatch(badgeNumber?: string, unitId?: string): Promise<DispatchCall[]> {
    const params = new URLSearchParams();
    if (badgeNumber) params.append('badge_number', badgeNumber);
    if (unitId) params.append('unit_id', unitId);

    return this.request(`/api/mobile/dispatch/active?${params}`);
  }

  // Messaging
  async getMessages(
    badgeNumber: string,
    unitId?: string,
    limit = 100
  ): Promise<MobileMessage[]> {
    const params = new URLSearchParams({
      badge_number: badgeNumber,
      limit: limit.toString(),
    });
    if (unitId) params.append('unit_id', unitId);

    return this.request(`/api/mobile/messages/feed?${params}`);
  }

  async sendMessage(
    badgeNumber: string,
    officerName: string,
    content: string,
    recipientBadges?: string[],
    recipientUnits?: string[],
    channel?: string
  ): Promise<MobileMessage> {
    return this.request(`/api/mobile/messages/send?badge_number=${badgeNumber}&officer_name=${officerName}`, {
      method: 'POST',
      body: JSON.stringify({
        content,
        recipient_badges: recipientBadges || [],
        recipient_units: recipientUnits || [],
        channel,
      }),
    });
  }

  // Unit Status
  async getUnitStatus(badgeNumber: string): Promise<{ status: UnitStatus } | null> {
    return this.request(`/api/mobile/unit/status?badge_number=${badgeNumber}`);
  }

  async updateUnitStatus(
    badgeNumber: string,
    unitId: string,
    status: UnitStatus,
    location?: string,
    latitude?: number,
    longitude?: number,
    callId?: string
  ): Promise<void> {
    await this.request(`/api/mobile/unit/status/update?badge_number=${badgeNumber}`, {
      method: 'POST',
      body: JSON.stringify({
        unit_id: unitId,
        status,
        location,
        latitude,
        longitude,
        call_id: callId,
      }),
    });
  }

  // Intel Feed
  async getIntelFeed(
    badgeNumber: string,
    limit = 50,
    intelType?: string
  ): Promise<IntelPacket[]> {
    const params = new URLSearchParams({
      badge_number: badgeNumber,
      limit: limit.toString(),
    });
    if (intelType) params.append('intel_type', intelType);

    return this.request(`/api/mobile/intel/feed?${params}`);
  }

  async getIntelPacket(packetId: string): Promise<IntelPacket | null> {
    return this.request(`/api/mobile/intel/${packetId}`);
  }

  async markIntelRead(packetId: string, badgeNumber: string): Promise<void> {
    await this.request(`/api/mobile/intel/${packetId}/read?badge_number=${badgeNumber}`, {
      method: 'POST',
    });
  }

  // Safety
  async getSafetyStatus(badgeNumber: string): Promise<OfficerSafetyStatus> {
    return this.request(`/api/mobile/safety/status?badge_number=${badgeNumber}`);
  }

  async checkIn(
    badgeNumber: string,
    checkInType: string,
    latitude?: number,
    longitude?: number,
    notes?: string
  ): Promise<void> {
    await this.request(`/api/mobile/safety/checkin?badge_number=${badgeNumber}`, {
      method: 'POST',
      body: JSON.stringify({
        check_in_type: checkInType,
        latitude,
        longitude,
        notes,
      }),
    });
  }

  async getProximityWarnings(
    badgeNumber: string,
    includeAcknowledged = false
  ): Promise<ProximityWarning[]> {
    return this.request(
      `/api/mobile/safety/warnings?badge_number=${badgeNumber}&include_acknowledged=${includeAcknowledged}`
    );
  }

  async acknowledgeWarning(warningId: string, badgeNumber: string): Promise<void> {
    await this.request(`/api/mobile/safety/warnings/${warningId}/acknowledge?badge_number=${badgeNumber}`, {
      method: 'POST',
    });
  }

  // Telemetry
  async updateGPS(
    badgeNumber: string,
    unitId: string,
    latitude: number,
    longitude: number,
    accuracy?: number,
    heading?: number,
    speed?: number
  ): Promise<void> {
    await this.request(`/api/mobile/telemetry/gps?badge_number=${badgeNumber}`, {
      method: 'POST',
      body: JSON.stringify({
        unit_id: unitId,
        latitude,
        longitude,
        accuracy_meters: accuracy,
        heading,
        speed_mps: speed,
      }),
    });
  }

  async getTelemetry(badgeNumber: string): Promise<UnitTelemetry | null> {
    return this.request(`/api/mobile/telemetry/unit/${badgeNumber}`);
  }

  // Incidents
  async getIncidentSummary(incidentId: string): Promise<Record<string, unknown>> {
    return this.request(`/api/mobile/incident/${incidentId}`);
  }

  async getIncidentTimeline(incidentId: string): Promise<Record<string, unknown>> {
    return this.request(`/api/mobile/incident/timeline/${incidentId}`);
  }
}

export const api = new ApiService();
