/**
 * G3TI RTCC Mobile App - Safety Indicator Component
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ThreatLevel } from '../types';

interface SafetyIndicatorProps {
  threatLevel: ThreatLevel;
  threatScore: number;
  inHotzone?: boolean;
  nearbyThreats?: number;
  compact?: boolean;
}

const threatColors: Record<ThreatLevel, string> = {
  critical: '#dc2626',
  high: '#ea580c',
  elevated: '#ca8a04',
  moderate: '#eab308',
  low: '#22c55e',
  minimal: '#10b981',
};

const threatLabels: Record<ThreatLevel, string> = {
  critical: 'CRITICAL',
  high: 'HIGH',
  elevated: 'ELEVATED',
  moderate: 'MODERATE',
  low: 'LOW',
  minimal: 'MINIMAL',
};

export const SafetyIndicator: React.FC<SafetyIndicatorProps> = ({
  threatLevel,
  threatScore,
  inHotzone,
  nearbyThreats,
  compact,
}) => {
  const color = threatColors[threatLevel];
  const label = threatLabels[threatLevel];

  if (compact) {
    return (
      <View style={[styles.compactContainer, { backgroundColor: color }]}>
        <Ionicons name="shield" size={14} color="#fff" />
        <Text style={styles.compactText}>{label}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={[styles.levelIndicator, { backgroundColor: color }]}>
        <Ionicons name="shield-checkmark" size={32} color="#fff" />
        <Text style={styles.levelText}>{label}</Text>
        <Text style={styles.scoreText}>{Math.round(threatScore * 100)}%</Text>
      </View>
      
      <View style={styles.detailsContainer}>
        {inHotzone && (
          <View style={styles.warningRow}>
            <Ionicons name="flame" size={16} color="#dc2626" />
            <Text style={styles.warningText}>IN HOTZONE</Text>
          </View>
        )}
        
        {nearbyThreats !== undefined && nearbyThreats > 0 && (
          <View style={styles.warningRow}>
            <Ionicons name="warning" size={16} color="#ea580c" />
            <Text style={styles.warningText}>{nearbyThreats} nearby threats</Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    margin: 8,
  },
  levelIndicator: {
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  levelText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    marginTop: 8,
  },
  scoreText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
    marginTop: 4,
  },
  detailsContainer: {
    gap: 8,
  },
  warningRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#374151',
    padding: 8,
    borderRadius: 6,
  },
  warningText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 8,
    fontWeight: '500',
  },
  compactContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  compactText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
});
