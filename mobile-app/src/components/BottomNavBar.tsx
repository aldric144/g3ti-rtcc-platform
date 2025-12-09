/**
 * G3TI RTCC Mobile App - Bottom Navigation Bar Component
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NavItem {
  key: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  iconActive: keyof typeof Ionicons.glyphMap;
  badge?: number;
}

interface BottomNavBarProps {
  activeTab: string;
  onTabPress: (tab: string) => void;
  items: NavItem[];
}

export const BottomNavBar: React.FC<BottomNavBarProps> = ({
  activeTab,
  onTabPress,
  items,
}) => {
  return (
    <View style={styles.container}>
      {items.map((item) => {
        const isActive = activeTab === item.key;
        return (
          <TouchableOpacity
            key={item.key}
            style={styles.tab}
            onPress={() => onTabPress(item.key)}
          >
            <View style={styles.iconContainer}>
              <Ionicons
                name={isActive ? item.iconActive : item.icon}
                size={24}
                color={isActive ? '#3b82f6' : '#9ca3af'}
              />
              {item.badge !== undefined && item.badge > 0 && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>
                    {item.badge > 99 ? '99+' : item.badge}
                  </Text>
                </View>
              )}
            </View>
            <Text style={[styles.label, isActive && styles.labelActive]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#111827',
    borderTopWidth: 1,
    borderTopColor: '#374151',
    paddingBottom: 20,
    paddingTop: 8,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -8,
    backgroundColor: '#dc2626',
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 4,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  label: {
    color: '#9ca3af',
    fontSize: 11,
    marginTop: 4,
  },
  labelActive: {
    color: '#3b82f6',
    fontWeight: '600',
  },
});
