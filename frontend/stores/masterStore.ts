import { create } from 'zustand';

export interface Alert {
  alert_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  source: string;
  timestamp: string;
  title: string;
  summary: string;
  geolocation?: { lat: number; lng: number };
  constitutional_compliance_tag: boolean;
  moral_compass_tag?: string;
  public_safety_audit_ref?: string;
  affected_areas: string[];
  requires_action: boolean;
  action_taken: boolean;
  active: boolean;
}

export interface MasterEvent {
  event_id: string;
  event_type: string;
  priority: string;
  source: string;
  timestamp: string;
  title: string;
  summary: string;
  details: Record<string, unknown>;
  geolocation?: { lat: number; lng: number };
  constitutional_compliance: boolean;
  moral_compass_tag?: string;
}

export interface ModuleHealth {
  module_id: string;
  module_name: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'offline' | 'unknown';
  last_heartbeat?: string;
  response_time_ms: number;
  cpu_usage: number;
  memory_usage: number;
  error_count: number;
}

export interface OfficerStatus {
  officer_id: string;
  name: string;
  badge_number: string;
  status: 'available' | 'on_call' | 'responding' | 'busy' | 'off_duty';
  location?: { lat: number; lng: number };
  current_assignment?: string;
}

export interface DroneStatus {
  drone_id: string;
  name: string;
  status: 'active' | 'standby' | 'returning' | 'charging' | 'maintenance';
  battery: number;
  position?: { lat: number; lng: number; altitude: number };
  mission_id?: string;
}

export interface RobotStatus {
  robot_id: string;
  name: string;
  status: 'active' | 'standby' | 'patrolling' | 'charging' | 'maintenance';
  battery: number;
  position?: { lat: number; lng: number };
  task_id?: string;
}

export interface Investigation {
  case_id: string;
  title: string;
  status: 'open' | 'active' | 'pending' | 'closed';
  priority: 'critical' | 'high' | 'medium' | 'low';
  assigned_to: string;
  created_at: string;
  updated_at: string;
}

export interface ThreatIndicator {
  threat_id: string;
  threat_level: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  source: string;
  timestamp: string;
  affected_areas: string[];
}

export interface HumanStabilityPulse {
  overall_score: number;
  mental_health_alerts: number;
  crisis_interventions: number;
  community_wellness: number;
  trend: 'improving' | 'stable' | 'declining';
}

export interface MoralCompassScore {
  overall_score: number;
  constitutional_compliance: number;
  ethical_alignment: number;
  bias_detection: number;
  fairness_index: number;
}

interface MasterState {
  alerts: Alert[];
  events: MasterEvent[];
  moduleHealth: Record<string, ModuleHealth>;
  officers: OfficerStatus[];
  drones: DroneStatus[];
  robots: RobotStatus[];
  investigations: Investigation[];
  threats: ThreatIndicator[];
  humanStability: HumanStabilityPulse;
  moralCompass: MoralCompassScore;
  wsConnected: boolean;
  lastUpdate: string;

  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  updateAlert: (alertId: string, updates: Partial<Alert>) => void;
  setEvents: (events: MasterEvent[]) => void;
  addEvent: (event: MasterEvent) => void;
  setModuleHealth: (health: Record<string, ModuleHealth>) => void;
  updateModuleHealth: (moduleId: string, health: ModuleHealth) => void;
  setOfficers: (officers: OfficerStatus[]) => void;
  updateOfficer: (officerId: string, updates: Partial<OfficerStatus>) => void;
  setDrones: (drones: DroneStatus[]) => void;
  updateDrone: (droneId: string, updates: Partial<DroneStatus>) => void;
  setRobots: (robots: RobotStatus[]) => void;
  updateRobot: (robotId: string, updates: Partial<RobotStatus>) => void;
  setInvestigations: (investigations: Investigation[]) => void;
  setThreats: (threats: ThreatIndicator[]) => void;
  setHumanStability: (pulse: HumanStabilityPulse) => void;
  setMoralCompass: (score: MoralCompassScore) => void;
  setWsConnected: (connected: boolean) => void;
  setLastUpdate: (timestamp: string) => void;
}

