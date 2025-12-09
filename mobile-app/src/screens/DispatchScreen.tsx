/**
 * G3TI RTCC Mobile App - Dispatch Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DispatchCard, UnitStatusBadge } from '../components';
import { useAuthStore, useDispatchStore, useUnitStore } from '../store';
import { api } from '../services/api';
import type { DispatchCall, UnitStatus } from '../types';

export const DispatchScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedCall, setSelectedCall] = useState<DispatchCall | null>(null);
  const { session } = useAuthStore();
  const { activeCalls, assignedCalls, setCalls, setAssignedCalls, setLoading } = useDispatchStore();
  const { currentStatus, setStatus } = useUnitStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadDispatch = async () => {
    setLoading(true);
    try {
      const [allCalls, myCalls] = await Promise.all([
        api.getActiveDispatch(),
        api.getActiveDispatch(badgeNumber),
      ]);
      setCalls(allCalls);
      setAssignedCalls(myCalls);
    } catch (error) {
      console.error('Failed to load dispatch:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDispatch();
  }, [badgeNumber]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDispatch();
    setRefreshing(false);
  };

  const handleStatusChange = async (newStatus: UnitStatus) => {
    try {
      await api.updateUnitStatus(
        badgeNumber,
        session?.user.unit_id || '',
        newStatus,
        undefined,
        undefined,
        undefined,
        selectedCall?.id
      );
      setStatus(newStatus);
      setShowStatusModal(false);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const handleCallPress = (call: DispatchCall) => {
    setSelectedCall(call);
    setShowStatusModal(true);
  };

  const statuses: { status: UnitStatus; label: string; icon: keyof typeof Ionicons.glyphMap }[] = [
    { status: 'en_route', label: 'En Route', icon: 'navigate' },
    { status: 'on_scene', label: 'On Scene', icon: 'location' },
    { status: 'transporting', label: 'Transporting', icon: 'car' },
    { status: 'at_hospital', label: 'At Hospital', icon: 'medkit' },
    { status: 'available', label: 'Clear/Available', icon: 'checkmark-circle' },
    { status: 'reports', label: 'Reports', icon: 'document-text' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Dispatch</Text>
          <Text style={styles.subtitle}>{activeCalls.length} active calls</Text>
        </View>
        <UnitStatusBadge status={currentStatus} onPress={() => setShowStatusModal(true)} />
      </View>

      {assignedCalls.length > 0 && (
        <View style={styles.assignedSection}>
          <Text style={styles.sectionTitle}>My Assigned Calls</Text>
          {assignedCalls.map((call) => (
            <DispatchCard
              key={call.id}
              call={call}
              isAssigned
              onPress={() => handleCallPress(call)}
            />
          ))}
        </View>
      )}

      <Text style={styles.sectionTitle}>All Active Calls</Text>
      <FlatList
        data={activeCalls}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <DispatchCard
            call={item}
            isAssigned={assignedCalls.some(c => c.id === item.id)}
            onPress={() => handleCallPress(item)}
          />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="radio" size={48} color="#6b7280" />
            <Text style={styles.emptyText}>No active calls</Text>
          </View>
        }
      />

      <Modal
        visible={showStatusModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowStatusModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Update Status</Text>
              <TouchableOpacity onPress={() => setShowStatusModal(false)}>
                <Ionicons name="close" size={24} color="#9ca3af" />
              </TouchableOpacity>
            </View>
            {selectedCall && (
              <View style={styles.callInfo}>
                <Text style={styles.callNumber}>{selectedCall.call_number}</Text>
                <Text style={styles.callType}>{selectedCall.call_type}</Text>
              </View>
            )}
            <View style={styles.statusList}>
              {statuses.map((item) => (
                <TouchableOpacity
                  key={item.status}
                  style={[
                    styles.statusOption,
                    currentStatus === item.status && styles.statusOptionActive,
                  ]}
                  onPress={() => handleStatusChange(item.status)}
                >
                  <Ionicons
                    name={item.icon}
                    size={24}
                    color={currentStatus === item.status ? '#3b82f6' : '#9ca3af'}
                  />
                  <Text
                    style={[
                      styles.statusLabel,
                      currentStatus === item.status && styles.statusLabelActive,
                    ]}
                  >
                    {item.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      </Modal>
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
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
  },
  subtitle: {
    color: '#9ca3af',
    fontSize: 14,
  },
  assignedSection: {
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
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 16,
    marginTop: 12,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1f2937',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: 40,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  callInfo: {
    backgroundColor: '#374151',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  callNumber: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  callType: {
    color: '#9ca3af',
    fontSize: 14,
  },
  statusList: {
    gap: 8,
  },
  statusOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#374151',
    borderRadius: 12,
  },
  statusOptionActive: {
    backgroundColor: '#1e3a5f',
    borderColor: '#3b82f6',
    borderWidth: 1,
  },
  statusLabel: {
    color: '#d1d5db',
    fontSize: 16,
    marginLeft: 12,
  },
  statusLabelActive: {
    color: '#3b82f6',
    fontWeight: '600',
  },
});
