/**
 * G3TI RTCC Mobile App - Alerts Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AlertCard } from '../components';
import { useAuthStore, useAlertsStore } from '../store';
import { api } from '../services/api';
import type { MobileAlert, AlertPriority } from '../types';

export const AlertsScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<AlertPriority | 'all'>('all');
  const { session } = useAuthStore();
  const { alerts, setAlerts, markRead, markAcknowledged, setLoading } = useAlertsStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts(badgeNumber, undefined, 100);
      setAlerts(data);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [badgeNumber]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAlerts();
    setRefreshing(false);
  };

  const handleAlertPress = async (alert: MobileAlert) => {
    if (!alert.read) {
      try {
        await api.markAlertRead(alert.id, badgeNumber);
        markRead(alert.id);
      } catch (error) {
        console.error('Failed to mark alert read:', error);
      }
    }
  };

  const handleAcknowledge = async (alert: MobileAlert) => {
    try {
      await api.acknowledgeAlert(alert.id, badgeNumber);
      markAcknowledged(alert.id);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.priority === filter);

  const filters: { key: AlertPriority | 'all'; label: string; color: string }[] = [
    { key: 'all', label: 'All', color: '#6b7280' },
    { key: 'critical', label: 'Critical', color: '#dc2626' },
    { key: 'high', label: 'High', color: '#ea580c' },
    { key: 'medium', label: 'Medium', color: '#ca8a04' },
    { key: 'low', label: 'Low', color: '#2563eb' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Alerts</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{alerts.filter(a => !a.read).length}</Text>
        </View>
      </View>

      <View style={styles.filterContainer}>
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[
              styles.filterButton,
              filter === f.key && { backgroundColor: f.color },
            ]}
            onPress={() => setFilter(f.key)}
          >
            <Text
              style={[
                styles.filterText,
                filter === f.key && styles.filterTextActive,
              ]}
            >
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredAlerts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <AlertCard
            alert={item}
            onPress={() => handleAlertPress(item)}
            onAcknowledge={() => handleAcknowledge(item)}
          />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="notifications-off" size={48} color="#6b7280" />
            <Text style={styles.emptyText}>No alerts</Text>
          </View>
        }
        contentContainerStyle={filteredAlerts.length === 0 && styles.emptyContainer}
      />
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
  badge: {
    backgroundColor: '#dc2626',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginLeft: 8,
  },
  badgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 8,
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#374151',
  },
  filterText: {
    color: '#9ca3af',
    fontSize: 13,
    fontWeight: '500',
  },
  filterTextActive: {
    color: '#fff',
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
  emptyContainer: {
    flex: 1,
  },
});
