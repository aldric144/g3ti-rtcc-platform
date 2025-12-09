/**
 * G3TI RTCC Mobile App - Dashboard Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafetyIndicator, UnitStatusBadge, AlertCard, DispatchCard } from '../components';
import {
  useAuthStore,
  useAlertsStore,
  useDispatchStore,
  useSafetyStore,
  useUnitStore,
} from '../store';
import { api } from '../services/api';
import type { UnitStatus } from '../types';

interface DashboardScreenProps {
  onNavigate: (screen: string) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({ onNavigate }) => {
  const [refreshing, setRefreshing] = useState(false);
  const { session } = useAuthStore();
  const { alerts, setAlerts } = useAlertsStore();
  const { assignedCalls, setAssignedCalls } = useDispatchStore();
  const { status: safetyStatus, setStatus: setSafetyStatus } = useSafetyStore();
  const { currentStatus, setStatus } = useUnitStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadData = async () => {
    try {
      const [alertsData, dispatchData, safetyData] = await Promise.all([
        api.getAlerts(badgeNumber, undefined, 5),
        api.getActiveDispatch(badgeNumber),
        api.getSafetyStatus(badgeNumber),
      ]);

      setAlerts(alertsData);
      setAssignedCalls(dispatchData);
      setSafetyStatus(safetyData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  useEffect(() => {
    loadData();
  }, [badgeNumber]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleStatusChange = async (newStatus: UnitStatus) => {
    try {
      await api.updateUnitStatus(badgeNumber, session?.user.unit_id || '', newStatus);
      setStatus(newStatus);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const quickStatuses: { status: UnitStatus; label: string }[] = [
    { status: 'available', label: 'Available' },
    { status: 'en_route', label: 'En Route' },
    { status: 'on_scene', label: 'On Scene' },
    { status: 'reports', label: 'Reports' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.name}>{session?.user.name || `Officer ${badgeNumber}`}</Text>
        </View>
        <UnitStatusBadge status={currentStatus} size="medium" />
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
      >
        {/* Safety Status */}
        {safetyStatus && (
          <SafetyIndicator
            threatLevel={safetyStatus.threat_level}
            threatScore={safetyStatus.threat_score}
            inHotzone={safetyStatus.in_hotzone}
            nearbyThreats={safetyStatus.nearby_threats}
          />
        )}

        {/* Quick Status Buttons */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Status</Text>
          <View style={styles.statusButtons}>
            {quickStatuses.map((item) => (
              <TouchableOpacity
                key={item.status}
                style={[
                  styles.statusButton,
                  currentStatus === item.status && styles.statusButtonActive,
                ]}
                onPress={() => handleStatusChange(item.status)}
              >
                <Text
                  style={[
                    styles.statusButtonText,
                    currentStatus === item.status && styles.statusButtonTextActive,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Assigned Calls */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Assigned Calls</Text>
            <TouchableOpacity onPress={() => onNavigate('dispatch')}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          {assignedCalls.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="radio" size={32} color="#6b7280" />
              <Text style={styles.emptyText}>No assigned calls</Text>
            </View>
          ) : (
            assignedCalls.slice(0, 2).map((call) => (
              <DispatchCard
                key={call.id}
                call={call}
                isAssigned
                onPress={() => onNavigate('dispatch')}
              />
            ))
          )}
        </View>

        {/* Recent Alerts */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Alerts</Text>
            <TouchableOpacity onPress={() => onNavigate('alerts')}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          {alerts.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="notifications-off" size={32} color="#6b7280" />
              <Text style={styles.emptyText}>No recent alerts</Text>
            </View>
          ) : (
            alerts.slice(0, 3).map((alert) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onPress={() => onNavigate('alerts')}
              />
            ))
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity style={styles.actionButton} onPress={() => onNavigate('safety')}>
              <View style={[styles.actionIcon, { backgroundColor: '#dc2626' }]}>
                <Ionicons name="shield" size={24} color="#fff" />
              </View>
              <Text style={styles.actionText}>Safety</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={() => onNavigate('intel')}>
              <View style={[styles.actionIcon, { backgroundColor: '#7c3aed' }]}>
                <Ionicons name="document-text" size={24} color="#fff" />
              </View>
              <Text style={styles.actionText}>Intel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={() => onNavigate('messages')}>
              <View style={[styles.actionIcon, { backgroundColor: '#3b82f6' }]}>
                <Ionicons name="chatbubbles" size={24} color="#fff" />
              </View>
              <Text style={styles.actionText}>Messages</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={() => onNavigate('scene')}>
              <View style={[styles.actionIcon, { backgroundColor: '#ea580c' }]}>
                <Ionicons name="people" size={24} color="#fff" />
              </View>
              <Text style={styles.actionText}>Scene</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingTop: 60,
    backgroundColor: '#1f2937',
  },
  greeting: {
    color: '#9ca3af',
    fontSize: 14,
  },
  name: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  section: {
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  seeAll: {
    color: '#3b82f6',
    fontSize: 14,
  },
  statusButtons: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    gap: 8,
  },
  statusButton: {
    flex: 1,
    backgroundColor: '#374151',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  statusButtonActive: {
    backgroundColor: '#3b82f6',
  },
  statusButtonText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  statusButtonTextActive: {
    color: '#fff',
  },
  emptyState: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    borderRadius: 8,
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 8,
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    gap: 8,
  },
  actionButton: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: '#1f2937',
    padding: 16,
    borderRadius: 12,
  },
  actionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  actionText: {
    color: '#d1d5db',
    fontSize: 12,
    fontWeight: '500',
  },
});
