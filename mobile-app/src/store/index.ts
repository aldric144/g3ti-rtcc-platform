/**
 * G3TI RTCC Mobile App State Management
 * Using Zustand for state management
 */

import { create } from 'zustand';
import type {
  AuthSession,
  User,
  MobileAlert,
  DispatchCall,
  MobileMessage,
  OfficerSafetyStatus,
  ProximityWarning,
  IntelPacket,
  UnitTelemetry,
  IncidentSummary,
  UnitStatus,
} from '../types';

interface AuthState {
  session: AuthSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setSession: (session: AuthSession | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

interface AlertsState {
  alerts: MobileAlert[];
  unreadCount: number;
  isLoading: boolean;
  setAlerts: (alerts: MobileAlert[]) => void;
  addAlert: (alert: MobileAlert) => void;
  markRead: (alertId: string) => void;
  markAcknowledged: (alertId: string) => void;
  setLoading: (loading: boolean) => void;
}

interface DispatchState {
  activeCalls: DispatchCall[];
  assignedCalls: DispatchCall[];
  selectedCall: DispatchCall | null;
  isLoading: boolean;
  setCalls: (calls: DispatchCall[]) => void;
  setAssignedCalls: (calls: DispatchCall[]) => void;
  selectCall: (call: DispatchCall | null) => void;
  setLoading: (loading: boolean) => void;
}

interface MessagingState {
  messages: MobileMessage[];
  unreadCount: number;
  isLoading: boolean;
  setMessages: (messages: MobileMessage[]) => void;
  addMessage: (message: MobileMessage) => void;
  markRead: (messageId: string) => void;
  setLoading: (loading: boolean) => void;
}

interface SafetyState {
  status: OfficerSafetyStatus | null;
  warnings: ProximityWarning[];
  isLoading: boolean;
  setStatus: (status: OfficerSafetyStatus | null) => void;
  setWarnings: (warnings: ProximityWarning[]) => void;
  addWarning: (warning: ProximityWarning) => void;
  acknowledgeWarning: (warningId: string) => void;
  setLoading: (loading: boolean) => void;
}

interface IntelState {
  packets: IntelPacket[];
  unreadCount: number;
  selectedPacket: IntelPacket | null;
  isLoading: boolean;
  setPackets: (packets: IntelPacket[]) => void;
  addPacket: (packet: IntelPacket) => void;
  selectPacket: (packet: IntelPacket | null) => void;
  markRead: (packetId: string) => void;
  setLoading: (loading: boolean) => void;
}

interface UnitState {
  currentStatus: UnitStatus;
  telemetry: UnitTelemetry | null;
  isLoading: boolean;
  setStatus: (status: UnitStatus) => void;
  setTelemetry: (telemetry: UnitTelemetry | null) => void;
  setLoading: (loading: boolean) => void;
}

interface IncidentState {
  activeIncidents: IncidentSummary[];
  selectedIncident: IncidentSummary | null;
  isLoading: boolean;
  setIncidents: (incidents: IncidentSummary[]) => void;
  selectIncident: (incident: IncidentSummary | null) => void;
  setLoading: (loading: boolean) => void;
}

interface SettingsState {
  darkMode: boolean;
  notificationsEnabled: boolean;
  locationEnabled: boolean;
  offlineMode: boolean;
  toggleDarkMode: () => void;
  toggleNotifications: () => void;
  toggleLocation: () => void;
  toggleOfflineMode: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  setSession: (session) => set({ session, isAuthenticated: !!session, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  logout: () => set({ session: null, isAuthenticated: false }),
}));

export const useAlertsStore = create<AlertsState>((set) => ({
  alerts: [],
  unreadCount: 0,
  isLoading: false,
  setAlerts: (alerts) => set({ alerts, unreadCount: alerts.filter(a => !a.read).length }),
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts],
    unreadCount: state.unreadCount + (alert.read ? 0 : 1),
  })),
  markRead: (alertId) => set((state) => ({
    alerts: state.alerts.map(a => a.id === alertId ? { ...a, read: true } : a),
    unreadCount: Math.max(0, state.unreadCount - 1),
  })),
  markAcknowledged: (alertId) => set((state) => ({
    alerts: state.alerts.map(a => a.id === alertId ? { ...a, acknowledged: true, read: true } : a),
  })),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useDispatchStore = create<DispatchState>((set) => ({
  activeCalls: [],
  assignedCalls: [],
  selectedCall: null,
  isLoading: false,
  setCalls: (activeCalls) => set({ activeCalls }),
  setAssignedCalls: (assignedCalls) => set({ assignedCalls }),
  selectCall: (selectedCall) => set({ selectedCall }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useMessagingStore = create<MessagingState>((set) => ({
  messages: [],
  unreadCount: 0,
  isLoading: false,
  setMessages: (messages) => set({ messages, unreadCount: messages.filter(m => !m.read).length }),
  addMessage: (message) => set((state) => ({
    messages: [message, ...state.messages],
    unreadCount: state.unreadCount + (message.read ? 0 : 1),
  })),
  markRead: (messageId) => set((state) => ({
    messages: state.messages.map(m => m.id === messageId ? { ...m, read: true } : m),
    unreadCount: Math.max(0, state.unreadCount - 1),
  })),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useSafetyStore = create<SafetyState>((set) => ({
  status: null,
  warnings: [],
  isLoading: false,
  setStatus: (status) => set({ status }),
  setWarnings: (warnings) => set({ warnings }),
  addWarning: (warning) => set((state) => ({ warnings: [warning, ...state.warnings] })),
  acknowledgeWarning: (warningId) => set((state) => ({
    warnings: state.warnings.map(w => w.id === warningId ? { ...w, acknowledged: true } : w),
  })),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useIntelStore = create<IntelState>((set) => ({
  packets: [],
  unreadCount: 0,
  selectedPacket: null,
  isLoading: false,
  setPackets: (packets) => set({ packets, unreadCount: packets.filter(p => !p.is_critical).length }),
  addPacket: (packet) => set((state) => ({
    packets: [packet, ...state.packets],
    unreadCount: state.unreadCount + 1,
  })),
  selectPacket: (selectedPacket) => set({ selectedPacket }),
  markRead: (packetId) => set((state) => ({
    packets: state.packets.map(p => p.id === packetId ? { ...p, is_critical: false } : p),
    unreadCount: Math.max(0, state.unreadCount - 1),
  })),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useUnitStore = create<UnitState>((set) => ({
  currentStatus: 'available',
  telemetry: null,
  isLoading: false,
  setStatus: (currentStatus) => set({ currentStatus }),
  setTelemetry: (telemetry) => set({ telemetry }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useIncidentStore = create<IncidentState>((set) => ({
  activeIncidents: [],
  selectedIncident: null,
  isLoading: false,
  setIncidents: (activeIncidents) => set({ activeIncidents }),
  selectIncident: (selectedIncident) => set({ selectedIncident }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export const useSettingsStore = create<SettingsState>((set) => ({
  darkMode: true,
  notificationsEnabled: true,
  locationEnabled: true,
  offlineMode: false,
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  toggleNotifications: () => set((state) => ({ notificationsEnabled: !state.notificationsEnabled })),
  toggleLocation: () => set((state) => ({ locationEnabled: !state.locationEnabled })),
  toggleOfflineMode: () => set((state) => ({ offlineMode: !state.offlineMode })),
}));
