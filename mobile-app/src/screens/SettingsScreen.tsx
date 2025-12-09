/**
 * G3TI RTCC Mobile App - Settings Screen
 */

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore, useSettingsStore } from '../store';
import { api } from '../services/api';

interface SettingsScreenProps {
  onLogout: () => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ onLogout }) => {
  const { session, logout } = useAuthStore();
  const {
    darkMode,
    notificationsEnabled,
    locationEnabled,
    offlineMode,
    toggleDarkMode,
    toggleNotifications,
    toggleLocation,
    toggleOfflineMode,
  } = useSettingsStore();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await api.logout();
            logout();
            onLogout();
          },
        },
      ]
    );
  };

  const SettingRow: React.FC<{
    icon: keyof typeof Ionicons.glyphMap;
    iconColor?: string;
    title: string;
    subtitle?: string;
    value?: boolean;
    onToggle?: () => void;
    onPress?: () => void;
    showArrow?: boolean;
  }> = ({ icon, iconColor = '#9ca3af', title, subtitle, value, onToggle, onPress, showArrow }) => (
    <TouchableOpacity
      style={styles.settingRow}
      onPress={onPress}
      disabled={!onPress && !onToggle}
    >
      <View style={[styles.iconContainer, { backgroundColor: iconColor + '20' }]}>
        <Ionicons name={icon} size={20} color={iconColor} />
      </View>
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {onToggle !== undefined && value !== undefined && (
        <Switch
          value={value}
          onValueChange={onToggle}
          trackColor={{ false: '#374151', true: '#3b82f6' }}
          thumbColor="#fff"
        />
      )}
      {showArrow && <Ionicons name="chevron-forward" size={20} color="#6b7280" />}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Profile Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Profile</Text>
          <View style={styles.profileCard}>
            <View style={styles.avatar}>
              <Ionicons name="person" size={32} color="#fff" />
            </View>
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>
                {session?.user.name || `Officer ${session?.user.badge_number}`}
              </Text>
              <Text style={styles.profileBadge}>Badge: {session?.user.badge_number}</Text>
              <Text style={styles.profileRole}>{session?.user.role || 'Officer'}</Text>
            </View>
          </View>
        </View>

        {/* Preferences Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          <View style={styles.settingsGroup}>
            <SettingRow
              icon="moon"
              iconColor="#7c3aed"
              title="Dark Mode"
              subtitle="Use dark theme"
              value={darkMode}
              onToggle={toggleDarkMode}
            />
            <SettingRow
              icon="notifications"
              iconColor="#f59e0b"
              title="Push Notifications"
              subtitle="Receive alerts and messages"
              value={notificationsEnabled}
              onToggle={toggleNotifications}
            />
            <SettingRow
              icon="location"
              iconColor="#22c55e"
              title="Location Services"
              subtitle="Share location for safety features"
              value={locationEnabled}
              onToggle={toggleLocation}
            />
            <SettingRow
              icon="cloud-offline"
              iconColor="#6b7280"
              title="Offline Mode"
              subtitle="Cache data for offline access"
              value={offlineMode}
              onToggle={toggleOfflineMode}
            />
          </View>
        </View>

        {/* Device Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device</Text>
          <View style={styles.settingsGroup}>
            <SettingRow
              icon="phone-portrait"
              iconColor="#3b82f6"
              title="Device Registration"
              subtitle="Manage registered devices"
              showArrow
              onPress={() => Alert.alert('Device Management', 'Device management coming soon')}
            />
            <SettingRow
              icon="finger-print"
              iconColor="#ec4899"
              title="Biometric Login"
              subtitle="Use fingerprint or face ID"
              showArrow
              onPress={() => Alert.alert('Biometric', 'Biometric login coming soon')}
            />
          </View>
        </View>

        {/* Security Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>
          <View style={styles.settingsGroup}>
            <SettingRow
              icon="key"
              iconColor="#f59e0b"
              title="Change PIN"
              subtitle="Update your security PIN"
              showArrow
              onPress={() => Alert.alert('Change PIN', 'PIN change coming soon')}
            />
            <SettingRow
              icon="shield-checkmark"
              iconColor="#22c55e"
              title="CJIS Compliance"
              subtitle="View compliance status"
              showArrow
              onPress={() => Alert.alert('CJIS Compliance', 'All security requirements met')}
            />
          </View>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <View style={styles.settingsGroup}>
            <SettingRow
              icon="information-circle"
              iconColor="#3b82f6"
              title="App Version"
              subtitle="1.0.0 (Build 1)"
            />
            <SettingRow
              icon="document-text"
              iconColor="#6b7280"
              title="Terms of Service"
              showArrow
              onPress={() => Alert.alert('Terms', 'Terms of Service')}
            />
            <SettingRow
              icon="lock-closed"
              iconColor="#6b7280"
              title="Privacy Policy"
              showArrow
              onPress={() => Alert.alert('Privacy', 'Privacy Policy')}
            />
          </View>
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out" size={20} color="#dc2626" />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.footerText}>G3TI RTCC Mobile</Text>
          <Text style={styles.footerText}>Global 3 Technology & Intelligence</Text>
        </View>
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
    padding: 16,
    paddingTop: 60,
    backgroundColor: '#1f2937',
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
  },
  content: {
    flex: 1,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    padding: 16,
    borderRadius: 12,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#3b82f6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  profileInfo: {
    marginLeft: 16,
  },
  profileName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  profileBadge: {
    color: '#9ca3af',
    fontSize: 14,
    marginTop: 2,
  },
  profileRole: {
    color: '#6b7280',
    fontSize: 12,
    marginTop: 2,
    textTransform: 'capitalize',
  },
  settingsGroup: {
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    borderRadius: 12,
    overflow: 'hidden',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingContent: {
    flex: 1,
    marginLeft: 12,
  },
  settingTitle: {
    color: '#fff',
    fontSize: 16,
  },
  settingSubtitle: {
    color: '#6b7280',
    fontSize: 13,
    marginTop: 2,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1f2937',
    marginHorizontal: 8,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  logoutText: {
    color: '#dc2626',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    padding: 24,
  },
  footerText: {
    color: '#4b5563',
    fontSize: 12,
  },
});
