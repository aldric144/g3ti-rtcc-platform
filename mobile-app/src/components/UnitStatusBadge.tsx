/**
 * G3TI RTCC Mobile App - Unit Status Badge Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { UnitStatus } from '../types';

interface UnitStatusBadgeProps {
  status: UnitStatus;
  onPress?: () => void;
  showLabel?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const statusConfig: Record<UnitStatus, { color: string; label: string; icon: keyof typeof Ionicons.glyphMap }> = {
  available: { color: '#22c55e', label: 'Available', icon: 'checkmark-circle' },
  en_route: { color: '#3b82f6', label: 'En Route', icon: 'navigate' },
  on_scene: { color: '#f59e0b', label: 'On Scene', icon: 'location' },
  transporting: { color: '#8b5cf6', label: 'Transporting', icon: 'car' },
  at_hospital: { color: '#ec4899', label: 'At Hospital', icon: 'medkit' },
  reports: { color: '#6366f1', label: 'Reports', icon: 'document-text' },
  out_of_service: { color: '#ef4444', label: 'Out of Service', icon: 'close-circle' },
  off_duty: { color: '#6b7280', label: 'Off Duty', icon: 'moon' },
};

export const UnitStatusBadge: React.FC<UnitStatusBadgeProps> = ({
  status,
  onPress,
  showLabel = true,
  size = 'medium',
}) => {
  const config = statusConfig[status];
  const sizeStyles = {
    small: { padding: 4, fontSize: 10, iconSize: 12 },
    medium: { padding: 8, fontSize: 12, iconSize: 16 },
    large: { padding: 12, fontSize: 14, iconSize: 20 },
  };
  const s = sizeStyles[size];

  const content = (
    <View style={[styles.container, { backgroundColor: config.color, padding: s.padding }]}>
      <Ionicons name={config.icon} size={s.iconSize} color="#fff" />
      {showLabel && (
        <Text style={[styles.label, { fontSize: s.fontSize }]}>{config.label}</Text>
      )}
    </View>
  );

  if (onPress) {
    return <TouchableOpacity onPress={onPress}>{content}</TouchableOpacity>;
  }

  return content;
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 6,
  },
  label: {
    color: '#fff',
    fontWeight: '600',
    marginLeft: 6,
  },
});
