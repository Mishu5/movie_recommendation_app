import React from 'react';
import { Tabs } from 'expo-router';
import { Text } from 'react-native';

const TabLayout = () => {
    return (
        <Tabs screenOptions={{ headerShown: false }}>
            <Tabs.Screen
                name="index"
                options={{ title: 'Home', tabBarIcon: () => <Text>🏠</Text> }}
            />
            <Tabs.Screen
                name="userPanel"
                options={{ title: 'User Panel', tabBarIcon: () => <Text>👤</Text> }}
            />
            <Tabs.Screen
                name="room"
                options={{ title: 'Room', tabBarIcon: () => <Text>📺</Text> }}
            />
        </Tabs>
    );
};

export default TabLayout;