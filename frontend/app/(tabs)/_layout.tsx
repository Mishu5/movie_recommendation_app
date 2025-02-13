import { Tabs } from 'expo-router';
import React from 'react';
import { Platform } from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: Platform.OS === 'web',
        tabBarButton: HapticTab,
        tabBarPosition: Platform.OS === 'web' ? 'bottom' : 'top',
        tabBarBackground: TabBarBackground,
        tabBarStyle: Platform.select({
          ios: {
            // Use a transparent background on iOS to show the blur effect
            position: 'absolute',
          },
          default: {},
        }),
      }}>
      <Tabs.Screen name="index" options={{ title: 'Media' }} />
      <Tabs.Screen name="login" options={{ title: 'Login' }} />
      <Tabs.Screen name="user" options={{ title: 'User Panel' }} />
      <Tabs.Screen name="room" options={{ title: 'Rooms' }} />
    </Tabs>
  );
}
