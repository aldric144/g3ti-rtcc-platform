/**
 * G3TI RTCC Mobile App Types
 */

export type DeviceType = 'ios' | 'android' | 'mdt' | 'tablet' | 'unknown';
export type DeviceStatus = 'pending' | 'active' | 'suspended' | 'revoked';
export type AlertPriority = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type AlertType = 'dispatch' | 'officer_safety' | 'bolo' | 'intel' | 'message' | 'ambush' | 'hotzone' | 'threat' | 'system';
export type UnitStatus = 'available' | 'en_route' | 'on_scene' | 'transporting' | 'at_hospital' | 'reports' | 'out_of_service' | 'off_duty';
export type ThreatLevel = 'critical' | 'high' | 'elevated' | 'moderate' | 'low' | 'minimal';
export type CheckInType = 'routine' | 'safe' | 'emergency' | 'arrived' | 'cleared';
export type IntelPacketType = 'vehicle' | 'person' | 'location' | 'officer_safety' | 'bulletin' | 'command_note' | 'bolo' | 'warrant' | 'gunfire' | 'lpr_hit' | 'general';

export interface User {
  id: string;
  badge_number: string;
  name: string;
  role: string;
  unit_id?: string;
  district?: string;
}

export interface AuthSession {
  session_id: string;
  access_token: string;
  refresh_token: string;
  expires_at: string;
  user: User;
}

export interface MobileAlert {
  id: string;
  alert_type: AlertType;
  priority: AlertPriority;
  title: string;
  body: string;
  data: Record<string, unknown>;
  created_at: string;
  expires_at?: string;
  read: boolean;
  acknowledged: boolean;
}

export interface DispatchCall {
  id: string;
  call_number: string;
  call_type: string;
  priority: number;
  location: string;
  latitude?: number;
  longitude?: number;
  description?: string;
  assigned_units: string[];
  status: string;
  created_at: string;
  notes: string[];
  hazards: string[];
}

export interface MobileMessage {
  id: string;
  sender_badge: string;
  sender_name: string;
  content: string;
  priority: AlertPriority;
  created_at: string;
  is_rtcc: boolean;
  read: boolean;
}

export interface OfficerSafetyStatus {
  badge_number: string;
  officer_name: string;
  threat_level: ThreatLevel;
  threat_score: number;
  active_warnings: string[];
  nearby_threats: number;
  in_hotzone: boolean;
  hotzone_name?: string;
  last_check_in?: string;
  last_location?: { lat: number; lng: number };
}

export interface ProximityWarning {
  id: string;
  warning_type: string;
  title: string;
  description: string;
  threat_level: ThreatLevel;
  distance_meters: number;
  direction?: string;
  latitude?: number;
  longitude?: number;
  acknowledged: boolean;
}

export interface IntelPacket {
  id: string;
  packet_type: IntelPacketType;
  priority: AlertPriority;
  title: string;
  summary: string;
  details: Record<string, unknown>;
  images: string[];
  location?: string;
  latitude?: number;
  longitude?: number;
  safety_notes: Array<{ content: string; severity: string }>;
  created_at: string;
  is_critical: boolean;
}

export interface UnitTelemetry {
  badge_number: string;
  unit_id: string;
  gps?: {
    latitude: number;
    longitude: number;
    accuracy_meters?: number;
    heading?: number;
    speed_mps?: number;
  };
  battery?: {
    level_percent: number;
    status: string;
    is_charging: boolean;
  };
  is_online: boolean;
  last_update: string;
}

export interface IncidentSummary {
  id: string;
  incident_type: string;
  status: string;
  location: string;
  commander?: string;
  start_time: string;
  assigned_units: string[];
}

export interface TimelineEvent {
  id: string;
  event_type: string;
  title: string;
  description: string;
  timestamp: string;
  source: string;
}

export interface SceneCoordination {
  call_id: string;
  incident_commander?: string;
  staging_location?: string;
  assignments: Array<{
    unit_id: string;
    badge_number: string;
    officer_name: string;
    role: string;
  }>;
  perimeter_established: boolean;
  resources_on_scene: string[];
}
