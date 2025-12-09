/**
 * G3TI RTCC Mobile App - Scene Role Assignment Widget Component
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { SceneCoordination } from '../types';

interface SceneRoleAssignmentWidgetProps {
  coordination: SceneCoordination;
}

const roleColors: Record<string, string> = {
  incident_commander: '#dc2626',
  operations: '#ea580c',
  perimeter: '#ca8a04',
  traffic: '#2563eb',
  investigation: '#7c3aed',
  medical: '#ec4899',
  support: '#6b7280',
  other: '#374151',
};

const roleIcons: Record<string, keyof typeof Ionicons.glyphMap> = {
  incident_commander: 'star',
  operations: 'settings',
  perimeter: 'shield',
  traffic: 'car',
  investigation: 'search',
  medical: 'medkit',
  support: 'people',
  other: 'ellipsis-horizontal',
};

export const SceneRoleAssignmentWidget: React.FC<SceneRoleAssignmentWidgetProps> = ({
  coordination,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Scene Coordination</Text>
        {coordination.perimeter_established && (
          <View style={styles.perimeterBadge}>
            <Ionicons name="shield-checkmark" size={14} color="#22c55e" />
            <Text style={styles.perimeterText}>Perimeter Set</Text>
          </View>
        )}
      </View>

      {coordination.incident_commander && (
        <View style={styles.commanderRow}>
          <Ionicons name="star" size={16} color="#fbbf24" />
          <Text style={styles.commanderLabel}>IC:</Text>
          <Text style={styles.commanderName}>{coordination.incident_commander}</Text>
        </View>
      )}

      {coordination.staging_location && (
        <View style={styles.stagingRow}>
          <Ionicons name="location" size={16} color="#3b82f6" />
          <Text style={styles.stagingText}>{coordination.staging_location}</Text>
        </View>
      )}

      <Text style={styles.sectionTitle}>Assigned Units</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.assignmentsList}>
        {coordination.assignments.map((assignment, index) => {
          const color = roleColors[assignment.role] || roleColors.other;
          const icon = roleIcons[assignment.role] || roleIcons.other;
          return (
            <View key={index} style={[styles.assignmentCard, { borderLeftColor: color }]}>
              <View style={styles.assignmentHeader}>
                <Ionicons name={icon} size={14} color={color} />
                <Text style={styles.roleName}>{assignment.role.replace('_', ' ')}</Text>
              </View>
              <Text style={styles.unitId}>{assignment.unit_id}</Text>
              <Text style={styles.officerName}>{assignment.officer_name}</Text>
            </View>
          );
        })}
      </ScrollView>

      {coordination.resources_on_scene.length > 0 && (
        <View style={styles.resourcesSection}>
          <Text style={styles.sectionTitle}>Resources On Scene</Text>
          <View style={styles.resourcesList}>
            {coordination.resources_on_scene.map((resource, index) => (
              <View key={index} style={styles.resourceBadge}>
                <Text style={styles.resourceText}>{resource}</Text>
              </View>
            ))}
          </View>
        </View>
      )}
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  perimeterBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#14532d',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  perimeterText: {
    color: '#22c55e',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  commanderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#374151',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  commanderLabel: {
    color: '#9ca3af',
    fontSize: 14,
    marginLeft: 8,
  },
  commanderName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
  stagingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stagingText: {
    color: '#d1d5db',
    fontSize: 14,
    marginLeft: 8,
  },
  sectionTitle: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  assignmentsList: {
    marginBottom: 12,
  },
  assignmentCard: {
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 10,
    marginRight: 8,
    borderLeftWidth: 3,
    minWidth: 100,
  },
  assignmentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  roleName: {
    color: '#9ca3af',
    fontSize: 10,
    textTransform: 'uppercase',
    marginLeft: 4,
  },
  unitId: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  officerName: {
    color: '#d1d5db',
    fontSize: 12,
  },
  resourcesSection: {
    marginTop: 8,
  },
  resourcesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  resourceBadge: {
    backgroundColor: '#374151',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  resourceText: {
    color: '#d1d5db',
    fontSize: 12,
  },
});
