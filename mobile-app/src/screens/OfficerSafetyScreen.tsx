/**
 * G3TI RTCC Mobile App - Officer Safety Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import { SafetyIndicator } from '../components';
import { useAuthStore, useSafetyStore } from '../store';
import { api } from '../services/api';
import type { ProximityWarning, CheckInType } from '../types';

export const OfficerSafetyScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [checkingIn, setCheckingIn] = useState(false);
  const { session } = useAuthStore();
  const { status, warnings, setStatus, setWarnings, acknowledgeWarning, setLoading } = useSafetyStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadSafetyData = async () => {
    setLoading(true);
    try {
      const [safetyStatus, warningsData] = await Promise.all([
        api.getSafetyStatus(badgeNumber),
        api.getProximityWarnings(badgeNumber),
      ]);
      setStatus(safetyStatus);
      setWarnings(warningsData);
    } catch (error) {
      console.error('Failed to load safety data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSafetyData();
  }, [badgeNumber]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSafetyData();
    setRefreshing(false);
  };

  const handleCheckIn = async (type: CheckInType) => {
    setCheckingIn(true);
    try {
      const { status: permStatus } = await Location.requestForegroundPermissionsAsync();
      let latitude: number | undefined;
      let longitude: number | undefined;

      if (permStatus === 'granted') {
        const location = await Location.getCurrentPositionAsync({});
        latitude = location.coords.latitude;
        longitude = location.coords.longitude;
      }

      await api.checkIn(badgeNumber, type, latitude, longitude);
      Alert.alert('Check-In Recorded', `Your ${type} check-in has been recorded.`);
      await loadSafetyData();
    } catch (error) {
      console.error('Failed to check in:', error);
      Alert.alert('Error', 'Failed to record check-in');
    } finally {
      setCheckingIn(false);
    }
  };

  const handleAcknowledgeWarning = async (warning: ProximityWarning) => {
    try {
      await api.acknowledgeWarning(warning.id, badgeNumber);
      acknowledgeWarning(warning.id);
    } catch (error) {
      console.error('Failed to acknowledge warning:', error);
    }
  };

  const threatLevelColors: Record<string, string> = {
    critical: '#dc2626',
    high: '#ea580c',
    elevated: '#ca8a04',
    moderate: '#eab308',
    low: '#22c55e',
    minimal: '#10b981',
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Officer Safety</Text>
        {status && (
          <View style={[styles.statusBadge, { backgroundColor: threatLevelColors[status.threat_level] }]}>
            <Text style={styles.statusText}>{status.threat_level.toUpperCase()}</Text>
          </View>
        )}
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
      >
        {/* Safety Status */}
        {status && (
          <SafetyIndicator
            threatLevel={status.threat_level}
            threatScore={status.threat_score}
            inHotzone={status.in_hotzone}
            nearbyThreats={status.nearby_threats}
          />
        )}

        {/* Check-In Buttons */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Check-In</Text>
          <View style={styles.checkInButtons}>
            <TouchableOpacity
              style={[styles.checkInButton, styles.safeButton]}
              onPress={() => handleCheckIn('safe')}
              disabled={checkingIn}
            >
              <Ionicons name="checkmark-circle" size={32} color="#fff" />
              <Text style={styles.checkInText}>I'm Safe</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.checkInButton, styles.routineButton]}
              onPress={() => handleCheckIn('routine')}
              disabled={checkingIn}
            >
              <Ionicons name="radio" size={32} color="#fff" />
              <Text style={styles.checkInText}>Routine</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.checkInButton, styles.emergencyButton]}
              onPress={() => handleCheckIn('emergency')}
              disabled={checkingIn}
            >
              <Ionicons name="alert-circle" size={32} color="#fff" />
              <Text style={styles.checkInText}>Emergency</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Proximity Warnings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Proximity Warnings ({warnings.filter(w => !w.acknowledged).length})
          </Text>
          {warnings.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="shield-checkmark" size={32} color="#22c55e" />
              <Text style={styles.emptyText}>No active warnings</Text>
            </View>
          ) : (
            warnings.map((warning) => (
              <View
                key={warning.id}
                style={[
                  styles.warningCard,
                  { borderLeftColor: threatLevelColors[warning.threat_level] },
                  warning.acknowledged && styles.warningAcknowledged,
                ]}
              >
                <View style={styles.warningHeader}>
                  <Ionicons
                    name="warning"
                    size={20}
                    color={threatLevelColors[warning.threat_level]}
                  />
                  <Text style={styles.warningTitle}>{warning.title}</Text>
                  <Text style={styles.warningDistance}>
                    {Math.round(warning.distance_meters)}m
                  </Text>
                </View>
                <Text style={styles.warningDescription}>{warning.description}</Text>
                {warning.direction && (
                  <Text style={styles.warningDirection}>Direction: {warning.direction}</Text>
                )}
                {!warning.acknowledged && (
                  <TouchableOpacity
                    style={styles.ackButton}
                    onPress={() => handleAcknowledgeWarning(warning)}
                  >
                    <Text style={styles.ackButtonText}>Acknowledge</Text>
                  </TouchableOpacity>
                )}
              </View>
            ))
          )}
        </View>

        {/* Last Check-In */}
        {status?.last_check_in && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Last Check-In</Text>
            <View style={styles.lastCheckIn}>
              <Ionicons name="time" size={20} color="#9ca3af" />
              <Text style={styles.lastCheckInText}>
                {new Date(status.last_check_in).toLocaleString()}
              </Text>
            </View>
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
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  checkInButtons: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    gap: 8,
  },
  checkInButton: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
  },
  safeButton: {
    backgroundColor: '#22c55e',
  },
  routineButton: {
    backgroundColor: '#3b82f6',
  },
  emergencyButton: {
    backgroundColor: '#dc2626',
  },
  checkInText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginTop: 4,
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
  warningCard: {
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    marginVertical: 4,
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
  },
  warningAcknowledged: {
    opacity: 0.6,
  },
  warningHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  warningTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
    marginLeft: 8,
  },
  warningDistance: {
    color: '#9ca3af',
    fontSize: 14,
  },
  warningDescription: {
    color: '#d1d5db',
    fontSize: 14,
    marginBottom: 4,
  },
  warningDirection: {
    color: '#9ca3af',
    fontSize: 12,
    marginBottom: 8,
  },
  ackButton: {
    backgroundColor: '#374151',
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  ackButtonText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: '600',
  },
  lastCheckIn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    padding: 12,
    borderRadius: 8,
  },
  lastCheckInText: {
    color: '#d1d5db',
    fontSize: 14,
    marginLeft: 8,
  },
});
