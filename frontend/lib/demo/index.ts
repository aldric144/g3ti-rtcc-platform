/**
 * Demo Mode Utilities for G3TI RTCC-UIP Frontend.
 *
 * Provides fail-safe API wrappers, demo data, and fallback behavior
 * when the backend is unavailable or in demo mode.
 */

// Demo mode configuration
export const DEMO_MODE_CONFIG = {
  enabled: true,
  apiTimeout: 2500, // 2.5 seconds
  showBanner: true,
  bannerMessage: 'RTCC is running in Demo Mode — Some data is simulated.',
};

// Demo user data
export const DEMO_USER = {
  id: 'demo-user-001',
  username: 'demo',
  email: 'demo@g3ti-demo.com',
  first_name: 'Demo',
  last_name: 'User',
  badge_number: 'DEMO-001',
  department: 'Demo Operations',
  role: 'admin',
  is_active: true,
};

// Demo cameras data
export const DEMO_CAMERAS = [
  {
    id: 'cam-001',
    name: 'City Hall - Main Entrance',
    location: { latitude: 26.7753, longitude: -80.0589 },
    address: '600 W Blue Heron Blvd, Riviera Beach, FL',
    status: 'online',
    type: 'fixed',
    zone: 'downtown',
  },
  {
    id: 'cam-002',
    name: 'Marina Village - North',
    location: { latitude: 26.7821, longitude: -80.0512 },
    address: '200 E 13th St, Riviera Beach, FL',
    status: 'online',
    type: 'ptz',
    zone: 'marina',
  },
  {
    id: 'cam-003',
    name: 'Blue Heron & Congress',
    location: { latitude: 26.7748, longitude: -80.0721 },
    address: 'Blue Heron Blvd & Congress Ave',
    status: 'online',
    type: 'fixed',
    zone: 'commercial',
  },
  {
    id: 'cam-004',
    name: 'Riviera Beach Marina',
    location: { latitude: 26.7789, longitude: -80.0478 },
    address: '200 E 13th St, Riviera Beach, FL',
    status: 'online',
    type: 'ptz',
    zone: 'marina',
  },
  {
    id: 'cam-005',
    name: 'Singer Island Beach Access',
    location: { latitude: 26.7912, longitude: -80.0345 },
    address: 'Singer Island, Riviera Beach, FL',
    status: 'online',
    type: 'fixed',
    zone: 'beach',
  },
];

// Demo incidents data
export const DEMO_INCIDENTS = [
  {
    id: 'inc-2024-001234',
    incident_number: '2024-001234',
    incident_type: 'traffic_accident',
    status: 'active',
    priority: 'medium',
    title: 'Vehicle Collision - Blue Heron Blvd',
    description: 'Two-vehicle collision with minor injuries reported',
    location: { latitude: 26.7753, longitude: -80.0621 },
    address: 'Blue Heron Blvd & Congress Ave, Riviera Beach, FL',
    reported_at: new Date().toISOString(),
  },
  {
    id: 'inc-2024-001235',
    incident_number: '2024-001235',
    incident_type: 'suspicious_activity',
    status: 'active',
    priority: 'low',
    title: 'Suspicious Vehicle - Marina Area',
    description: 'White sedan circling marina parking lot for 30+ minutes',
    location: { latitude: 26.7821, longitude: -80.0512 },
    address: '200 E 13th St, Riviera Beach, FL',
    reported_at: new Date().toISOString(),
  },
  {
    id: 'inc-2024-001238',
    incident_number: '2024-001238',
    incident_type: 'medical_emergency',
    status: 'active',
    priority: 'critical',
    title: 'Medical Emergency - Beach Area',
    description: 'Possible drowning, lifeguards on scene, EMS en route',
    location: { latitude: 26.7912, longitude: -80.0345 },
    address: 'Singer Island Beach, Riviera Beach, FL',
    reported_at: new Date().toISOString(),
  },
];

// Demo LPR hits data
export const DEMO_LPR_HITS = [
  {
    id: 'lpr-001',
    plate_number: 'ABC-1234',
    plate_state: 'FL',
    hit_type: 'stolen_vehicle',
    confidence: 98.5,
    location: { latitude: 26.7753, longitude: -80.0621 },
    address: 'Blue Heron Blvd & Congress Ave',
    timestamp: new Date().toISOString(),
    alert_status: 'active',
  },
  {
    id: 'lpr-005',
    plate_number: 'JKL-7890',
    plate_state: 'FL',
    hit_type: 'amber_alert',
    confidence: 97.3,
    location: { latitude: 26.7912, longitude: -80.0345 },
    address: 'Singer Island Beach Access',
    timestamp: new Date().toISOString(),
    alert_status: 'active',
  },
];

// Demo gunshot alerts data
export const DEMO_GUNSHOT_ALERTS = [
  {
    id: 'gs-001',
    alert_type: 'gunshot',
    rounds_detected: 3,
    confidence: 95.5,
    location: { latitude: 26.7712, longitude: -80.0656 },
    address: '400 Block Avenue E, Riviera Beach, FL',
    timestamp: new Date().toISOString(),
    status: 'active',
    responding_units: ['Unit-01', 'Unit-03', 'Unit-12'],
  },
];

