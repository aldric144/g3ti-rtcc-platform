/**
 * G3TI RTCC Mobile App - Scene Coordination Screen
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
import { SceneRoleAssignmentWidget, DispatchCard } from '../components';
import { useAuthStore, useDispatchStore, useIncidentStore } from '../store';
import { api } from '../services/api';
import type { SceneCoordination, DispatchCall } from '../types';

export const SceneCoordinationScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [sceneCoordination, setSceneCoordination] = useState<SceneCoordination | null>(null);
  const [selectedCall, setSelectedCall] = useState<DispatchCall | null>(null);
  const { session } = useAuthStore();
  const { assignedCalls, setAssignedCalls } = useDispatchStore();
  const { activeIncidents, setIncidents, setLoading } = useIncidentStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadData = async () => {
    setLoading(true);
    try {
      const calls = await api.getActiveDispatch(badgeNumber);
      setAssignedCalls(calls);

      // If there's an assigned call, try to get scene coordination
      if (calls.length > 0) {
        setSelectedCall(calls[0]);
        // Scene coordination would be fetched from MDT API
      }
    } catch (error) {
      console.error('Failed to load scene data:', error);
    } finally {
      setLoading(false);
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

  // Mock scene coordination for display
  const mockCoordination: SceneCoordination = {
    call_id: selectedCall?.id || '',
    incident_commander: 'Sgt. Johnson',
    staging_location: '100 Main St - Parking Lot',
    assignments: [
      { unit_id: 'A1', badge_number: '1234', officer_name: 'Officer Smith', role: 'perimeter' },
      { unit_id: 'A2', badge_number: '5678', officer_name: 'Officer Davis', role: 'traffic' },
      { unit_id: 'D1', badge_number: '9012', officer_name: 'Det. Wilson', role: 'investigation' },
    ],
    perimeter_established: true,
    resources_on_scene: ['K9', 'Air Support', 'SWAT'],
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Scene Coordination</Text>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
      >
        {/* Active Call Selection */}
        {assignedCalls.length > 0 ? (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Active Scene</Text>
              {selectedCall && (
                <DispatchCard
                  call={selectedCall}
                  isAssigned
                  onPress={() => {}}
                />
              )}
            </View>

            {/* Scene Coordination Widget */}
            <SceneRoleAssignmentWidget coordination={mockCoordination} />

            {/* My Assignment */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>My Assignment</Text>
              <View style={styles.assignmentCard}>
                <View style={styles.assignmentHeader}>
                  <Ionicons name="shield" size={24} color="#ca8a04" />
                  <View style={styles.assignmentInfo}>
                    <Text style={styles.assignmentRole}>PERIMETER</Text>
                    <Text style={styles.assignmentUnit}>Unit {session?.user.unit_id || 'A1'}</Text>
                  </View>
                </View>
                <Text style={styles.assignmentNotes}>
                  Maintain perimeter on north side of building. Report any suspicious activity.
                </Text>
                <View style={styles.assignmentActions}>
                  <TouchableOpacity style={styles.actionButton}>
                    <Ionicons name="checkmark-circle" size={20} color="#22c55e" />
                    <Text style={styles.actionText}>In Position</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.actionButton}>
                    <Ionicons name="chatbubble" size={20} color="#3b82f6" />
                    <Text style={styles.actionText}>Report</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>

            {/* Quick Status Updates */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Quick Updates</Text>
              <View style={styles.quickButtons}>
                <TouchableOpacity style={[styles.quickButton, { backgroundColor: '#22c55e' }]}>
                  <Ionicons name="checkmark" size={24} color="#fff" />
                  <Text style={styles.quickButtonText}>Clear</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.quickButton, { backgroundColor: '#f59e0b' }]}>
                  <Ionicons name="eye" size={24} color="#fff" />
                  <Text style={styles.quickButtonText}>Activity</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.quickButton, { backgroundColor: '#dc2626' }]}>
                  <Ionicons name="alert" size={24} color="#fff" />
                  <Text style={styles.quickButtonText}>Urgent</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.quickButton, { backgroundColor: '#3b82f6' }]}>
                  <Ionicons name="hand-left" size={24} color="#fff" />
                  <Text style={styles.quickButtonText}>Backup</Text>
                </TouchableOpacity>
              </View>
            </View>
          </>
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={64} color="#6b7280" />
            <Text style={styles.emptyTitle}>No Active Scene</Text>
            <Text style={styles.emptyText}>
              You are not currently assigned to any active calls with scene coordination.
            </Text>
          </View>
        )}
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
    padding: 16,
    paddingTop: 60,
    backgroundColor: '#1f2937',
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  section: {
    marginBottom: 8,
  },
  sectionTitle: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  assignmentCard: {
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#ca8a04',
  },
  assignmentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  assignmentInfo: {
    marginLeft: 12,
  },
  assignmentRole: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
  assignmentUnit: {
    color: '#9ca3af',
    fontSize: 14,
  },
  assignmentNotes: {
    color: '#d1d5db',
    fontSize: 14,
    marginBottom: 16,
  },
  assignmentActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#374151',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  quickButtons: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    gap: 8,
  },
  quickButton: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
  },
  quickButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginTop: 4,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
  },
  emptyTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
    marginTop: 16,
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
  },
});
