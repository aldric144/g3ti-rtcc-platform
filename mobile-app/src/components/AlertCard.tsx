/**
 * G3TI RTCC Mobile App - Alert Card Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { MobileAlert, AlertPriority } from '../types';

interface AlertCardProps {
  alert: MobileAlert;
  onPress: () => void;
  onAcknowledge?: () => void;
}

const priorityColors: Record<AlertPriority, string> = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#ca8a04',
  low: '#2563eb',
  info: '#6b7280',
};

const priorityIcons: Record<AlertPriority, keyof typeof Ionicons.glyphMap> = {
  critical: 'alert-circle',
  high: 'warning',
  medium: 'information-circle',
  low: 'notifications',
  info: 'information',
};

export const AlertCard: React.FC<AlertCardProps> = ({ alert, onPress, onAcknowledge }) => {
  const color = priorityColors[alert.priority];
  const icon = priorityIcons[alert.priority];

  return (
    <TouchableOpacity style={[styles.container, { borderLeftColor: color }]} onPress={onPress}>
      <View style={styles.iconContainer}>
        <Ionicons name={icon} size={24} color={color} />
      </View>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title} numberOfLines={1}>{alert.title}</Text>
          <Text style={styles.time}>
            {new Date(alert.created_at).toLocaleTimeString()}
          </Text>
        </View>
        <Text style={styles.body} numberOfLines={2}>{alert.body}</Text>
        <View style={styles.footer}>
          <View style={[styles.badge, { backgroundColor: color }]}>
            <Text style={styles.badgeText}>{alert.priority.toUpperCase()}</Text>
          </View>
          <Text style={styles.type}>{alert.alert_type}</Text>
          {!alert.acknowledged && onAcknowledge && (
            <TouchableOpacity style={styles.ackButton} onPress={onAcknowledge}>
              <Text style={styles.ackText}>ACK</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
      {!alert.read && <View style={styles.unreadDot} />}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#1f2937',
    borderRadius: 8,
    padding: 12,
    marginVertical: 4,
    marginHorizontal: 8,
    borderLeftWidth: 4,
  },
  iconContainer: {
    marginRight: 12,
    justifyContent: 'center',
  },
  content: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  title: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  time: {
    color: '#9ca3af',
    fontSize: 12,
    marginLeft: 8,
  },
  body: {
    color: '#d1d5db',
    fontSize: 14,
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 8,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  type: {
    color: '#9ca3af',
    fontSize: 12,
    flex: 1,
  },
  ackButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 4,
  },
  ackText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3b82f6',
    position: 'absolute',
    top: 8,
    right: 8,
  },
});