export const useMasterStore = create<MasterState>((set) => ({
  alerts: [
    {
      alert_id: 'alert-001',
      severity: 'high',
      source: 'officer_assist',
      timestamp: new Date().toISOString(),
      title: 'Officer Safety Alert - High Risk Stop',
      summary: 'Officer approaching vehicle with known armed suspect',
      geolocation: { lat: 26.7753, lng: -80.0589 },
      constitutional_compliance_tag: true,
      affected_areas: ['Downtown Riviera Beach'],
      requires_action: true,
      action_taken: false,
      active: true,
    },
    {
      alert_id: 'alert-002',
      severity: 'medium',
      source: 'tactical_analytics',
      timestamp: new Date().toISOString(),
      title: 'Crime Pattern Detected',
      summary: 'Increased burglary activity in Singer Island area',
      geolocation: { lat: 26.785, lng: -80.035 },
      constitutional_compliance_tag: true,
      affected_areas: ['Singer Island'],
      requires_action: false,
      action_taken: false,
      active: true,
    },
    {
      alert_id: 'alert-003',
      severity: 'critical',
      source: 'emergency_mgmt',
      timestamp: new Date().toISOString(),
      title: 'Weather Alert - Tropical Storm Warning',
      summary: 'Tropical storm approaching Palm Beach County',
      constitutional_compliance_tag: true,
      affected_areas: ['All Neighborhoods'],
      requires_action: true,
      action_taken: false,
      active: true,
    },
  ],
  events: [],
  moduleHealth: {},
  officers: [
    { officer_id: 'off-001', name: 'Officer Johnson', badge_number: 'RB-1234', status: 'available', location: { lat: 26.775, lng: -80.058 } },
    { officer_id: 'off-002', name: 'Officer Martinez', badge_number: 'RB-1235', status: 'responding', location: { lat: 26.78, lng: -80.04 }, current_assignment: 'Traffic Stop' },
    { officer_id: 'off-003', name: 'Officer Williams', badge_number: 'RB-1236', status: 'on_call', location: { lat: 26.77, lng: -80.05 } },
    { officer_id: 'off-004', name: 'Officer Davis', badge_number: 'RB-1237', status: 'busy', location: { lat: 26.785, lng: -80.035 }, current_assignment: 'Investigation' },
    { officer_id: 'off-005', name: 'Officer Brown', badge_number: 'RB-1238', status: 'available', location: { lat: 26.772, lng: -80.062 } },
  ],
  drones: [
    { drone_id: 'drone-001', name: 'Sentinel-1', status: 'active', battery: 85, position: { lat: 26.775, lng: -80.058, altitude: 150 }, mission_id: 'patrol-001' },
    { drone_id: 'drone-002', name: 'Sentinel-2', status: 'standby', battery: 100, position: { lat: 26.78, lng: -80.04, altitude: 0 } },
    { drone_id: 'drone-003', name: 'Sentinel-3', status: 'returning', battery: 25, position: { lat: 26.77, lng: -80.05, altitude: 100 } },
  ],
  robots: [
    { robot_id: 'robot-001', name: 'Guardian-1', status: 'patrolling', battery: 72, position: { lat: 26.775, lng: -80.058 }, task_id: 'patrol-downtown' },
    { robot_id: 'robot-002', name: 'Guardian-2', status: 'standby', battery: 95, position: { lat: 26.78, lng: -80.04 } },
  ],
  investigations: [
    { case_id: 'case-001', title: 'Burglary Series - Singer Island', status: 'active', priority: 'high', assigned_to: 'Det. Smith', created_at: '2025-12-01T10:00:00Z', updated_at: new Date().toISOString() },
    { case_id: 'case-002', title: 'Vehicle Theft Ring', status: 'open', priority: 'medium', assigned_to: 'Det. Jones', created_at: '2025-12-05T14:30:00Z', updated_at: new Date().toISOString() },
    { case_id: 'case-003', title: 'Fraud Investigation', status: 'pending', priority: 'low', assigned_to: 'Det. Garcia', created_at: '2025-12-10T09:15:00Z', updated_at: new Date().toISOString() },
  ],
  threats: [
    { threat_id: 'threat-001', threat_level: 'medium', title: 'Cyber Threat - Phishing Campaign', source: 'cyber_intel', timestamp: new Date().toISOString(), affected_areas: ['Government Networks'] },
    { threat_id: 'threat-002', threat_level: 'low', title: 'Social Media Threat Assessment', source: 'global_awareness', timestamp: new Date().toISOString(), affected_areas: ['Downtown Riviera Beach'] },
  ],
  humanStability: {
    overall_score: 78,
    mental_health_alerts: 3,
    crisis_interventions: 1,
    community_wellness: 82,
    trend: 'stable',
  },
  moralCompass: {
    overall_score: 94,
    constitutional_compliance: 98,
    ethical_alignment: 92,
    bias_detection: 95,
    fairness_index: 91,
  },
  wsConnected: false,
  lastUpdate: new Date().toISOString(),

  setAlerts: (alerts) => set({ alerts, lastUpdate: new Date().toISOString() }),
  addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts], lastUpdate: new Date().toISOString() })),
  updateAlert: (alertId, updates) =>
    set((state) => ({
      alerts: state.alerts.map((a) => (a.alert_id === alertId ? { ...a, ...updates } : a)),
      lastUpdate: new Date().toISOString(),
    })),
  setEvents: (events) => set({ events, lastUpdate: new Date().toISOString() }),
  addEvent: (event) => set((state) => ({ events: [event, ...state.events].slice(0, 100), lastUpdate: new Date().toISOString() })),
  setModuleHealth: (moduleHealth) => set({ moduleHealth, lastUpdate: new Date().toISOString() }),
  updateModuleHealth: (moduleId, health) =>
    set((state) => ({
      moduleHealth: { ...state.moduleHealth, [moduleId]: health },
      lastUpdate: new Date().toISOString(),
    })),
  setOfficers: (officers) => set({ officers, lastUpdate: new Date().toISOString() }),
  updateOfficer: (officerId, updates) =>
    set((state) => ({
      officers: state.officers.map((o) => (o.officer_id === officerId ? { ...o, ...updates } : o)),
      lastUpdate: new Date().toISOString(),
    })),
  setDrones: (drones) => set({ drones, lastUpdate: new Date().toISOString() }),
  updateDrone: (droneId, updates) =>
    set((state) => ({
      drones: state.drones.map((d) => (d.drone_id === droneId ? { ...d, ...updates } : d)),
      lastUpdate: new Date().toISOString(),
    })),
  setRobots: (robots) => set({ robots, lastUpdate: new Date().toISOString() }),
  updateRobot: (robotId, updates) =>
    set((state) => ({
      robots: state.robots.map((r) => (r.robot_id === robotId ? { ...r, ...updates } : r)),
      lastUpdate: new Date().toISOString(),
    })),
  setInvestigations: (investigations) => set({ investigations, lastUpdate: new Date().toISOString() }),
  setThreats: (threats) => set({ threats, lastUpdate: new Date().toISOString() }),
  setHumanStability: (humanStability) => set({ humanStability, lastUpdate: new Date().toISOString() }),
  setMoralCompass: (moralCompass) => set({ moralCompass, lastUpdate: new Date().toISOString() }),
  setWsConnected: (wsConnected) => set({ wsConnected }),
  setLastUpdate: (lastUpdate) => set({ lastUpdate }),
}));
