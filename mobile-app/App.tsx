/**
 * G3TI RTCC Mobile App
 * Officer Mobile Access for Real Time Crime Center
 */

import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';

import {
  LoginScreen,
  DashboardScreen,
  AlertsScreen,
  DispatchScreen,
  MessagingScreen,
  OfficerSafetyScreen,
  IntelFeedScreen,
  SceneCoordinationScreen,
  SettingsScreen,
} from './src/screens';
import { useAuthStore, useAlertsStore, useMessagingStore } from './src/store';
import { api } from './src/services/api';
import { websocket } from './src/services/websocket';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  const { alerts } = useAlertsStore();
  const { messages } = useMessagingStore();

  const unreadAlerts = alerts.filter(a => !a.read).length;
  const unreadMessages = messages.filter(m => !m.read).length;

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#111827',
          borderTopColor: '#374151',
          paddingBottom: 20,
          paddingTop: 8,
          height: 80,
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#6b7280',
        tabBarLabelStyle: {
          fontSize: 11,
          marginTop: 4,
        },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      >
        {(props) => <DashboardScreen {...props} onNavigate={(screen) => {}} />}
      </Tab.Screen>
      <Tab.Screen
        name="Alerts"
        component={AlertsScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="notifications" size={size} color={color} />
          ),
          tabBarBadge: unreadAlerts > 0 ? unreadAlerts : undefined,
        }}
      />
      <Tab.Screen
        name="Dispatch"
        component={DispatchScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="radio" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Messages"
        component={MessagingScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="chatbubbles" size={size} color={color} />
          ),
          tabBarBadge: unreadMessages > 0 ? unreadMessages : undefined,
        }}
      />
      <Tab.Screen
        name="Safety"
        component={OfficerSafetyScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="shield" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

function MoreScreens() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Intel" component={IntelFeedScreen} />
      <Stack.Screen name="Scene" component={SceneCoordinationScreen} />
      <Stack.Screen name="Settings">
        {(props) => <SettingsScreen {...props} onLogout={() => {}} />}
      </Stack.Screen>
    </Stack.Navigator>
  );
}

export default function App() {
  const { isAuthenticated, session, setSession } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize API and check for existing session
    const init = async () => {
      try {
        await api.init();
        // Check if we have a valid session
        const refreshed = await api.refreshSession();
        if (!refreshed) {
          setSession(null);
        }
      } catch (error) {
        console.error('Failed to initialize:', error);
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  useEffect(() => {
    // Connect WebSocket when authenticated
    if (isAuthenticated && session?.user.badge_number) {
      websocket.connect(session.user.badge_number);

      return () => {
        websocket.disconnect();
      };
    }
  }, [isAuthenticated, session]);

  useEffect(() => {
    // Request notification permissions
    const requestPermissions = async () => {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        console.log('Notification permissions not granted');
      }
    };

    requestPermissions();
  }, []);

  if (isLoading) {
    return null; // Or a splash screen
  }

  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#111827' },
        }}
      >
        {!isAuthenticated ? (
          <Stack.Screen name="Login">
            {(props) => (
              <LoginScreen
                {...props}
                onLoginSuccess={() => {}}
              />
            )}
          </Stack.Screen>
        ) : (
          <>
            <Stack.Screen name="Main" component={MainTabs} />
            <Stack.Screen name="Intel" component={IntelFeedScreen} />
            <Stack.Screen name="Scene" component={SceneCoordinationScreen} />
            <Stack.Screen name="Settings">
              {(props) => <SettingsScreen {...props} onLogout={() => setSession(null)} />}
            </Stack.Screen>
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
