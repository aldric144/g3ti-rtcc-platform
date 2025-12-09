/**
 * G3TI RTCC Mobile App - Dispatch Card Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { DispatchCall } from '../types';

interface DispatchCardProps {
  call: DispatchCall;
  onPress: () => void;
  isAssigned?: boolean;
}

const priorityColors: Record<number, string> = {
  1: '#dc2626',
  2: '#ea580c',
  3: '#ca8a04',
  4: '#2563eb',
  5: '#6b7280',
};

export const DispatchCard: React.FC<DispatchCardProps> = ({ call, onPress, isAssigned }) => {
  const color = priorityColors[call.priority] || '#6b7280';

  return (
    <TouchableOpacity 
      style={[styles.container, { borderLeftColor: color }, isAssigned && styles.assigned]} 
      onPress={onPress}
    >
      <View style={styles.header}>
        <View style={[styles.priorityBadge, { backgroundColor: color }]}>
          <Text style={styles.priorityText}>P{call.priority}</Text>
        </View>
        <Text style={styles.callNumber}>{call.call_number}</Text>
        <Text style={styles.status}>{call.status.toUpperCase()}</Text>
      </View>
      
      <Text style={styles.callType}>{call.call_type}</Text>
      
      <View style={styles.locationRow}>
        <Ionicons name="location" size={16} color="#9ca3af" />
        <Text style={styles.location} numberOfLines={1}>{call.location}</Text>
      </View>
      
      {call.description && (
        <Text style={styles.description} numberOfLines={2}>{call.description}</Text>
      )}
      
      <View style={styles.footer}>
        <View style={styles.unitsContainer}>
          <Ionicons name="people" size={14} color="#9ca3af" />
          <Text style={styles.unitsText}>{call.assigned_units.length} units</Text>
        </View>
        <Text style={styles.time}>
          {new Date(call.created_at).toLocaleTimeString()}
        </Text>
      </View>
      
      {call.hazards.length > 0 && (
        <View style={styles.hazardsContainer}>
          <Ionicons name="warning" size={14} color="#dc2626" />
          <Text style={styles.hazardsText}>{call.hazards.join(', ')}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1f2937',
    borderRadius: 8,
    padding: 12,
    marginVertical: 4,
    marginHorizontal: 8,
    borderLeftWidth: 4,
  },
  assigned: {
    backgroundColor: '#1e3a5f',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 8,
  },
  priorityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  callNumber: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  status: {
    color: '#9ca3af',
    fontSize: 12,
  },
  callType: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  location: {
    color: '#d1d5db',
    fontSize: 14,
    marginLeft: 4,
    flex: 1,
  },
  description: {
    color: '#9ca3af',
    fontSize: 13,
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  unitsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  unitsText: {
    color: '#9ca3af',
    fontSize: 12,
    marginLeft: 4,
  },
  time: {
    color: '#9ca3af',
    fontSize: 12,
  },
  hazardsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    backgroundColor: '#7f1d1d',
    padding: 6,
    borderRadius: 4,
  },
  hazardsText: {
    color: '#fca5a5',
    fontSize: 12,
    marginLeft: 4,
  },
});
