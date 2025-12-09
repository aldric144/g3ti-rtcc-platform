/**
 * G3TI RTCC Mobile App - Intel Card Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { IntelPacket, AlertPriority } from '../types';

interface IntelCardProps {
  packet: IntelPacket;
  onPress: () => void;
}

const priorityColors: Record<AlertPriority, string> = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#ca8a04',
  low: '#2563eb',
  info: '#6b7280',
};

const typeIcons: Record<string, keyof typeof Ionicons.glyphMap> = {
  vehicle: 'car',
  person: 'person',
  location: 'location',
  officer_safety: 'shield',
  bulletin: 'document-text',
  command_note: 'clipboard',
  bolo: 'eye',
  warrant: 'document',
  gunfire: 'flash',
  lpr_hit: 'scan',
  general: 'information-circle',
};

export const IntelCard: React.FC<IntelCardProps> = ({ packet, onPress }) => {
  const color = priorityColors[packet.priority];
  const icon = typeIcons[packet.packet_type] || 'information-circle';

  return (
    <TouchableOpacity 
      style={[styles.container, { borderLeftColor: color }, packet.is_critical && styles.critical]} 
      onPress={onPress}
    >
      <View style={styles.header}>
        <View style={styles.iconContainer}>
          <Ionicons name={icon} size={20} color={color} />
        </View>
        <View style={styles.titleContainer}>
          <Text style={styles.title} numberOfLines={1}>{packet.title}</Text>
          <Text style={styles.type}>{packet.packet_type.replace('_', ' ').toUpperCase()}</Text>
        </View>
        {packet.is_critical && (
          <View style={[styles.badge, { backgroundColor: '#dc2626' }]}>
            <Text style={styles.badgeText}>CRITICAL</Text>
          </View>
        )}
      </View>

      <Text style={styles.summary} numberOfLines={2}>{packet.summary}</Text>

      {packet.images.length > 0 && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: packet.images[0] }} style={styles.thumbnail} />
          {packet.images.length > 1 && (
            <View style={styles.moreImages}>
              <Text style={styles.moreImagesText}>+{packet.images.length - 1}</Text>
            </View>
          )}
        </View>
      )}

      {packet.location && (
        <View style={styles.locationRow}>
          <Ionicons name="location" size={14} color="#9ca3af" />
          <Text style={styles.locationText} numberOfLines={1}>{packet.location}</Text>
        </View>
      )}

      {packet.safety_notes.length > 0 && (
        <View style={styles.safetyContainer}>
          <Ionicons name="warning" size={14} color="#fbbf24" />
          <Text style={styles.safetyText} numberOfLines={1}>
            {packet.safety_notes[0].content}
          </Text>
        </View>
      )}

      <View style={styles.footer}>
        <Text style={styles.source}>{packet.details.source as string || 'RTCC'}</Text>
        <Text style={styles.time}>
          {new Date(packet.created_at).toLocaleTimeString()}
        </Text>
      </View>
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
  critical: {
    backgroundColor: '#450a0a',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#374151',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  titleContainer: {
    flex: 1,
  },
  title: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
  type: {
    color: '#9ca3af',
    fontSize: 11,
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  summary: {
    color: '#d1d5db',
    fontSize: 14,
    marginBottom: 8,
  },
  imageContainer: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  thumbnail: {
    width: 60,
    height: 60,
    borderRadius: 4,
  },
  moreImages: {
    width: 60,
    height: 60,
    borderRadius: 4,
    backgroundColor: '#374151',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 4,
  },
  moreImagesText: {
    color: '#9ca3af',
    fontSize: 14,
    fontWeight: '600',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  locationText: {
    color: '#9ca3af',
    fontSize: 13,
    marginLeft: 4,
    flex: 1,
  },
  safetyContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#422006',
    padding: 6,
    borderRadius: 4,
    marginBottom: 8,
  },
  safetyText: {
    color: '#fbbf24',
    fontSize: 12,
    marginLeft: 4,
    flex: 1,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  source: {
    color: '#6b7280',
    fontSize: 12,
  },
  time: {
    color: '#6b7280',
    fontSize: 12,
  },
});
