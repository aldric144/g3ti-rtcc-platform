/**
 * G3TI RTCC Mobile App - Intel Feed Screen
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
  ScrollView,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { IntelCard } from '../components';
import { useAuthStore, useIntelStore } from '../store';
import { api } from '../services/api';
import type { IntelPacket, IntelPacketType } from '../types';

export const IntelFeedScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<IntelPacketType | 'all'>('all');
  const [selectedPacket, setSelectedPacket] = useState<IntelPacket | null>(null);
  const { session } = useAuthStore();
  const { packets, setPackets, markRead, setLoading } = useIntelStore();

  const badgeNumber = session?.user.badge_number || '';

  const loadIntel = async () => {
    setLoading(true);
    try {
      const data = await api.getIntelFeed(badgeNumber, 100);
      setPackets(data);
    } catch (error) {
      console.error('Failed to load intel:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIntel();
  }, [badgeNumber]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadIntel();
    setRefreshing(false);
  };

  const handlePacketPress = async (packet: IntelPacket) => {
    setSelectedPacket(packet);
    try {
      await api.markIntelRead(packet.id, badgeNumber);
      markRead(packet.id);
    } catch (error) {
      console.error('Failed to mark intel read:', error);
    }
  };

  const filteredPackets = filter === 'all'
    ? packets
    : packets.filter(p => p.packet_type === filter);

  const filters: { key: IntelPacketType | 'all'; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'vehicle', label: 'Vehicle' },
    { key: 'person', label: 'Person' },
    { key: 'location', label: 'Location' },
    { key: 'officer_safety', label: 'Safety' },
    { key: 'bulletin', label: 'Bulletin' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Intel Feed</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{packets.filter(p => p.is_critical).length}</Text>
        </View>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterContainer}>
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterButton, filter === f.key && styles.filterButtonActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <FlatList
        data={filteredPackets}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <IntelCard packet={item} onPress={() => handlePacketPress(item)} />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="document-text-outline" size={48} color="#6b7280" />
            <Text style={styles.emptyText}>No intel packets</Text>
          </View>
        }
      />

      {/* Intel Detail Modal */}
      <Modal
        visible={!!selectedPacket}
        transparent
        animationType="slide"
        onRequestClose={() => setSelectedPacket(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{selectedPacket?.title}</Text>
              <TouchableOpacity onPress={() => setSelectedPacket(null)}>
                <Ionicons name="close" size={24} color="#9ca3af" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {selectedPacket?.is_critical && (
                <View style={styles.criticalBanner}>
                  <Ionicons name="alert-circle" size={20} color="#fff" />
                  <Text style={styles.criticalText}>CRITICAL INTEL</Text>
                </View>
              )}

              <Text style={styles.summary}>{selectedPacket?.summary}</Text>

              {selectedPacket?.images && selectedPacket.images.length > 0 && (
                <ScrollView horizontal style={styles.imagesContainer}>
                  {selectedPacket.images.map((uri, index) => (
                    <Image key={index} source={{ uri }} style={styles.image} />
                  ))}
                </ScrollView>
              )}

              {selectedPacket?.location && (
                <View style={styles.detailRow}>
                  <Ionicons name="location" size={16} color="#9ca3af" />
                  <Text style={styles.detailText}>{selectedPacket.location}</Text>
                </View>
              )}

              {selectedPacket?.safety_notes && selectedPacket.safety_notes.length > 0 && (
                <View style={styles.safetySection}>
                  <Text style={styles.sectionLabel}>Safety Notes</Text>
                  {selectedPacket.safety_notes.map((note, index) => (
                    <View key={index} style={styles.safetyNote}>
                      <Ionicons name="warning" size={14} color="#fbbf24" />
                      <Text style={styles.safetyNoteText}>{note.content}</Text>
                    </View>
                  ))}
                </View>
              )}

              {selectedPacket?.details && Object.keys(selectedPacket.details).length > 0 && (
                <View style={styles.detailsSection}>
                  <Text style={styles.sectionLabel}>Details</Text>
                  {Object.entries(selectedPacket.details).map(([key, value]) => (
                    value && (
                      <View key={key} style={styles.detailItem}>
                        <Text style={styles.detailKey}>{key.replace('_', ' ')}:</Text>
                        <Text style={styles.detailValue}>
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </Text>
                      </View>
                    )
                  ))}
                </View>
              )}

              <View style={styles.footer}>
                <Text style={styles.footerText}>
                  {selectedPacket?.packet_type.replace('_', ' ').toUpperCase()}
                </Text>
                <Text style={styles.footerText}>
                  {selectedPacket && new Date(selectedPacket.created_at).toLocaleString()}
                </Text>
              </View>
            </ScrollView>
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
    backgroundColor: '#7c3aed',
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
    paddingHorizontal: 8,
    paddingVertical: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#374151',
    marginHorizontal: 4,
  },
  filterButtonActive: {
    backgroundColor: '#7c3aed',
  },
  filterText: {
    color: '#9ca3af',
    fontSize: 14,
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1f2937',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  modalTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    flex: 1,
    marginRight: 16,
  },
  modalBody: {
    padding: 16,
  },
  criticalBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#dc2626',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  criticalText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
    marginLeft: 8,
  },
  summary: {
    color: '#d1d5db',
    fontSize: 16,
    marginBottom: 16,
  },
  imagesContainer: {
    marginBottom: 16,
  },
  image: {
    width: 200,
    height: 150,
    borderRadius: 8,
    marginRight: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailText: {
    color: '#9ca3af',
    fontSize: 14,
    marginLeft: 8,
  },
  safetySection: {
    marginTop: 16,
  },
  sectionLabel: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  safetyNote: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#422006',
    padding: 10,
    borderRadius: 6,
    marginBottom: 8,
  },
  safetyNoteText: {
    color: '#fbbf24',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  detailsSection: {
    marginTop: 16,
  },
  detailItem: {
    flexDirection: 'row',
    marginBottom: 4,
  },
  detailKey: {
    color: '#9ca3af',
    fontSize: 14,
    textTransform: 'capitalize',
    marginRight: 8,
  },
  detailValue: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#374151',
  },
  footerText: {
    color: '#6b7280',
    fontSize: 12,
  },
});