// Demo officers data
export const DEMO_OFFICERS = [
  {
    id: 'officer-001',
    badge_number: '1001',
    name: 'Officer James Rodriguez',
    rank: 'Patrol Officer',
    unit_id: 'Unit-01',
    status: 'on_duty',
    current_location: { latitude: 26.7753, longitude: -80.0589 },
    assigned_beat: 'Beat-1',
  },
  {
    id: 'officer-002',
    badge_number: '1002',
    name: 'Officer Maria Santos',
    rank: 'Patrol Officer',
    unit_id: 'Unit-03',
    status: 'responding',
    current_location: { latitude: 26.7712, longitude: -80.0656 },
    assigned_beat: 'Beat-2',
  },
  {
    id: 'officer-003',
    badge_number: '1003',
    name: 'Sergeant Michael Thompson',
    rank: 'Sergeant',
    unit_id: 'Unit-07',
    status: 'on_duty',
    current_location: { latitude: 26.7698, longitude: -80.0789 },
    assigned_beat: 'Beat-3',
  },
];

// Demo dashboard stats
export const DEMO_DASHBOARD_STATS = {
  active_incidents: 3,
  total_cameras: 8,
  online_cameras: 7,
  officers_on_duty: 8,
  open_cases: 4,
  lpr_hits_today: 5,
  gunshot_alerts_today: 1,
  patrol_beats_active: 6,
  demo_mode: true,
};

/**
 * Check if we're in demo mode (either explicitly or due to backend unavailability).
 */
export function isDemoMode(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Check localStorage for demo mode flag
  const demoFlag = localStorage.getItem('rtcc-demo-mode');
  if (demoFlag === 'true') return true;
  
  // Check if we've detected backend unavailability
  const backendStatus = localStorage.getItem('rtcc-backend-status');
  if (backendStatus === 'unavailable') return true;
  
  return DEMO_MODE_CONFIG.enabled;
}

/**
 * Set demo mode status.
 */
export function setDemoMode(enabled: boolean): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('rtcc-demo-mode', enabled ? 'true' : 'false');
}

/**
 * Mark backend as unavailable (triggers demo mode).
 */
export function markBackendUnavailable(): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('rtcc-backend-status', 'unavailable');
}

/**
 * Mark backend as available.
 */
export function markBackendAvailable(): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('rtcc-backend-status', 'available');
}

/**
 * Fail-safe fetch wrapper that returns demo data on timeout or error.
 */
export async function failSafeFetch<T>(
  fetchFn: () => Promise<T>,
  demoData: T,
  timeoutMs: number = DEMO_MODE_CONFIG.apiTimeout
): Promise<{ data: T; isDemo: boolean }> {
  // If already in demo mode, return demo data immediately
  if (isDemoMode()) {
    return { data: demoData, isDemo: true };
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    const result = await Promise.race([
      fetchFn(),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), timeoutMs)
      ),
    ]);

    clearTimeout(timeoutId);
    markBackendAvailable();
    return { data: result, isDemo: false };
  } catch (error) {
    console.warn('[DEMO_MODE] API call failed, returning demo data:', error);
    markBackendUnavailable();
    return { data: demoData, isDemo: true };
  }
}

/**
 * Generate a random simulated event for WebSocket fallback.
 */
export function generateRandomEvent(): {
  type: string;
  data: Record<string, unknown>;
} {
  const eventTypes = ['lpr_hit', 'gunshot_alert', 'incident', 'officer_update'];
  const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
  const now = new Date().toISOString();

  const baseLocation = {
    latitude: 26.77 + (Math.random() - 0.5) * 0.04,
    longitude: -80.05 + (Math.random() - 0.5) * 0.04,
  };

  switch (eventType) {
    case 'lpr_hit':
      return {
        type: 'lpr_hit',
        data: {
          id: `lpr-sim-${Math.floor(Math.random() * 10000)}`,
          plate_number: `${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}-${Math.floor(Math.random() * 10000)}`,
          plate_state: 'FL',
          hit_type: ['stolen_vehicle', 'wanted_person', 'bolo'][Math.floor(Math.random() * 3)],
          confidence: 85 + Math.random() * 14,
          location: baseLocation,
          timestamp: now,
          alert_status: 'active',
        },
      };

    case 'gunshot_alert':
      return {
        type: 'gunshot_alert',
        data: {
          id: `gs-sim-${Math.floor(Math.random() * 10000)}`,
          alert_type: 'gunshot',
          rounds_detected: Math.floor(Math.random() * 6) + 1,
          confidence: 75 + Math.random() * 23,
          location: baseLocation,
          timestamp: now,
          status: 'active',
        },
      };

    case 'incident':
      return {
        type: 'incident',
        data: {
          id: `inc-sim-${Math.floor(Math.random() * 10000)}`,
          incident_type: ['traffic_accident', 'suspicious_activity', 'theft', 'disturbance'][Math.floor(Math.random() * 4)],
          status: 'active',
          priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
          location: baseLocation,
          timestamp: now,
        },
      };

    default:
      return {
        type: 'officer_update',
        data: {
          officer_id: `officer-${Math.floor(Math.random() * 8) + 1}`,
          status: ['on_duty', 'responding', 'on_scene', 'available'][Math.floor(Math.random() * 4)],
          location: baseLocation,
          timestamp: now,
        },
      };
  }
}
